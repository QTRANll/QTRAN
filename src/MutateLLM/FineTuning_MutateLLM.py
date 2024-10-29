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
    api_key="sk-HPcogl7E8mm2gmWSAe93D5EeE49b49849c52B5Fa748a2000",
    base_url="https://api.openai.com/v1"
)
client.base_url="https://ai-yyds.com/v1"
"""


def fine_tuning_pinolo(training_data_filename, testing_data_filename,suffix):
  client = OpenAI(
    api_key="sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A",
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
    api_key="sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A",
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

  # Delete a fine-tuned model (must be an owner of the org the model was created in)
  # client.models.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")



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
  """
  第一次check状态
  List 10 fine-tuning jobs:
  SyncCursorPage[FineTuningJob](data=[FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='validating_files', trained_tokens=None, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])], object='list', has_more=False)

  Retrieve the state of a fine-tune:ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ
  FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='validating_files', trained_tokens=None, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])

  List up to 10 events from a fine-tuning job:ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ
  SyncCursorPage[FineTuningJobEvent](data=[FineTuningJobEvent(id='ftevent-2CT7fwITvhbSbrlP4Z1F7bZT', created_at=1723205158, level='info', message='Validating training file: file-F5ONQvl0svALeKfomy71T8rg and validation file: file-ctERcdOSaxu2iYywFNTzpQs7', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-SSat1MhrdZjBQO1H6jSizNZr', created_at=1723205158, level='info', message='Created fine-tuning job: ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', object='fine_tuning.job.event', data={}, type='message')], object='list', has_more=False)


  完成后查询结果：
  List 10 fine-tuning jobs:
  SyncCursorPage[FineTuningJob](data=[FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', finished_at=1723208013, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-olGk5MMJhcAPQWI4y0oW5fIj'], status='succeeded', trained_tokens=379446, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])], object='list', has_more=False)

  Retrieve the state of a fine-tune:ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ
  FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', finished_at=1723208013, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-olGk5MMJhcAPQWI4y0oW5fIj'], status='succeeded', trained_tokens=379446, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])

  List up to 10 events from a fine-tuning job:ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ
  SyncCursorPage[FineTuningJobEvent](data=[FineTuningJobEvent(id='ftevent-xVUWKhkSReoSt1aA3SMn0lpL', created_at=1723208021, level='info', message='The job has successfully completed', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-QhXCSOyKMRXfy3OuxOayB1ja', created_at=1723208015, level='info', message='New fine-tuned model created: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-FSE2wiOLE6v76LtIw82MQ2kp', created_at=1723208015, level='info', message='Checkpoint created at step 200 with Snapshot ID: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPavMj:ckpt-step-200', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-4DsBFQUO2O5XM3MyoeGaExSu', created_at=1723208015, level='info', message='Checkpoint created at step 100 with Snapshot ID: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPavaa:ckpt-step-100', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-9ZPjLQD7owPxiAsl7jwxhcoe', created_at=1723207997, level='info', message='Step 300/300: training loss=0.00, validation loss=0.00, full validation loss=0.05', object='fine_tuning.job.event', data={'step': 300, 'train_loss': 0.0013630171306431293, 'valid_loss': 5.731426301549693e-05, 'total_steps': 300, 'full_valid_loss': 0.05314807081111815, 'train_mean_token_accuracy': 1.0, 'valid_mean_token_accuracy': 1.0, 'full_valid_mean_token_accuracy': 0.6705839612061476}, type='metrics'), FineTuningJobEvent(id='ftevent-3YRvTVoVXPEWfuUWFZPEaWJl', created_at=1723207944, level='info', message='Step 299/300: training loss=0.00', object='fine_tuning.job.event', data={'step': 299, 'train_loss': 2.608481963761733e-06, 'total_steps': 300, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-rgvKFRjeX3M8R09NRzAAfzJ6', created_at=1723207941, level='info', message='Step 298/300: training loss=0.00', object='fine_tuning.job.event', data={'step': 298, 'train_loss': 2.0562149074976332e-05, 'total_steps': 300, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-NIsap3GgXBNNfnkIU8k5pdBs', created_at=1723207941, level='info', message='Step 297/300: training loss=0.00', object='fine_tuning.job.event', data={'step': 297, 'train_loss': 6.864314855192788e-06, 'total_steps': 300, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-9RWdrber2cC9Ca563He7uKiP', created_at=1723207941, level='info', message='Step 296/300: training loss=0.00', object='fine_tuning.job.event', data={'step': 296, 'train_loss': 6.175851467560278e-06, 'total_steps': 300, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-TYvaD8C72TrV50wOgXC2vlTk', created_at=1723207941, level='info', message='Step 295/300: training loss=0.00', object='fine_tuning.job.event', data={'step': 295, 'train_loss': 1.410470486007398e-05, 'total_steps': 300, 'train_mean_token_accuracy': 1.0}, type='metrics')], object='list', has_more=True)
  """

  # checkpoints
  url = "https://api.openai.com/v1/fine_tuning/jobs/ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ/checkpoints"
  headers = {
    "Authorization": f"Bearer sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A"
  }
  # response = requests.get(url, headers=headers)
  # print(response.json())
  """
  {'object': 'list', 'data': [{'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_nuaEKibogmcsHp3FUBLfgbDs', 'created_at': 1723207952, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', 'fine_tuning_job_id': 'ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', 'metrics': {'step': 300, 'train_loss': 0.0013630171306431293, 'train_mean_token_accuracy': 1.0, 'valid_loss': 5.731426301549693e-05, 'valid_mean_token_accuracy': 1.0}, 'step_number': 300}, {'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_3KWdet7MWtkMVINuoNIDac8D', 'created_at': 1723207781, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPavMj:ckpt-step-200', 'fine_tuning_job_id': 'ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', 'metrics': {'step': 200, 'train_loss': 7.321757493627956e-06, 'train_mean_token_accuracy': 1.0, 'valid_loss': 0.0057771366494924915, 'valid_mean_token_accuracy': 0.9974093264248705}, 'step_number': 200}, {'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_vm20GTYRyKsuvrVjzFECbquK', 'created_at': 1723207598, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPavaa:ckpt-step-100', 'fine_tuning_job_id': 'ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', 'metrics': {'step': 100, 'train_loss': 0.0066589792259037495, 'train_mean_token_accuracy': 0.996515691280365, 'valid_loss': 4.8786846559439135e-06, 'valid_mean_token_accuracy': 1.0}, 'step_number': 100}], 'has_more': False, 'first_id': 'ftckpt_nuaEKibogmcsHp3FUBLfgbDs', 'last_id': 'ftckpt_vm20GTYRyKsuvrVjzFECbquK'}
  """


  # 微调结束后，获取微调的job events信息
  """
  client = OpenAI(
    api_key="sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A",
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
      "Authorization": f"Bearer sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A"
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
  """
  最新一次的check状态
  List 10 fine-tuning jobs:
  SyncCursorPage[FineTuningJob](data=[FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='running', trained_tokens=None, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[]), FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', finished_at=1723208013, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-olGk5MMJhcAPQWI4y0oW5fIj'], status='succeeded', trained_tokens=379446, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])], object='list', has_more=False)
  
  Retrieve the state of a fine-tune:ftjob-j6mDj7MYs1O9bp3D1oPw3rIk
  FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='running', trained_tokens=None, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[])
  
  List up to 10 events from a fine-tuning job:ftjob-j6mDj7MYs1O9bp3D1oPw3rIk
  SyncCursorPage[FineTuningJobEvent](data=[FineTuningJobEvent(id='ftevent-695C31Btj1ELJyKOkQA63K2K', created_at=1723885748, level='info', message='Fine-tuning job started', object='fine_tuning.job.event', data=None, type='message'), FineTuningJobEvent(id='ftevent-cLCJwDjiHrL6tbBWQA7XoVvy', created_at=1723885745, level='info', message='Files validated, moving job to queued state', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-wGwSHqx3hOwtr3luD3ccOt4j', created_at=1723885698, level='info', message='Validating training file: file-8QiUEBvXynmHVMNY36Ud7iHf and validation file: file-Zn0ACseWyn6wSuSJJctp7B1O', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-U03aoOGFufH7l95h9eVZ9sln', created_at=1723885698, level='info', message='Created fine-tuning job: ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', object='fine_tuning.job.event', data={}, type='message')], object='list', has_more=False)


  完成后查询结果：fine_tuned_model != None
  List 10 fine-tuning jobs:
  SyncCursorPage[FineTuningJob](data=[FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR', finished_at=1723886491, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-EvKrlLqCuTD6FmHonxKuJQzy'], status='succeeded', trained_tokens=170589, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[]), FineTuningJob(id='ftjob-mJP5PgIEaFxN4jpMHIcCKMmQ', created_at=1723205158, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9uJPbR69', finished_at=1723208013, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-olGk5MMJhcAPQWI4y0oW5fIj'], status='succeeded', trained_tokens=379446, training_file='file-F5ONQvl0svALeKfomy71T8rg', validation_file='file-ctERcdOSaxu2iYywFNTzpQs7', user_provided_suffix='pinolo-mutate-llm', seed=2069133622, estimated_finish=None, integrations=[])], object='list', has_more=False)
  
  Retrieve the state of a fine-tune:ftjob-j6mDj7MYs1O9bp3D1oPw3rIk
  FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR', finished_at=1723886491, hyperparameters=Hyperparameters(n_epochs=3, batch_size=1, learning_rate_multiplier=1.8), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=['file-EvKrlLqCuTD6FmHonxKuJQzy'], status='succeeded', trained_tokens=170589, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[])
  
  List up to 10 events from a fine-tuning job:ftjob-j6mDj7MYs1O9bp3D1oPw3rIk
  SyncCursorPage[FineTuningJobEvent](data=[FineTuningJobEvent(id='ftevent-nBnZf4jjZrVM90mBlQNPquPk', created_at=1723886498, level='info', message='The job has successfully completed', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-JPGJWr6i5p1K4LIIZfwqdBms', created_at=1723886493, level='info', message='New fine-tuned model created: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-P3a5lYKGfZvnqDUuH3mCLfAJ', created_at=1723886493, level='info', message='Checkpoint created at step 160 with Snapshot ID: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umLQq:ckpt-step-160', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-nMJnfFvBac3Pyw5s7zActUXn', created_at=1723886493, level='info', message='Checkpoint created at step 80 with Snapshot ID: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umRGJ:ckpt-step-80', object='fine_tuning.job.event', data={}, type='message'), FineTuningJobEvent(id='ftevent-TDcK6kP2mRRiof75k5YpPXzb', created_at=1723886483, level='info', message='Step 240/240: training loss=0.00, validation loss=0.00, full validation loss=0.00', object='fine_tuning.job.event', data={'step': 240, 'train_loss': 3.4570693969726562e-06, 'valid_loss': 2.2545838967347758e-05, 'total_steps': 240, 'full_valid_loss': 0.004403916553852115, 'train_mean_token_accuracy': 1.0, 'valid_mean_token_accuracy': 1.0, 'full_valid_mean_token_accuracy': 0.8761806558053207}, type='metrics'), FineTuningJobEvent(id='ftevent-ml9jt0iUDwi10K1KBuNOtXpc', created_at=1723886465, level='info', message='Step 239/240: training loss=0.00', object='fine_tuning.job.event', data={'step': 239, 'train_loss': 1.258850079466356e-05, 'total_steps': 240, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-g1uLxyxnC2NBBcv98gzmQ57v', created_at=1723886463, level='info', message='Step 238/240: training loss=0.00', object='fine_tuning.job.event', data={'step': 238, 'train_loss': 1.705848717392655e-06, 'total_steps': 240, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-tS0B4BxGnZ40OaJm42tQ66e2', created_at=1723886460, level='info', message='Step 237/240: training loss=0.00', object='fine_tuning.job.event', data={'step': 237, 'train_loss': 2.736069745878922e-06, 'total_steps': 240, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-CNnVw24vyRDTDGJHC4SGePV6', created_at=1723886458, level='info', message='Step 236/240: training loss=0.00', object='fine_tuning.job.event', data={'step': 236, 'train_loss': 7.722277587163262e-06, 'total_steps': 240, 'train_mean_token_accuracy': 1.0}, type='metrics'), FineTuningJobEvent(id='ftevent-jzS87Ua53giIDqovqLnZT76q', created_at=1723886456, level='info', message='Step 235/240: training loss=0.00', object='fine_tuning.job.event', data={'step': 235, 'train_loss': 1.3411770396487555e-06, 'total_steps': 240, 'train_mean_token_accuracy': 1.0}, type='metrics')], object='list', has_more=True)
  """

  # checkpoints
  url = "https://api.openai.com/v1/fine_tuning/jobs/ftjob-j6mDj7MYs1O9bp3D1oPw3rIk/checkpoints"
  headers = {
    "Authorization": f"Bearer sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A"
  }
  response = requests.get(url, headers=headers)
  # print(response.json())
  """
  {'object': 'list', 'data': [{'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_uWjgiFOd5wyKuEIFH2MSG5Ud', 'created_at': 1723886468, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR', 'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', 'metrics': {'step': 240, 'train_loss': 3.4570693969726562e-06, 'train_mean_token_accuracy': 1.0, 'valid_loss': 2.2545838967347758e-05, 'valid_mean_token_accuracy': 1.0}, 'step_number': 240}, {'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_PNFULGYpE6LPdomNTM2IJVL7', 'created_at': 1723886272, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umLQq:ckpt-step-160', 'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', 'metrics': {'step': 160, 'train_loss': 3.60225276381243e-05, 'train_mean_token_accuracy': 1.0, 'valid_loss': 0.00014691037426662817, 'valid_mean_token_accuracy': 1.0}, 'step_number': 160}, {'object': 'fine_tuning.job.checkpoint', 'id': 'ftckpt_YR0QObTiHLsH1cNgbEp5DN1i', 'created_at': 1723886072, 'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umRGJ:ckpt-step-80', 'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', 'metrics': {'step': 80, 'train_loss': 0.0028356313705444336, 'train_mean_token_accuracy': 1.0, 'valid_loss': 0.0011850879149718986, 'valid_mean_token_accuracy': 0.9986244841815681}, 'step_number': 80}], 'has_more': False, 'first_id': 'ftckpt_uWjgiFOd5wyKuEIFH2MSG5Ud', 'last_id': 'ftckpt_YR0QObTiHLsH1cNgbEp5DN1i'}
  """


  # 微调结束后，获取微调的job events信息

  client = OpenAI(
    api_key="sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A",
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

