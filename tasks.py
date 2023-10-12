
from services.model import Model
from celery import Celery
import requests
import redis
import json
import time
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from app import db


app = Celery("tasks", backend='redis://localhost:6379/0',
             broker='redis://localhost:6379/0')
app.conf.broker_connection_retry_on_startup = True
rds = redis.Redis(host='localhost', port=6379, db=1)
headers = {'Content-Type': 'application/json'}
llm={}


@app.task()
def get_info_from_docs(_data, callback_api, rds_task_id):
    # training operation    
    result = llm.get_data_from_llm(text=_data)
    # time.sleep(4)
    # result ={
    #         "income": 9999,
    #         "bankbalance": 9955,
    #         "aadhar": 98765432145,
    #         "pan": "DFER4567U",
    #         "name": "User test",
    #         "address": "Pune, Maharashtra",
    #         "accountNo": 40097587451
    #     }
    # For callback
    task_id = rds.get(rds_task_id).decode("utf-8")
    print(task_id,"*****")
    url = callback_api
    result=json.loads(result)
    result["task_id"] = task_id
    requests.post(url, data=json.dumps(result), headers=headers)
    return result

@app.task()
def get_response(_data, callback_api, rds_task_id):
    # loan status operation
    print(_data,"Data is ***********")
    try:
        llm=Model()
        # result = llm.get_response_from_watsonx(data=_data)
        result=llm.get_response_singelton(data=_data)

        # For callback
        task_id = rds.get(rds_task_id).decode("utf-8")
        url = callback_api
        result=json.loads(result)

        result["task_id"] = task_id    
        requests.post(url, data=json.dumps(result), headers=headers)
        return result
    except Exception as e:
        return json.dumps({'error':str(e)}),500

@app.task
def create_bot(data,callback_api,rds_task_id,name):
    try:
        print(type(data),"***")
        data=json.loads(data)
        filename='./docs/'+data["name"]+'.'+data["extension"]+''
        print(filename,"jjjj")

        with open(filename, 'w') as f:
            f.write(data["text"])
        loader = TextLoader(filename)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(separator="question",chunk_size=1000)
        texts = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings()
        docsearch = Chroma.from_documents(texts, embeddings,persist_directory='./vector_db_store/'+name)
        task_id = rds.get(rds_task_id).decode("utf-8")
        url = callback_api
        result={}
        result["task_id"] = task_id
        result["name"]=name
        result["path"]='./vector_db_store/'+name
        db.vectordb.insert_one(result)
        requests.post(url, data=json.dumps(result), headers=headers)
        print("************************************")
        return result    
    except Exception as e:
        return json.dumps({'error':str(e)}),500
