> 原始查询合成与变异查询合成+查询验证不在同一个上下文中
>



<h1 id="Nb6aj">设计1</h1>
<h2 id="cyX3g">原始查询合成-系统提示词</h2>
需要嵌入的信息

+ 待测DMBS

```plain
你是一名数据库专家，擅长编写应用了指定的语法特征，且满足特定格式的{db_type} Query SQL。
```

```plain
You are a database expert skilled in writing {db_type} SQL queries that apply specific syntax features and meet a particular format.
```



<h2 id="VtlNy">原始查询合成-用户输入提示词</h2>
需要嵌入的信息

+ 数据库模式（DDLs+relations）
+ 语法特征的信息
+ 生成步骤
+ 输出格式



```plain
{DDLs}

{relations}

{feature_info}

{original_operation}

请逐步分析，严格按照下面的格式输出，分析过程不超过150词。
process: ```
<analysis process, e.g, Task1: xxx; Task2: xxx;...>
```
output: ```
{output_format}
```
```

```plain
{DDLs}

{relations}

{feature_info}

{original_operation}

Please analyze step by step and output strictly under the format bellow. Limit the analysis to no more than 150 words.
process: ```
<analysis process, e.g, Task1: xxx; Task2: xxx;...>
```
output: ```
{output_format}
```
```



<h2 id="L7nDf">变异查询合成-系统提示词</h2>
需要嵌入的信息：

+ 待测DBMS
+ test oracle原理说明



```plain
你是一名测试专家，擅长根据下面的test oracle来检查{db_type}中的Logical Bugs：
{test_oracle_expaination}
```

```plain
You are a testing expert skilled at detecting Logical Bugs in {db_type} using the following test oracle:
{test_oracle_expaination}
```



<h2 id="sXeNi">变异查询合成-用户输入提示词</h2>
需要嵌入的信息：

+ 数据库模式（DDLs+relations）
+ 生成步骤
+ 输出格式
+ 合成示例（few-shot）
+ 用户输入（原始查询合成结果）



```plain
{DDLs}

{relations}

{examples}

{mutation_operation}

{original_query_result}

请逐步分析，严格按照下面的格式输出，分析过程不超过150词。
process: ```
<analysis process, e.g, Task1: xxx; Task2: xxx;...>
```
output: ```
<generated mutation query>
```
```

```plain
{DDLs}

{relations}

{examples}

{mutation_operation}

{original_query_result}

Please analyze step by step and output strictly under the format bellow. Limit the analysis to no more than 150 words.
process: ```
<analysis process, e.g, Task1: xxx; Task2: xxx;...>
```
output: ```
<generated mutation query>
```
```



<h2 id="mSlWE">变异查询合成-变异查询验证</h2>
```plain
请逐步分析mutation query的生成过程是否违反生成步骤，分析过程不超过150词。
请严格按照下面的格式输出：
process: ```
<analysis process, e.g, Task 1 is valid/invalid, reason: xxx; Task 2 is valid/invalid, reason: xxx; ...>
```
output:```
<Yes if violation, otherwise No>
```
```

```plain
Please analyze step by step whether the generation process of the mutation query violates the generation steps. Limit the analysis to no more than 150 words.
Strictly follow the format below:
process: ```
<analysis process, e.g, Task 1 is valid/invalid, reason: xxx; Task 2 is valid/invalid, reason: xxx; ...>
```
output:```
<Yes if violation, otherwise No>
```
```

**上述提示词（变异查询验证）存在的问题如下：**

1. 分析SQL语句的内容，认为某个语法结构不符合语义要求，从而产生误报
2. LLM输出过于浅显，对不符合变异步骤要求的微小改动不敏感，从而产生漏报



**改进思路：**

1. 只检查格式是否满足生成步骤，不分析语法结构的合法性
2. 强调基于mutation query的内容进行分析



**改进方案：**

1. 逆向拆解mutation query的生成步骤，判断每一步具体的操作内容是否符合要求



**改进后的提示词如下：**

```plain
请回顾生成mutation query的每一步具体操作所生成的内容，判断操作和生成的内容是否违背相应的步骤，分析不过不超过150词。
注意，你只需要判断操作是否严格满足步骤的要求即可，不需要判断SQL的结构是否正确。
请严格按照下面的格式输出：
process: ```
<analysis process, e.g, Task 1: <detail operations, corresponding step, whether operation violate the step, reasoning>; Task 2: ...>
```
output:```
<Yes if violation, otherwise No>
```
```

```plain
Review the content generated at each step of creating the mutation query, and determine if the operations and generated content strictly follow the instructions. Your analysis should not exceed 150 words.
Note: You only need to check if the operations meet the step requirements, not the correctness of the SQL structure.
Output strictly in the following format:
process: ```
<analysis process, e.g., Task 1: <detailed operations, corresponding step, whether the operation violates the step, reasoning>; Task 2: ...>
```
output: ``` 
<Yes if violation, otherwise No>
```
```

****

<h2 id="uDMhO">NoREC test oracle</h2>
<h3 id="zlRs2">原理介绍</h3>
```plain
WHERE子句对查询性能有重要影响，含WHERE子句的Query一般都会被DBMS优化。记这样的Query查询出的记录数为n1，我们可通过移除WHERE子句并改为在表格的每条记录上执行WJERE子句的谓词的方式移除优化。统计移除优化后查询结果为TRUE的记录数量n2，n1和n2理论上应该相等，若不一致，则说明存在bugs。
```

```plain
The WHERE clause significantly impacts query performance, and queries with a WHERE clause are generally optimized by the DBMS. Let the number of records returned by such a query be n1. We can remove the optimization by eliminating the WHERE clause and applying its predicate to each record individually. Count the number of records where the result is TRUE as n2. Theoretically, n1 and n2 should be equal; if they are not, it indicates the presence of bugs.
```



<h3 id="vxCt9">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT <columns> FROM <tables> [<joins>] WHERE predicate [GROUP BY] [ORDER BY]`格式的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT <columns> FROM <tables> [<joins>] WHERE predicate [GROUP BY] [ORDER BY]`格式的base query
Task 3：逐项检查base query是否违反下述要求。若违反，则给出修正后的base query：
1. 必须使用上述特征
2. 必须含有WHERE子句
3. 不含子查询
4. 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
5. 不含DISTINCT子句
6. 不含聚合函数或窗口函数
Task 4: 使用COUNT来统计base query查询记录的数量，生成original query。示例如下：
- query 1: select Q1.c0 FROM Q1;
- original query of query 1 is: select count(*) from Q1;
- query 2: select Q1.c0 FROM Q1 GROUP BY Q1.c1;
- original query of query 2 is: select count(*) from (select Q1.c0 FROM Q1 GROUP BY Q1.c1) AS derived_table;
```

```plain
Task 1: Summarize how to use the mentioned syntax features in SQL formatted as `SELECT SELECT <columns> FROM <tables> [<joins>] WHERE predicate [GROUP BY] [ORDER BY]`.
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT <columns> FROM <tables> [<joins>] WHERE predicate [GROUP BY] [ORDER BY]`.
Task 3: Check the original query against the following requirements. If any are violated, provide a corrected version:
- Must use the mentioned features.
- Must include a WHERE clause.
- Must not contain subqueries.
- Must not use random functions (e.g., random number generation, current timestamp) or LIMIT.
- Must not include a DISTINCT clause.
- Must not include aggregate functions or window functions.
Task 4: Use COUNT to count the records returned by the base query and generate the original query. Examples:
- query 1: SELECT Q1.c0 FROM Q1;
- As query 1 dones't have GROUP BY clause, so original query for query 1 is: SELECT count(*) FROM Q1;
- query 2: SELECT Q1.c0 FROM Q1 GROUP BY Q1.c1;
- As query 2 has GROUP BY clause, so original query for query 2 is: SELECT count(*) FROM (SELECT Q1.c0 FROM Q1 GROUP BY Q1.c1) AS derived_table;
```



<h3 id="SwOSB">原始查询合成输出</h3>
```plain
base_query := <generated base query from Task 2/Task 3>
original_query := <generated original query from Task 4>
```



<h3 id="gZ6nW">变异查询合成步骤</h3>
```plain
Tasl 1: 从last conversation answer中完整提取出base query
Task 2：取出base query的WHERE子句的谓词p
Task 3：对base query进行重写，移除SELECT子句和WHERE子句的内容，并用(p IS TURE)作为SELECT子句的新内容，生成rewritten query
Task 4：使用SUM来统计rewritten query中查询结果为TRUE的记录数，生成mutation query
```

```plain
Task 1: Extract the base query entirely from last conversation answer.
Task 2: Extract the predicate p from the WHERE clause of the base query.
Task 3: Rewrite the base query by removing the contents of the SELECT and WHERE clauses, replacing the SELECT clause with (p IS TRUE), generating the rewritten query.
Task 4: Use SUM to count the number of TRUE results in the rewritten query, generating the mutation query.
```



<h3 id="W0ALG">变异查询合成的例子</h3>
```plain
Task 1: base query = SELECT Q1.c0, Q2.c1 FROM Q1, Q2 WHERE Q1.c2 + Q1.c3 >= Q2.c3
Task 2: The WHERE predicate p of base query is `Q1.c2 + Q1.c3 >= Q2.c3`
Task 3: rewritten query = SELECT (Q1.c2 + Q1.c3 >= Q2.c3 IS TRUE) AS count FROM Q1, Q2
Task 4: mutation query = SELECT SUM(count) FROM (SELECT (Q1.c2 + Q1.c3 >= Q2 IS TRUE) AS count FROM Q1, Q2) AS derived_table;
```



```plain
Task 1: base query = SELECT Q1.c0, Q2.c0, Q3.c0 FROM Q1, Q2, Q3 WHERE ABS(Q1.c1) > ABS(Q2.c1) GROUP BY Q1.c1;
Task 2: The WHERE predicate p of base query is `ABS(Q1.c1) > ABS(Q2.c1)`
Task 3: rewritten query = SELECT (ABS(Q1.c1) > ABS(Q2.c1) IS TRUE) AS count FROM Q1, Q2, Q3 GROUP BY Q1.c1;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT (ABS(Q1.c1) > ABS(Q2.c1) IS TRUE) AS count FROM Q1, Q2, Q3 GROUP BY Q1.c1) AS derived_table;
```



```plain
Task 1: base query = SELECT Q1.c0, Q2.c1 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c2 = Q3.c1 WHERE SIN(Q1.c4) < Q2.c5;
Task 2: The WHERE predicate p of base query is `SIN(Q1.c4) < Q2.c5`
Task 3: rewritten query = SELECT (SIN(Q1.c4) < Q2.c5 IS TRUE) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c2 = Q3.c1;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT (SIN(Q1.c4) < Q2.c5 IS TRUE) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c2 = Q3.c1) AS derived_table;
```



<h2 id="ySdsO">TLP: Where test oracle</h2>
<h3 id="ncPg2">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="zFTtG">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT <columns> FROM <tables> [<joins>]`格式的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT <columns> FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
1. 必须使用上述特征
2. 必须不含WHERE子句
3. 不含子查询
4. 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
5. 不含DISTINCT子句
6. 不含聚合函数或窗口函数
```

```plain
Task 1: Summarize how to use the mentioned syntax features in SQL formatted as `SELECT <columns> FROM <tables> [<joins>]`.
Task 2: Based on Task 1 and the given database schemas, generate an original query in the `SELECT <columns> FROM <tables> [<joins>]` format.
Task 3: Check the original query against the following requirements. If any are violated, provide a corrected version:
- Must use the mentioned features.
- Must not contain a WHERE clause.
- Must not contain subqueries.
- Must not use random functions (e.g., random number generation, current timestamp) or LIMIT.
- Must not include a DISTINCT clause.
- Must not include aggregate functions or window functions.
```



<h3 id="ET1SA">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="ycLZ6">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL to generate the mutation query.
```





<h3 id="vsoVW">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT Q1.c0, Q1.c2 FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
# original query = SELECT Q1.c0 + Q1.c1 FROM Q1;
Task 4: mutation query = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
```



```plain
Task 1: original query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS NOT NULL
Task 3: partitioning query1 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE p = Q2.c1 AND TRUE IS NOT NULL;
partitioning query2 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (p = Q2.c1 AND TRUE IS NOT NULL);
partitioning query3 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (p = Q2.c1 AND TRUE IS NOT NULL) IS NULL;
Task 4: mutation query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE p = Q2.c1 AND TRUE IS NOT NULL UNION ALL SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (p = Q2.c1 AND TRUE IS NOT NULL) UNION ALL SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (p = Q2.c1 AND TRUE IS NOT NULL) IS NULL;
```



```plain
Task 1: original query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
```





<h2 id="EWDnH">TLP: Where extended test oracle</h2>
<h3 id="VRxTP">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别使用AND加入到查询语句的WHERE过滤条件中，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE and the others FALSE.

Add these partition predicates with AND to the WHERE clause to create three partition queries. The results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="ao7Jm">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT <columns> FROM <tables> [<joins>] WHERE Pexisting`格式的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT <columns> FROM <tables> [<joins>] WHERE Pexisting`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须含有WHERE子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含聚合函数或窗口函数
```

```plain
Task 1: Summarize how to use the mentioned syntax features in SQL formatted as `SELECT <columns> FROM <tables> [<joins>] WHERE Pexisting`.
Task 2: Based on Task 1 and the given database schemas, generate an original query in the `SELECT <columns> FROM <tables> [<joins>] WHERE Pexisting` format.
Task 3: Check the original query against the following requirements. If any are violated, provide a corrected version:
- Must use the mentioned features.
- Must contain a WHERE clause.
- Must not contain subqueries.
- Must not use random functions (e.g., random number generation, current timestamp) or LIMIT.
- Must not include a DISTINCT clause.
- Must not include aggregate functions or window functions.
```



<h3 id="hs3IV">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="KdICV">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：在original query的WHERE子句的谓词的基础上，使用()包裹原有的谓词，然后再使用AND分别加上p，NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，得到mutation query
```

```plain
Task 1: Extract the original query entirely from the last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Wrap the original WHERE clause predicate in parentheses, then use AND to add p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL to generate the mutation query.
```



<h3 id="eThS2">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE Q1.c2 > 0;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query2 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c2 > 0) AND (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
```

```plain
Task 1: original query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE Q1.c2 IS NOT NULL;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND (Q2.c1 AND TRUE IS TRUE);
partitioning query2 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q1.c2 IS NOT NULL) AND (Q2.c1 AND TRUE IS TRUE) IS NULL;
```

```plain
Task 1: original query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q1.c1 + Q2.c2 <= Q3.c3;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND (Q3.c4 IS NULL);
partitioning query2 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND (Q3.c4 IS NULL) UNION ALL SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND NOT (Q3.c4 IS NULL) UNION ALL SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q1.c1 + Q2.c2 <= Q3.c3) AND (Q3.c4 IS NULL) IS NULL;
```



<h2 id="dxdsl">TLP: GROUP BY test oracle</h2>
<h3 id="rTzwF">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="h3na6">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT <columns> FROM <tables> [<joins>] GROUP BY <columns>`格式的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT <columns> FROM <tables> [<joins>] GROUP BY <columns>`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有HAVING子句
- GROUP BY后的<columns>必须来自SELECT后的<columns>
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含聚合函数或窗口函数
```

```plain
Task 1: Summarize how to use the mentioned syntax features in SQL formatted as `SELECT <columns> FROM <tables> [<joins>] GROUP BY <columns>`.
Task 2: Based on Task 1 and the given database schemas, generate an original query in the `SELECT <columns> FROM <tables> [<joins>] GROUP BY <columns>` format.
Task 3: Check the original query against the following requirements. If any are violated, provide a corrected version:
- Must use the mentioned features.
- Must not contain a WHERE clause.
- Must not contain a HAVING clause.
- The <columns> behind GROUP BY must come from the <columns> in SELECT clause.
- Must not contain subqueries.
- Must not use random functions (e.g., random number generation, current timestamp) or LIMIT.
- Must not include a DISTINCT clause.
- Must not include aggregate functions or window functions.
```



<h3 id="znQy5">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="DOhJN">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION将三个分区查询合并，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION to generate the mutation query.
```



<h3 id="vRICj">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT Q1.c0 + Q1.c1 FROM Q1 GROUP BY Q1.c0;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 GROUP BY Q1.c0;
partitioning query2 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) GROUP BY Q1.c0;
partitioning query3 = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL GROUP BY Q1.c0;
Task 4: mutation query = SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 GROUP BY Q1.c0 UNION SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) GROUP BY Q1.c0 UNION SELECT Q1.c0 + Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL GROUP BY Q1.c0;
```

```plain
Task 1: original query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 GROUP BY Q2.c1;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE GROUP BY Q2.c1;
partitioning query2 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) GROUP BY Q2.c1;
partitioning query3 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL GROUP BY Q2.c1;
Task 4: mutation query = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE GROUP BY Q2.c1 UNION SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) GROUP BY Q2.c1 UNION SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL GROUP BY Q2.c1;
```

```plain
Task 1: original query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2, Q3.c1 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 GROUP BY Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2, Q3.c1 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL GROUP BY Q3.c1;
partitioning query2 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2, Q3.c1 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) GROUP BY Q3.c1;
partitioning query3 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2, Q3.c1 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL GROUP BY Q3.c1;
Task 4: mutation query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2, Q3.c1 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL GROUP BY Q3.c1 UNION SELECT Q1.c0, SIN(Q1.c1), Q2.c2, Q3.c1 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) GROUP BY Q3.c1 UNION SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2, Q3.c1 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL GROUP BY Q3.c1;
```



<h2 id="l9AWE">TLP: DISTINCT test oracle</h2>
<h3 id="hAocn">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="SfWxt">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT DISTINCT <columns> FROM <tables> [<joins>]`格式的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT DISTINCT <columns> FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须含DISTINCT关键字
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含聚合函数或窗口函数
```

```plain
Task 1: Summarize how to use the mentioned syntax features in SQL formatted as `SELECT DISTINCT <columns> FROM <tables> [<joins>]`.
Task 2: Based on Task 1 and the given database schemas, generate an original query in the `SELECT DISTINCT <columns> FROM <tables> [<joins>]` format.
Task 3: Check the original query against the following requirements. If any are violated, provide a corrected version:
- Must use the mentioned features.
- Must not contain a WHERE clause.
- Must include a DISTINCT keyword.
- Must not contain subqueries.
- Must not use random functions (e.g., random number generation, current timestamp) or LIMIT.
- Must not include aggregate functions or window functions.
```



<h3 id="ThhlM">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="nvv21">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询。分区查询中的DISTINCT关键字可加可不加。
Task 4：使用UNION将三个分区查询合并，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.The DISTINCT keyword in the partitioned query is optional.
Task 4: Combine the three partitioned queries using UNION to generate the mutation query.
```



<h3 id="LDCZF">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT DISTINCT Q1.c0, Q1.c1 FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT Q1.c0, Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT DISTINCT Q1.c0, Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT Q1.c0, Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT Q1.c0, Q1.c1 FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION SELECT DISTINCT Q1.c0, Q1.c1 FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ELECT Q1.c0, Q1.c1 FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
```

```plain
Task 1: original query = SELECT DISTINCT Q1.c0, ABS(Q2.c1) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT DISTINCT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT DISTINCT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT DISTINCT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION SELECT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION SELECT DISTINCT Q1.c0, ABS(Q2.c1) FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
```

```plain
Task 1: original query = SELECT DISTINCT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION SELECT Q1.c0, SIN(Q1.c1), Q2.c2 FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
```



<h2 id="SE7LY">TLP: MIN test oracle</h2>
<h3 id="ZXx2A">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="wxHIS">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT MIN(<e>) AS count FROM <tables> [<joins>]`格式（e表示表达式）的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT MIN(<e>) AS count FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有GROUP子句和HAVING子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含窗口函数
```

```plain
Task 1: Summarize how to use the specified syntax features in SQL with the format `SELECT MIN(<e>) AS count FROM <tables> [<joins>]` (where e is an expression).
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT MIN(<e>) AS count FROM <tables> [<joins>]`.
Task 3: Check the original query for the following violations. If any are found, provide a corrected query:
- Must use the specified syntax features.
- Must not contain a WHERE clause.
- Must not contain GROUP BY or HAVING clauses.
- No subqueries.
- No random functions (e.g., random number generation, current timestamp) or LIMIT.
- No DISTINCT clause.
- No window functions.
```



<h3 id="hUTEK">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="q5HIF">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，并对合并的结果使用MIN进行查询，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL, then apply MIN to the result to generate the mutation query.
```



<h3 id="hCXqe">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT MIN(Q1.c0 + Q1.c1) FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT MIN(count) FROM (SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT MIN(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT MIN(ABS(Q1.c0)) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT MIN(count) FROM (SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION ALL SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT MIN(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT MIN(Q1.c0) FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT MIN(count) FROM (SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT MIN(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL) AS derived_table;
```



<h2 id="mQuKP">TLP: MAX test oracle</h2>
<h3 id="u9ERS">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="ABQ2O">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT MAX(<e>) AS count FROM <tables> [<joins>]`格式（e表示表达式）的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT MAX(<e>) AS count FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有GROUP子句和HAVING子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含窗口函数
```

```plain
Task 1: Summarize how to use the specified syntax features in SQL with the format `SELECT MAX(<e>) AS count FROM <tables> [<joins>]` (where e is an expression).
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT MAX(<e>) AS count FROM <tables> [<joins>]`.
Task 3: Check the original query for the following violations. If any are found, provide a corrected query:
- Must use the specified syntax features.
- Must not contain a WHERE clause.
- Must not contain GROUP BY or HAVING clauses.
- No subqueries.
- No random functions (e.g., random number generation, current timestamp) or LIMIT.
- No DISTINCT clause.
- No window functions.
```



<h3 id="iqs7B">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="aUVBT">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，并对合并的结果使用MAX进行查询，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL, then apply MAX to the result to generate the mutation query.
```



<h3 id="Hqog1">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT MAX(Q1.c0 + Q1.c1) FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT MAX(count) FROM (SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT MAX(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT MAX(ABS(Q1.c0)) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT MAX(count) FROM (SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION ALL SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT MAX(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT MAX(Q1.c0) FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT MAX(count) FROM (SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT MAX(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL) AS derived_table;
```



<h2 id="p1cag">TLP: SUM test oracle</h2>
<h3 id="BqeZU">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="YpylI">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT SUM(<e>) AS count FROM <tables> [<joins>]`格式（e表示表达式）的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT SUM(<e>) AS count FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有GROUP子句和HAVING子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含窗口函数
```

```plain
Task 1: Summarize how to use the specified syntax features in SQL with the format `SELECT SUM(<e>) AS count FROM <tables> [<joins>]` (where e is an expression).
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT SUM(<e>) AS count FROM <tables> [<joins>]`.
Task 3: Check the original query for the following violations. If any are found, provide a corrected query:
- Must use the specified syntax features.
- Must not contain a WHERE clause.
- Must not contain GROUP BY or HAVING clauses.
- No subqueries.
- No random functions (e.g., random number generation, current timestamp) or LIMIT.
- No DISTINCT clause.
- No window functions.
```



<h3 id="SyEiT">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="TAVCI">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，并对合并的结果使用SUM进行查询，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL, then apply SUM to the result to generate the mutation query.
```





<h3 id="Hzk14">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT SUM(Q1.c0 + Q1.c1) FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT SUM(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT SUM(ABS(Q1.c0)) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION ALL SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT SUM(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT SUM(Q1.c0) FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT SUM(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL) AS derived_table;
```



<h2 id="yS8ly">TLP: COUNT test oracle</h2>
<h3 id="TI0ZS">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="P0KtJ">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT COUNT(<e>) AS count FROM <tables> [<joins>]`格式（e表示表达式）的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT COUNT(<e>) AS count FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有GROUP子句和HAVING子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含窗口函数
```

```plain
Task 1: Summarize how to use the specified syntax features in SQL with the format `SELECT COUNT(<e>) AS count FROM <tables> [<joins>]` (where e is an expression).
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT COUNT(<e>) AS count FROM <tables> [<joins>]`.
Task 3: Check the original query for the following violations. If any are found, provide a corrected query:
- Must use the specified syntax features.
- Must not contain a WHERE clause.
- Must not contain GROUP BY or HAVING clauses.
- No subqueries.
- No random functions (e.g., random number generation, current timestamp) or LIMIT.
- No DISTINCT clause.
- No window functions.
```



<h3 id="dc1sG">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="YoeJl">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：为original query添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，并对合并的结果使用SUM进行查询，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Add a WHERE clause to the original query using the predicates p, NOT p and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL, then apply SUM to the result to generate the mutation query.
```



<h3 id="TCtiV">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT COUNT(Q1.c0 + Q1.c1) FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT COUNT(Q1.c0 + Q1.c1) AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT COUNT(ABS(Q1.c0)) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION ALL SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT COUNT(ABS(Q1.c0)) AS count FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT COUNT(Q1.c0) FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT SUM(count) FROM (SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT COUNT(Q1.c0) AS count FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL) AS derived_table;
```



<h2 id="HczcB">TLP: AVG test oracle</h2>
<h3 id="WPiYq">原理介绍</h3>
```plain
设有任意谓词表达式p，由于SQL是基于三元布尔逻辑的，将表中的某一记录r代入p后，p(r)的值有且仅有TRUE、FALSE和NULL三种。基于此，我们可构造三个分区谓词，即：p，NOT p和p IS NULL，r只会使其中一个分区谓词的结果为TRUE，其余均为FALSE。
将这三个分区谓词分别作为查询语句的WHERE过滤条件，得到三个分区查询语句，执行后得到三个分区查询结果。基于上述性质，三个分区查询结果是互斥的，且合并后应该等于原始查询结果，若不相等，则说明存在bugs。
```

```plain
Given any predicate expression p, since SQL uses ternary Boolean logic, substituting a record r into p will result in one of three values: TRUE, FALSE, or NULL. Based on this, we can construct three partition predicates: p, NOT p, and p IS NULL, where r will make only one predicate TRUE, and the others FALSE.

Use these partition predicates as WHERE filters in queries to obtain results. These results should be mutually exclusive and, when combined, equal the original query result. If not, there are bugs.
```



<h3 id="jesCw">原始查询合成步骤</h3>
```plain
Task 1: 总结如何在`SELECT AVG(<e>) FROM <tables> [<joins>]`格式（e表示表达式）的SQL中使用上述的语法特征
Task 2：基于Task 1和上述的数据库模式，生成满足`SELECT AVG(<e>) FROM <tables> [<joins>]`格式的original query
Task 3：逐项检查original query是否违反下述要求。若违反，则给出修正后的original query：
- 必须使用上述特征
- 必须不含有WHERE子句
- 必须不含有GROUP子句和HAVING子句
- 不含子查询
- 不含随机性函数（如随机数字生成、获取当前时刻）和LIMIT
- 不含DISTINCT子句
- 不含窗口函数
```

```plain
Task 1: Summarize how to use the specified syntax features in SQL with the format `SELECT AVG(<e>) FROM <tables> [<joins>]` (where e is an expression).
Task 2: Based on Task 1 and the given database schemas, generate an original query in the format `SELECT AVG(<e>) FROM <tables> [<joins>]`.
Task 3: Check the original query for the following violations. If any are found, provide a corrected query:
- Must use the specified syntax features.
- Must not contain a WHERE clause.
- Must not contain GROUP BY or HAVING clauses.
- No subqueries.
- No random functions (e.g., random number generation, current timestamp) or LIMIT.
- No DISTINCT clause.
- No window functions.
```



<h3 id="dZZAD">原始查询合成输出</h3>
```plain
original_query := <generated original query from Task 2/Task 3>
```



<h3 id="y3S6F">变异查询合成步骤</h3>
```plain
Task 1： 从last conversation answer中完整提取出original query
Task 2：基于提供的数据库模式，随机生成谓词p
Task 3：将original query的SELECT子句的内容替换为`SELECT SUM(<e>) AS s, COUNT(<e>)`（e来自AVG(e)），并添加WHERE子句，WHERE子句的谓词分别为p、NOT p和p IS NULL（p来自Task 2），以此得到三个分区查询
Task 4：使用UNION ALL将三个分区查询合并，并对合并的结果使用`SUM(s)/SUM(c)`进行查询，得到mutation query
```

```plain
Task 1: Extract the original query entirely from last conversation answer.
Task 2: Randomly generate a predicate p based on the provided database schemas.
Task 3: Replace the SELECT clause in the original query with SELECT SUM(<e>) AS s, COUNT(<e>) (where e comes from AVG(e)), and add a WHERE clause with predicates p, NOT p, and p IS NULL (from Task 2) to create three partitioned queries.
Task 4: Combine the three partitioned queries using UNION ALL, and apply SUM(s)/SUM(c) to generate the mutation query.
```



<h3 id="Kh71W">变异查询合成的例子</h3>
```plain
Task 1: original query = SELECT AVG(Q1.c0 + Q1.c1) FROM Q1;
Task 2: p = Q1.c1 + Q2.c3 > Q1.c2
Task 3: partitioning query1 = SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2;
partitioning query2 = SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2);
partitioning query3 = SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL;
Task 4: mutation query = SELECT SUM(s)/SUM(c) FROM (SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c FROM Q1 WHERE Q1.c1 + Q2.c3 > Q1.c2 UNION ALL SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c AS count FROM Q1 WHERE NOT (Q1.c1 + Q2.c3 > Q1.c2) UNION ALL SELECT SUM(Q1.c0 + Q1.c1) AS s, COUNT(Q1.c0 + Q1.c1) AS c AS count FROM Q1 WHERE (Q1.c1 + Q2.c3 > Q1.c2) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT AVG(ABS(Q1.c0)) FROM Q1, Q2;
Task 2: p = Q2.c1 AND TRUE IS TRUE
Task 3: partitioning query1 = SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE;
partitioning query2 = SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE);
partitioning query3 = SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL;
Task 4: mutation query = SELECT SUM(s)/SUM(c) FROM (SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE Q2.c1 AND TRUE IS TRUE UNION ALL SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE NOT (Q2.c1 AND TRUE IS TRUE) UNION ALL SELECT SUM(ABS(Q1.c0)) AS s, COUNT(ABS(Q1.c0)) AS c FROM Q1, Q2 WHERE (Q2.c1 AND TRUE IS TRUE) IS NULL) AS derived_table;
```

```plain
Task 1: original query = SELECT AVG(Q1.c0) FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1;
Task 2: p = Q3.c4 IS NULL
Task 3: partitioning query1 = SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL;
partitioning query2 = SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL);
partitioning query3 = SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL;
Task 4: mutation query = SELECT SUM(s)/SUM(c) FROM (SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE Q3.c4 IS NULL UNION ALL SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE NOT (Q3.c4 IS NULL) UNION ALL SELECT SUM(Q1.c0) AS s, COUNT(Q1.c0) AS c FROM Q1, Q2 LEFT JOIN Q3 ON Q1.c0 = Q3.c1 WHERE (Q3.c4 IS NULL) IS NULL) AS derived_table;
```



<h2 id="jdNub">PINOLO: DISTINCT upper test oracle</h2>


<h2 id="BO7vP">PINOLO: DISTINCT lower test oracle</h2>


<h2 id="gFNzz">PINOLO: Compare Operator upper test oracle</h2>


<h2 id="aWf4g">PINOLO: Compare Operator lower test oracle</h2>


<h2 id="QqXdU">PINOLO: UNION upper test oracle</h2>


<h2 id="peVgy">PINOLO: UNION lower test oracle</h2>


<h2 id="mS1fB">PINOLO: IN NULL upper test oracle</h2>




<h2 id="NYjpN">PINOLO: WHERE upper test oracle</h2>


<h2 id="TsPgM">PINOLO: WHERE lower test oracle</h2>




<h2 id="B0Xdj">PINOLO: UNION ALL lower test oracle</h2>




<h2 id="ID9FH">PINOLO: LIKE upper test oracle</h2>


<h2 id="Z4bJf">PINOLO: LIKE lower test oracle</h2>




<h2 id="R3Yer">PINOLO: Regular Expression upper test oracle</h2>


<h2 id="Z5iJl">PINOLO: Regular Expression lower test oracle</h2>






