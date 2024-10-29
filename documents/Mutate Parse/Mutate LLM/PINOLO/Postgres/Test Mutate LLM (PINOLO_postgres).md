### Testing 说明
1. DB：针对postgres的logic bug检测
2. 变异策略：FixMDistinctL，FixMCmpOpU，FixMHaving1U，FixMOn1U
3. 微调数据集来源：pinolo，mysql->postgres（transfer llm）的结果sql，以jsonl文件存储，一行一条json格式的数据点。
4. 数据集选取
* 选取output2/mysql的简化后的"originalSqlsim"transfer为postgres语句
* 数据集大小：testing（100 x 4）
* 数据集每条sample包括：mutate name，mutate stragegy，IsUpper，mysql的(original sql，mutated sql)，postgres的(original sql，xxx)等等
5. 评估
* 执行成功率：postgres的所有变异结果的执行成功率
* 检测bug：变异前和变异后的结果集是否满足oracle（IsUpper: ((candidate.U^candidate.Flag)^1) == 1）
* 分析不满足oracle的测试项

## [Use a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/use-a-fine-tuned-model)
1. 执行mutate之前的原始sql语句并记录结果："transferredSqlsim_exec"
2. 使用微调好的mutate llm对原始sql进行mutate并记录结果："MutateLLM_Result"
``` Python
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="ft:gpt-4o-mini:my-org:custom_suffix:id",
  messages=[  
    {"role": "system", "content": str(role_prompt + 
    mutate_strategy_illustration[key])},  
    {"role": "user", "content": str(item["originalSqlsim_postgres"])}
  ]  
)
print(completion.choices[0].message)
```
3. 处理mutate llm得到的mutate result并记录结果："MutateLLM_OracleCheck"
```Python
# 计算oracle,IsUpper: ((candidate.U^candidate.Flag)^1) == 1  
# 运行"MutateLLM_Result"并保存运行结果    
# 比较该"MutateLLM_Result"的运行结果是否满足oracle  
```
4. 最终结果Json格式结果
```JSON
{  
  "index": 214,  
  "reportTime": "2022-12-23 13:09:33.473682952 +0800 CST m=+12091.538554476",  
  "bugId": 48,  
  "sqlId": 24318,  
  "mutationName": "FixMOn1U",  
  "isUpper": true,  
  "originalSql": "",  
  "mutatedSql": "",  
  "originalSqlsim": "",  
  "mutatedSqlsim": "",  
  "transferredSqlsim": "",  
  "MutateLLM_Message": [  
    {  "role": "system",  "content": ""    },  
    {  "role": "user",  "content": ""  }  
  ],  
  "transferredSqlsim_exec": {  
    "exec_result": "",  
    "error_message": "None"  
  },  
  "MutateLLM_Result": "",  
  "MutateLLM_OracleCheck": [  
    {  
      "isUpper": true,  
      "mutate_exec": {  
        "exec_result": "None",  
        "exec_time": "0",  
        "error_message": ""  
      },  
      "CheckOracle": {  
        "end": false,  
        "error": "None"  
      }  
    }  
  ]  
}
```


## 变异结果评估
1. 执行成功率：postgres的所有变异结果的执行成功率（部分变异后语句无法执行）
2. 检测bug：变异前和变异后的结果集是否满足oracle（IsUpper: ((candidate.U^candidate.Flag)^1) == 1）
3. 分析不满足oracle的测试项（无不满足orcale的测试项）

* "FixMCmpOpU"
```JSON
{  
    "ExecSuccessRate": "0.9504950495049505(96/101)",  
    "ExecFailIndexes": [  
        24,  
        36,  
        83,  
        133,  
        240  
    ],  
    "OracleFalseIndexes": []  
}


```

* "FixMDistinctL"
```JSON
{  
    "ExecSuccessRate": "0.9509043927648578(368/387)",  
    "ExecFailIndexes": [  
        78,  
        92,  
        97,  
        112,  
        137,  
        138,  
        139,  
        146,  
        147,  
        150,  
        160,  
        161,  
        172,  
        178,  
        181,  
        194,  
        210,  
        212,  
        222  
    ],  
    "OracleFalseIndexes": []  
}
```
* "FixMHaving1U"（暂时不测，因为pinolo误将having的用法和where混淆了）
```JSON
{  
    "ExecSuccessRate": "0.9(90/100)",  
    "ExecFailIndexes": [  
        79,  
        82,  
        83,  
        111,  
        120,  
        134,  
        161,  
        163,  
        168,  
        198  
    ],  
    "OracleFalseIndexes": []  
}
```
* "FixMOn1U"
```JSON
{  
    "ExecSuccessRate": "0.91(91/100)",  
    "ExecFailIndexes": [  
        2,  
        30,  
        37,  
        94,  
        132,  
        136,  
        158,  
        204,  
        214  
    ],  
    "OracleFalseIndexes": []  
}
```







