# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/14 16:40
# @Author  : shaocanfan
# @File    : rag_based_feature_mapping_2.0.py
# @Intro   :


import os
import bs4
import openai
# import chromadb
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
os.environ["OPENAI_API_KEY"] = ""  # app5
os.environ["OPENAI_API_BASE"] = "https://ai-yyds.com/v1"  # "https://ai-yyds.com/v1"
openai.api_key = os.environ['OPENAI_API_KEY']
openai.api_base = os.environ['OPENAI_API_BASE']

# import requests
# from langchain.document_loaders import TextLoader
# from langchain.document_loaders import TextLoader
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Weaviate
import weaviate
from weaviate.embedded import EmbeddedOptions
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
embeddings = OpenAIEmbeddings()
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import TextLoader
# from langchain_community import embeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter

llm_local = ChatOllama(model="qwen:7b")

# 1，读取文件并分词
documents = TextLoader("3guo2.txt").load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
doc_splits = text_splitter.split_documents(documents)

# 2，嵌入并存储
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = DocArrayInMemorySearch.from_documents(doc_splits, embeddings)
retriever = vectorstore.as_retriever()

# 3，向模型提问
template = """
Answer the question based only on the following context:
{context}
Question: {question}
"""


prompt = ChatPromptTemplate.from_template(template)
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm_local
    | StrOutputParser())
resp = chain.invoke("身长七尺，细眼长髯的是谁？")
print(resp)




"""
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Load, chunk and index the contents of the blog.

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

# print(len(docs[0].page_content))
# print(docs[0].page_content[:500])

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# client = weaviate.connect_to_local()
# db = WeaviateVectorStore.from_documents(splits, embeddings, client=client)

client = weaviate.Client(
  embedded_options=EmbeddedOptions()
)

vectorstore = Weaviate.from_documents(
    client=client,
    documents=splits,
    embedding=OpenAIEmbeddings(),
    by_text=False
)

vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()


retrieved_docs = retriever.invoke("What are the approaches to Task Decomposition?")

print(len(retrieved_docs))
prompt = hub.pull("rlm/rag-prompt")


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

rag_chain.invoke("What is Task Decomposition?")
"""