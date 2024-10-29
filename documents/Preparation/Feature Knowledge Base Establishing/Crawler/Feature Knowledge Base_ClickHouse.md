# Functions(finished)

## Functions文档相关链接
英文版本：
[Regular Functions | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/functions)
### Fucntions目录解释
对于functions的分类如下：
* Regular Functions
```
Arithmetic Functions.json
arrayJoin Functions.json
Arrays Functions.jsonl
Bit Functions.jsonl
Bitmap Functions.json
Comparison Functions.json
Conditional Functions.json!
Dates and Times Functions.jsonl
Dictionaries Functions.jsonl
Distance Functions.jsonl
Embedded Dictionaries Functions.jsonl
Encoding Functions.jsonl
Encryption Functions.jsonl
Files Functions.jsonl
Geo Functions.jsonl
Hash Functions.json
Introspection Functions.json
IP Addresses Functions.json
JSON Functions.jsonl
Logical Functions.jsonl
Maps Functions.jsonl
Mathematical Functions.jsonl
NLP (experimental) Functions.jsonl
Nullable Functions.jsonl
Other Functions.jsonl
Random Numbers Functions.isonl
Replacing in Strings Functions.json!
Rounding Functions.jsonl
Searching in Strings Functions.jsonl
Splitting Strings Functions.jsonl
Strings Functions.jsonl
Time Series Functions.json
Time Window Functions.jsonl
Tuples Functions.jsonl
Type Conversion Functions.jsonl
ULlD Functions.jsonl
uniqTheta Functions.jsonl
URLs Functions.jsonl
UUlDs Functions.jsonl
```
* Aggregate Functions
* Table Functions
* Window Functions


上述functions的网页组织形式有以下四种：
1. 以h2作为标题划分页面内多个函数，有一个h1上级标题（即页面顶部标题）：例如[Arithmetic Functions | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/arithmetic-functions)
2. 以h3作为标题划分页面内多个函数，有一个h2上级标题：例如[Functions for Working with Embedded Dictionaries | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/ym-dict-functions)
3. 页面内只有一个函数，Syntax和Example没有明确的划分：例如[arrayJoin function | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/array-join)


* 读取页面内所有h2标题个数h2_cnt和h3标题个数h3_cnt。
	* h2_cnt > 1，h3_cnt = 任意：情况1
	* h2_cnt = 1，h3_cnt = 0：情况1
	* h2_cnt = 1，h3_cnt != 0：情况2
	* h2_cnt = 0，h3_cnt = 任意：情况3

* [Aggregate Function Combinators | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators)暂时不做考虑
* category从页面上方的导航栏中提取
## 爬取Functions
### 数据结构

### 爬取过程




# SQL Statements(unfinished)
## SQL Statements相关链接

英文版本：
[SQL Reference | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference)
中文版本：
暂无
## SQL Statements元素解释
## 爬取SQL Documents

### 数据结构

### 爬取过程


# Operators(finished)

## Functions and Operators文档相关链接
英文版本：
[Operators | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/operators)
## 爬取Operators

### 需爬取的目标结构
Operators（function_crawler）: [Operators | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/operators)
EXISTS:[EXISTS | ClickHouse Docs](https://clickhouse.com/docs/en/sql-reference/operators/exists)
### 数据结构

### 爬取过程
1. Operators：直接用function_crawler
2. EXISTS：大部分以编码格式获取+小部分人工获取
* op的小类别以h2为标题，内部以h3为下属标题分小类别（小分类不做考虑），只考虑h2作为op的小类别，分块处理
* 依次处理h2小标题下的小块：若小块内没有p标签（txt内含-），则以function函数的处理方式（function的情形2）进行爬取；否则读取p标签的内容

















