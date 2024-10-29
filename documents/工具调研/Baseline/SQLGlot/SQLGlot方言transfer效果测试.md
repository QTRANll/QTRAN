## Set up
### db
结合SQLGlot支持的db和PINOLO,SQLANCER支持的db，测试SQLGlot下面几种方言transfer的效果
1. Pinolo：mysql->postgres，mysql->duckdb
2. Sqlancer：mysql->postgres，mysql->duckdb
### 测试数据
1. Pinolo
* "init_output1_mysql_1_800_originalSql_random_200.json"
* "init_output2_mysql_1_800_originalSql_random_200.json"
2. Sqlancer


## 测试结果
### PINOLO
#### mysql->postgres
1. "init_output1_mysql_1_800_originalSql_random_200.json"
* 结果
``` JSON
origin 可执行比例:1.0(200/200)
transfer 成功比例:0.78(156/200)
transfer 可执行比例:0.0(0/200)
transfer 结果一致比例:0.0(0/200)
```

``` JSON
{  
  'UndefinedFunction': 81,  
  'ProgrammingError': 44,  
  'SyntaxError': 15,  
  'UndefinedObject': 48,  
  'InvalidDatetimeFormat': 2,  
  'CannotCoerce': 8,  
  'DatatypeMismatch': 1,  
  'UndefinedColumn': 1  
}
```


2. "init_output2_mysql_1_800_originalSql_random_200.json"
* 结果
``` JSON
origin 可执行比例:1.0(200/200)
transfer 成功比例:0.725(145/200)
transfer 可执行比例:0.0(0/200)
transfer 结果一致比例:0.0(0/200)
```

``` JSON
{  
  'ProgrammingError': 55,  
  'UndefinedFunction': 63,  
  'UndefinedObject': 57,  
  'CannotCoerce': 6,  
  'SyntaxError': 10,  
  'DatatypeMismatch': 8,  
  'UndefinedColumn': 1  
}
```


#### mysql->duckdb
1. "init_output1_mysql_1_800_originalSql_random_200.json"
* 结果
``` JSON
origin 可执行比例:1.0(200/200)
transfer 成功比例:0.78(156/200)
transfer 可执行比例:0.0(0/200)
transfer 结果一致比例:0.0(0/200)
```

``` JSON
{  
  'UndefinedColumn': 41,  
  'SyntaxError': 104,  
  'ProgrammingError': 44,  
  'UndefinedFunction': 7,  
  'UndefinedObject': 4  
}
```

2. "init_output2_mysql_1_800_originalSql_random_200.json"
* 结果
``` JSON
origin 可执行比例:1.0(200/200)
transfer 成功比例:0.725(145/200)
transfer 可执行比例:0.0(0/200)
transfer 结果一致比例:0.0(0/200)
```

``` JSON
{  
  'ProgrammingError': 55,  
  'UndefinedColumn': 30,  
  'SyntaxError': 103,  
  'UndefinedObject': 7,  
  'UndefinedFunction': 3,  
  'DatatypeMismatch': 2  
}
```




### SQLancer(ddl语句)

#### mysql->postgres
1. "init_output1_mysql_1_800_originalSql_random_200.json"

2. "init_output2_mysql_1_800_originalSql_random_200.json"


#### mysql->duckdb
1. "init_output1_mysql_1_800_originalSql_random_200.json"

2. "init_output2_mysql_1_800_originalSql_random_200.json"
