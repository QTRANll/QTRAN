# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/15 13:30
# @Author  : shaocanfan
# @File    : SQLGlot_test.py
# @Intro   : 测试sqlglot的方言转换，包括转换后语句的执行成功率，执行结果是否等价
import json
import os
import sqlite3
import sqlglot
from src.Connector import test_database_postgres, database_connection_args, test_database_mysql_like, test_database_sqlite
from src.OracleChecker.oracle_check import execSQL_result_convertor, Check
from src.OracleChecker.Result import Result
from src.TransferLLM.TransferLLM import load_data, sql_statement_process
from src.SQLExecuteErrorAnalyse.sql_execute_error_analyzer import execute_error_analyzer

def dialect_transfer_SQLGlot(origin_sql, read_db, write_db):
    # 如果是mysql_like转postgres，先把sql语句的列名进行替换，和postgres的ddl语句中的列名保持一致，便于后续语句转换
    if write_db == "postgres":
        sql_statement_processed = sql_statement_process(origin_sql)
    else:
        sql_statement_processed = origin_sql

    try:
        transferred_sql = sqlglot.transpile(sql_statement_processed, read=read_db, write=write_db)[0]
        TransferResult = {
            "TransferSQL": transferred_sql,
            "Explanation": ""
        }
    except Exception as e:
        transferred_sql = ""
        TransferResult = {
            "TransferSQL": transferred_sql,
            "Explanation": str(e)
        }
        print(e)
    # 执行方言转换前及转换后的语句并记录结果
    read_db_args = database_connection_args[read_db]
    write_db_args = database_connection_args[write_db]

    origin_result, origin_time, origin_message = test_database_mysql_like(read_db_args["db_type"], read_db_args["host"], read_db_args["port"], read_db_args["username"], read_db_args["password"], read_db_args["dbname"], origin_sql)
    transferred_result, transferred_time, transferred_message = test_database_postgres(write_db_args["db_type"], write_db_args["host"], write_db_args["port"], write_db_args["username"], write_db_args["password"], write_db_args["dbname"], transferred_sql)
    # 判断方言转换前后的语句是否可执行，执行结果是否等价
    converted_origin_result = execSQL_result_convertor(origin_result)
    converted_transferred_result = execSQL_result_convertor(transferred_result)

    # 创建 Result 对象
    origin_result_object = Result(converted_origin_result["column_names"], converted_origin_result["column_types"], converted_origin_result["rows"])
    transferred_result_object = Result(converted_transferred_result["column_names"], converted_transferred_result["column_types"], converted_transferred_result["rows"])

    end, error = Check(origin_result_object, transferred_result_object, True)
    end_, error_ = Check(transferred_result_object, origin_result_object, True)

    if end and end_:
        equal_flag = True
    else:
        equal_flag = False

    if not origin_message or not transferred_message:
        equal_flag = False
    return equal_flag, TransferResult, [origin_result, origin_time, origin_message], [transferred_result, transferred_time, transferred_message]


def load_sqls(sqls_filename):
    with open(sqls_filename, "r", encoding="utf-8") as r:
        contents = json.load(r)
    return contents

def SQLGlot_evaluate(origin_sqls_filename, transferred_results_filename, origin_db_name, transferred_db_name):
    if os.path.exists(transferred_results_filename):
        print(transferred_results_filename+":已存在\n")
        return
    sqls = load_sqls(origin_sqls_filename)
    sqls_num = len(sqls)
    origin_executable_cnt = 0
    transferred_success_cnt = 0
    transferred_executable_cnt = 0
    equal_cnt = 0
    for sql in sqls:
        equal_flag, transfer_result, origin_exec_results, transferred_exec_results = dialect_transfer_SQLGlot(sql["Sql"], origin_db_name, transferred_db_name)
        if equal_flag:
            equal_cnt += 1
        if transfer_result["TransferSQL"] != "":
            transferred_success_cnt += 1
        if not origin_exec_results[2]:
            origin_executable_cnt += 1
        if not transferred_exec_results[2]:
            transferred_executable_cnt += 1

        sql["SqlExecResult"] = str(origin_exec_results[0])
        sql["SqlExecTime"] = str(origin_exec_results[1])
        sql["SqlExecError"] = str(origin_exec_results[2])
        sql["TransferResult"].append(transfer_result)
        sql["TransferCost"].append({})
        sql["TransferSqlExecResult"] = str(transferred_exec_results[0])
        sql["TransferSqlExecTime"] = str(transferred_exec_results[1])
        sql["TransferSqlExecError"] = str(transferred_exec_results[2])
        sql["TransferSqlExecEqualities"].append(equal_flag)

        # 保存
        with open(transferred_results_filename, "a", encoding="utf-8") as w:
            json.dump(sql, w)
            w.write("\n")

    print("origin 可执行比例:" + str(origin_executable_cnt / sqls_num)+"("+str(origin_executable_cnt)+"/"+str(sqls_num)+")")
    print("transfer 成功比例:" + str(transferred_success_cnt / sqls_num)+"("+str(transferred_success_cnt)+"/"+str(sqls_num)+")")
    print("transfer 可执行比例:" + str(transferred_executable_cnt/sqls_num)+"("+str(transferred_executable_cnt)+"/"+str(sqls_num)+")")
    print("transfer 结果一致比例:"+str(equal_cnt/sqls_num)+"("+str(equal_cnt)+"/"+str(sqls_num)+")")


def SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, origin_db, transfer_db):
    SQLGlot_evaluate(origin_sqls_path, transferred_results_path, origin_db, transfer_db)
    execute_errors = execute_error_analyzer(transferred_results_path)
    print(execute_errors)
    cnt = 0
    for key, value in execute_errors.items():
        cnt += value
    print(cnt)



origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output1_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output1_mysql_to_postgres_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "postgres")

origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output2_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output2_mysql_to_postgres_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "postgres")

origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output1_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output1_mysql_to_duckdb_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "duckdb")

origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output2_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output2_mysql_to_duckdb_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "duckdb")



origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output1_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "sqlancer_output1_mysql_to_postgres_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "sqlancer_mysql_tlp", "postgres")
"""
origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output2_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output2_mysql_to_postgres_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "postgres")

origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output1_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output1_mysql_to_duckdb_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "duckdb")

origin_sqls_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingDataset","RANDOM", "init_output2_mysql_1_800_originalSql_random_200.json")
transferred_results_path = os.path.join("..", "..", "..", "Dataset", "Baseline", "TestingResults","RANDOM", "output2_mysql_to_duckdb_1_800_originalSql_random_200.jsonl")
SQLGlot_evaluate_f1(origin_sqls_path, transferred_results_path, "mysql", "duckdb")
"""
