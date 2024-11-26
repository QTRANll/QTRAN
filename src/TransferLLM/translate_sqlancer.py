# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/20 19:21
# @Author  : shaocanfan
# @File    : sqlancer_exp.py
# @Intro   :

from src.DialectRecognition.dialect_feature_recognizer import potential_features_refiner_single_sql, sqlancer_potential_dialect_features_process_and_map
# from src.TransferLLM.rag_based_feature_mapping import rag_feature_mapping_llm, rag_feature_mapping_count, rag_feature_mapping_process
from src.TransferLLM.TransferLLM import transfer_llm
from src.Tools.DatabaseConnect.database_connector import database_clear
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


current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

"""
sqlancer_norec_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_NOREC']
sqlancer_dqe_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_DQE']
sqlancer_tlp_mutate_id = os.environ['SQLANCER_MUTATE_MODEL_TLP']
"""

"""
TLP_supported_dbs = ["sqlite", "mysql", "tidb", "duckdb"]
TLP_extended_dbs = ["mariadb", "postgres", "monetdb", "clickhouse"]

NoRec_supported_dbs = ["sqlite", "mariadb", "postgres"]
NoRec_extended_dbs = ["mysql", "tidb", "monetdb", "duckdb", "clickhouse"]
"""


# 获取sqlancer的bug report,并进行potential dialect feature识别
def load_sqlancer_bug_report(fuzzer, a_db, b_db, bug):
    # 以列表形式返回bug经过处理得到的input信息
    bug_input = []
    # 有多条数据，存储在jsonl文件中，每一句sql存为一行
    for sql in bug["sqls"]:
        # 识别potential feature,将所有的feature都粗略的认为是dialect
        SqlPotentialFunctionIndexes, SqlPotentialOperatorIndexes, SqlPotentialDialectFunction, SqlPotentialDialectOperator = potential_features_refiner_single_sql(sql)
        # 获取对应的mapping indexes
        SqlPotentialDialectFunctionMapping = sqlancer_potential_dialect_features_process_and_map(a_db, b_db, SqlPotentialDialectFunction, "function",
                                                            search_k=0, version_id=1)
        # 暂不考虑operator
        SqlPotentialDialectOperatorMapping = []
        # SqlPotentialDialectOperatorMapping = sqlancer_potential_dialect_features_process_and_map(a_db, b_db, SqlPotentialDialectOperator, "operator",search_k=0, version_id=1)
        new_content = {
            "index": bug["index"],
            "a_db": bug["a_db"],
            "b_db": bug["b_db"],
            "molt": bug["molt"],
            "sql": sql
        }
        bug_input.append(new_content)
    return bug_input

def sqlancer_translate(input_filepath,tool="sqlancer",temperature=0.3, model="gpt-4o-mini",error_iteration=True,iteration_num=4,FewShot=False,with_knowledge=True):
    input_filename = os.path.basename(input_filepath).replace(".jsonl", "")
    input_dic = os.path.join(current_dir, "..", "..", "Input", input_filename)
    if not os.path.exists(input_dic):
        os.makedirs(input_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常
    # 新建所需transfer output文件夹
    output_transfer_dic = os.path.join(current_dir, "..", "..", "Output", input_filename, "TransferLLM")
    if not os.path.exists(output_transfer_dic):
        os.makedirs(output_transfer_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常
    # 新建所需mutate output文件夹
    output_mutate_dic = os.path.join(current_dir, "..", "..", "Output", input_filename, "MutationLLM")
    if not os.path.exists(output_mutate_dic):
        os.makedirs(output_mutate_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常

    with open(input_filepath, "r", encoding="utf-8") as r:
        bugs = r.readlines()
    for line in bugs:
        bug = json.loads(line)
        a_db = bug["a_db"]
        b_db = bug["b_db"]
        fuzzer = bug["molt"]

        # Step1: rag_based_feature_mapping。先做以下mapping，SQLite/mariadb/（Postgres是0暂时不弄）mapping to mysql/tidb/monetdb/duckdb/clickhouse
        # rag_feature_mapping_llm(1,0,a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])
        # rag_feature_mapping_count(1,0, a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])
        # rag_feature_mapping_process(1,0, a_db, b_db, ["function"], ["Feature", "Description", "Examples", "Category"])

        # Step2: potential_features_refiner
        bug_input = []
        bug_input_filename = os.path.join(input_dic, str(bug["index"]) + ".jsonl")
        if not os.path.exists(bug_input_filename):
            bug_input = load_sqlancer_bug_report(fuzzer, a_db, b_db, bug)
            for info in bug_input:
                with open(bug_input_filename, "a", encoding="utf-8") as a:
                    json.dump(info, a)
                    a.write('\n')
        else:
            print(bug_input_filename + " exists.")
            with open(bug_input_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                bug_input.append(json.loads(line))

        # Step3: 根据bug report中信息进行transfer并存储到output文件夹中
        transfer_outputs = []
        bug_output_transfer_filename = os.path.join(output_transfer_dic, str(bug["index"]) + ".jsonl")
        if not os.path.exists(bug_output_transfer_filename):
            # transfer llm conversion
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
                transfer_start_time = datetime.now()  # 使用 ISO 8601 格式
                costs, transfer_results, exec_results, exec_times, error_messages, origin_exec_result, origin_exec_time, origin_error_message, exec_equalities = transfer_llm(
                    tool=tool,
                    exp=fuzzer,
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
                info["SqlExecResult"] = origin_exec_result
                info["SqlExecError"] = origin_error_message
                info["TransferResult"] = transfer_results
                info["TransferCost"] = costs
                info["TransferTimeCost"] = (transfer_end_time - transfer_start_time).total_seconds()
                info["TransferSqlExecResult"] = exec_results
                info["TransferSqlExecError"] = error_messages
                info["TransferSqlExecEqualities"] = exec_equalities
                transfer_outputs.append(info)
            # sqlancer执行完一组sql后，将a_db和d_db都进行clear
            database_clear(tool, fuzzer, a_db)
            database_clear(tool, fuzzer, b_db)
            # 全部执行完再进行存储
            with open(bug_output_transfer_filename, "a", encoding="utf-8") as a:
                for item in transfer_outputs:
                    json.dump(item, a)
                    a.write('\n')
        else:
            print(bug_output_transfer_filename + " exists.")
            with open(bug_output_transfer_filename, "r", encoding="utf-8") as r:
                lines = r.readlines()
            for line in lines:
                transfer_outputs.append(json.loads(line))

        # Step4:mutate llm,将transfer后的最后一句select语句进行mutate并返回结果
        mutate_results = []
        bug_output_mutate_filename = os.path.join(output_mutate_dic, str(bug["index"]) + ".jsonl")
        if not os.path.exists(bug_output_mutate_filename):
            for item in transfer_outputs:
                mutate_results.append(item)
            if len(mutate_results) and len(mutate_results[-1]["TransferResult"]):
                mutate_sql = mutate_results[-1]["TransferResult"][-1]["TransferSQL"]
                # mutate llm client
                client = OpenAI(api_key=os.environ['OPENAI_API_key'])
                mutate_start_time = datetime.now()  # 使用 ISO 8601 格式
                if fuzzer.lower() == "norec":
                    # mutate_llm_model_ID = sqlancer_norec_mutate_id
                    mutate_llm_model_ID = os.environ[f"{fuzzer}_MUTATION_LLM_ID".upper()]
                elif "tlp" in fuzzer.lower():
                    fuzzer_temp = "tlp"
                    mutate_llm_model_ID = os.environ[f"{fuzzer_temp}_MUTATION_LLM_ID".upper()]
                else:
                    mutate_llm_model_ID = ""
                mutate_content, cost = run_muatate_llm_single_sql(tool, client, mutate_llm_model_ID, fuzzer, bug["molt"],b_db, mutate_sql)
                mutate_end_time = datetime.now()  # 使用 ISO 8601 格式
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
        if "MutateSqlExecResult" not in mutate_results[-1]:
            ddls = []
            transfer_fail_flag = False
            for i in range(len(mutate_results)-1):
                ddls.append(mutate_results[i]["TransferResult"][-1]["TransferSQL"])
                if mutate_results[i]["TransferSqlExecError"][-1] != "None":
                    transfer_fail_flag = True
            # 先创造执行环境
            database_clear(tool, fuzzer, b_db)
            for ddl in ddls:
                exec_sql_statement(tool, fuzzer, b_db, ddl)

            before_mutate = mutate_results[-1]["TransferResult"][-1]["TransferSQL"]
            after_mutate = mutate_results[-1]["MutateResult"]

            before_result, before_exec_time, before_error_message = exec_sql_statement(tool, fuzzer, b_db, before_mutate)
            after_result, after_exec_time, after_error_message = exec_sql_statement(tool, fuzzer, b_db, after_mutate)

            # 对于sqlancer的tlp，谓词的随机性比较大，这里将重复几次，以生成可执行的mutate sql
            if fuzzer.lower() == "tlp":
                client = OpenAI(api_key=os.environ['OPENAI_API_BASE'])
                mutate_cnt = 1
                while mutate_cnt <= iteration_num:
                    if after_error_message != None:
                        mutate_llm_model_ID = os.environ[f"{fuzzer}_MUTATION_LLM_ID".upper()]
                        mutate_results[-1]["MutateResult"], mutate_results[-1]["MutateCost"] = run_muatate_llm_single_sql(tool, client, mutate_llm_model_ID, fuzzer, bug["oracle"], b_db, before_mutate)
                        after_mutate = mutate_results[-1]["MutateResult"]
                        after_result, after_exec_time, after_error_message = exec_sql_statement(tool, fuzzer, b_db, after_mutate)

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
            # 全部执行完再次进行clear
            database_clear(tool, fuzzer, b_db)
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
            with open(bug_output_mutate_filename, "w", encoding="utf-8") as a:
                pass
            with open(bug_output_mutate_filename, "a", encoding="utf-8") as a:
                for item in mutate_results:
                    json.dump(item, a)
                    a.write('\n')
        print('------------------------')


def sqlancer_qtran_run(input_filepath,tool="sqlancer",temperature=0.3, model="gpt-4o-mini",error_iteration=True,iteration_num=4,FewShot=False,with_knowledge=True):
    sqlancer_translate(input_filepath=input_filepath, tool="sqlancer", temperature=temperature, model=model, error_iteration=True, iteration_num=iteration_num,FewShot=False, with_knowledge=False)
    getSuspicious(input_filepath=input_filepath, tool="sqlancer")



def getSuspicious(input_filepath, tool):
    input_filename = os.path.basename(input_filepath).replace(".jsonl", "")
    output_mutate_dic = os.path.join(current_dir, "..", "..", "Output", input_filename, "MutationLLM")
    if not os.path.exists(output_mutate_dic):
        os.makedirs(output_mutate_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常

    suspicious_dic = os.path.join(current_dir, "..", "..", "Output", input_filename, "SuspiciousBugs")
    if not os.path.exists(suspicious_dic):
        os.makedirs(suspicious_dic, exist_ok=True)  # 如果文件夹已存在，则不会抛出异常

    filenames = os.listdir(output_mutate_dic)
    for file in filenames:
        if os.path.exists(os.path.join(suspicious_dic, file)):
            continue
        with open(os.path.join(output_mutate_dic, file), "r", encoding="utf-8") as r:
            lines = r.readlines()
        contents = []
        for line in lines:
            contents.append(json.loads(line))
        if contents[-1]["OracleCheck"]["end"] == False and contents[-1]["OracleCheck"]["error"] == None:
            original_sqls = []
            results_sqls = []
            for content in contents:
                new_content = {
                    "index": content["index"],
                    "sql": content["sql"],
                    "TransferResult": [content["TransferResult"][-1]["TransferSQL"]]
                }
                original_sqls.append(content["sql"]+"\n")
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

def evaluate(tool,temperature, model,error_iteration,iteration_num,FewShot,with_knowledge,fuzzer, a_db, b_db):
    # 总数：total_cnt
    # executable总数：mutate可执行的数目
    # valid：mutate满足oracle的数目
    # precise：mutate语义正确的数量
    total_cnt = 0
    executable_cnt = 0
    valid_cnt = 0
    precise_cnt = 0

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

    oracle_check_fail = {
        "end": False,
        "error": None
    }

    output_mutate_dic = os.path.join(sqlancer_output_mutate_dic, fuzzer, (a_db + "_to_" + b_db).lower())
    output_mutate_dic_ = os.path.join(sqlancer_output_mutate_dic_, fuzzer, (a_db + "_to_" + b_db).lower())

    files = os.listdir(output_mutate_dic)
    for file in files:
        total_cnt += 1
        contents = []
        with open(os.path.join(output_mutate_dic, file), "r", encoding="utf-8") as r:
            lines = r.readlines()
        for line in lines:
            contents.append(json.loads(line))
        oracle_check = contents[-1]["OracleCheck"]
        mutate_sql = contents[-1]["MutateResult"]

        contents_ = []
        with open(os.path.join(output_mutate_dic_, file), "r", encoding="utf-8") as r:
            lines = r.readlines()
        for line in lines:
            contents_.append(json.loads(line))
        right_mutate_sql = contents_[-1]["MutateResult"]
        if oracle_check != oracle_check_transfer_fail:
            if oracle_check != oracle_check_mutate_fail:
                executable_cnt += 1
                if oracle_check == oracle_check_mutate_success:
                    valid_cnt += 1
                # 判断no finetuning的生成的句子和fine tuning生成的句子是否相同，相同则认为是正确的
                if mutate_sql == right_mutate_sql:
                    precise_cnt += 1
                # print("before mutate:"+contents[-1]["Sql"])
                # print("after mutate:"+mutate_sql)
                # print("right mutate:"+right_mutate_sql)
                # print('------------------')
    print("total_cnt:"+str(total_cnt))
    print("executable_cnt:"+str(executable_cnt))
    print("valid_cnt:"+str(valid_cnt))
    print("precise_cnt:"+str(precise_cnt))
