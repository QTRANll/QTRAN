# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/10 17:12
# @Author  : shaocanfan
# @File    : feature_knowledge_base_processor.py
# @Intro   : 处理前面第一轮爬取的（mysql，tidb，oceanbase）数据库的信息，将信息格式重新编排统一
import json
import os
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
                json.dump(data, w)
                w.write('\n')

def processor(source_dic_name, direcct_din_name, type):
    # 注意处理重复的情况
    filenames = os.listdir(source_dic_name)
    for file in filenames:
        with open(os.path.join(source_dic_name, file), "r", encoding="utf-8") as r:
            value = json.load(r)
            # 排除feature为空的
            if len(value["Feature"]) == 0:
                print(file)
                continue

            new_value = value
            new_value["HTML"] = [value["HTML"]]
            new_value["Title"] = [value["Title"]]
            # 存储到results中
            file_cnt = len(os.listdir(direcct_din_name))
            direcct_filaname = os.path.join(direcct_din_name, str(file_cnt) + "_" + file)
            if os.path.exists(direcct_filaname):
                print(direcct_filaname + ":已存在")
            with open(direcct_filaname, "w", encoding="utf-8") as w:
                json.dump(new_value, w, indent=4)


def processor_temp(source_dic_name, direcct_din_name, type):
    # 注意处理重复的情况
    filenames = os.listdir(source_dic_name)
    for file in filenames:
        with open(os.path.join(source_dic_name, file), "r", encoding="utf-8") as r:
            value = json.load(r)
            # 排除feature为空的
            if len(value["Feature"]) == 0:
                print(file)
                continue
            print(value)

            if "Effective SQLs Generated2" in value:
                examples_temp = value["Effective SQLs Refined"] + value["Effective SQLs Generated1"] + value["Effective SQLs Generated2"]
            else:
                examples_temp = value["Effective SQLs Refined"] + value["Effective SQLs Generated1"]

            new_value = {
                "HTML": [value["HTML"]],
                "Title": [value["Title"]],
                "Feature": value["Feature"],
                "Description": value["Description"],
                "Examples": examples_temp,
                "Category": value["Category"]
            }
            # 存储到results中
            file_cnt = len(os.listdir(direcct_din_name))
            direcct_filaname = os.path.join(direcct_din_name, str(file_cnt) + "_" + file)
            if os.path.exists(direcct_filaname):
                print(direcct_filaname + ":已存在")

            with open(direcct_filaname, "w", encoding="utf-8") as w:
                json.dump(new_value, w, indent=4)


function_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/MariaDB/Functions/Results"
function_direct = "../../../Feature Knowledge Base/MariaDB/Functions/Results"
function_direct_category = "../../../Feature Knowledge Base/MariaDB/Functions/Results_Category"

op_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/MariaDB/Operators/Results"
op_direct = "../../../Feature Knowledge Base/MariaDB/Operators/Results"
op_direct_category = "../../../Feature Knowledge Base/MariaDB/Operators/Results_Category"

statement_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/MariaDB/SQL_Statements/SQL_Statements_Results"
statement_direct = "../../../Feature Knowledge Base/MariaDB/SQL_Statements/SQL_Statements_Results"
statement_direct_category = "../../../Feature Knowledge Base/MariaDB/SQL_Statements/SQL_Statements_Results_Category"


# processor(function_source, function_direct, "function")
# processor(op_source, op_direct, "op")
# processor(statement_source, statement_direct, "statement")

# 下面的函数只运行一次：add
# category_classifier(function_direct, function_direct_category)
# category_classifier(op_direct, op_direct_category)
# category_classifier(statement_direct, statement_direct_category)


function_source = "../../../Feature Knowledge Base Processed1/MariaDB_/Functions/Results"
function_direct = "../../../Feature Knowledge Base Processed1/MariaDB/Functions/Results"
function_direct_category = "../../../Feature Knowledge Base Processed1/MariaDB/Functions/Results_Category"

op_source = "../../../Feature Knowledge Base Processed1/MariaDB_/Operators/Results"
op_direct = "../../../Feature Knowledge Base Processed1/MariaDB/Operators/Results"
op_direct_category = "../../../Feature Knowledge Base Processed1/MariaDB/Operators/Results_Category"

# processor_temp(function_source, function_direct, "function")
processor_temp(op_source, op_direct, "op")
# processor_temp(statement_source, statement_direct, "statement")

# 下面的函数只运行一次：add
# category_classifier(function_direct, function_direct_category)
# category_classifier(op_direct, op_direct_category)
# category_classifier(statement_direct, statement_direct_category)