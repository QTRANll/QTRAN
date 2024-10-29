# 链接

* [Mastering OpenAI’s ‘evals’: A Deep Dive into Evaluating LLMs | by Xinzhe Li, PhD in Language Intelligence | Level Up Coding (gitconnected.com)](https://levelup.gitconnected.com/mastering-openais-evals-a-deep-dive-into-evaluating-llms-22433097bc99)
* [掌握 OpenAI 的 "evals"：深入评估LLMs - 腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/news/1170800)

# Introduction

openai/evals 不仅仅是另一个平台;它是一个关键工具，旨在评估 LLM（大型语言模型）以及将 LLM 编织到其核心的复杂系统。在通过图灵测试已成为人工智能黄金标准的时代，确保对这些模型进行严格评估比以往任何时候都更加重要。让我们深入了解 openai/evals 的 LLM 评估。

## Easy Use of evals

**安装该工具后，我们只需在命令行中定义completion function（模型的使用、提示策略......）和评估任务（评估指标、数据集和一般协议），即可运行评估。**

- `completion_fn`(`gpt-3.5-turbo`)：我只想评估 openai Chat LLM。因此，我可以使用任何 openai 模型 ID，例如“gpt-3.5-turbo”、“gpt-4”、“gpt-4–32k”。在这里，我使用`.`,但是 evals 框架为其他 LLM 管道线提供了通用协议，并将它们命名为完成函数，例如 [LangChain LLM](https://github.com/openai/evals/blob/main/evals/completion_fns/langchain_llm.py)。
- `eval_task`(`match_mmlu_machine_learning`)：**它指的是 evals.registry.evals 目录中的 YAML 文件。** 该文件定义了特定评估任务的参数，例如 _evaluation_ _data, evaluation metrics 和prompting strategies_。有关详细信息，请参阅**Section 1: Specification File**。这里，指的是下一个要点中讨论的 **Specification File**。

```
oaieval gpt-3.5-turbo match_mmlu_machine_learning
```

* `Specification file`(`match_mmlu_machine_learning` `eval_task` `mmlu.yaml` `evals/registry/evals/` `eval_task` )：**它指定了评估指标、数据和通用协议(evaluation metrics, data and general protocols)。例如，在目录中命名的 YAML 文件中定义它后有效。** 重要的是，第一行对应于`.`的名称。这将在上述命令中使用。下面的样例指定了一个少样本评估和 [MMLU 机器学习数据集。](https://github.com/hendrycks/test) **在整篇文章中，我将使用此**specification**作为运行示例。**
```
match_mmlu_machine_learning:  
   id: match_mmlu_machine_learning.test.v1  
   metrics:  
   - accuracy  
match_mmlu_machine_learning.test.v1:  
   args:  
     few_shot_jsonl:
     evals/registry/data/mmlu/machine_learning/few_shot.jsonl  
     num_few_shot: 4  
     samples_jsonl: evals/registry/data/mmlu/machine_learning/samples.jsonl 
   class: evals.elsuite.basic.match:Match
```

## About This Article

但是，到目前为止，还没有官方文档介绍该框架的工作原理。这限制了我们扩展或定制此评估框架以供个人使用的控制。

希望我的探索可以为任何需要使用此工具的人提供服务。我会保持这篇博文的更新。因此，如果您还需要使用 evals，请密切关注这篇博文。

Blow 是本文的目录。

**Introduction  
Section 1: Specification File  
Section 2: Specification Objects  
Section 3: Evaluation Protocols  
Section 4: Running Evaluation  
Section 5: Result Recording  
(Optional) Section 6: evals.registry.Registry Module  
Conclusion**


了解了这些部分后，**您可以从头开始编写 Python 代码来创建自己的评估。** 为了给您一个大致的理解，这里是运行示例的代码。**要运行代码，您可以在 [GitHub 上克隆代码并](https://github.com/xinzhel/llm_eval)按照 README.md 中的说明进行操作。**

``` Python
import logging  
import evals  
import evals.api  
import evals.base  
import evals.record  
from evals.eval import Eval  
from evals.registry import Registry  
from types import SimpleNamespace  
import openai  
evals.eval.set_max_samples(8)

# define the arguments  
args = {  
    "completion_fn": "gpt-3.5-turbo",  
    "eval": "match_mmlu_machine_learning",  
    "cache": True,  
    "seed": 20220722  
    }  
args = SimpleNamespace(**args)

# evaluation specification  
registry = Registry()  
eval_spec = registry.get_eval(args.eval)

# eval object  
eval_class = registry.get_class(eval_spec)

openai.api_key = "YOUR_API_KEY"  
completion_fn_instance = registry.make_completion_fn(args.completion_fn)   
eval: Eval = eval_class(  
    completion_fns=[completion_fn_instance],  
    samples_jsonl=eval_spec.args["samples_jsonl"],  
    name=eval_spec.key, # match_mmlu_machine_learning.test.v1,  
    seed=args.seed  
    )
    
# recorder  
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
recorder_path = f"evallogs/{run_spec.run_id}_{args.completion_fn}_{args.eval}.jsonl"  
recorder = evals.record.LocalRecorder(recorder_path, run_spec)

# run the evaluation  
result = eval.run(recorder)  
recorder.record_final_report(result)
```


# Section 1: Specification File
现在，我们来回答一个问题：如何为特定的评估任务定义参数，例如评估数据、评估指标( evaluation data, evaluation metrics)？

```
1 match_mmlu_machine_learning:  
2    id: match_mmlu_machine_learning.test.v1  
3    metrics:  
4    - accuracy  
5 match_mmlu_machine_learning.test.v1:  
6    args:  
7      few_shot_jsonl:
       evals/registry/data/mmlu/machine_learning/few_shot.jsonl  
8      num_few_shot: 4  
9      samples_jsonl: 
       evals/registry/data/mmlu/machine_learning/samples.jsonl 
10   class: evals.elsuite.basic.match:Match
```

- Evaluation Task（第 1 行）：名为`match_mmlu_machine_learning`的评估任务。这应该对应于上述 bash 命令中的`$eval_name` 。
- Evaluation ID（第 2 行）：`id: match_mmlu_machine_learning.test.v1`。它定义了评估任务的更具体的版本或变体。 
- **Metrics（第 3、4 行）**：`metrics`：`accuracy`。在任务下方，有一个键，其中列出了用于评估此任务的指标。在这种情况下，唯一指定的度量是accuracy 。这表明任务的执行将根据准确性来衡量。
- **Evaluation parameters（第 5 行）**：这个键提供有关评估任务的此版本/变体的更具体详细信息。键包含用于评估的参数：  
    * （第 7 行）：可能包含少量样本的 JSONL 文件的路径。这些是模型在评估之前看到的示例，可帮助模型理解任务。  
    * （第 8 行）：指定要使用的少镜头样本的数量。在本例中，将使用 4 个示例。  
    * （第 9 行）：JSONL 文件的路径，该文件可能包含将评估模型的实际样本或数据。
- **The class reference（第 10 行）**：类引用的值将分为两部分。  
    1）the module name () 和 2)the class name。它表明评估将由位于模块中的类处理。此类可能包含有关如何**处理响应或完成**以及如何**计算最终准确性指标**的逻辑。它检查模型输出是否与正确答案匹配（match）。

在hood下，将生成一个completion，并为每个提示选择模型，检查 completion是否与真实答案匹配，然后记录结果”。

# Section 2: Specification Objects

本节将介绍如何使用 YAML 文件来构造`evals`中的 Specification object，该对象将用于`evals.elsuite`中定义的评估工作流。

现在，我们来演示如何使用Specification File。`Registry`类用于 
1） 检索Specification File的信息
2） 根据这些信息构造 Specification object。

简单来说，你可以将上述文件(Specification File)保存到`evals/registry/evals/`中，并调用以下方法来获取 Specification object。

``` Python
Registry().get_eval_set(name) -> evals.base.EvalSetSpec  
Registry().get_eval(name) -> Evals.base.EvalSpec
```

有关详细信息，您可以参考 **Section6: evals.registry.Registry Module** 模块。

在我们的示例中，我们可以调用以下代码行：

``` Python
registry = Registry()  
eval_spec = registry.get_eval(name = "match_mmlu_machine_learning")  
print(eval_spec)  

# EvalSpec(cls='evals.elsuite.basic.match:Match',  
# args={'few_shot_jsonl': 'evals/registry/data/mmlu/  
# machine_learning/few_shot.jsonl',  
# 'num_few_shot': 4,  
# 'samples_jsonl': 'evals/  
# registry/data/mmlu/machine_learning/samples.jsonl'},  
# key='match_mmlu_machine_learning.test.v1',  
# group='mmlu')
```

# Section 3: Evaluation Protocols

评估协议定义了如何处理响应或完成（responses or completions），以及如何计算最终的准确性指标。`evals.Eval` 定义此类协议的接口。

获得规范对象 (`EvalSpec`) 后，可以调用方法`Registry().get_class`来获取继承自`evals.Eval`的具体类。

``` Python
Registry().get_class(spec: EvalSpec) -> evals.Eval
```

在我们的示例中，与评估变量`match_mmlu_machine_learning.test.v1`关联的类`Match`来自模块`evals.elsuite.basic.match`，如文件`mmlu.yaml`中的最后一行所定义。因此，它将输出一个对象`evals.elsuite.basic.match.Match`，如下所示。

`functools.partial`将保持类和`EvalSpec`类相同，并在对象中定义了部分`EvalSpec`类中定义的参数。

``` Python
eval_class = registry.get_class(eval_spec)  
print(eval_class)  
# functools.partial(<class 'evals.elsuite.basic.match.Match'>,  
# few_shot_jsonl='evals/registry/data/mmlu/machine_learning/few_shot.jsonl', num_few_shot=4, samples_jsonl='/Users/xinzheli/git_repo/evals/examples/../evals/registry/data/mmlu/machine_learning/samples.jsonl')
```

然后，可以使用这个类来实例化具有指定完成函数（completion functions）的对象。关于该方法的更多细节，可以参考 **Section6： evals.registry.Registry Module** 了解详情。
``` Python
eval: Eval = eval_class(  
	completion_fns=[completion_fn_instance],
	samples_jsonl=eval_spec.args["samples_jsonl"],  
	name=eval_spec.key # match_mmlu_machine_learning.test.v1,  
)
```

# Section 4: Running Evaluation

让我们了解`evals.Eval`是如何运行评估实验的。每个`evals.Eval`类都需要实现 `eval_sample`和`run`方法。您只需调用`evals.Eval.run`以启动该过程即可。

那么，我们先来看看该方法的实现。

``` Python
class Match(evals.Eval):  
   ...  
   def run(self, recorder):  
      samples = self.get_samples()  
      self.eval_all_samples(recorder, samples)  
      events = recorder.get_events("match")  
      return {  
          "accuracy": evals.metrics.get_accuracy(events),  
          "boostrap_std": evals.metrics.get_bootstrap_accuracy_std(events), 
      }
```

它有三个步骤：

- 通过`get_samples`加载数据
- 调用`eval_all_samples`：它将为每个样本调用`eval_sample`。
- 汇总记录的结果。

现在，让我们看一下该方法（`eval_sample`）的实现。

``` Python
class Match(evals.Eval):   
   ...  
   def eval_sample(self, sample: Any, *_):  
    
      prompt = sample["input"]  
      
      # add few-shot demonstrations to prompt(See source code for details)  
      ...
      
      # get model completion  
      result = self.completion_fn(  
         prompt=prompt,  
         temperature=0.0,  
      )  
      sampled = result.get_completions()[0]  
      
      # calculate metrics  
      return evals.record_and_check_match(  
         prompt=prompt,  
         sampled=sampled,  
         expected=sample["ideal"],  
      )

```


它也有三个步骤：

- 构造提示
- 查询模型以进行完成（completion）
- 计算和记录指标（例如，一个布尔值，用于指示完成completion是否与预期响应匹配）

在正在运行的示例中，我调用以下代码行。在下一节中，我将解释 recorder的使用。


``` Python
result = eval.run(recorder)
```


# Section 5: Result Recording

`openai/evals`框架中的recorder是一个实用程序，用于记录、存储和管理评估结果。它提供了一种结构化的方式来保存评估详细信息、结果和其他相关信息。为了演示，由于我将结果保存到本地文件中，下面将使用`LocalRecorder`。

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

# (Optional) Section 6: evals.registry.Registry Module

`registry`类起到`factory`类的作用，为三种主要类型的组件生成类和对象：completion functions, evaluations, evaluation sets（完成函数、评估、评估集）。

- `Rigistry()._registry_paths`：它提供包含所有类型配置的目录的路径，例如 completion functions , evaluation and evaluation sets（完成函数、评估和评估集）。默认路径为`evals/registry`，用于保存这三种配置的目录是`evals/registry/completion_fns/`，`evals/registry/evals/`，`evals/registry/eval_sets/`。
- `Rigistry()._completion_fns`, `Rigistry()._eval_sets`, `Rigistry()._evals`: 作为内部属性工作，以检索配置文件中的所有信息。假设 `evals/registry/evals/`只包含“mmlu.yaml”文件。`Rigistry()._evals`将输出一个字典，如下所示。
``` JSON
{  
  'match_mmlu_machine_learning': {  
    'id': 'match_mmlu_machine_learning.test.v1',  
    'metrics': [  
      'accuracy'  
    ],  
    'key': 'match_mmlu_machine_learning',  
    'group': 'mmlu'  
  },  
  'match_mmlu_machine_learning.test.v1': {  
    'args': {  
      'few_shot_jsonl': 'evals/registry/data/mmlu/machine_learning/few_shot.jsonl',  
      'num_few_shot': 4,  
      'samples_jsonl': '/Users/xinzheli/git_repo/evals/examples/../evals/registry/data/mmlu/machine_learning/samples.jsonl'  
    },  
    'key': 'match_mmlu_machine_learning.test.v1',  
    'group': 'mmlu',  
    'cls': 'evals.elsuite.basic.match:Match'  
  }  
}
```

- `Registry().get_completion_fn(name)`, `Registry().get_eval_set(name)` and `Registry().get_eval(name)`: 但是，上述内部属性旨在供这些方法使用，以便为用户提供高级对象，例如 `evals.base.CompletionFnSpec` , `evals.base.EvalSetSpec` and `evals.base.EvalSpec` .
- `Registry().get_class(spec: EvalSpec)`：此方法旨在检索与给定评估规范 （`EvalSpec`） 关联的类。请注意，它只返回类，即用于创建对象（实例instances）的蓝图。
- `Registry().make_completion_fn`：创建 CompletionFn

# Conclusion
OpenAI 的“evals”框架提供了一种全面且结构化的方法来评估大型语言模型 （LLM）。本文旨在让用户利用此框架的模块化设计，根据特定需求定制评估。希望随着人工智能领域的发展，我们都可以帮助确保稳健和准确的模型评估。

# Reference
[https://github.com/openai/evals](https://github.com/openai/evals)  
[https://github.com/xinzhel/llm_eval](https://github.com/xinzhel/llm_eval)