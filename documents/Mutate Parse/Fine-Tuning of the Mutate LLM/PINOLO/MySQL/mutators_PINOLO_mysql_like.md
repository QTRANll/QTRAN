## Pinolo-main\\mutation\\stage2\doc.go
所有mutate strategy name
```
// all mutations（共18个）:
//   FixMDistinctU:OK
//	 FixMDistinctL:ok
//	 FixMCmpOpU:Ok
//	 FixMCmpOpL:ok
//	 FixMUnionAllU:OK
//	 FixMUnionAllL:ok
//   FixMInNullU:ok
//	 FixMWhere1U:OK
//	 FixMWhere0L:OK
//	 FixMHaving1U:OK
//	 FixMHaving0L:OK
//	 FixMOn1U:OK
//	 FixMOn0L:OK
//	 FixMRmUnionAllL:ok
//	 RdMLikeU
//	 RdMLikeL
//	 RdMRegExpU
//	 RdMRegExpL
```


## Pinolo-main\\mutation\\stage2\\allmutations.go
介绍了各个category对应的upper和lower的strategy name
```GO
// all mutations（共去个）
const (
	// *ast.SelectStmt(SELECT statement): Distinct true -> false
	FixMDistinctU = "FixMDistinctU"
	// *ast.SelectStmt(SELECT statement): Distinct false -> true
	FixMDistinctL = "FixMDistinctL"

	// *ast.SelectStmt(SELECT statement): AfterSetOperator(the set operator in SELECT statement) UNION -> UNION ALL
	FixMUnionAllU = "FixMUnionAllU"
	// *ast.SelectStmt(SELECT statement): AfterSetOperator(the set operator in SELECT statement) UNION ALL -> UNION
	FixMUnionAllL = "FixMUnionAllL"

	// *ast.BinaryOperationExpr(Binary operation expression), *ast.CompareSubqueryExpr(Comparison subquery expression): a {>|<|=} b -> a {>=|<=|>=} b
	FixMCmpOpU = "FixMCmpOpU"
	// *ast.BinaryOperationExpr(Binary operation expression), *ast.CompareSubqueryExpr(Comparison subquery expression): a {>=|<=} b -> a {>|<} b
	FixMCmpOpL = "FixMCmpOpL"

	// *ast.PatternInExpr(Pattern matching expression): in(x,x,x) -> in(x,x,x,null)
	FixMInNullU = "FixMInNullU"

	// *ast.SelectStmt(SELECT statement): WHERE xxx -> WHERE 1
	FixMWhere1U = "FixMWhere1U"
	// *ast.SelectStmt(SELECT statement): WHERE xxx -> WHERE 0
	FixMWhere0L = "FixMWhere0L"

	// *ast.SelectStmt(SELECT statement): HAVING xxx -> HAVING 1
	FixMHaving1U = "FixMHaving1U"
	// *ast.SelectStmt(SELECT statement): HAVING xxx -> HAVING 0
	FixMHaving0L = "FixMHaving0L"

	// *ast.Join(JOIN statement): ON xxx -> ON 1
	FixMOn1U = "FixMOn1U"
	// *ast.Join(JOIN statement): ON xxx -> ON 0
	FixMOn0L = "FixMOn0L"

	// *ast.SetOprSelectList: remove Selects[1:] for UNION ALL(识别 UNION ALL 语句,并移除其中的 Selects[1:] 部分,也就是移除第二个及后面的所有select语句，只留下第一个select语句)
	FixMRmUnionAllL = "FixMRmUnionAllL"

	// *ast.PatternLikeExpr(Pattern Like Expression): normal char -> '_'|'%',  '_' -> '%'（修改 SQL 语句中的 LIKE 表达式，将normal char 随机替换为 '_' 或 '%', 将 '_' 替换为 '%'；对于每个字符,如果不是 %,就以50%的概率将其替换为 %。）
	//% 字符在 LIKE 表达式中表示匹配任意长度的字符串。例如: 'abc%' 可以匹配 'abc'、'abcd'、'abcdef' 等任意以 'abc' 开头的字符串。
	RdMLikeU = "RdMLikeU"
	// *ast.PatternLikeExpr(Pattern Like Expression): '%' -> '_'（修改 SQL 语句中的 LIKE 表达式，将'%'随机替换为 '_' ；对于每个字符,如果是 %,就以50%的概率将其替换为 _。）
	RdMLikeL = "RdMLikeL"

	// *ast.PatternRegexpExpr(Regular expression REGEXP): '^'|'$' -> '', normal char -> '.', '+'|'?' -> '*'(处理正则表达式REGEXP,以 50% 的概率删除 '^' 或 '$' 字符,以 50% 的概率将 '+' 或 '?' 字符替换为 '*',普通字符不变。)
	RdMRegExpU = "RdMRegExpU"
	// *ast.PatternRegexpExpr(regular expression REGEXP): '*' -> '+'|'?'(处理正则表达式REGEXP,遍历模式字符串,对于每个 '*' 字符,以 50% 的概率将其替换为 '+' 或 '?'(概率各50%)。)
	RdMRegExpL = "RdMRegExpL"
)
```


## 18种变异策略的system message
### 1.0
```

* FixMDistinctU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMDistinctU":"Distinct true -> false".This mutate strategy will change "DISTINCT" in SELECT statement from true to false.
* FixMDistinctL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMDistinctL" :"Distinct false -> true".This mutate strategy will change "DISTINCT" in SELECT statement from false to true.
* FixMCmpOpU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMCmpOpU": "a {>|<|=} b -> a {>=|<=|>=} b".This mutate strategy will change ">" to ">=","<" to "<=","=" to ">=" in Binary operation expression and Comparison subquery expression.
* FixMCmpOpL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMCmpOpL" : "a {>=|<=} b -> a {>|<} b".This mutate strategy will change ">=" to ">","<=" to "<" in Binary operation expression and Comparison subquery expression.
* FixMUnionAllU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMUnionAllU" :"UNION -> UNION ALL".This mutate strategy will change the set operator "UNION" to "UNION ALL" between SELECT statements.
* FixMUnionAllL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMUnionAllL": "UNION ALL -> UNION".This mutate strategy will change the set operator "UNION ALL" to "UNION" between SELECT statements.
* FixMInNullU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMInNullU":"in(x,x,x) -> in(x,x,x,null)".This mutate strategy will include null value in IN List Expression to increase the scope of the query result set.
* FixMWhere1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMWhere1U":"WHERE xxx -> WHERE 1".This mutate strategy will change the condition of WHERE clause to "1" in SELECT statement. 
* FixMWhere0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMWhere0L" : "WHERE xxx -> WHERE 0".This mutate strategy will change the condition of WHERE clause to "0" in SELECT statement. 
* FixMHaving1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMHaving1U" : "HAVING xxx -> HAVING 1".This mutate strategy will change the condition of HAVING clause to "1" in SELECT statement. 
* FixMHaving0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMHaving0L" : "HAVING xxx -> HAVING 0".This mutate strategy will change the condition of HAVING clause to "0" in SELECT statement. 
* FixMOn1U(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMOn1U":"ON xxx -> ON 1".This mutate strategy will change the condition of ON clause to "1" in JOIN statement. 
* FixMOn0L(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMOn0L":"ON xxx -> ON 0".This mutate strategy will change the condition of ON clause to "0" in JOIN statement. 
* FixMRmUnionAllL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "FixMRmUnionAllL":"remove Selects[1:] for UNION ALL".This mutate strategy will keep only the first SELECT statement and remove all subsequent SELECT statements connected by "UNION ALL".
* RdMLikeU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMLikeU":"normal char -> '_'|'%',  '_' -> '%'".This mutate strategy will modify the LIKE expression such that for each character, if it is not '%', there is a 50% probability of replacing it with '%'.
* RdMLikeL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMLikeL":"'%' -> '_'". This mutate strategy will modify the LIKE expression such that for each character, if it is '%', there is a 50% probability of replacing it with '_'.
* RdMRegExpU(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMRegExpU":"'^'|'$' -> '', '+'|'?' -> '*'".This mutate strategy will modify the  regular expression REGEXP such that for each character, if it is '^' or '$', there is a 50% probability of deleting it;and if it is '+' or '?', there is a 50% probability of replacing it with '*'.
* RdMRegExpL(ok): Mutate the seed sql given by user into the mutated sql according to the mutate strategy "RdMRegExpL":"'*' -> '+'|'?'".This mutate strategy will modify the  regular expression REGEXP such that for each character, if it is '*',there is a 50% probability of replacing it with '+' or '?'.
```

### 2.0
``` JSON
{  
  "FixMDistinctL": "Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMDistinctL\" :\"Distinct false -> true\".This mutate strategy will mutate all SELECT clauses in the seed SQL once a time and give the positive \"flag\" of each clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each SELECT clause, it will change \"DISTINCT\" from false to true, and provide the positive \"flag\" for the clause.",  
  "FixMCmpOpU":"Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMCmpOpU\": \"a {>|<|=} b -> a {>=|<=|>=} b\".This mutate strategy will mutate all Binary operation expressions and Comparison subquery expressions in the seed SQL once a time and give the positive \"flag\" of each expression (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each Binary operation expression or Comparison subquery expression, it will change \">\" to \">=\",\"<\" to \"<=\",\"=\" to \">=\", and provide the positive \"flag\" for the expression.",  
  "FixMHaving1U":"Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMHaving1U\" : \"HAVING xxx -> HAVING 1\".This mutate strategy will mutate all HAVING clauses in the seed SQL once a time and give the positive \"flag\" of each HAVING clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each HAVING clause, it will change the condition of HAVING clause to \"1\", and provide the positive \"flag\" for the HAVING clause.",  
  "FixMOn1U": "Mutate the seed SQL given by user into the mutated SQLs according to the mutate strategy \"FixMOn1U\":\"ON xxx -> ON 1\".This mutate strategy will mutate all ON clauses in the seed SQL once a time and give the positive \"flag\" of each ON clause (such as NOT,NOT IN,IS FALSE, <>, etc. which represent \"flag\"=False). For each ON clause, it will change the condition of ON clause to \"1\", and provide the positive \"flag\" for the ON clause."
}

```

## Pinolo-main\\documents\\mutators.md
介绍了所有的mutate strategies

| **category**          | **mutation name** | **upper**                                              | **upper name** | **lower**                                                                    | **lower name** |
| --------------------- | ----------------- | ------------------------------------------------------ | -------------- | ---------------------------------------------------------------------------- | -------------- |
| Relation              | distinct          | remove distinct                                        | FixMDistinctU  | add distinct                                                                 | FixMDistinctL  |
| Relation              | union_unionall    | union→union all                                        | FixMUnionAllU  | union all→union                                                              | FixMUnionAllL  |
| Relation              | union             | r→r union r                                            |                | r1 union r2→r1<br>r1 union r2→r2                                             |                |
| Relation              | union_intersect   | r1 intersect r2→r1 union r2                            |                | r1 union r2→r1 intersect r2                                                  |                |
| Relation              | minus             | r1 minus r2→r1                                         |                | r1→r1 minus r1                                                               |                |
| Predicate             | false             | -                                                      |                | p→false                                                                      |                |
| Predicate             | is_false          | -                                                      |                | p is {true,false}→false                                                      |                |
| Predicate             | isnot_false       | -                                                      |                | p is not {true,false}→false                                                  |                |
| Predicate             | true              | p→true                                                 |                | -                                                                            |                |
| Predicate             | is_true           | p is {true,false}→true                                 |                | -                                                                            |                |
| Predicate             | isnot_true        | p is not {true,false}→true                             |                | -                                                                            |                |
| Comparison expression | le_e              | e1=e2→e1<=e2                                           | FixMCmpOpU     | e1<=e2→e1=e2                                                                 | FixMCmpOpL     |
| Comparison expression | ge_e              | e1=e2→e1>=e2                                           | FixMCmpOpU     | e1>=e2→e1=e2                                                                 | FixMCmpOpL     |
| Comparison expression | le_l              | e1\<e2→e1<=e2                                          | FixMCmpOpU     | e1<=e2→e1<e2                                                                 | FixMCmpOpL     |
| Comparison expression | ge_g              | e1>e2→e1>=e2                                           | FixMCmpOpU     | e1>=e2→e1>e2                                                                 | FixMCmpOpL     |
| Comparison expression | ne_l              | e1\<e2→e1!=e2                                          |                | e1!=e2→e1<e2                                                                 |                |
| Comparison expression | ne_g              | e1>e2→e1!=e2                                           |                | e1!=e2→e1>e2                                                                 |                |
| Comparison expression | any_all           | e op all r→e op any r                                  |                | e op any r→e op all r                                                        |                |
| Comparison expression | like_nw           | char→_<br>char→%                                       |                | _→random char<br/>%→random char                                              |                |
| Comparison expression | like_ww           | _→%                                                    |                | %→_                                                                          |                |
| Comparison expression | regexp_prefix     | remove ^                                               |                | add ^                                                                        |                |
| Comparison expression | regexp_suffix     | remove $                                               |                | add $                                                                        |                |
| Comparison expression | regexp_nw         | char→.                                                 |                | .→random char                                                                |                |
| Comparison expression | regexp_ww         | +→\*<br>?→\*                                           |                | \*→+<br>\*→?                                                                 |                |
| Comparison expression | in_null           | in(e1,e2,...)→in(e1,e2,...,null)                       | FixMInNullU    | in(e1,e2,...,null)→in(e1,e2,...)                                             |                |
| Comparison expression | between           | e between e1 and e2→e1<=e<br>e between e1 and e2→e<=e2 |                | e between e1 and e2→e1<e and e <= e2<br>e between e1 and e2→e1<=e and e < e2 |                |