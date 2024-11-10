# Functions(finished)

* functions和operators是混合在一起，分类别进行展示的。
## Functions文档相关链接
英文版本：
[USER GUIDE | MonetDB Docs](https://www.monetdb.org/documentation-Aug2024/user-guide/)
### Fucntions目录解释
类别如下：
- [Logical Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/logical-functions)
- [Comparison Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/comparison-functions)
- [Cast Conversion Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/cast-conversion-functions)
- [Mathematics Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/mathematics-functions)
- [Character String Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/string-functions)
- [Binary String Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/binary-string-functions)
- [Date Time Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/date-time-functions)
- [INET Functions & Operators](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/inet-functions)
- [JSON Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/json-functions)
- [URL Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/url-functions)
- [UUID Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/uuid-functions)
- [Aggregate Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/aggregate-functions)
- [Window Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/window-functions)
- [Generate Series Functions](https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/generator-functions)
## 爬取Functions
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
2. 所有的functions都会在对应的表格中列出，表格如下，表格的列名如下。
![[Pasted image 20241014084127.png]]

``` Python
[  
  [  
    'Function',  
    'Return type',  
    'Description',  
    'Example',  
    'Result'  
  ],  
  [  
    'Operator',  
    'Description',  
    'Example',  
    'Result'  
  ],  
  [  
    'Operator',  
    'Description',  
    'Example'  
  ],  
  [  
    'Statistic Function',  
    'Return type',  
    'Description',  
    'Example',  
    'Result'  
  ],  
  [  
    'Function',  
    'Return type',  
    'Description',  
    'Available since'  
  ],  
  [  
    'Function',  
    'Return type',  
    'Available since'  
  ],  
  [  
    'Function',  
    'Argument types',  
    'Description'  
  ]  
]
```
3. 对于列名进行处理
* 第一列在下列范围，视为functions和operators相关（也是feature列）表格：Function，Operator，Statistic Function
* Description列：Return type（添加returen type的说明），Argument types（添加arguments type的说明），Description
* Examples列：Example

# # Operators(finished)

DuckDB的functions和operators是混合在一起，分类别进行展示的。
## Operators文档相关链接
英文版本：
[USER GUIDE | MonetDB Docs](https://www.monetdb.org/documentation-Aug2024/user-guide/)
### Opeartors目录解释

## 爬取Operators
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
2. 所有的opearators都会在对应的表格中列出



# SQL Statements(unfinished)
## SQL Statements相关链接

英文版本：
[USER GUIDE | MonetDB Docs](https://www.monetdb.org/documentation-Aug2024/user-guide/)
中文版本：
暂无
## SQL Statements元素解释
statement的sytax以语法图的形式展示，所以无法获取syntax
## 爬取SQL Documents

### 数据结构

### 爬取过程

















