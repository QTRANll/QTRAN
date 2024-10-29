# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/10 17:12
# @Author  : shaocanfan
# @File    : feature_knowledge_base_processor.py
# @Intro   : 处理前面第一轮爬取的（mysql，tidb，oceanbase）数据库的信息，将信息格式重新编排统一
import json
import os
from src.FeatureKnowledgeBase_Code.crawler_options import sanitize_title
import glob

def category_classifier(results_dicname, results_category_dicname):
    # 对爬取的所有结果以category进行分类并存储到SQL_Statements_Results_Category中
    json_files = glob.glob(os.path.join(results_dicname, '*.json'))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as r:
            data = json.load(r)

        # 将结果存储到对应的jsonl文件中,可能属于多个类别
        for category in data["Category"]:
            with open(os.path.join(results_category_dicname, category + ".jsonl"), "a",encoding="utf-8") as w:
                json.dump(data, w, ensure_ascii=False)
                w.write('\n')


def processor(source_dic_name, direcct_din_name, direcct_din_name_category):
    # 注意处理重复的情况
    filenames = os.listdir(source_dic_name)
    for file in filenames:
        with open(os.path.join(source_dic_name, file), "r", encoding="utf-8") as r:
            data = json.load(r)
        for key, value in data.items():
            # 排除feature为空的
            if len(value["Feature"]) == 0:
                print(file)
                continue
            if "Title" in value:
                title_temp = value["Title"] if type(value["Title"]) == list else [value["Title"]]
            else:
                title_temp = value["Feature"] if type(value["HTML"]) == list else [value["Feature"]]
            new_value = {
                "HTML": value["HTML"] if type(value["HTML"]) == list else [value["HTML"]],
                "Title": title_temp,
                "Feature": [value["Feature"]],
                "Description": value["Description"] + value["Illustration"] if type(value["Description"]) == list else [value["Description"]] + value["Illustration"],
                "Examples": value["Examples"],
                "Category": value["Category"]
            }
            # 存储到results中
            # 为文件名加上前缀数字编号
            file_cnt = len(os.listdir(direcct_din_name))
            direcct_filaname = os.path.join(direcct_din_name, str(file_cnt) + "_" + sanitize_title(key.strip()) + ".json")
            if os.path.exists(direcct_filaname):
                print(direcct_filaname + ":已存在")
            with open(direcct_filaname, "w", encoding="utf-8") as w:
                json.dump(new_value, w, indent=4, ensure_ascii=False)


function_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/Functions_MySQL/Functions_MySQL_Results"
function_direct = "../../../Feature Knowledge Base/OceanBase_MySQL/Functions/Functions_Results"
function_direct_category = "../../../Feature Knowledge Base/OceanBase_MySQL/Functions/Functions_Results_Category"

op_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/Operators_MySQL/Operators_MySQL_Results_Category"
op_direct = "../../../Feature Knowledge Base/OceanBase_MySQL/Operators/Operators_Results"
op_direct_category = "../../../Feature Knowledge Base/OceanBase_MySQL/Operators/Operators_Results_Category"

statement_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/SQL_Statements_MySQL/SQL_Statements_MySQL_Results"
statement_direct = "../../../Feature Knowledge Base/OceanBase_MySQL/SQL_Statements/SQL_Statements_Results"
statement_direct_category = "../../../Feature Knowledge Base/OceanBase_MySQL/SQL_Statements/SQL_Statements_Results_Category"

# 下面的函数只运行一次：add
# processor(function_source, function_direct, function_direct_category)
# processor(op_source, op_direct, op_direct_category)
# processor(statement_source, statement_direct, statement_direct_category)


# 下面的函数只运行一次：add
# category_classifier(function_direct, function_direct_category)
# category_classifier(op_direct, op_direct_category)
# category_classifier(statement_direct, statement_direct_category)


function_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/Functions_Oracle/Functions_Oracle_Results"
function_direct = "../../../Feature Knowledge Base/OceanBase_Oracle/Functions/Functions_Results"
function_direct_category = "../../../Feature Knowledge Base/OceanBase_Oracle/Functions/Functions_Results_Category"

op_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/Operators_Oracle/Operators_Oracle_Results_Category"
op_direct = "../../../Feature Knowledge Base/OceanBase_Oracle/Operators/Operators_Results"
op_direct_category = "../../../Feature Knowledge Base/OceanBase_Oracle/Operators/Operators_Results_Category"

statement_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/OceanBase/SQL_Statements_Oracle/SQL_Statements_Oracle_Results"
statement_direct = "../../../Feature Knowledge Base/OceanBase_Oracle/SQL_Statements/SQL_Statements_Results"
statement_direct_category = "../../../Feature Knowledge Base/OceanBase_Oracle/SQL_Statements/SQL_Statements_Results_Category"

# 下面的函数只运行一次：add
# processor(function_source, function_direct, function_direct_category)
# processor(op_source, op_direct, op_direct_category)
# processor(statement_source, statement_direct, statement_direct_category)


# 下面的函数只运行一次：add
# category_classifier(function_direct, function_direct_category)
# category_classifier(op_direct, op_direct_category)
# category_classifier(statement_direct, statement_direct_category)