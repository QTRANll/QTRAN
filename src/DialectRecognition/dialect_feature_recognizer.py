# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/17 16:39
# @Author  : shaocanfan
# @File    : dialect_feature_recognizer.py
# @Intro   : transfer a_db to b_db时，识别a_db sql中对于d_db是方言的所有feature元素(functions+operators)
import json
import os
import sqlglot
import re
from src.Tools.database_connector import exec_sql_statement, database_connection_args_sqlancer, database_connection_args_pinolo
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.chains import ConversationChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from src.DialectRecognition.TokenType_not_op import TokenType_not_op


effective_sqls_generator_v2_skip = [
    "BINLOG_GTID_POS.json",
    "COLUMN_ADD.json",
    "COLUMN_DELETE.json",
    "COLUMN_EXISTS.json",
    "COLUMN_GET.json",
    "COLUMN_JSON.json",
    "CROSSES.json",
    "LIKE.json",
    "MATCH AGAINST.json",
    "NEXT VALUE for sequence_name.json",
    "NOT LIKE.json",
    "NOT REGEXP.json",
    "OVERLAPS.json",
    "PERCENTILE_DISC.json",
    "PREVIOUS VALUE FOR sequence_name.json",
    "RLIKE.json",
    "SETVAL.json",
    "SPIDER_BG_DIRECT_SQL.json",
    "SPIDER_COPY_TABLES.json",
    "SPIDER_DIRECT_SQL.json",
    "ST_NUMGEOMETRIES.json",
    "VALUES _ VALUE.json",
    "VEC_DISTANCE.json",
    "WSREP_SYNC_WAIT_UPTO_GTID.json"
]



def tokenize_sql(sql):
    lists = sqlglot.tokenize(sql)
    return lists


# 判断枚举成员的名称
def is_member_name(name):
    return name in TokenType_not_op.__members__


def potential_features_refiner_single_sql(origin_sql):
    lists = tokenize_sql(origin_sql)  # 利用sqlglot分词函数得到origin_sql的分词列表
    val_indexes = []  # 类型为VAL的分词的下标
    function_name_indexes = []  # potential functions的分词的下标
    operator_indexes = []  # potential functions的分词的下标
    function_names = []  # potential functions的分词的下标
    operators = []  # potential functions的分词的下标

    # 遍历所有分词结果，refine operator features
    for index in range(len(lists)):
        if lists[index].token_type in [sqlglot.TokenType.VAR, sqlglot.TokenType.LEFT, sqlglot.TokenType.TIMESTAMP]:
            val_indexes.append(index)
        if not is_member_name(str(lists[index].token_type).split(".")[-1]):
            operator_indexes.append(index)
            operators.append(lists[index].text)

    # refine potential function features:sqlglot.TokenType.VAR后一个字符为sqlglot.TokenType.L_PAREN，且左边字符不为sqlglot.TokenType.UNKNOWN，则认为是potential functions
    for VAL_index in val_indexes:
        if VAL_index + 1 < len(lists) and lists[VAL_index+1].token_type == sqlglot.TokenType.L_PAREN and lists[VAL_index-1].token_type != sqlglot.TokenType.UNKNOWN and lists[VAL_index-1].text.lower() != "table":
            function_name_indexes.append(VAL_index)
            function_names.append(lists[VAL_index].text)

    print(origin_sql)
    """
    for item in lists:
        print(item)
    """
    """
    print("operators features")
    for index in operator_indexes:
        print(lists[index])

    print("function features")
    for index in function_name_indexes:
        print(lists[index])
    print('----------------')
    """

    return function_name_indexes, operator_indexes, function_names, operators


def potential_features_refiner(db_name, filename, dir_filename):
    # 从filename中获取测试集(数据库类型为db_name)，提取测试集中所有数据项的sql的potential features
    with open(filename, "r", encoding="utf-8") as r:
        contents = json.load(r)
    results = []
    for content in contents:
        # 遍历处理所有测试数据
        content["SqlPotentialFunctionIndexes"], content["SqlPotentialOperatorIndexes"],_,_ = potential_features_refiner_single_sql(content["Sql"])
        results.append(content)

    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(results, w, indent=4)

def effective_sqls_refiner(db_name, feature_type,tool):
    # 从feature的Examples字符串中提取出可执行的sql语句
    if tool.lower() == "pinolo":
        database_args = database_connection_args_pinolo[db_name]
    elif tool.lower() == "sqlancer":
        database_args = database_connection_args_sqlancer[db_name]

    if feature_type in ["Functions", "Operators"]:
        effective_feature_cnt = 0  # 记录有效的feature个数，即文件中的description和feature语法部分不为空
        indistinct_feature_cnt = 0  # 记录唯一的feature个数
        none_effective_cnt = 0  # 未提取到effective sql的feature数量
        none_example_cnt = 0  # 官网未提供Example字符串的feature数量
        source_dic = os.path.join("..", "..", "Feature Knowledge Base", db_name, feature_type,
                                  feature_type + "_Results")
        direct_dic = os.path.join("..", "..", "Feature Knowledge Base Processed", db_name, feature_type,
                                  feature_type + "_Results")
        ineffective_sqls_filename = os.path.join("..", "..", "Feature Knowledge Base Processed", db_name, feature_type, "ineffective_sqls.jsonl")
        dropped_list_filename = os.path.join("..", "..", "Feature Knowledge Base Processed", db_name, feature_type, "dropped_files.jsonl")


        if os.path.exists(ineffective_sqls_filename):
            print(ineffective_sqls_filename+"已存在："+db_name+"_"+feature_type+"的Effective sqls refiner已完成！")
            return
        source_filenames = os.listdir(source_dic)

        # 获取同义feature个数
        if os.path.exists(os.path.join(os.path.dirname(source_dic), "synonym_feature_filenames.jsonl")):
            with open(os.path.join(os.path.dirname(source_dic), "synonym_feature_filenames.jsonl"), 'r',
                      encoding='utf-8') as file:
                indistinct_feature_cnt = sum(1 for line in file)
        else:
            indistinct_feature_cnt = 0

        # 遍历Functions_Results内的所有结果文件，预处理单个feature内所有Examples语句，将结果存到Feature Knowledge Base Processed文件夹
        # 1.提取examples字符串中的sql语句(正则表达式匹配)
        # 2.执行提取出来的sql语句，只保留可执行的sql语句
        # 3.将提取出来的effective sqls更新到feature knowledge base processed中

        # 正则表达式模式，用于匹配 SQL 语句
        sql_pattern = r'(?i)(SELECT.*?;|SET.*?;|INSERT.*?;|UPDATE.*?;|DELETE.*?;|CREATE.*?;|DROP.*?;|ALTER.*?;|TRUNCATE.*?;|MERGE.*?;|CALL|EXEC.*?;)'
        # pattern = r'(?i)(SELECT.*?;|INSERT.*?;|UPDATE.*?;|DELETE.*?;|CREATE.*?;|DROP.*?;|ALTER.*?;|TRUNCATE.*?;|MERGE.*?;|CALL|EXEC.*?;|SELECT.*?\n|INSERT.*?\n|UPDATE.*?\n|DELETE.*?\n|CREATE.*?\n|DROP.*?\n|ALTER.*?\n|TRUNCATE.*?\n|MERGE.*?\n|CALL|EXEC.*?\n)'

        for filename in source_filenames:
            # 重复的同义文件直接跳过
            effective_sqls = []  # 存储提取过程中的effective sqls：执行成功
            ineffective_sqls = []  # 存储提取过程中的ineffective sqls：执行失败
            ineffective_wrong_messages = []  # 存储提取过程中的ineffective sqls的执行失败原因
            with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
                content = json.load(r)

            # 对于description和feature都为空的feature，跳过，不包含
            if len(content["Feature"]) == 0 and len(content["Description"]) == 0:
                with open(dropped_list_filename, "a", encoding="utf-8") as w:
                    json.dump(content, w)
                    w.write('\n')
                continue
            else:
                effective_feature_cnt += 1

            if len(content["Examples"]) == 0:
                # 官网未提供Example字符串的feature数量
                none_example_cnt += 1


            # 提取Examples字符串中的sql语句
            for examples in content["Examples"]:
                # 1.提取examples字符串中的sql语句(正则表达式匹配)
                matches = re.findall(sql_pattern, examples, re.DOTALL)
                print(matches)
                for match in matches:
                    # 判断match中是否包含feature元素，不包含则认为与feature无关，跳过。这里对于feature name的处理，简化为取title的字符串并以空格划分，取第一个元素。
                    if feature_type == "Functions":
                        feature_name = content["Title"].split(" ")[0]
                    else:
                        feature_name = ""
                    if feature_name.lower() not in match.lower():
                        continue
                    # 2.执行提取出来的sql语句，只保留可执行的sql语句
                    exec_result, _, exec_error_message = exec_sql_statement(tool,db_name,match.strip())
                    if not exec_error_message:
                        effective_sqls.append(match.strip())
                    else:
                        ineffective_sqls.append(match.strip())
                        ineffective_wrong_messages.append(exec_error_message)

            if len(effective_sqls) == 0:
                # 说明该feature没有提取出任何一个有效的sql
                none_effective_cnt += 1
                if len(content["Examples"]) != 0:
                    # 若其examples字符串列表还不为空，则说明提取出来的sql不可运行
                    content_temp = content
                    content_temp["Effective SQLs Refined"] = effective_sqls
                    content_temp["Ineffective SQLs Refined"] = ineffective_sqls
                    content_temp["Wrong Messages from Ineffective SQLs Refined"] = ineffective_wrong_messages
                    with open(ineffective_sqls_filename, "a", encoding="utf-8") as w:
                        json.dump(content_temp, w)
                        w.write('\n')
            content["Effective SQLs Refined"] = effective_sqls
            content["Ineffective SQLs Refined"] = ineffective_sqls
            content["Wrong Messages from Ineffective SQLs Refined"] = ineffective_wrong_messages
            # 3.将提取出来的effective sqls更新到feature knowledge base processed中
            with open(os.path.join(direct_dic,  filename), "w", encoding="utf-8") as w:
                json.dump(content, w, indent=4)

        print("总features文件个数:"+str(len(source_filenames)))
        print("总有效features（feature和description信息齐全）个数:"+str(effective_feature_cnt))
        print("重复的features（同义的算作一个）个数:" + str(indistinct_feature_cnt))
        print("未提取到effective sqls的feature数量:"+str(none_effective_cnt))
        print("官网未提供Example字符串的feature数量:"+str(none_example_cnt))


def sql_generator_llm(tool, db_name, temperature, model, content, max_cnt, with_table, with_examples):
    chat = ChatOpenAI(temperature=temperature, model=model)
    memory = ConversationBufferMemory()  # 内存：对话缓冲区内存
    conversation = ConversationChain(
        llm=chat,
        memory=memory,
        verbose=False  # 为true的时候是展示langchain实际在做什么
    )

    if not with_table:
        llm_string = """  
        根据下面提供的{feature}的信息，生成一句关于{feature}的{db_name} sql。\
        要求只生成一句，生成的sql语句尽可能简单。\
        除{feature}以外尽量不包含其他语法元素；生成的sql语句要尽量不依赖于数据库表和外部资源（比如文件和其他数据源）。
        下面是feature相关信息：
        feature语法:{syntax}\
        feature描述:{description}\
        feature例子:{examples}\
        Answer the following information: {format_instructions}
        """
    else:
        llm_string = """  
            根据下面提供的{feature}的信息，生成一句关于{feature}的{db_name} sql。\
            要求只生成一句，生成的sql语句尽可能简单。\
            除{feature}以外尽量不包含其他语法元素；\
            在下面已有数据表dialect_recognize_table的基础上生成一句sql语句。\
            已有数据库表如下，其建表语句为："CREATE TABLE dialect_recognize_table (\n    id INT AUTO_INCREMENT PRIMARY KEY,\n    dialect_name VARCHAR(50) NOT NULL,\n    region VARCHAR(50),\n    speaker_count INT,\n    description TEXT,\n    is_endangered BOOLEAN\n);",
            "INSERT INTO dialect_recognize_table (dialect_name, region, speaker_count, description, is_endangered) VALUES\n('Mandarin', 'China', 920000000, 'The most widely spoken dialect in the world.', FALSE),\n('Cantonese', 'China', 87000000, 'A dialect spoken in Guangdong province and Hong Kong.', TRUE),\n('Spanish', 'Spain', 46000000, 'The official language of Spain and many Latin American countries.', FALSE),\n('Scottish Gaelic', 'Scotland', 58000, 'A Celtic language native to Scotland.', TRUE),\n('Hmong', 'Southeast Asia', 4000000, 'A language spoken by the Hmong people in various countries.', TRUE);"\
        +----+-----------------+----------------+---------------+-------------------------------------------------------------------+---------------+
        | id | dialect_name    | region         | speaker_count | description                                                       | is_endangered |
        +----+-----------------+----------------+---------------+-------------------------------------------------------------------+---------------+
        |  1 | Mandarin        | China          |     920000000 | The most widely spoken dialect in the world.                      |             0 |
        |  2 | Cantonese       | China          |      87000000 | A dialect spoken in Guangdong province and Hong Kong.             |             1 |
        |  3 | Spanish         | Spain          |      46000000 | The official language of Spain and many Latin American countries. |             0 |
        |  4 | Scottish Gaelic | Scotland       |         58000 | A Celtic language native to Scotland.                             |             1 |
        |  5 | Hmong           | Southeast Asia |       4000000 | A language spoken by the Hmong people in various countries.       |             1 |
        +----+-----------------+----------------+---------------+-------------------------------------------------------------------+---------------+
            下面是feature相关信息：
            feature语法:{syntax}\
            feature描述:{description}\
            feature例子:{examples}\
            Answer the following information: {format_instructions}
            """

    response_schemas = [
        ResponseSchema(type="json", name="Example SQL", description='SQL Statements,每个语句分开单独存储')
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt_template = ChatPromptTemplate.from_template(llm_string)

    iterate_llm_string = """  
    生成的sql语句执行失败，错误原因如下，请根据错误信息修改sql并生成新的关于{feature}的{db_name}语句。
    error message:{error_message}  
    Answer the following information: {format_instructions}  
    """

    iterate_prompt_template = ChatPromptTemplate.from_template(iterate_llm_string)

    costs = []
    generate_results = []
    exec_results = []
    exec_times = []
    error_messages = []

    conversation_cnt = 0  # conversation_cnt = 0:初始第一条prompt
    # 边界1：达到最大迭代次数
    while conversation_cnt <= max_cnt:
        prompt_messages = None
        if conversation_cnt == 0:
            # 初始第一条prompt
            if with_examples:
                prompt_messages = prompt_template.format_messages(
                    db_name=db_name,
                    feature=str(content["Title"]),
                    syntax=str(content["Feature"]),
                    description=str(content["Description"]),
                    examples=str(content["Examples"]),
                    format_instructions=format_instructions
                )
            else:
                prompt_messages = prompt_template.format_messages(
                    db_name=db_name,
                    feature=str(content["Title"]),
                    syntax=str(content["Feature"]),
                    description=str(content["Description"]),
                    examples="",
                    format_instructions=format_instructions
                )
        else:
            # 边界3：判断上一次得到的transfer sql执行是否执行成功，能执行成功则break直接跳出循环，执行失败则进行下面的error信息迭代处理

            if len(error_messages) and error_messages[-1] == "None":
                break
            # error信息迭代处理：
            # 将执行的error信息返回给llm，提示llm根据error信息重新生成新的sql，反复迭代
            # 此处运用了ConversationBufferMemory()，并且规定了最高迭代次数
            # 迭代的prompt：每次取error_messages数组的最后一个元素，则为最新的报错信息
            prompt_messages = iterate_prompt_template.format_messages(
                feature=str(content["Title"]),
                db_name=db_name,
                error_message=error_messages[-1] if len(error_messages) else "",
                format_instructions=format_instructions
            )

        try:
            cost = {}
            with get_openai_callback() as cb:
                # print(prompt_messages[0].content)
                response = conversation.predict(input=prompt_messages[0].content)
                output_dict = output_parser.parse(response)
                # print(response)
                print(output_dict)
                cost["Total Tokens"] = cb.total_tokens
                cost["Prompt Tokens"] = cb.prompt_tokens
                cost["Completion Tokens"] = cb.completion_tokens
                cost["Total Cost (USD)"] = cb.total_cost  # 用了4o-mini以后变成0.0了，还没修改，也可以用户token乘单价计算

                # 2.执行提取出来的sql语句，只保留可执行的sql语句
                exec_result, exec_time, error_message = exec_sql_statement(tool, db_name, output_dict["Example SQL"])

                costs.append(cost)
                generate_results.append(output_dict)
                exec_results.append(str(exec_result))
                exec_times.append(str(exec_time))
                # 简化error_message,只留下关键部分
                if error_message:
                    error_message = error_message.split("[SQL:")[0]
                error_messages.append(str(error_message))
        except Exception as e:
            print("transfer llm:")
            print(e)

        conversation_cnt += 1

    return costs, generate_results, exec_results, exec_times, error_messages


def effective_sqls_generator(db_name, feature_type, temperature, model, max_cnt):
    # 对于提取effective sql失败的feature：利用llm为该feature生成一个简单的effective sql
    if feature_type in ["Functions", "Operators"]:
        none_effective_cnt = 0
        generate_without_table_fail_cnt = 0
        generate_with_table_fail_cnt = 0

        source_dic = os.path.join("..", "..", "Feature Knowledge Base Processed1", db_name, feature_type,
                                  feature_type + "_Results")

        source_filenames = os.listdir(source_dic)
        for filename in source_filenames:
            with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
                content = json.load(r)

            if len(content["Effective SQLs Refined"]) == 0:
                # 提取effective sql失败，需要利用llm为该feature生成简单的sql样例
                none_effective_cnt += 1
                if "Effective SQLs Generated1" in content:
                    if len(content["Effective SQLs Generated1"]):
                        # 第二轮已经成功生成effective sqls
                        continue
                """
                if "Effective SQLs Generated2" in content:
                    continue
                """
                costs, generate_results, exec_results, exec_times, error_messages = sql_generator_llm(db_name, temperature, model, content, max_cnt, False, True)
                content["SQLs Generated1"] = generate_results
                content["SQLs Generated Costs1"] = costs
                content["SQLs Generated ExecResults1"] = exec_results
                content["SQLs Generated ExecTimes1"] = exec_times
                content["SQLs Generated ErrorMessages1"] = error_messages

                if len(error_messages) and error_messages[-1] == "None":
                    # 第一轮无表格的生成成功
                    content["Effective SQLs Generated1"] = [generate_results[-1]["Example SQL"]]
                else:
                    # 最后一条记录有错误，说明第一轮未能成功生成effective sql
                    generate_without_table_fail_cnt += 1
                    content["Effective SQLs Generated1"] = []

                    # 第二轮基于表格进行生成
                    costs, generate_results, exec_results, exec_times, error_messages = sql_generator_llm(db_name,
                                                                                                          temperature,
                                                                                                          model,
                                                                                                          content,
                                                                                                          max_cnt,
                                                                                                          True, False)
                    content["SQLs Generated2"] = generate_results
                    content["SQLs Generated Costs2"] = costs
                    content["SQLs Generated ExecResults2"] = exec_results
                    content["SQLs Generated ExecTimes2"] = exec_times
                    content["SQLs Generated ErrorMessages2"] = error_messages

                    if len(error_messages) and error_messages[-1] == "None":
                        # 第二轮无表格的生成成功
                        content["Effective SQLs Generated2"] = [generate_results[-1]["Example SQL"]]
                    else:
                        # 最后一条记录有错误，说明第一轮未能成功生成effective sql
                        generate_with_table_fail_cnt += 1
                        content["Effective SQLs Generated2"] = []

            else:
                content["SQLs Generated1"] = []
                content["SQLs Generated Costs1"] = []
                content["SQLs Generated ExecResults1"] = []
                content["SQLs Generated ExecTimes1"] = []
                content["SQLs Generated ErrorMessages1"] = []
                content["Effective SQLs Generated1"] = []
                content["SQLs Generated2"] = []
                content["SQLs Generated Costs2"] = []
                content["SQLs Generated ExecResults2"] = []
                content["SQLs Generated ExecTimes2"] = []
                content["SQLs Generated ErrorMessages2"] = []
                content["Effective SQLs Generated2"] = []
            # 3.将生成的sqls更新到feature knowledge base processed中
            with open(os.path.join(source_dic, filename), "w", encoding="utf-8") as w:
                json.dump(content, w, indent=4)
        print("未提取到effective sqls的feature数量:" + str(none_effective_cnt))
        print("生成sql(无基本表)失败的feature数量:" + str(generate_without_table_fail_cnt))
        print("生成sql(有基本表)失败的feature数量:" + str(generate_with_table_fail_cnt))


def effective_sqls_generator_v2(db_name, feature_type, temperature, model, max_cnt):
    # 对于提取effective sql失败的feature：利用llm为该feature生成一个简单的effective sql
    if feature_type in ["Functions", "Operators"]:
        none_effective_cnt = 0
        generate_without_table_fail_cnt = 0
        generate_with_table_fail_cnt = 0

        source_dic = os.path.join("..", "..", "Feature Knowledge Base Processed", db_name, feature_type,
                                  feature_type + "_Results")

        source_filenames = os.listdir(source_dic)
        for filename in source_filenames:
            # effective_sqls_generator(version2)
            if filename not in effective_sqls_generator_v2_skip:
                continue

            with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
                content = json.load(r)

            if len(content["Effective SQLs Refined"]) == 0:
                # 提取effective sql失败，需要利用llm为该feature生成简单的sql样例
                none_effective_cnt += 1
                if "Effective SQLs Generated1" in content:
                    if len(content["Effective SQLs Generated1"]):
                        # 第二轮已经成功生成effective sqls
                        continue

                    # 第二轮基于表格进行生成
                    costs, generate_results, exec_results, exec_times, error_messages = sql_generator_llm(db_name,
                                                                                                          temperature,
                                                                                                          model,
                                                                                                          content,
                                                                                                          max_cnt,
                                                                                                          True, True)
                    content["SQLs Generated2"] = generate_results
                    content["SQLs Generated Costs2"] = costs
                    content["SQLs Generated ExecResults2"] = exec_results
                    content["SQLs Generated ExecTimes2"] = exec_times
                    content["SQLs Generated ErrorMessages2"] = error_messages

                    if len(error_messages) and error_messages[-1] == "None":
                        # 第二轮无表格的生成成功
                        content["Effective SQLs Generated2"] = [generate_results[-1]["Example SQL"]]
                    else:
                        # 最后一条记录有错误，说明第一轮未能成功生成effective sql
                        generate_with_table_fail_cnt += 1
                        content["Effective SQLs Generated2"] = []

            else:
                content["SQLs Generated1"] = []
                content["SQLs Generated Costs1"] = []
                content["SQLs Generated ExecResults1"] = []
                content["SQLs Generated ExecTimes1"] = []
                content["SQLs Generated ErrorMessages1"] = []
                content["Effective SQLs Generated1"] = []
                content["SQLs Generated2"] = []
                content["SQLs Generated Costs2"] = []
                content["SQLs Generated ExecResults2"] = []
                content["SQLs Generated ExecTimes2"] = []
                content["SQLs Generated ErrorMessages2"] = []
                content["Effective SQLs Generated2"] = []
            # 3.将生成的sqls更新到feature knowledge base processed中
            with open(os.path.join(source_dic, filename), "w", encoding="utf-8") as w:
                json.dump(content, w, indent=4)
        print("未提取到effective sqls的feature数量:" + str(none_effective_cnt))
        print("生成sql(无基本表)失败的feature数量:" + str(generate_without_table_fail_cnt))
        print("生成sql(有基本表)失败的feature数量:" + str(generate_with_table_fail_cnt))


def mariadb_knowledge_base_processing(db_name, feature_type):
    effective_sqls_refiner(db_name, feature_type)
    effective_sqls_generator(db_name, feature_type, 0.3, "gpt-4o-mini", 4)


def feature_knowledge_base_preprocessing(db_name, feature_type):
    # 对feature knowledge base中的数据进行预处理
    if db_name == "MariaDB":
        mariadb_knowledge_base_processing(db_name, feature_type)


def potential_dialect_features_process_and_map(tool, a_db, b_db, source_filename, dir_filename, knowledge_base_dic, feature_types, search_k=0, version_id=1):
    """
    遍历a_db上origin_sql的所有potential features(functions+operators)，对每一个feature进行以下操作。
    * 在a_db的feature knowledge base processed中检索到该feature
    * 若未检索到该feature，先认为该feature为方言；若检索到该feature，选出最短的一个example sql作为方言检测example sql。
    * 在b_db引擎上执行该方言检测example sql，若无法执行则认为是dialect（虽然其中可能包括由于example sql中其他feature造成的无法执行，这里暂且粗略认为是方言）。
    * 统计：针对a_db的所有测试语句，potential dialect features/总features个数
    :return:
    """
    # 获取knowledge base的functions和operators的dic:Title及对应的json文件名
    features_dictionary = {}
    features_total_cnt = 0
    features_searched_fail_cnt = 0
    dialect_features_cnt = 0
    not_dialect_features_cnt = 0

    # 获取a_db的feature的详细信息，为了获取其examples供执行
    names = "merge"
    for feature_type in feature_types:
        names = names + "_" + feature_type
    a_merge_feature_filename = os.path.join("..", "..", "Feature Knowledge Base Processed1", a_db, "RAG_Embedding_Data", names + ".jsonl")
    with open(a_merge_feature_filename, "r", encoding="utf-8") as r:
        a_merge_features = r.readlines()

    # 获取a_db -> b_db的预先搭建好的mapping结果
    features_mapping_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_types[0], a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + "_processed" + ".jsonl")
    with open(features_mapping_filename, "r", encoding="utf-8") as r:
        mapping_info = r.readlines()

    # 获取测试文件的数据内容
    if os.path.exists(dir_filename):
        with open(dir_filename, "r", encoding="utf-8") as r:
            contents = r.readlines()
        with open(dir_filename, 'w'):
            pass
    else:
        with open(source_filename, "r", encoding="utf-8") as r:
            contents = json.load(r)

    results = []
    not_dialects = []
    for content in contents:
        if type(content) != dict:
            content = json.loads(content)
        potential_dialect = []
        not_potential_dialect = []
        potential_dialect_mapping_index = []  #存储potential dialect map的feature
        lists = tokenize_sql(content["Sql"])
        if feature_types[0] == "Functions":
            feature_indexes = content["SqlPotentialFunctionIndexes"]  # potential functions的分词的下标
        elif feature_types[0] == "Operators":
            feature_indexes = content["SqlPotentialOperatorIndexes"]  # potential functions的分词的下标
        else:
            feature_indexes = []
        features_total_cnt += len(feature_indexes)

        # 处理potential features
        for index in feature_indexes:
            feature_name = str(lists[index].text)
            feature_searched_index = None
            # 在a_db的feature knowledge base processed中检索到该feature
            for line in a_merge_features:
                a_feature = json.loads(line)
                a_feature_Feature = ""
                for item in a_feature["Feature"]:
                    a_feature_Feature += item
                if str(feature_name).lower().strip() in a_feature_Feature.split("(")[0].lower().strip():
                    feature_searched_index = a_feature["index"]
                    break
            # 若未检索到该feature，先认为该feature为方言；若检索到该feature，选出最短的一个example sql作为方言检测example sql。
            if feature_searched_index:
                # 成功检索到，获取该feature的example信息
                feature_searched_content = json.loads(a_merge_features[feature_searched_index])
                # 选择最短的sql作为方言检测sql
                effective_sqls = feature_searched_content["Examples"]
                if len(effective_sqls):
                    dialect_recognize_sql = min(effective_sqls, key=len)
                    # 在b_db引擎上执行该方言检测example sql，若无法执行则认为是dialect（虽然其中可能包括由于example sql中其他feature造成的无法执行，这里暂且粗略认为是方言）。
                    exec_result, exec_time, error_message = exec_sql_statement(tool, b_db, dialect_recognize_sql)


                    if exec_result == None:
                        # 说明无法执行
                        dialect_features_cnt += 1
                        potential_dialect.append(feature_name)
                        # 为方言添加对应的mapping index
                        print(feature_searched_content)
                        potential_dialect_mapping_index.append([feature_searched_index, json.loads(mapping_info[feature_searched_index])["b_db"]["index"]])
                        print(json.loads(mapping_info[feature_searched_index]))
                    else:
                        not_dialect_features_cnt += 1
                        not_potential_dialect.append(feature_name)
                else:
                    dialect_features_cnt += 1
            else:
                # 未成功检索到
                features_searched_fail_cnt += 1
                dialect_features_cnt += 1

        if feature_types[0] == "Functions":
            content["SqlPotentialDialectFunction"] = potential_dialect
            content["SqlNotDialectFunction"] = not_potential_dialect
            content["SqlPotentialDialectFunctionMapping"] = potential_dialect_mapping_index
        elif feature_types[0] == "Operators":
            content["SqlPotentialDialectOperator"] = potential_dialect
            content["SqlNotDialectOperator"] = not_potential_dialect
            content["SqlPotentialDialectOperatorMapping"] = potential_dialect_mapping_index
        else:
            pass

        not_dialects += not_potential_dialect

        results.append(content)
        # 存储
        with open(dir_filename, "a", encoding="utf-8") as a:
            json.dump(content, a)
            a.write('\n')


    """
    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(results, w, indent=4)
    """

    print("feature总个数"+str(features_total_cnt))
    print("feature在knowledge base中检索失败的个数"+str(features_searched_fail_cnt))
    print("feature中方言的个数"+str(dialect_features_cnt))
    print("feature中非方言的个数" + str(not_dialect_features_cnt))

    print(not_dialects)



def sqlancer_potential_dialect_features_process_and_map(a_db, b_db, potential_dialect, feature_type, search_k=0, version_id=1):
    """
    遍历a_db上origin_sql的所有potential features(functions+operators)，对每一个feature(全部认为是方言)进行以下操作。
    * 在a_db的feature knowledge base中检索到该feature
    * 获取mapping结果并返回
    :return:
    """
    potential_dialect_mapping_index = []  # 存储potential dialect map的feature
    # 获取a_db -> b_db的预先搭建好的mapping结果
    features_mapping_filename = os.path.join("..", "..", "RAG_Feature_Mapping", a_db, feature_type, a_db + "_mapping_" + b_db + "_k" + str(search_k) + "_" + str(version_id) + "_processed" + ".jsonl")
    if not os.path.exists(features_mapping_filename):
        return potential_dialect_mapping_index
    with open(features_mapping_filename, "r", encoding="utf-8") as r:
        mapping_info = r.readlines()

    # 处理potential features，获取potential dialect features和mapping结果

    for dialect in potential_dialect:
        map_searched_index = None
        # 在a_db -> b_db的预先搭建好的mapping结果中进行检索
        for info in mapping_info:
            map = json.loads(info)
            a_feature_Feature = ""
            for item in map["a_db"]["Feature"]:
                a_feature_Feature += item
            dialect_str = str(dialect).lower().strip()
            a_feature_str = a_feature_Feature.split("(")[0].lower().strip()
            if a_feature_str.startswith(dialect_str+"("):
                # 为方言添加对应的mapping index
                potential_dialect_mapping_index.append([map["a_db"]["index"],map["b_db"]["index"]])
                break
    return potential_dialect_mapping_index


def potential_dialect_features_recognizer(a_db, b_db, source_filename, dir_filename, knowledge_base_dic, search_k=0,version_id=1):
    potential_dialect_features_process_and_map(a_db, b_db, source_filename, dir_filename, knowledge_base_dic, ["Functions"], search_k=0,version_id=1)
    potential_dialect_features_process_and_map(a_db, b_db, source_filename, dir_filename, knowledge_base_dic,["Operators"], search_k=0, version_id=1)

