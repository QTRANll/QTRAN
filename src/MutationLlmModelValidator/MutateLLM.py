# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/2 21:19
# @Author  : shaocanfan
# @File    : MutationLlmModelFineTuning.py
# @Intro   :
import json
import os
from src.Tools.DatabaseConnect.database_connector import exec_sql_statement
from src.Tools.OracleChecker.oracle_check import execSQL_result_convertor, Check
from src.Tools.OracleChecker.oracle_check import Result

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在目录
current_dir = os.path.dirname(current_file_path)




filenames = {
    "FixMCmpOpU":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl",
    "FixMDistinctL":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl",
    "FixMHaving1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl",
    "FixMOn1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMOn1U).jsonl"
}

results_filenames = {
    "FixMCmpOpU":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl",
    "FixMDistinctL":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl",
    "FixMHaving1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl",
    "FixMOn1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMOn1U).jsonl"
}

eval_filenames = {
    "FixMCmpOpU":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMCmpOpU)_eval.jsonl",
    "FixMDistinctL":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMDistinctL)_eval.jsonl",
    "FixMHaving1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMHaving1U)_eval.jsonl",
    "FixMOn1U":"../../Dataset/MutationLlmModelFineTuning/PostgresSQL/TestingResult/postgres_testing_dataset_raw2.0(FixMOn1U)_eval.jsonl"
}

# 处理mutate llm生成的结果，依次处理所有可能的变异：计算oracle，运行并记录结果，oracle check以检测bug
def process_mutate_llm_result(muatate_name, muatate_result, exec_result_before):
    """
    [
        {
            "isUpper": True,
            "transferredSqlsim_exec": {
                "exec_result": str(exec_result),
                "exec_time": str(exec_time),
                "error_message": str(error_message)
            },
            "CheckOracle":{
                "end":True,
                "error":""
            }
        }
    ]
    """
    procrssed_result = []
    for result in muatate_result:
        # 计算oracle,IsUpper: ((candidate.U^candidate.Flag)^1) == 1
        U = muatate_name.endswith('U')
        isUpper = bool((U ^ result["flag"]) ^ 1)
        # 运行该"MutateLLM_Result"并保存运行结果
        exec_result, exec_time, error_message = exec_sql_statement("pinolo", "postgres", result["mutated sql"])

        # 比较该"MutateLLM_Result"的运行结果是否满足oracle
        exec_result_before_formatted = execSQL_result_convertor(exec_result_before)
        exec_result_formatted = execSQL_result_convertor(exec_result)
        exec_result_before_object = Result(exec_result_before_formatted["column_names"], exec_result_formatted["column_types"],exec_result_before_formatted["rows"])
        exec_result_object = Result(exec_result_formatted["column_names"], exec_result_formatted["column_types"],exec_result_before_formatted["rows"])
        end, error = Check(exec_result_before_object, exec_result_object, isUpper)

        processed_item = {
            "isUpper": isUpper,
            "mutate_exec": {
                "exec_result": str(exec_result),
                "exec_time": str(exec_time),
                "error_message": str(error_message)
            },
            "CheckOracle": {
                "end": end,
                "error": str(error)
            } 
        }
        procrssed_result.append(processed_item)

    return procrssed_result

"""
def run_muatate_llm(tool, mutate_name):
    client = OpenAI(api_key=api_key)

    # 为Mutate LLM构造满足特定格式的testing data数据项


    if tool.lower() == "pinolo":
        with open(filenames[mutate_name], "r", encoding="utf-8") as r:
            lines = r.readlines()

        for line in lines:
            data = json.loads(line)
            # 执行"transferredSqlsim"并记录结果
            exec_result, exec_time, error_message = exec_sql_statement("pinolo", "postgres", data["transferredSqlsim"])

            data["transferredSqlsim_exec"] = {
                "exec_result": str(exec_result),
                "exec_time": str(exec_time),
                "error_message": str(error_message)
            }

            # mutate the transferredSqlsim
            completion = client.chat.completions.create(
                model=mutate_llm_model_ID,
                messages=data["MutateLLM_Message"]
            )
            response_content = completion.choices[0].message.content
            # 转换字符串结果为python数据结构：mutate llm返回的结果是list形式的，有多个结果
            data["MutateLLM_Result"] = str(response_content)
            MutateLLM_Result_json = eval(response_content)

            # 处理mutate llm的结果并存储
            data["MutateLLM_OracleCheck"] = process_mutate_llm_result(mutate_name, MutateLLM_Result_json, exec_result)

            with open(results_filenames[mutate_name], "a", encoding="utf-8") as w:
                json.dump(data, w)
                w.write("\n")
"""

def run_muatate_llm_single_sql(tool, client, model_id, mutate_name, oracle, db_type, sql):

    # 为Mutate LLM构造满足特定格式的testing data数据项
    """
    sqlancer格式如下
    messages=[
    {
      "role": "system",
      "content": "Synthesize mutated SQL that returns the same result as the user-provided seed SQL, following this mutation strategy:\nMove predicate P from the WHERE clause to the SELECT list to disable optimization, and use SUM(.) to count the rows where P IS TRUE in the SELECT list.\nNote: The mutated SQL must belong to the same DBMS of the user-provided seed SQL."
    },
    {
      "role": "user",
      "content": "A seed SQL from cockroach:\n"+"SELECT COUNT(*) FROM t2 WHERE true;"
    },
    ]
    completion = client.chat.completions.create(
      model="gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR",
      messages=[
          {"role": "system","content": "You are an expert in mysql statement mutation.Mutate the seed sql given by user into the mutated sql according to the mutate strategy \"FixMDistinctL\" :\"Distinct false -> true\".This mutate strategy will change \"DISTINCT\" in SELECT statement from false to true."},
          {"role": "user","content": "(SELECT (DATE_SUB(WEEK(_UTF8MB4'2005-08-02'), INTERVAL 1 DAY_MICROSECOND)) AS `f1`,(BINARY `f5`&CHARSET(`f4`) DIV `f6`) AS `f2`,(`f4`-0) AS `f3` FROM (SELECT `col_char(20)_key_signed` AS `f7`,`col_float_key_signed` AS `f5`,`col_double_undef_unsigned` AS `f8` FROM `table_3_utf8_undef` USE INDEX (`col_decimal(40, 20)_key_signed`, `col_bigint_key_unsigned`)) AS `t1` NATURAL JOIN (SELECT (CHARSET(`f12`)) AS `f4`,(DATE_SUB(`f10`, INTERVAL 1 HOUR_MINUTE)) AS `f9`,(COLLATION(`f12`)%REPEAT(`f11`, 3)) AS `f6` FROM (SELECT `col_double_key_unsigned` AS `f10`,`col_double_key_signed` AS `f11`,`col_double_undef_signed` AS `f12` FROM `table_7_utf8_undef` IGNORE INDEX (`col_char(20)_key_signed`, `col_decimal(40, 20)_key_unsigned`)) AS `t2` WHERE ((((DATE_ADD(MINUTE(_UTF8MB4'2005-01-05 12:14:45'), INTERVAL 1 YEAR_MONTH))>=ALL (SELECT `col_decimal(40, 20)_key_signed` FROM `table_7_utf8_undef` FORCE INDEX (`col_decimal(40, 20)_key_signed`))) AND ((LOCATE(`f12`, `f12`)) IS TRUE)) OR ((NOT ((DATE_ADD(~6, INTERVAL 1 HOUR_MICROSECOND)) NOT IN (SELECT `col_bigint_key_signed` FROM `table_7_utf8_undef` IGNORE INDEX (`col_bigint_key_signed`, `col_bigint_key_unsigned`)))) AND (NOT (1)))) IS TRUE HAVING ((DAYNAME(_UTF8MB4'2018-05-21')) NOT BETWEEN CRC32(_UTF8MB4'2007') AND `f4`) OR ((CAST((FROM_DAYS(105096451230399333)) AS CHAR) LIKE _UTF8MB4'%1%') IS TRUE) OR ((RTRIM(_UTF8MB4'was')) BETWEEN HOUR(_UTF8MB4'14:44:22') AND `f6`) ORDER BY `f10`) AS `t3`) UNION ALL (SELECT (COLLATION(`f13`)) AS `f1`,(ROUND(0.9230651247279676)) AS `f2`,(TIMEDIFF(_UTF8MB4'2014-05-24 03:48:34', _UTF8MB4'2011-06-19 04:02:54')>>~`f13`) AS `f3` FROM (SELECT (CEIL(0.05303136671365602)^DEGREES(-5382834637802595851)-`f20`) AS `f16`,(UCASE(`f18`)) AS `f14`,(`f19`) AS `f17` FROM (SELECT `col_double_key_unsigned` AS `f18`,`col_double_key_signed` AS `f19`,`col_char(20)_undef_signed` AS `f20` FROM `table_7_utf8_undef` USE INDEX (`col_decimal(40, 20)_key_unsigned`, `col_float_key_signed`)) AS `t4`) AS `t5` NATURAL JOIN (SELECT (TIME(_UTF8MB4'2003-03-20 08:48:54')) AS `f13`,(DATE_ADD(-7078353141775895169, INTERVAL 1 DAY_SECOND)) AS `f21`,(CONCAT(0.9420451500844236, 1, `f22`)) AS `f15` FROM (SELECT `col_decimal(40, 20)_key_unsigned` AS `f22`,`col_double_undef_unsigned` AS `f23`,`col_float_undef_unsigned` AS `f24` FROM `table_3_utf8_undef`) AS `t6`) AS `t7`)"}
      ]
    )
    """
    if tool.lower() == "sqlancer":
        # 构造格式化输入词
        mutate_stratege = None
        if "norec" in mutate_name.lower():
            mutate_stratege = "norec"
        elif "tlp" in mutate_name.lower():
            mutate_stratege = "tlp"
        mutate_prompt_path = os.path.join(current_dir, "..","..", "Input", "MutatePrompt", tool.lower(), mutate_stratege+ ".json")
        with open(mutate_prompt_path, "r", encoding="utf-8") as r:
            system_message = json.load(r)[oracle]

        formatted_input = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": "A seed SQL from " + db_type.lower() + ":\n" + sql
            }
        ]
        # mutate the sql
        cost = {}
        # print(oracle)
        # print(model_id)
        # print(formatted_input)
        completion = client.chat.completions.create(
            model=model_id,
            messages=formatted_input
        )
        response_content = completion.choices[0].message.content
        print(response_content)
        cost["Total Tokens"] = completion.usage.total_tokens
        cost["Prompt Tokens"] = completion.usage.prompt_tokens
        cost["Completion Tokens"] = completion.usage.completion_tokens
        cost["Total Cost (USD)"] = 0  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算
        return response_content, cost


# 评估mutate llm的变异结果并检测bug
def detect_bug(mutate_name):
    detect_results = {}
    exec_fail_mutate_sql_indexes = []
    oracle_false_indexes = []
    with open(results_filenames[mutate_name], "r", encoding="utf-8") as r:
        lines = r.readlines()
    total_num = len(lines)
    total_mutate_sql_num = 0  # 所有可能的mutate语句总数
    exec_success_mutate_sql_num = 0  #所有可能的mutate语句中成功执行的数量

    for line in lines:
        data = json.loads(line)
        MutateLLM_Result = eval(data["MutateLLM_Result"])
        MutateLLM_OracleCheck = data["MutateLLM_OracleCheck"]

        total_mutate_sql_num += len(MutateLLM_Result)
        for possible_answer in MutateLLM_OracleCheck:
            # 1.执行成功率：postgres的所有变异结果的执行成功率
            if possible_answer["mutate_exec"]["exec_result"] != "None":
                exec_success_mutate_sql_num += 1
                # 2.检测bug：变异前和变异后的结果集是否满足oracle（IsUpper: ((candidate.U ^ candidate.Flag) ^ 1) == 1）
                if possible_answer["CheckOracle"]["end"] == False:
                    oracle_false_indexes.append(data["index"])
                # 3.分析不满足oracle的测试项
            else:
                exec_fail_mutate_sql_indexes.append(data["index"])

    success_rate = str(exec_success_mutate_sql_num/total_mutate_sql_num)+"("+str(exec_success_mutate_sql_num)+"/"+str(total_mutate_sql_num)+")"
    detect_results["ExecSuccessRate"] = success_rate
    detect_results["ExecFailIndexes"] = exec_fail_mutate_sql_indexes
    detect_results["OracleFalseIndexes"] = oracle_false_indexes

    with open(eval_filenames[mutate_name], "w", encoding="utf-8") as w:
        json.dump(detect_results, w, indent=4)

