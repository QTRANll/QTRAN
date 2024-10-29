## Preparing your dataset
### Training Dataset说明
1. 训练集来源：PINOLO
2. 训练集要求：选取的sample尽量简练（长度较短）；训练集大小；训练集中的mutate strategies的种类数；为每种mutate strategies提供的sample数目
3. 训练集选取
* 选取output1-4/mysql的简化后的（"originalSqlsim"，"mutatedSqlsim"）对
* 训练集大小
* 训练集中的mutate strategies的种类数，每种提供的sample数
* 训练集sample需要包括dbname，mutate name，mutate stragegy，original sql，mutated sql

### Training Dataset 和Testing Dataset 的获取
1. 有18种变异策略([[mutators_PINOLO_mysql_like]])，从已有pinolo数据中选取典型sample。
* 变异策略：先测以下几种，FixMDistinctU，FixMDistinctL；FixMCmpOpU，FixMCmpOpL；FixMInNullU；FixMWhere1U；FixMHaving1U，FixMHaving0L；FixMOn1U，FixMOn0L
* DB：mariadb，mysql，tidb，oceanbase

``` 
mysql:
FixMDistinctU:
FixMDistinctL:25527+26184+25969+26208
FixMCmpOpU:930+902+892+853
FixMCmpOpL:5+4+5+5（全选）
FixMUnionAllU:
FixMUnionAllL:
FixMInNullU:9+7+3+14（全选）
FixMWhere1U:3+6+5+5（全选）
FixMWhere0L:2+1(去除)
FixMHaving1U:14682+15207+14920+15072
FixMHaving0L:1(需要额外修改)
FixMOn1U:454+433+457+465
FixMOn0L:(需要额外修改)
FixMRmUnionAllL:
RdMLikeU
RdMLikeL
RdMRegExpU
RdMRegExpL
```

2. 验证training data和testing data中sql和mutated sql的正确性
* 分别运行sql和mutated sql语句：是否可执行（语法正确性），是否符合变异策略（变异正确性）
* 保证语法正确性：修改sql和mutated sql语句，保证可执行
* 保证变异正确性：修改sql和mutated sql，保证符合变异策略
* 注：mysql的句子在mariadb上是无法全部执行成功的，测试的132个里面有12个不可执行

3. 编写training data和testing data中18种变异策略的system message
  [[mutators_PINOLO_mysql_like#Pinolo-main mutation stage2 allmutations.go]]
```

* FixMDistinctU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMDistinctU":"Distinct true -> false".This mutate strategy will change "DISTINCT" in SELECT statement from true to false.
* FixMDistinctL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMDistinctL" :"Distinct false -> true".This mutate strategy will change "DISTINCT" in SELECT statement from false to true.
* FixMCmpOpU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMCmpOpU": "a {>|<|=} b -> a {>=|<=|>=} b".This mutate strategy will change ">" to ">=","<" to "<=","=" to ">=" in Binary operation expression and Comparison subquery expression.
* FixMCmpOpL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMCmpOpL" : "a {>=|<=} b -> a {>|<} b".This mutate strategy will change ">=" to ">","<=" to "<" in Binary operation expression and Comparison subquery expression.
* FixMUnionAllU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMUnionAllU" :"UNION -> UNION ALL".This mutate strategy will change the set operator "UNION" to "UNION ALL" between SELECT statements.
* FixMUnionAllL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMUnionAllL": "UNION ALL -> UNION".This mutate strategy will change the set operator "UNION ALL" to "UNION" between SELECT statements.
* FixMInNullU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMInNullU":"in(x,x,x) -> in(x,x,x,null)".This mutate strategy will include null value in IN List Expression to increase the scope of the query result set.
* FixMWhere1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMWhere1U":"WHERE xxx -> WHERE 1".This mutate strategy will change the condition of WHERE clause to "1" in SELECT statement. 
* FixMWhere0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMWhere0L" : "WHERE xxx -> WHERE 0".This mutate strategy will change the condition of WHERE clause to "0" in SELECT statement. 
* FixMHaving1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMHaving1U" : "HAVING xxx -> HAVING 1".This mutate strategy will change the condition of HAVING clause to "1" in SELECT statement. 
* FixMHaving0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMHaving0L" : "HAVING xxx -> HAVING 0".This mutate strategy will change the condition of HAVING clause to "0" in SELECT statement. 
* FixMOn1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMOn1U":"ON xxx -> ON 1".This mutate strategy will change the condition of ON clause to "1" in JOIN statement. 
* FixMOn0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMOn0L":"ON xxx -> ON 0".This mutate strategy will change the condition of ON clause to "0" in JOIN statement. 
* FixMRmUnionAllL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMRmUnionAllL":"remove Selects[1:] for UNION ALL".This mutate strategy will keep only the first SELECT statement and remove all subsequent SELECT statements connected by "UNION ALL".
* RdMLikeU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMLikeU":"normal char -> '_'|'%',  '_' -> '%'".This mutate strategy will modify the LIKE expression such that for each character, if it is not '%', there is a 50% probability of replacing it with '%'.
* RdMLikeL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMLikeL":"'%' -> '_'". This mutate strategy will modify the LIKE expression such that for each character, if it is '%', there is a 50% probability of replacing it with '_'.
* RdMRegExpU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMRegExpU":"'^'|'$' -> '', '+'|'?' -> '*'".This mutate strategy will modify the  regular expression REGEXP such that for each character, if it is '^' or '$', there is a 50% probability of deleting it;and if it is '+' or '?', there is a 50% probability of replacing it with '*'.
* RdMRegExpL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMRegExpL":"'*' -> '+'|'?'".This mutate strategy will modify the  regular expression REGEXP such that for each character, if it is '*',there is a 50% probability of replacing it with '+' or '?'.
```


4. 形成格式化的training data和testing data，格式如下
* 在system里加一句角色扮演提示词以添加数据库类型信息

``` JSON
role_prompt = "You are an expert in " + db_name + " statement mutation."
single_train_data = {  
    "messages": [  
        {"role": "system", "content": mutate_strategy_illustration[key]},  
        {"role": "user", "content": item["originalSqlsim_modified"]},  
        {"role": "assistant", "content": item["mutatedSqlsim_modified"]}  
    ]  
}
```

5. 检查training data的格式并预测成本 [Check data formatting](https://platform.openai.com/docs/guides/fine-tuning/check-data-formatting)
  It checks for format errors, provides basic statistics, and estimates token counts for fine-tuning costs.
``` JSON
Num examples: 110
First example:
{'role': 'system', 'content': 'Synthesize the mutated sql that should return a superset of the result set of the seed sql given by user according to the mutate strategy "FixMDistinctU":"Distinct true -> false".This mutate strategy will change "DISTINCT" in SELECT statement from true to false.'}
{'role': 'user', 'content': "SELECT DISTINCT (OCTET_LENGTH(`f8`)) AS `f1`,(`f8`) AS `f2`,(DATE_ADD(`f7`, INTERVAL 1 WEEK)) AS `f3` FROM (SELECT `col_double_key_unsigned` AS `f7`,`col_double_key_unsigned` AS `f8`,`col_bigint_key_signed` AS `f9` FROM `table_7_utf8_undef`) AS `t2` HAVING (NOT (CAST((FORMAT_BYTES(`f3`)) AS CHAR) LIKE '%0%')) IS TRUE"}
{'role': 'assistant', 'content': "SELECT (OCTET_LENGTH(`f8`)) AS `f1`,(`f8`) AS `f2`,(DATE_ADD(`f7`, INTERVAL 1 WEEK)) AS `f3` FROM (SELECT `col_double_key_unsigned` AS `f7`,`col_double_key_unsigned` AS `f8`,`col_bigint_key_signed` AS `f9` FROM `table_7_utf8_undef`) AS `t2` HAVING (NOT (CAST((FORMAT_BYTES(`f3`)) AS CHAR) LIKE '%0%')) IS TRUE"}
No errors found
Num examples missing system message: 0
Num examples missing user message: 0

#### Distribution of num_messages_per_example:
min / max: 3, 3
mean / median: 3.0, 3.0
p5 / p95: 3.0, 3.0

#### Distribution of num_total_tokens_per_example:
min / max: 280, 1196
mean / median: 446.8545454545455, 370.0
p5 / p95: 299.0, 623.3000000000001

#### Distribution of num_assistant_tokens_per_example:
min / max: 78, 539
mean / median: 172.85454545454544, 130.0
p5 / p95: 104.0, 253.60000000000005

0 examples may be over the 16,385 token limit, they will be truncated during fine-tuning
Dataset has ~49154 tokens that will be charged for during training
By default, you'll train for 3 epochs on this dataset
By default, you'll be charged for ~147462 tokens  
```


### [Upload a training file](https://platform.openai.com/docs/guides/fine-tuning/upload-a-training-file)
``` Python
from openai import OpenAI
client = OpenAI()

file_object = client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)
# FileObject(id='file-Q4iMX3ECBhQ7S6fkJToqRdJZ', bytes=145639, created_at=1722772740, filename='mysql_training_dataset_formatted1.0.jsonl', object='file', purpose='fine-tune', status='processed', status_details=None)
print(training_file_object.id)
```

在您上传文件后,可能需要一些时间来处理。在文件处理过程中,您仍然可以创建微调作业,但是它只有在文件处理完成后才会开始。
[Train and test splits](https://platform.openai.com/docs/guides/fine-tuning/train-and-test-splits)：收集初始数据集后,我们建议将其分为训练集和测试集。在提交同时包含训练集和测试集的微调任务时,我们将在训练过程中为这两个集合都提供统计信息。这些统计信息将成为您判断模型改进程度的初始信号。此外,在训练开始时构建测试集也很有用,因为可以利用测试集生成样本,从而评估训练后的模型性能。


## [Create a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model)

在确保您的数据集数量和结构正确,并已上传文件之后,下一步就是创建一个微调作业。

``` Python
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="file-abc123", 
  validation_file="file-abc125", 
  model="gpt-4o-mini-2024-07-18"
)
```

在此示例中,`model`是您想要微调的模型名称(`gpt-4o-mini`, `gpt-3.5-turbo`, `babbage-002`, `davinci-002`或现有的微调模型)。`training_file`**是在将训练文件上传到OpenAI API时返回的文件ID**。 您可以使用后缀参数自定义您的微调模型名称。

如需设置额外的微调参数,如`validation_file` 或`hyperparameters`，请参考 [API specification for fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning/create).


在您启动微调作业后,可能需要一些时间才能完成。您的作业可能会排在我们系统中其他作业的队列之后,并且根据模型和数据集大小,训练模型可能需要几分钟或几个小时的时间。**在模型训练完成后,创建微调作业的用户将收到一封电子邮件确认。**


除了创建微调作业外，还可以列出现有作业、检索作业的状态或取消作业。

``` Python
from openai import OpenAI
client = OpenAI()

# List 10 fine-tuning jobs
client.fine_tuning.jobs.list(limit=10)

# Retrieve the state of a fine-tune
client.fine_tuning.jobs.retrieve("ftjob-abc123")

# Cancel a job
client.fine_tuning.jobs.cancel("ftjob-abc123")

# List up to 10 events from a fine-tuning job
client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-abc123", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
client.models.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")
```


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
``` Python
{
    "object": "fine_tuning.job.checkpoint",
    "id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
    "created_at": 1519129973,
    "fine_tuned_model_checkpoint": "ft:gpt-3.5-turbo-0125:my-org:custom-suffix:96olL566:ckpt-step-2000",
    "metrics": {
        "full_valid_loss": 0.134,
        "full_valid_mean_token_accuracy": 0.874
    },
    "fine_tuning_job_id": "ftjob-abc123",
    "step_number": 2000
}
```


每个检查点将指定其:
* `step_number` :创建检查点的步骤(其中每个epoch是训练集中的步数除以批处理大小)
* `metrics`:一个对象，包含在创建检查点时的步骤中微调作业的指标。
目前，只有作业的最后3个epoch的检查点被保存并可供使用。我们计划在不久的将来发布更复杂和灵活的检查点策略。


## [Analyzing your fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/analyzing-your-fine-tuned-model)

我们提供以下经过培训过程计算的培训指标:
- training loss
- training token accuracy
- valid loss
- valid token accuracy

Valid loss 和valid token accuracy以两种不同的方式计算——在每个步骤期间对一小批数据进行计算，以及在每个epoch结束时对完全有效分割进行计算（on a small batch of the data during each step, and on the full valid split at the end of each epoch）。**完全有效丢失和完全有效令牌准确性（The full valid loss and full valid token accuracy）指标是跟踪模型整体性能的最准确指标**。**这些统计数据是为了提供一个健全的检查，训练进行顺利：(损失loss应该减少，令牌准确性token accuracy应该提高)**。 **当一个活动的微调作业正在运行时，您可以查看一个事件对象，其中包含一些有用的指标:**

``` Python
{
    "object": "fine_tuning.job.event",
    "id": "ftevent-abc-123",
    "created_at": 1693582679,
    "level": "info",
    "message": "Step 300/300: training loss=0.15, validation loss=0.27, full validation loss=0.40",
    "data": {
        "step": 300,
        "train_loss": 0.14991648495197296,
        "valid_loss": 0.26569826706596045,
        "total_steps": 300,
        "full_valid_loss": 0.4032616495084362,
        "train_mean_token_accuracy": 0.9444444179534912,
        "valid_mean_token_accuracy": 0.9565217391304348,
        "full_valid_mean_token_accuracy": 0.9089635854341737
    },
    "type": "metrics"
}
```


在微调工作完成后，您还可以通过[查询微调工作](https://platform.openai.com/docs/api-reference/fine-tuning/retrieve)，从`result_files`中提取文件ID，然后[检索文件内容](https://platform.openai.com/docs/api-reference/files/retrieve-contents)来查看有关培训过程的指标。每个结果CSV文件都有以下列:`step`，`train_loss`，` train_accuracy`，`valid_loss`和`valid_mean_token_accuracy`。
（检索结果文件输出为乱码，用上面的job.event进行替代，查询得到所有的中间过程events并存储）
```
step,train_loss,train_accuracy,valid_loss,valid_mean_token_accuracy
1,1.52347,0.0,,
2,0.57719,0.0,,
3,3.63525,0.0,,
4,1.72257,0.0,,
5,1.52379,0.0,,
```

**虽然度量标准可以提供帮助，但是评估来自微调模型的样本可以提供最相关的模型质量感觉。我们建议在测试集上从基本模型和微调模型生成样本，并并排比较样本。** 理想情况下，测试集应该包括您可能在生产用例中发送给模型的输入的完整分布。**如果手动评估太耗时，可以考虑使用我们的eval库[Evals library](https://github.com/openai/evals)来自动化未来的评估。**






### [Iterating on data quality](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-data-quality)

如果微调工作的结果不像你预期的那样好，考虑以下方法来调整训练数据集:

* 收集针对剩余问题的示例
	* 如果模型在某些方面仍然不擅长，添加训练样例，直接向模型展示如何正确地做这些方面
* 仔细检查现有示例中的问题
	* 如果您的模型有语法、逻辑或样式问题，请检查您的数据是否有相同的问题。例如，如果模型现在说“我将为你安排这个会议”(当它不应该这样做的时候)，看看现有的例子是否教会模型说它可以做它不能做的新事情
* 考虑数据的平衡性和多样性
	* 如果数据中60%的助理回答说“我不能回答这个问题”，但在推理时间只有5%的回答应该这么说，你可能会得到过多的拒绝
* 确保你的训练示例包含回答所需的所有信息
	* 如果我们希望模型根据用户的个人特征来赞美他们，并且一个训练示例包括对之前对话中没有发现的特征的辅助赞美，那么模型可能会学习产生幻觉信息
* 看看训练示例中的一致性
	* 如果多人创建训练数据，那么模型的性能很可能会受到人与人之间的一致/一致性水平的限制。例如，在文本提取任务中，如果人们只同意提取的片段的70%，那么模型可能无法做得比这更好
* 确保你所有的训练样本都是相同的格式，正如你所期望的那样


### [Iterating on data quantity](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-data-quantity)
**一旦你对样本的质量和分布感到满意，你就可以考虑增加训练样本的数量。** 这有助于模型更好地学习任务，特别是在可能的“边缘情况”下。我们期望每次将训练样例的数量增加一倍，都会有类似的改进。你可以通过增加训练数据大小来粗略地估计预期的质量增益:

* 对当前数据集进行微调
* 对当前数据集的一半进行微调
* 观察两者之间的质量差距

一般来说，如果您必须做出权衡，那么少量的高质量数据通常比大量的低质量数据更有效。

### [Iterating on hyperparameters](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-hyperparameters)
我们允许您指定以下超参数:

- epochs
- learning rate multiplier
- batch size

**我们建议在初始训练时不指定任何这些，允许我们根据数据集大小为您选择默认值**，然后根据以下情况进行调整:

* 如果模型不像预期的那样遵循训练数据，则将epoch的个数增加1或2
	* 这对于只有一个理想完成(或一小部分相似的理想完成)的任务来说更常见。一些示例包括分类、实体提取或结构化解析。对于这些任务，您通常可以根据参考答案计算最终的精度度量。
* 如果模型的多样性低于预期，则将epoch的数量减少1或2
	* 这对于有很多可能完成的任务来说更常见
* 如果模型没有收敛，增加学习率乘数

您可以设置超参数，如下所示:

``` Python
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="file-abc123", 
  model="gpt-4o-mini", 
  hyperparameters={
    "n_epochs":2
  }
)
```