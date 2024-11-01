# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/14 20:26
# @Author  : shaocanfan
# @File    : temp.py
# @Intro   :


import json
import os
import openai
from langchain_community.chat_models import ChatOpenAI


os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
os.environ["OPENAI_API_KEY"] = ""  # app5
os.environ["OPENAI_API_BASE"] = "https://ai-yyds.com/v1"  # "https://ai-yyds.com/v1"
openai.api_key = os.environ['OPENAI_API_KEY']
openai.api_base = os.environ['OPENAI_API_BASE']


llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini")
# 提问
question = "中国的国宝是什么"
response = llm.predict(question)

# 打印回答
print(response)
