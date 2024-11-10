# 数据集
## Pinolo
### output1-output4文件夹
* mariadb,mysql, tidb
```shell
${IMPOHOME}/output/mysql/task-1
  |-- bugs
     |-- bug-0-0-FixMHaving1U.log
     |-- bug-0-0-FixMHaving1U.json
  |-- maystable
  |-- sqlsim
  |-- unstable
  |-- result.json
  |-- task.log
  |-- output.data.sql

与${IMPOHOME}/output/mysql/task-x同级的文件夹中，包含所有task的配置文件 task-xxx-config.json
```

* oceanbase
```shell
${IMPOHOME}/output/mysql/task-1
  |-- bugs
     |-- bug-0-0-FixMHaving1U.log
     |-- bug-0-0-FixMHaving1U.json
  |-- result.json
  |-- task.log
  |-- output.data.sql


与${IMPOHOME}/output/mysql/task-1同级的文件夹中，包含所有task的配置文件 task-xxx-config.json
```

### output1-output4文件夹文件夹说明
* `bugs` 文件夹：位于`bugs`中的两种名为bug-`bugId`-`sqlId`-`mutationName`.log和bug-`bugId`-`sqlId`-`mutationName`.json的文件。这是检测到的逻辑错误。
* bug-`bugId`-`sqlId`-`mutationName`.log：保存突变名称、`originalSql`、原始结果、 `MutatedSql`、突变的结果，以及原始结果和我们期望的突变结果之间的关系(`IsUpper`)。`[IsUpper] true`是指变异后的结果应该 ⊆ 原结果。
* bug-`bugId`-`sqlId`-`mutationName`.json：bug-`bugId`-`sqlId`-`mutationName`.log 的Json格式
``` JSON
{
  "reportTime": "2022-12-23 09:53:25.383603754 +0800 CST m=+123.625818891",
  "bugId": 0,
  "sqlId": 317,
  "mutationName": "FixMDistinctL",
  "isUpper": false,
  "originalSql": "",
  "mutatedSql": ""
}
```
* `task.log`：任务日志文件，从中可以获得任务进度和错误消息。
* `result.json`：如果任务成功执行，我们将创建一个结果文件，从中您可以获得任务的开始时间(`startTime`)、结束时间(`endTime`)以及我们检测到的逻辑错误数量(`impoBugsNum`)。剩下的字段用于我们的调试，请忽略它们!
* `output.data.sql`, `output.rand.sql`：您还将看到两个sql文件`output.data.sql`, `output.rand.sql`。这是`go-randgen`自动生成的`ddlPath` 和`dmlPath`。
* maystable文件夹，unstable文件夹：两个文件夹中只有json和log这两种文件格式。有些bug是不稳定的，将每个bug的`originalSql`/ `MutatedSql`重复`execNum`(建议10次)，将稳定的bug保存到`maystable`目录，将不稳定的bug保存到`unstable`目录。
* sqlsim文件夹：尝试删除原始/变异sql语句中的每一个ast节点，如果 the implication oracle仍然可以检测到错误则进行简化。之后将在`task-0`下看到一个新文件夹`sqlsim`，其中包含一些友好的简化过的sql语句。


### 数据集处理和数据集格式（dataset processor.py）

将上面文件中的数据以下面的格式存储：
1.  output.data.sql：`go-randgen`将根据`zzPath`生成一个ddl sql文件`output.data.sql`，提取其中的database definition language语句存为ddl_mysql_like.json文件，已知output1-output4的ddl均相同。
2. 将bugs文件夹中的所有bug-`bugId`-`sqlId`-`mutationName`.json文件合并到一个名为bugs.json的文件中。格式如下：
``` JSON
bugId-sqlId-mutationName可以做到唯一
{
  "0-317-FixMDistinctL": {
    "reportTime": "2022-12-23 18:59:54.79919114 +0800 CST m=+33118.683823390",
    "bugId": 0,
    "sqlId": 317,
    "mutationName": "FixMDistinctL",
    "isUpper": false,
    "originalSql": "",
    "mutatedSql": "",
    "originalSqllength": integer
  }
}
```

3. 将sqlsim文件夹中的所有bug-`bugId`-`sqlId`-`mutationName`.json文件合并到一个名为sqlsim.json的文件中。格式如下：
``` JSON
bugId-sqlId-mutationName可以做到唯一
{
  "0-317-FixMDistinctL": {
    "reportTime": "2022-12-23 18:59:54.79919114 +0800 CST m=+33118.683823390",
    "bugId": 0,
    "sqlId": 317,
    "mutationName": "FixMDistinctL",
    "isUpper": false,
    "originalSql": "",
    "mutatedSql": "",
    "originalSqllength": integer
  }
}
```
4. 合并bugs.json和sqlsim.json得到task-xx_bugs_sqlsim.json文件，合并内容存储在dbname_merged文件夹中，得到如下格式：
``` JSON
{
  "0-317-FixMDistinctL": {
    "reportTime": "2022-12-23 18:59:54.79919114 +0800 CST m=+33118.683823390",
    "bugId": 0,
    "sqlId": 317,
    "mutationName": "FixMDistinctL",
    "isUpper": false,
    "originalSql": "",
    "mutatedSql": "",
    "originalSqllength": integer,
    "originalSqlsim": "",
    "mutatedSqlsim": "",
    "originalSqlsimlength": integer
}
```
5. 将得到所有sql和对应sqlsim的列表存为json格式（分别在每个dbname_merged文件夹下的originalSql_all.json和originalSqlsim_all.json文件中），便于transfer llm的测试


# Transfer LLM的构建_version1(未添加feature knowledge的初始版本，few-shot)
## Transfer LLM流程（Transfer LLM Test.py）
1. load data：分为两种加载方式，提取特定长度区间的sql语句，和随机选取特定数目的sql语句。
2. init data：为后续transfer  data的工作初始化结果文件，填入基本信息。
3. transfer data：转换origin db中每一条sql语句为target db的sql语句，并运行前后语句得到执行结果，进行结果对比。可以选择，温度值（temperature），是否根据执行结果的错误信息进行迭代（error_iteration），是否few-shot（FewShot），是否为优化后的sqlsim语句（sqls_type）。
4. evaluation：评估transfer llm的初步测试效果。

## 主要Prompt
1. 一次转换
``` Python
transfer_llm_string = """  Let's think step by step.Transfer the sql statement in {origin_db} database to the corresponding executable sql statement in {target_db} database to perform similar data operations.\  
{origin_db} statement: {sql_statement}\  
Here are some examples: {examples}\  
Answer the following information: {format_instructions}  
"""  
  
response_schemas = [  
    ResponseSchema(type="string", name="TransferSQL", description='The transferred SQL statement result.'),  
    ResponseSchema(type="string", name="Explanation", description='Explain the basis for the conversion.')  
]
```
2. 错误信息多次迭代
``` Python
iterate_llm_string = """  The corresponding executable SQL statement that you provided in your most recent response resulted in an error when executed. Please modify your most recent SQL statement response based on the error message.
error message:{error_message}  
Answer the following information: {format_instructions}  
"""  
  
iterate_response_schemas = [  
    ResponseSchema(type="string", name="TransferSQL", description='The new transferred SQL statement result after modification.'),  
    ResponseSchema(type="string", name="Explanation", description='Explain the basis for the conversion and modification.')  
]
```

## 结果输出
结果包括：
* 转换前语句Sql，对应运行结果"SqlExecResult"，运行报错"SqlExecError"
* transfer llm的结果列表"TransferResult"，花销列表"TransferCost"
* 转换后语句Sql的运行结果列表"TransferSqlExecResult"，运行报错列表"TransferSqlExecError"，运行结果与原sql的一致性列表"TransferSqlExecEqualities"
* 列表是为返回error进行迭代设计的，能记录多次迭代的过程值

``` JSON
[  
    {  
        "index": 0,  
        "origin_index": 80197,  
        "Sql": "",  
        "SqlLength": 675,  
        "SqlExecResult": "",  
        "SqlExecTime": "0.003152132034301758",  
        "SqlExecError": "None",  
        "TransferResult": [  
            {  
                "TransferSQL": "",  
                "Explanation": ""  
            }  
        ],  
        "TransferCost": [  
            {  
                "Total Tokens": 1062,  
                "Prompt Tokens": 710,  
                "Completion Tokens": 352,  
                "Total Cost (USD)": 0.0  
            }  
        ],  
        "TransferSqlExecResult": [  
            ""  
        ],  
        "TransferSqlExecTime": [  
            "0.002135038375854492"  
        ],  
        "TransferSqlExecError": [  
            "None"  
        ],  
        "TransferSqlExecEqualities": [  
            true  
        ]  
    }
]
```

## 初步测试结果
[[MariaDB to MySQL]]





