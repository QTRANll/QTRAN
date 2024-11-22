# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/10 17:12
# @Author  : shaocanfan
# @File    : feature_knowledge_base_processor.py
# @Intro   : 处理前面第一轮爬取的（mysql，tidb，oceanbase）数据库的信息，将信息格式重新编排统一
import json
import os
from src.Tools.Crawler.crawler_options import sanitize_title
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


def processor(source_dic_name, direcct_din_name, direcct_din_name_category):
    # 注意处理重复的情况
    filenames = os.listdir(source_dic_name)
    for file in filenames:
        with open(os.path.join(source_dic_name, file), "r", encoding="utf-8") as r:
            contents = json.load(r)
        for key, value in contents.items():
            # 排除feature为空的
            if len(value["Feature"]) == 0:
                print(file)
                continue
            if "Category" not in value:
                category_temp = [file.split(".")[0]]
            else:
                category_temp = value["Category"]
            new_value = {
                "HTML": value["HTML"],
                "Title": value["Title"],
                "Feature": [value["Feature"]],
                "Description": value["Description"] + value["Illustration"],
                "Examples": value["Examples"],
                "Category": category_temp
            }
            # 存储到results中
            file_cnt = len(os.listdir(direcct_din_name))
            direcct_filaname = os.path.join(direcct_din_name, str(file_cnt) + "_" + sanitize_title(new_value["Feature"][0]) + ".json")
            if os.path.exists(direcct_filaname):
                print(direcct_filaname + ":已存在")
            with open(direcct_filaname, "w", encoding="utf-8") as w:
                json.dump(new_value, w, indent=4)

            # 存储到category文件夹里
            # 将结果存储到对应的jsonl文件中,可能属于多个类别
            for category in new_value["Category"]:
                with open(os.path.join(direcct_din_name_category, category + ".jsonl"), "a", encoding="utf-8") as w:
                    json.dump(new_value, w)
                    w.write('\n')


function_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/sqlite/func"
function_direct = "../../../FeatureKnowledgeBase/sqlite/function/results"
function_direct_category = "../../../FeatureKnowledgeBase/sqlite/function/results_category"

op_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/sqlite/expr"
op_direct = "../../../FeatureKnowledgeBase/sqlite/operator/results"
op_direct_category = "../../../FeatureKnowledgeBase/sqlite/operator/results_category"

statement_source = "../../../Feature Knowledge Base_PINOLO_WithoutProcess/sqlite/statement"
statement_direct = "../../../FeatureKnowledgeBase/sqlite/SQL_Statements/SQL_Statements_Results"
statement_direct_category = "../../../FeatureKnowledgeBase/sqlite/SQL_Statements/SQL_Statements_Results_Category"

# 下面的函数只运行一次：add
# processor(function_source, function_direct, function_direct_category)
# processor(op_source, op_direct, op_direct_category)
