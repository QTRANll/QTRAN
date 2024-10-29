## 部分修改
1.  ddl
* ddl初始化：只需要进行一次，在Connector.py文件中
* 修改postgres的ddl语句与mariadb的origin sql：postgres中的列名中不能包含小括号；在mariadb的ddl语句基础上确定postgres的ddl语句，其中列名中的小括号均改为下划线；修改传递给llm的origin sql，使其列名和postgres语句中的列名完全一样，再指示llm“转换过程中sql语句列名保持不变”，这样就能保证转换后的sql可执行
* 修改添加新的few-shot样例：mariadb to postgres
* 增加迭代次数到10：mariadb转postgres语法错误较多，需要多次修正
* 简化error-iteration过程中返回给llm的error message：原本返回的error message中包含完整sql语句，为无用信息

## 测试数据
1. output1，mariadb(mysql)转postgres

## 测试参数设置
temperature = 0.1
iteration_num = 10
1. 200条，error_iteration=False，sqls_type="origin"，FewShot=False  
2. 200条，error_iteration=False，sqls_type="simple"，FewShot=False  
3. 200条，error_iteration=False，sqls_type="origin"，FewShot=True
4. 200条，error_iteration=False，sqls_type="simple"，FewShot=True 
5. 200条，error_iteration=True，sqls_type="origin"，FewShot=False 
6. 200条，error_iteration=True，sqls_type="simple"，FewShot=False
7. 200条，error_iteration=True，sqls_type="origin"，FewShot=True 
8. 200条，error_iteration=True，sqls_type="simple"，FewShot=True 
9. 101条，error_iteration=True，sqls_type="simple"，FewShot=True ，length_range = [1,240)
备注：
* error_iteration = True的测试结果包含对应的error_iteration = False的结果（5-8分别包含1-4，因此只需要测5-8，不需要测1-4）
* 本次只测了9号的101条,长度区间在1-240的101条数据以及长度区间在240-400的100条数据
## 评估指标

1. 单次转换执行成功率：单次转换(未错误迭代)执行成功/总样本 + 错误迭代/总样本 = 1
2. 错误迭代执行成功率：错误迭代执行成功/错误迭代
3. 执行成功率：执行成功/总样本
4. 执行结果一致率：执行结果一致/执行成功，执行结果一致/总样本
5. 不同sql语句长度区间的成功率：区间有[1,400 ),[400,800),[800,1200),[1200,1600),[1600,+)

## 评估结论
1. sql语句的语法和语义正确性
* 长度较短的sql语句transfer通过多次error-iteration可以保证较高的语法正确性；而语义正确性难以保证，由于domain knowledge的缺少和语法元素之间映射的缺失 [[Transfer Phase/Transfer LLM without Feature Knowledge(Baseline)/Transfer Records/Semantic Correctness Analysis(MariaDB to PostgresSQL)]]
* 长度较长的sql语句transfer效果差，即使在多次error-iteration下执行成功率依然低（sql语句ast切分）

|                                                                                | 单次转换执行成功率      | 错误迭代执行成功率     | 执行成功率          | 执行结果一致率（执行成功） | 执行结果一致率（总样本）  | 平均迭代次数          |
| ------------------------------------------------------------------------------ | -------------- | ------------- | -------------- | ------------- | ------------- | --------------- |
| error_iteration=True，sqls_type="simple"，FewShot=True ，length_range = [1,240)   | 0.188 (19/101) | 0.963 (79/83) | 0.970 (98/101) | 0.000  (0/98) | 0.000 (0/101) | 3.396 (343/101) |
| error_iteration=True，sqls_type="simple"，FewShot=True ，length_range = [240,400) | 0.080 (8/100)  | 0.750 (69/92) | 0.770 (77/100) | 0.026 (2/77)  | 0.020 (2/100) |                 |

2. error_iteration执行错误类型
* iterated_fewshot_output1_mariadb_to_postgres_1_240_originalSqlsim_all.json
```JSON
sum = 248
{  
  'UndefinedFunction': 151,  
  'InvalidTextRepresentation': 40,  
  'SyntaxError': 17,  
  'AmbiguousFunction': 8,  
  'DatatypeMismatch': 15,  
  'UndefinedColumn': 5,  
  'InvalidDatetimeFormat': 1,  
  'CannotCoerce': 6,  
  'DivisionByZero': 3,  
  'InvalidParameterValue': 1,  
  'InvalidArgumentForPowerFunction': 1  
}
```
* iterated_fewshot_output1_mariadb_to_postgres_240_400_originalSqlsim_random_100.json
``` JSON
sum = 566
{  
  'IntervalFieldOverflow': 1,  
  'UndefinedFunction': 322,  
  'InvalidDatetimeFormat': 13,  
  'InvalidTextRepresentation': 72,  
  'UndefinedColumn': 5,  
  'DivisionByZero': 13,  
  'SyntaxError': 24,  
  'DatatypeMismatch': 22,  
  'DatetimeFieldOverflow': 20,  
  'AmbiguousFunction': 5,  
  'CannotCoerce': 51,  
  'NumericValueOutOfRange': 15,  
  'InvalidParameterValue': 2,  
  'UndefinedObject': 1  
}  
```
