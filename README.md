# Agricultural-information-sharing-platform :farmer: :seedling:

Agricultural Information Sharing Platform (AISP) is a groundbreaking 
endeavor that harnesses the power of advanced AI technologies to revolutionize the 
way farmers interact with information. The platform is built using Llama-2-Chat 
(Large Language Model Meta AI), a pretrained and finetuned generative text model. 
The platform assists users with agricultural-related queries, providing information on 
crops, pest control, farming practices, and more. 

The platform is designed and developed with the Django framework with 
MongoDB database in the virtual machine (VM) with GPU support. The Llama-2
chat models of version 7b and 13b are downloaded from Meta AI that plays a critical 
role in generating contextually relevant responses for the user’s queries and inquiries. 

![image](https://github.com/user-attachments/assets/7767eebb-9e6d-4940-bbc4-65322a260860)

Technologies: Django, HTML, CSS, JavaScript, MongoDB <br>
Language: Python <br>
Libraries: Langchain, transformers, torch, BeautifulSoup <br>

MODULE DESCRIPTION 
--
This platform is built on the Llama2 Generative AI model which is mainly 
used for Chatbot applications. The 2 main modules are the Chat module and the Crop 
recommendation module. <br><br>
<b> Register Page: </b> <br>
• There will be a placeholder where the user had to provide the username and 
password and his/her name to store the details in the MongoDB. <br>
• Once submitted the user will be redirected to the Login Page. <br>
<b> Login Page: </b> <br>
• The user must enter the username and password to move to the next page. 
• The user details are validated by checking it with the MongoDB database. <br><br>
<b align="center"> Chat Module </b> <br><br>
Chat Page:  <br>
• The user enters the query in the message box and pressing the enter key will 
send it to the intent classification model. <br>
• The intent classification model is where the queries are classified as a General 
Query or else as a Crop Recommendation Query. <br>
• If it is classified as a General Query then, it is processed for reply from the 
LLM. <br>
• If it is a crop recommendation related query then a form is displayed. <br>
• In the form the user must enter the details of Nitrogen, Phosphorous, 
Potassium contents of the soil, Humidity, Rainfall, Temperature in the 
atmosphere. 
<br><br>
Intent Classification:  <br>
• The intent classification module is built using Machine Learning Models MLP 
classifier, Bernoulli classifier, Complement Naïve Bayes and MultinomialNB, 
Logistic Regression and Random Forest Classifier. <br>
• The best 4 models out of all are taken and the query asked by the user is 
classified into the respective category. <br>
• The mode of prediction is used for classifying the query into a category.
<br><br>
Llama2 Integration:  <br>
• The Llama2 model is downloaded from the Meta AI website and is converted 
into binary files using transformer script. <br>
• Then the model is given the context of the data we have using a Retrieval 
Augmented Generation. <br>
• Data required for knowledge base are collected from Tamil Nadu Government 
websites and are also web scraped using Beautiful Soup Library and then are 
ingested into the Pipeline for query processing. <br><br>
Voice recognition feature:  <br>
• The voice recognition features enable the user to submit queries through voice 
input. <br>
• This voice input gets converted into text and then is processed for intent 
classification. <br>
• The feature is added with the Web Speech API in JavaScript. 
<br><br>
<b> Crop recommendation Module </b>
<br> <br>
Data Collection: 
The data required for crop recommendation is collected from Kaggle and are 
then used for model training. The features in the dataset include nitrogen, potassium, 
phosphorus, humidity, pH value, rainfall and temperature. 
<br> <br>
Model Training: <br>
• The dataset is trained using machine learning models. <br>
• Once the dataset is trained, the best 3 algorithms that gave high accuracy and 
low rmse is selected for prediction. <br>
• Then the mode is taken for the predicted output with the 3 models which 
gives the recommended crop for the farmer’s land.<br>
