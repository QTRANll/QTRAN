# 链接
 [Getting Started with OpenAI Evals](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals)


# 正文

[OpenAI Evals](https://github.com/openai/evals/tree/main) 框架包括

1. 用于评估 LLM（大型语言模型）或构建在 LLM 之上的系统的框架。
2. 具有挑战性的评估的开源注册表（An open-source registry of challenging evals）

本笔记本将涵盖：
- Introduction to Evaluation and the [OpenAI Evals](https://github.com/openai/evals/tree/main) library
- Building an Eval
- Running an Eval

#### [什么是evaluation/`evals`？](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#what-are-evaluations-evals)

Evaluation是验证和测试您的 LLM 应用程序正在产生的输出的过程。拥有强大的评估 （“evals”） 将意味着一个更稳定、更可靠的应用程序，能够适应代码和模型的变化。**eval 是用于测量 LLM 或 LLM 系统输出质量的任务。给定输入提示，将生成输出。我们用一组理想的答案来评估这个输出，并找到LLM系统的质量。**

#### [Evaluations的重要性](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#importance-of-evaluations)

如果您正在使用像`GPT-4`这样的基础模型进行构建，那么创建高质量的evals是您可以做的最有影响力的事情之一。**开发 AI 解决方案涉及一个迭代设计过程。[如果没有评估，要理解](https://youtu.be/XGJNo8TpuVA?feature=shared&t=1089)不同的模型版本和提示如何影响您的用例可能会非常困难且耗时。**

借助 OpenAI [的持续模型升级](https://platform.openai.com/docs/models/continuous-model-upgrades)，evals 使您能够以标准化的方式有效地测试用例的模型性能。开发一套针对您的目标定制的评估套件将帮助您快速有效地了解新模型在您的用例中的表现。您还可以将评估作为 CI/CD 管道的一部分，以确保在部署之前达到所需的准确性。

#### [Evals的类型](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#types-of-evals)

我们可以通过两种主要方式evaluate/grade completions：**在代码中编写一些验证逻辑 或者使用模型本身来检查答案。我们将通过一些示例来介绍每个示例。**（目前主要使用前者）


**编写答案检查的逻辑（Writing logic for answer checking）**

**最简单和最常见的 eval 类型有一个输入和一个理想的响应或答案。** 例如 我们可以有一个 eval 样本，其中输入是“奧巴馬是哪一年首次当选总统 时间？“，而最理想的答案是”2008年”。我们将输入输入到模型中并得到完成。如果模型 说“2008”，然后将其评定为正确。我们可以编写一个字符串匹配来检查完成是否包含短语“2008”。如果是这样，我们认为它是正确的。

考虑另一个评估，其中输入是为了生成有效的 JSON：我们可以编写一些代码来 尝试将completion解析为 JSON，然后认为completion正确（如果是 可解析）。

**模型分级：一个两阶段的过程，模型首先回答问题，然后我们让另一个模型来查看响应以检查它是否正确。（Model grading: A two stage process where the model first answers the question, then we ask a another model to look at the response to check if it’s correct.）**

考虑一个输入，要求模型写一个有趣的笑话。然后，该模型会生成一个 completion 。然后，我们为模型创建一个新的包含completion的输入来回答以下问题：“以下的笑话好笑吗？首先一步一步地解释，然后回答“是”或“否”。最后，如果新模型完成以“yes”结尾，则认为原始completion是正确的。

模型分级最适合最新、最强大的模型，例如 `GPT-4` ，如果我们赋予它们能力 在做出判断之前进行推理。模型分级将具有错误率，因此在大规模运行evals之前，通过人工评估来验证性能非常重要。为了获得最佳效果，使用与完成completion的模型不同的模型进行分级，例如使用 `GPT-4` 对的`GPT-3.5`答案进行评分。

#### [OpenAI 评估模板](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#openai-eval-templates)（ [OpenAI Eval Templates](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#openai-eval-templates)）
在使用 evals 时，我们发现了几个“模板”，它们适应许多不同的基准测试。我们在 OpenAI Evals 库中实现了这些模板，以简化新evals的开发。例如，我们定义了 2 种类型的评估模板，这些模板可以开箱即用：

- **基本评估模板**（**Basic Eval Templates**）：**这些模板包含确定性函数，用于将输出与ideal_answers进行比较。在期望的模型响应变化很小的情况下，例如回答多项选择题或回答简单问题并给出简单的答案，我们发现以下模板很有用。**
- **模型分级模板**（**Model-Graded Templates**）：这些模板包含函数，其中 LLM 将输出与ideal_answers进行比较并尝试判断准确性。在期望的模型响应可能包含显着变化的情况下，例如回答开放式问题，我们发现使用模型对自身进行评分是自动评估的可行策略。

### [Getting Setup](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#getting-setup)

首先，转到 [github.com/openai/evals](https://github.com/openai/evals)，使用`git clone git@github.com:openai/evals.git`克隆存储库并完成[setup instructions](https://github.com/openai/evals)。

要稍后在此笔记本中运行 evals，您需要设置并指定 OpenAI API 密钥。获取 API 密钥后，请使用环境变量`OPENAI_API_KEY`指定它。

请注意在运行 evals 时使用 API 的相关费用。
``` Python
from openai import OpenAI
import pandas as pd

client = OpenAI()
```

## [Building an evaluation for OpenAI Evals framework](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#building-an-evaluation-for-openai-evals-framework)

从本质上讲，eval 是在 YAML 文件中定义的数据集和 eval 类。要开始创建评估，我们需要

1. `jsonl`格式的测试数据集。
2. 要使用的评估模板
### [Creating the eval dataset](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#creating-the-eval-dataset)
让我们为一个用例创建一个数据集，在该用例中，我们正在评估模型生成语法正确的 SQL 的能力。在这个用例中，我们有一系列与汽车制造相关的表格

首先，我们需要创建一个我们想要评估的系统提示(system prompt)。我们将传递模型的说明以及表结构的概述：

``` JSON
"TASK: Answer the following question with syntactically correct SQLite SQL. The SQL should be correct and be in context of the previous question-answer pairs.\nTable car_makers, columns = [*,Id,Maker,FullName,Country]\nTable car_names, columns = [*,MakeId,Model,Make]\nTable cars_data, columns = [*,Id,MPG,Cylinders,Edispl,Horsepower,Weight,Accelerate,Year]\nTable continents, columns = [*,ContId,Continent]\nTable countries, columns = [*,CountryId,CountryName,Continent]\nTable model_list, columns = [*,ModelId,Maker,Model]\nForeign_keys = [countries.Continent = continents.ContId,car_makers.Country = countries.CountryId,model_list.Maker = car_makers.Id,car_names.Model = model_list.Model,cars_data.Id = car_names.MakeId]"
```

对于这个提示，我们可以提出一个具体的问题：

```
"Q: how many car makers are their in germany?"
```

我们有一个预期的答案：

```
"A: SELECT count ( * )  FROM CAR_MAKERS AS T1 JOIN COUNTRIES AS T2 ON T1.Country   =   T2.CountryId WHERE T2.CountryName   =   'germany'"
```
数据集需要采用以下格式：

``` JSON
"input": [{"role": "system", "content": "<input prompt>"}, {"role": "user", "content": <user input>}, "ideal": "correct answer"]
```

把它们放在一起，我们得到：

``` JSON
{"input": [{"role": "system", "content": "TASK: Answer the following question with syntactically correct SQLite SQL. The SQL should be correct and be in context of the previous question-answer pairs.\nTable car_makers, columns = [*,Id,Maker,FullName,Country]\nTable car_names, columns = [*,MakeId,Model,Make]\nTable cars_data, columns = [*,Id,MPG,Cylinders,Edispl,Horsepower,Weight,Accelerate,Year]\nTable continents, columns = [*,ContId,Continent]\nTable countries, columns = [*,CountryId,CountryName,Continent]\nTable model_list, columns = [*,ModelId,Maker,Model]\nForeign_keys = [countries.Continent = continents.ContId,car_makers.Country = countries.CountryId,model_list.Maker = car_makers.Id,car_names.Model = model_list.Model,cars_data.Id = car_names.MakeId]\n"}, {"role": "system", "content": "Q: how many car makers are their in germany"}, "ideal": ["A: SELECT count ( * )  FROM CAR_MAKERS AS T1 JOIN COUNTRIES AS T2 ON T1.Country   =   T2.CountryId WHERE T2.CountryName   =   'germany'"]}
```

加快构建evals数据集过程的一种方法是使用 `GPT-4`生成合成数据
``` Python
## Use GPT-4 to generate synthetic data
# Define the system prompt and user input (these should be filled as per the specific use case)
system_prompt = """You are a helpful assistant that can ask questions about a database table and write SQL queries to answer the question.
    A user will pass in a table schema and your job is to return a question answer pairing. The question should relevant to the schema of the table,
    and you can speculate on its contents. You will then have to generate a SQL query to answer the question. Below are some examples of what this should look like.

    Example 1
    ```````````
    User input: Table museum, columns = [*,Museum_ID,Name,Num_of_Staff,Open_Year]\nTable visit, columns = [*,Museum_ID,visitor_ID,Num_of_Ticket,Total_spent]\nTable visitor, columns = [*,ID,Name,Level_of_membership,Age]\nForeign_keys = [visit.visitor_ID = visitor.ID,visit.Museum_ID = museum.Museum_ID]\n
    Assistant Response:
    Q: How many visitors have visited the museum with the most staff?
    A: SELECT count ( * )  FROM VISIT AS T1 JOIN MUSEUM AS T2 ON T1.Museum_ID   =   T2.Museum_ID WHERE T2.Num_of_Staff   =   ( SELECT max ( Num_of_Staff )  FROM MUSEUM ) 
    ```````````

    Example 2
    ```````````
    User input: Table museum, columns = [*,Museum_ID,Name,Num_of_Staff,Open_Year]\nTable visit, columns = [*,Museum_ID,visitor_ID,Num_of_Ticket,Total_spent]\nTable visitor, columns = [*,ID,Name,Level_of_membership,Age]\nForeign_keys = [visit.visitor_ID = visitor.ID,visit.Museum_ID = museum.Museum_ID]\n
    Assistant Response:
    Q: What are the names who have a membership level higher than 4?
    A: SELECT Name   FROM VISITOR AS T1 WHERE T1.Level_of_membership   >   4 
    ```````````

    Example 3
    ```````````
    User input: Table museum, columns = [*,Museum_ID,Name,Num_of_Staff,Open_Year]\nTable visit, columns = [*,Museum_ID,visitor_ID,Num_of_Ticket,Total_spent]\nTable visitor, columns = [*,ID,Name,Level_of_membership,Age]\nForeign_keys = [visit.visitor_ID = visitor.ID,visit.Museum_ID = museum.Museum_ID]\n
    Assistant Response:
    Q: How many tickets of customer id 5?
    A: SELECT count ( * )  FROM VISIT AS T1 JOIN VISITOR AS T2 ON T1.visitor_ID   =   T2.ID WHERE T2.ID   =   5 
    ```````````
    """

user_input = "Table car_makers, columns = [*,Id,Maker,FullName,Country]\nTable car_names, columns = [*,MakeId,Model,Make]\nTable cars_data, columns = [*,Id,MPG,Cylinders,Edispl,Horsepower,Weight,Accelerate,Year]\nTable continents, columns = [*,ContId,Continent]\nTable countries, columns = [*,CountryId,CountryName,Continent]\nTable model_list, columns = [*,ModelId,Maker,Model]\nForeign_keys = [countries.Continent = continents.ContId,car_makers.Country = countries.CountryId,model_list.Maker = car_makers.Id,car_names.Model = model_list.Model,cars_data.Id = car_names.MakeId]"

messages = [{
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": user_input
    }
]

completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    temperature=0.7,
    n=5
)

for choice in completion.choices:
    print(choice.message.content + "\n")

```

一旦我们有了合成数据，我们就需要转换它以匹配 eval 数据集的格式。

``` Python
eval_data = []
input_prompt = "TASK: Answer the following question with syntactically correct SQLite SQL. The SQL should be correct and be in context of the previous question-answer pairs.\nTable car_makers, columns = [*,Id,Maker,FullName,Country]\nTable car_names, columns = [*,MakeId,Model,Make]\nTable cars_data, columns = [*,Id,MPG,Cylinders,Edispl,Horsepower,Weight,Accelerate,Year]\nTable continents, columns = [*,ContId,Continent]\nTable countries, columns = [*,CountryId,CountryName,Continent]\nTable model_list, columns = [*,ModelId,Maker,Model]\nForeign_keys = [countries.Continent = continents.ContId,car_makers.Country = countries.CountryId,model_list.Maker = car_makers.Id,car_names.Model = model_list.Model,cars_data.Id = car_names.MakeId]"

for choice in completion.choices:
    question = choice.message.content.split("Q: ")[1].split("\n")[0]  # Extracting the question
    answer = choice.message.content.split("\nA: ")[1].split("\n")[0]  # Extracting the answer
    eval_data.append({
        "input": [
            {"role": "system", "content": input_prompt},
            {"role": "user", "content": question},
        ],
        "ideal": answer
    })

for item in eval_data:
    print(item)
```

接下来，我们需要创建 eval 注册表(eval registry)以在框架中运行它。

evals 框架需要一个具有以下属性结构的`.yaml`文件：

- `id`- 评估的标识符
- `description`- 评估的简短描述
- `disclaimer`- 关于评估的附加说明
- `metrics`- 我们可以选择三种类型的评估指标：**match、includes、fuzzyMatch**

对于我们的评估，我们将配置以下内容：
``` Python
"""
spider-sql:
  id: spider-sql.dev.v0
  metrics: [accuracy]
  description: Eval that scores SQL code from 194 examples in the Spider Text-to-SQL test dataset. The problems are selected by taking the first 10 problems for each database that appears in the test set.
    Yu, Tao, et al. \"Spider; A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task.\" Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, 2018, https://doi.org/10.18653/v1/d18-1425.
  disclaimer: Problems are solved zero-shot with no prompting other than the schema; performance may improve with training examples, fine tuning, or a different schema format. Evaluation is currently done through model-grading, where SQL code is not actually executed; the model may judge correct SQL to be incorrect, or vice-versa.
spider-sql.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: sql/spider_sql.jsonl
    eval_type: cot_classify
    modelgraded_spec: sql
  """""
```

## [Running an evaluation](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#running-an-evaluation)
我们可以使用 `oaieval`CLI 运行此评估。要进行设置，请安装库：`pip install .`（如果您在本地运行 [OpenAI Evals 库](https://cookbook.openai.com/examples/evaluation/github.com/openai/evals)）或者`pip install oaieval`如果您正在运行现有的 eval。

然后，使用 CLI 运行 eval ：`oaieval gpt-3.5-turbo spider-sql`

此命令需要模型名称和评估集名称。请注意，我们提供了两个命令行接口 （CLI）：用于运行单个 eval 的`oaieval`和运行一组 eval的 `oaievalset`。有效的 eval 名称在 `evals/registry/evals`下的 YAML 文件中 指定，其相应的实现可在 `evals/elsuite`中找到。

```
!pip install evals --quiet
```

 `oaieval` CLI 可以接受各种flags来修改默认行为。**您可以运行`oaieval --help`以查看 CLI 选项的完整列表。(查看有哪些matrics)**

运行该命令后，您将看到打印到控制台的最终准确性报告，以及包含完整报告的临时文件的文件路径。

这些 CLI 可以接受各种标志来修改其默认行为。您可以运行以查看 CLI 选项的完整列表。`oaieval --help`

`oaieval`将按照上述单元格 4 中指定的格式在`evals/registry/evals`目录中搜索`spider-sql` eval YAML 文件。eval 数据集的路径在 eval YAML 文件的 args中： 参数`samples_jsonl: sql/spider_sql.jsonl` ，文件内容采用 JSONL 格式（如上述步骤 3 中生成）。

运行该命令后，您将看到打印到控制台的最终准确性报告，以及包含完整报告的临时文件的文件路径。
```
!oaieval gpt-3.5-turbo spider-sql --max_samples 25
```

`oaievalset`需要模型名称和评估集名称，在  `evals/registry/eval_sets`下的YAML 文件指定了有效选项。


### [Going through eval logs](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#going-through-eval-logs)
评估日志位于 `/tmp/evallogs` ，并且为每个evaluation运行创建不同的日志文件。
``` Python
log_name = '240327024443FACXGMKA_gpt-3.5-turbo_spider-sql.jsonl' # "EDIT THIS" - copy from above
events = f"/tmp/evallogs/{log_name}"
display(pd.read_json(events, lines=True).head(5))
```


``` Python
# processing the log events generated by oaieval
with open(events, "r") as f:
    events_df = pd.read_json(f, lines=True)
```

此文件将包含评估的结构化日志。第一个条目提供了评估的详细规范，包括完成函数、评估名称、运行配置、创建者名称、运行 ID 和创建时间戳。
a detailed specification of the evaluation, including the completion functions, evaluation name, run configuration, creator’s name, run ID, and creation timestamp
``` Python
display(events_df.iloc[0].spec)
```

```
结果：
{'completion_fns': ['gpt-3.5-turbo'],
 'eval_name': 'spider-sql.dev.v0',
 'base_eval': 'spider-sql',
 'split': 'dev',
 'run_config': {'completion_fns': ['gpt-3.5-turbo'],
  'eval_spec': {'cls': 'evals.elsuite.modelgraded.classify:ModelBasedClassify',
   'registry_path': '/Users/shyamal/.virtualenvs/openai/lib/python3.11/site-packages/evals/registry',
   'args': {'samples_jsonl': 'sql/spider_sql.jsonl',
    'eval_type': 'cot_classify',
    'modelgraded_spec': 'sql'},
   'key': 'spider-sql.dev.v0',
   'group': 'sql'},
  'seed': 20220722,
  'max_samples': 25,
  'command': '/Users/shyamal/.virtualenvs/openai/bin/oaieval gpt-3.5-turbo spider-sql --max_samples 25',
  'initial_settings': {'visible': False}},
 'created_by': '',
 'run_id': '240327024443FACXGMKA',
 'created_at': '2024-03-27 02:44:43.626043'}
```

让我们再看一下提供评估最终报告的条目。
``` Python
display(events_df.dropna(subset=['final_report']).iloc[0]['final_report'])
```
```
{'counts/Correct': 20, 'counts/Incorrect': 5, 'score': 0.8}
```


我们还可以查看提供特定样本 （`sample_id`）、结果、事件类型和元数据的单个评估事件。
``` Python
pd.set_option('display.max_colwidth', None)  # None means no truncation

display(events_df.iloc[2][['run_id', 'event_id', 'sample_id', 'type', 'data', 'created_at']])
```

![[Pasted image 20240817225322.png]]

``` Python
# Inspect samples
for i, row in events_df[events_df['type'] == 'sampling'].head(5).iterrows():
    data = pd.json_normalize(row['data'])
    print(f"Prompt: {data['prompt'].iloc[0]}")
    print(f"Sampled: {data['sampled'].iloc[0]}")
    print("-" * 10)
```

![[Pasted image 20240817225414.png]]

让我们回顾一下我们的失败，以了解哪些测试没有成功。

``` Python
def pretty_print_text(prompt):
    # Define markers for the sections
    markers = {
        "question": "[Question]:",
        "expert": "[Expert]:",
        "submission": "[Submission]:",
        "end": "[END DATA]"
    }
    
    # Function to extract text between markers
    def extract_text(start_marker, end_marker):
        start = prompt.find(start_marker) + len(start_marker)
        end = prompt.find(end_marker)
        text = prompt[start:end].strip()
        if start_marker == markers["question"]:
            text = text.split("\n\nQuestion:")[-1].strip() if "\n\nQuestion:" in text else text
        elif start_marker == markers["submission"]:
            text = text.replace("```sql", "").replace("```", "").strip()
        return text
    
    # Extracting text for each section
    question_text = extract_text(markers["question"], markers["expert"])
    expert_text = extract_text(markers["expert"], markers["submission"])
    submission_text = extract_text(markers["submission"], markers["end"])
    
    # HTML color codes and formatting
    colors = {
        "question": '<span style="color: #0000FF;">QUESTION:<br>', 
        "expert": '<span style="color: #008000;">EXPECTED:<br>',  
        "submission": '<span style="color: #FFA500;">SUBMISSION:<br>' 
    }
    color_end = '</span>'
    
    # Display each section with color
    from IPython.display import display, HTML
    display(HTML(f"{colors['question']}{question_text}{color_end}"))
    display(HTML(f"{colors['expert']}{expert_text}{color_end}"))
    display(HTML(f"{colors['submission']}{submission_text}{color_end}"))
```

``` Python
# Inspect metrics where choice is made and print only the prompt, result, and expected result if the choice is incorrect
for i, row in events_df[events_df['type'] == 'metrics'].iterrows():
    if row['data']['choice'] == 'Incorrect':
        # Get the previous row's data, which contains the prompt and the expected result
        prev_row = events_df.iloc[i-1]
        prompt = prev_row['data']['prompt'][0]['content'] if 'prompt' in prev_row['data'] and len(prev_row['data']['prompt']) > 0 else "Prompt not available"
        expected_result = prev_row['data'].get('ideal', 'Expected result not provided')
        
        # Current row's data will be the actual result
        result = row['data'].get('result', 'Actual result not provided')
        
        pretty_print_text(prompt)
        print("-" * 40)
```

![[Pasted image 20240817225510.png]]

回顾一些失败，我们看到以下内容：

- 第二个错误的答案与“模板”表进行了不必要的联接。我们的评估能够准确地识别出这一点，并将其标记为不正确。
- 很少有其他答案具有细微的语法差异，导致答案被标记。
    - 在这种情况下，值得探索的是，我们是否应该继续迭代提示以确保某些风格选择，或者我们是否应该修改评估套件以捕获这种变化。
    - 这种类型的失败暗示了可能需要对模型分级的评估作为确保结果分级准确性的一种方式

# [Conclusion](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals#conclusion)

构建有效的评估是基于 LLM 的应用程序开发周期的核心部分。OpenAI Evals 框架提供了开箱即用构建 evals 的核心结构，并允许您为各种用例快速启动新测试。在本指南中，我们逐步演示了如何创建评估、运行评估并分析结果。

本指南中显示的示例代表了 evals 的直接前向用例。在您继续探索此框架时，我们建议您探索为实际生产用例创建更复杂的模型分级评估。祝您评估愉快！

