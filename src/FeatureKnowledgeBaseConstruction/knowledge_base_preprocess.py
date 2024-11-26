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
import copy
from src.Tools.DatabaseConnect.database_connector import exec_sql_statement, run_with_timeout, database_clear
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.chains import ConversationChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from src.DialectRecognition.TokenType_not_op import TokenType_not_op
from src.Tools.DatabaseConnect.database_connector import get_database_connector_args
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
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

def effective_sqls_refiner(tool, exp, dbType, featureType):
    if featureType.lower() not in ["function", "operator","datatype"]:
        return
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    # 从feature的Examples字符串中提取出可执行的sql语句
    effective_feature_cnt = 0  # 记录有效的feature个数，即文件中的description和feature语法部分不为空
    indistinct_feature_cnt = 0  # 记录唯一的feature个数
    none_effective_cnt = 0  # 未提取到effective sql的feature数量
    none_example_cnt = 0  # 官网未提供Example字符串的feature数量

    source_dic = os.path.join(current_dir, "..", "..", "FeatureKnowledgeBase", dbType.lower(), featureType, "results")
    source_filenames = os.listdir(source_dic)

    # 遍历Functions_Results内的所有结果文件，预处理单个feature内所有Examples语句，将结果存到Feature Knowledge Base Processed文件夹
    # 1.提取examples字符串中的sql语句(正则表达式匹配)
    # 2.执行提取出来的sql语句，只保留可执行的sql语句
    # 3.将提取出来的effective sqls更新到feature knowledge base processed中

    # 正则表达式模式，用于匹配 SQL 语句
    sql_pattern = r'(?i)(SELECT.*?;|SET.*?;|INSERT.*?;|UPDATE.*?;|DELETE.*?;|CREATE.*?;|DROP.*?;|ALTER.*?;|TRUNCATE.*?;|MERGE.*?;|CALL|EXEC.*?;)'
    # pattern = r'(?i)(SELECT.*?;|INSERT.*?;|UPDATE.*?;|DELETE.*?;|CREATE.*?;|DROP.*?;|ALTER.*?;|TRUNCATE.*?;|MERGE.*?;|CALL|EXEC.*?;|SELECT.*?\n|INSERT.*?\n|UPDATE.*?\n|DELETE.*?\n|CREATE.*?\n|DROP.*?\n|ALTER.*?\n|TRUNCATE.*?\n|MERGE.*?\n|CALL|EXEC.*?\n)'

    for filename in source_filenames:
        effective_sqls = []  # 存储提取过程中的effective sqls：执行成功
        ineffective_sqls = []  # 存储提取过程中的ineffective sqls：执行失败
        ineffective_wrong_messages = []  # 存储提取过程中的ineffective sqls的执行失败原因
        with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
            content = json.load(r)
        if "EffectiveSQLsRefined" in content:
            print(filename + " has been refined.")
            continue
        # clear the database
        database_clear(tool, exp, dbType)
        # 对于description和feature都为空的feature，跳过，不包含
        if len(content["Feature"]) == 0 and len(content["Description"]) != 0:
            effective_feature_cnt += 1
        if len(content["Examples"]) == 0: none_example_cnt += 1

        # 提取Examples字符串中的sql语句
        for examples in content["Examples"]:
            # 1.提取examples字符串中的sql语句(正则表达式匹配)
            matches = re.findall(sql_pattern, examples, re.DOTALL)
            for match in matches:
                # 2.执行提取出来的sql语句，只保留可执行的sql语句
                print(filename + " " + match)
                try:
                    exec_result, _, exec_error_message = run_with_timeout(exec_sql_statement, 17, "knowledge_base", "preprocess", dbType, match.strip())
                except TimeoutError as e:
                    exec_result, _, exec_error_message = None, None, "error"
                    print(e)
                if not exec_error_message:
                    effective_sqls.append(match.strip())
                else:
                    ineffective_sqls.append(match.strip())
                    ineffective_wrong_messages.append(exec_error_message)
        if len(effective_sqls) == 0:
            # 说明该feature没有提取出任何一个有效的sql
            none_effective_cnt += 1
        content["EffectiveSQLsRefined"] = effective_sqls
        # 3.将提取出来的effective sqls更新到feature knowledge base processed中
        with open(os.path.join(source_dic, filename), "w", encoding="utf-8") as w:
            json.dump(content, w, indent=4)

    print("总features文件个数:" + str(len(source_filenames)))
    print("总有效features（feature和description信息齐全）个数:" + str(effective_feature_cnt))
    print("重复的features（同义的算作一个）个数:" + str(indistinct_feature_cnt))
    print("未提取到effective sqls的feature数量:" + str(none_effective_cnt))
    print("官网未提供Example字符串的feature数量:" + str(none_example_cnt))


def sql_generator_llm(tool, exp, dbType, temperature, model, content, max_cnt, with_table, with_examples):
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
                    db_name=dbType,
                    feature=str(content["Title"]),
                    syntax=str(content["Feature"]),
                    description=str(content["Description"]),
                    examples=str(content["Examples"]),
                    format_instructions=format_instructions
                )
            else:
                prompt_messages = prompt_template.format_messages(
                    db_name=dbType,
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
                db_name=dbType,
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
                exec_result, exec_time, error_message = exec_sql_statement(tool, exp, dbType, output_dict["Example SQL"])
                costs.append(cost)
                generate_results.append(output_dict["Example SQL"])
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


def effective_sqls_generator(tool, exp, dbType, featureType, temperature, model, max_cnt):
    if featureType.lower() not in ["function", "operator","datatype"]:
        return
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    # 对于提取effective sql失败的feature：利用llm为该feature生成一个简单的effective sql
    none_effective_cnt = 0
    generate_without_table_fail_cnt = 0
    generate_with_table_fail_cnt = 0
    source_dic = os.path.join(current_dir, "..", "..", "FeatureKnowledgeBase", dbType.lower(), featureType, "results")
    source_filenames = os.listdir(source_dic)

    for filename in source_filenames:
        print(filename)
        with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
            content = json.load(r)
        if len(content["EffectiveSQLsRefined"]) == 0:
            # 提取effective sql失败，需要利用llm为该feature生成简单的sql样例
            none_effective_cnt += 1
            if "EffectiveSQLsGenerated" in content and "EffectiveSQLsGeneratedCosts" in content and len(content["EffectiveSQLsGenerated"]):
                print(filename + " has generated effective sqls.")
                continue
            database_clear(tool, exp, dbType)
            costs, generate_results, exec_results, exec_times, error_messages = sql_generator_llm(tool, exp, dbType, temperature,
                                                                                                  model, content,
                                                                                                  max_cnt, False, False)
            content["EffectiveSQLsGenerated"] = generate_results
            content["EffectiveSQLsGeneratedCosts"] = costs
            content["EffectiveSQLsGeneratedErrors"] = error_messages
        else:
            content["EffectiveSQLsGenerated"] = []
            content["EffectiveSQLsGeneratedCosts"] = []
            content["EffectiveSQLsGeneratedErrors"] = []
            # 3.将生成的sqls更新到feature knowledge base processed中
        with open(os.path.join(source_dic, filename), "w", encoding="utf-8") as w:
            json.dump(content, w, indent=4)
    print("未提取到effective sqls的feature数量:" + str(none_effective_cnt))
    print("生成sql(无基本表)失败的feature数量:" + str(generate_without_table_fail_cnt))
    print("生成sql(有基本表)失败的feature数量:" + str(generate_with_table_fail_cnt))

def merge_effective_sqls(tool, exp, dbType, featureType):
    if featureType.lower() not in ["function", "operator","datatype"]:
        return
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    source_dic = os.path.join(current_dir, "..", "..", "FeatureKnowledgeBase", dbType.lower(), featureType, "results")
    source_filenames = os.listdir(source_dic)
    none_effective_cnt = 0  # 未提取到effective sql的feature数量
    for filename in source_filenames:
        with open(os.path.join(source_dic, filename), "r", encoding="utf-8") as r:
            content = json.load(r)
        content["EffectiveSQLs"] = copy.deepcopy(content["EffectiveSQLsRefined"])
        if len(content["EffectiveSQLsGeneratedErrors"]) and content["EffectiveSQLsGeneratedErrors"][-1] == "None":
            content["EffectiveSQLs"].append(content["EffectiveSQLsGenerated"][-1])
        with open(os.path.join(source_dic, filename), "w", encoding="utf-8") as w:
            json.dump(content, w, indent=4)

        if not len(content["EffectiveSQLs"]):
            none_effective_cnt += 1

    print("总features文件个数:" + str(len(source_filenames)))
    print("未提取/生成到effective sqls的feature数量:" + str(none_effective_cnt))

def knowledge_base_processing(tool, exp, dbType, featureType):
    effective_sqls_refiner(tool, exp, dbType, featureType)
    effective_sqls_generator(tool, exp, dbType, featureType,0.3, "gpt-4o-mini", 4)
    merge_effective_sqls(tool, exp, dbType, featureType)

