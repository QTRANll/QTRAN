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


## Evals
**虽然度量标准可以提供帮助，但是评估来自微调模型的样本可以提供最相关的模型质量感觉。我们建议在测试集上从基本模型和微调模型生成样本，并并排比较样本。** 理想情况下，测试集应该包括您可能在生产用例中发送给模型的输入的完整分布。**如果手动评估太耗时，可以考虑使用我们的eval库[Evals library](https://github.com/openai/evals)来自动化未来的评估。**
### Prepare Eval testing dataset 
参考
[[Evals_Data_Format_README]]
[[How To Best Leverage OpenAI’s Evals Framework#Building Samples]]
[[How To Best Leverage OpenAI’s Evals Framework#How Does the Eval Framework Work?]] 
1. samples的外观如下，用测试集数据构造下面的 **samples.jsonl** 文件，并存放在`evals/registry/data/pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl`和`postgres_eval_dataset_plus_formatted1.0.jsonl` 中：**特别注意的是**
* eval的测试数据集有两种：一种的ideal答案为key="mutatedSqlsim_postgres"的数据（只有一条标准答案），另一种ideal答案为key="mutatedSqlsim_postgres_training"的数据（包含所有变异可能）。对于前者使用自定义模板JsonMatch，对于后者已有模板JsonMatch
* 要使用后续的eval相关模板，需要将单条sample设置为dict类型，将"ideal"设置为list格式
```json
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "Once upon a "}], "ideal": ["time"]}
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "The first US president was "}], "ideal": ["George Washington"]}
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "OpenAI was founded in 20"}], "ideal": ["15"]}
```
2. sample.json
* `postgres_eval_dataset_formatted1.0.jsonl`：db="postgres"，key="mutatedSqlsim_postgres"
* `postgres_eval_dataset_plus_formatted1.0.jsonl`：db="postgres"，key="mutatedSqlsim_postgres_training"
* `mysql_eval_dataset_formatted1.0.jsonl`：db="mysql"。key="mutatedSqlsim_postgres"

### Eval测试代码编写
* 主要参考[[Mastering OpenAI’s ‘evals’_A Deep Dive into Evaluating LLMs]]
* 结合以下两种现有模板为mutate llm（pinolo）编写自定义的eval模板：[`basic/fuzzy_match.py:FuzzyMatch`](../evals/elsuite/basic/fuzzy_match.py): `any([(a in b or b in a) for b in B])`，和[basic/json_match.py:JsonMatch ](../evals/elsuite/basic/json_match.py)，具体参考[[eval-templates#Basic eval templates]]
* `basic/fuzzy_match.py:FuzzyMatch`的尝试实现：[[Mutate LLM Fine-tuning(PINOLO_postgres,FuzzyMatch)]]
#### Section0: 设置环境变量和注册completion-fn
1. 要运行eval，你需要设置并指定你的[OpenAI API密钥](https://platform.openai.com/account/api-keys)。获取API密钥后，使用['OPENAI_API_KEY '环境变量](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key)指定它。参考以下链接在Edit Configuration中添加环境变量： https://blog.csdn.net/qq_36797973/article/details/122096750
2. 注册要使用的语言模型的接口，参考[[completion-fns#Registering Completion Functions]].将`eval/registry/completion_fns`中的Completion Functions注册为`yaml`文件(该yaml文件位于`evals\registry\completion_fns`)。下面介绍如何注册已有语言模型和自行微调的模型。
* 注册已有的openai模型：在`evals/registry.py`中的is_chat_model(model_name: str)函数中的CHAT_MODEL_NAMES数组中进行添加
```
CHAT_MODEL_NAMES = {"gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k", "gpt-4o-mini"}
```
* 注册自行微调的模型：先将Resgistry的make_completion_fn方法中的`# spec.args["registry"] = self`注释掉（因为这里报错，不涉及参数"resgistry"），然后在.yaml中添加的补全函数"gpt-4o-mini"的注册信息，
```yaml
openai/pinolo-mutate-llm-postgres:
  class: evals.completion_fns.openai:OpenAIChatCompletionFn
  args:
    model: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR
    api_base: "https://api.openai.com/v1"
    api_key: "sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A"
```

`openai/pinolo-mutate-llm-postgres`:这是用于访问`oaieval`补全函数的顶级键。
`class`:这是你实现补全函数协议的路径。该类需要在python环境中可导入。
`args`:这些是在实例化完成函数时传递给它的参数。

注意：报错`ModuleNotFoundError: No module named 'langchain_community'` 的解决方法如下 https://stackoverflow.com/questions/77998568/langchain-modulenotfounderror-no-module-named-langchain-community

#### Section 1: Specification File
1. `postgres_eval_dataset_formatted1.0.jsonl`：db="postgres"，key="mutatedSqlsim_postgres"

`evals/registry/evals/JsonMatch_pinolo_mutate_llm_postgres.yaml`中（注意：samples_jsonl的隐藏前缀为`evals/registry/data/`）。
```
JsonMatch_pinolo_mutate_llm_postgres:  
  id: JsonMatch_pinolo_mutate_llm_postgres.test.v1  
  description: evaluate the mutate llm for postgres with four mutate strategies.  
  metrics: [accuracy,f1_score,boostrap_std]  
JsonMatch_pinolo_mutate_llm_postgres.test.v1:  
  class: evals.elsuite.pinolo_mutate_llm.json_match:JsonMatch  
  args:  
    samples_jsonl: pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl
```

2. `postgres_eval_dataset_plus_formatted1.0.jsonl`：db="postgres"，key="mutatedSqlsim_postgres_training"
`evals/registry/evals/JsonMatch_basic_mutate_llm_postgres.yaml`中。

```
JsonMatch_basic_mutate_llm_postgres:  
  id: JsonMatch_basic_mutate_llm_postgres.test.v1  
  description: evaluate the mutate llm for postgres with four mutate strategies.  
  metrics: [accuracy,f1_score,boostrap_std]  
JsonMatch_basic_mutate_llm_postgres.test.v1:  
  class: evals.elsuite.basic.json_match:JsonMatch  
  args:  
    samples_jsonl: pinolo_mutate_llm/postgres/postgres_eval_dataset_plus_formatted1.0.jsonl
```

3. `mysql_eval_dataset_formatted1.0.jsonl`：db="mysql"。key="mutatedSqlsim_postgres"
`evals/registry/evals/JsonMatch_pinolo_mutate_llm_mysql.yaml`中（注意：samples_jsonl的隐藏前缀为`evals/registry/data/`）。
```
JsonMatch_pinolo_mutate_llm_mysql:  
  id: JsonMatch_pinolo_mutate_llm_mysql.test.v1  
  description: evaluate the mutate llm for mysql with four mutate strategies.  
  metrics: [accuracy,f1_score,boostrap_std]  
JsonMatch_pinolo_mutate_llm_mysql.test.v1:  
  class: evals.elsuite.pinolo_mutate_llm.json_match:JsonMatch  
  args:  
    samples_jsonl: pinolo_mutate_llm/mysql/mysql_eval_dataset_formatted1.0.jsonl
```


#### Section 2: Specification Objects
使用 YAML 文件来构造`evals`中的 Specification object，该对象将用于`evals.elsuite`中定义的评估工作流。

`Registry`类用于 
1） 检索Specification File的信息
2） 根据这些信息构造 Specification object。

调用以下方法来根据Specification File的信息获取 Specification object。

``` Python
Registry().get_eval_set(name) -> evals.base.EvalSetSpec  
Registry().get_eval(name) -> Evals.base.EvalSpec
```

在我们的示例中，我们可以调用以下代码行：

``` Python
# define the arguments:  
args = {  
    "completion_fn": "openai/pinolo-mutate-llm-postgres",  
    "eval": "FuzzyMatch_pinolo_mutate_llm_postgres",  
    "cache": True,  
    "seed": 20220722  
}  
args = SimpleNamespace(**args)  
  
# evaluation specification  
registry = Registry()  
eval_spec = registry.get_eval(args.eval)  
print(eval_spec)  

# EvalSpec(cls='evals.elsuite.pinolo_mutate_llm.json_match:JsonMatch', registry_path=WindowsPath('D:/PycharmFiles/evals-main/evals/registry'), args={'samples_jsonl': 'pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl'}, key='JsonMatch_pinolo_mutate_llm_postgres.test.v1', group='JsonMatch_pinolo_mutate_llm_postgres')
```
#### Section 3: Evaluation Protocols
评估协议定义了如何处理响应或完成（responses or completions），以及如何计算最终的准确性指标。`evals.Eval` 定义此类协议的接口。

获得规范对象 (`EvalSpec`) 后，调用方法`Registry().get_class`来获取继承自`evals.Eval`的具体类。

``` Python
Registry().get_class(spec: EvalSpec) -> evals.Eval
```

在我们的示例中，与评估变量`JsonMatch_pinolo_mutate_llm_postgres.test.v1`关联的类`JsonMatch`来自模块`evals.elsuite.pinolo_mutate_llm.json_match`，如文件`.yaml`中的最后一行所定义。因此，它将输出一个对象`evals.elsuite.pinolo_mutate_llm.json_match.JsonMatch`，如下所示。

`functools.partial`将保持类和`EvalSpec`类相同，并在对象中定义了部分`EvalSpec`类中定义的参数。

``` Python
# eval object  
eval_class = registry.get_class(eval_spec)  
print(eval_class)  

# functools.partial(<class 'evals.elsuite.pinolo_mutate_llm.json_match.JsonMatch'>, samples_jsonl='pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl')
```

然后，可以使用这个类来实例化具有指定完成函数（completion functions）的对象。
``` Python
openai.api_key = os.environ.get("OPENAI_API_KEY")  
completion_fn_instance = registry.make_completion_fn(args.completion_fn)  
eval: Eval = eval_class(  
    completion_fns=[completion_fn_instance],  
    eval_registry_path=eval_spec.registry_path,  
    samples_jsonl=eval_spec.args["samples_jsonl"],  
    name=eval_spec.key,    
    seed=args.seed,  
    max_tokens=4000  
)
```

#### Section 4: Running Evaluation
每个`evals.Eval`类都需要实现 `eval_sample`和`run`方法。只需调用`evals.Eval.run`以启动该过程即可。

那么，我们先来看看json_match方法的实现。

``` Python
class JsonMatch(evals.Eval):  
    """  
    比较一个json格式的completion（json格式的列表，列表内可能有多个dict）和一个json格式的ideal answer（json格式的列表，列表中只有一个dict）  
    解码后的 JSON 对象逐元素进行比较,必须完全匹配。  
    """  
    def __init__(  
            self,  
            completion_fns: list[CompletionFn],  
            samples_jsonl: str,  
            *args: Any,  
            max_tokens: int = 512,  # Increase this for longer JSON completions  
            **kwargs: Any,  
    ):  
        super().__init__(completion_fns, *args, **kwargs)  
        assert len(completion_fns) == 1, "JsonMatch only supports one completion fn"  
        self.max_tokens = max_tokens  
        self.samples_jsonl = samples_jsonl  
  
    ...
  
    def run(self, recorder: RecorderBase) -> Dict[str, float]:  
        samples = self.get_samples()  
        self.eval_all_samples(recorder, samples)  
        events = recorder.get_events("match")  
        return {  
            "accuracy": evals.metrics.get_accuracy(events),  
            "f1_score": np.mean(recorder.get_scores("f1_score")),  
            "boostrap_std": evals.metrics.get_bootstrap_accuracy_std(events),  
        }  
        # "accuracy": np.mean(recorder.get_scores("accuracy")),
```

run函数有三个步骤：
- 通过`get_samples`加载数据
- 调用`eval_all_samples`：它将为每个样本调用`eval_sample`。
- 汇总记录的结果。

现在，让我们看一下该方法（`eval_sample`）的实现。

``` Python
class JsonMatch(evals.Eval):  
    ...
  
    def eval_sample(self, sample: Any, rng: random.Random):  
        # 重写eval类的函数，评估单个测试样本:接受两个参数:sample(要评估的样本)和rng(随机数生成器,在这里没有使用,del删除了)  
        del rng  
  
        # 检查test_sample的格式合法性  
        assert isinstance(sample, dict), "sample must be a dict"  
        assert "input" in sample, "sample must have an 'input' key"  
        assert "ideal" in sample, "sample must have an 'ideal' key"  
  
        # 从 sample 字典中获取 "input" 键的值,并将其强制转换为字符串类型。  
        prompt, correct_answer = sample["input"], sample["ideal"]  
        # 检查correct_answers变量是否是一个列表:如果不是,函数会将它转换为一个只包含correct_answers值的列表  
        if not isinstance(correct_answer, list):  
            correct_answer = [correct_answer]  
  
        result = self.completion_fn(  
            prompt=prompt,  
            temperature=0.0,  # Q: why are these hardcoded?  
            max_tokens=self.max_tokens,  
        )  
        # 这一行从result对象中提取第一个completion,并将其赋给sampled变量，既模型给出的答案。  
        sampled = result.get_completions()[0]  
  
        # 尝试将 sampled 字符串解析为 JSON。如果解析失败(即 sampled 字符串不是有效的 JSON),sampled_json 变量将被设置为 None        sampled_json: Any  
        try:  
            sampled_json = eval(sampled)  
            # sampled_json = json.loads(sampled)  
        except ValueError:  
            # If the sampled string is not valid JSON, it will never match  
            sampled_json = None  
  
        # 这个列表推导式遍历 sampled_json 列表(可能包含单个字符串或字符串列表),并将每个元素解析为 JSON,将结果存储在 sampled_list_json 列表中。  
        # sampled_list_json = [json.loads(sample_answer) for sample_answer in sampled_json]  
  
        # 尝试将 correct_answer 内的唯一一个答案{}解析为 JSON格式。如果解析失败,correct_answers 变量将被设置为 None        # correct_answer: 如果解析成功，应该是一个dict答案  
        correct_answer_json: Any  
        try:  
            correct_answer_json = correct_answer[0]  # 因为correct_answer唯一,且correct_answer本身就是list格式的  
        except ValueError:  
            correct_answer_json = None  
  
  
        # 使用列表推导式创建一个布尔值列表,表示sampled_json（列表中可能有多个answer）中的每个answer是否与correct_answers_json（列表中只有一个ideal answer）中的唯一答案匹配。  
        matches = [json_match(sj, correct_answer_json) for sj in sampled_json]  
  
        evals.record.record_match(  
            True in matches,  
            expected=correct_answer,  
            picked=[sampled for i in range(len(sampled_json)) if matches[i]],  
        )  
  
        # 记录metrics结果：  
        # accuracy=float(True in matches),如果sampled文本与任何正确答案匹配,则计数为1.0,否则计数为0.0。  
        # f1_score=utils.f1_score(sampled, correct_answers):F1得分,使用utils.f1_score()函数计算,输入参数为sampled文本和正确答案列表  
        sampled_str_list = []  
        for item in sampled_json:  
            sampled_str_list.append(str(item))  
        evals.record.record_metrics(  
            accuracy=float(True in matches),  
            f1_score=utils.f1_score(str(correct_answer_json), sampled_str_list),  
        )  
```


`eval_sample`也有三个步骤：

- 构造提示
- 查询模型以进行完成（completion）
- 计算和记录指标（例如，一个布尔值，用于指示完成completion是否与预期响应匹配）


在正在运行的示例中，调用以下代码行。下一节将解释 recorder的使用。

``` Python
result = eval.run(recorder)
```


#### Section 5: Result Recording
`openai/evals`框架中的recorder是一个实用程序，用于记录、存储和管理评估结果。它提供了一种结构化的方式来保存评估详细信息、结果和其他相关信息。

**1. Instantiation of the Recorder**
`Recorder`的实例化需要创建一个`RunSpec`对象，以保存有关评估运行的各种详细信息。而这个运行规范会被保存到 `recorder_path`的JSON文件中。

``` Python
# recorder  
eval_name = eval_spec.key  
run_spec = evals.base.RunSpec(  
    completion_fns=[args.completion_fn],  
    eval_name=eval_name,  
    base_eval=eval_name.split(".")[0],  
    split=eval_name.split(".")[1],  
    run_config={  
        "completion_fns": [args.completion_fn],  
        "eval_spec": eval_spec,  
        "seed": args.seed,  
    },  
    created_by="zhuqinglin",  # my name  
)  
# A path is defined for the recorder to save the evaluation logs.  
recorder_path = f"evallogs/{run_spec.run_id}_{args.completion_fn}_{args.eval}.jsonl"  
recorder = evals.record.LocalRecorder(recorder_path, run_spec)  

```


**2. The Use of Recoder**
借助 `eval.run`运行评估后 ，调用方法`recorder.record_final_report(result)`将评估结果写入本地 JSONL 文件。

``` Python
# run the evaluation  
# save evaluation into recoder object  
result = eval.run(recorder)  
# write evaluation result into local json file  
recorder.record_final_report(result)
```

此文件将包含评估的结构化日志。
- Evaluation Specification（评估规范）：第一个条目提供了评估的详细规范，包括 the completion functions, evaluation name, run configuration, creator’s name, run ID, and creation timestamp（完成函数、评估名称、运行配置、创建者姓名、运行 ID 和创建时间戳）。
``` JSON
{  
  "spec": {  
    "completion_fns": [  
      "openai/pinolo-mutate-llm-postgres"  
    ],  
    "eval_name": "JsonMatch_pinolo_mutate_llm_postgres.test.v1",  
    "base_eval": "JsonMatch_pinolo_mutate_llm_postgres",  
    "split": "test",  
    "run_config": {  
      "completion_fns": [  
        "openai/pinolo-mutate-llm-postgres"  
      ],  
      "eval_spec": {  
        "cls": "evals.elsuite.pinolo_mutate_llm.json_match:JsonMatch",  
        "registry_path": "D:/PycharmFiles/evals-main/evals/registry",  
        "args": {  
          "samples_jsonl": "pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl"  
        },  
        "key": "JsonMatch_pinolo_mutate_llm_postgres.test.v1",  
        "group": "JsonMatch_pinolo_mutate_llm_postgres"  
      },  
      "seed": 20220722  
    },  
    "created_by": "zhuqinglin",  
    "run_id": "240818144321HHHG4WJV",  
    "created_at": "2024-08-18 14:43:21.781140"  
  }  
}
```

- Final Report（最终报告）：第二个条目提供评估的最终报告，其中包括准确性及其引导标准偏差（bootstrap standard deviation）等指标。
``` JSON
{  
  "final_report": {  
    "accuracy": 0.975,  
    "f1_score": 0.9997881355932204,  
    "boostrap_std": 0.01776309376206748  
  },  
  "run_id": "24081817505666LX7TAA"  
}
```

* Individual Evaluation Events（单个评估事件）：后续条目记录单个评估事件，详细说明specific samples (`sample_id`), their results, event IDs, event types, and timestamps（特定样本、其结果、事件 ID、事件类型和时间戳）。
``` JSON
{  
  "run_id": "240818144321HHHG4WJV",  
  "event_id": 1,  
  "sample_id": "JsonMatch_pinolo_mutate_llm_postgres.test.54",  
  "type": "match",  
  "data": {  
    "correct": true,  
    "expected": {  
      "mutated sql": "SELECT (-0.7238938848807085) AS f1, (f15) AS f2, (DATE '2017-10-11' - INTERVAL '1 MONTH' || TO_CHAR(f14, 'FM99999999999999999999')) AS f3 FROM (SELECT col_float_undef_signed AS f13, col_double_undef_unsigned AS f14, col_double_key_unsigned AS f15 FROM table_3_utf8_undef) AS t4 GROUP BY f15, f14 HAVING TRUE",  
      "flag": true  
    },  
    "picked": [  
      "[{'mutated sql': \"SELECT (-0.7238938848807085) AS f1, (f15) AS f2, (DATE '2017-10-11' - INTERVAL '1 MONTH' || TO_CHAR(f14, 'FM99999999999999999999')) AS f3 FROM (SELECT col_float_undef_signed AS f13, col_double_undef_unsigned AS f14, col_double_key_unsigned AS f15 FROM table_3_utf8_undef) AS t4 GROUP BY f15, f14 HAVING TRUE\", 'flag': True}]"  
    ]  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-18 14:43:26.809733+00:00"  
}
```


### OpenAI LLM + few-shot

#### Section 0: 准备fewshot
fewshot文件格式参考[[Evals_Data_Format_README]]
``` JSON
single_eval_data = {  
    "sample": [  
        {"role": "system", "content": str(item[user_key]), "name": "example_user"},  
        {"role": "system", "content": str(item[assistant_key]), "name": "example_assistant"}  
    ]  
}
```

#### Section 1: Specification File
```
evals/registry/evals/JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres.yaml:

JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres:  
  id: JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres.test.v1  
  description: evaluate the basic openai llm + few-shot for postgres with four mutate strategies.  
  metrics: [accuracy,f1_score,boostrap_std]  
JsonMatch_pinolo_gpt-4o-mini_fewshot_postgres.test.v1:  
  class: evals.elsuite.pinolo_mutate_llm.json_match:JsonMatch  
  args:  
    samples_jsonl: pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl  
    num_few_shot: 3  
    few_shot_jsonl: pinolo_mutate_llm/postgres/postgres_fewshot_eval_dataset_formatted1.0.jsonl
```
#### Section 2-4

#### Section 5: Result Recording

- Evaluation Specification（评估规范）：
- Final Report（最终报告）：第二个条目提供评估的最终报告，其中包括准确性及其引导标准偏差（bootstrap standard deviation）等指标。
``` JSON
{  
  "final_report": {  
    "accuracy": 0.125,  
    "f1_score": 0.8468648800969358,  
    "boostrap_std": 0.0371381794788059  
  },  
  "run_id": "240818184243V2U3SX4C"  
}
```

* Individual Evaluation Events（单个评估事件）：后续条目记录单个评估事件，详细说明specific samples (`sample_id`), their results, event IDs, event types, and timestamps（特定样本、其结果、事件 ID、事件类型和时间戳）。
``` JSON
{  
  "run_id": "240818144321HHHG4WJV",  
  "event_id": 1,  
  "sample_id": "JsonMatch_pinolo_mutate_llm_postgres.test.54",  
  "type": "match",  
  "data": {  
    "correct": true,  
    "expected": {  
      "mutated sql": "SELECT (-0.7238938848807085) AS f1, (f15) AS f2, (DATE '2017-10-11' - INTERVAL '1 MONTH' || TO_CHAR(f14, 'FM99999999999999999999')) AS f3 FROM (SELECT col_float_undef_signed AS f13, col_double_undef_unsigned AS f14, col_double_key_unsigned AS f15 FROM table_3_utf8_undef) AS t4 GROUP BY f15, f14 HAVING TRUE",  
      "flag": true  
    },  
    "picked": [  
      "[{'mutated sql': \"SELECT (-0.7238938848807085) AS f1, (f15) AS f2, (DATE '2017-10-11' - INTERVAL '1 MONTH' || TO_CHAR(f14, 'FM99999999999999999999')) AS f3 FROM (SELECT col_float_undef_signed AS f13, col_double_undef_unsigned AS f14, col_double_key_unsigned AS f15 FROM table_3_utf8_undef) AS t4 GROUP BY f15, f14 HAVING TRUE\", 'flag': True}]"  
    ]  
  },  
  "created_by": "zhuqinglin",  
  "created_at": "2024-08-18 14:43:26.809733+00:00"  
}
```

## 验证Oracle（检测bug）
运行测试集的80个postgres测试样例(origin sql,mutated sql)，验证oracle：其中73 true，7 false。

1. "index"=35，"mutationName"="FixMDistinctL" ：不算bug，decode() 函数是 PostgreSQL 中的一个内置函数,用于对字符串进行编码和解码操作，这里对字符串 '2017' 进行 'escape' 编码。
``` JSON
{  
    "index": 35,  
    "reportTime": "2022-12-23 15:12:48.775439617 +0800 CST m=+19492.660071877",  
    "bugId": 29,  
    "sqlId": 14995,  
    "mutationName": "FixMDistinctL",  
    "isUpper": false,  
    "originalSqlsim": "SELECT (`f6`) AS `f1`,(FORMAT_BYTES(`f5`)) AS `f2`,(BIN('2017')) AS `f3` FROM (SELECT (!`f10`&PI()%NULL) AS `f7`,(SUBTIME('2008-05-17 09:56:14', '14:24:29')) AS `f5`,(`f10`) AS `f8` FROM (SELECT `col_float_key_unsigned` AS `f9`,`col_double_key_signed` AS `f10`,`col_double_undef_signed` AS `f11` FROM `table_3_utf8_undef`) AS `t1`) AS `t2` NATURAL JOIN (SELECT `col_float_undef_unsigned` AS `f4`,`col_char(20)_undef_signed` AS `f12`,`col_double_key_unsigned` AS `f6` FROM `table_3_utf8_undef`) AS `t3`",  
    "mutatedSqlsim": "SELECT (`f6`) AS `f1`,(FORMAT_BYTES(`f5`)) AS `f2`,(BIN('2017')) AS `f3` FROM (SELECT DISTINCT (!`f10`&PI()%NULL) AS `f7`,(SUBTIME('2008-05-17 09:56:14', '14:24:29')) AS `f5`,(`f10`) AS `f8` FROM (SELECT `col_float_key_unsigned` AS `f9`,`col_double_key_signed` AS `f10`,`col_double_undef_signed` AS `f11` FROM `table_3_utf8_undef`) AS `t1`) AS `t2` NATURAL JOIN (SELECT `col_float_undef_unsigned` AS `f4`,`col_char(20)_undef_signed` AS `f12`,`col_double_key_unsigned` AS `f6` FROM `table_3_utf8_undef`) AS `t3`",  
    "originalSqlsim_postgres": "SELECT (f6) AS f1, (LENGTH(f5::text)) AS f2, (decode('2017', 'escape')) AS f3 FROM (SELECT (CASE WHEN f10 IS NOT NULL THEN TRUE ELSE FALSE END) AS f7, (TIMESTAMP '2008-05-17 09:56:14' - INTERVAL '14:24:29') AS f5, (f10) AS f8 FROM (SELECT col_float_key_unsigned AS f9, col_double_key_signed AS f10, col_double_undef_signed AS f11 FROM table_3_utf8_undef) AS t1) AS t2 NATURAL JOIN (SELECT col_float_undef_unsigned AS f4, col_char_20_undef_signed AS f12, col_double_key_unsigned AS f6 FROM table_3_utf8_undef) AS t3",   
    "mutatedSqlsim_postgres": {  
    "mutated sql": "SELECT (f6) AS f1, (LENGTH(f5::text)) AS f2, (decode('2017', 'escape')) AS f3 FROM (SELECT DISTINCT (CASE WHEN f10 IS NOT NULL THEN TRUE ELSE FALSE END) AS f7, (TIMESTAMP '2008-05-17 09:56:14' - INTERVAL '14:24:29') AS f5, (f10) AS f8 FROM (SELECT col_float_key_unsigned AS f9, col_double_key_signed AS f10, col_double_undef_signed AS f11 FROM table_3_utf8_undef) AS t1) AS t2 NATURAL JOIN (SELECT col_float_undef_unsigned AS f4, col_char_20_undef_signed AS f12, col_double_key_unsigned AS f6 FROM table_3_utf8_undef) AS t3",  
    "flag": true  
},
    "originalSqlsim_mysql_result": "[(0.0, '18.26 TiB', '11111100001'), (0.0, '18.26 TiB', '11111100001'), (0.0, '18.26 TiB', '11111100001'), (0.0001, '18.26 TiB', '11111100001'), (0.0001, '18.26 TiB', '11111100001'), (0.0001, '18.26 TiB', '11111100001'), (1.0, '18.26 TiB', '11111100001'), (1.0, '18.26 TiB', '11111100001'), (1.0, '18.26 TiB', '11111100001')]",  
    "originalSqlsim_mysql_error": "None",  
    "mutatedSqlsim_mysql_result": "[(0.0, '1.96 KiB', '11111100001'), (0.0, '1.96 KiB', '11111100001'), (0.0, '1.96 KiB', '11111100001'), (0.0001, '1.96 KiB', '11111100001'), (0.0001, '1.96 KiB', '11111100001'), (0.0001, '1.96 KiB', '11111100001'), (1.0, '1.96 KiB', '11111100001'), (1.0, '1.96 KiB', '11111100001'), (1.0, '1.96 KiB', '11111100001')]",  
    "mutatedSqlsim_mysql_error": "None",  
    "mysql_oracle_check": {  
        "end": false,  
        "error": null  
    },  
    "originalSqlsim_postgres_result": "[(0.0, 19, <memory at 0x000002077B5B6700>), (1.0, 19, <memory at 0x000002077B5B67C0>), (0.0001, 19, <memory at 0x000002077B5B6880>), (0.0, 19, <memory at 0x000002077B5B6940>), (1.0, 19, <memory at 0x000002077B5B6D00>), (0.0001, 19, <memory at 0x000002077B5B6DC0>), (0.0, 19, <memory at 0x000002077B5B6E80>), (1.0, 19, <memory at 0x000002077B5B6F40>), (0.0001, 19, <memory at 0x000002077B69E040>)]",  
    "originalSqlsim_postgres_error": "None",  
    "mutatedSqlsim_postgres_result": "[(0.0, 19, <memory at 0x000002077B69E100>), (1.0, 19, <memory at 0x000002077B69E1C0>), (0.0001, 19, <memory at 0x000002077B69E280>), (0.0, 19, <memory at 0x000002077B69E340>), (1.0, 19, <memory at 0x000002077B69E400>), (0.0001, 19, <memory at 0x000002077B69E4C0>), (0.0, 19, <memory at 0x000002077B69E580>), (1.0, 19, <memory at 0x000002077B69E640>), (0.0001, 19, <memory at 0x000002077B69E700>)]",  
    "mutatedSqlsim_postgres_error": "None",  
    "postgres_oracle_check": {  
        "end": false,  
        "error": null  
    }  
}
```
 

2. "index"=36，"mutationName"="FixMCmpOpU"：不算bug
* mysql的origin sql中(DATE_SUB(0, INTERVAL 1 DAY_MINUTE))，意味着从一个日期/时间值减去一个指定的时间间隔，INTERVAL 1 DAY_MINUTE表示需要减去的时间间隔。从 1970-01-01 00:00:00 (Unix 纪元) 开始,减去 1 天的时间间隔，得到一个固定值
* postgres的origin sql中(CURRENT_TIMESTAMP - INTERVAL '1 minute')代表获取当前时间减去 1 分钟的时间点。这导致origin sql和mutated sql的结果集不可能有互相包含的关系，除非严格意义上同时执行。

``` JSON
{  
    "index": 36,  
    "reportTime": "2022-12-24 07:03:40.989191741 +0800 CST m=+76544.873823985",  
    "bugId": 26,  
    "sqlId": 13269,  
    "mutationName": "FixMCmpOpU",  
    "isUpper": false,  
    "originalSqlsim": "SELECT (COLLATION(`f4`)) AS `f1`,(`f6`|`f6`) AS `f2`,(DATE_SUB(0, INTERVAL 1 DAY_MINUTE)) AS `f3` FROM (SELECT `col_decimal(40, 20)_key_signed` AS `f4`,`col_double_key_signed` AS `f5`,`col_float_key_signed` AS `f6` FROM `table_3_utf8_undef`) AS `t1` WHERE (NOT ((-LTRIM(`f5`))=ANY (SELECT `col_char(20)_key_signed` FROM `table_7_utf8_undef`))) OR ((CAST((0.8201428585920637) AS CHAR) REGEXP '^[a-z]') IS TRUE)",  
    "mutatedSqlsim": "SELECT (COLLATION(`f4`)) AS `f1`,(`f6`|`f6`) AS `f2`,(DATE_SUB(0, INTERVAL 1 DAY_MINUTE)) AS `f3` FROM (SELECT `col_decimal(40, 20)_key_signed` AS `f4`,`col_double_key_signed` AS `f5`,`col_float_key_signed` AS `f6` FROM `table_3_utf8_undef`) AS `t1` WHERE (NOT ((-LTRIM(`f5`))>=ANY (SELECT `col_char(20)_key_signed` FROM `table_7_utf8_undef`))) OR ((CAST((0.8201428585920637) AS CHAR) REGEXP '^[a-z]') IS TRUE)",  
    "originalSqlsim_postgres": "SELECT (f4) AS f1, (f6 + f6) AS f2, (CURRENT_TIMESTAMP - INTERVAL '1 minute') AS f3 FROM (SELECT col_decimal_40_20_key_signed AS f4, col_double_key_signed AS f5, col_float_key_signed AS f6 FROM table_3_utf8_undef) AS t1 WHERE (NOT ((-CAST(f5 AS TEXT)::FLOAT) = ANY (SELECT NULLIF(CAST(col_char_20_key_signed AS TEXT), '')::FLOAT FROM table_7_utf8_undef WHERE col_char_20_key_signed ~ '^[0-9.]+$'))) OR (CAST(0.8201428585920637 AS TEXT) ~ '^[a-z]') IS TRUE",  
    "mutatedSqlsim_postgres": {  
        "mutated sql": "SELECT (f4) AS f1, (f6 + f6) AS f2, (CURRENT_TIMESTAMP - INTERVAL '1 minute') AS f3 FROM (SELECT col_decimal_40_20_key_signed AS f4, col_double_key_signed AS f5, col_float_key_signed AS f6 FROM table_3_utf8_undef) AS t1 WHERE (NOT ((-CAST(f5 AS TEXT)::FLOAT) >= ANY (SELECT NULLIF(CAST(col_char_20_key_signed AS TEXT), '')::FLOAT FROM table_7_utf8_undef WHERE col_char_20_key_signed ~ '^[0-9.]+$'))) OR (CAST(0.8201428585920637 AS TEXT) ~ '^[a-z]') IS TRUE",  
        "flag": false  
    },  
    "originalSqlsim_mysql_result": "[('binary', 94, None), ('binary', 1, None)]",  
    "originalSqlsim_mysql_error": "None",  
    "mutatedSqlsim_mysql_result": "[('binary', 1, None)]",  
    "mutatedSqlsim_mysql_error": "None",  
    "mysql_oracle_check": {  
        "end": true,  
        "error": null  
    },  
    "originalSqlsim_postgres_result": "[(Decimal('-2.00000000000000000000'), 188.2212, datetime.datetime(2024, 8, 22, 14, 50, 24, 821337, tzinfo=datetime.timezone.utc)), (Decimal('12.99100000000000000000'), 2.0, datetime.datetime(2024, 8, 22, 14, 50, 24, 821337, tzinfo=datetime.timezone.utc)), (Decimal('47.15150000000000000000'), 0.0002, datetime.datetime(2024, 8, 22, 14, 50, 24, 821337, tzinfo=datetime.timezone.utc))]",  
    "originalSqlsim_postgres_error": "None",  
    "mutatedSqlsim_postgres_result": "[(Decimal('-2.00000000000000000000'), 188.2212, datetime.datetime(2024, 8, 22, 14, 50, 24, 850976, tzinfo=datetime.timezone.utc)), (Decimal('12.99100000000000000000'), 2.0, datetime.datetime(2024, 8, 22, 14, 50, 24, 850976, tzinfo=datetime.timezone.utc)), (Decimal('47.15150000000000000000'), 0.0002, datetime.datetime(2024, 8, 22, 14, 50, 24, 850976, tzinfo=datetime.timezone.utc))]",  
    "mutatedSqlsim_postgres_error": "None",  
    "postgres_oracle_check": {  
        "end": false,  
        "error": null  
    }  
}
```

3. "index"=38，"mutationName"="FixMCmpOpU"：不算bug
* mysql的origin sql中(DATE_ADD(-SPACE(7), INTERVAL 1 SECOND))，得到一个固定值
* postgres的origin sql中(NOW() - INTERVAL '7 days' + INTERVAL '1 second')代表当前时间减去 7 天,再加 1 秒钟。这导致origin sql和mutated sql的结果集不可能有互相包含的关系，除非严格意义上同时执行。

4. "index"= 21，"mutationName"="FixMHaving1U"：不算bug
* mysql的origin sql中(DATE_SUB(0, INTERVAL 1 MINUTE))，得到一个固定值
* postgres的origin sql中(NOW() - INTERVAL '1 minute')

5. "index"= 30，"mutationName"="FixMOn1U"：不算bug
* mysql的origin sql中(DATE_SUB(1, INTERVAL 1 HOUR_MINUTE))，得到一个固定值
* postgres的origin sql中(NOW() - INTERVAL '1 hour')

6. "index"= 31，"mutationName"="FixMOn1U"：不算bug
* mysql的origin sql中(DATE_SUB(0.2817114686285644, INTERVAL 1 WEEK))和(DATE_SUB('b', INTERVAL 1 DAY))，得到一个固定值
* postgres的origin sql中(NOW() - INTERVAL '1 week') 和(NOW() - INTERVAL '1 day')


7. "index"= 37，"mutationName"="FixMOn1U"：不算bug
* mysql的origin sql中(DATE_ADD(LOG2(4), INTERVAL 1 HOUR))，得到一个固定值
* postgres的origin sql中(NOW() + INTERVAL '1 hour')


过程中发现：
* mysql的（origin sqlsim，target sqlsim）满足oracle的有17个，不满足的有63个。（这里奇怪的是，检测逻辑bug按道理不应该是不满足吗。已知，oracle checker代码无误。）:可能修复了

## Eval结果汇总
[[Mutate LLM Fine-tuning(PINOLO_postgres) Results]]

---






