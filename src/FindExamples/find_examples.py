# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/4 20:05
# @Author  : shaocanfan
# @File    : find_examples.py
# @Intro   :
import json
import os


def find_transfer_error_example():
    """
    需要一个original query和mutated query同时transfer然后不满足关系的例子
    之前做的是对original sql做 transfer，把mutated sql也transfer一下，两种sql比较结果。
    （original query和mutated query都transfer成功执行的；original query和mutated query执行结果符号给出oracle的）
    :return:
    """
    origin_transfer_result_filename = "../../Dataset/Pinolo Output/output_test_results/ALL/iterated_fewshot_output1_mariadb_to_postgres_1_240_originalSqlsim_all.json"
    mutate_transfer_result_filename = "../../Dataset/Pinolo Output/output_test_results/ALL/iterated_fewshot_output1_mariadb_to_postgres_1_240_mutatedSqlsim_all.json"

    with open(origin_transfer_result_filename, "r", encoding="utf-8") as r:
        origin_results = json.load(r)

    with open(mutate_transfer_result_filename, "r", encoding="utf-8") as r:
        mutate_results = json.load(r)

    for index in range(len(origin_results)):

        origin_res = origin_results[index]
        mutate_res = mutate_results[index]

        if len(mutate_res["TransferResult"]) == 0:
            continue

        if origin_res["TransferSqlExecResult"][-1] == "None" or mutate_res["TransferSqlExecResult"][-1] == "None":
            continue

        print(index)

        origin_sqlsim = mutate_res["originalSqlsim"]
        mutated_sqlsim = mutate_res["mutatedSqlsim"]

        transfer_origin_sqlsim = origin_res["TransferResult"][-1]["TransferSQL"]
        transfer_mutated_sqlsim = mutate_res["TransferResult"][-1]["TransferSQL"]

        print("origin_sqlsim:"+origin_sqlsim)
        print("mutated_sqlsim:"+mutated_sqlsim)
        print("transfer_origin_sqlsim:"+transfer_origin_sqlsim)
        print("transfer_mutated_sqlsim:"+transfer_mutated_sqlsim)
        print('-----------------')



find_transfer_error_example()