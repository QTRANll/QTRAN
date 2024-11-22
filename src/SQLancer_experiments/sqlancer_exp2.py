# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 19:21
# @Author  : shaocanfan
# @File    : sqlancer_exp.py
# @Intro   :

from src.DialectRecognition.dialect_feature_recognizer import potential_features_refiner_single_sql, sqlancer_potential_dialect_features_process_and_map
from src.Tools.DatabaseConnect.database_connector import database_clear_sqlancer,database_connection_args_sqlancer
# from src.TransferLLM.rag_based_feature_mapping import rag_feature_mapping_llm, rag_feature_mapping_count, rag_feature_mapping_process
from src.TransferLLM_with_Feature_Knowledge.TransferLLM import transfer_llm
from datetime import datetime
from src.MutationLlmModelValidator.MutateLLM import run_muatate_llm_single_sql
from src.Tools.OracleChecker.oracle_check import execSQL_result_convertor, Result, Check
import os
import json
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from src.Tools.DatabaseConnect.database_connector import exec_sql_statement

sqlancer_norec_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_NOREC']
sqlancer_dqe_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_DQE']
sqlancer_tlp_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_TLP']

"""
总计：499个
tlp:85个
{'SQLite': 4, 'mysql': 10, 'tidb': 31, 'duckdb': 30, 'CockroachDB': 7, 'H2': 3}
norec:55个
{'SQLite': 43, 'mariadb': 5, 'CockroachDB': 7}
"""
TLP_supported_dbs = ["sqlite", "mysql", "tidb", "duckdb"]
TLP_extended_dbs = ["mariadb", "postgres", "monetdb", "clickhouse"]

NoRec_supported_dbs = ["sqlite", "mariadb", "postgres"]
NoRec_extended_dbs = ["mysql", "tidb", "monetdb", "duckdb", "clickhouse"]



# 获取sqlancer的bug report,并进行potential dialect feature识别
def load_sqlancer_bug_report(fuzzer, a_db, b_db, bug):
    # 以列表形式返回bug经过处理得到的input信息
    bug_input = []
    # 有多条数据，存储在jsonl文件中，每一句sql存为一行
    for sql in bug["test"]:
        # 识别potential feature,将所有的feature都粗略的认为是dialect
        SqlPotentialFunctionIndexes, SqlPotentialOperatorIndexes, SqlPotentialDialectFunction, SqlPotentialDialectOperator = potential_features_refiner_single_sql(sql)
        # 获取对应的mapping indexes
        SqlPotentialDialectFunctionMapping = sqlancer_potential_dialect_features_process_and_map(a_db, b_db, SqlPotentialDialectFunction, "function",
                                                            search_k=0, version_id=1)
        # 暂不考虑operator
        SqlPotentialDialectOperatorMapping = []
        # SqlPotentialDialectOperatorMapping = sqlancer_potential_dialect_features_process_and_map(a_db, b_db, SqlPotentialDialectOperator, "operator",search_k=0, version_id=1)
        new_content = {
            "index": -1,
            "origin_index": bug["index"],
            "Sql": sql,
            "SqlLength": len(sql),
            "SqlExecResult": "",
            "SqlExecTime": "",
            "SqlExecError": "",
            "TransferResult": [],
            "TransferCost": [],
            "TransferSqlExecResult": [],
            "TransferSqlExecTime": [],
            "TransferSqlExecError": [],
            "TransferSqlExecEqualities": [],
            "SqlPotentialFunctionIndexes": SqlPotentialFunctionIndexes,
            "SqlPotentialOperatorIndexes": SqlPotentialOperatorIndexes,
            "SqlPotentialDialectFunction": SqlPotentialDialectFunction,
            "SqlPotentialDialectFunctionMapping": SqlPotentialDialectFunctionMapping,
            "SqlPotentialDialectOperator": SqlPotentialDialectOperator,
            "SqlPotentialDialectOperatorMapping": SqlPotentialDialectOperatorMapping
        }
        bug_input.append(new_content)
    return bug_input



def check_sqlancer_connect(filename, db_type):
    with open(filename, "r", encoding="utf-8") as r:
        contents = json.load(r)
    check_res = {"wrong":0, "right":0}
    for content in contents:
        if db_type.lower() != content["dbms"].lower():
            continue
        for sql in content["test"]:
            exec_sql_statement("sqlancer", db_type, sql)
        flag = database_clear_sqlancer(db_type, database_connection_args_sqlancer[db_type]["dbname"])

        if flag:
            check_res["right"] += 1
        else:
            check_res["wrong"] += 1
    print(check_res)


def sqlancer_extend(tool,temperature, model,error_iteration,iteration_num,FewShot,with_knowledge,fuzzer, a_db, b_db):
    # 判断a_db和b_db是否支持，不支持则退出函数
    if "norec" in fuzzer.lower():
        if a_db.lower() not in NoRec_supported_dbs:
            print(fuzzer+"不支持"+a_db)
            return
        if b_db.lower() not in NoRec_extended_dbs:
            print(fuzzer+" extend不支持"+b_db)
            return
    elif "tlp" in fuzzer.lower():
        if a_db.lower() not in TLP_supported_dbs:
            print(fuzzer+"不支持"+a_db)
            return
        if b_db.lower() not in TLP_extended_dbs:
            print(fuzzer+" extend不支持"+b_db)
            return
    mutate_llm_id = sqlancer_tlp_mutate_id

    # 获取sqlancer bug reports(jsonl)
    with open(sqlancer_reports_filename, "r", encoding="utf-8") as r:
        bugs = r.readlines()

    index = 0  # 记录处理的bug的数目
    for line in bugs:
        bug = json.loads(line)
        # 跳过不符合当下检测的fuzzer的数据
        if fuzzer.lower() not in bug["oracle"].lower() or a_db.lower() not in bug["dbms"].lower():
            continue
        else:
            # 新建所需input文件夹
            input_dic = os.path.join(sqlancer_input_dic, fuzzer, (a_db + "_to_" + b_db).lower())
            if not os.path.exists(input_dic):
                os.makedirs(input_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常
            # 新建所需transfer output文件夹
            output_transfer_dic = os.path.join(sqlancer_output_transfer_dic, fuzzer, (a_db + "_to_" + b_db).lower())
            if not os.path.exists(output_transfer_dic):
                os.makedirs(output_transfer_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常
            # 新建所需mutate output文件夹
            output_mutate_dic = os.path.join(sqlancer_output_mutate_dic, fuzzer, (a_db + "_to_" + b_db).lower())
            if not os.path.exists(output_mutate_dic):
                os.makedirs(output_mutate_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常
            # 新建所需oracle check false 文件夹
            oracle_check_dic = os.path.join(sqlancer_oracle_check_dic, fuzzer, (a_db + "_to_" + b_db).lower())
            if not os.path.exists(oracle_check_dic):
                os.makedirs(oracle_check_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常


        # Step1: rag_based_feature_mapping。先做以下mapping，SQLite/mariadb/（Postgres是0暂时不弄）mapping to mysql/tidb/monetdb/duckdb/clickhouse
        # rag_feature_mapping_llm(1,0,a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])
        # rag_feature_mapping_count(1,0, a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])
        # rag_feature_mapping_process(1,0, a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])

        # Step2: potential_features_refiner,将得到的结果存储到input文件夹中作为输入
        # 将bug input内容存储
        # print(bug["test"][-1])
        bug_input = []
        bug_input_filename = os.path.join(input_dic, str(index) + "_bug.jsonl")
        if not os.path.exists(bug_input_filename):
            # 构造input文件，包括测试数据基本信息和feature mapping等信息
            bug_input = load_sqlancer_bug_report(fuzzer, a_db, b_db, bug)
            # 全部生成完再进行存储
            for info in bug_input:
                info["index"] = index
                with open(bug_input_filename, "a", encoding="utf-8") as a:
                    json.dump(info, a)
                    a.write('\n')
        else:
            print(bug_input_filename + "已存在")
            # load出来
            with open(bug_input_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                bug_input.append(json.loads(line))

        # Step3: 根据bug report中信息进行transfer并存储到output文件夹中
        transfer_outputs = []
        bug_output_transfer_filename = os.path.join(output_transfer_dic, str(index) + "_bug.jsonl")
        if not os.path.exists(bug_output_transfer_filename):
            # transfer llm conversion(记录上下文)
            chat = ChatOpenAI(temperature=temperature, model=model)
            memory = ConversationBufferMemory()  # 内存：对话缓冲区内存
            if error_iteration:
                conversation = ConversationChain(
                    llm=chat,
                    memory=memory,
                    verbose=False  # 为true的时候是展示langchain实际在做什么
                )
            else:
                conversation = ConversationChain(
                    llm=chat,
                    verbose=False  # 为true的时候是展示langchain实际在做什么
                )

            for info in bug_input:
                info["index"] = index
                transfer_start_time = datetime.now()  # 使用 ISO 8601 格式
                costs, transfer_results, exec_results, exec_times, error_messages, origin_exec_result, origin_exec_time, origin_error_message, exec_equalities = transfer_llm(
                    tool=tool,
                    conversation=conversation,
                    error_iteration=error_iteration,
                    iteration_num=iteration_num,
                    FewShot=FewShot,
                    with_knowledge=with_knowledge,
                    origin_db=a_db,
                    target_db=b_db,
                    test_info=info
                )
                transfer_end_time = datetime.now()  # 使用 ISO 8601 格式
                info["TransferStartTime"] = transfer_start_time.isoformat()
                info["TransferEndTime"] = transfer_end_time.isoformat()
                info["TransferTimeCost"] = (transfer_end_time - transfer_start_time).total_seconds()
                info["SqlExecResult"] = origin_exec_result
                info["SqlExecTime"] = origin_exec_time
                info["SqlExecError"] = origin_error_message
                info["TransferResult"] = transfer_results
                info["TransferCost"] = costs
                info["TransferSqlExecResult"] = exec_results
                info["TransferSqlExecTime"] = exec_times
                info["TransferSqlExecError"] = error_messages
                info["TransferSqlExecEqualities"] = exec_equalities
                transfer_outputs.append(info)

            # 全部执行完再进行存储
            with open(bug_output_transfer_filename, "a", encoding="utf-8") as a:
                for item in transfer_outputs:
                    json.dump(item, a)
                    a.write('\n')
        else:
            print(bug_output_transfer_filename + "已存在")
            # load出来
            with open(bug_output_transfer_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                transfer_outputs.append(json.loads(line))

        # Step4:mutate llm,将transfer后的最后一句select语句进行mutate并返回结果
        mutate_results = []
        bug_output_mutate_filename = os.path.join(output_mutate_dic, str(index) + "_bug.jsonl")
        if not os.path.exists(bug_output_mutate_filename):
            for item in transfer_outputs:
                mutate_results.append(item)
            if len(mutate_results) and len(mutate_results[-1]["TransferResult"]):
                mutate_sql = mutate_results[-1]["TransferResult"][-1]["TransferSQL"]
                # mutate llm client
                client = OpenAI(api_key=mutate_llm_api)
                mutate_start_time = datetime.now()  # 使用 ISO 8601 格式
                if fuzzer.lower() == "norec":
                    mutate_llm_model_ID = sqlancer_norec_mutate_id
                elif fuzzer.lower() == "tlp":
                    mutate_llm_model_ID = sqlancer_tlp_mutate_id
                else:
                    mutate_llm_model_ID = ""
                mutate_content, cost = run_muatate_llm_single_sql(tool, client, mutate_llm_model_ID, fuzzer, bug["oracle"],b_db, mutate_sql)
                mutate_end_time = datetime.now()  # 使用 ISO 8601 格式
                mutate_results[-1]["MutateStartTime"] = mutate_start_time.isoformat()
                mutate_results[-1]["MutateEndTime"] = mutate_end_time.isoformat()
                mutate_results[-1]["MutateTimeCost"] = (mutate_end_time - mutate_start_time).total_seconds()
                mutate_results[-1]["MutateResult"] = str(mutate_content)
                mutate_results[-1]["MutateCost"] = cost
                # 进行存储
                with open(bug_output_mutate_filename, "a", encoding="utf-8") as a:
                    for item in mutate_results:
                        json.dump(item, a)
                        a.write('\n')
        else:
            print(bug_output_mutate_filename + "已存在")
            # load出来
            with open(bug_output_mutate_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                mutate_results.append(json.loads(line))

        # Step5: check oracle,执行mutate后sql并记录执行结果以及oracle check结果
        oracle_check_false_filename = os.path.join(oracle_check_dic, str(index) + "_bug.jsonl")
        if "MutateSqlExecResult" not in mutate_results[-1]:
            print("不存在"+"MutateSqlExecResult")
            # 获取所有的b_db上的ddl语句，并判断ddl语句是否均可执行，如不行则返回
            transfer_fail_flag = False
            for i in range(len(mutate_results)-1):
                if mutate_results[i]["TransferSqlExecError"][-1] != "None":
                    transfer_fail_flag = True

            before_mutate = mutate_results[-1]["TransferResult"][-1]["TransferSQL"]
            after_mutate = mutate_results[-1]["MutateResult"]

            before_result, before_exec_time, before_error_message = exec_sql_statement(tool, b_db, before_mutate)
            after_result, after_exec_time, after_error_message = exec_sql_statement(tool, b_db, after_mutate)

            # 对于sqlancer的tlp，谓词的随机性比较大，这里将重复几次，以生成可执行的mutate sql
            if fuzzer.lower() == "tlp":
                client = OpenAI(api_key=mutate_llm_api)
                mutate_cnt = 1
                while mutate_cnt <= iteration_num:
                    if after_error_message != None:
                        mutate_llm_model_ID = sqlancer_tlp_mutate_id
                        mutate_results[-1]["MutateResult"], mutate_results[-1]["MutateCost"] = run_muatate_llm_single_sql(tool, client, mutate_llm_model_ID, fuzzer, bug["oracle"], b_db, before_mutate)
                        after_mutate = mutate_results[-1]["MutateResult"]
                        after_result, after_exec_time, after_error_message = exec_sql_statement(tool, b_db, after_mutate)

                        # 将最后一次的结果存储到对应的mutate output文件中,先清空
                        with open(bug_output_mutate_filename, "w", encoding="utf-8") as a:
                            pass
                        with open(bug_output_mutate_filename, "a", encoding="utf-8") as a:
                            for item in mutate_results:
                                json.dump(item, a)
                                a.write('\n')
                        mutate_cnt += 1
                    else:
                        break
            mutate_results[-1]["MutateSqlExecResult"] = str(after_result)
            mutate_results[-1]["MutateSqlExecTime"] = str(after_exec_time)
            mutate_results[-1]["MutateSqlExecError"] = str(after_error_message)

            if before_error_message or after_error_message:
                # 如果是mutate前和后的语句有执行fail的情况
                oracle_check_res = {
                    "end": False,
                    "error": "exec fail"
                }
            else:
                converted_before_result = execSQL_result_convertor(before_result)
                converted_after_result = execSQL_result_convertor(after_result)
                # 创建 Result 对象
                before_result_object = Result(converted_before_result["column_names"],
                                              converted_before_result["column_types"],
                                              converted_before_result["rows"])
                after_result_object = Result(converted_after_result["column_names"],
                                             converted_after_result["column_types"],
                                             converted_after_result["rows"])

                oracle_check, error = Check(before_result_object, after_result_object, True,
                                            True)  # check result->another_result是否符合is_upper
                oracle_check_res = {
                    "end": oracle_check,
                    "error": error
                }
                # 判断是否为sqlancer的特殊情况：0==None(表示个数时)
                if converted_before_result['rows'] == [['0']] and converted_after_result['rows'] == [['None']]:
                    oracle_check_res = {
                        "end": True,
                        "error": None
                    }
            # 如果ddls中有transfer失败的情况
            if transfer_fail_flag:
                oracle_check_res = {
                    "end": False,
                    "error": "transfer fail"
                }

            mutate_results[-1]["OracleCheck"] = oracle_check_res
            # 记录oracle check不满足的
            if not oracle_check_res["end"]:
                with open(oracle_check_false_filename, "w", encoding="utf-8") as a:
                    pass
                with open(oracle_check_false_filename, "a", encoding="utf-8") as a:
                    for item in mutate_results:
                        json.dump(item, a)
                        a.write('\n')

            # 存储结果，重写
            with open(bug_output_mutate_filename, "w", encoding="utf-8") as a:
                pass
            with open(bug_output_mutate_filename, "a", encoding="utf-8") as a:
                for item in mutate_results:
                    json.dump(item, a)
                    a.write('\n')
        index += 1
        print('------------------------')


def getSuspicious(tool,temperature, model,error_iteration,iteration_num,FewShot,with_knowledge,fuzzer, a_db, b_db):
    suspicious_dic = os.path.join(sqlancer_suspicious_dic, fuzzer, (a_db + "_to_" + b_db).lower())
    if not os.path.exists(suspicious_dic):
        os.makedirs(suspicious_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常

    oracle_check_dic = os.path.join(sqlancer_oracle_check_dic, fuzzer, (a_db + "_to_" + b_db).lower())
    filenames = os.listdir(oracle_check_dic)
    print(filenames)
    for file in filenames:
        if os.path.exists(os.path.join(suspicious_dic, file)):
            continue

        with open(os.path.join(oracle_check_dic, file), "r", encoding="utf-8") as r:
            lines = r.readlines()
        contents = []
        for line in lines:
            contents.append(json.loads(line))

        # 判断是否存在
        if os.path.exists(os.path.join(suspicious_dic, file)):
            continue
        # 根据oracle check结果判断是否为可疑的
        if contents[-1]["OracleCheck"]["end"] == False and contents[-1]["OracleCheck"]["error"] == None:
            original_sqls = []
            results_sqls = []
            for content in contents:
                new_content = {
                    "index": content["index"],
                    "origin_index": content["origin_index"],
                    "Sql": content["Sql"],
                    "TransferResult": [content["TransferResult"][-1]["TransferSQL"]]
                }

                original_sqls.append(content["Sql"]+"\n")
                results_sqls.append(content["TransferResult"][-1]["TransferSQL"]+"\n")
                if "MutateResult" in content:
                    new_content["TransferSqlExecResult"] = [content["TransferSqlExecResult"][-1]]
                    new_content["MutateResult"] = content["MutateResult"]
                    new_content["MutateSqlExecResult"] = content["MutateSqlExecResult"]
                    results_sqls.append(content["MutateResult"]+"\n")

                with open(os.path.join(suspicious_dic, file),"a",encoding="utf-8") as a:
                    json.dump(new_content, a)
                    a.write('\n')

            with open(os.path.join(suspicious_dic, file.replace("jsonl","txt")), "w", encoding="utf-8") as file:
                file.writelines(original_sqls + ["\n", "\n"] + results_sqls)


def evaluate(tool,temperature, model,error_iteration,iteration_num,FewShot,with_knowledge,fuzzer, a_db_s, b_db):
    total_cnt = 0
    transfer_success_cnt = 0
    mutate_success_cnt = 0
    oracle_check_false_cnt = 0
    mutate_fail_cnt = 0
    oracle_check_transfer_fail = {
        "end": False,
        "error": "transfer fail"
    }
    oracle_check_mutate_fail = {
        "end": False,
        "error": "exec fail"
    }

    oracle_check_mutate_success = {
        "end": True,
        "error": None
    }

    oracle_check_fail= {
        "end": False,
        "error": None
    }
    for a_db in a_db_s:
        output_mutate_dic = os.path.join(sqlancer_output_mutate_dic, fuzzer, (a_db + "_to_" + b_db).lower())
        files = os.listdir(output_mutate_dic)
        for file in files:
            total_cnt += 1
            contents = []
            with open(os.path.join(output_mutate_dic, file), "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                contents.append(json.loads(line))
            oracle_check = contents[-1]["OracleCheck"]
            if oracle_check != oracle_check_transfer_fail:
                transfer_success_cnt += 1
                if oracle_check == oracle_check_mutate_success:
                    mutate_success_cnt += 1
                    print(oracle_check)
                    if not oracle_check["end"]:
                        oracle_check_false_cnt += 1

                if oracle_check == oracle_check_mutate_fail:
                    mutate_fail_cnt += 1
    print(total_cnt)
    print(transfer_success_cnt)
    print("mutate success:"+str(mutate_success_cnt))
    print("check oracle fail:"+str(oracle_check_false_cnt))
    print(mutate_fail_cnt)



def sqlancer_input_process():
    dic_path = "../../Dataset/SQLancer Output/sqlite3_NoREC"
    target_path = "../../SQLancer_bug_reports/sqlite3_NoREC.jsonl"
    if os.path.exists(target_path):
        print(target_path + "已存在")
        return

    index = 0
    filenames = os.listdir(dic_path)
    # 处理所有的filenames
    # 内容如下
    # {
    # "initial_sql": "SELECT ALL * FROM vt0, v0 WHERE ((((((v0.c4, v0.c1, v0.c4)) BETWEEN ((v0.c1, vt0.c0, v0.c2)) AND ((v0.c1, v0.c4, v0.c3)))) IS TRUE));",
    # "mutated_sql": "SELECT SUM(count) FROM (SELECT ALL (((((((v0.c4, v0.c1, v0.c4)) BETWEEN ((v0.c1, vt0.c0, v0.c2)) AND ((v0.c1, v0.c4, v0.c3)))) IS TRUE)) IS TRUE)  as count FROM vt0, v0);",
    # "dbname": "sqlite3",
    # "oracle": "NoREC",
    # "ddl": ""
    # }
    # 要转为下下面的内容
    # {"dbms": "SQLite","oracle": "error", "test": []}

    for file in filenames:
        if index > 1000:
            return
        if ".json" not in file:
            continue
        with open(os.path.join(dic_path, file), "r", encoding="utf-8") as r:
            content = json.load(r)
        input_pro = {
            "index": index,
            "dbms": content["dbname"],
            "oracle": content["oracle"],
            "test": [content["initial_sql"]]
        }
        index += 1

        with open(target_path, "a", encoding="utf-8") as a:
            json.dump(input_pro, a)
            a.write('\n')


sqlancer_reports_filename = "../../SQLancer_bug_reports/sqlite3_NoREC.jsonl"
sqlancer_input_dic = "../../Input/TransferLLM/sqlancer/exp_2"
sqlancer_output_transfer_dic = "../../Output/TransferLLM/sqlancer/exp_2"
sqlancer_output_mutate_dic = "../../Output/MutationLlmModelFineTuning/sqlancer/exp_2"
sqlancer_oracle_check_dic = "../../Output/OracleCheck/sqlancer/exp_2"
sqlancer_suspicious_dic = "../../Output/Suspicious/sqlancer/exp_2"



# norec
a_db = ["SQLite", "mariadb"]
b_db = ["mysql","tidb", "monetdb", "duckdb", "clickhouse"]

a_db = ["SQLite", "mariadb"]
b_db = ["clickhouse"]

a_db = ["tidb", "duckdb", "mysql", "SQLite"]
b_db = ["mariadb", "PostgresSQL", "monetdb", "clickhouse"]


temperature = 0.3
Iteration_Num = 3  # 默认最大迭代次数
model = "gpt-4o-mini"
fuzzer = "norec"

a_db = ["sqlite"]
b_db = ["tidb", "monetdb", "duckdb", "clickhouse", "mariadb"]

a_db = ["sqlite"]
b_db = ["tidb"]


# sqlancer_input_process()

"""
for b in b_db:
    for a in a_db:
        # exp_2同一用一套ddl：先claer再建表
        database_clear_sqlancer(a, database_connection_args_sqlancer[a.lower()]["dbname"])
        database_clear_sqlancer(b, database_connection_args_sqlancer[b.lower()]["dbname"])
        # transfer之前
        database_define_sqlancer(a, "../../DatabaseDefinite/SQLancer_exp2/sqlite.json")
        database_define_sqlancer(b, "../../DatabaseDefinite/SQLancer_exp2/ddl_tidb.json")

        sqlancer_extend(tool="sqlancer", temperature=temperature, model=model, error_iteration=True, iteration_num=Iteration_Num,FewShot=False, with_knowledge=False, fuzzer=fuzzer, a_db=a, b_db=b)
        # getSuspicious(tool="sqlancer", temperature=temperature, model=model, error_iteration=True, iteration_num=Iteration_Num,FewShot=False, with_knowledge=True, fuzzer=fuzzer, a_db=a, b_db=b)

        # 执行完成以后再次清场
        database_clear_sqlancer(a, database_connection_args_sqlancer[a.lower()]["dbname"])
        database_clear_sqlancer(b, database_connection_args_sqlancer[b.lower()]["dbname"])
"""

"""
for b in b_db:
    print(b)
    evaluate(tool="sqlancer", temperature=temperature, model=model, error_iteration=True, iteration_num=Iteration_Num,FewShot=False, with_knowledge=True, fuzzer=fuzzer, a_db_s=a_db, b_db=b)
"""


"""
database_clear_sqlancer("postgres",database_connection_args_sqlancer["postgres"]["dbname"])
database_clear_sqlancer("mariadb",database_connection_args_sqlancer["mariadb"]["dbname"])

sqls = [
    "create table t6 (c22 int CHECK (c22 >= 0));",
    "insert into t6 values (16);",
    "insert into t6 values (80);",
    "select * from t6 where TO_HEX(t6.c22) > REVERSE(RPAD('+YeL', t6.c22, '7+02o'));",
    "select * from t6 where TO_HEX(t6.c22) > REVERSE(RPAD(case when true then '+YeL' else '+YeL' end, t6.c22, '7+02o'));"
]

for sql in sqls:
    print(sql)
    print(exec_sql_statement("sqlancer", "postgres", sql))
    print('-------------------------')

sqls = [
    "create table t6 (c22 int CHECK (c22 >= 0));",
    "insert into t6 values (16);",
    "insert into t6 values (80);",
    "select * from t6 where CONV(c22, 10, 16) > REVERSE(RPAD('+YeL', c22, '7+02o'));",
    "select * from t6 where CONV(c22, 10, 16) > REVERSE(RPAD(case when true then '+YeL' else '+YeL' end, c22, '7+02o'));"
]

for sql in sqls:
    print(sql)
    print(exec_sql_statement("sqlancer", "mariadb", sql))
    print('-------------------------')

sqls= [
    "create table t6 (c22 INT UNSIGNED);",
    "insert into t6 values (16);",
    "insert into t6 values (80);",
    "select * from t6 where HEX(t6.c22) > REVERSE(RPAD('+YeL', t6.c22, '7+02o'));",
    "select * from t6 where HEX(t6.c22) > REVERSE(RPAD(case when true then '+YeL' else '+YeL' end, t6.c22, '7+02o'));"
]


database_clear_sqlancer("mariadb",database_connection_args_sqlancer["mariadb"]["dbname"])
for sql in sqls:
    print(sql)
    print(exec_sql_statement("sqlancer", "mariadb", sql))
    print('-------------------------')
"""


sqls = [
    "CREATE TABLE t0(c0);",
    "CREATE TABLE t1(c0);",
    "CREATE VIEW v0(c0) AS SELECT t0.c0 FROM t1 LEFT JOIN t0;",
    "INSERT INTO t1(c0) VALUES ('example_value');",
    "SELECT COUNT(*) FROM v0 WHERE (DATE('now'), c0) != (CAST(NULL AS TEXT), '0');",
    "SELECT SUM(CASE WHEN (DATE('now'), c0) != (CAST(NULL AS TEXT), '0') THEN 1 ELSE 0 END) FROM v0;"
]

database_clear_sqlancer("sqlite",database_connection_args_sqlancer["sqlite"]["dbname"])
for sql in sqls:
    print(sql)
    print(exec_sql_statement("sqlancer", "sqlite", sql))
    print('-------------------------')




sqls = [
    "CREATE TABLE t0 (c0 TEXT);",
    "CREATE TABLE t1 (c0 TEXT);",
    "CREATE VIEW v0 AS SELECT t0.c0 FROM t1 LEFT JOIN t0 ON t1.c0 = t0.c0;",
    "INSERT INTO t1(c0) VALUES ('example_value');",
    "SELECT COUNT(*) FROM v0 WHERE (CURRENT_DATE, c0) != (CAST(NULL AS TEXT), '0');",
    "SELECT SUM(CASE WHEN (CURRENT_DATE, c0) != (CAST(NULL AS TEXT), '0') THEN 1 ELSE 0 END) FROM v0;"
]

sqls = [
    "CREATE TABLE t0 (c0 TEXT);",
    "CREATE TABLE t1 (c0 TEXT);",
    "CREATE VIEW v0 AS SELECT t0.c0 FROM t1 LEFT JOIN t0 ON t1.c0 = t0.c0;",
    "INSERT INTO t1(c0) VALUES ('example_value');",
    "SELECT COUNT(*) FROM v0 WHERE (CAST(CURRENT_DATE AS TIMESTAMP), c0) != (CAST(NULL AS TEXT), '0');",
    "SELECT SUM(CASE WHEN (CAST(CURRENT_DATE AS TIMESTAMP), c0) != (CAST(NULL AS TEXT), '0') THEN 1 ELSE 0 END) FROM v0;"
]
database_clear_sqlancer("duckdb",database_connection_args_sqlancer["duckdb"]["dbname"])
for sql in sqls:
    print(sql)
    print(exec_sql_statement("sqlancer", "duckdb", sql))
    print('-------------------------')






