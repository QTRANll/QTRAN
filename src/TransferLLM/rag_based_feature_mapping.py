# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/30 10:58
# @Author  : shaocanfan
# @File    : rag_based_feature_mapping.py
# @Intro   :

import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
from langchain.prompts import ChatPromptTemplate
from src.Tools.JSONLoader import JSONLoader
from langchain_community.vectorstores import Chroma
import chromadb
from langchain.vectorstores import Weaviate
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
import openai
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
os.environ["OPENAI_API_KEY"] = ""  # app5
os.environ["OPENAI_API_BASE"] = "https://ai-yyds.com/v1"  # "https://ai-yyds.com/v1"
openai.api_key = os.environ['OPENAI_API_KEY']
openai.api_base = os.environ['OPENAI_API_BASE']


# 获取database的feature向量嵌入数据，并将它们存储起来
def load_database_feature_embedding_data(db, feature_type, content_key):
    if db.lower() == "mysql":
        embedding_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "MySQL", "RAG_Embedding_Data",
                                               feature_type + ".jsonl")
        if not os.path.exists(embedding_data_filename):
            # 创建embedding_data_filename
            feature_filepath = os.path.join("..", "..", "Feature Knowledge Base", "MySQL", "Functions_and_Operators",
                                            "Functions_and_Operators_Results_Category", "Functions_Category")
            filenames = os.listdir(feature_filepath)

            index = 0
            feature_names = []
            for filename in filenames:
                with open(os.path.join(feature_filepath, filename), "r", encoding="utf-8") as r:
                    data = json.load(r)
                for key, value in data.items():
                    value["index"] = index
                    value["Feature_Category"] = str(value["index"]) + ":" + value["Feature"] + "," + filename.replace(
                        ".json", "")
                    index += 1
                    if value["Feature"] in feature_names:
                        continue
                    else:
                        feature_names.append(value["Feature"])
                    with open(embedding_data_filename, "a", encoding="utf-8") as a:
                        json.dump(value, a)
                        a.write("\n")

        loader = JSONLoader(file_path=embedding_data_filename, content_key=content_key, json_lines=True)
        data = loader.load()
        return data
    elif db.lower() == "tidb":
        embedding_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "TiDB", "RAG_Embedding_Data",
                                               feature_type + ".jsonl")
        if not os.path.exists(embedding_data_filename):
            # 创建embedding_data_filename
            feature_filepath = os.path.join("..", "..", "Feature Knowledge Base", "TiDB", "Functions",
                                            "Functions_Results_Category")
            filenames = os.listdir(feature_filepath)
            index = 0
            feature_names = []
            for filename in filenames:
                with open(os.path.join(feature_filepath, filename), "r", encoding="utf-8") as r:
                    lines = r.readlines()

                for line in lines:
                    value = json.loads(line)
                    value["index"] = index

                    feature_str = ""
                    for item in value["Feature"]:
                        feature_str += item
                    value["Feature_Category"] = str(value["index"]) + ":" + feature_str + "," + value["Category"][0]
                    index += 1
                    if value["Feature"] in feature_names:
                        continue
                    else:
                        feature_names.append(value["Feature"])
                    with open(embedding_data_filename, "a", encoding="utf-8") as a:
                        json.dump(value, a)
                        a.write("\n")

        loader = JSONLoader(file_path=embedding_data_filename, content_key=content_key, json_lines=True)
        data = loader.load()
        return data
    elif db.lower() == "mariadb":
        embedding_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "MariaDB", "RAG_Embedding_Data",
                                               feature_type + ".jsonl")
        if not os.path.exists(embedding_data_filename):
            # 创建embedding_data_filename
            feature_filepath = os.path.join("..", "..", "Feature Knowledge Base", "MariaDB", "Functions",
                                            "Functions_Results")
            filenames = os.listdir(feature_filepath)

            index = 0
            for filename in filenames:
                with open(os.path.join(feature_filepath, filename), "r", encoding="utf-8") as r:
                    data = json.load(r)
                data["index"] = index
                feature_str = ""
                for item in data["Feature"]:
                    feature_str += item
                data["Feature_Category"] = str(data["index"]) + ":" + feature_str + "," + data["Category"][0]
                index += 1
                with open(embedding_data_filename, "a", encoding="utf-8") as a:
                    json.dump(data, a)
                    a.write("\n")

        loader = JSONLoader(file_path=embedding_data_filename, content_key=content_key, json_lines=True)
        data = loader.load()
        return data
    elif db.lower() == "clickhouse":
        embedding_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "ClickHouse", "RAG_Embedding_Data",
                                               feature_type + ".jsonl")
        if not os.path.exists(embedding_data_filename):
            # 创建embedding_data_filename
            feature_filepath = os.path.join("..", "..", "Feature Knowledge Base", "ClickHouse", "Functions",
                                            "Functions_Results")
            filenames = os.listdir(feature_filepath)

            index = 0
            for filename in filenames:
                with open(os.path.join(feature_filepath, filename), "r", encoding="utf-8") as r:
                    data = json.load(r)
                data["index"] = index
                feature_str = ""
                for item in data["Feature"]:
                    feature_str += item
                data["Feature_Category"] = str(data["index"]) + ":" + feature_str + "," + data["Category"][0]
                index += 1
                with open(embedding_data_filename, "a", encoding="utf-8") as a:
                    json.dump(data, a)
                    a.write("\n")

        loader = JSONLoader(file_path=embedding_data_filename, content_key=content_key, json_lines=True)
        data = loader.load()
        return data


def rag_feature_mapping(a_db, b_db, feature_type, content_key):
    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, a_db + "_mapping_" + b_db + ".jsonl")
    if os.path.exists(dir_filename):
        print(dir_filename + ":已存在！")
        return

    # 读取被检索b_db的feature_type的embedding data
    data = load_database_feature_embedding_data(b_db, feature_type, content_key)
    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(data, embedding_function)

    # 获取a_db的feature_type所有feature
    load_database_feature_embedding_data(a_db, feature_type, content_key)
    query_data_filename = ""
    if a_db.lower() == "mariadb":
        query_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "MariaDB", "RAG_Embedding_Data",
                                           feature_type + ".jsonl")
    elif a_db.lower() == "tidb":
        query_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "TiDB", "RAG_Embedding_Data",
                                           feature_type + ".jsonl")
    elif a_db.lower() == "mysql":
        query_data_filename = os.path.join("..", "..", "Feature Knowledge Base", "MySQL", "RAG_Embedding_Data",
                                           feature_type + ".jsonl")
    if len(query_data_filename) == 0:
        return

    with open(query_data_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    # 检索
    for query in query_data:
        query_json = json.loads(query)
        if len(query_json["Feature"]) == 0 and len(query_json["Description"]) == 0:
            continue

        query_merged = ""
        for item in query_json["Feature"]:
            query_merged += item
        query_merged = query_merged + "," + query_json["Category"][0]
        docs = db.similarity_search(query_merged.lower(), k=4)
        mapping_docs = []  # 得到检索得到的docs的下标index
        for doc in docs:
            """
            if len(doc.page_content.split(":", 2)) != 3:
                print(doc)
                print(query)
                print('---------------')
            """
            # split的错误处理
            index_mapping_doc = doc.page_content.split(":", 2)[0]
            txt_mapping_docs = doc.page_content.split(":", 2)[1]
            """
            index_mapping_doc = doc.page_content.split(":", 2)[1]
            if len(doc.page_content.split(":", 2)) > 3:
                txt_mapping_docs = doc.page_content.split(":", 2)[2]
            else:
                txt_mapping_docs = ""
            """
            mapping_docs.append({"index": index_mapping_doc, "doc": txt_mapping_docs})

        mapping_result = {
            "index": query_json["index"],
            "doc": query_merged,
            "mapping docs": mapping_docs
        }
        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a)
            a.write("\n")


rag_feature_mapping("MariaDB", "TiDB", "functions", "Feature_Category")
rag_feature_mapping("MariaDB", "MySQL", "functions", "Feature_Category")
# rag_feature_mapping("MariaDB", "ClickHouse", "functions", "Feature_Category")
rag_feature_mapping("MariaDB", "ClickHouse", "functions", "Feature")

