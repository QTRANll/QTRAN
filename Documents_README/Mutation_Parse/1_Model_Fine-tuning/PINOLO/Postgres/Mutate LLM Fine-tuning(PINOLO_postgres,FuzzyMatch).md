#### Section0: 设置环境变量和注册completion-fn
1. 要运行eval，你需要设置并指定你的[OpenAI API密钥](https://platform.openai.com/account/api-keys)。获取API密钥后，使用['OPENAI_API_KEY '环境变量](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key)指定它。参考以下链接在Edit Configuration中添加环境变量： https://blog.csdn.net/qq_36797973/article/details/122096750
2. 注册要使用的语言模型的接口，参考[[completion-fns#Registering Completion Functions]].将`eval/registry/completion_fns`中的Completion Functions注册为`yaml`文件(该yaml文件位于`evals\registry\completion_fns`)。下面介绍如何注册已有语言模型和自行微调的模型。
* 注册已有的openai模型：在`evals/registry.py`中的is_chat_model(model_name: str)函数中的CHAT_MODEL_NAMES数组中进行添加
```
CHAT_MODEL_NAMES = {"gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k", "gpt-4o-mini"}
```
* 注册自行微调的模型：先将Resgistry的make_completion_fn方法中的`# spec.args["registry"] = self`注释掉（因为这里报错，不涉及参数"resgistry"），然后在.yaml中添加的补全函数"gpt-4o-mini"的注册信息，
```yaml
openai/pinolo-mutate-llm-postgres:
  class: evals.completion_fns.openai:OpenAIChatCompletionFn
  args:
    model: ft:gpt-4o-mini-2024-07-18:personal:pinolo-mutate-llm:9x9umpsR
    api_base: "https://api.openai.com/v1"
    api_key: "sk-TZTfbY7z8DTGoAXrcvUX0ulZVXCAdPyPlGzjDOfAUFT3BlbkFJ8bQ0FsADuBAcjskOTXqWocvcddmOH5MK_5RGKcZV8A"
```

`openai/pinolo-mutate-llm-postgres`:这是用于访问`oaieval`补全函数的顶级键。
`class`:这是你实现补全函数协议的路径。该类需要在python环境中可导入。
`args`:这些是在实例化完成函数时传递给它的参数。

注意：报错`ModuleNotFoundError: No module named 'langchain_community'` 的解决方法如下 https://stackoverflow.com/questions/77998568/langchain-modulenotfounderror-no-module-named-langchain-community

#### Section 1: Specification File
将下面的内容放在`evals/registry/evals/FuzzyMatch_pinolo_mutate_llm_postgres.yaml`中（注意：samples_jsonl的隐藏前缀为`evals/registry/data/`）。

```
FuzzyMatch_pinolo_mutate_llm_postgres:  
  id: FuzzyMatch_pinolo_mutate_llm_postgres.test.v1  
  description: evaluate the mutate llm for postgres with four mutate strategies.
  metrics: [accuracy,f1_score]  
FuzzyMatch_pinolo_mutate_llm_postgres.test.v1:  
  class: evals.elsuite.basic.fuzzy_match:FuzzyMatch  
  args:  
    samples_jsonl: pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl
```
#### Section 2: Specification Objects
使用 YAML 文件来构造`evals`中的 Specification object，该对象将用于`evals.elsuite`中定义的评估工作流。

`Registry`类用于 
1） 检索Specification File的信息
2） 根据这些信息构造 Specification object。

调用以下方法来根据Specification File的信息获取 Specification object。

``` Python
Registry().get_eval_set(name) -> evals.base.EvalSetSpec  
Registry().get_eval(name) -> Evals.base.EvalSpec
```

在我们的示例中，我们可以调用以下代码行：

``` Python
evals.eval.set_max_samples(80)  # 最大值  
  
# define the arguments:gpt-3.5-turbo  
args = {  
    "completion_fn": "langchain/llm/gpt-4o-mini",  
    "eval": "FuzzyMatch_pinolo_mutate_llm_postgres",  
    "cache": True,  
    "seed": 20220722  
}  
args = SimpleNamespace(**args)


# evaluation specification  
registry = Registry()  
eval_spec = registry.get_eval(args.eval)  
print(eval_spec)  
  
"""
EvalSpec(cls='evals.elsuite.basic.fuzzy_match:FuzzyMatch', registry_path=WindowsPath('D:/PycharmFiles/evals-main/evals/registry'), args={'samples_jsonl': 'evals/registry/data/pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl'}, key='FuzzyMatch_pinolo_mutate_llm_postgres.test.v1', group='FuzzyMatch_pinolo_mutate_llm_postgres')
"""
```
#### Section 3: Evaluation Protocols
评估协议定义了如何处理响应或完成（responses or completions），以及如何计算最终的准确性指标。`evals.Eval` 定义此类协议的接口。

获得规范对象 (`EvalSpec`) 后，调用方法`Registry().get_class`来获取继承自`evals.Eval`的具体类。

``` Python
Registry().get_class(spec: EvalSpec) -> evals.Eval
```

在我们的示例中，与评估变量`FuzzyMatch_pinolo_mutate_llm_postgres.test.v1`关联的类`FuzzyMatch`来自模块`evals.elsuite.basic.fuzzy_match`，如文件`.yaml`中的最后一行所定义。因此，它将输出一个对象`evals.elsuite.basic.fuzzy_match.FuzzyMatch`，如下所示。

`functools.partial`将保持类和`EvalSpec`类相同，并在对象中定义了部分`EvalSpec`类中定义的参数。

``` Python
# eval object  
eval_class = registry.get_class(eval_spec)  
print(eval_class)

"""
functools.partial(<class 'evals.elsuite.basic.fuzzy_match.FuzzyMatch'>, samples_jsonl='evals/registry/data/pinolo_mutate_llm/postgres/postgres_eval_dataset_formatted1.0.jsonl')
"""
```

然后，可以使用这个类来实例化具有指定完成函数（completion functions）的对象。
``` Python
completion_fn_instance = registry.make_completion_fn(args.completion_fn)  
eval: Eval = eval_class(  
    completion_fns=[completion_fn_instance],  
    eval_registry_path=eval_spec.registry_path,  
    samples_jsonl=eval_spec.args["samples_jsonl"],  
    name=eval_spec.key,  # match_mmlu_machine_learning.test.v1,  
    seed=args.seed  
)
```

#### Section 4: Running Evaluation
每个`evals.Eval`类都需要实现 `eval_sample`和`run`方法。只需调用`evals.Eval.run`以启动该过程即可。

那么，我们先来看看fuzzy_match方法的实现。

``` Python
class FuzzyMatch(evals.Eval):  
    def __init__(  
        self,  
        completion_fns: list[CompletionFn],  
        samples_jsonl: str,  
        *args,  
        max_tokens: int = 6000,  
        **kwargs,  
    ):  
        super().__init__(completion_fns, *args, **kwargs)  
        assert len(completion_fns) == 1, "FuzzyMatch only supports one completion fn"  
        self.max_tokens = max_tokens  
        self.samples_jsonl = samples_jsonl  
    
    ...
  
    def run(self, recorder: RecorderBase):  
        samples = self.get_samples()  
        self.eval_all_samples(recorder, samples)  
  
        return {  
            "accuracy": np.mean(recorder.get_scores("accuracy")),  
            "f1_score": np.mean(recorder.get_scores("f1_score")),  
        }
```

run函数有三个步骤：
- 通过`get_samples`加载数据
- 调用`eval_all_samples`：它将为每个样本调用`eval_sample`。
- 汇总记录的结果。

现在，让我们看一下该方法（`eval_sample`）的实现。

``` Python
class FuzzyMatch(evals.Eval):  
    ...
    def eval_sample(self, test_sample, rng):  
        # 重写eval类的函数，评估单个测试样本:接受两个参数:test_sample(要评估的样本)和rng(随机数生成器,在这里没有使用,del删除了)  
        del rng  
  
        # 检查test_sample的格式合法性  
        assert isinstance(test_sample, dict), "sample must be a dict"  
        assert "input" in test_sample, "sample must have an 'input' key"  
        assert "ideal" in test_sample, "sample must have an 'ideal' key"  
  
        # 从test_sample字典中提取"input"和"ideal"的值,并分别赋给prompt和correct_answers变量。  
        prompt, correct_answers = test_sample["input"], test_sample["ideal"]  
        # 检查correct_answers变量是否是一个列表:如果不是,函数会将它转换为一个只包含correct_answers值的列表  
        if not isinstance(correct_answers, list):  
            correct_answers = [correct_answers]  
  
        result = self.completion_fn(  
            prompt=prompt,  
            temperature=0.0,  # Q: why are these hardcoded?  
            max_tokens=self.max_tokens,  
        )  
  
        # 这一行从result对象中提取第一个completion,并将其赋给sampled变量，既模型给出的答案。  
        sampled = result.get_completions()[0]  
  
        # 使用列表推导式创建一个布尔值列表,表示sampled文本是否与correct_answers（列表中可能有多个ideal answer）中的每个答案模糊匹配。  
        matches = [utils.fuzzy_match(sampled, correct_answer) for correct_answer in correct_answers]  
  
        # 记录match结果：  
        # correct=True in matches,一个布尔值,表示sampled文本是否与任何正确答案匹配  
        # expected=correct_answers,  
        # picked=[sampled for i in range(len(correct_answers)) if matches[i]],一个列表,包含每个与正确答案匹配的sampled文本  
        # 等价于picked = []  
        # for i in range(len(correct_answers)):        #     if matches[i]:        #         picked.append(sampled)        evals.record.record_match(  
            True in matches,  
            expected=correct_answers,  
            picked=[sampled for i in range(len(correct_answers)) if matches[i]],  
        )  
  
        # 记录metrics结果：  
        # accuracy=float(True in matches),如果sampled文本与任何正确答案匹配,则计数为1.0,否则计数为0.0。  
        # f1_score=utils.f1_score(sampled, correct_answers):F1得分,使用utils.f1_score()函数计算,输入参数为sampled文本和正确答案列表  
        evals.record.record_metrics(  
            accuracy=float(True in matches),  
            f1_score=utils.f1_score(sampled, correct_answers),  
        )  
```


`eval_sample`也有三个步骤：

- 构造提示
- 查询模型以进行完成（completion）
- 计算和记录指标（例如，一个布尔值，用于指示完成completion是否与预期响应匹配）


在正在运行的示例中，调用以下代码行。下一节将解释 recorder的使用。

``` Python
result = eval.run(recorder)
```


#### Section 5: Result Recording
`openai/evals`框架中的recorder是一个实用程序，用于记录、存储和管理评估结果。它提供了一种结构化的方式来保存评估详细信息、结果和其他相关信息。

**1. Instantiation of the Recorder**
`Recorder`的实例化需要创建一个`RunSpec`对象，以保存有关评估运行的各种详细信息。而这个运行规范会被保存到 `recorder_path`的JSON文件中。

``` Python
eval_name = eval_spec.key # match_mmlu_machine_learning.test.v1  
run_spec = evals.base.RunSpec(
	completion_fns=[args.completion_fn],  
	eval_name=eval_name,  
	base_eval=eval_name.split(".")[0],  
	split=eval_name.split(".")[1],  
	run_config = {  
	   "completion_fns": [args.completion_fn],  
	   "eval_spec": eval_spec,  
	   "seed": args.seed,  
	},  
	created_by="xinzhe", # my name  
)  

# A path is defined for the recorder to save the evaluation logs.  
recorder_path = f"evallogs/{run_spec.run_id}_{args.completion_fn}_{args.eval}.jsonl"  

recorder = evals.record.LocalRecorder(recorder_path, run_spec)
```


**2. The Use of Recoder**
借助 `eval.run`运行评估后 ，调用方法`recorder.record_final_report(result)`将评估结果写入本地 JSONL 文件。

``` Python
# save evaluation into recoder object  
result = eval.run(recorder)  
# write evaluation result into local json file  
recorder.record_final_report(result)
```

此文件将包含评估的结构化日志。
- Evaluation Specification（评估规范）：第一个条目提供了评估的详细规范，包括 the completion functions, evaluation name, run configuration, creator’s name, run ID, and creation timestamp（完成函数、评估名称、运行配置、创建者姓名、运行 ID 和创建时间戳）。
``` JSON
{  
  "spec": {  
    "completion_fns": [  
      "gpt-3.5-turbo"  
    ],  
    "eval_name": "match_mmlu_machine_learning.test.v1",  
    "base_eval": "match_mmlu_machine_learning",  
    "split": "test",  
    "run_config": {  
      "completion_fns": [  
        "gpt-3.5-turbo"  
      ],  
      "eval_spec": {  
        "cls": "evals.elsuite.basic.match:Match",  
        "args": {  
          "few_shot_jsonl": "evals/registry/data/mmlu/machine_learning/few_shot.jsonl",  
          "num_few_shot": 4,  
          "samples_jsonl": "evals/registry/data/mmlu/machine_learning/samples.jsonl"  
        },  
        "key": "match_mmlu_machine_learning.test.v1",  
        "group": "mmlu"  
      },  
      "seed": 20220722  
    },  
    "created_by": "xinzhe",  
    "run_id": "230816022025W4JC7NZA",  
    "created_at": "2023-08-16 02:20:25.272607"  
  }  
}
```

- Final Report（最终报告）：第二个条目提供评估的最终报告，其中包括准确性及其引导标准偏差（bootstrap standard deviation）等指标。
``` JSON
{  
  "final_report": {  
    "accuracy": 0.5,  
    "boostrap_std": 0.18939640968085958  
  }  
}
```

* Individual Evaluation Events（单个评估事件）：后续条目记录单个评估事件，详细说明specific samples (`sample_id`), their results, event IDs, event types, and timestamps（特定样本、其结果、事件 ID、事件类型和时间戳）。
``` JSON
{  
  "run_id": "230816022025W4JC7NZA",  
  "event_id": 15,  
  "sample_id": "match_mmlu_machine_learning.test.44",  
  "type": "match",  
  "data": {  
    "correct": true,  
    "expected": "D",  
    "picked": "D",  
    "sampled": "D",  
    "options": [  
      "D"  
    ]  
  },  
  "created_by": "xinzhe",  
  "created_at": "2023-08-16 02:39:46.577700+00:00"  
}
```
