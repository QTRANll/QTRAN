# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/2 21:24
# @Author  : shaocanfan
# @File    : FineTuning_MutateLLM.py
# @Intro   :


import os
from openai import OpenAI
import requests

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


"""
client = OpenAI(
    # 修改api_key为网站生成的令牌
    api_key="",
    base_url="https://api.openai.com/v1"
)
client.base_url="https://ai-yyds.com/v1"
"""


def fine_tuning_pinolo(training_data_filename, testing_data_filename,suffix):
  client = OpenAI(
    api_key="",
  )

  # 上传训练数据集
  # FileObject(id='file-Q4iMX3ECBhQ7S6fkJToqRdJZ', bytes=145639, created_at=1722772740, filename='mysql_training_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
  training_file_object = client.files.create(
    file=open(training_data_filename, "rb"),
    purpose="fine-tune"
  )
  print("训练集：")
  print(training_file_object)

  # 上传测试数据集
  testing_file_object = client.files.create(
    file=open(testing_data_filename,"rb"),
    purpose="fine-tune"
  )
  print("测试集：")
  print(testing_file_object)

  # 创建微调模型任务
  model_object = client.fine_tuning.jobs.create(
    training_file=training_file_object.id,
    validation_file=testing_file_object.id,
    model="gpt-4o-mini-2024-07-18",
    suffix=suffix
  )
  print("微调任务：")
  print(model_object)


def check_fine_tuning_stage(ftjob_id):
  client = OpenAI(
    api_key="",
  )
  # List 10 fine-tuning jobs
  print("List 10 fine-tuning jobs:")
  print(client.fine_tuning.jobs.list(limit=10))
  # Retrieve the state of a fine-tune
  print("Retrieve the state of a fine-tune:"+ftjob_id)
  print(client.fine_tuning.jobs.retrieve(ftjob_id))
  # Cancel a job
  # client.fine_tuning.jobs.cancel("")

  # List up to 10 events from a fine-tuning job
  print("List up to 10 events from a fine-tuning job:"+ftjob_id)
  print(client.fine_tuning.jobs.list_events(fine_tuning_job_id=ftjob_id, limit=10))




def mysql_fine_tuning_1(training_data_filename, testing_data_filename):


  # fine_tuning_pinolo(training_data_filename, testing_data_filename,"pinolo-mutate-llm")
  """
  训练集：
  FileObject(id='file-F5ONQvl0svALeKfomy71T8rg', bytes=347981, created_at=1723205154, filename='mysql_training_dataset_formatted2.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
  测试集：
  FileObject(id='file-ctERcdOSaxu2iYywFNTzpQs7', bytes=373532, created_at=1723205155, filename='mysql_testing_dataset_formatted2.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
  微调任务：
  FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs='auto', batch_size='auto', learning_rate_multiplier='auto'), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='validating_files', trained_tokens=None, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])
  """


  # check_fine_tuning_stage("ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ")


  # checkpoints
  url = "https://api.openai.com/v1/fine_tuning/jobs/ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ/checkpoints"
  headers = {
    "Authorization": f"Bearer "
  }
  # response = requests.get(url, headers=headers)
  # print(response.json())



  # 微调结束后，获取微调的job events信息
  """
  client = OpenAI(
    api_key="",
  )
  job_events = client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ", limit=300).data
  job_events_json = []
  for event in job_events:
    job_events_json.append(event.dict())
  with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingEvaluation/mysql_training2.0_JobEvents.json", "w",
            encoding="utf-8") as w:
    json.dump(job_events_json, w, indent=4)
  """


  # 获取results files：打印出来为乱码
  """
  results_files = "file-olGk5MMJhcAPQWI4y0oW5fIj"
  content = client.files.content(results_files)
  print(content.text)
  print(content.content.decode('utf-8'))
  print(content.encoding)
  with open("file.csv", "w", encoding="utf-8") as f:
    f.write(content.text)
  """

  """
  url = "https://api.openai.com/v1/files/file-olGk5MMJhcAPQWI4y0oW5fIj/content"
  headers = {
      "Authorization": f"Bearer "
  }
  # 发送 GET 请求并获取响应
  response = requests.get(url, headers=headers)
  print(response.text)
  # 检查请求是否成功
  if response.status_code == 200:
      # 将响应内容保存为 JSON Lines 格式的文件
      with open("file.csv", "w", encoding="utf-8") as f:
          f.write(response.text)
      print("File saved successfully.")
  else:
      print(f"Error: {response.status_code} - {response.text}")
  """


def postgres_fine_tuning_1(training_data_filename, testing_data_filename):
  # fine_tuning_pinolo(training_data_filename, testing_data_filename,"pinolo-mutate-llm")
  """
  训练集：
  FileObject(id='file-8QiUEBvXynmHVMNY36Ud7iHf', bytes=181185, created_at=1723885693, filename='postgres_training_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
  测试集：
  FileObject(id='file-Zn0ACseWyn6wSuSJJctp7B1O', bytes=165365, created_at=1723885695, filename='postgres_testing_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
  微调任务：
  FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs='auto', batch_size='auto', learning_rate_multiplier='auto'), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='validating_files', trained_tokens=None, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[])
  """


  # check_fine_tuning_stage("ftjob-j6mDj7MYs1O9bp3D1oPw3rIk")


  # checkpoints
  url = "https://api.openai.com/v1/fine_tuning/jobs/ftjob-j6mDj7MYs1O9bp3D1oPw3rIk/checkpoints"
  headers = {
    "Authorization": f"Bearer "
  }
  response = requests.get(url, headers=headers)
  # print(response.json())



  # 微调结束后，获取微调的job events信息

  client = OpenAI(
    api_key="",
  )
  """
  job_events = client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-j6mDj7MYs1O9bp3D1oPw3rIk", limit=240).data
  job_events_json = []
  for event in job_events:
    job_events_json.append(event.dict())
  with open("../../Dataset/FineTuning/Pinolo FineTuning/TrainingEvaluation/postgres_training1.0_JobEvents.json", "w",
            encoding="utf-8") as w:
    json.dump(job_events_json, w, indent=4)
  """





mysql_training_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/mysql_training_dataset_formatted2.0.jsonl"
mysql_testing_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/mysql_testing_dataset_formatted2.0.jsonl"
# mysql_fine_tuning_1(mysql_training_data_filename, mysql_testing_data_filename)

postgres_training_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TrainingDataset/postgres_training_dataset_formatted1.0.jsonl"
postgres_testing_data_filename = "../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset_formatted1.0.jsonl"
# postgres_fine_tuning_1(postgres_training_data_filename,postgres_testing_data_filename)

