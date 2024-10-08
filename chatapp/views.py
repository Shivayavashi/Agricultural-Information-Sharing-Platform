############################# IMPORT FUNCTIONS ############################################

from django.shortcuts import redirect, render
from django.views import View
import re
import contractions
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem import WordNetLemmatizer
import pickle
import statistics
from chatapp.models import Profile,Chatlogs
import pymongo
import sys
from django.http import JsonResponse
import os
import logging
import click
from langchain import LLMChain,PromptTemplate
import torch
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from transformers import (
    GenerationConfig,
    pipeline,
)

from load_models import (
    load_full_model    #importing the load_full_model function to load the llama-2 model 
)

from constants import (
    MODEL_ID,
    MODEL_BASENAME,
    MAX_NEW_TOKENS,
    EMBEDDING_MODEL_NAME,
    PERSIST_DIRECTORY,
)
 
from prompt_template_utils import get_prompt_template #import from prompt_template_utils.py file

#################### LOAD MODEL ##########################################################

# Load model function to load the model from the load_models.py file

def load_model(device_type, model_id, model_basename=None, LOGGING=logging):
    logging.info(f"Loading Model: {model_id}, on: {device_type}")
    logging.info("This action can take a few minutes!")
    model, tokenizer = load_full_model(model_id, model_basename, device_type, LOGGING)

    # Load configuration from the model to avoid warnings
    generation_config = GenerationConfig.from_pretrained(model_id)
    # see here for details:
    # https://huggingface.co/docs/transformers/
    # main_classes/text_generation#transformers.GenerationConfig.from_pretrained.returns

    # Create a pipeline for text generation
    pipe = pipeline(
        "text-generation", 
        model=model,
        tokenizer=tokenizer,
        max_length=MAX_NEW_TOKENS,  # Refers to the context length of the model : 2048
        temperature=0.2,
        # top_p=0.95,
        repetition_penalty=1.15,
        generation_config=generation_config,
    )
    local_llm = HuggingFacePipeline(pipeline=pipe)
    logging.info("Local LLM Loaded")

    return local_llm

##########################   QA PIPELINE FOR RAG ###############################################

def retrieval_qa_pipline(llm,device_type, use_history, promptTemplate_type="llama"):
    #embeddings for converting the text into embeddings with the hkunlp/instructor-large model
    # This model is defined in the constants.py
    
    embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": device_type})
    
    # Chroma DB is used for storing the embeddings.
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY, #Defined in the constants.py this will create a DB folder in the current Directory AIEP_LLAMA
        embedding_function=embeddings,
    )


    retriever = db.as_retriever() #This DB is used as retriever 
    prompt, memory = get_prompt_template(promptTemplate_type=promptTemplate_type, history=use_history) #Call to get_prompt_template function
    if use_history:
        qa = RetrievalQA.from_chain_type( #this qa is a pipeline to generate answers from llama with the query
            llm=llm,   
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )
    else:
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
            retriever=retriever,
            return_source_documents=True,  # verbose=True,
            callbacks=callback_manager,
            chain_type_kwargs={
                "prompt": prompt,
            },
        )
    print("qa returned")
    return qa

############################################################################################################

device_type = "cuda"
use_history=False
llm=load_model(device_type,model_id=MODEL_ID,model_basename=MODEL_BASENAME,LOGGING=logging)
qa = retrieval_qa_pipline(llm,device_type, use_history, promptTemplate_type="llama")

############################################################################################################

# These are the pickle files for models created for query classification
# whether the query is an agricultural domain or non domain

with open('picklefiles/count_vectorizer.pkl', 'rb') as cv_file:
    loaded_cv = pickle.load(cv_file)
with open('picklefiles/lr_model.pkl', 'rb') as file:
    lr = pickle.load(file)
with open('picklefiles/clf_model.pkl', 'rb') as file:
    clf = pickle.load(file)

# These are the pickle files for models created for classification for knowledge base access
# whether the query needs database or not

with open('picklefiles/count_vectorizer1.pkl', 'rb') as cv_file:
    loaded_cv1 = pickle.load(cv_file)
with open('picklefiles/lr_model1.pkl', 'rb') as file:
    lr1 = pickle.load(file)
with open('picklefiles/clf_model1.pkl', 'rb') as file:
    clf1 = pickle.load(file)

############################################################################################################

#Lemmatizer extracts only the root word.
lemmatizer = WordNetLemmatizer()
nltk_stopwords = set(stopwords.words('english'))
sk_stopwords = set(ENGLISH_STOP_WORDS)
stopwords = sk_stopwords.union(nltk_stopwords)
def stop(text):
    y = []
    for i in text.split():
        if i not in stopwords:
            y.append(i.lower())
    return " ".join(y)

def lemmatate(text):
    y = []
    for i in text.split():
            y.append(lemmatizer.lemmatize(i))
    return " ".join(y)

#This class contains the chat functionality.
class chat(View):
    def get(self, request):#loads the chat page
        username = request.session['username']
        messages = Chatlogs.objects.all().filter(username=username)
        return render(request, 'chatpage.html',{'username':username,'messages':messages})
def llm(request):
    if request.method == 'POST':#when question get posted
        question = request.POST.get('input')
        question = re.sub(r"[^a-zA-Z]", " ", question)
        question = stop(question)
        question = lemmatate(question)
        question = contractions.fix(question)
        question1 = loaded_cv.transform([question])
        x1 = lr.predict(question1)
        x2 = clf.predict(question1)#using models to predict
        agriculture =  statistics.mode([x1[0],x2[0],x1[0]])
        if agriculture==0:#not agri domain
            Chatlogs.objects.create(username = request.session['username'],question = request.POST.get('input'),reply ='Ask domain specific questions')
            return JsonResponse({'message': 'Ask domain specific questions'})
        else:# is agri domain
            question2 = loaded_cv1.transform([question])
            y1 = lr1.predict(question2)
            y2 = clf1.predict(question2)
            database = statistics.mode([y1[0],y2[0],y1[0]])
            if database==0:# no need knowledge base and apis
                query= str(request.POST.get('input'))
                res = qa(query)
                answer=res["result"]
                docs=res["source_documents"]
                logging.info(f"Relevent docs are : {docs}")
                Chatlogs.objects.create(username = request.session['username'],question = request.POST.get('input'),reply =answer)
                return JsonResponse({'message': answer})
            else:# uses knowledge base and apis
                username = request.session['username']
                client = pymongo.MongoClient('mongodb://localhost:27017/')
                db = client['agritn']#fetch the db
                collection = db["chatapp_profile"]#fetch the collection
                document = collection.find_one({"username": username})#filter
                district = document['district'].lower()
                dcrop = db["districtcrops"]
                #query to get crops of that particular user region
                query = {
                    "$or": [
                        {"districts": district},
                        {"districts": "all"}
                    ]
                }
                crop = dcrop.find(query)
                crops = ''
                for i in crop:
                    crops = crops + i['crops'] + ','
                #######soil
                dsoil = db["soil"]
                query = {
                    "$or": [
                        {"districts": district},
                        {"districts": "all"}
                    ]
                }
                soil = dsoil.find(query)
                soils = ''
                for i in soil:
                    soils = soils + i['soil type'] + ','
                ########weather
                import requests
                URL = "http://api.openweathermap.org/data/2.5/weather?"
                API_KEY = "008a46fd637b639f0729c916f97220d7"
                CITY = district
                url = URL + "appid=" + API_KEY + "&q=" + CITY
                weather_data = requests.get(url).json()
                try:
                    weather_description = str(weather_data['weather'][0]['description'])
                    temperature = str(float(weather_data['main']['temp'])-273.15)
                    humidity = str(weather_data['main']['humidity'])
                    wind_speed = str(weather_data['wind']['speed'])
                    #feed the live datas with the question to tha llm
                    query='QUESTION ::'+str(request.POST.get('input'))+ ' ; DATA ::Crops in ' +district+ ' are ' + crops +', soil type in '+ district + 'is ' + soils + ';Weather in '+ district + ' is ' + weather_description + ' temp : '+temperature+'celsius ;humidity : '+humidity+' wind speed is '+wind_speed
                except:
                    query= 'QUESTION ::'+str(request.POST.get('input'))+ ' ; DATA ::Crops in ' +district+ ' are ' + crops +', soil type in '+ district + 'is ' + soils

                res = qa(query)#llama is called
                answer=res["result"]
                #stores the chathistory in the chatlogs collections
                Chatlogs.objects.create(username = username,question = request.POST.get('input'),reply =answer)
                return JsonResponse({'message': answer})

#logging out function
def logout(request):
    request.session.clear()
    return redirect('login')

#class which has login in functionality
class login(View):
    def get(self, request):
        if request.session.get('authenticated'):
            return redirect('chat')
        return render(request, 'login.html')
    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = client['agritn']
            collection = db["chatapp_profile"]
            document = collection.find_one({"username": username})
            if document:#checks username is present
                stored_password = document.get("password")
                if stored_password == password:#check password matches
                    request.session['authenticated'] = True
                    request.session['username'] = username
                    return redirect('chat')
                else:
                    return render(request, 'login.html',{'error':'Password is incorrect!!'})
            else:
                return render(request, 'login.html',{'error':'Username not found!!'})
    
class register(View):
    def get(self, request):
        return render(request, 'register.html')
    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            number = request.POST.get('number')
            dob = request.POST.get('dob')
            gender =  request.POST.get('gender')
            country = request.POST.get('country')
            state =  request.POST.get('state')
            district =  request.POST.get('district')
            taluk =  request.POST.get('taluk')
            #creates record in profile collection
            Profile.objects.create(username = username,password = password,name = name,number = number,dob = dob,gender = gender,country = country,  state =  state,district =  district,taluk =  taluk,)
            return redirect('login')