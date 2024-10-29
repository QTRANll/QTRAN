# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/24 14:13
# @Author  : zql
# @File    : Deduplicate_and Classify.py
# @Intro   : 对MySQL的关于functions和operators的所有信息进行去重和分类
import json
import os

Functions_Categories = {
    "14.1": "Built-In Functions",
    "14.2": "Loadable Functions",
    "14.4.2": "Comparison Functions",
    "14.5": "Flow Control Functions",
    "14.6.2": "Mathematical Functions",
    "14.7": "Date and Time Functions",
    "14.8": "String Functions",
    "14.10": "Cast Functions",
    "14.11": "XML Functions",
    "14.12": "Bit Functions",
    "14.13": "Encryption and Compression Functions",
    "14.14": "Locking Functions",
    "14.15": "Information Functions",
    "14.16": "Spatial Analysis Functions",
    "14.17": "JSON Functions",
    "14.18": "Replication Functions",
    "14.19": "Aggregate Functions",
    "14.20": "Window Functions",
    "14.21": "Performance Schema Functions",
    "14.22": "Internal Functions",
    "14.23": "Miscellaneous Functions"
}

Operators_Categories = {
    "14.1": "Built-In Operators",
    "14.4.2": "Comparison Operators",
    "14.4.3": "Logical Operators",
    "14.4.4": "Assignment Operators",
    "14.6.1": "Arithmetic Operators",
    "14.8": "String Operators",
    "14.10": "Cast Operators",
    "14.12": "Bit Operators"
}


def deduplicate_process(results_dicname, results_merged_filename):
    results_filenames = os.listdir(results_dicname)

    if os.path.exists(results_merged_filename):
        print("文件 " + results_merged_filename + " 已存在！")
        return

    results_merged = {}
    for filename in results_filenames:
        with open(results_dicname + '/' + filename, "r", encoding="utf-8") as f:
            contents = json.load(f)

        for result in contents:
            if result["Feature"] == "":
                continue
            if result["Feature"] not in results_merged:
                results_merged[result["Feature"]] = result
            elif result["Feature"] in results_merged:
                temp = results_merged[result["Feature"]]
                temp["Title"] += result["Title"]
                temp["HTML"] += result["HTML"]
                if result["Category"] not in temp["Category"]:
                    temp["Category"] += result["Category"]
                results_merged[result["Feature"]] = temp

    with open(results_merged_filename, 'a', encoding='utf-8') as f:
        json.dump(results_merged, f, indent=4)


def results_category(dic_name, category_array, results_merged_filename):
    with open(results_merged_filename, "r", encoding="utf-8") as f:
        results_contents = json.load(f)

    for key_cat, value_cat in category_array.items():
        dir_filename = dic_name + "/" + value_cat + ".json"
        if os.path.exists(dir_filename):
            continue
        info_selected = {}
        for key_res, value_res in results_contents.items():
            if value_cat in value_res["Category"]:
                info_selected[key_res] = value_res
        with open(dir_filename, 'a', encoding='utf-8') as f:
            json.dump(info_selected, f, indent=4)


prefix = "../../../Feature Knowledge Base/MySQL/"
# 对结果进行去重，并合并到results_merged文件中
Results_Dicname = prefix + "Functions_and_Operators/Functions_Results"
Results_Merged_Filename = prefix + "Functions_and_Operators/Results_merged.json"
deduplicate_process(Results_Dicname, Results_Merged_Filename)

# 为去重后的数据进行分类，存储到results_category文件夹中
Dic_Name_Functions = prefix + "Functions_and_Operators/Functions_Results_Category/Functions_Category"
Category_Array_Functions = Functions_Categories
Dic_Name_Operators = prefix + "Functions_and_Operators/Functions_Results_Category/Operators_Category"
Category_Array_Operators = Operators_Categories
Results_Merged_Filename = prefix + "Functions_and_Operators/Results_merged.json"

results_category(Dic_Name_Functions, Category_Array_Functions, Results_Merged_Filename)
results_category(Dic_Name_Operators, Category_Array_Operators, Results_Merged_Filename)

# 统计并打印数量
count = 0
dic_name_fun = prefix + "Functions_and_Operators/Functions_Results_Category/Functions_Category"
filenames_dic = os.listdir(dic_name_fun)
dic_name_op = prefix + "Functions_and_Operators/Functions_Results_Category/Operators_Category"
filenames_op = os.listdir(dic_name_op)

for filename_dic in filenames_dic:
    with open(dic_name_fun + '/' + filename_dic, "r", encoding="utf-8") as rf:
        results = json.load(rf)
    count = count + len(results)

for filename_dic in filenames_op:
    with open(dic_name_op + '/' + filename_dic, "r", encoding="utf-8") as rf:
        results = json.load(rf)
    count = count + len(results)

print(count)
