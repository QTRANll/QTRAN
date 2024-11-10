# Functions(finished)

* DuckDB的functions和operators是混合在一起，分类别进行展示的。
* functions有少部分函数类别的展示形式不够统一，没有被爬取到：
	* [List Functions – DuckDB](https://duckdb.org/docs/sql/functions/list#lambda-functions)
	* [Pattern Matching – DuckDB](https://duckdb.org/docs/sql/functions/pattern_matching#regular-expressions)
	
## Functions文档相关链接
英文版本：
[Functions – DuckDB](https://duckdb.org/docs/sql/functions/overview)
### Fucntions目录解释

## 爬取Functions
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
2. 所有的functions都会在对应的表格中列出，表格分下面两种情况：第一种情况没有examples，第二种有examples。（表格列名：Function（Name），Description，Example）
![[Pasted image 20241011150438.png]]
![[Pasted image 20241012083906.png]]

3. 页面中还有函数的详细信息描述，对应了前面function表格中的函数（部分function有自己的详细信息，部分没有）（详细信息行名：Description，Example，Alias(es)，Aliases，Alias，Result，Formula等其他不常见的则全部归为description即可，其中别名可能有多个）
![[Pasted image 20241011150606.png]]
![[Pasted image 20241011151202.png]]
4. 页面中有同名的情况，需要进行特殊处理：为同名的情况增加一条function信息
![[Pasted image 20241011150854.png]]



# # Operators(finished)

DuckDB的functions和operators是混合在一起，分类别进行展示的。
## Operators文档相关链接
英文版本：
[Functions – DuckDB](https://duckdb.org/docs/sql/functions/overview)
### Opeartors目录解释


## 爬取Operators
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
2. 所有的opearators都会在对应的表格中列出（表格列名：Operator, Description, Example, Result）
![[Pasted image 20241011211409.png]]

![[Pasted image 20241011150606.png]]
![[Pasted image 20241011151202.png]]
4. 页面中有同名的情况，需要进行特殊处理：为同名的情况增加一条function信息
![[Pasted image 20241011150854.png]]



# SQL Statements(unfinished)
## SQL Statements相关链接

英文版本：
[Statements Overview – DuckDB](https://duckdb.org/docs/sql/statements/overview)
中文版本：
暂无
## SQL Statements元素解释
statement的sytax以语法图的形式展示，所以无法获取syntax
## 爬取SQL Documents

### 数据结构

### 爬取过程

















