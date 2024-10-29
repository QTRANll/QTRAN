## Preparing your dataset
### Training/Testing Dataset说明
1. DB：mutate llm针对postgres的变异微调
2. 变异策略：
* 先测能找到例子的八种变异策略，选其中数据量充足的几种策略进行测试：FixMDistinctL，FixMCmpOpU，FixMHaving1U，FixMOn1U
* pinolo在mysql-like中的18种变异策略，同样适用于postgres
3. 微调数据集来源：pinolo，先用mysql转postgres（transfer llm）的结果sql语句作为训练集和测试集。
4. 数据集选取
* 选取output1-4/mysql的简化后的（"originalSqlsim"，"mutatedSqlsim"）transfer为postgres语句
* 数据集大小：training（20 x 4）+testing（20 x 4）
* 数据集每条sample包括：dbname，mutate name，mutate stragegy，original sql，mutated sqls（origin sql可能包括多个可变异子句）及对应的oracles（IsUpper）
5. 评估
	* 微调过程中评估：openai官方评估mutate llm效果，上传测试集进行效果评估，记录微调的过程结果
	* Eval工具：评估mutate llm，选择合适的eval-template进行修改并添加注册（costom-eval.md），添加需要的matrics(eval /metrics.py，在eval_sample中的evals.record.record_metrics(）中进行添加）
	* 变异正确性，变异的oracle（IsUpper）正确性，变异后语句的执行成功率，真实结果是否满足oracle（检测bug）


### Training Dataset 和Testing Dataset 的获取
1. 有18种变异策略([[mutators_PINOLO_postgres]])。
* 变异策略：先测以下几种，FixMDistinctL，FixMCmpOpU，FixMHaving1U，FixMOn1U
* DB：postgres
```
# mysql
FixMDistinctU:DISTINCT true -> false，变异简单，暂不包括 
FixMDistinctL:25527+26184+25969+26208，包括
FixMCmpOpU:930+902+892+853，包括
FixMCmpOpL:5+4+5+5，数据量少，和FixMCmpOpU原理相近，暂不包括
FixMUnionAllU:
FixMUnionAllL:
FixMInNullU:9+7+3+14，数量少，暂不包括
FixMWhere1U:3+6+5+5，数量少，暂不包括
FixMWhere0L:2+1，数据量少，和FixMWhere1U原理相近，暂不包括
FixMHaving1U:14682+15207+14920+15072，包括
FixMHaving0L:1，数据量少，和FixMHaving1U原理相近，暂不包括
FixMOn1U:454+433+457+465，包括
FixMOn0L:数据量少，和FixMOn1U原理相近，暂不包括
FixMRmUnionAllL:
RdMLikeU
RdMLikeL
RdMRegExpU
RdMRegExpL
```
2. mysql->postgres得到训练集+测试集：postgres_training_testing_dataset_raw1.0.jsonl
* transfer llm：mysql->postgres，FixMDistinctL，FixMCmpOpU，FixMHaving1U，FixMOn1U各40条数据
* 训练集（postgres_training_dataset1.0.jsonl）：添加postgres的origin sql变异后的mutated sql+Flag；添加用于训练的mutated sqls（origin sql可能包括多个可变异子句）及对应的Flags（用于计算出IsUpper）
* 测试集（postgres_testing_dataset1.0.jsonl）：添加postgres的origin sql变异后的mutated sql+Flag；添加用于测试的mutated sqls（origin sql可能包括多个可变异子句）及对应的Flags（用于计算出IsUpper）
* 验证postgres的training data和testing data中origin sql和mutated sqls的正确性：分别运行origin sql和mutated sql语句，是否可执行（语法正确性），是否符合变异策略（变异正确性）
* 人工修正数据集中的flag
```
1. FixMCmpOpU
* training:4（CASE内的不算），0（flag有疑问），7（<>不算），15（<>不算）
* testing:24（>=不算,!=不算），26（<=不算），27（>=不算）
```

3. training data和testing data中4种变异策略的system message

```
* FixMDistinctL: Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy "FixMDistinctL" :"Distinct false -> true".This mutate strategy will mutate all SELECT clauses in the seed SQL once a time and give the positive "flag" of each clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent "flag"=False). For each SELECT clause, it will change "DISTINCT" from false to true, and provide the positive "flag" for the clause.Organize answer in a JSON list format.


* FixMCmpOpU: Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy "FixMCmpOpU": "a {>|<|=} b -> a {>=|<=|>=} b".This mutate strategy will mutate all Binary operation expressions and Comparison subquery expressions in the seed SQL once a time and give the positive "flag" of each expression (such as NOT,NOT IN,IS FALSE, <>, etc. which represent "flag"=False). For each Binary operation expression or Comparison subquery expression, it will change ">" to ">=","<" to "<=","=" to ">=", and provide the positive "flag" for the expression.Organize answer in a JSON list format.


* FixMHaving1U: Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy "FixMHaving1U" : "HAVING xxx -> HAVING 1".This mutate strategy will mutate all HAVING clauses in the seed SQL once a time and give the positive "flag" of each HAVING clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent "flag"=False). For each HAVING clause, it will change the condition of HAVING clause to "1", and provide the positive "flag" for the HAVING clause.Organize answer in a JSON list format.


* FixMOn1U: Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy "FixMOn1U":"ON xxx -> ON 1".This mutate strategy will mutate all ON clauses in the seed SQL once a time and give the positive "flag" of each ON clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent "flag"=False). For each ON clause, it will change the condition of ON clause to "1", and provide the positive "flag" for the ON clause.Organize answer in a JSON list format.
```

4. 形成格式化的training data和testing data，格式如下
* 在system里加一句角色扮演提示词以添加数据库类型信息
``` JSON
role_prompt = "You are an expert in " + db_name + " statement mutation."
single_train_data = {  
    "messages": [  
        {"role": "system", "content": str(role_prompt + 
        mutate_strategy_illustration[key])},  
        {"role": "user", "content": str(item["originalSqlsim_postgres"])},  
        {"role": "assistant", "content":       
          str(item["mutatedSqlsim_postgres_training"])}  
    ]  
}
```

5. 检查training data的格式并预测成本 [Check data formatting](https://platform.openai.com/docs/guides/fine-tuning/check-data-formatting)
  It checks for format errors, provides basic statistics, and estimates token counts for fine-tuning costs.
``` JSON
Num examples: 80
First example:
{'role': 'system', 'content': 'You are an expert in PostgresSQL statement mutation.Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy "FixMDistinctL" :"Distinct false -> true".This mutate strategy will mutate all SELECT clauses in the seed SQL once a time and give the positive "flag" of each clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent "flag"=false). For each SELECT clause, it will change "DISTINCT" from false to true, and provide the positive "flag" for the clause.Organize answer in a JSON list format.'}
{'role': 'user', 'content': "SELECT (EXTRACT(HOUR FROM TIME '06:04:16')) AS f1, (f9) AS f2 FROM (SELECT col_bigint_key_unsigned AS f10, col_float_key_unsigned AS f8, col_char_20_undef_signed AS f11 FROM table_3_utf8_undef) AS t2 NATURAL JOIN (SELECT (TO_TIMESTAMP(f13::text, 'YYYYMMDD') + INTERVAL '1 day') AS f7, (0) AS f12, (DATE '2007-02-13' + INTERVAL '1 month') AS f9 FROM (SELECT col_bigint_undef_unsigned AS f13, col_float_undef_signed AS f14, col_float_undef_signed AS f15 FROM table_7_utf8_undef) AS t3) AS t4"}
{'role': 'assistant', 'content': '[{\'mutated sql\': "SELECT DISTINCT (EXTRACT(HOUR FROM TIME \'06:04:16\')) AS f1, (f9) AS f2 FROM (SELECT col_bigint_key_unsigned AS f10, col_float_key_unsigned AS f8, col_char_20_undef_signed AS f11 FROM table_3_utf8_undef) AS t2 NATURAL JOIN (SELECT (TO_TIMESTAMP(f13::text, \'YYYYMMDD\') + INTERVAL \'1 day\') AS f7, (0) AS f12, (DATE \'2007-02-13\' + INTERVAL \'1 month\') AS f9 FROM (SELECT col_bigint_undef_unsigned AS f13, col_float_undef_signed AS f14, col_float_undef_signed AS f15 FROM table_7_utf8_undef) AS t3) AS t4", \'flag\': True}, {\'mutated sql\': "SELECT (EXTRACT(HOUR FROM TIME \'06:04:16\')) AS f1, (f9) AS f2 FROM (SELECT DISTINCT col_bigint_key_unsigned AS f10, col_float_key_unsigned AS f8, col_char_20_undef_signed AS f11 FROM table_3_utf8_undef) AS t2 NATURAL JOIN (SELECT (TO_TIMESTAMP(f13::text, \'YYYYMMDD\') + INTERVAL \'1 day\') AS f7, (0) AS f12, (DATE \'2007-02-13\' + INTERVAL \'1 month\') AS f9 FROM (SELECT col_bigint_undef_unsigned AS f13, col_float_undef_signed AS f14, col_float_undef_signed AS f15 FROM table_7_utf8_undef) AS t3) AS t4", \'flag\': True}, {\'mutated sql\': "SELECT (EXTRACT(HOUR FROM TIME \'06:04:16\')) AS f1, (f9) AS f2 FROM (SELECT col_bigint_key_unsigned AS f10, col_float_key_unsigned AS f8, col_char_20_undef_signed AS f11 FROM table_3_utf8_undef) AS t2 NATURAL JOIN (SELECT DISTINCT (TO_TIMESTAMP(f13::text, \'YYYYMMDD\') + INTERVAL \'1 day\') AS f7, (0) AS f12, (DATE \'2007-02-13\' + INTERVAL \'1 month\') AS f9 FROM (SELECT col_bigint_undef_unsigned AS f13, col_float_undef_signed AS f14, col_float_undef_signed AS f15 FROM table_7_utf8_undef) AS t3) AS t4", \'flag\': True}, {\'mutated sql\': "SELECT (EXTRACT(HOUR FROM TIME \'06:04:16\')) AS f1, (f9) AS f2 FROM (SELECT col_bigint_key_unsigned AS f10, col_float_key_unsigned AS f8, col_char_20_undef_signed AS f11 FROM table_3_utf8_undef) AS t2 NATURAL JOIN (SELECT (TO_TIMESTAMP(f13::text, \'YYYYMMDD\') + INTERVAL \'1 day\') AS f7, (0) AS f12, (DATE \'2007-02-13\' + INTERVAL \'1 month\') AS f9 FROM (SELECT DISTINCT col_bigint_undef_unsigned AS f13, col_float_undef_signed AS f14, col_float_undef_signed AS f15 FROM table_7_utf8_undef) AS t3) AS t4", \'flag\': True}]'}
No errors found
Num examples missing system message: 0
Num examples missing user message: 0

#### Distribution of num_messages_per_example:
min / max: 3, 3
mean / median: 3.0, 3.0
p5 / p95: 3.0, 3.0

#### Distribution of num_total_tokens_per_example:
min / max: 363, 1666
mean / median: 707.4, 552.0
p5 / p95: 409.8, 1302.0000000000002

#### Distribution of num_assistant_tokens_per_example:
min / max: 101, 1281
mean / median: 364.5, 189.5
p5 / p95: 110.9, 938.6000000000001

0 examples may be over the 16,385 token limit, they will be truncated during fine-tuning
Dataset has ~56592 tokens that will be charged for during training
By default, you'll train for 3 epochs on this dataset
By default, you'll be charged for ~169776 tokens
```


### [Upload a training file and a testing file](https://platform.openai.com/docs/guides/fine-tuning/upload-a-training-file)

FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk')
```
"""  
训练集：  
FileObject(id='file-8QiUEBvXynmHVMNY36Ud7iHf', bytes=181185, created_at=1723885693, filename='postgres_training_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)  
测试集：  
FileObject(id='file-Zn0ACseWyn6wSuSJJctp7B1O', bytes=165365, created_at=1723885695, filename='postgres_testing_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)  
微调任务：  
FineTuningJob(id='ftjob-j6mDj7MYs1O9bp3D1oPw3rIk', created_at=1723885698, error=Error(code=None, message=None, param=None), fine_tuned_model=None, finished_at=None, hyperparameters=Hyperparameters(n_epochs='auto', batch_size='auto', learning_rate_multiplier='auto'), model='gpt-4o-mini-2024-07-18', object='fine_tuning.job', organization_id='org-15Epzv4bAIKOsvoxUezfHEZX', result_files=[], status='validating_files', trained_tokens=None, training_file='file-8QiUEBvXynmHVMNY36Ud7iHf', validation_file='file-Zn0ACseWyn6wSuSJJctp7B1O', user_provided_suffix='pinolo-mutate-llm', seed=1960319362, estimated_finish=None, integrations=[])  
"""
```
## [Create a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model)
 fine_tuned_model='ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR'

## [Use a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/use-a-fine-tuned-model)

**当作业成功完成时,您在retrieve the job details时会看到 `fine_tuned_model` 字段已填充了模型名称。**

在您的作业完成之后,该模型应该立即可用于推理使用。在某些情况下,您的模型可能需要几分钟的时间才能准备好处理请求。如果对您的模型的请求超时或找不到模型名称,这可能是因为您的模型仍在加载中。如果出现这种情况,请在几分钟后再试。

``` Python
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="ft:gpt-4o-mini:my-org:custom_suffix:id",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)
print(completion.choices[0].message)
```

## [Use a checkpointed model](https://platform.openai.com/docs/guides/fine-tuning/use-a-checkpointed-model)

除了在每个微调作业结束时创建最终的微调模型外，OpenAI还将在每个训练纪元结束时为您创建一个完整的模型检查点。这些检查点本身就是完整的模型，可以在我们的完成和聊天完成端点中使用。检查点是有用的，因为它们可能提供在模型经历过拟合之前的微调模型的版本。

要进入这些检查点，

1. 等待作业成功：可通过查询作业状态进行验证 [querying the status of a job.](https://platform.openai.com/docs/api-reference/fine-tuning/retrieve)。
2. 使用您的微调作业ID查询检查点端点 [Query the checkpoints endpoint](https://platform.openai.com/docs/api-reference/fine-tuning/list-checkpoints) ，以访问微调作业的模型检查点列表。


对于每个检查点对象，您将看到fine_tuned_model_checkpoint字段填充了模型检查点的名称。现在，您可以像使用最终的微调模型一样使用该模型。

本任务中得到的检查点信息如下
``` Python
{  
  'object': 'list',  
  'data': [  
    {  
      'object': 'fine_tuning.job.checkpoint',  
      'id': 'ftckpt_uWjgiFOd5wyKuEIFH2MSG5Ud',  
      'created_at': 1723886468,  
      'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR',  
      'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk',  
      'metrics': {  
        'step': 240,  
        'train_loss': 3.4570693969726562e-06,  
        'train_mean_token_accuracy': 1.0,  
        'valid_loss': 2.2545838967347758e-05,  
        'valid_mean_token_accuracy': 1.0  
      },  
      'step_number': 240  
    },  
    {  
      'object': 'fine_tuning.job.checkpoint',  
      'id': 'ftckpt_PNFULGYpE6LPdomNTM2IJVL7',  
      'created_at': 1723886272,  
      'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umLQq:ckpt-step-160',  
      'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk',  
      'metrics': {  
        'step': 160,  
        'train_loss': 3.60225276381243e-05,  
        'train_mean_token_accuracy': 1.0,  
        'valid_loss': 0.00014691037426662817,  
        'valid_mean_token_accuracy': 1.0  
      },  
      'step_number': 160  
    },  
    {  
      'object': 'fine_tuning.job.checkpoint',  
      'id': 'ftckpt_YR0QObTiHLsH1cNgbEp5DN1i',  
      'created_at': 1723886072,  
      'fine_tuned_model_checkpoint': 'ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umRGJ:ckpt-step-80',  
      'fine_tuning_job_id': 'ftjob-j6mDj7MYs1O9bp3D1oPw3rIk',  
      'metrics': {  
        'step': 80,  
        'train_loss': 0.0028356313705444336,  
        'train_mean_token_accuracy': 1.0,  
        'valid_loss': 0.0011850879149718986,  
        'valid_mean_token_accuracy': 0.9986244841815681  
      },  
      'step_number': 80  
    }  
  ],  
  'has_more': False,  
  'first_id': 'ftckpt_uWjgiFOd5wyKuEIFH2MSG5Ud',  
  'last_id': 'ftckpt_YR0QObTiHLsH1cNgbEp5DN1i'  
}
```

每个检查点将指定其:
* `step_number` :创建检查点的步骤(其中每个epoch是训练集中的步数除以批处理大小)
* `metrics`:一个对象，包含在创建检查点时的步骤中微调作业的指标。
目前，只有作业的最后3个epoch的检查点被保存并可供使用。我们计划在不久的将来发布更复杂和灵活的检查点策略。


## [Analyzing your fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/analyzing-your-fine-tuned-model)

我们提供以下经过培训过程计算的培训指标:
1. train loss：
- 定义: 在每个步骤期间计算的一小批训练数据的损失值
- 内涵: 指示模型在当前训练数据上的误差或损失。较低的 train loss 意味着模型在训练数据上表现良好。
2. valid loss
- 定义：在每个训练步骤期间，对一小批验证数据计算的损失值。
- 内涵：表示模型在当前验证数据小批次上的误差或损失。较低的 `valid loss` 表明模型在这些验证数据上的表现较好。不过这个值仅基于小批量验证数据，而非整个验证集。
3. full_valid_loss
- 定义：在每个epoch结束时，对整个验证数据集（完全有效分割）计算的损失值。
- 内涵：这个指标是跟踪模型整体性能的最准确指标之一。它表示模型在完整验证集上的整体误差或损失。较低的 `full_valid_loss` 意味着模型在整个验证数据上表现良好。
4. train_mean_token_accuracy
- 定义：在每个训练步骤期间，对一小批训练数据计算的平均令牌准确性。
- 内涵：这个指标表示模型在当前步骤的小批量训练数据上的平均预测准确性。较高的 `train_mean_token_accuracy` 表明模型在这些训练数据上的预测准确度高。
5. valid_mean_token_accuracy
- 定义：在每个训练步骤期间，对一小批验证数据计算的平均令牌准确性。
- 内涵：这个指标表示模型在当前验证数据小批次上的平均预测准确性。较高的 `valid_mean_token_accuracy` 表明模型在这些验证数据上的预测准确度高。这个值仅基于小批验证数据。
6. full_valid_mean_token_accuracy
- 定义：在每个epoch结束时，对整个验证数据集（完全有效分割）计算的平均令牌准确性。
- 内涵：它表示模型在完整验证集上的平均预测准确性。较高的 `full_valid_mean_token_accuracy` 表明模型在整个验证数据上的预测准确度高，但通常会低于小批量计算的准确性。


Valid loss 和valid token accuracy以两种不同的方式计算——在每个步骤期间对一小批数据进行计算，以及在每个epoch结束时对完全有效分割进行计算（on a small batch of the data during each step, and on the full valid split at the end of each epoch）。**完全有效丢失和完全有效令牌准确性（The full valid loss and full valid token accuracy）指标是跟踪模型整体性能的最准确指标**。**这些统计数据是为了提供一个健全的检查，训练进行顺利：(损失loss应该减少，令牌准确性token accuracy应该提高)**。 **当一个活动的微调作业正在运行时，您可以查看一个事件对象，其中包含一些有用的指标:**

``` Python
{  
    "id": "ftevent-TDcK6kP2mRRiof75k5YpPXzb",  
    "created_at": 1723886483,  
    "level": "info",  
    "message": "Step 240/240: training loss=0.00, validation loss=0.00, full validation loss=0.00",  
    "object": "fine_tuning.job.event",  
    "data": {  
        "step": 240,  
        "train_loss": 3.4570693969726562e-06,  
        "valid_loss": 2.2545838967347758e-05,  
        "total_steps": 240,  
        "full_valid_loss": 0.004403916553852115,  
        "train_mean_token_accuracy": 1.0,  
        "valid_mean_token_accuracy": 1.0,  
        "full_valid_mean_token_accuracy": 0.8761806558053207  
    },  
    "type": "metrics"  
}
```
