import os
import requests
import json
import re
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from langchain.chains import RetrievalQA
from services.loadModel import llama
from services.vectorDb import VectorDB
from dotenv import load_dotenv

load_dotenv()
llm=llama()


class Model:
    # singelton class

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Model, cls).__new__(cls)
        return cls.instance

    def __init__(self,):
        self.parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 250
        }

        self.api_key = os.getenv('APIKEY')
        self.token_url = "https://iam.cloud.ibm.com/identity/token"
        self.token = ""
        self.model_id = ModelTypes.LLAMA_2_70B_CHAT
        self.llm=llm.getModel()
        self.vectordb=None
        self.qa=None     
      
    def get_token(self):
        print(self.api_key, "******************")
        token_response = requests.post(self.token_url, data={
            "apikey": self.api_key, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        self.token = token_response.json()["access_token"]

    # def get_vector_db(self,name):
    #     self.vectordb = Chroma(persist_directory=name, embedding_function=self.embeddings)
    #     self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.vectordb.as_retriever())

    # def get_response_from_watsonx(self,data):
    #     name=data["name"]
    #     self.get_vector_db(name=name)
    #     res=self.qa.run(data["question"] + "and dont ask me confirmations")
    #     return json.dumps({
    #         "answer":res,
    #         "status":True,
    #     })
    def get_response_singelton(self,data):
        name=data["name"]
        vectorDb=VectorDB(name,self.llm)
        res=vectorDb.qa.run("you are an chatbot answer the questions,question="+" "+data["question"])
        ans=self.remove_after_context(res)
        ans=self.remove_after_question(ans)
        return json.dumps({
            "answer":ans,
            "status":True,
        })
    def remove_after_context(self,input_text):
        # Find the index of the word 'context' in the input text
        context_index = input_text.lower().find('context')

        # Remove the text after 'context' if it exists
        if context_index != -1:
            output_text = input_text[:context_index]
        else:
            output_text = input_text

        return output_text
    def remove_after_question(self,input_text):
        # Find the index of the word 'context' in the input text
        context_index = input_text.lower().find('question')

        # Remove the text after 'context' if it exists
        if context_index != -1:
            output_text = input_text[:context_index]
        else:
            output_text = input_text

        return output_text
        
        
# llm=Model()
# print(llm.get_response_from_watsonx({"question":"how to reset atm pin?","name":"saved_vdb_copy"}))