"""
This file implements prompt template for llama based models. 
Modify the prompt template based on the model you select. 
This seems to have significant impact on the output of the LLM.
"""

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# this is specific to Llama-2.

# if you need to change the domain then change the system prompt according to the use case

system_prompt = """You are a helpful agricultural assistant and should answer only agricultural specific questions, you will use the provided context to answer user agricultural questions.
Read the given context before answering questions and think step by step.Do not provide response to question other than agriculture.Provide answer within 150 words."""


def get_prompt_template(system_prompt=system_prompt, promptTemplate_type=None, history=False):
    if promptTemplate_type == "llama":  ###### prompt template for llama model
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS    #context is where the texts chunk comes here
        if history:
            instruction = """
            Context: {history} \n {context}         
            User: {question}"""

            prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST #overall prompt  
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            instruction = """
            Context: {context}
            User: {question}"""

            prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    else: # for other models
        # change this based on the model you have selected.
        if history:
            prompt_template = (
                system_prompt
                + """
    
            Context: {history} \n {context}
            User: {question}
            Answer:"""
            )
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            prompt_template = (
                system_prompt
                + """
            
            Context: {context}
            User: {question}
            Answer:"""
            )
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    memory = ConversationBufferMemory(input_key="question", memory_key="history") # this can track questions for chatbot flow --> using a buffer memory for storing k conversations

    return (
        prompt,
        memory,
    )
