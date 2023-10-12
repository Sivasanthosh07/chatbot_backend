from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings

class VectorDB:
    # singelton class

    def __new__(cls,name,llm):
        if not hasattr(cls, name):
            # print(name,"888888")
            # cls.name=name
            cls.name = super(VectorDB, cls).__new__(cls)
        return cls.name

    def __init__(self,name,llm):
        self.name=name
        self.llm=llm
        self.embeddings = HuggingFaceEmbeddings()

        self.vectordb = Chroma(persist_directory='./vector_db_store/'+self.name, embedding_function=self.embeddings)
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.vectordb.as_retriever())
    def get_qa(self):
        return self.qa