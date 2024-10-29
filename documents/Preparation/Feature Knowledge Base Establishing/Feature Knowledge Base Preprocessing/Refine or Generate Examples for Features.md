## 1 Overview
### 1.1 Set Up
1. 假设 transfer a_db to b_db
2. a_db = mariadb, b_db = postgres
### 1. 2 Procedure
1. Effective SQLs Refiner：从feature的Examples字符串中提取出可执行的sql语句。
2. Effective SQLs Generator：对于提取effective sql失败的feature，利用llm为该feature生成一个简单的effective sql。
## 2 Detailed Realization
预处理feature knowledge base中functions和operators的所有feature（主要是预处理Examples字符串并提取/生成可执行的sql语句），具体步骤如下。
### 2.1 Effective SQLs Refiner
从feature的Examples字符串中提取出可执行的sql语句
1. 丢弃description和feature语法均为空的feature文件（丢弃/总数=34/440）。这部分丢弃的feature多为A synonym for xxx（链接），其详细信息在其同义feature文件（在feature语法描述中已包含）中已经被包含，所以可以直接丢弃。
2. 提取examples字符串中的sql语句(利用正则表达式匹配)  ，只保留包含feature name的sql语句（认为不包含feature name不算feature的样例sql）。
3. 执行提取出来的sql语句，只保留可执行的sql语句作为effective sqls。将提取出来的effective sqls更新到feature knowledge base processed文件夹中。
4. 提取结果
```
Functions
总features文件个数:440
总有效features（feature和description信息齐全）个数:406
重复的features（同义的算作一个）个数:34
未提取到effective sqls的feature数量:123
官网未提供Example字符串的feature数量:55

Operators
总features文件个数:43
总有效features（feature和description信息齐全）个数:41
重复的features（同义的算作一个）个数:0
未提取到effective sqls的feature数量:1
官网未提供Example字符串的feature数量:0

```
5. 提取过程注意点和遇到的问题
* Example字符的分割：一个Example字符内包含多个sql语句，有的是独立sql，有的是一组sqls。假设均为独立sql（因为一组sqls难以区分与划分。即使有被遗漏的有效sql，可以后续由llm生成简单样例）。
* 提取过程中遇到的数据库自动断连问题：(pymysql.err.OperationalError) (2013, 'Lost connection to MySQL server during query')，设置容器自动重启+强制等3s（见[设置docker开机自启动，并设置容器自动重启_小雅全家桶容器重启](https://blog.csdn.net/chj_1224365967/article/details/109029856)）
* 提取失败的原因分析：官网文档未提供Example+提取的sql不可执行
	1. mariadb docker版本较低：mariadb的最新版本已经更新到11.6.1，但是docker镜像的mariadb最高版本为11.5.2。部分function不支持11.6.0以前版本，比如vector functions（[VEC_ToText - MariaDB Knowledge Base](https://mariadb.com//kb/en/vec_totext/)）
	2. 正则表达式匹配sql语句遗漏：Example字符串中的部分sql语句不包含在匹配模式中，正则表达式没有匹配到，比如ENCODE（[ENCODE - MariaDB Knowledge Base](https://mariadb.com//kb/en/encode/)）。可以在后续利用llm生成对应的example sql，llm根据这些现有例子直接提取出来或者模仿给出一个。
	3. TABLE未定义：在未定义的TABLE上执行，且Example中未包含ddl语句（[COLUMN_CREATE - MariaDB Knowledge Base](https://mariadb.com//kb/en/column_create/)）
	4. TABLE已定义：Example字符串中首先包含了一组ddl语句进行table设置。这类操作较为复杂，而我们的目标是寻找最简单的只包括feature的sql。（[CUME_DIST - MariaDB Knowledge Base](https://mariadb.com//kb/en/cume_dist/)）。这些复杂语句简化后可以在空数据库上运行，比如[DES_ENCRYPT - MariaDB Knowledge Base](https://mariadb.com//kb/en/des_encrypt/)，[JSON_NORMALIZE - MariaDB Knowledge Base](https://mariadb.com//kb/en/json_normalize/)
	5. 部分函数需要打开特定的数据库权限：如SELECT BINLOG_GTID_POS(\"master-bin.000001\", 600)，报错如下，You are not using binary logging。（[BINLOG_GTID_POS - MariaDB Knowledge Base](https://mariadb.com//kb/en/binlog_gtid_pos/)）
	6. 部分函数已经被新版本和未来版本丢弃：比如DES_ENCRYPT（[DES_ENCRYPT - MariaDB Knowledge Base](https://mariadb.com//kb/en/des_encrypt/)）
	7. 部分函数的参数为外部的文件或者数据源：例如[JSON_SET - MariaDB Knowledge Base](https://mariadb.com//kb/en/json_set/)，[LOAD_FILE - MariaDB Knowledge Base](https://mariadb.com//kb/en/load_file/)，例如Spider Functions的[SPIDER_BG_DIRECT_SQL - MariaDB Knowledge Base](https://mariadb.com//kb/en/spider_bg_direct_sql/)。
	8. 部分函数对参数和表格有特定的约束：尤其是数学相关的functions（Geographic Functions）

### 2.2 Effective SQLs Generator
对于提取effective sql失败的feature：利用llm为该feature生成一个简单的effective sql，分以下两个步骤：
* Generate Step 1：不提供基本表进行生成
* Generate Step 2：对于前一步生成example sql无效的情况，再提供基本表（ddl语句搭建的）进行生成。
#### Effective SQLs Generator(version1)
1. Generate Step 1：不提供基本表 + 不提供feature的examples。指导llm生成一个最简单的sql，尽量不依赖于任何表格和外部资源
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```

2. Generate Step 2：提供基本表 + 不提供feature examples。指导llm生成一个sql，可以依赖于基本表和提供的examples
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```
3. 综合结果
```
Functions
提取effective sql失败的个数:123
生成effective sql第一步失败的个数:24
生成effective sql第二步失败的个数:11


最终生成effective sql失败的如下:
BINLOG_GTID_POS.json --5
COLUMN_ADD.json
COLUMN_DELETE.json
COLUMN_EXISTS.json
COLUMN_GET.json
COLUMN_JSON.json
CROSSES.json  --8
MATCH AGAINST.json 
OVERLAPS.json
SETVAL.json
SPIDER_COPY_TABLES.json --7

原因有:
1. llm生成的字符串没有按照提示词要求只给出一个sql语句，而是给出了一串sql（包含多个）
2. 加上examples以后，不按照指令生成指定基本表上的sql语句，而是继续仿照examples生成sqls
```

```
Operators
未提取到effective sqls的feature数量:1
生成sql(无基本表)失败的feature数量:1
生成sql(有基本表)失败的feature数量:0

原因：
1."This result object does not return rows. It has been closed automatically."也算执行成功。
```


#### Effective SQLs Generator(version2，在version1的基础上为Step2添加feature examples)
1. Generate Step 1：不提供基本表 + 不提供feature的examples。指导llm生成一个最简单的sql，尽量不依赖于任何表格和外部资源
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```

2. Generate Step 2：提供基本表 + 提供feature examples。指导llm生成一个sql，可以依赖于基本表和提供的examples
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```

3. 综合结果
```
Functions
提取effective sql失败的个数:123
生成effective sql第一步失败的个数:24
生成effective sql第二步失败的个数:13
```

#### Effective SQLs Generator(version3，在version1的基础上为Step1添加feature examples)
1. Generate Step 1：不提供基本表 + 提供feature的examples。指导llm生成一个最简单的sql，尽量不依赖于任何表格和外部资源
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```

2. Generate Step 2：提供基本表 + 不提供feature examples。指导llm生成一个sql，可以依赖于基本表和提供的examples
```
temperature=0.3,
model="gpt-4o-mini",
max_cnt = 4
```

3. 综合结果
```
Functions
提取effective sql失败的个数:123
生成effective sql第一步失败的个数:32
生成effective sql第二步失败的个数:8
```

#### 总结上述版本

1. Generate Step 1：不提供基本表
```
Functions
不提供官网example,生成effective sql第一步失败的个数:24
提供官网examplem,生成effective sql第一步失败的个数:32

结论：可见不提供feature examples效果更好
原因猜测：不提供example更有助于生成简单的sql语句，因为llm会模仿给出的examples来生成更复杂的sql(这些feature提取effective sql失败，其examples往往较为复杂)。
```

2. Generate Step 2：提供基本表
```
Functions
不提供官网example,生成effective sql第二步失败的个数:11
提供官网examplem,生成effective sql第二步失败的个数:13
```

3. 合适的设置
* Generate Step 1（不提供基本表）：不提供examples
* Generate Step 2（提供基本表）：（不）提供examples


