# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/16 17:50
# @Author  : shaocanfan
# @File    : sql_execute_error_analyzer.py
# @Intro   : 统计结果文件中sql语句执行报错原因，统计错误原因及对应的数量和比例
import json
import re

def execute_error_analyzer(execute_results_filename):
    with open(execute_results_filename, "r", encoding="utf-8") as r:
        lines = r.readlines()
    execute_errors_cnt = 0
    execute_errors = {}
    for line in lines:
        result = json.loads(line)
        if result["TransferSqlExecError"] != "None":
            execute_errors_cnt += 1
        # 使用正则表达式提取内容
        pattern = r'\(psycopg2\.errors\.\w+\)'
        # pattern = r'\.errors\.(\w+)'
        pattern = r'\.(\w+)\)'
        match = re.search(pattern, result["TransferSqlExecError"])
        if match:
            error_str = match.group(1)
            if error_str in execute_errors:
                execute_errors[error_str] += 1
            else:
                execute_errors[error_str] = 1

    return execute_errors


def execute_error_analyzer_transferllm(execute_results_filename):
    with open(execute_results_filename, "r", encoding="utf-8") as r:
        lines = json.load(r)
    execute_errors_cnt = 0
    execute_errors = {}
    for result in lines:
        # 使用正则表达式提取内容
        pattern = r'\(psycopg2\.errors\.\w+\)'
        # pattern = r'\.errors\.(\w+)'
        pattern = r'\.(\w+)\)'
        for item in result["TransferSqlExecError"]:
            if item != "None":
                execute_errors_cnt += 1
                match = re.search(pattern, item)
                if match:
                    error_str = match.group(1)
                    if error_str in execute_errors:
                        execute_errors[error_str] += 1
                    else:
                        execute_errors[error_str] = 1
    return execute_errors


execute_errors = execute_error_analyzer_transferllm("../../Dataset/Pinolo Output/output_test_results/ALL/iterated_fewshot_output1_mariadb_to_postgres_1_240_originalSqlsim_all.json")
print(execute_errors)
cnt = 0
for key, value in execute_errors.items():
    cnt += value
print(cnt)

execute_errors = execute_error_analyzer_transferllm("../../Dataset/Pinolo Output/output_test_results/RANDOM/iterated_fewshot_output1_mariadb_to_postgres_240_400_originalSqlsim_random_100.json")
print(execute_errors)
cnt = 0
for key, value in execute_errors.items():
    cnt += value
print(cnt)
