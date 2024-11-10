# SQL Statements
## SQL Statements相关链接

英文版本：
https://mariadb.com/kb/en/sql-statements/
中文版本：
暂无

## SQL Statements元素解释
1. SQL文档的内容包括feature，illustration和example。
* Feature：MariaDB页面中是Syntax模块
* Description：MariaDB页面中是Description模块
* Examples：MariaDB页面中是Examples或Example模块，部分statement不存在Example模块（对于不存在Example模块的，则忽略）

2. 分类情况如下（官网页面的Transactions，HELP Command和Comment Syntax不做考虑）
* Account Management SQL Commands
* Administrative SQL Statements
* Build-in Functions
* Data Definition
* Data Manipulation
* Prepared Statements 
* Programmatic and Compound Statements
* Stored Routine Statements
* Table Statements
* Transactions


3. 页面中的statement文档信息的block如下：div(class="answer formatted")
![[Pasted image 20240901111312.png]]


## 爬取SQL Documents

### 数据结构
1. SQL_Statements_HTMLs.json：分不同类别的statements的htmls。
![[Pasted image 20240901105105.png]]
2. SQL_Statements_Results：为所有的html爬取页面信息，包括以下内容。
``` JSON
{  
    "HTML": "https://mariadb.com//kb/en/about-show/",  
    "Title": "About SHOW",  
    "Feature": [],  
    "Description": [],  
    "Examples": [],  
    "Category": [  
        "Administrative SQL Statements"  
    ]  
}
```
3. SQL_Statements_Results_Category：将第二步爬取的到的所有信息，按照category进行分类，以jsonl文件格式存储（每一行为一条json格式的sql statement信息）
![[Pasted image 20240901183926.png]]

### 爬取过程
#### 爬取Statement的html：HTMLs_Crawler_MariaDB.py(函数statements_htmls_crawler)
1. 以前面提到的分类情况进行分类别递归访问文档的文件夹来爬取htmls并分别存储，最后合并到文件SQL_Statements_HTMLs.jsonl中

#### 爬取Statement的具体信息：Info_Crawler.py

1. 获取feature,description和example：读取所有文档主体内容的代码块儿文本
* examples只取class为fixed的pre中的文本，不包含example的说明文本
2. 获取category：以页面顶部的目录导航栏中'SQL Statements'下一级目录名为category，如果不存在则以html的category为category

#### 根据类型将结果进行分类：Info_Crawler.py
1. 根据category将结果分类存储到文件夹SQL_Statements_Results_Category中



# Functions and Operators

## Functions and Operators文档相关链接
英文版本：
下面的页面列举了MariaDB的functions和operators的完整列表： https://mariadb.com/kb/en/function-and-operator-reference/
functions：
https://mariadb.com/kb/en/built-in-functions/
operators：
https://mariadb.com/kb/en/operators/

中文版本：
暂无

### MariaDB官网Fucntions and Operators目录解释
官网： https://mariadb.com/kb/en/function-and-operator-reference/
在这份表格中列举了所有的functions和operators，表格中包括了对应的Name（Name上的链接），Description（表格中的不作为最终Description）

![[Pasted image 20240901162240.png]]

## 爬取Functions and Operators

### 需爬取的目标结构
1.  Reference table：Name，html
2. Detailed Description：基本同前面的sql statements部分的信息
* Feature：MariaDB页面中是Syntax模块
* Description：MariaDB页面中是Description模块
* Examples：MariaDB页面中是Examples或Example模块，部分statement不存在Example模块（对于不存在Example模块的，则忽略）

### 数据结构
1. Reference Table：获取reference table（operators+fucntions）中的所有title及html，类别暂未确定（no category）
![[Pasted image 20240903103555.png]]
2. Operators Htmls：获取[Operators - MariaDB Knowledge Base](https://mariadb.com/kb/en/operators/)的所有operators的htmls，划分类别。
![[Pasted image 20240903103855.png]]
3. Functions and Operators信息
``` JSON
{  
    "HTML": "https://mariadb.com//kb/en/about-show/",  
    "Title": "About SHOW",  
    "Feature": [],  
    "Description": [],  
    "Examples": [],  
    "Category": [  
        "Administrative SQL Statements"  
    ]  
}
```

### 爬取过程

#### 爬取operators的htmls：HTMLs_Crawler_MariaDB.py（函数ops_htmls_crawler）
1. operators的类别包括
* Arithmetic Operators
* Assignment Operators
* Bit Functions and Operators
* Comparison Operators
* Logical Operators

#### 爬取functions的htmls：HTMLs_Crawler_MariaDB.py(函数funcs_htmls_crawler)
1. 收集functions+operators的Name和Reference html
2. 非operators的htmls即为functions的htmls
3. functions的类别包括
* String Functions 
* Date & Time Functions 
* Aggregate Functions  
* Numeric Functions 
* Control Flow Functions 
* Encryption,Hashing and compression Functions 
* Information Functions 
* Miscellaneous Functions 
* Dynamic Columns Functions 
* Galera Functions 
* Geographic Functions 
* JSON Functions 
* SEQUENCE Functions 
* Spider Functions 
* Vector Functions 
* Window Functions  
* Regular Expressions Functions
* No Category

#### 爬取Functions/Operators信息:Info_Crawler.py
#### 分类别存储结构


