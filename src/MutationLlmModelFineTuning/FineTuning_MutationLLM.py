#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/2 21:24
# @Author  : shaocanfan
# @File    : FineTuning_MutationLLM.py
# @Intro   :

import os
from openai import OpenAI
import requests
import openai
import argparse

environment_variables = os.environ

def fine_tune_mutation_llm(api_key, training_data_filename, suffix):
    client = OpenAI(
        api_key=api_key,
    )
    # 上传训练数据集
    training_file_object = client.files.create(
        file=open(training_data_filename, "rb"),
        purpose="fine-tune"
    )
    print("Training Data File Object Information:")
    print(training_file_object)
    print('\n')

    # 创建微调模型任务
    model_object = client.fine_tuning.jobs.create(
        training_file=training_file_object.id,
        model="gpt-4o-mini-2024-07-18",
        suffix=suffix
    )
    print("Fine-tuning Task Information:")
    print(model_object, flush=True)
    print('\n')

    print("Fine-tuning Job ID:" + model_object.id)
    print('Please record the "Fine-tuning Job ID" to check the fine-tuning stage, which can take several minutes.\n')


def check_fine_tuning_stage(api_key, ftjob_id):
    client = OpenAI(
        api_key=api_key,
    )
    # List 10 fine-tuning jobs
    """
    print("List 10 fine-tuning jobs:")
    print(client.fine_tuning.jobs.list(limit=10))
    """
    # Retrieve the state of a fine-tune
    print(f"Retrieve the state of a fine-tune: {ftjob_id}")
    stage = client.fine_tuning.jobs.retrieve(ftjob_id)
    print(stage)
    print('\n')
    # List up to 10 events from a fine-tuning job
    """
    print(f"List up to 10 events from a fine-tuning job: {ftjob_id}")
    print(client.fine_tuning.jobs.list_events(fine_tuning_job_id=ftjob_id, limit=10))
    """
    if stage.fine_tuned_model:
      print(f"The Fine-tuning Job {ftjob_id} has been finished.\nThe fine_tuned_model ID is: {stage.fine_tuned_model}.\nPlease record the fine_tuned_model ID to run QTRAN's Mutation LLM later.")
    else:
      print(
        f"The Fine-tuning Job {ftjob_id} hasn't been finished.\nThe fine_tuned_model ID is: {stage.fine_tuned_model}.\nPlease wait for several minutes and check later.")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune or Check fine-tuning status of Mutation LLM")

    # 添加命令行参数
    parser.add_argument("--api_key", required=True, help="Your OpenAI API key")
    parser.add_argument("--training_data_filename", help="Path to the training data file (e.g., .jsonl)")
    parser.add_argument("--suffix", help="Suffix for the fine-tuned model")
    parser.add_argument("--job_id", help="Fine-tuning Job ID to check progress")

    # 解析参数
    args = parser.parse_args()

    # 如果指定了 job_id，调用 check_fine_tuning_stage
    if args.job_id:
        check_fine_tuning_stage(args.api_key, args.job_id)
    else:
        # 否则执行微调操作
        if not args.training_data_filename or not args.suffix:
            print("You must provide --training_data_filename and --suffix for fine-tuning.")
        else:
            fine_tune_mutation_llm(args.api_key, args.training_data_filename, args.suffix)


if __name__ == "__main__":
    main()
