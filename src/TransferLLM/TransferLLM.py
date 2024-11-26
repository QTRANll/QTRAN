# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/26 17:09
# @Author  : zql
# @File    : TransferLLM.py
# @Intro   :

import os
import json
import random
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.callbacks import get_openai_callback
from src.Tools.DatabaseConnect.database_connector import exec_sql_statement


db_names = ["mysql", "mariadb", "tidb"]

def load_data(output_name, db_name, len_low, len_high, is_random, num):
    """
    # 加载数据：
    # 加载所有的originalSql及对应的originalSqlsim数据：长度在[len_low,len_high)。
    # len_high = float('inf')代表无穷大;len_low=1,len_high = float('inf')则表示获取所有数据
    # random=True时,则随机选择num条数据；random=False时，则返回长度在[len_low,len_high)的所有数据
    # 源文件：Pinolo Output/output(1-4)/dbname文件夹内的originalSql_all.json,originalSqlsim_all.json
    # 目标文件：Pinolo Output/output_test下ALL和RANDOM文件夹内的output1_mariadb_x_x_originalSql_all.json，output1_mariadb_x_x_originalSqlsim_all.json，output1_mariadb_x_x_originalSqlIndex_all.json
    """
    if len_low >= len_high:
        return
    # sql语句的文件名
    filename = os.path.join("..\..\Dataset\Pinolo Output", output_name, db_name+"_merged", "originalSql_all.json")
    # sqlsim语句的文件名
    sim_filename = os.path.join("..\..\Dataset\Pinolo Output", output_name, db_name+"_merged", "originalSqlsim_all.json")
    # 存储加载所得数据的目标文件名
    dir_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "ALL", output_name+"_" + db_name+"_"+str(len_low)+"_"+str(len_high)+"_originalSql_all.json")
    dir_sim_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "ALL", output_name+"_" + db_name+"_"+str(len_low)+"_"+str(len_high)+"_originalSqlsim_all.json")
    dir_index_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "ALL", output_name+"_" + db_name+"_"+str(len_low)+"_"+str(len_high)+"_originalSqlIndex_all.json")

    # 文件已存在，返回
    if os.path.exists(dir_filename) and os.path.exists(dir_sim_filename) and os.path.exists(dir_index_filename):
        return

    with open(filename, "r", encoding="utf-8") as rf:
        contents = json.load(rf)
    with open(sim_filename, "r", encoding="utf-8") as f:
        sim_contents = json.load(f)

    selected_sqls = []
    selected_sqlsims = []
    selected_sql_indexes = []
    # 选取指定长度区间的数据
    for i in range(len(contents)):
        content = contents[i]
        if len_low <= len(content) < len_high:
            selected_sqls.append(content)
            selected_sqlsims.append(sim_contents[i])
            selected_sql_indexes.append(i)

    if is_random:
        # 随机加载：从指定长度区间中随机选择num条数据并返回
        random_num = 0
        random_sqls = []
        random_sqlsims = []
        random_sql_indexes = []
        if len(selected_sqls) < num:
            # [len_low,len_high)的数量小于要提取的数目num
            random_num = len(selected_sqls)
            random_sqls = selected_sqls
            random_sqlsims = selected_sqlsims
            random_sql_indexes = selected_sql_indexes
        else:
            random_num = num
            random_numbers = random.sample(range(0, len(selected_sqls)), num)
            for number in random_numbers:
                random_sqls.append(selected_sqls[number])
                random_sqlsims.append(selected_sqlsims[number])
                random_sql_indexes.append(selected_sql_indexes[number])
        random_dir_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "RANDOM", output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSql_random_" + str(random_num)+".json")
        random_dir_sim_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "RANDOM", output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlsim_random_" + str(random_num)+".json")
        random_dir_index_filename = os.path.join("..\..\Dataset\Pinolo Output", "output_test", "RANDOM", output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlIndex_ramdom_" + str(random_num)+".json")
        with open(random_dir_filename, 'w', encoding='utf-8') as f:
            json.dump(random_sqls, f, indent=4)
        with open(random_dir_sim_filename, 'w', encoding='utf-8') as f:
            json.dump(random_sqlsims, f, indent=4)
        with open(random_dir_index_filename, 'w', encoding='utf-8') as f:
            json.dump(random_sql_indexes, f, indent=4)
        print(random_dir_filename + ":" + str(len(random_sqls)))
        print(random_dir_sim_filename + ":" + str(len(random_sqlsims)))
    else:
        # 全部加载：直接存储所有[len_low,len_high)长度的数据
        with open(dir_filename, 'w', encoding='utf-8') as f:
            json.dump(selected_sqls, f, indent=4)
        with open(dir_sim_filename, 'w', encoding='utf-8') as f:
            json.dump(selected_sqlsims, f, indent=4)
        with open(dir_index_filename, 'w', encoding='utf-8') as f:
            json.dump(selected_sql_indexes, f, indent=4)

        print(dir_filename + ":" + str(len(selected_sqls)))
        print(dir_sim_filename + ":" + str(len(selected_sqlsims)))


def init_data(output_name, db_name, len_low, len_high, is_random, num):
    """
    # 初始化结果数据：
    # 根据load_data()得到的数据，初始化结果数据并存储到output_test文件夹中
    # 源文件：Pinolo Output/output_test下ALL和RANDOM文件夹内的output1_mariadb_x_x_originalSql_all.json，output1_mariadb_x_x_originalSqlsim_all.json，output1_mariadb_x_x_originalSqlIndex_all.json
    # 目标文件：Pinolo Output/output_test下ALL和RANDOM文件夹内的init_output1_mariadb_x_x_originalSql_all.json,init_output1_mariadb_x_x_originalSqlsim_all.json
    """
    prefix = os.path.join("..\..\Dataset\Pinolo Output", "output_test")
    # exec_args = database_connection_args[db_name]

    # 源文件和目标文件
    if is_random:
        sql_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSql_random_" + str(num) + ".json"
        sqlsim_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlsim_random_" + str(num) + ".json"
        index_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlIndex_ramdom_" + str(num) + ".json"
        sql_filename = os.path.join(prefix, "RANDOM", sql_temp)
        sqlsim_filename = os.path.join(prefix,  "RANDOM", sqlsim_temp)
        index_filename = os.path.join(prefix, "RANDOM", index_temp)
        sql_dir_filename = os.path.join(prefix, "RANDOM", "init_"+sql_temp)
        sqlsim_dir_filename = os.path.join(prefix, "RANDOM", "init_"+sqlsim_temp)
    else:
        sql_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSql_all.json"
        sqlsim_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlsim_all.json"
        index_temp = output_name + "_" + db_name + "_" + str(len_low) + "_" + str(len_high) + "_originalSqlIndex_all.json"
        sql_filename = os.path.join(prefix, "ALL", sql_temp)
        sqlsim_filename = os.path.join(prefix, "ALL", sqlsim_temp)
        index_filename = os.path.join(prefix, "ALL", index_temp)
        sql_dir_filename = os.path.join(prefix, "ALL", "init_"+sql_temp)
        sqlsim_dir_filename = os.path.join(prefix, "ALL", "init_"+sqlsim_temp)

    # 文件已存在，返回
    if os.path.exists(sql_dir_filename) and os.path.exists(sqlsim_dir_filename):
        return

    with open(sql_filename, "r", encoding="utf-8") as rf:
        sqls = json.load(rf)
    with open(sqlsim_filename, "r", encoding="utf-8") as rf:
        sqlsims = json.load(rf)
    with open(index_filename, "r", encoding="utf-8") as rf:
        sql_indexes = json.load(rf)
    # 初始化结果数据
    sql_init_results = []
    sqlsim_init_results = []
    avg_sql_length = 0
    avg_sqlsim_length = 0
    for index in range(len(sqls)):
        result = {
            "index": index,
            "origin_index": sql_indexes[index],
            "Sql": sqls[index],
            "SqlLength": len(sqls[index]),
            "SqlExecResult": "",
            "SqlExecTime": "",
            "SqlExecError": "",
            "TransferResult": [],
            "TransferCost": [],
            "TransferSqlExecResult": [],
            "TransferSqlExecTime": [],
            "TransferSqlExecError": [],
            "TransferSqlExecEqualities": []
        }
        sim_result = {
            "index": index,
            "origin_index": sql_indexes[index],
            "Sql": sqlsims[index],
            "SqlLength": len(sqlsims[index]),
            "SqlExecResult": "",
            "SqlExecTime": "",
            "SqlExecError": "",
            "TransferResult": [],
            "TransferCost": [],
            "TransferSqlExecResult": [],
            "TransferSqlExecTime": [],
            "TransferSqlExecError": [],
            "TransferSqlExecEqualities": []
        }
        avg_sql_length += len(sqls[index])
        avg_sqlsim_length += len(sqlsims[index])
        sql_init_results.append(result)
        sqlsim_init_results.append(sim_result)

    avg_sql_length /= len(sqls)
    avg_sqlsim_length /= len(sqlsims)
    print("sql平均长度："+str(avg_sql_length))
    print("sqlsim平均长度："+str(avg_sqlsim_length))
    with open(sql_dir_filename, 'w', encoding='utf-8') as f:
        json.dump(sql_init_results, f, indent=4)

    with open(sqlsim_dir_filename, 'w', encoding='utf-8') as f:
        json.dump(sqlsim_init_results, f, indent=4)

# 处理传递给transfer llm的sql statement(这是针对pinolo的process)
def sql_statement_process(origin_sql):
    map_list = {
        "col_decimal(40, 20)_undef_signed": "col_decimal_40_20_undef_signed",
        "col_decimal(40, 20)_undef_unsigned": "col_decimal_40_20_undef_unsigned",
        "col_decimal(40, 20)_key_signed": "col_decimal_40_20_key_signed",
        "col_decimal(40, 20)_key_unsigned": "col_decimal_40_20_key_unsigned",
        "col_char(20)_undef_signed": "col_char_20_undef_signed",
        "col_char(20)_key_signed": "col_char_20_key_signed",
        "col_varchar(20)_undef_signed": "col_varchar_20_undef_signed",
        "col_varchar(20)_key_signed": "col_varchar_20_key_signed"
    }
    sql_statement = origin_sql
    for key, value in map_list.items():
        if key in origin_sql:
            sql_statement = sql_statement.replace(key, value)
    return sql_statement


def get_examples_string(FewShot, origin_db, target_db):
    examples_string = ""
    examples_data = None
    if FewShot:  # 给出样例
        # example是给出的例子
        with open(os.path.join("../../Dataset/Pinolo Output/output_test/",
                               "examples_" + origin_db + "_" + target_db + ".json"), "r", encoding="utf-8") as r:
            examples_data = json.load(r)
        example = None
        for index in range(len(examples_data)):
            example = examples_data[index]
            OriginDB = example["origin_db"]
            TargetDB = example["target_db"]
            SQL = example["Sql"]
            Answer = json.dumps(example["answer"])
            # 坏了，这句好像写在for循环外面了
            examples_string = examples_string + '[Example ' + str(
                index) + ' start]: ' + '[original database]: ' + OriginDB + '\n' + '[target database]: ' + TargetDB + '\n' + '[sql statement]: ' + SQL + '\n' + '[Answer]: ' + Answer + '\n' + '[Example ' + str(
                index) + ' end]\n'
    return examples_string

"""
def get_feature_knowledge_string(origin_db, target_db, with_knowledge, mapping_indexes):
    knowledge_string = ""
    steps_string = ""
    examples_data = None
    if with_knowledge:  # 给出样例
        # 获取对应的详细信息
        names_ = "merge"
        for feature_type in ["function"]:
            names_ = names_ + "_" + feature_type
        origin_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase Processed1", origin_db, "RAG_Embedding_Data",names_ + ".jsonl")
        target_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase Processed1", target_db,"RAG_Embedding_Data", names_ + ".jsonl")
        with open(origin_merge_feature_filename, "r", encoding="utf-8") as r:
            origin_features = r.readlines()
        with open(target_merge_feature_filename, "r", encoding="utf-8") as r:
            target_features = r.readlines()
        cnt = 0
        for mapping_pair in mapping_indexes:
            # 获取a_db以及b_db中的feature knowledge
            origin_feature = json.loads(origin_features[mapping_pair[0]])
            target_feature = json.loads(target_features[mapping_pair[1]])
            knowledge_string = knowledge_string + "[Feature Mapping "+str(cnt) + " Start]" + "Here is the original feature.\n"
            knowledge_string = knowledge_string + "Feature Syntax(Database "+origin_db+"):"
            for item in origin_feature["Feature"]:
                knowledge_string += item
            knowledge_string += "\nDescription(Database "+origin_db+"):"
            for item in origin_feature["Description"]:
                knowledge_string += item
            knowledge_string = knowledge_string + "\nExamples(Database "+origin_db+"):"
            for item in origin_feature["Examples"]:
                knowledge_string += item

            knowledge_string += "Here is the mapping feature.\n"

            knowledge_string = knowledge_string + "Feature Syntax(Database "+target_db+"):"
            for item in target_feature["Feature"]:
                knowledge_string += item
            knowledge_string = knowledge_string + "\nDescription(Database "+origin_db+"):"
            for item in target_feature["Description"]:
                knowledge_string += item
            knowledge_string = knowledge_string + "\nExamples(Database "+origin_db+"):"
            for item in target_feature["Examples"]:
                knowledge_string += item
            knowledge_string += "\n"

            knowledge_string = knowledge_string + "[Feature Mapping " + str(cnt) + " End]"

            # 拼接steps的提示词
            steps_string = steps_string + "Replace "+str(origin_feature["Feature"])+" from "+origin_db+" in original sql with "+str(target_feature["Feature"])+" from "+target_db+"\n"
            cnt += 1
    return knowledge_string, steps_string
"""

def get_feature_knowledge_string(origin_db, target_db, with_knowledge, mapping_indexes):
    knowledge_string = ""
    steps_string = ""
    examples_data = None
    if with_knowledge:  # 给出样例
        # 获取对应的详细信息
        names_ = "merge"
        for feature_type in ["function"]:
            names_ = names_ + "_" + feature_type
        origin_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", origin_db, "RAG_Embedding_Data",names_ + ".jsonl")
        target_merge_feature_filename = os.path.join("..", "..", "FeatureKnowledgeBase", target_db,"RAG_Embedding_Data", names_ + ".jsonl")
        with open(origin_merge_feature_filename, "r", encoding="utf-8") as r:
            origin_features = r.readlines()
        with open(target_merge_feature_filename, "r", encoding="utf-8") as r:
            target_features = r.readlines()
        cnt = 0
        for mapping_pair in mapping_indexes:
            # 获取a_db以及b_db中的feature knowledge
            origin_feature = json.loads(origin_features[mapping_pair[0]])
            target_feature = json.loads(target_features[mapping_pair[1]])
            knowledge_string = knowledge_string + " Step " + str(cnt) + ": Transfer " + str(origin_feature["Feature"])+" from "+origin_db+" to "+str(target_feature["Feature"])+" from "+target_db+"\n"

            knowledge_string = knowledge_string + "Here is the original feature from "+origin_db +".\n"
            knowledge_string = knowledge_string + "Feature Syntax(Database "+origin_db+"):"
            for item in origin_feature["Feature"]:
                knowledge_string += item

            """
            knowledge_string += "\nDescription(Database "+origin_db+"):"
            for item in origin_feature["Description"]:
                knowledge_string += item
            """

            knowledge_string = knowledge_string + "\nExamples(Database "+origin_db+"):"
            for item in origin_feature["Examples"]:
                knowledge_string += item

            knowledge_string = knowledge_string + "Here is the mapping feature from "+target_db +".\n"

            knowledge_string = knowledge_string + "Feature Syntax(Database "+target_db+"):"
            for item in target_feature["Feature"]:
                knowledge_string += item
            """
            knowledge_string = knowledge_string + "\nDescription(Database "+origin_db+"):"
            for item in target_feature["Description"]:
                knowledge_string += item
            """
            knowledge_string = knowledge_string + "\nExamples(Database "+origin_db+"):"
            for item in target_feature["Examples"]:
                knowledge_string += item
            knowledge_string += "\n\n"

            cnt += 1
    return knowledge_string

def transfer_llm(tool, exp, conversation, error_iteration, iteration_num, FewShot, with_knowledge, origin_db, target_db, test_info):
    """
    # transfer llm:单条sql语句的转换及结果处理
    # 返回结果：costs, transfer_results, exec_results, exec_times, error_messages, str(origin_exec_result), str(origin_exec_time), str(origin_error_message), exec_equalities
    :return:
    # * transfer llm的花销列表"costs",结果列表"transfer_results"，
    # * 转换后语句Sql的运行结果列表"exec_results"，运行报错列表"error_messages"，
    # * 转换前语句Sql，对应运行结果"str(origin_exec_result)"，运行报错"str(origin_error_message)"
    # * 运行结果与原sql的一致性列表"exec_equalities"
    # * 列表是为返回error进行迭代设计的，能记录多次迭代的过程值
    """

    sql_statement = test_info["sql"]
    sql_statement_processed = sql_statement
    # 如果是mysql_like转postgres，先把sql语句的列名进行替换，和postgres的ddl语句中的列名保持一致，便于后续语句转换
    if target_db == "postgres" and tool.lower() == "pinolo":
        sql_statement_processed = sql_statement_process(sql_statement)

    transfer_llm_string = """  
    Let's think step by step.You are an expert in sql statement translation between different database.\
    With the assistance of feature knowledge,transfer the following {origin_db} statement to executable {target_db} statement with similar semantics.\
    {origin_db} statement: {sql_statement}\

    Transfer should ensure following requirements:
    1. All column names and feature variables remain unchanged.
    2. Strictly forbid meaningless features(such as NULL,0), features with random return value(such as current_time).
    3. Transfer as far as possible, and ensure similar semantics.\

    Transfer by carrying out following instructions step by step.\
    {feature_knowledge}\
    
    Check if transfer result satisfies requirements mentioned before.If not,modify the result.

    Here are some transfer examples: {examples}\
    Answer the following information: {format_instructions}
    """

    response_schemas = [
        ResponseSchema(type="string", name="TransferSQL", description='The transferred SQL statement result.'),
        ResponseSchema(type="string", name="Explanation", description='Explain the basis for the conversion.')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    examples_string = get_examples_string(FewShot, origin_db,target_db)
    if with_knowledge:
        feature_knowledge_string = get_feature_knowledge_string(origin_db, target_db, with_knowledge, test_info["SqlPotentialDialectFunctionMapping"])
    else:
        feature_knowledge_string = ""

    prompt_template = ChatPromptTemplate.from_template(transfer_llm_string)

    iterate_llm_string = """  
    The corresponding executable SQL statement that you provided in your most recent response resulted in an error when executed.\
    Please modify your most recent SQL statement response based on the error message.\
    Ensure that all column names remain unchanged between the sql statements before and after the transfer.\
    error message:{error_message}  
    Answer the following information: {format_instructions}  
    """

    iterate_response_schemas = [
        ResponseSchema(type="string", name="TransferSQL", description='The new transferred SQL statement result after modification.'),
        ResponseSchema(type="string", name="Explanation", description='Explain the basis for the conversion and modification.')
    ]

    iterate_output_parser = StructuredOutputParser.from_response_schemas(iterate_response_schemas)
    iterate_format_instructions = iterate_output_parser.get_format_instructions()

    iterate_prompt_template = ChatPromptTemplate.from_template(iterate_llm_string)

    costs = []
    transfer_results = []
    exec_results = []
    exec_times = []
    error_messages = []
    exec_equalities = []
    # 执行origin sql得到结果，并和得到的所有transfer sql结果依次进行比对，确定执行结果是否相同，将对比结果存储到exec_same中
    origin_exec_result, origin_exec_time, origin_error_message = exec_sql_statement(tool, exp, origin_db, sql_statement)

    conversation_cnt = 0  # conversation_cnt = 0:初始第一条prompt
    # 边界1：达到最大迭代次数
    while conversation_cnt <= iteration_num:
        prompt_messages = None
        if conversation_cnt == 0:
            # 初始第一条prompt
            prompt_messages = prompt_template.format_messages(
                origin_db=origin_db,
                target_db=target_db,
                sql_statement=sql_statement_processed,
                examples=examples_string,
                feature_knowledge=feature_knowledge_string,
                format_instructions=format_instructions
            )
        else:
            # 边界2：判断是否需要迭代，不需要迭代则break跳出while循环
            print(error_messages)
            if error_iteration is False:
                break
            # 边界3：判断上一次得到的transfer sql执行是否执行成功，能执行成功则break直接跳出循环，执行失败则进行下面的error信息迭代处理
            if len(error_messages) and error_messages[-1] == "None":
                break

            # error信息迭代处理：
            # 针对执行失败的transfer sql，将执行的error信息返回给llm，提示llm根据error信息重新生成新的transfer sql，反复迭代
            # 此处运用了ConversationBufferMemory()，并且规定了最高迭代次数为 iteration_num

            # 迭代的prompt：每次取error_messages数组的最后一个元素，则为最新的报错信息
            prompt_messages = iterate_prompt_template.format_messages(
                error_message=error_messages[-1] if len(error_messages) else "",
                format_instructions=iterate_format_instructions
            )

        """
        try:

        except Exception as e:
            print("transfer llm:")
            print(e)
        """
        cost = {}
        with (get_openai_callback() as cb):
            print(prompt_messages[0].content)
            response = conversation.predict(input=prompt_messages[0].content)
            output_dict = output_parser.parse(response)
            # print(response)
            print(output_dict)
            cost["Total Tokens"] = cb.total_tokens
            cost["Prompt Tokens"] = cb.prompt_tokens
            cost["Completion Tokens"] = cb.completion_tokens
            cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算

            exec_result, exec_time, error_message = exec_sql_statement(tool, exp, target_db, output_dict["TransferSQL"])
            costs.append(cost)
            transfer_results.append(output_dict)
            exec_results.append(str(exec_result))
            exec_times.append(str(exec_time))
            # 简化error_message,只留下关键部分
            """
            if error_message:
                error_message = error_message.split(":")[1]
            """
            print(error_messages)
            error_messages.append(str(error_message))
            if not error_message and not origin_error_message and exec_result == origin_exec_result:
                exec_equalities.append(True)
            else:
                exec_equalities.append(False)
        conversation_cnt += 1

    return costs, transfer_results, exec_results, exec_times, error_messages, str(origin_exec_result), str(origin_exec_time), str(origin_error_message), exec_equalities

def pinolo_qtran_run(input_filename,tool,temperature=0.3, model="gpt-4o-mini",error_iteration=True,iteration_num=4,FewShot=False,with_knowledge=True):
    return

def get_feature_knowledge(value,feature_type):
    if feature_type == "function":
        mapping_indexes = value["SqlPotentialDialectFunctionMapping"]

def transfer_data(tool,temperature, model, error_iteration, iteration_num, FewShot, with_knowledge, output_name, origin_db_name, target_db_name, len_low, len_high, IsRandom, num, sqls_type):
    """
    # transfer data：将经过init_data()处理的初始化后数据，逐条进行transfer llm的转换并存储结果
    # 源文件：Pinolo Output/output_test下ALL和RANDOM文件夹内的init_output1_mariadb_x_x_originalSql_all.json,init_output1_mariadb_x_x_originalSqlsim_all.json
    # 目标文件：Pinolo Output/output_test_results下ALL和RANDOM文件夹内的文件
    """

    results_filename = None
    sqls_filename = None
    if IsRandom:
        sql_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSql_random_" + str(num) + ".jsonl"
        sqlsim_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSqlsim_random_" + str(num) + ".jsonl"
        res_sql_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSql_random_" + str(num) + ".jsonl"
        res_sqlsim_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSqlsim_random_" + str(num) + ".jsonl"
        if FewShot:
            res_sql_temp = "fewshot_"+res_sql_temp
            res_sqlsim_temp = "fewshot_" + res_sqlsim_temp
        if error_iteration:
            res_sql_temp = "iterated_"+res_sql_temp
            res_sqlsim_temp = "iterated_" + res_sqlsim_temp
        if sqls_type == "origin":
            sqls_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "PotentialDialectFeatures", "RANDOM", "init_"+sql_temp)
            results_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "Results_With_Feature_Knowledge", "RANDOM", res_sql_temp)
        elif sqls_type == "simple":
            sqls_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "PotentialDialectFeatures", "RANDOM", "init_"+sqlsim_temp)
            results_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "Results_With_Feature_Knowledge", "RANDOM", res_sqlsim_temp)
    else:
        sql_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSql_all_" + str(num) + ".jsonl"
        sqlsim_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name + "_" + str(len_low) + "_" + str(
            len_high) + "_originalSqlsim_all_" + str(num) + ".jsonl"
        res_sql_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name+"_" + str(len_low) + "_" + str(len_high) + "_originalSql_all.jsonl"
        res_sqlsim_temp = output_name + "_" + origin_db_name + "_to_" + target_db_name+"_" + str(len_low) + "_" + str(len_high) + "_originalSqlsim_all.jsonl"
        if FewShot:
            res_sql_temp = "fewshot_" + res_sql_temp
            res_sqlsim_temp = "fewshot_" + res_sqlsim_temp
        if error_iteration:
            res_sql_temp = "iterated_" + res_sql_temp
            res_sqlsim_temp = "iterated_" + res_sqlsim_temp
        if sqls_type == "origin":
            sqls_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "PotentialDialectFeatures", "ALL", "init_"+sql_temp)
            results_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "Results_With_Feature_Knowledge", "ALL", res_sql_temp)
        elif sqls_type == "simple":
            sqls_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "PotentialDialectFeatures", "ALL", "init_"+sqlsim_temp)
            results_filename = os.path.join("..\..\Output\TransferLLM\Pinolo", "Results_With_Feature_Knowledge", "ALL", res_sqlsim_temp)

    processed_cnt = 0
    if os.path.exists(results_filename):
        with open(results_filename, "r", encoding="utf-8") as rf:
            processed_cnt = len(rf.readlines())

    with open(sqls_filename, "r", encoding="utf-8") as rf:
        Sqls = rf.readlines()

    for index in range(len(Sqls)):
        # for index in range(30):
        value = json.loads(Sqls[index])
        print(index)
        if value["index"] < processed_cnt:
            continue
        print(value)
        costs, transfer_results, exec_results, exec_times, error_messages, origin_exec_result, origin_exec_time, origin_error_message, exec_equalities = transfer_llm(
            tool=tool,
            temperature=temperature,
            model=model,
            error_iteration=error_iteration,
            iteration_num=iteration_num,
            FewShot=FewShot,
            with_knowledge=with_knowledge,
            origin_db=origin_db_name,
            target_db=target_db_name,
            test_info=value
        )

        value["SqlExecResult"] = origin_exec_result
        value["SqlExecTime"] = origin_exec_time
        value["SqlExecError"] = origin_error_message

        value["TransferResult"] = transfer_results
        value["TransferCost"] = costs
        value["TransferSqlExecResult"] = exec_results
        value["TransferSqlExecTime"] = exec_times
        value["TransferSqlExecError"] = error_messages  # 记录transfer sql的多次执行是否有报错：如果为None则表示成功执行，如果不是None而是具体报错则说明执行失败
        value["TransferSqlExecEqualities"] = exec_equalities  # 记录transfer sql的多次执行结果是否与origin sql一样：如果为True则说明一样，否则为不一样

        with open(results_filename, 'a', encoding='utf-8') as a:
            json.dump(value, a)
            a.write('\n')

        try:
            a = 1
        except Exception as e:
            print(e)


# sql_type:"origin"或"simple"，分别代表原始sql和简化后的sql
def exec_transfer_llm(temperature, model, error_iteration, iteration_num, FewShot, with_knowledge, output_name, origin_db_name, target_db_name, len_low, len_high, IsRandom, num, sqls_type):
    load_data(output_name, origin_db_name, len_low, len_high, IsRandom, num)
    init_data(output_name, origin_db_name, len_low, len_high, IsRandom, num)
    transfer_data("pinolo",temperature, model, error_iteration, iteration_num, FewShot, with_knowledge, output_name, origin_db_name, target_db_name, len_low, len_high, IsRandom, num, sqls_type)



