# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/25 15:26
# @Author  : shaocanfan
# @File    : postgres_duckdb.py
# @Intro   :
from src.Connector import test_database_duckdb
import json
results_filenames = {
    "FixMCmpOpU":"../Dataset/MutateLLM/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl",
    "FixMDistinctL":"../Dataset/MutateLLM/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl",
    "FixMHaving1U":"../Dataset/MutateLLM/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl",
    "FixMOn1U":"../Dataset/MutateLLM/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMOn1U).jsonl"
}

def func1(mutate_name):
    with open(results_filenames[mutate_name], "r", encoding="utf-8") as r:lines = r.readlines()

    success_cnt = 0
    for line in lines:
        data = json.loads(line)
        result, exec_time, error_message = test_database_duckdb("TEST3", data["transferredSqlsim"])
        if result != None:
            success_cnt += 1
        print('------------------------------')
    print(success_cnt)


def func2(filename, item_key):
    with open(filename, "r", encoding="utf-8") as r:
        contents = json.load(r)

    index = 0
    success_cnt = 0
    for key, value in contents.items():
        for item in value:
            print(index)
            index += 1
            if item_key == "mutatedSqlsim_postgres":
                sql_statement = item[item_key]["mutated sql"]
            else:
                sql_statement = item[item_key]
            result, exec_time, error_message = test_database_duckdb("TEST3", sql_statement)
            if result != None:
                success_cnt += 1
            print('------------------------------')
    print(success_cnt)




# postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl:17/100
# postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl:59/100
# postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl:64/100
# postgres_testing_dataset_raw2.0(FixMOn1U).jsonl:47/100

# 检查postgres的100 x 4 条测试数据中，有多少条测试数据可以直接在duckdb中运行
# func1("FixMDistinctL")
# func1("FixMCmpOpU")
# func1("postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl")
# func1("postgres_testing_dataset_raw2.0(FixMOn1U).jsonl")


# 检查mutate llm关于postgres的训练集和测试集中，有多少数据可以直接在duckdb中运行
# postgres_training_dataset1.0.jsonl:32/80
# func2("../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset1.0.jsonl", "originalSqlsim_postgres")
# func2("../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset1.0.jsonl", "mutatedSqlsim_postgres")

# postgres_testing_dataset1.0.jsonl:43/80
# func2("../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset1.0.jsonl", "originalSqlsim_postgres")
# func2("../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset1.0.jsonl", "mutatedSqlsim_postgres")