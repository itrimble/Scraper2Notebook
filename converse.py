from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from tinydb import TinyDB
import json

db = TinyDB('db.json')
agent_table = db.table('agent_table')

class Converse:
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma(persist_directory="../chroma_db", embedding_function=self.embedding_function)
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    def chat(self, query, agent_table_row):
        llm = OllamaLLM(model=agent_table_row["model"])
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", agent_table_row["system_message"]),
            ("human", "{query}")
        ])
        chain = (
            {"query": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )
        # Handle context and question separately
        if "Context:" in query:
            context, question = query.split("\nQuestion: ", 1)
            context = context.replace("Context: ", "")
            if context == "No relevant context found.":
                return chain.invoke("I couldn't find relevant context. Here's my best answer: " + question)
            return chain.invoke(f"Here's some context to help you answer my question: {context}\n\nHere's my question: {question}")
        return chain.invoke(query)