# 项目结构图
![[70e7c712bf47f1df5a75aae912774cf8.png]]


# SQL Statements
## SQL Statements相关链接
英文版本：
[MySQL :: MySQL 8.4 Reference Manual :: 15 SQL Statements](https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html)
[MySQL :: MySQL 8.0 Reference Manual :: 15 SQL Statements](https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html)
中文版本：
[第 13 章 SQL 语句_MySQL 8.0 参考手册](https://mysql.net.cn/doc/refman/8.0/en/sql-statements.html)

select语句部分：
[13.2.10 SELECT 语句_MySQL 8.0 参考手册](https://mysql.net.cn/doc/refman/8.0/en/select.html)


## SQL Statements元素解释
1. SQL文档的内容包括feature，illustration和example（主要看select语句）。
* feature：语法元素或者函数的使用形式（一个用来表示function或语法元素咋用的式子，如：AVG([DISTINCT]expr)，sum函数）
* illustration：关于该function或语法元素的解释  
* example：运用了该function或语法元素的实例
* feature和example文本的简单区分：feature文本中不包含分号";",而example的文本中一定包含分号";"。

![[743665bb966ce94850c47da22c597aa.png|500]]


## 爬取SQL Documents

### SQL Documents网页结构
![[Pasted image 20240707160455.png|300]]


![[Pasted image 20240707161715.png]]
### 数据结构

1. Statement with no child
``` JSON
{  
    "HTML":"",
    "Title":"",
    "Feature":["","",……],  
    "Overall Illustration":["","","",……],  
    "Detailed Illustration":[
        {
           "Sub-title":"",
           "Illustration":["","","",……]
        },
        {
           "Sub-title":"",
           "Illustration":["","","",……]
        },
        ……
    ],
    "Examples":["","",……],
    "Category": [  
        "Data Definition Statements"  
    ]
}
```

2. Statement with child
``` JSON
{   
    "HTML":"",
    "Title":"",
    "Feature":["","",……],  
    "Overall Illustration":["","","",……],  
    "Detailed Illustration":[
        {
           "Sub-title":"",
           "Illustration":["","","",……]
        },
        {
           "Sub-title":"",
           "Illustration":["","","",……]
        },
        ……
    ],
    "Examples":["","",……],
    "Category": [  
        "Data Definition Statements"  
    ]
}

{
    "Father statement":"",
    "Children statements":["","",……],
}
```

3. 目录
```
{
   "15.1.1 Atomic Data Definition Statement Support":"",
}
```
### 爬取过程
#### 相关链接
[BeautifulSoup 如何检查迭代变量是NavigableString类型还是Tag类型|极客教程 (geek-docs.com)](https://geek-docs.com/beautifulsoup/beautifulsoup-questions/459_beautifulsoup_how_to_check_whether_or_not_a_iterating_variable_navigablestring_or_tag_type.html)

[BeautifulSoup 如何检查迭代变量是否为 NavigableString 或 Tag 类型|极客笔记 (deepinout.com)](https://deepinout.com/beautifulsoup/beautifulsoup-questions/459_beautifulsoup_how_to_check_whether_or_not_a_iterating_variable_navigablestring_or_tag_type.html)

[遍历文档树 | Beautiful Soup 4.2.0 中文文档 (gitbooks.io)](https://wizardforcel.gitbooks.io/bs4-doc/content/6.html)
#### Chrome和ChromeDriver的版本匹配
* 问题：
[【Python】已完美解决：selenium.common.exceptions.SessionNotCreatedException: Message: session not created](https://blog.csdn.net/a1657054242/article/details/139636170)
* ChromeDriver下载地址及文件位置
[chromedriver/126.0.6478.126 chromedriver-win64.zip at main · dreamshao/chromedriver · GitHub](https://github.com/dreamshao/chromedriver/blob/main/126.0.6478.126%20chromedriver-win64.zip)
[python+selenium+chromedriver时候chromedriver.exe放在那里？_python chromedriver 放在哪个目录下](https://blog.csdn.net/wyj_427/article/details/100668067)

#### 爬取Statement的html：HTMLs_Crawler_MySQL.py
``` Python
  
prefix = "../../../Feature Knowledge Base/MySQL/"  
html_statements = "https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html"  # statements的目录页  
dir_filename_statement = prefix + "SQL_Statements/SQL_Statements_HTMLs.json"  
htmls_crawler(html_statements, dir_filename_statement)
```
![[Pasted image 20240709131724.png]]


#### 爬取Statement的具体信息：SQL_Document_Info_Crawler.py

1. 获取feature和example：读取所有language-sql代码块儿文本（不包括终端的代码块language-terminal），其中Feature不包含分号，Example包含分号
2. 获取illustration：遍历处理Document Body的内容并获取overall illustration和detailed illustration
* 跳过非Tag
* 跳过非illustration的Tag
* 如果是SubTitle则记录下标
* 切片处理所有信息到overall illustration和detailed illustration中

![[Pasted image 20240709133346.png]]





# Functions and Operators

## Functions and Operators文档相关链接
英文版本：
[MySQL :: MySQL 8.4 Reference Manual :: 14 Functions and Operators](https://dev.mysql.com/doc/refman/8.4/en/functions.html)
中文版本：
[第 12 章函数和运算符_MySQL 8.0 参考手册](https://mysql.net.cn/doc/refman/8.0/en/functions.html)

## Functions and Operators文档元素解释
### MySQL官网Fucntions and Operators目录
This chapter describes the **built-in functions and operators** that are permitted for writing expressions in MySQL. For information about loadable functions and stored functions, see [Section 7.7, “MySQL Server Loadable Functions”](https://dev.mysql.com/doc/refman/8.4/en/server-loadable-functions.html "7.7 MySQL Server Loadable Functions"), and [Section 27.2, “Using Stored Routines”](https://dev.mysql.com/doc/refman/8.4/en/stored-routines.html "27.2 Using Stored Routines"). For the rules describing how the server interprets references to different kinds of functions, see [Section 11.2.5, “Function Name Parsing and Resolution”](https://dev.mysql.com/doc/refman/8.4/en/function-resolution.html "11.2.5 Function Name Parsing and Resolution").
```
Table of Contents
14.1 Built-In Function and Operator Reference
14.2 Loadable Function Reference
14.3 Type Conversion in Expression Evaluation
14.4 Operators
14.4.1 Operator Precedence
14.4.2 Comparison Functions and Operators
14.4.3 Logical Operators
14.4.4 Assignment Operators
14.5 Flow Control Functions
14.6 Numeric Functions and Operators
14.7 Date and Time Functions
14.8 String Functions and Operators
14.9 Full-Text Search Functions
14.10 Cast Functions and Operators
14.11 XML Functions
14.12 Bit Functions and Operators
14.13 Encryption and Compression Functions
14.14 Locking Functions
14.15 Information Functions
14.16 Spatial Analysis Functions
14.17 JSON Functions
14.18 Replication Functions
14.19 Aggregate Functions
14.20 Window Functions
14.21 Performance Schema Functions
14.22 Internal Functions
14.23 Miscellaneous Functions
14.24 Precision Math
```

### MySQL官网Fucntions and Operators目录解释

* 14.1，14.2分别枚举了Built-In Function and Operator，Loadable Function，网页页面包括feature（Name），simplified illustrations（Description）元素以及对应的链接
  ![[Pasted image 20240710170349.png|500]]
* 14.3关于表达式求值中的类型转换，不做考虑
* 14.4-14.24：页面中的表格均包括了feature（Name），simplified illustrations（Description）元素以及对应的链接；后续配有feature的详细信息,包括feature，illustration和examples。
  ![[Pasted image 20240710174734.png|500]]
  ![[Pasted image 20240710174755.png]]
  * 14.10有点特殊


## 爬取Functions and Operators

### 需爬取的目标结构

Reference table：Name，Description，html
Detailed Description：feature，illustration，examples

### 数据结构

1. 设置Functions and Operators的所有类别
```
Category =[  
"14.1 Built-In Function and Operator Reference",
"14.2 Loadable Function Reference",
"14.4.2 Comparison Functions and Operators",  
"14.4.3 Logical Operators",  
"14.4.4 Assignment Operators",  
"14.5 Flow Control Functions",  
"14.6.1 Arithmetic Operators",  
"14.6.2 Mathematical Functions",  
"14.7 Date and Time Functions",  
"14.8 String Functions and Operators",  
"14.10 Cast Functions and Operators",  
"14.11 XML Functions",  
"14.12 Bit Functions and Operators",  
"14.13 Encryption and Compression Functions",  
"14.14 Locking Functions",  
"14.15 Information Functions",  
"14.16 Spatial Analysis Functions",  
"14.17 JSON Functions",  
"14.18 Replication Functions",  
"14.19 Aggregate Functions",  
"14.20 Window Functions",  
"14.21 Performance Schema Functions",  
"14.22 Internal Functions",  
"14.23 Miscellaneous Functions"  
]
```
2. htmls目录
```
{
     
    "14.1 Built-In Function and Operator Reference": "https://dev.mysql.com/doc/refman/8.4/en/built-in-function-reference.html",  
    "14.2 Loadable Function Reference": "https://dev.mysql.com/doc/refman/8.4/en/loadable-function-reference.html",  
    "14.3 Type Conversion in Expression Evaluation": "https://dev.mysql.com/doc/refman/8.4/en/type-conversion.html",
}
```

3. Reference Table
* 避免Functions/Operators元素数据的重复：以单条数据的Feature作为key来组织数据，每条数据可能同时属于多个Functions/Operators类别。
``` JSON
对于htmls目录中的每个html，爬取该页面内的Reference Table信息，Reference Tabl内单行信息的组织结构如下：
{  
    "HTML":"https://dev.mysql.com/doc/refman/8.4/en/built-in-function-reference.html",
    "Title":"14.1 Built-In Function and Operator Reference",
    "Name":">",  
    "Description":"Greater than operator",  
    "Reference HTML":"(https://dev.mysql.com/doc/refman/8.4/en/comparison-operators.html#operator_greater-than"
}
```

4. Functions/Operators信息
``` JSON
{   
    "HTML":"https://dev.mysql.com/doc/refman/8.4/en/built-in-function-reference.html",
    "Title":"14.1 Built-In Function and Operator Reference",
    "Type":"Operator",
    "Name":">",  
    "Description":"Greater than operator",  
    "Reference HTML":"(https://dev.mysql.com/doc/refman/8.4/en/comparison-operators.html#operator_greater-than",
    "Feature":">",
    "Illustration":["","",……],
    "Examples":["","",……]
}
```


### 爬取过程
#### 爬取Functions and Operators的html：HTMLs_Crawler_MySQL.py
* 收集嵌套目录的name和html
``` Python
html_func_op = "https://dev.mysql.com/doc/refman/8.4/en/functions.html"  
dir_filename_fun_op = prefix + "Functions_and_Operators/Functions_and_Operators_HTMLs.json"  # functions 和 operators的目录页  
htmls_crawler(html_func_op, dir_filename_fun_op)
```
![[Pasted image 20240710215949.png]]
#### 爬取Reference table：Reference_Table_Crawler.py
* 收集functions/operators的Name，Description和Reference html
![[Pasted image 20240711095144.png|500]]

#### 爬取Functions/Operators信息:Functions_and_Operators_Info_Crawler.py
![[Pasted image 20240711095537.png]]

* 获取所有functions/operators的具体信息，包括完整的feature，illustration和exampls
* 圆点标题为完整的feature
* 其余文字部分皆为illustration
* 包含分号和对应Name的sql语句才算examples


#### 去重，为每条数据分配对应的类别：Deduplicate_and Classify.py
结果在Results_merged2.0.json中
* 共528条数据
* 以"Feature"为唯一确定的key，便于索引
* "HTML"：该"Feature"出现过的所有页面的链接
* "Title"：该"Feature"出现过的所有页面的标题
* "Name"：该"Feature"在Reference Table中的名称
* "Description"：该"Feature"在Reference Table中的简短描述
* "Reference HTML"：该"Feature"在Reference Table中的详细信息链接，该链接页面包含了详细信息
* "Type": "Operator"或者Functions""  
* "Feature": 详细信息，Feature比Name更详细，Feature包含了函数的参数信息
* "Illustration": 详细信息
* "Examples":   详细信息
* "Category"：所属类别，可能不止一个
```
{  
    "&": {  
        "HTML": [  
            "https://dev.mysql.com/doc/refman/8.4/en/built-in-function-reference.html",  
            "https://dev.mysql.com/doc/refman/8.4/en/bit-functions.html",  
            "https://dev.mysql.com/doc/refman/8.4/en/non-typed-operators.html"  
        ],  
        "Title": [  
            "14.1 Built-In Function and Operator Reference",  
            "14.12 Bit Functions and Operators",  
            "14.4 Operators"  
        ],  
        "Name": "&",  
        "Description": "Bitwise AND",  
        "Reference HTML": "https://dev.mysql.com/doc/refman/8.4/en/bit-functions.html#operator_bitwise-and",  
        "Type": "Operator",  
        "Feature": "&",  
        "Illustration": [],
        "Examples": []  
    },
    "Category": [  
        "Built-In Operators",  
        "Bit Operators"  
    ]
}
```


根据下面的类别，将Results_merged2.0.json的内容分类存放在文件夹Functions_and_Operators_Results_Category中
```
类别：
Functions_Categories = {  
   "14.1":"Built-In Functions",  
   "14.2":"Loadable Functions",  
   "14.4.2":"Comparison Functions",  
   "14.5":"Flow Control Functions",  
   "14.6.2":"Mathematical Functions",  
   "14.7":"Date and Time Functions",  
   "14.8":"String Functions",  
   "14.10":"Cast Functions",  
   "14.11":"XML Functions",  
   "14.12":"Bit Functions",  
   "14.13":"Encryption and Compression Functions",  
   "14.14":"Locking Functions",  
   "14.15":"Information Functions",  
   "14.16":"Spatial Analysis Functions",  
   "14.17":"JSON Functions",  
   "14.18":"Replication Functions",  
   "14.19":"Aggregate Functions",  
   "14.20":"Window Functions",  
   "14.21":"Performance Schema Functions",  
   "14.22":"Internal Functions",  
   "14.23":"Miscellaneous Functions"  
}  
  
  
Operators_Categories = {  
   "14.1":"Built-In Operators",  
   "14.4.2":"Comparison Operators",  
   "14.4.3":"Logical Operators",  
   "14.4.4":"Assignment Operators",  
   "14.6.1":"Arithmetic Operators",  
   "14.8":"String Operators",  
   "14.10":"Cast Operators",  
   "14.12":"Bit Operators"  
}
```







