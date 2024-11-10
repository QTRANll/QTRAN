## 0 待完成
1. 添加静态的RAG建成的向量数据库，每次不用重新再次建立

## 1 Overview

### 1.1 Set Up
1. 假设 transfer a_db to b_db
2. 已完成
* a_db = mariadb, b_db = postgres
* a_db = mariadb, b_db = clickhouse

## 2 链接
* [利用LangChain实现RAG_langchain rag-CSDN博客](https://blog.csdn.net/qiaotl/article/details/134378276?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522171229270416800185872895%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=171229270416800185872895&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_click~default-5-134378276-null-null.142^v100^pc_search_result_base7&utm_term=RAG&spm=1018.2226.3001.4187)
* [Build a Retrieval Augmented Generation (RAG) App | 🦜️🔗 Langchain](https://js.langchain.com/docs/tutorials/rag/)
* [Retrieval-Augmented Generation (RAG): From Theory to LangChain Implementation | by Leonie Monigatti | Towards Data Science](https://towardsdatascience.com/retrieval-augmented-generation-rag-from-theory-to-langchain-implementation-4e9bd5f6a4f2)
* [检索增强生成（RAG）从理论到 LangChain 实践 | 宝玉的分享 (baoyu.io)](https://baoyu.io/translations/rag/retrieval-augmented-generation-rag-from-theory-to-langchain-implementation)
* [一文带你了解大模型的RAG(检索增强生成) | 概念理论介绍+ 代码实操（含源码）_rag大模型-CSDN博客](https://blog.csdn.net/m0_59596990/article/details/135310933?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522171229270416800185872895%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=171229270416800185872895&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_click~default-4-135310933-null-null.142^v100^pc_search_result_base7&utm_term=RAG&spm=1018.2226.3001.4187)
* [LangChain（0.0.340）官方文档七：Retrieval——document_loaders_langchain.document_loaders-CSDN博客](https://blog.csdn.net/qq_56591814/article/details/134835702?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~Rate-3-134835702-blog-132709044.235%5Ev43%5Epc_blog_bottom_relevance_base6&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~Rate-3-134835702-blog-132709044.235%5Ev43%5Epc_blog_bottom_relevance_base6&utm_relevant_index=4)
* [正确完成检索增强生成 （RAG）：数据库数据-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/2404168)
* [同济大学发布最新检索增强(RAG)的LLM生成技术综述-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/2373340)
* https://www.bing.com/search?q=weaviate.exceptions.WeaviateStartUpError%3A+Windows+is+not+supported+with+EmbeddedDB.+Please+upvote+this+feature+request+if+you+want&form=ANNTH1&refig=670cf39055334b258dc878eb8357eb42&pc=ASTS&ucpdpc=UCPD&adppc=EDGEESS
## 3 RAG的工作流程

1. **检索：** 利用用户的查询内容，从外部知识源获取相关信息。具体来说，就是将用户的查询通过嵌入模型转化为向量，以便与向量数据库中的其他上下文信息进行比对。通过这种相似性搜索，可以找到向量数据库中最匹配的前 k 个数据。
2. **增强：** 将用户的查询和检索到的额外信息一起嵌入到一个预设的提示模板中。
3. **生成：** 这个经过检索增强的提示内容会被输入到大语言模型 (LLM) 中，以生成所需的输出。
![[RAG工作流程图.png]]

## 4  基于 LangChain 实现RAG
利用 Python 结合 [OpenAI](https://openai.com/) 的大语言模型 (LLM)、[Weaviate](https://weaviate.io/) 的向量数据库以及 [OpenAI](https://openai.com/) 的嵌入模型来实现一个检索增强生成（RAG）流程。在这个过程中将使用 [LangChain](https://www.langchain.com/) 来进行整体编排。
### 准备工作
JSON Lines 是一种文件格式，其中每一行都是有效的 JSON 值。
关于JSON Lines file：[LangChain（0.0.340）官方文档七：Retrieval——document_loaders_langchain.document_loaders-CSDN博客](https://blog.csdn.net/qq_56591814/article/details/134835702?spm=1001.2101.3001.6650.3&utm_medium=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~Rate-3-134835702-blog-132709044.235%5Ev43%5Epc_blog_bottom_relevance_base6&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2~default~CTRLIST~Rate-3-134835702-blog-132709044.235%5Ev43%5Epc_blog_bottom_relevance_base6&utm_relevant_index=4)

1. TextLoad
2. TextSplit
3. Generate and save Embedding

### RAG具体实现
对比了下面几个版本，a_db=mariadb对应的是query，b_db=postgres对应的是vector database
#### Version 1(采纳版本，看这个就行)
1. query：feature
2. vector database：feature，description，examples，category
3. prompt
``` Python
query_merged = """Use the following pieces of retrieved context to answer the question.  
Question: {question}  
Context: {context}  
Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}  
"""  
  
feature_name = ""  
for item in query_json["Feature"]:  
    feature_name += item  
prompt = ChatPromptTemplate.from_template(query_merged)  
chain = (  
        {"context": retriever, "question": RunnablePassthrough()}  
        | prompt  
        | llm  
        | StrOutputParser())
resp = chain.invoke(  
    "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?"  
)
```
4. mapping结果
* llm返回的feature在b_db feature knowledge base中确实存在的个数 / a_db 的 feature总数
```
4.1 a_db = mariadb, b_db = postgres
4.1.1 Functions
不同的k值下，有以下结果（k值的影响似乎不大）
检索相似度前几 k = 默认值:247/401
k = 6:242/401
k = 10:244/401

4.1.2 Operators
检索相似度前几 k = 默认值:0/40



4.2 a_db = mariadb, b_db = clickhouse
4.2.1 Functions
检索相似度前几 k = 默认值:267/401

```


* 统计了mariadb 进行mapping后，没有直接字符串匹配到feature的各类别数量和占比
```
4.1 a_db = mariadb, b_db = postgres
4.1.1 Functions
mapping 字符串匹配直接成功的个数：247
mapping 字符串匹配失败的个数：154
mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.0967741935483871(3/31)
Information Functions:0.55(11/20)
String Functions:0.26229508196721313(16/61)
Date & Time Functions:0.11290322580645161(7/62)
Geographic Functions:0.8780487804878049(72/82)
Miscellaneous Functions:0.45(9/20)
Aggregate Functions:0.0(0/17)
Control Flow Functions:1.0(4/4)
JSON Functions:0.36363636363636365(12/33)
Encryption, Hashing and Compression Functions:0.6875(11/16)
No Category:0.045454545454545456(1/22)
Window Functions:0.0(0/7)
SEQUENCE Functions:0.3333333333333333(1/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:0.75(3/4)
Dynamic Columns Functions:0.125(1/8)
Vector Functions:1.0(3/3)
Galera Functions:0.0(0/3)

4.1.2 Operators
mapping 字符串匹配直接成功的个数：0
mapping 字符串匹配失败的个数：40
mapping 字符串匹配失败的各个类别占比：
Logical Operators:1.0(4/4)
Arithmetic Operators:1.0(7/7)
Comparison Operators:1.0(20/20)
Bit Functions and Operators:1.0(7/7)
Assignment Operators:1.0(2/2)


4.2 a_db = mariadb, b_db = clickhouse
4.2.1 Functions
mapping 字符串匹配直接成功的个数：267
mapping 字符串匹配失败的个数：134
mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.1935483870967742(6/31)
Information Functions:0.1(2/20)
String Functions:0.21311475409836064(13/61)
Date & Time Functions:0.0(0/62)
Geographic Functions:0.5975609756097561(49/82)
Miscellaneous Functions:0.65(13/20)
Aggregate Functions:0.11764705882352941(2/17)
Control Flow Functions:0.25(1/4)
JSON Functions:0.6060606060606061(20/33)
Encryption, Hashing and Compression Functions:0.6875(11/16)
No Category:0.2727272727272727(6/22)
Window Functions:0.14285714285714285(1/7)
SEQUENCE Functions:1.0(3/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:0.25(1/4)
Dynamic Columns Functions:0.625(5/8)
Vector Functions:0.3333333333333333(1/3)
Galera Functions:0.0(0/3)
```
#### Version2
1. query：feature，description，examples，category
2. vector database：feature，description，examples，category
3. prompt
``` Python
query_merged = """Use the following pieces of retrieved context to answer the question.  
Question: {question}  
Context: {context}  
Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}  
"""  
  
feature_name = ""  
for item in query_json["Feature"]:  
    feature_name += item  
prompt = ChatPromptTemplate.from_template(query_merged)  
chain = (  
        {"context": retriever, "question": RunnablePassthrough()}  
        | prompt  
        | llm  
        | StrOutputParser())

# 区别在这一句
resp = chain.invoke(  
    "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?" + data_a[query_json["index"]].page_content  
)
```
4. mapping结果
* llm返回的feature在b_db feature knowledge base中确实存在的个数 / a_db 的 feature总数
```
Functions
检索相似度前几 k = 默认值:233/401
```

#### Version3
该版本为，直接提问llm a_ab对应到b_db中feature是什么featutre，并不涉及到检索增强生成。
1. query：feature
2. vector database：无
3. prompt
``` Python
query_merged = """Use the following pieces of retrieved context to answer the question.  
Question: {question}  
Answer the mapping feature name and reason in json format:{{"Feature":"", "Explanation":"...."}}  
"""
  
feature_name = ""  
for item in query_json["Feature"]:  
    feature_name += item  
prompt = ChatPromptTemplate.from_template(query_merged)  
chain = (  
        {"question": RunnablePassthrough()}  
        | prompt  
        | llm  
        | StrOutputParser())

resp = chain.invoke(  
    "About the feature " + feature_name + " in " + a_db + ", what is the similar feature in " + b_db + "?" + data_a[query_json["index"]].page_content  
)
```
4. mapping结果
* llm返回的feature在b_db feature knowledge base中确实存在的个数 / a_db 的 feature总数
```
Functions
195/401
```

#### Version4
该版本为，直接RAG提问功能最为相似的一个feature向量文档是哪个，**直接返回对应的文档**，而不是像前面几个version提问功能最为相似的feature name是什么。
1. query：feature
2. vector database：feature，description，examples，category
3. prompt
``` Python
query_temp = "About the feature " + feature_name + " in " + a_db + ", which feature has most similar function in " + b_db + "?"  
docs = retriever.get_relevant_documents(query_temp)  
# 提取文档内容字符串  
if docs:  # 检查是否有返回结果  
    top_doc_content = docs[0].page_content  # 获取第一个文档的内容  
else:  
    top_doc_content = "-1:"
```
4. mapping结果
* 直接RAG字符串匹配的效果比较差，如之前所示


#### 总结
1. version1：k的取值影响不大，用默认值即可
2. version1和version2对比：query只包括feature name即可
3. version3：前面提到的先提问llm再进行检索，该方法的效果不如version1
4. 总之，暂定使用version1。version1-version3在b_db中字符串匹配llm回答的feature时，都是字符串完全匹配的，算上部分遗漏实际上mapping正确的数量大于247。针对未直接匹配到的feature，进行RAG检索出最相似的feature向量文档作为近似mapping feature。
5. Operators的mapping效果很不好，后期需要细化




