# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/16 16:12
# @Author  : zql
# @File    : HTMLs_Category_Classifier.py
# @Intro   : 分类OceanBase的Mysql模式和Oracle模式下，关于functions，operators和sql statements的所有htmls


import json
import os


# 为HTMLs进行分类
def htmls_category(category, functions_end, txt_filename, dir_filename):
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return

    htmls = []  # 获取txt的每行数据
    htmls_category = {}

    with open(txt_filename, 'r', encoding='utf-8') as f:
        for line in f:
            htmls.append(line)

    ptr = 0
    for index in range(len(functions_end)):
        function_end = functions_end[index]
        htmls_results = {}
        while htmls[ptr].split(":", 1)[0].strip() != function_end:
            title = htmls[ptr].split(":", 1)[0].strip()
            html = htmls[ptr].split(":", 1)[1].strip()
            htmls_results[title] = html
            ptr = ptr + 1
        title = htmls[ptr].split(":", 1)[0].strip()
        html = htmls[ptr].split(":", 1)[1].strip()
        htmls_results[title] = html
        ptr = ptr + 1
        htmls_category[category[index]] = htmls_results

    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(htmls_category, f, indent=4, ensure_ascii=False)




prefix = "../../../Feature Knowledge Base/OceanBase/"

# 系统租户：考虑，OceanBase 数据库管理命令的使用参考信息
administrations_statements_categories = [
    "No Category"
]

administrations_statements_ends = [
    "SHOW RESTORE PREVIEW"
]

administrations_statements_categories_filename = prefix + "Database_Administration_Statements/Database_Administration_Statements_HTMLs_Category.json"
administrations_statements_categories_txt_filename = prefix + "Database_Administration_Statements/Database_Administration_Statements_HTMLs.txt"

# 普通租户（MySQL模式）：函数部分
functions_mysql_categories = [
        "Date and Time Functions",
        "String Functions",
        "Cast Functions",
        "Mathematical Functions",
        "Comparison Functions",
        "Flow Control Functions",
        "Aggregate Functions",
        "Analysis Functions",
        "Encryption Functions",
        "Information Functions",
        "JSON Functions",
        "XML Functions",
        "Spatial Functions",
        "Performance Schema Functions",
        "Locking Functions",
        "Miscellaneous Functions"
    ]

functions_mysql_ends = [
        "DAY",
        "SOUNDEX",
        "TIMESTAMP_TO_SCN",
        "ZIPF",
        "LEAST",
        "ORA_DECODE",
        "VARIANCE",
        "VARIANCE",
        "VALIDATE_PASSWORD_STRENGTH",
        "OB_VERSION",
        "JSON_SCHEMA_VALIDATION_REPORT",
        "UPDATEXML",
        "几何处理函数",
        "FORMAT_PICO_TIME",
        "RELEASE_LOCK",
        "VALUES"
    ]

functions_mysql_categories_filename = prefix + "Functions_MySQL/Functions_MySQL_HTMLs_Category.json"
functions_mysql_categories_txt_filename = prefix + "Functions_MySQL/Functions_MySQL_HTMLs.txt"

#  普通租户（Oracle模式）：函数部分
functions_oracle_categories = [
    "Numeric Functions",
    "Character Functions Returning CharacterValues",
    "Character Functions Returning NumberValues",
    "Datetime Functions",
    "General Comparison Functions",
    "Conversion Functions",
    "Encoding and Decoding Functions",
    "NULL-Related Functions",
    "Environment and Identifier Functions",
    "Hierarchical Functions",
    "JSON Functions",
    "XML Functions",
    "Spatial Functions",
    "Aggregate Functions",
    "Analytic Functions",
    "Information Functions"
    ]

functions_oracle_ends = [
    "ZIPF",
    "UPPER",
    "REGEXP_INSTR",
    "TZ_OFFSET",
    "LEAST",
    "UNISTR",
    "VSIZE",
    "NVL2",
    "OB_VERSION",
    "SYS_CONNECT_BY_PATH",
    "JSON_MERGEPATCH",
    "DELETEXML",
    "SDO_GEOMETRY 格式转换函数",
    "GROUPING_ID",
    "WMSYS.WM_CONCAT/WM_CONCAT",
    "OB_TRANSACTION_ID"
    ]

functions_oracle_categories_filename = prefix + "Functions_Oracle/Functions_Oracle_HTMLs_Category.json"
functions_oracle_categories_txt_filename = prefix + "Functions_Oracle/Functions_Oracle_HTMLs.txt"


#  普通租户（MySQL模式）：SQL语句部分
statements_mysql_categories = [
    "No Category"
]

statements_mysql_ends = [
    "VALUES"
]

statements_mysql_categories_filename = prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_HTMLs_Category.json"
statements_mysql_categories_txt_filename = prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_HTMLs.txt"


#  普通租户（Oracle模式）：SQL语句部分
statements_oracle_categories = [
    "DDL",
    "DML",
    "DCL"
]

statements_oracle_ends = [
    "MAJOR 和 MINOR",
    "UPDATE",
    "TRANSACTION"
]

statements_oracle_categories_filename = prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_HTMLs_Category.json"
statements_oracle_categories_txt_filename = prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_HTMLs.txt"



htmls_category(administrations_statements_categories, administrations_statements_ends, administrations_statements_categories_txt_filename, administrations_statements_categories_filename)
htmls_category(functions_mysql_categories, functions_mysql_ends, functions_mysql_categories_txt_filename, functions_mysql_categories_filename)
htmls_category(functions_oracle_categories, functions_oracle_ends, functions_oracle_categories_txt_filename, functions_oracle_categories_filename)
htmls_category(statements_mysql_categories, statements_mysql_ends, statements_mysql_categories_txt_filename, statements_mysql_categories_filename)
htmls_category(statements_oracle_categories, statements_oracle_ends, statements_oracle_categories_txt_filename, statements_oracle_categories_filename)
