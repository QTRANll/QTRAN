# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/27 17:31
# @Author  : shaocanfan
# @File    : TransferLLMEvaluation.py
# @Intro   :

import json


def evaluate_sql_length(results, ranges):
    """分别评估固定区间内的成功率数据"""
    evaluations = {}
    for range_item in ranges:
        evaluation_temp = []
        low_length = range_item[0]
        high_length = range_item[1]

        results_len = 0
        exec_success_cnt = 0
        exec_result_equality_cnt = 0
        exec_fail_indexes = []
        exec_result_unequality_indexes = []
        transfer_changed_indexes = []
        no_iteration_exec_success_cnt = 0  # 第一次transfer就执行成功的数量
        error_iteration_cnt = 0  # 进行错误迭代的数目
        error_iteration_sucess_cnt = 0  # 进行错误迭代并且迭代后成功生成可执行sql的数目

        for result_item in results:
            if not (low_length <= result_item["SqlLength"] < high_length):
                continue

            if result_item["TransferResult"]:
                results_len += 1
            else:
                continue

            if result_item["Sql"] != result_item["TransferResult"][-1]["TransferSQL"]:
                transfer_changed_indexes.append(result_item["index"])

            if len(result_item["TransferSqlExecError"]) > 1:
                error_iteration_cnt += 1
                if result_item["TransferSqlExecError"][-1] == "None":
                    error_iteration_sucess_cnt += 1

            if result_item["TransferSqlExecError"][0] == "None":
                no_iteration_exec_success_cnt += 1
            if result_item["TransferSqlExecError"][-1] == "None":
                exec_success_cnt += 1
                # if result_item["TransferSqlExecEqualities"][-1] == True:
                if result_item["TransferSqlExecResult"][-1] == result_item["SqlExecResult"]:
                    exec_result_equality_cnt += 1
                else:
                    exec_result_unequality_indexes.append(result_item["index"])
            else:
                exec_fail_indexes.append(result_item["index"])

        if results_len == 0:
            continue


        print(range_item)
        print("单次转换(未错误迭代)执行成功/总样本：" + str(format(no_iteration_exec_success_cnt / results_len,'.3f')) + " (" + str(no_iteration_exec_success_cnt) + "/" + str(results_len) + ")")
        if error_iteration_cnt > 0:
            print("错误迭代/总样本：" + str(format(error_iteration_cnt / results_len,'.3f')) + " (" + str(error_iteration_cnt) + "/" + str(results_len) + ")")
            print("错误迭代执行成功/错误迭代：" + str(format(error_iteration_sucess_cnt / error_iteration_cnt,'.3f')) + " (" + str(error_iteration_sucess_cnt) + "/" + str(error_iteration_cnt) + ")")
           
        print("执行成功/总样本：" + str(format(exec_success_cnt / results_len,'.3f')) + " (" + str(exec_success_cnt) + "/" + str(results_len) + ")")
        # print("执行失败的下标："+str(exec_fail_indexes))
        print('--------------------------------------------------')
        if exec_success_cnt > 0:
            print("执行结果一致/执行成功：" + str(format(exec_result_equality_cnt / exec_success_cnt,'.3f')) + " (" + str(exec_result_equality_cnt) + "/" + str(exec_success_cnt) + ")")
        else:
            print("执行结果一致/执行成功："  + " (" + str(exec_result_equality_cnt) + "/" + str(exec_success_cnt) + ")")

        print("执行结果一致/总样本：" + str(format(exec_result_equality_cnt / results_len,'.3f')) + " (" + str(exec_result_equality_cnt) + "/" + str(results_len) + ")")
        # print("执行结果不一样的下标："+str(exec_result_unequality_indexes))
        print('--------------------------------------------------')
        # print("sql语句有修改的下标："+str(transfer_changed_indexes))
        # print("sql语句有修改的数量："+str(len(transfer_changed_indexes)))



        evaluation_temp.append(str(format(no_iteration_exec_success_cnt / results_len, '.3f')) + " (" + str(no_iteration_exec_success_cnt) + "/" + str(results_len) + ")")
        if error_iteration_cnt > 0:
            evaluation_temp.append(str(format(error_iteration_cnt / results_len, '.3f')) + " (" + str(error_iteration_cnt) + "/" + str(results_len) + ")")
            evaluation_temp.append(str(format(error_iteration_sucess_cnt / error_iteration_cnt, '.3f')) + " (" + str(error_iteration_sucess_cnt) + "/" + str(error_iteration_cnt) + ")")

        evaluation_temp.append(str(format(exec_success_cnt / results_len, '.3f')) + " (" + str(exec_success_cnt) + "/" + str(results_len) + ")")
        if exec_success_cnt > 0:
            evaluation_temp.append(str(format(exec_result_equality_cnt / exec_success_cnt, '.3f')) + " (" + str(exec_result_equality_cnt) + "/" + str(exec_success_cnt) + ")")
        else:
            evaluation_temp.append(" (" + str(exec_result_equality_cnt) + "/" + str(exec_success_cnt) + ")")
        evaluation_temp.append(str(format(exec_result_equality_cnt / results_len, '.3f')) + " (" + str(exec_result_equality_cnt) + "/" + str(results_len) + ")")

        # print("\n\n")
        evaluations[str(range_item)] = evaluation_temp
    return evaluations


def evaluate_transfer_llm(result_filename, ranges):
    with open(result_filename, "r", encoding="utf-8") as rf:
        results = json.load(rf)

    evaluations = evaluate_sql_length(results, ranges)

    print(result_filename)
    print(evaluations)
    print("\n\n\n")

    # ["单次转换(未错误迭代)执行成功/总样本：","错误迭代/总样本：","错误迭代执行成功/错误迭代：","执行成功/总样本：","执行结果一致/执行成功：","执行结果一致/总样本："]
    # ["单次转换(未错误迭代)执行成功/总样本：","执行成功/总样本：","执行结果一致/执行成功：","执行结果一致/总样本："]


