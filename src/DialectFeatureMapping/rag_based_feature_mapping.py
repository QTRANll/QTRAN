# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/30 10:58
# @Author  : shaocanfan
# @File    : rag_based_feature_mapping.py
# @Intro   :

import json
import os
from langchain.prompts import ChatPromptTemplate
from src.Tools.JsonLoader.JSONLoader import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.callbacks import get_openai_callback
# from langchain_openai import OpenAIEmbeddings
# import chromadb
# import chromadb
# from langchain.vectorstores import Weaviate


from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini")

feature_knowledge_base = "FeatureKnowledgeBase"

# 合并每个feature type中所有的feature数据，并将它们以jsonl格式存储起来
def feature_knowledge_merge(db, feature_type):
    merge_data_filename = os.path.join("..", "..", feature_knowledge_base, db, "RAG_Embedding_Data", feature_type + ".jsonl")
    if not os.path.exists(merge_data_filename):
        # 创建embedding_data_filename
        feature_filepath = os.path.join("..", "..", feature_knowledge_base, db, feature_type, feature_type + "_Results")
        filenames = os.listdir(feature_filepath)
        feature_names = []
        for filename in filenames:
            with open(os.path.join(feature_filepath, filename), "r", encoding="utf-8") as r:
                value = json.load(r)
            with open(merge_data_filename, "a", encoding="utf-8") as a:
                json.dump(value, a)
                a.write("\n")
    else:
        print(merge_data_filename + ":已存在！")


# 合并不同类别的feature到一个jsonl文件
def feature_type_merge(db, feature_types):
    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    merge_feature_filename = os.path.join("..", "..", feature_knowledge_base, db, "RAG_Embedding_Data", names + ".jsonl")
    if not os.path.exists(merge_feature_filename):
        index_all = 0
        for feature_type in feature_types:
            embedding_data_filename = os.path.join("..", "..", feature_knowledge_base, db, "RAG_Embedding_Data", feature_type + ".jsonl")
            with open(embedding_data_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                value = json.loads(line)
                value["index"] = index_all
                index_all += 1
                with open(merge_feature_filename, "a", encoding="utf-8") as a:
                    json.dump(value, a)
                    a.write('\n')
    return merge_feature_filename


def load_feature_knowledge_embedding(db, feature_types, content_keys):
    names = "embedding"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    for content_key in content_keys:
        names = names + "_" + content_key
    embedding_data_filename = os.path.join("..", "..", feature_knowledge_base, db, "RAG_Embedding_Data",
                                           names + ".jsonl")
    if not os.path.exists(embedding_data_filename):
        names_ = "merge"
        for feature_type in feature_types:
            names_ = names_ + "_" + feature_type
        merge_feature_filename = os.path.join("..", "..", feature_knowledge_base, db, "RAG_Embedding_Data",
                                              names_ + ".jsonl")

        with open(merge_feature_filename, "r", encoding="utf-8") as r:
            lines = r.readlines()
        for line in lines:
            value = json.loads(line)
            # 获取feature的信息并将信息连接成字符串
            vector_txt = str(value["index"]) + ":"
            # 将所有content keys的内容拼接到字符串上
            for content_key in content_keys:
                vector_txt = vector_txt + content_key + ": "
                for txt in value[content_key]:
                    print(txt)
                    vector_txt += txt
                vector_txt += "\n"

            value["vector_txt"] = vector_txt  # 拼接所得的字符串的key为vector_txt
            with open(embedding_data_filename, "a", encoding="utf-8") as a:
                json.dump(value, a)
                a.write("\n")
    else:
        print(embedding_data_filename+":已存在！")

    loader = JSONLoader(file_path=embedding_data_filename, content_key="vector_txt", json_lines=True)
    data = loader.load()
    return data

def rag_feature_mapping_llm_v1(version_id, search_k, a_db, b_db, feature_types, content_keys):
    # 先为a_db,b_db的所有feature_types分别进行数据合并
    for feature_type in feature_types:
        feature_knowledge_merge(a_db, feature_type)
        feature_knowledge_merge(b_db, feature_type)

    # 为a_db,b_db的所有feature_types进行全部数据合并：用于存储所有类别的feature，将他们合并成一个文件
    a_merge_feature_filename = feature_type_merge(a_db, feature_types)
    feature_type_merge(b_db, feature_types)

    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0],
                                a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    # 读取被检索b_db的feature_type的embedding data
    data_b = load_feature_knowledge_embedding(b_db, feature_types, content_keys)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(data_b, embeddings)
    if search_k == 0:
        retriever = vectorstore.as_retriever()
    else:
        retriever = vectorstore.as_retriever(search_k=search_k)

    # 获取a_db的feature_type所有feature
    data_a = load_feature_knowledge_embedding(a_db, feature_types, content_keys)

    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    processed_lines_cnt = 0
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    response_schemas = [
        ResponseSchema(type="string", name="Feature", description='The mapping feature name'),
        ResponseSchema(type="string", name="Explanation", description='Explain the mapping reason.')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    for query in query_data:
        query_json = json.loads(query)
        print(query_json["index"])
        print("proce_line_cnt"+str(processed_lines_cnt))
        if query_json["index"] < processed_lines_cnt:
            continue

        # 后70个
        query_merged = """Use the following pieces of retrieved context to answer the question.
        Question: {question}
        Context: {context}
        Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}
        """

        feature_name = ""
        for item in query_json["Feature"]:
            feature_name += item

        prompt = ChatPromptTemplate.from_template(query_merged)
        chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser())
        cost = {}

        with get_openai_callback() as cb:
            resp = chain.invoke(
                "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?"
            )
            try:
                resp_json = output_parser.parse(resp)
            except Exception as e:
                resp_json = {"Feature":"","Explanation":""}
            resp_json["index"] = -1
            resp_json["Feature"] = [resp_json["Feature"]]
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算
        
        mapping_result = {
            "a_db": {
                "index": query_json["index"],
                "Feature": query_json["Feature"]
            },
            "b_db": resp_json,
            "cost": cost
        }

        print(mapping_result)
        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a, ensure_ascii=False)
            a.write("\n")


def rag_feature_mapping_llm_v2(version_id, search_k, a_db, b_db, feature_types, content_keys):
    # 先为a_db,b_db的所有feature_types分别进行数据合并
    for feature_type in feature_types:
        feature_knowledge_merge(a_db, feature_type)
        feature_knowledge_merge(b_db, feature_type)

    # 为a_db,b_db的所有feature_types进行全部数据合并：用于存储所有类别的feature，将他们合并成一个文件
    a_merge_feature_filename = feature_type_merge(a_db, feature_types)
    feature_type_merge(b_db, feature_types)

    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    # 读取被检索b_db的feature_type的embedding data
    data_b = load_feature_knowledge_embedding(b_db, feature_types, content_keys)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(data_b, embeddings)
    if search_k == 0:
        retriever = vectorstore.as_retriever()
    else:
        retriever = vectorstore.as_retriever(search_k=search_k)

    # 获取a_db的feature_type所有feature
    data_a = load_feature_knowledge_embedding(a_db, feature_types, content_keys)

    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    processed_lines_cnt = 0
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    response_schemas = [
        ResponseSchema(type="string", name="Feature", description='The mapping feature name'),
        ResponseSchema(type="string", name="Explanation", description='Explain the mapping reason.')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    for query in query_data:
        query_json = json.loads(query)
        print(query_json["index"])
        if query_json["index"] < processed_lines_cnt:
            continue

        # 后70个
        query_merged = """Use the following pieces of retrieved context to answer the question.
        Question: {question}
        Context: {context}
        Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}
        """

        feature_name = ""
        for item in query_json["Feature"]:
            feature_name += item
        prompt = ChatPromptTemplate.from_template(query_merged)
        chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser())

        cost = {}
        with get_openai_callback() as cb:
            resp = chain.invoke(
                "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?" + data_a[query_json["index"]].page_content
            )

            resp_json = output_parser.parse(resp)
            resp_json["index"] = -1
            resp_json["Feature"] = [resp_json["Feature"]]
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算

        mapping_result = {
            "a_db": {
                "index": query_json["index"],
                "Feature": query_json["Feature"]
            },
            "b_db": resp_json,
            "cost": cost
        }

        print(mapping_result)

        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a, ensure_ascii=False)
            a.write("\n")

def rag_feature_mapping_llm_v3(version_id, search_k, a_db, b_db, feature_types, content_keys):
    for feature_type in feature_types:
        feature_knowledge_merge(a_db, feature_type)
        feature_knowledge_merge(b_db, feature_type)

    # 为a_db,b_db的所有feature_types进行全部数据合并：用于存储所有类别的feature，将他们合并成一个文件
    a_merge_feature_filename = feature_type_merge(a_db, feature_types)
    feature_type_merge(b_db, feature_types)

    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    # 读取被检索b_db的feature_type的embedding data
    data_b = load_feature_knowledge_embedding(b_db, feature_types, content_keys)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(data_b, embeddings)
    retriever = vectorstore.as_retriever()

    # 获取a_db的feature_type所有feature
    data_a = load_feature_knowledge_embedding(a_db, feature_types, content_keys)

    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    processed_lines_cnt = 0
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    response_schemas = [
        ResponseSchema(type="string", name="Feature", description='The mapping feature name'),
        ResponseSchema(type="string", name="Explanation", description='Explain the mapping reason.')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    for query in query_data:
        query_json = json.loads(query)
        print(query_json["index"])
        if query_json["index"] < processed_lines_cnt:
            continue

        # 后70个
        query_merged = """Use the following pieces of retrieved context to answer the question.
        Question: {question}
        Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}
        """

        feature_name = ""
        for item in query_json["Feature"]:
            feature_name += item
        prompt = ChatPromptTemplate.from_template(query_merged)
        chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser())

        cost = {}
        with get_openai_callback() as cb:
            resp = chain.invoke(
                "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?"
            )
            resp_json = output_parser.parse(resp)
            resp_json["index"] = -1
            resp_json["Feature"] = [resp_json["Feature"]]
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算

        mapping_result = {
            "a_db": {
                "index": query_json["index"],
                "Feature": query_json["Feature"]
            },
            "b_db": resp_json,
            "cost": cost
        }

        print(mapping_result)

        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a, ensure_ascii=False)
            a.write("\n")


def rag_feature_mapping_llm_v4(version_id, search_k, a_db, b_db, feature_types, content_keys):
    # 先为a_db,b_db的所有feature_types分别进行数据合并
    for feature_type in feature_types:
        feature_knowledge_merge(a_db, feature_type)
        feature_knowledge_merge(b_db, feature_type)

    # 为a_db,b_db的所有feature_types进行全部数据合并：用于存储所有类别的feature，将他们合并成一个文件
    a_merge_feature_filename = feature_type_merge(a_db, feature_types)
    feature_type_merge(b_db, feature_types)

    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0],
                                a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    # 读取被检索b_db的feature_type的embedding data
    data_b = load_feature_knowledge_embedding(b_db, feature_types, content_keys)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(data_b, embeddings)
    if search_k == 0:
        retriever = vectorstore.as_retriever()
    else:
        retriever = vectorstore.as_retriever(search_k=search_k)

    # 获取a_db的feature_type所有feature
    data_a = load_feature_knowledge_embedding(a_db, feature_types, content_keys)


    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", a_db, "RAG_Embedding_Data",
                                          names + ".jsonl")
    with open(merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    b_names = "merge"
    for feature_type in feature_types:
        b_names = b_names + "_" + feature_type
    b_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", b_db, "RAG_Embedding_Data",
                                            b_names + ".jsonl")
    with open(b_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        b_query_data = read_lines.readlines()

    processed_lines_cnt = 0
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    for query in query_data:
        query_json = json.loads(query)
        print(query_json["index"])
        print(query_json)
        if query_json["index"] < processed_lines_cnt:
            continue

        feature_name = ""
        for item in query_json["Feature"]:
            feature_name += item

        cost = {}
        with get_openai_callback() as cb:
            query_temp = "About the feature " + feature_name + " in " + a_db + ", which feature has most similar function in " + b_db + "?"
            docs = retriever.get_relevant_documents(query_temp)
            # 提取文档内容字符串
            if docs:  # 检查是否有返回结果
                top_doc_content = docs[0].page_content  # 获取第一个文档的内容
            else:
                top_doc_content = "-1:"
            print(top_doc_content)
            index_temp = int(top_doc_content.split(":")[1].strip())
            feature_temp = json.loads(b_query_data[index_temp])["Feature"]
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算
            mapping_result = {
                "a_db": {
                    "index": query_json["index"],
                    "Feature": query_json["Feature"]
                },
                "b_db": {
                    "index": index_temp,
                    "Feature": feature_temp,
                    "Explanation": ""
                },
                "cost": cost
            }

        print(mapping_result)
        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a, ensure_ascii=False)
            a.write("\n")


def rag_feature_mapping_llm(version_id, search_k, a_db, b_db, feature_types, content_keys):
    # feature_type:mapping的feature 种类，content_key:mapping的vector中包含的keys
    if version_id == 1:
        rag_feature_mapping_llm_v1(version_id, search_k, a_db, b_db, feature_types, content_keys)
    elif version_id == 2:
        rag_feature_mapping_llm_v2(version_id, search_k, a_db, b_db, feature_types, content_keys)
    elif version_id == 3:
        rag_feature_mapping_llm_v3(version_id, search_k, a_db, b_db, feature_types, content_keys)
    elif version_id == 4:
        rag_feature_mapping_llm_v4(version_id, search_k, a_db, b_db, feature_types, content_keys)


def rag_feature_mapping_llm_temp(version_id, a_db, b_db, feature_types, content_keys):
    # 先为a_db,b_db的所有feature_types分别进行数据合并
    for feature_type in feature_types:
        feature_knowledge_merge(a_db, feature_type)
        feature_knowledge_merge(b_db, feature_type)

    # 为a_db,b_db的所有feature_types进行全部数据合并：用于存储所有类别的feature，将他们合并成一个文件
    a_merge_feature_filename = feature_type_merge(a_db, feature_types)
    feature_type_merge(b_db, feature_types)

    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, a_db + "_mapping_" + b_db + "_" + str(version_id) + ".jsonl")
    # 读取被检索b_db的feature_type的embedding data
    data_b = load_feature_knowledge_embedding(b_db, feature_types, content_keys)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(data_b, embeddings)
    retriever = vectorstore.as_retriever()

    # 获取a_db的feature_type所有feature
    data_a = load_feature_knowledge_embedding(a_db, feature_types, content_keys)

    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    processed_lines_cnt = 0
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    response_schemas = [
        ResponseSchema(type="string", name="Feature", description='The mapping feature name'),
        ResponseSchema(type="string", name="Explanation", description='Explain the mapping reason.')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    for query in query_data:
        query_json = json.loads(query)
        print(query_json["index"])
        if query_json["index"] < processed_lines_cnt:
            continue

        # 后70个
        query_merged = """Use the following pieces of retrieved context to answer the question.
        Question: {question}
        Context: {context}
        Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}
        """

        feature_name = ""
        for item in query_json["Feature"]:
            feature_name += item
        prompt = ChatPromptTemplate.from_template(query_merged)
        chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser())

        cost = {}
        with get_openai_callback() as cb:
            resp = chain.invoke(
                "关于" + a_db + "中的feature " + feature_name + "，" + b_db + "中与之功能相似的feature名称是什么？" + data_a[query_json["index"]].page_content
            )

            """
            resp = chain.invoke(
                "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db +"?"
            )
            """
            resp_json = output_parser.parse(resp)
            resp_json["index"] = -1
            resp_json["Feature"] = [resp_json["Feature"]]
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算

        mapping_result = {
            "a_db": {
                "index": query_json["index"],
                "Feature": query_json["Feature"]
            },
            "b_db": resp_json,
            "cost": cost
        }

        print(mapping_result)

        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(mapping_result, a, ensure_ascii=False)
            a.write("\n")


def rag_feature_mapping_process(version_id, search_k, a_db, b_db, feature_types, content_keys):
    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    with open(dir_filename, "r", encoding="utf-8") as r:
        lines = r.readlines()

    processed_dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + "_processed" + ".jsonl")
    processed_lines_cnt = 0
    if os.path.exists(processed_dir_filename):
        with open(processed_dir_filename, "r", encoding="utf-8") as direct_file_r:
            processed_lines_cnt = sum(1 for line in direct_file_r)

    a_names = "merge"
    for feature_type in feature_types:
        a_names = a_names + "_" + feature_type
    a_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", a_db, "RAG_Embedding_Data",
                                            a_names + ".jsonl")
    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        a_merge_data = read_lines.readlines()

    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", b_db, "RAG_Embedding_Data",
                                          names + ".jsonl")
    with open(merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    mapping_success_cnt = 0
    mapping_fail_cnt = {}
    mapping_category_cnt = {}
    for line in lines:
        value = json.loads(line)
        value_origin = value
        if value["a_db"]["index"] < processed_lines_cnt:
            continue
        print(value["a_db"]["index"])

        a_value_json = json.loads(a_merge_data[value["a_db"]["index"]])

        if a_value_json["Category"][0] not in mapping_category_cnt:
            mapping_category_cnt[a_value_json["Category"][0]] = 1
        else:
            mapping_category_cnt[a_value_json["Category"][0]] += 1

        # 处理前面llm生成的结果，在b_db中匹配寻找对应的feature
        # 先以feature name 进行匹配（直接匹配），如果没有匹配到则以rag进行寻找（近似匹配）
        b_db_json = value["b_db"]
        b_db_feature = b_db_json["Feature"][0].split("(")[0].strip()
        # 直接匹配
        flag = False  # 用于标记该条feature是否成功完全匹配到mapping feature
        for query in query_data:
            query_json = json.loads(query)
            query_json_feature = query_json["Feature"][0].split("(")[0].strip()
            if query_json_feature.lower() == b_db_feature.lower():
            # if len(query_json_feature) and query_json_feature.lower() in b_db_feature.lower() or b_db_feature.lower() in query_json_feature.lower():
                b_db_json["index"] = query_json["index"]
                b_db_json["Feature"] = query_json["Feature"]
                print("直接匹配：")
                print(value_origin)
                value["b_db"] = b_db_json
                print(value)
                print('--------------')
                flag = True
                break
        if not flag:
            # print(a_value_json["Category"][0])
            if a_value_json["Category"][0] not in mapping_fail_cnt:
                mapping_fail_cnt[a_value_json["Category"][0]] = 1
            else:
                mapping_fail_cnt[a_value_json["Category"][0]] += 1

            # print(b_db_feature)

            # 该feature未成功完全匹配到mapping feature：进行RAG相似度检索，取k=1
            data_b = load_feature_knowledge_embedding(b_db, feature_types, ["Feature"])
            embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = Chroma.from_documents(data_b, embeddings)
            retriever = vectorstore.as_retriever()
            # 查询检索器并获取最相似的文档
            query = "Which feature in " + b_db + " is most similar to the feature " + b_db_feature  # 替换为你的查询语句
            docs = retriever.get_relevant_documents(query)
            # 提取文档内容字符串
            if docs:  # 检查是否有返回结果
                top_doc_content = docs[0].page_content  # 获取第一个文档的内容
                b_db_json["index"] = int(top_doc_content.split(":")[1].strip())
                b_db_json["Feature"] = json.loads(query_data[b_db_json["index"]])["Feature"]
                print("RAG检索：")
                print(value_origin)
                value["b_db"] = b_db_json
                print(value)
                print('--------------')
            else:
                print("未找到相似的文档")
        else:
            mapping_success_cnt += 1
        # 将process后的信息进行存储

        with open(processed_dir_filename, "a", encoding="utf-8") as a:
            json.dump(value, a)
            a.write('\n')
    print("mapping 字符串匹配直接成功的个数：" + str(mapping_success_cnt))
    print("mapping 字符串匹配失败的各个类别占比：")
    for key_, value_ in mapping_fail_cnt.items():
        print(key_+":"+str(value_/mapping_category_cnt[key_]))


def rag_feature_mapping_count(version_id, search_k, a_db, b_db, feature_types, content_keys):
    dir_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + ".jsonl")
    with open(dir_filename, "r", encoding="utf-8") as r:
        lines = r.readlines()

    a_names = "merge"
    for feature_type in feature_types:
        a_names = a_names + "_" + feature_type
    a_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", a_db, "RAG_Embedding_Data",
                                            a_names + ".jsonl")
    with open(a_merge_feature_filename, "r", encoding="utf-8") as read_lines:
        a_merge_data = read_lines.readlines()

    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", b_db, "RAG_Embedding_Data",
                                          names + ".jsonl")
    with open(merge_feature_filename, "r", encoding="utf-8") as read_lines:
        query_data = read_lines.readlines()

    mapping_success_cnt = 0
    mapping_fail_cnt = {}
    mapping_category_cnt = {}
    cnt = 0
    for line in lines:
        value = json.loads(line)
        value_origin = value
        # print(value["a_db"]["index"])

        a_value_json = json.loads(a_merge_data[value["a_db"]["index"]])

        if a_value_json["Category"][0] not in mapping_category_cnt:
            mapping_category_cnt[a_value_json["Category"][0]] = 1
        else:
            mapping_category_cnt[a_value_json["Category"][0]] += 1

        # 处理前面llm生成的结果，在b_db中匹配寻找对应的feature
        # 先以feature name 进行匹配（直接匹配），如果没有匹配到则以rag进行寻找（近似匹配）
        b_db_json = value["b_db"]
        b_db_feature = b_db_json["Feature"][0].split("(")[0].strip()
        # 直接匹配
        flag = False  # 用于标记该条feature是否成功完全匹配到mapping feature
        for query in query_data:
            query_json = json.loads(query)
            query_json_feature = query_json["Feature"][0].split("(")[0].strip()
            if query_json_feature.lower() == b_db_feature.lower():
            # if len(query_json_feature) and query_json_feature.lower() in b_db_feature.lower() or b_db_feature.lower() in query_json_feature.lower():
                flag = True
                break
        if not flag:
            print(value)
            if a_value_json["Category"][0] not in mapping_fail_cnt:
                mapping_fail_cnt[a_value_json["Category"][0]] = 1
            else:
                mapping_fail_cnt[a_value_json["Category"][0]] += 1
        else:
            mapping_success_cnt += 1
        # 将process后的信息进行存储

    print("mapping 字符串匹配直接成功的个数：" + str(mapping_success_cnt))
    print("mapping 字符串匹配失败的个数：" + str(len(lines)-mapping_success_cnt))
    print('\n')
    print("mapping 字符串匹配失败的各个类别占比：")
    for key_, value_ in mapping_category_cnt.items():
        fail_cnt = mapping_fail_cnt[key_] if key_ in mapping_fail_cnt else 0
        print(key_+":"+str(fail_cnt/value_) + "(" + str(fail_cnt)+"/"+str(value_)+")")
