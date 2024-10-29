# Transfer LLM的构建
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
[[Transfer Phase/Transfer LLM with Feature Knowledge/Transfer Records/MariaDB to PostgresSQL|MariaDB to PostgresSQL]]






