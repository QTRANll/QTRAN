# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/2 21:25
# @Author  : shaocanfan
# @File    : FineTuning_DatasetEstablish.py
# @Intro   : 构造微调mutate llm的训练集

import os
import json
from src.Connector import test_database_mysql_like,test_database_postgres
import tiktoken # for token counting
import numpy as np
from collections import defaultdict
import openai
import random
import re
from src.TransferLLM.TransferLLM import transfer_llm
from langchain.chat_models import ChatOpenAI






os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
os.environ["OPENAI_API_KEY"] = ""  # app5
os.environ["OPENAI_API_BASE"] = ""  # "https://ai-yyds.com/v1"
openai.api_key = os.environ['OPENAI_API_KEY']
openai.api_base = os.environ['OPENAI_API_BASE']


encoding = tiktoken.get_encoding("cl100k_base")
db_names = ["mariadb", "mysql", "tidb"]

database_connection_args = {
    "mysql": {
        "db_type": "mysql",
        "host": "127.0.0.1",
        "port": 13306,
        "username": "root",
        "password": "123456",
        "dbname": "TEST"
    },
    "mariadb": {
        "db_type": "mariadb",
        "host": "127.0.0.1",
        "port": 9901,
        "username": "root",
        "password": "123456",
        "dbname": "TEST"
    },
    "MySQL": {
        "db_type": "mysql",
        "host": "127.0.0.1",
        "port": 13306,
        "username": "root",
        "password": "123456",
        "dbname": "TEST"
    },
    "MariaDB": {
        "db_type": "mariadb",
        "host": "127.0.0.1",
        "port": 9901,
        "username": "root",
        "password": "123456",
        "dbname": "TEST"
    },
    "postgres": {
        "db_type": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
        "username": "postgres",
        "password": "123456",
        "dbname": "test2"
    }
}
mutate_strategy_names = [
    "FixMDistinctU",
    "FixMDistinctL",
    "FixMCmpOpU",
    "FixMCmpOpL",
    "FixMUnionAllU",
    "FixMUnionAllL",
    "FixMInNullU",
    "FixMWhere1U",
    "FixMWhere0L",
    "FixMHaving1U",
    "FixMHaving0L",
    "FixMOn1U",
    "FixMOn0L",
    "FixMRmUnionAllL",
    "RdMLikeU",
    "RdMLikeL",
    "RdMRegExpU",
    "RdMRegExpL"
]

# 加载output_name文件夹中db_name的，"originalSqlsimlength"长度在[len_low,len_high）范围的，变异类型为mutation_name的，包含text的完整sample信息
#
def load_fine_tuning_dataset(output_name, db_name, len_low, len_high, mutation_name , text):
    dic_name = os.path.join("..\..\Dataset\Pinolo Output", output_name, db_name+"_merged")
    target_dic_name = os.path.join("../../Dataset/FineTuning/Pinolo FineTuning/TrainingTestingDatasetCandidate")  # 结果文件的目标文件夹
    sub_dic_names = os.listdir(dic_name)

    fine_tuning_dataset = {}
    fine_tuning_dataset_word = {}
    mutate_names=[]
    # 为18种mutate strategies初始化存储结果的列表
    for name in mutate_strategy_names:
        fine_tuning_dataset[name] = []
        fine_tuning_dataset_word[name] = []
    for sub_dic in sub_dic_names:
        if ".json" in sub_dic:
            continue
        filename = os.path.join(dic_name, sub_dic, sub_dic + "_bugs_sqlsim.json")
        # 获取task-id内json文件的内容
        with open(filename, "r", encoding="utf-8") as rf:
            contents = json.load(rf)
        for key, value in contents.items():
            if value["mutationName"] not in mutate_names:
                mutate_names.append(value["mutationName"])
            # 满足变异类型
            if mutation_name != "AllMutation" and mutation_name != value["mutationName"]:
                continue

            # 满足长度要求
            if len_low <= value["originalSqlsimlength"] < len_high:
                if text in value["originalSqlsim"] and text != "":
                    fine_tuning_dataset_word[value["mutationName"]].append(value)
                    print(value)
                # 名称在18种的范围内
                if value["mutationName"] in mutate_strategy_names:
                    fine_tuning_dataset[value["mutationName"]].append(value)

    with open(os.path.join(target_dic_name, output_name+"_"+db_name+"_"+str(len_low)+"_"+str(len_high)+"_"+ mutation_name +"_"+"FineTuningDatasetCandidate.json"), 'w', encoding='utf-8') as f:
        json.dump(fine_tuning_dataset, f, indent=4)
    if text != "":
        with open(os.path.join(target_dic_name, output_name+"_"+db_name+"_"+str(len_low)+"_"+str(len_high)+"_"+text+"_"+"FineTuningDatasetCandidate.json"), 'w', encoding='utf-8') as f:
            json.dump(fine_tuning_dataset_word, f, indent=4)

    # 统计获取到底数据量
    for key, value in fine_tuning_dataset.items():
        if len(value) != 0:
            print(key+":"+str(len(value)))
    print(len(mutate_names))
    print('-------------------------')
    return fine_tuning_dataset

# 执行训练集的sql语句，验证语句的正确性
def exec_dataset_sqls(dataset_filename, db_name, sql_keys):
    with open(dataset_filename, "r", encoding="utf-8") as f:
        contents = json.load(f)

    cnt_error = 0
    cnt = 0
    mutated_error_cnt = 0
    errors = []
    for key, value in contents.items():
        for item in value:
            if "index" in item:
                print(item["index"])
            print(item["bugId"])
            print(item["sqlId"])
            print(item["mutationName"])
            print(item["isUpper"])

            origin_exec_args = database_connection_args[db_name]
            for key in sql_keys:
                if db_name in ["mariadb", "mysql", "tidb"]:
                    statement = item[key]
                    exec_result, exec_time, error_message = test_database_mysql_like(
                        origin_exec_args["db_type"],
                        origin_exec_args["host"],
                        origin_exec_args["port"],
                        origin_exec_args["username"],
                        origin_exec_args["password"],
                        origin_exec_args["dbname"],
                        statement)
                elif db_name == "postgres":
                    if isinstance(item[key],str):
                        statement = item[key]
                    elif isinstance(item[key],dict):
                        statement = item[key]["mutated sql"]
                    exec_result, exec_time, error_message = test_database_postgres(
                        origin_exec_args["db_type"],
                        origin_exec_args["host"],
                        origin_exec_args["port"],
                        origin_exec_args["username"],
                        origin_exec_args["password"],
                        origin_exec_args["dbname"],
                        statement)

                cnt += 1
                if error_message == None:
                    print(key +":"+ str(exec_result))
                else:
                    cnt_error += 1
                    print(key+":" + str(exec_result))
                    print(key+":" + str(error_message))
                    errors.append(str(item["bugId"])+","+str(item["sqlId"])+","+str(item["mutationName"])+":"+str(error_message))
            print('--------------------------------------------')

    print("总执行语句个数："+str(cnt))
    print("执行失败语句个数："+str(cnt_error))
    print("错误信息："+str(errors))
    print(mutated_error_cnt)


def load_training_raw():
    with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset_raw1.0.jsonl", "r", encoding="utf-8") as f:
        contents_raw = json.load(f)

    with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset1.0.jsonl", "r", encoding="utf-8") as f:
        contents = json.load(f)

    for key, value in contents_raw.items():
        value_new = contents[key]
        for item in value:
            if key == "FixMDistinctU":
                item["originalSqlsim_modified"] = item["mutatedSqlsim"]
                item["mutatedSqlsim_modified"] = item["originalSqlsim"]
            else:
                item["originalSqlsim_modified"] = item["originalSqlsim"]
                item["mutatedSqlsim_modified"] = item["mutatedSqlsim"]


    with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset1.0.jsonl", "w", encoding="utf-8") as f:
        json.dump(contents_raw,f,indent=4)


# 构造标准对话格式的训练数据集并返回
def data_json_establish(db_name, strategies_illustration_filename, dataset_filename,dir_filename,user_key,assistant_key):
    """
    {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
    {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
    {"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}
    """

    # 加载mutate strategies illustration
    with open(strategies_illustration_filename, "r", encoding="utf-8") as r:
        mutate_strategy_illustration = json.load(r)

    # 加载training dataset的sql和mutated sql语句
    with open(dataset_filename, "r",encoding="utf-8") as rf:
        sqls = json.load(rf)

    # 角色信息中包含db类型信息
    role_prompt = "You are an expert in " + db_name + " statement mutation."
    # 遍历数据并形成最终的training dataset
    for key, value in sqls.items():
        for item in value:
            single_train_data = {
                "messages": [
                    {"role": "system", "content": str(role_prompt+mutate_strategy_illustration[key])},
                    {"role": "user", "content": str(item[user_key])},
                    {"role": "assistant", "content": str(item[assistant_key])}
                ]
            }
            with open(dir_filename, "a") as wf:
                json.dump(single_train_data, wf)
                wf.write("\n")


# 构造eval标准对话格式的测试数据集
def eval_data_json_establish(db_name, strategies_illustration_filename, dataset_filename,dir_filename, user_key, assistant_key):
    """
    {"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "Once upon a "}], "ideal": "time"}
    {"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "The first US president was "}], "ideal": "George Washington"}
    {"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "OpenAI was founded in 20"}], "ideal": "15"}
    """

    # 要使用后续的eval模板，需要将单条sample设置为dict类型，将"ideal"设置为list格式
    # eval的测试数据集（key="mutatedSqlsim_postgres"）和微调时上传的测试数据集（key="mutatedSqlsim_postgres_training"）不一样，eval的测试数据集每条sample的标准答案只有一条

    # 加载mutate strategies illustration
    with open(strategies_illustration_filename, "r", encoding="utf-8") as r:
        mutate_strategy_illustration = json.load(r)

    # 加载dataset的sql和mutated sql语句
    with open(dataset_filename, "r",encoding="utf-8") as rf:
        sqls = json.load(rf)

    # 角色信息中包含db类型信息
    role_prompt = "You are an expert in " + db_name + " statement mutation."
    # 遍历数据并形成最终的training dataset
    for key, value in sqls.items():
        for item in value:
            if assistant_key == "mutatedSqlsim":
                assistant_content = [{
                    "mutated sql": item[assistant_key],
                    "flag": item["mutatedSqlsim_postgres"]["flag"]
                }]
            else:
                assistant_content = [item[assistant_key]]
            single_eval_data = {
                "input": [
                    {"role": "system", "content": str(role_prompt + mutate_strategy_illustration[key])},
                    {"role": "user", "content": str(item[user_key])}
                ],
                "ideal": assistant_content
            }

            with open(dir_filename, "a") as wf:
                json.dump(single_eval_data, wf)
                wf.write("\n")



# 构造eval标准对话格式的fewshot数据集
def eval_fewshot_data_json_establish(shot_num, db_name, strategies_illustration_filename, dataset_filename,dir_filename, user_key,assistant_key):
    """
    {
       "input": [
         {"role": "system", "content": "Answer the following questions as concisely as possible."},
         {"role": "system", "content": "What's the capital of France?", "name": "example_user"},
         {"role": "system", "content": "Paris", "name": "example_assistant"},
         {"role": "system", "content": "What's 2+2?", "name": "example_user"},
         {"role": "system", "content": "4", "name": "example_assistant"},
         {"role": "user", "content": "Who is the girl who plays eleven in stranger things?"}
       ],
       "ideal": ["Millie Bobby Brown"]
    }
    """

    # 加载mutate strategies illustration
    with open(strategies_illustration_filename, "r", encoding="utf-8") as r:
        mutate_strategy_illustration = json.load(r)

    # 加载dataset的sql和mutated sql语句
    with open(dataset_filename, "r",encoding="utf-8") as rf:
        sqls = json.load(rf)

    # 角色信息中包含db类型信息
    role_prompt = "You are an expert in " + db_name + " statement mutation."
    # 遍历数据并形成最终的training dataset
    for key, value in sqls.items():
        cnt = 0
        for item in value:
            if cnt >= shot_num:
                break
            single_eval_data = {
                "sample": [
                    {"role": "system", "content": str(item[user_key]), "name": "example_user"},
                    {"role": "system", "content": str(item[assistant_key]), "name": "example_assistant"}
                ]
            }

            with open(dir_filename, "a") as wf:
                json.dump(single_eval_data, wf)
                wf.write("\n")
            cnt += 1




# not exact!
# simplified from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
# Token Counting Utilities
def num_tokens_from_messages(messages, tokens_per_message=3, tokens_per_name=1):
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens

# Token Counting Utilities
def num_assistant_tokens_from_messages(messages):
    num_tokens = 0
    for message in messages:
        if message["role"] == "assistant":
            num_tokens += len(encoding.encode(message["content"]))
    return num_tokens

# Token Counting Utilities
def print_distribution(values, name):
    print(f"\n#### Distribution of {name}:")
    print(f"min / max: {min(values)}, {max(values)}")
    print(f"mean / median: {np.mean(values)}, {np.median(values)}")
    print(f"p5 / p95: {np.quantile(values, 0.1)}, {np.quantile(values, 0.9)}")

def data_formatting_check_and_cost_estimation(training_data_path):
    # Load the dataset
    with open(training_data_path, 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f]

    # Initial dataset stats
    print("Num examples:", len(dataset))
    print("First example:")
    for message in dataset[0]["messages"]:
        print(message)

    # Format error checks
    format_errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            format_errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            format_errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                format_errors["message_missing_key"] += 1

            if any(k not in ("role", "content", "name", "function_call", "weight") for k in message):
                format_errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in ("system", "user", "assistant", "function"):
                format_errors["unrecognized_role"] += 1

            content = message.get("content", None)
            function_call = message.get("function_call", None)

            if (not content and not function_call) or not isinstance(content, str):
                format_errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            format_errors["example_missing_assistant_message"] += 1

    if format_errors:
        print("Found errors:")
        for k, v in format_errors.items():
            print(f"{k}: {v}")
    else:
        print("No errors found")

    # Data Warnings and Token Counts
    n_missing_system = 0
    n_missing_user = 0
    n_messages = []
    convo_lens = []
    assistant_message_lens = []

    for ex in dataset:
        messages = ex["messages"]
        if not any(message["role"] == "system" for message in messages):
            n_missing_system += 1
        if not any(message["role"] == "user" for message in messages):
            n_missing_user += 1
        n_messages.append(len(messages))
        convo_lens.append(num_tokens_from_messages(messages))
        assistant_message_lens.append(num_assistant_tokens_from_messages(messages))

    print("Num examples missing system message:", n_missing_system)
    print("Num examples missing user message:", n_missing_user)
    print_distribution(n_messages, "num_messages_per_example")
    print_distribution(convo_lens, "num_total_tokens_per_example")
    print_distribution(assistant_message_lens, "num_assistant_tokens_per_example")
    n_too_long = sum(l > 16385 for l in convo_lens)
    print(f"\n{n_too_long} examples may be over the 16,385 token limit, they will be truncated during fine-tuning")


    # Cost Estimation:Pricing and default n_epochs estimate
    MAX_TOKENS_PER_EXAMPLE = 16385

    TARGET_EPOCHS = 3
    MIN_TARGET_EXAMPLES = 100
    MAX_TARGET_EXAMPLES = 25000
    MIN_DEFAULT_EPOCHS = 1
    MAX_DEFAULT_EPOCHS = 25

    n_epochs = TARGET_EPOCHS
    n_train_examples = len(dataset)
    if n_train_examples * TARGET_EPOCHS < MIN_TARGET_EXAMPLES:
        n_epochs = min(MAX_DEFAULT_EPOCHS, MIN_TARGET_EXAMPLES // n_train_examples)
    elif n_train_examples * TARGET_EPOCHS > MAX_TARGET_EXAMPLES:
        n_epochs = max(MIN_DEFAULT_EPOCHS, MAX_TARGET_EXAMPLES // n_train_examples)

    n_billing_tokens_in_dataset = sum(min(MAX_TOKENS_PER_EXAMPLE, length) for length in convo_lens)
    print(f"Dataset has ~{n_billing_tokens_in_dataset} tokens that will be charged for during training")
    print(f"By default, you'll train for {n_epochs} epochs on this dataset")
    print(f"By default, you'll be charged for ~{n_epochs * n_billing_tokens_in_dataset} tokens")



def train_test_data_raw_load(strategies, output_name, db_name, len_low, len_high):
    # 从output_name文件夹中获取db_name的随机原始数据，涉及到的策略包括strategies，每个strategy获取的sample数量为sanmple_num
    dic_name = os.path.join("..\..\Dataset\Pinolo Output", output_name, db_name+"_merged")
    sub_dic_names = os.listdir(dic_name)

    fine_tuning_dataset = {}
    # 为18种mutate strategies初始化存储结果的列表
    for name in mutate_strategy_names:
        fine_tuning_dataset[name] = []
    for sub_dic in sub_dic_names:
        if ".json" in sub_dic:
            continue
        filename = os.path.join(dic_name, sub_dic, sub_dic + "_bugs_sqlsim.json")
        # 获取task-id内json文件的内容
        with open(filename, "r", encoding="utf-8") as rf:
            contents = json.load(rf)
        for key, value in contents.items():
            # 满足长度要求
            if len_low <= value["originalSqlsimlength"] < len_high:
                # 名称在18种的范围内
                if value["mutationName"] in strategies:
                    fine_tuning_dataset[value["mutationName"]].append(value)

    return fine_tuning_dataset

def train_test_data_raw_establish(strategies, db_name, sample_num, len_low, len_high):
    data_load_1 = train_test_data_raw_load(strategies, "output1", db_name, len_low, len_high)
    data_load_2 = train_test_data_raw_load(strategies, "output2", db_name, len_low, len_high)
    data_load_3 = train_test_data_raw_load(strategies, "output3", db_name, len_low, len_high)
    data_load_4 = train_test_data_raw_load(strategies, "output4", db_name, len_low, len_high)
    data_load = {}
    for name in mutate_strategy_names:
        data_load[name] = data_load_1[name] + data_load_2[name] + data_load_3[name] + data_load_4[name]


    raw_data = {}
    for key, value in data_load.items():
        # 不在指定strategies范围内则跳过
        if key not in strategies:
            raw_data[key] = []
            continue

        # 全选
        if key in ["FixMCmpOpL","FixMInNullU","FixMWhere1U","FixMWhere0L"]:
            raw_data[key] = value
            continue
        # 随机加载：从指定长度区间中随机选择num条数据并返回
        raw_value = []
        if len(value) < sample_num:
            # [len_low,len_high)的数量小于要提取的数目num
            print(key+":个数不足"+str(sample_num)+"个")
            raw_value = value
            # 缺少的个数 = sample_num - len(value)
            needed_num = sample_num - len(value)
            if key == "FixMDistinctU":
                substitute_key = "FixMDistinctL"
            elif key == "FixMCmpOpL":
                substitute_key = "FixMCmpOpU"
            elif key == "FixMWhere0L":
                substitute_key = "FixMWhere1U"
            elif key == "FixMHaving0L":
                substitute_key = "FixMHaving1U"
            elif key == "FixMOn0L":
                substitute_key = "FixMOn1U"

            random_numbers = random.sample(range(0, len(data_load[substitute_key])), needed_num)
            for number in random_numbers:
                raw_value.append(data_load[substitute_key][number])
        else:
            random_numbers = random.sample(range(0, len(value)), sample_num)
            for number in random_numbers:
                raw_value.append(value[number])

        raw_data[key] = raw_value

    # 分割为一半训练集，一半测试集
    training_raw_data = {}
    testing_raw_data = {}
    for key, value in raw_data.items():
        if len(value) < sample_num/2:
            training_raw_data[key] = value
            testing_raw_data[key] = []
        else:
            end_index = int(sample_num/2)
            training_raw_data[key] = value[:end_index]
            testing_raw_data[key] = value[end_index:]

    train_target_dic_name = os.path.join("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset")  # 结果文件的目标文件夹
    test_target_dic_name = os.path.join("../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset")  # 结果文件的目标文件夹
    with open(os.path.join(train_target_dic_name,db_name+"_"+"training_dataset_raw2.0"+".jsonl"),"w",encoding="utf-8") as w:
        json.dump(training_raw_data,w,indent=4)
    with open(os.path.join(test_target_dic_name,db_name+"_"+"testing_dataset_raw2.0"+".jsonl"),"w",encoding="utf-8") as w:
        json.dump(testing_raw_data,w,indent=4)


def train_test_data_establish(strategies, db_name, sample_num, len_low, len_high):
    train_target_dic_name = os.path.join("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset")  # 结果文件的目标文件夹
    test_target_dic_name = os.path.join("../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset")  # 结果文件的目标文件夹
    with open(os.path.join(train_target_dic_name,db_name+"_"+"training_dataset_raw2.0"+".jsonl"),"r",encoding="utf-8") as r:
        train_data_raw = json.load(r)
    with open(os.path.join(test_target_dic_name,db_name+"_"+"testing_dataset_raw2.0"+".jsonl"),"r",encoding="utf-8") as r:
        test_data_raw = json.load(r)

    for key, value in train_data_raw.items():
        for item in value:
            if key in ["FixMDistinctU", "FixMHaving0L", "FixMOn0L"]:
                if item["mutationName"] != key:
                    if key == "FixMHaving0L":
                        item["originalSqlsim_modified"] = item["originalSqlsim"]
                        item["mutatedSqlsim_modified"] = item["mutatedSqlsim"].replace("HAVING 1","HAVING 0")
                    elif key == "FixMOn0L":
                        item["originalSqlsim_modified"] = item["originalSqlsim"]
                        item["mutatedSqlsim_modified"] = item["mutatedSqlsim"].replace("ON 1", "ON 0")
                    elif key == "FixMDistinctU":
                        item["originalSqlsim_modified"] = item["mutatedSqlsim"]
                        item["mutatedSqlsim_modified"] = item["originalSqlsim"]
                elif item["mutationName"] == key:
                    item["originalSqlsim_modified"] = item["originalSqlsim"]
                    item["mutatedSqlsim_modified"] = item["mutatedSqlsim"]
            else:
                item["originalSqlsim_modified"] = item["originalSqlsim"]
                item["mutatedSqlsim_modified"] = item["mutatedSqlsim"]
    for key, value in test_data_raw.items():
        for item in value:
            if key in ["FixMDistinctU", "FixMHaving0L", "FixMOn0L"]:
                if item["mutationName"] != key:
                    if key == "FixMHaving0L":
                        item["originalSqlsim_modified"] = item["originalSqlsim"]
                        item["mutatedSqlsim_modified"] = item["mutatedSqlsim"].replace("HAVING 1","HAVING 0")
                    elif key == "FixMOn0L":
                        item["originalSqlsim_modified"] = item["originalSqlsim"]
                        item["mutatedSqlsim_modified"] = item["mutatedSqlsim"].replace("ON 1", "ON 0")
                    elif key == "FixMDistinctU":
                        item["originalSqlsim_modified"] = item["mutatedSqlsim"]
                        item["mutatedSqlsim_modified"] = item["originalSqlsim"]
                elif item["mutationName"] == key:
                    item["originalSqlsim_modified"] = item["originalSqlsim"]
                    item["mutatedSqlsim_modified"] = item["mutatedSqlsim"]
            else:
                item["originalSqlsim_modified"] = item["originalSqlsim"]
                item["mutatedSqlsim_modified"] = item["mutatedSqlsim"]

    with open(os.path.join(train_target_dic_name,db_name+"_"+"training_dataset2.0"+".jsonl"),"w",encoding="utf-8") as w:
        json.dump(train_data_raw,w,indent=4)
    with open(os.path.join(test_target_dic_name,db_name+"_"+"testing_dataset2.0"+".jsonl"),"w",encoding="utf-8") as w:
        json.dump(test_data_raw,w,indent=4)


# 将mysql的数据通过transfer llm转为对应的postgres语句，具体而言是transfer"originalSqlsim"
def transfer_mysql_to_postgres(dir_filename_prefix, mutation_name, origin_sqls, transfer_num):
    dir_filename = dir_filename_prefix + "("+mutation_name+")"+".jsonl"
    transferred_cnt = 0  # 记录已经transfer成功的个数
    transferred_success_cnt = 0     # 记录已经transfer成功的个数，达到目标的transfer_num则停止则结束并返回数据
    if os.path.exists(dir_filename):
        with open(dir_filename, 'r') as file:
            lines = file.readlines()
        transferred_cnt = len(lines)

        c = 0
        for line in lines:
            data = json.loads(line)
            if data["TransferSqlExecError"][-1] == "None":
                transferred_success_cnt += 1
            c += 1




    Iteration_Num = 15  # 默认最大迭代次数
    Temperature = 0.1
    Model = "gpt-4o-mini"
    # transferred_sqls = []

    chat = ChatOpenAI(temperature=Temperature, model=Model)
    for index in range(len(origin_sqls)):
        print("transferred_success_cnt:" + str(transferred_success_cnt))
        print(index)
        item = origin_sqls[index]
        # 已经达到需求的数目,跳出;
        if transferred_success_cnt >= transfer_num:
            break
        # 跳过已经处理过的数据项
        if index <= transferred_cnt-1:
            continue
        try:
            costs, transfer_results, exec_results, exec_times, error_messages, origin_exec_result, origin_exec_time, origin_error_message, exec_equalities = transfer_llm(
                chat=chat,
                temperature=Temperature,
                model=Model,
                error_iteration=True,
                iteration_num=Iteration_Num,
                FewShot=True,
                origin_db="mysql",
                target_db="postgres",
                sql_statement=item["originalSqlsim"]
                )

            item["SqlExecResult"] = origin_exec_result
            item["SqlExecTime"] = origin_exec_time
            item["SqlExecError"] = origin_error_message

            item["TransferResult"] = transfer_results
            item["TransferCost"] = costs
            item["TransferSqlExecResult"] = exec_results
            item["TransferSqlExecTime"] = exec_times
            item["TransferSqlExecError"] = error_messages  # 记录transfer sql的多次执行是否有报错：如果为None则表示成功执行，如果不是None而是具体报错则说明执行失败
            item["TransferSqlExecEqualities"] = exec_equalities   # 记录transfer sql的多次执行结果是否与origin sql一样：如果为True则说明一样，否则为不一样
            item["index"] = index
            #transferred_sqls.append(item)

            # 判断本条记录是否transfer 得到一个可执行的postgres语句，如果是则计数加一
            if error_messages[-1] == "None":
                transferred_success_cnt += 1

            with open(dir_filename, "a", encoding="utf-8") as w:
                json.dump(item, w)
                w.write("\n")
        except Exception as e:
            print(e)
            """
            with open(dir_filename, "a", encoding="utf-8") as w:
                json.dump(item, w)
                file.write("\n")
            """




def load_mysql_dataset_raw_3(TransferNum, dir_filename):
    training_testing_data_raw = {}
    if os.path.exists(dir_filename):
        with open(dir_filename,"r",encoding="utf-8") as r:
            training_testing_data_raw = json.load(r)

    # 变异策略：先测以下几种，FixMDistinctL，FixMCmpOpU，FixMInNullU，FixMWhere1U，FixMHaving1U，FixMOn1U
    fine_tuning_dataset = load_fine_tuning_dataset("output1", "mysql", 500, 510,"FixMDistinctL","")
    if "FixMDistinctL" not in training_testing_data_raw:
        training_testing_data_raw["FixMDistinctL"] = transfer_mysql_to_postgres(fine_tuning_dataset["FixMDistinctL"], 0, TransferNum)
    else:
        training_testing_data_raw["FixMDistinctL"] += transfer_mysql_to_postgres(fine_tuning_dataset["FixMDistinctL"], len(training_testing_data_raw["FixMDistinctL"]), TransferNum)


    fine_tuning_dataset = load_fine_tuning_dataset("output1", "mysql", 1, 500,"FixMCmpOpU","")
    if "FixMCmpOpU" not in training_testing_data_raw:
        training_testing_data_raw["FixMCmpOpU"] = transfer_mysql_to_postgres(fine_tuning_dataset["FixMCmpOpU"], 0, TransferNum)
    else:
        training_testing_data_raw["FixMCmpOpU"] += transfer_mysql_to_postgres(fine_tuning_dataset["FixMCmpOpU"], len(training_testing_data_raw["FixMCmpOpU"]), TransferNum)

    """
    FixMInNullU_dataset = load_fine_tuning_dataset("output1", "mysql", 1, float('inf') ,"FixMInNullU","")["FixMInNullU"]
    FixMInNullU_dataset += load_fine_tuning_dataset("output2", "mysql", 1, float('inf') ,"FixMInNullU","")["FixMInNullU"]
    FixMInNullU_dataset += load_fine_tuning_dataset("output3", "mysql", 1, float('inf') ,"FixMInNullU","")["FixMInNullU"]
    FixMInNullU_dataset += load_fine_tuning_dataset("output4", "mysql", 1, float('inf') ,"FixMInNullU","")["FixMInNullU"]
    if "FixMInNullU" not in training_testing_data_raw:
        training_testing_data_raw["FixMInNullU"] = transfer_mysql_to_postgres(FixMInNullU_dataset, 0, TransferNum)
    else:
        training_testing_data_raw["FixMInNullU"] += transfer_mysql_to_postgres(FixMInNullU_dataset, len(training_testing_data_raw["FixMInNullU"]), TransferNum)
    """

    """
    FixMWhere1U_dataset = load_fine_tuning_dataset("output1", "mysql", 1, float('inf') ,"FixMWhere1U","")["FixMWhere1U"]
    FixMWhere1U_dataset += load_fine_tuning_dataset("output2", "mysql", 1, float('inf') ,"FixMWhere1U","")["FixMWhere1U"]
    FixMWhere1U_dataset += load_fine_tuning_dataset("output3", "mysql", 1, float('inf') ,"FixMWhere1U","")["FixMWhere1U"]
    FixMWhere1U_dataset += load_fine_tuning_dataset("output4", "mysql", 1, float('inf') ,"FixMWhere1U","")["FixMWhere1U"]
    if "FixMWhere1U" not in training_testing_data_raw:
        training_testing_data_raw["FixMWhere1U"] = transfer_mysql_to_postgres(FixMWhere1U_dataset, 0, TransferNum)
    else:
        training_testing_data_raw["FixMWhere1U"] += transfer_mysql_to_postgres(FixMWhere1U_dataset, len(training_testing_data_raw["FixMWhere1U"]), TransferNum)
    """

    # fine_tuning_dataset = load_fine_tuning_dataset("output1", "mysql", 350, 600 ,"FixMHaving1U","")
    fine_tuning_dataset = load_fine_tuning_dataset("output1", "mysql", 300, 350 ,"FixMHaving1U","")
    if "FixMHaving1U" not in training_testing_data_raw:
        training_testing_data_raw["FixMHaving1U"] = transfer_mysql_to_postgres(fine_tuning_dataset["FixMHaving1U"], 0, TransferNum)
    else:
        training_testing_data_raw["FixMHaving1U"] += transfer_mysql_to_postgres(fine_tuning_dataset["FixMHaving1U"], len(training_testing_data_raw["FixMHaving1U"]), TransferNum)


    FixMOn1U_dataset = load_fine_tuning_dataset("output1", "mysql", 720, 760 ,"FixMOn1U","")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output2", "mysql", 720, 760, "FixMOn1U", "")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output3", "mysql", 720, 760, "FixMOn1U", "")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output4", "mysql", 720, 760, "FixMOn1U", "")["FixMOn1U"]

    if "FixMOn1U" not in training_testing_data_raw:
        training_testing_data_raw["FixMOn1U"] = transfer_mysql_to_postgres(FixMOn1U_dataset, 0, TransferNum)
    else:
        training_testing_data_raw["FixMOn1U"] += transfer_mysql_to_postgres(FixMOn1U_dataset, len(training_testing_data_raw["FixMOn1U"]), TransferNum)


    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(training_testing_data_raw, w, indent=4)


def load_mysql_dataset_raw_4(TransferNum, dir_filename_prefix):
    # 变异策略：先测以下几种，FixMDistinctL，FixMCmpOpU，FixMHaving1U，FixMOn1U
    fine_tuning_dataset = load_fine_tuning_dataset("output2", "mysql", 1, 600,"FixMDistinctL","")
    transfer_mysql_to_postgres(dir_filename_prefix, "FixMDistinctL", fine_tuning_dataset["FixMDistinctL"], TransferNum)


    fine_tuning_dataset = load_fine_tuning_dataset("output2", "mysql", 1, 700,"FixMCmpOpU","")
    transfer_mysql_to_postgres(dir_filename_prefix, "FixMCmpOpU", fine_tuning_dataset["FixMCmpOpU"], TransferNum)


    fine_tuning_dataset = load_fine_tuning_dataset("output2", "mysql", 1, 450 ,"FixMHaving1U","")
    transfer_mysql_to_postgres(dir_filename_prefix, "FixMHaving1U", fine_tuning_dataset["FixMHaving1U"], TransferNum)


    FixMOn1U_dataset = load_fine_tuning_dataset("output1", "mysql", 1, 830 ,"FixMOn1U","")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output2", "mysql", 1, 830, "FixMOn1U", "")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output3", "mysql", 1, 830, "FixMOn1U", "")["FixMOn1U"]
    FixMOn1U_dataset += load_fine_tuning_dataset("output4", "mysql", 1, 830, "FixMOn1U", "")["FixMOn1U"]
    transfer_mysql_to_postgres(dir_filename_prefix, "FixMOn1U", FixMOn1U_dataset, TransferNum)



def postgres_training_testing_dataset_establish(dataset_raw_filename, dataset_filename):
    with open(dataset_raw_filename,"r", encoding="utf-8") as r:
        postgres_raw = json.load(r)

    postgres_training_testing_dataset = {}
    for key, value in postgres_raw.items():
        items_new = []
        for item in value:
            flag = None
            if item["mutationName"][-1] == 'L':
                if item["isUpper"] == True:
                    flag = False
                elif item["isUpper"] == False:
                    flag = True
            elif item["mutationName"][-1] == 'U':
                if item["isUpper"] == True:
                    flag = True
                elif item["isUpper"] == False:
                    flag = False
            item_new = {
                "index": item["index"],
                "reportTime": item["reportTime"],
                "bugId": item["bugId"],
                "sqlId": item["sqlId"],
                "mutationName": item["mutationName"],
                "isUpper": item["isUpper"],
                "originalSql": item["originalSql"],
                "mutatedSql": item["mutatedSql"],
                "originalSqllength": item["originalSqllength"],
                "originalSqlsim": item["originalSqlsim"],
                "mutatedSqlsim": item["mutatedSqlsim"],
                "originalSqlsimlength": item["originalSqlsimlength"],
                "originalSqlsim_postgres": item["TransferResult"][-1]["TransferSQL"],
                "mutatedSqlsim_postgres": {
                    "mutated sql": item["TransferResult"][-1]["TransferSQL"],
                    "flag": flag
                }
            }
            items_new.append(item_new)
        postgres_training_testing_dataset[key] = items_new

    with open(dataset_filename,"w", encoding="utf-8") as w:
        json.dump(postgres_training_testing_dataset, w, indent=4)

def postgres_training_testing_dataset_split(training_size,training_filename, testing_filename):
    with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_testing_dataset1.0.jsonl","r", encoding="utf-8") as r:
        postgres_dataset = json.load(r)

    training_dataset = {}
    testing_dataset = {}

    """
    将剩余有效数据分配到训练集和测试集中，将以下index的样例分配到训练集中
    "FixMDistinctL":[7,8,11]
    "FixMCmpOpU":[4,6,30]
    "FixMHaving1U":[10,18,22,23,25,28,29,31,33,35,37]
    "FixMOn1U":[1,3,11]
    """
    temp = {
        "FixMDistinctL": [7, 8, 11],
        "FixMCmpOpU": [4, 6, 30],
        "FixMHaving1U": [10, 13,18, 22, 23, 25, 28, 29, 31, 33, 35, 37],
        "FixMOn1U": [1, 3, 11]
    }

    for key, value in postgres_dataset.items():
        training_cnt = 0
        training_dataset[key] = []
        testing_dataset[key] = []
        training_indexes = []
        if len(value) < training_size:
            continue

        for index in temp[key]:
            value[index]["mutatedSqlsim_postgres_training"] = []
            training_dataset[key].append(value[index])
            training_indexes.append(index)
            training_cnt += 1

        for item in value:
            if training_cnt >= training_size:
                break
            if item["index"] not in temp[key]:
                item["mutatedSqlsim_postgres_training"] = []
                training_dataset[key].append(item)
                training_indexes.append(item["index"])
                training_cnt += 1

        for item in value:
            if item["index"] not in training_indexes:
                testing_dataset[key].append(item)

        # 处理"FixMDistinctL"的数据:flag全部为true
        if key == "FixMDistinctL":
            for dataset in [training_dataset,testing_dataset]:
                for item in dataset[key]:
                    item["mutatedSqlsim_postgres_training"] = []
                    # 使用正则表达式查找所有"SELECT"子串
                    matches = re.findall(r"SELECT", item["originalSqlsim_postgres"], re.IGNORECASE)
                    if len(matches) > 0:
                        # 遍历所有匹配项,逐一修改为"SELECT DISTINCT"
                        origin_sql = item["originalSqlsim_postgres"]
                        last_end = 0
                        for match in matches:
                            start = origin_sql.index(match, last_end)
                            end = start + len(match)
                            modified_sql = origin_sql[:start] + "SELECT DISTINCT" + origin_sql[end:]
                            item["mutatedSqlsim_postgres_training"].append({
                                "mutated sql": modified_sql,
                                "flag": True
                            })
                            last_end = end



        # 处理"FixMCmpOpU"的数据：flag需要后续人工自行判断
        if key == "FixMCmpOpU":
            for dataset in [training_dataset,testing_dataset]:
                for item in dataset[key]:
                    item["mutatedSqlsim_postgres_training"] = []
                    matches = re.findall(r"[><=]", item["originalSqlsim_postgres"], re.IGNORECASE)
                    if len(matches) > 0:
                        # 遍历所有匹配项,逐一修改为"SELECT DISTINCT"
                        origin_sql = item["originalSqlsim_postgres"]
                        last_end = 0
                        for match in matches:
                            start = origin_sql.index(match, last_end)
                            end = start + len(match)
                            if match == "<":
                                match_replace = "<="
                            elif match == ">":
                                match_replace = ">="
                            elif match == "=":
                                match_replace = ">="
                            modified_sql = origin_sql[:start] + match_replace + origin_sql[end:]
                            item["mutatedSqlsim_postgres_training"].append({
                                "mutated sql": modified_sql,
                                "flag": True
                            })
                            last_end = end


        # 处理"FixMHaving1U"的数据：flag暂时定为全是true
        if key == "FixMHaving1U":
            for dataset in [training_dataset,testing_dataset]:
                for item in dataset[key]:
                    item["mutatedSqlsim_postgres_training"] = []
                    matches = re.findall(r" HAVING ", item["originalSqlsim_postgres"], re.IGNORECASE)
                    if len(matches) > 0:
                        # 遍历所有匹配项,逐一修改为"SELECT DISTINCT"
                        origin_sql = item["originalSqlsim_postgres"]
                        last_end = 0
                        for match in matches:
                            start = origin_sql.index(match, last_end)
                            end = start + len(match)
                            modified_sql = origin_sql[:start] + " HAVING TRUE"
                            item["mutatedSqlsim_postgres_training"].append({
                                "mutated sql": modified_sql,
                                "flag": True
                            })
                            last_end = end

        # 处理"FixMOn1U"的数据：flag暂时定为全是true
        if key == "FixMOn1U":
            for dataset in [training_dataset,testing_dataset]:
                for item in dataset[key]:
                    item["mutatedSqlsim_postgres_training"] = []
                    matches = re.findall(r" ON ", item["originalSqlsim_postgres"], re.IGNORECASE)
                    if len(matches) > 0:
                        origin_sql = item["originalSqlsim_postgres"]
                        last_end = 0
                        for match in matches:
                            start = origin_sql.index(match, last_end)
                            end = start + len(match)
                            modified_sql = origin_sql[:start] + " ON TRUE"
                            item["mutatedSqlsim_postgres_training"].append({
                                "mutated sql": modified_sql,
                                "flag": True
                            })
                            last_end = end

        print(len(training_dataset[key]))
        print(len(testing_dataset[key]))


    with open(training_filename, "w", encoding="utf-8") as w:
        json.dump(training_dataset, w, indent=4)
    with open(testing_filename,"w", encoding="utf-8") as w:
        json.dump(testing_dataset, w, indent=4)


strategy_names = [
    "FixMDistinctU",
    "FixMDistinctL",
    "FixMCmpOpU",
    "FixMCmpOpL",
    "FixMInNullU",
    "FixMWhere1U",
    "FixMHaving1U",
    "FixMHaving0L",
    "FixMOn1U",
    "FixMOn0L"
]

# mysql的mutate llm数据集构建

"""
load_fine_tuning_dataset("output1", "mysql", 1, float('inf'))
load_fine_tuning_dataset("output2", "mysql", 1, float('inf'))
load_fine_tuning_dataset("output3", "mysql", 1, float('inf'))
load_fine_tuning_dataset("output4", "mysql", 1, float('inf'))
"""
"""
# load_fine_tuning_dataset("output1", "mysql", 1, 340)
# load_fine_tuning_dataset("output1", "mysql", 1, 280)
# load_fine_tuning_dataset("output2", "mysql", 1, 300)
# load_fine_tuning_dataset("output1", "mysql", 320, 340)
# load_fine_tuning_dataset("output1", "mysql", 340, 690)
"""

"""
load_fine_tuning_dataset("output1", "mysql", 1, 320,"REGEXP")
load_fine_tuning_dataset("output2", "mysql", 1, 320,"REGEXP")
load_fine_tuning_dataset("output3", "mysql", 1, 320,"REGEXP")
load_fine_tuning_dataset("output4", "mysql", 1, 320,"REGEXP")
"""



# train_test_data_raw_establish(strategy_names, "mysql", 20, 1, float('inf'))
# train_test_data_establish(strategy_names, "mysql", 20, 1, float('inf'))

strategies_illustration_mysql_filename = "../../Dataset/FineTuning/Pinolo FineTuning/mutate_strategies_illustration_mysql1.0.json"

training_dataset_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset2.0.jsonl"
formatted_training_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset_formatted2.0.jsonl"
# exec_dataset_sqls(training_dataset_filename)
# data_json_establish("MySQL", strategies_illustration_mysql_filename,training_dataset_filename,formatted_training_data_filename,"originalSqlsim_modified","mutatedSqlsim_modified")

testing_dataset_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/mysql_testing_dataset2.0.jsonl"
formatted_testing_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/mysql_testing_dataset_formatted2.0.jsonl"
# exec_dataset_sqls(testing_dataset_filename)
# data_json_establish("MySQL", strategies_illustration_mysql_filename, testing_dataset_filename,formatted_testing_data_filename,"originalSqlsim_modified","mutatedSqlsim_modified")

# data_formatting_check_and_cost_estimation(formatted_training_data_filename)
# data_formatting_check_and_cost_estimation(formatted_testing_data_filename)





# postgres的mutate llm数据集构建：1.0
postgres_dataset_raw = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_testing_dataset_raw1.0.jsonl"
postgres_dataset = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_testing_dataset1.0.jsonl"

# load_mysql_dataset_raw_3(40, postgres_dataset_raw)
# postgres_training_testing_dataset_establish(postgres_dataset_raw, postgres_dataset)


"""
            "mutatedSqlsim_postgres": {
                "mutated sql": item["TransferResult"][-1]["TransferSQL"],
                "flag": item["isUpper"]
            }中的"mutated sql"暂定为和"originalSqlsim_postgres"一样的，再进行人工修改
"""
# 执行"originalSqlsim_postgres"和"mutatedSqlsim_postgres"语句保证正确性
# exec_dataset_sqls(postgres_dataset, "postgres", ["originalSqlsim_postgres", "mutatedSqlsim_postgres"])

# 将剩余有效数据分配到训练集和测试集中
training_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset1.0.jsonl"
testing_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset1.0.jsonl"
# postgres_training_testing_dataset_split(20, training_filename,testing_filename)
# exec_dataset_sqls(training_filename, "postgres", ["originalSqlsim_postgres", "mutatedSqlsim_postgres"])
# exec_dataset_sqls(testing_filename, "postgres", ["originalSqlsim_postgres", "mutatedSqlsim_postgres"])


strategies_illustration_postgres_filename = "../../Dataset/FineTuning/Pinolo FineTuning/mutate_strategies_illustration_postgres1.0.json"
strategies_illustration_postgres_fewshot_filename = "../../Dataset/FineTuning/Pinolo FineTuning/mutate_strategies_illustration_postgres2.0.json"

postgres_training_dataset_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset1.0.jsonl"
formatted_postgres_training_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset_formatted1.0.jsonl"
# data_json_establish("PostgresSQL", strategies_illustration_postgres_filename,postgres_training_dataset_filename, formatted_postgres_training_data_filename, "originalSqlsim_postgres", "mutatedSqlsim_postgres_training")
# data_formatting_check_and_cost_estimation(formatted_postgres_training_data_filename)



postgres_testing_dataset_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset1.0.jsonl"
formatted_postgres_testing_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_formatted1.0.jsonl"
formatted_postgres_eval_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_eval_dataset_formatted1.0.jsonl"
formatted_postgres_eval_data_plus_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_eval_dataset_plus_formatted1.0.jsonl"
formatted_postgres_fewshot_eval_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/FewShotDataset/postgres_fewshot_eval_dataset_formatted1.0.jsonl"
# data_json_establish("PostgresSQL", strategies_illustration_postgres_filename,postgres_testing_dataset_filename, formatted_postgres_testing_data_filename, "originalSqlsim_postgres", "mutatedSqlsim_postgres_training")
# data_formatting_check_and_cost_estimation(formatted_postgres_testing_data_filename)
# 构建postgres的测试集
# eval_data_json_establish("PostgresSQL", strategies_illustration_postgres_filename, postgres_testing_dataset_filename, formatted_postgres_eval_data_filename,"originalSqlsim_postgres", "mutatedSqlsim_postgres")
# eval_data_json_establish("PostgresSQL", strategies_illustration_postgres_filename, postgres_testing_dataset_filename, formatted_postgres_eval_data_plus_filename,"originalSqlsim_postgres", "mutatedSqlsim_postgres_training")

# 从微调训练集中选几个shot
# eval_fewshot_data_json_establish(3, "PostgresSQL", strategies_illustration_postgres_fewshot_filename, postgres_training_dataset_filename, formatted_postgres_fewshot_eval_data_filename,"originalSqlsim_postgres", "mutatedSqlsim_postgres_training")



# 构建mysql的测试集
strategies_illustration_mysql_filename = "../../Dataset/FineTuning/Pinolo FineTuning/mutate_strategies_illustration_mysql2.0.json"
formatted_mysql_eval_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/mysql_eval_dataset_formatted1.0.jsonl"
formatted_mysql_eval_data_plus_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/mysql_eval_dataset_plus_formatted1.0.jsonl"
# eval_data_json_establish("MySQL", strategies_illustration_mysql_filename, postgres_testing_dataset_filename, formatted_mysql_eval_data_filename,"originalSqlsim", "mutatedSqlsim")






# 为微调好的mutate llm构造数据集
def mutate_llm_testing_dataset(strategies_filename, src_filename, dir_filename, db_name, muatate_name):
    with open(strategies_filename, "r", encoding="utf-8") as r:
        strategies = json.load(r)
    with open(src_filename, "r", encoding="utf-8") as r:
        contents = r.readlines()
    # 角色信息中包含db类型信息
    role_prompt = "You are an expert in " + db_name + " statement mutation."
    for content in contents:
        data = json.loads(content)
        if data["TransferSqlExecError"][-1] != "None":
            continue
        # 特定格式的message
        data_new = {
            "index": data["index"],
            "reportTime": data["reportTime"],
            "bugId": data["bugId"],
            "sqlId": data["sqlId"],
            "mutationName": data["mutationName"],
            "isUpper": data["isUpper"],
            "originalSql": data["originalSql"],
            "mutatedSql": data["mutatedSql"],
            "originalSqlsim": data["originalSqlsim"],
            "mutatedSqlsim": data["mutatedSqlsim"],
            "transferredSqlsim": data["TransferResult"][-1]["TransferSQL"],
            "MutateLLM_Message": [
                {"role": "system", "content": str(role_prompt + strategies[muatate_name])},
                {"role": "user", "content": data["TransferResult"][-1]["TransferSQL"]}
            ]
        }
        with open(dir_filename, "a", encoding="utf-8") as w:
            json.dump(data_new, w)
            w.write("\n")


# postgres的mutate llm测试数据集构建：2.0,100 x 4
postgres_dataset_raw_2_prefix = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_raw2.0"
postgres_dataset = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_testing_dataset1.0.jsonl"

# transfer llm:mysql->postgres
# load_mysql_dataset_raw_4(100, postgres_dataset_raw_2_prefix)

# 为Mutate LLM构造满足特定格式的testing data文件
strategies_illustration_postgres_filename = "../../Dataset/FineTuning/Pinolo FineTuning/mutate_strategies_illustration_postgres1.0.json"
src_filename ={
    "FixMCmpOpU":"../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl",
    "FixMDistinctL":"../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl",
    "FixMHaving1U":"../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl",
    "FixMOn1U":"../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_raw2.0(FixMOn1U).jsonl"
}
dir_filenames = {
    "FixMCmpOpU":"../../Dataset/MutateLLM/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl",
    "FixMDistinctL":"../../Dataset/MutateLLM/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl",
    "FixMHaving1U":"../../Dataset/MutateLLM/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl",
    "FixMOn1U":"../../Dataset/MutateLLM/PostgresSQL/TestingDataset/postgres_testing_dataset_raw2.0(FixMOn1U).jsonl"
}
"""
for key, value in src_filename.items():
    mutate_llm_testing_dataset(strategies_illustration_postgres_filename, value, dir_filenames[key], "PostgresSQL", key)
"""

