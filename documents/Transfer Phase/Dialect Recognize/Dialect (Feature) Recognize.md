## 1 Overview
### 1.1 Set Up
1. 假设 transfer a_db to b_db
2. 识别的dialect features范围：暂定只考虑fucntions（分词后function name易识别，且‘UndefinedFunction’占执行报错的较大比例，至少60%，见  [[Transfer Phase/Transfer LLM without Feature Knowledge(Baseline)/Transfer Records/MariaDB to PostgresSQL#评估结论]]）和operators（operators个数较少)，不考虑statements
3. a_db = mariadb, b_db = postgres
4. 测试集：长度区间在1-240的101条数据以及长度区间在240-400的100条数据（见[[Transfer Phase/Transfer LLM without Feature Knowledge(Baseline)/Transfer Records/MariaDB to PostgresSQL]]）
### 1. 2 Procedure
1. Potential Features Refiner：借助SQLGlot的词法分析器（sqlglot.tokenize函数）对a_db的sql语句做简单的词法分析，提取分词结果中疑似为functions和operators的分词片段
2. Potential Dialect Features Rocognizer：遍历上一步识别得到的potential features(functions+operators)，对每一个feature进行以下操作。
* 在a_db的feature knowledge base中检索到该feature，获取该feature的样例sql
* 在b_db引擎上执行该样例sql语句，若无法执行则认为是a_db相对于b_db的potential dialect features
## 2 Detailed Realization
### 2.1 Potential Features Refiner
从a_db=mariadb的测试集每条sql语句中提取potential features，测试集有两个，分别是：长度区间在1-240的101条数据，长度区间在240-400的100条数据（见[[Transfer Phase/Transfer LLM without Feature Knowledge(Baseline)/Transfer Records/MariaDB to PostgresSQL]]）
#### 2.1.1 Functions
同时满足以下条件的认为是potential function name
* sqlglot.TokenType.VAR后一个字符为sqlglot.TokenType.L_PAREN，且左边字符不为sqlglot.TokenType.UNKNOWN（？？），则认为是potential functions
* 特殊
	* LEFT被sqlglot识别为关键字TokenType.LEFT，而LEFT也可以是mariadb中的函数名
#### 2.1.2 Operators
* 若不在sqlglot内置【[sqlglot.tokens API documentation](https://sqlglot.com/sqlglot/tokens.html#TokenType.GT)】的部分keywords和data types范围内，则认为是potential operators
### 2. 2 Potential Dialect Features Rocognizer
遍历a_db上origin_sql的所有potential features(functions+operators)，对每一个feature进行以下操作。
* 在a_db的feature knowledge base processed中检索到该feature
	* 若未检索到该feature，保守认为该feature为方言
	* 若检索到该feature，选出最短的一个example sql作为用于方言检测的example sql。
* 在b_db引擎上执行该用于方言检测的example sql
	* 若无法执行则认为是dialect（虽然其中可能包括由于example sql中其他feature造成的无法执行，这里暂且粗略认为是方言）。
* 结果统计：针对a_db的所有测试语句，结果如下
```
functions：
feature总个数133
feature在knowledge base中检索失败的个数2
feature中方言的个数75
feature中非方言的个数58
以下为非方言的feature name：
['PI', 'LEFT', 'COLLATION', 'COT', 'CHAR_LENGTH', 'ASIN', 'COS', 'COLLATION', 'CEILING', 'ACOS', 'FLOOR', 'CEIL', 'LOG10', 'COLLATION', 'COLLATION', 'COLLATION', 'COT', 'PI', 'PI', 'SIGN', 'LOG10', 'CEILING', 'PI', 'PI', 'TAN', 'PI', 'CEILING', 'COLLATION', 'ASIN', 'BIT_LENGTH', 'LN', 'BIT_LENGTH', 'COLLATION', 'TAN', 'DEGREES', 'COLLATION', 'COS', 'COLLATION', 'PI', 'COLLATION', 'TAN', 'PI', 'COLLATION', 'COLLATION', 'COLLATION', 'COLLATION', 'COLLATION', 'RADIANS', 'ATAN', 'COLLATION', 'ROUND', 'DEGREES', 'COLLATION', 'PI', 'REVERSE', 'SQRT', 'ACOS', 'SIGN']



operators：
feature总个数164
feature在knowledge base中检索失败的个数12
feature中方言的个数18
feature中非方言的个数146
```




