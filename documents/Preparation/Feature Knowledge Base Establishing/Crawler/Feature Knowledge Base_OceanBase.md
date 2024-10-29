# OceanBase官网文档
## 相关链接
[OceanBase分布式数据库-海量数据 笔笔算数](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000820805)
## 文档目录
* SQL语法：
	* 系统租户：考虑， OceanBase 数据库管理命令的使用参考信息
	* 普通租户（MySQL模式）：考虑，获取其中的运算符，函数，SQL语句部分
	* 普通租户（Oracle模式）：考虑，获取其中的运算符，函数，SQL语句部分
---

# 系统租户（OceanBase 数据库管理命令）
## 相关链接
[OceanBase分布式数据库-海量数据 笔笔算数](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000820805)
## OceanBase数据库管理命令页面元素解释
1. OceanBase数据库管理语句属于“SQL语句“部分：OceanBase数据库管理语句=MySQL官网文档的SQL Statements的Database Administration Statements。网页内包含以下元素
* description：”描述“
* 使用限制及注意事项：暂不考虑
* 权限要求：暂不考虑
* feature：“语法”或“声明”或"语法声明"或”函数语法“
* illustration：”参数解释“+“说明”+”参数说明“+”返回类型“
* examples：“示例”

## 获取OceanBase 数据库管理命令

### 数据结构
1. 分类HTMLs
```
{  
    "No Category:": {  "","",……},  
}
```
2. Database Administration Statements信息
```
{  
    "ADDDATE": {  
        "Title": [""],  
        "HTML": [""],  
        "Feature": "",
        "Description":[""],
        "Illustration": [""],  
        "Examples": [""],  
        "Detailed Examples":[""],
        "Category": [""]  
    }
}
```
### 获取过程

##### 获取HTMLs：HTMLs_Crawler_OceanBase.py
1. 从第一个“管理命令概述”页面开始，在右下角的“下一篇”按钮处获取下一个页面的标题及html
2. 重复步骤1，直到遇到最后一个结束页面的名称时停止，说明即将到下一个单元了
##### 分类HTMLs:HTMLs_Category_Classifier.py
1. 全部为No Category
#### 获取具体信息:Functions_and_Statements_Info_Crawler.py



---

# 普通租户（MySQL模式）

## 运算符（Operators）
### 运算符（MySQL模式）页面元素解释
OceanBase官网关于运算符的介绍，各个页面的格式不统一，比较混乱（有表格的，有非表格的，……）；考虑到OceanBase关于运算符的内容较少，编写代码进行爬取难以涵盖所有情况且耗时，因此人工获取运算符部分的信息。
### 获取运算符（MySQL模式）信息

#### 运算符（MySQL模式）分类

* Arithmetic Operators:算术运算符
* Bit Operators:位运算符
* Comparison Operators:比较运算符
* Logical Operators:逻辑运算符
* Assignment Operators:赋值运算符
* Data and Time Operators:日期时间运算符
* String Operators:字符连接运算符
* Cast Operators:BINARY 转换运算符
* CASE Conditional Operators:CASE 条件运算符
#### 数据结构
``` JSON
{  
    "+": {  
        "Feature": "+",  
        "Description": "一元表示正数，二元表示加法。",  
        "HTML": "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000822066",  
        "Illustration": [  
            "对于整数除法的运算规则特做以下说明：\n\n商数不论正负，统一向 0 取整。\n\n余数正负与被除数相同。"
        ],  
        "Examples": [  
            "SELECT (-7) DIV (3.6), (-7) MOD (3.6);\n+----------------+----------------+\n| (-7) DIV (3.6) | (-7) MOD (3.6) |\n+----------------+----------------+\n|             -1 |           -3.4 |\n+----------------+----------------+\n1 row in set\n\nSELECT (-7) DIV (-3.4), (-7) % (-3.4);\n+-----------------+---------------+\n| (-7) DIV (-3.4) | (-7) % (-3.4) |\n+-----------------+---------------+\n|               2 |          -0.2 |\n+-----------------+---------------+\n1 row in set\n"  
        ],  
        "Category": [  
            "Arithmetic Operators"  
        ]  
    }
}
```


## 函数（Functiosns）
### 函数（MySQL模式）页面元素解释
1. OceanBase函数网页较为规整，包含以下元素
* description：”描述“
* feature：“声明”或“语法”或"语法声明"或”函数语法“
* illustration：“说明”+”参数说明“+”参数解释“+”返回类型“
* examples：“示例”
### 获取函数（MySQL模式）信息

#### 函数（MySQL模式）分类
* 单行函数
	* Date and Time Functions:日期时间函数
	* String Functions:字符串函数
	* Cast Functions:转换函数
	* Mathematical Functions:数学函数
	* Comparison Functions:比较函数
	* Flow Control Functions:流程控制函数
* Aggregate Functions:聚合函数
* Analysis Functions:分析函数
* Encryption Functions:加密函数
* Information Functions:信息函数
* JSON Functions:JSON函数
* XML Functions:XML函数
* Spatial Functions:空间函数
* Performance Schema Functions:性能模式函数
* Locking Functions:锁函数
* Miscellaneous Functions:其他函数
#### 数据结构
1. 分类HTMLs
```
{  
    "Date and Time Functions:": {  "","",……},  
    "String Functions": {"","",……},
    ……
}
```
2. Functions信息
```
{  
    "ADDDATE": {  
        "Title": [""],  
        "HTML": [""],  
        "Feature": "",
        "Description":[""],
        "Illustration": [""],  
        "Examples": [""],  
        "Detailed Examples":[""],
        "Category": [""]  
    }
}
```
#### 获取过程
##### 获取HTMLs：HTMLs_Crawler_OceanBase.py
##### 分类HTMLs:HTMLs_Category_Classifier.py
##### 获取具体信息:Functions_and_Statements_Info_Crawler.py


## SQL语句（SQL Statements）
### SQL语句（MySQL模式）页面元素解释
1. OceanBase的SQL语句网页较为规整，包含以下元素
* description：”描述“
* feature：”语法“
* illustration：参数解释/参数说明
* examples：“示例”
### 获取SQL语句（MySQL模式）信息
#### SQL语句（MySQL模式）分类
官网文档未进行详细分类
#### 数据结构
1. 分类HTMLs
```
{  
    "No Category:": {  "","",……},  
}
```
2. SQL Statements信息
```
{  
    "ADDDATE": {  
        "Title": [""],  
        "HTML": [""],  
        "Feature": "",
        "Description":[""],
        "Illustration": [""], 
        "Detailed Examples":[""], 
        "Examples": [""],  
        "Category": [""]  
    }
}
```

#### 获取过程
##### 获取HTMLs：HTMLs_Crawler_OceanBase.py
##### 分类HTMLs:HTMLs_Category_Classifier.py
1. 全部为No Category
##### 获取具体信息:Functions_and_Statements_Info_Crawler.py

---

# 普通租户（Oracle模式）

## 运算符（Operators）
### 运算符（Oracle模式）页面元素解释
OceanBase官网关于运算符的介绍，各个页面的格式不统一，比较混乱（有表格的，有非表格的，……）；考虑到OceanBase关于运算符的内容较少，编写代码进行爬取难以涵盖所有情况且耗时，因此人工获取运算符部分的信息。
### 获取运算符（Oracle模式）信息

#### 运算符（Oracle模式）分类
* Arithmetic Operators:算术运算符
* Concatenation Operators:串联运算符
* Hierarchical Query Operators:层次查询运算符
* Set Operators:集合运算符
* COLLATE Operators:COLLATE 运算符
#### 数据结构
```
同MySQL模式的Operators
```


## 函数（Functiosns）
### 函数（Oracle模式）页面元素解释

1. OceanBase函数网页较为规整，包含以下元素
* description：”描述“
* feature：”语法“
* illustration：
	* ”参数解释“：可以看作illustration的一部分信息
	* “返回类型”：可以看作illustration的一部分信息
* examples：”示例“

### 获取函数（Oracle模式）信息

#### 函数（Oracle模式）分类
* Single-Row Functions:单行函数
	* Numeric Functions:数字函数
	* Character Functions Returning CharacterValues:返回字符串的字符串函数
	* Character Functions Returning NumberValues:返回数字的字符串函数
	* Datetime Functions:日期时间函数
	* General Comparison Functions:通用比较函数
	* Conversion Functions:转换函数
	* Encoding and Decoding Functions:编码解码函数
	* NULL-Related Functions:空值相关函数
	* Environment and ldentifier Functions:环境和标识符函数
	* Hierarchical Functions:层次函数
	* JSON Functions:JSON函数
	* XML Functions:XML函数
	* Spatial Functions:空间函数
* Aggregate Functions:聚合函数
* Analytic Functions:分析函数
* Information Functions:信息函数
#### 数据结构
1. 分类HTMLs
```
{  
    "Numeric Functions": {  "","",……},  
    "Character Functions Returning CharacterValues": {"","",……},
    ……
}
```
2. Functions信息
```
{  
    "ADDDATE": {  
        "Title": [""],  
        "HTML": [""],  
        "Feature": "",
        "Description":[""],
        "Illustration": [""],  
        "Examples": [""],  
        "Detailed Examples":[""],
        "Category": [""]  
    }
}
```
#### 获取过程
##### 获取HTMLs：HTMLs_Crawler_OceanBase.py
##### 分类HTMLs:HTMLs_Category_Classifier.py
##### 获取具体信息:Functions_and_Statements_Info_Crawler.py




## SQL语句（SQL Statements）
### SQL语句（Oracle模式）页面元素解释
1. OceanBase的SQL语句网页较为规整，包含以下元素
* description：”描述“
* feature：”语法“
* illustration：参数解释/参数说明
* examples：“示例”
### 获取SQL语句（Oracle模式）信息

#### SQL语句（Oracle模式）分类
* DDL
* DML
* DCL
#### 数据结构
1. 分类HTMLs
```
{  
    "DDL:": {  "","",……},  
}
```
2. SQL Statements信息
```
{  
    "ADDDATE": {  
        "Title": [""],  
        "HTML": [""],  
        "Feature": "",
        "Description":[""],
        "Illustration": [""],  
        "Examples": [""],  
        "Detailed Examples":[""],
        "Category": [""]  
    }
}
```
#### 获取过程
##### 获取HTMLs：HTMLs_Crawler_OceanBase.py
##### 分类HTMLs:HTMLs_Category_Classifier.py
1. 分类为
* DDL
* DML
* DCL
##### 获取具体信息:Functions_and_Statements_Info_Crawler.py

