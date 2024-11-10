# SQL Statements
## SQL Statements相关链接
英文版本：
[SQL 语句概述 | PingCAP 文档中心](https://docs.pingcap.com/zh/tidb/stable/sql-statement-overview)

## SQL Statements元素解释
1. SQL文档的内容包括feature（页面中为“语法图”的“代码”部分），illustration（页面中为开头的介绍部分）和example（页面中为“示例”部分）。

![[Pasted image 20240903194201.png|500]]



## 爬取SQL Documents

### 数据结构
1. htmls：分类别爬取sql statements的title及htmls
``` JSON
{  
    "Schema 管理与数据定义语句 (DDL)": {  
    },  
    "数据操作语句 (DML)": {  
    },  
    "事务语句": {  
    }
}
```

2. statements信息
``` JSON
{  
    "HTML": "",  
    "Title": "",  
    "Feature": [],  
    "Description": [],  
    "Examples": [],  
    "Category": [  
        ""  
    ]  
}
```


### 爬取过程
#### 爬取Statement的html：HTMLs_Crawler_TiDB.py
1. 爬取[SQL 语句概述 | PingCAP 文档中心](https://docs.pingcap.com/zh/tidb/stable/sql-statement-overview)页面的表格，分类爬取
#### 爬取Statement的具体信息：Info_Crawler.py
1. Feature：爬取“语法图”中的hidden代码部分
2. Examples：爬取“示例”中的包含分号的代码块
3. Description：开头的部分
#### 分类别存储结果
statements的类别包括以下：
* Schema管理与数据定义语句(DDL)
* TiCDC与 TiDB Binlog
* 事务语句
* 备份和恢复
* 实例管理
* 放置策略
* 效用语句
* 数据导入和导出
* 数据操作语句(DML).
* 显示语句
* 管理语句
* 统计信息和执行计划管理
* 账户管理与数据控制语言(DCL)
* 资源组
* 锁定语句
* 预处理语句





# Operators

## Functions and Operators文档相关链接
英文版本：
https://docs.pingcap.com/zh/tidb/stable/operators

## 爬取Operators

### 需爬取的目标结构
1.  Reference table：Name，html
* operators以四个表格形式列出了涉及的所有operators，需要获取name和对应的html（链接指向mysql的官方文档）

### 数据结构
1. Reference Table：获取reference table中的所有title及html，类别暂定为表名
2. Functions信息
``` JSON
{  
    "HTML": "",  
    "Title": "",  
    "Feature": [],  
    "Description": [],  
    "Examples": [],  
    "Category": [  
        ""  
    ]  
}
```

### 爬取过程

#### 爬取operators的htmls：HTMLs_Crawler_TiDB.py（函数operators_htmls_crawler）
1. 爬取四个table中的（name，html）
#### 爬取Operators信息:Info_Crawler.py
1. 替换步骤1获取的（name，html）中的html的mysql版本：8.0->8.4
2. 以html检索对应的mysql feature knowledge base，得到已爬取的mysql数据，修改后作为TiDB的数据
#### 分类别存储结果
TiDB的operators类别包括以下：
* Arithmetic Operators
* Assignment Operators
* Bit Operators
* Built-In Operators
* Cast Operators
* Comparison Operators
* Logical Operators
* String Operators




# Functions

## Functions文档相关链接
英文版本：
[函数和操作符概述 | PingCAP 文档中心](https://docs.pingcap.com/zh/tidb/stable/functions-and-operators-overview)
### Fucntions目录解释
TiDB对于functions的分类如下：
* Flow Control Functions：控制流程函数
* String Functions：字符串函数
* Mathematical Functions：数值函数
* Date and Time Functions：日期和时间函数
* Bit Functions：位函数
* Cast Functions：Cast函数
* Encryption and Compression Functions：加密和压缩函数
* Locking Functions：锁函数
* Information Functions：信息函数
* JSON Functions：JSON函数
* Aggregate Functions：GROUP BY 聚合函数
* Window Functions：窗口函数
* Sequence Functions：序列函数（Mysql中没有）
* TiDB Specific Functions： TiDB特有的函数
* Miscellaneous Functions：其他函数

上述类别functions的网页组织形式有以下四种：
1. 以h2作为标题进行划分：控制流程函数，Cast函数，JSON函数，窗口函数，序列函数，TiDB特有的函数
2. 以h3作为标题进行划分：字符串函数，加密和压缩函数，信息函数，其他函数
3. 以表格形式列出链接，链接指向mysql官方文档：数值函数，日期和时间函数，锁函数，GROUP BY 聚合函数
4. 特殊，只包含一个函数BIT_COUNT()：位函数

## 爬取Functions
### 数据结构
1. Htmls：函数分类别的html
2. Functions信息
``` JSON
{  
    "HTML": "",  
    "Title": "",  
    "Feature": [],  
    "Description": [],  
    "Examples": [],  
    "Category": [  
        ""  
    ]  
}
```
### 爬取过程

#### 爬取情形三（表格形式）的所有（name,html）：HTMLs_Crawler_TiDB.py

#### 按以上面四种分类获取functions的信息，分类别存储:Info_Crawler.py



