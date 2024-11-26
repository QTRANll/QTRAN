# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/17 16:39
# @Author  : shaocanfan
# @File    : dialect_feature_recognizer.py
# @Intro   : transfer a_db to b_db时，识别a_db sql中对于d_db是方言的所有feature元素(functions+operators)
import json
import os
import sqlglot
import re
from src.Tools.DatabaseConnect.database_connector import exec_sql_statement
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.chains import ConversationChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from src.DialectRecognition.TokenType_not_op import TokenType_not_op


effective_sqls_generator_v2_skip = [
    "BINLOG_GTID_POS.json",
    "COLUMN_ADD.json",
    "COLUMN_DELETE.json",
    "COLUMN_EXISTS.json",
    "COLUMN_GET.json",
    "COLUMN_JSON.json",
    "CROSSES.json",
    "LIKE.json",
    "MATCH AGAINST.json",
    "NEXT VALUE for sequence_name.json",
    "NOT LIKE.json",
    "NOT REGEXP.json",
    "OVERLAPS.json",
    "PERCENTILE_DISC.json",
    "PREVIOUS VALUE FOR sequence_name.json",
    "RLIKE.json",
    "SETVAL.json",
    "SPIDER_BG_DIRECT_SQL.json",
    "SPIDER_COPY_TABLES.json",
    "SPIDER_DIRECT_SQL.json",
    "ST_NUMGEOMETRIES.json",
    "VALUES _ VALUE.json",
    "VEC_DISTANCE.json",
    "WSREP_SYNC_WAIT_UPTO_GTID.json"
]



def tokenize_sql(sql):
    lists = sqlglot.tokenize(sql)
    return lists


# 判断枚举成员的名称
def is_member_name(name):
    return name in TokenType_not_op.__members__


def potential_features_refiner_single_sql(origin_sql):
    lists = tokenize_sql(origin_sql)  # 利用sqlglot分词函数得到origin_sql的分词列表
    val_indexes = []  # 类型为VAL的分词的下标
    function_name_indexes = []  # potential functions的分词的下标
    operator_indexes = []  # potential functions的分词的下标
    function_names = []  # potential functions的分词的下标
    operators = []  # potential functions的分词的下标

    # 遍历所有分词结果，refine operator features
    for index in range(len(lists)):
        if lists[index].token_type in [sqlglot.TokenType.VAR, sqlglot.TokenType.LEFT, sqlglot.TokenType.TIMESTAMP]:
            val_indexes.append(index)
        if not is_member_name(str(lists[index].token_type).split(".")[-1]):
            operator_indexes.append(index)
            operators.append(lists[index].text)

    # refine potential function features:sqlglot.TokenType.VAR后一个字符为sqlglot.TokenType.L_PAREN，且左边字符不为sqlglot.TokenType.UNKNOWN，则认为是potential functions
    for VAL_index in val_indexes:
        if VAL_index + 1 < len(lists) and lists[VAL_index+1].token_type == sqlglot.TokenType.L_PAREN and lists[VAL_index-1].token_type != sqlglot.TokenType.UNKNOWN and lists[VAL_index-1].text.lower() != "table":
            function_name_indexes.append(VAL_index)
            function_names.append(lists[VAL_index].text)

    print(origin_sql)
    """
    for item in lists:
        print(item)
    """
    """
    print("operators features")
    for index in operator_indexes:
        print(lists[index])

    print("function features")
    for index in function_name_indexes:
        print(lists[index])
    print('----------------')
    """

    return function_name_indexes, operator_indexes, function_names, operators


def potential_features_refiner(db_name, filename, dir_filename):
    # 从filename中获取测试集(数据库类型为db_name)，提取测试集中所有数据项的sql的potential features
    with open(filename, "r", encoding="utf-8") as r:
        contents = json.load(r)
    results = []
    for content in contents:
        # 遍历处理所有测试数据
        content["SqlPotentialFunctionIndexes"], content["SqlPotentialOperatorIndexes"],_,_ = potential_features_refiner_single_sql(content["Sql"])
        results.append(content)

    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(results, w, indent=4)



def potential_dialect_features_process_and_map(tool, a_db, b_db, source_filename, dir_filename, knowledge_base_dic, feature_types, search_k=0, version_id=1):
    """
    遍历a_db上origin_sql的所有potential features(functions+operators)，对每一个feature进行以下操作。
    * 在a_db的feature knowledge base processed中检索到该feature
    * 若未检索到该feature，先认为该feature为方言；若检索到该feature，选出最短的一个example sql作为方言检测example sql。
    * 在b_db引擎上执行该方言检测example sql，若无法执行则认为是dialect（虽然其中可能包括由于example sql中其他feature造成的无法执行，这里暂且粗略认为是方言）。
    * 统计：针对a_db的所有测试语句，potential dialect features/总features个数
    :return:
    """
    # 获取knowledge base的functions和operators的dic:Title及对应的json文件名
    features_dictionary = {}
    features_total_cnt = 0
    features_searched_fail_cnt = 0
    dialect_features_cnt = 0
    not_dialect_features_cnt = 0

    # 获取a_db的feature的详细信息，为了获取其examples供执行
    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    a_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase Processed1", a_db, "RAG_Embedding_Data", names + ".jsonl")
    with open(a_merge_feature_filename, "r", encoding="utf-8") as r:
        a_merge_features = r.readlines()

    # 获取a_db -> b_db的预先搭建好的mapping结果
    features_mapping_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + "_processed" + ".jsonl")
    with open(features_mapping_filename, "r", encoding="utf-8") as r:
        mapping_info = r.readlines()

    # 获取测试文件的数据内容
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as r:
            contents = r.readlines()
        with open(dir_filename, 'w'):
            pass
    else:
        with open(source_filename, "r", encoding="utf-8") as r:
            contents = json.load(r)

    results = []
    not_dialects = []
    for content in contents:
        if type(content) != dict:
            content = json.loads(content)
        potential_dialect = []
        not_potential_dialect = []
        potential_dialect_mapping_index = []  #存储potential dialect map的feature
        lists = tokenize_sql(content["Sql"])
        if feature_types[0] == "function":
            feature_indexes = content["SqlPotentialFunctionIndexes"]  # potential functions的分词的下标
        elif feature_types[0] == "operator":
            feature_indexes = content["SqlPotentialOperatorIndexes"]  # potential functions的分词的下标
        else:
            feature_indexes = []
        features_total_cnt += len(feature_indexes)

        # 处理potential features
        for index in feature_indexes:
            feature_name = str(lists[index].text)
            feature_searched_index = None
            # 在a_db的feature knowledge base processed中检索到该feature
            for line in a_merge_features:
                a_feature = json.loads(line)
                a_feature_Feature = ""
                for item in a_feature["Feature"]:
                    a_feature_Feature += item
                if str(feature_name).lower().strip() in a_feature_Feature.split("(")[0].lower().strip():
                    feature_searched_index = a_feature["index"]
                    break
            # 若未检索到该feature，先认为该feature为方言；若检索到该feature，选出最短的一个example sql作为方言检测example sql。
            if feature_searched_index:
                # 成功检索到，获取该feature的example信息
                feature_searched_content = json.loads(a_merge_features[feature_searched_index])
                # 选择最短的sql作为方言检测sql
                effective_sqls = feature_searched_content["Examples"]
                if len(effective_sqls):
                    dialect_recognize_sql = min(effective_sqls, key=len)
                    # 在b_db引擎上执行该方言检测example sql，若无法执行则认为是dialect（虽然其中可能包括由于example sql中其他feature造成的无法执行，这里暂且粗略认为是方言）。
                    exec_result, exec_time, error_message = exec_sql_statement(tool, b_db, dialect_recognize_sql)


                    if exec_result == None:
                        # 说明无法执行
                        dialect_features_cnt += 1
                        potential_dialect.append(feature_name)
                        # 为方言添加对应的mapping index
                        print(feature_searched_content)
                        potential_dialect_mapping_index.append([feature_searched_index, json.loads(mapping_info[feature_searched_index])["b_db"]["index"]])
                        print(json.loads(mapping_info[feature_searched_index]))
                    else:
                        not_dialect_features_cnt += 1
                        not_potential_dialect.append(feature_name)
                else:
                    dialect_features_cnt += 1
            else:
                # 未成功检索到
                features_searched_fail_cnt += 1
                dialect_features_cnt += 1

        if feature_types[0] == "function":
            content["SqlPotentialDialectFunction"] = potential_dialect
            content["SqlNotDialectFunction"] = not_potential_dialect
            content["SqlPotentialDialectFunctionMapping"] = potential_dialect_mapping_index
        elif feature_types[0] == "operator":
            content["SqlPotentialDialectOperator"] = potential_dialect
            content["SqlNotDialectOperator"] = not_potential_dialect
            content["SqlPotentialDialectOperatorMapping"] = potential_dialect_mapping_index
        else:
            pass

        not_dialects += not_potential_dialect

        results.append(content)
        # 存储
        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(content, a)
            a.write('\n')


    """
    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(results, w, indent=4)
    """

    print("feature总个数"+str(features_total_cnt))
    print("feature在knowledge base中检索失败的个数"+str(features_searched_fail_cnt))
    print("feature中方言的个数"+str(dialect_features_cnt))
    print("feature中非方言的个数" + str(not_dialect_features_cnt))

    print(not_dialects)



def sqlancer_potential_dialect_features_process_and_map(a_db, b_db, potential_dialect, feature_type, search_k=0, version_id=1):
    """
    遍历a_db上origin_sql的所有potential features(functions+operators)，对每一个feature(全部认为是方言)进行以下操作。
    * 在a_db的feature knowledge base中检索到该feature
    * 获取mapping结果并返回
    :return:
    """
    potential_dialect_mapping_index = []  # 存储potential dialect map的feature
    # 获取a_db -> b_db的预先搭建好的mapping结果
    features_mapping_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_type, a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + "_processed" + ".jsonl")
    if not os.path.exists(features_mapping_filename):
        return potential_dialect_mapping_index
    with open(features_mapping_filename, "r", encoding="utf-8") as r:
        mapping_info = r.readlines()

    # 处理potential features，获取potential dialect features和mapping结果

    for dialect in potential_dialect:
        map_searched_index = None
        # 在a_db -> b_db的预先搭建好的mapping结果中进行检索
        for info in mapping_info:
            map = json.loads(info)
            a_feature_Feature = ""
            for item in map["a_db"]["Feature"]:
                a_feature_Feature += item
            dialect_str = str(dialect).lower().strip()
            a_feature_str = a_feature_Feature.split("(")[0].lower().strip()
            if a_feature_str.startswith(dialect_str+"("):
                # 为方言添加对应的mapping index
                potential_dialect_mapping_index.append([map["a_db"]["index"],map["b_db"]["index"]])
                break
    return potential_dialect_mapping_index


def potential_dialect_features_recognizer(a_db, b_db, source_filename, dir_filename, knowledge_base_dic, search_k=0,version_id=1):
    potential_dialect_features_process_and_map(a_db, b_db, source_filename, dir_filename, knowledge_base_dic, ["function"], search_k=0,version_id=1)
    potential_dialect_features_process_and_map(a_db, b_db, source_filename, dir_filename, knowledge_base_dic,["operator"], search_k=0, version_id=1)

