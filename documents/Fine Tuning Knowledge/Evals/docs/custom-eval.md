# How to add a custom eval

**Important: Please note that we are currently not accepting Evals with custom code!** While we ask you to not submit such evals at the moment, you can still submit modelgraded evals with custom modelgraded YAML files.
**重要:请注意，我们目前不接受自定义代码的eval !** 虽然我们要求您现在不要提交这样的评估，但您仍然可以提交带有自定义模型分级的YAML文件的模型分级评估。

This tutorial will walk you through a simple example of writing and adding a custom eval. The example eval will test the model's ability to do basic arithmetic. We will assume that you have followed the setup instructions in the [README](../README.md) and gone through the other docs for how to run and build evals.
本教程将带您完成一个编写和添加自定义eval的简单示例。示例eval将测试模型执行基本算术的能力。我们假设您已经遵循了[README](../README.md)中的设置说明，并通过其他文档了解了如何运行和构建eval。

When writing your own evals, the primary files of interest are:
- `evals/api.py`, which provides common interfaces and utilities used by eval creators to sample from models and process the results,
- `evals/record.py`, which defines the recorder classes which log eval results in different ways, such as to a local JSON file or to a remote Snowflake database, and
- `evals/metrics.py`, which defines various common metrics of interest.
在编写自己的eval时，主要文件是:
- `eval /api.py`，它提供eval创建者使用的通用接口和实用程序，用于从模型中采样并处理结果;
- `eval /record.py`，定义以不同方式记录eval结果的记录器类，例如到本地JSON文件或到远程Snowflake数据库，以及
- `eval /metrics.py`，其中定义了各种常见的感兴趣的指标。


These files provide a suite of tools for writing new evals. Once you have gone through this tutorial, you can see a more realistic example of these tools in action with the [machine translation](../evals/elsuite/translate.py) [eval example](../examples/lafand-mt.ipynb), which also implements custom eval logic in lieu of using an existing template.
这些文件提供了一套用于编写新evals的工具。完成本教程后，您可以看到这些工具的一个更实际的示例:[machine translation](../evals/elsuite/translate.py) [eval example](../examples/lafand-mt.ipynb)，它也实现了自定义的eval逻辑，而不是使用现有的模板。

## Create your datasets

The first step is to create the datasets for your eval. Here, we will create toy train and test sets of just two examples each. The test examples are what we will evaluate the model on, and we'll include the train examples as few-shot examples in the prompt to the model.
第一步是为您的eval创建数据集。在这里，我们将创建toy 训练集和测试集，每个只有两个示例。我们将在测试示例上评估模型，并且我们将在模型提示中包括训练示例作为 few-shot 示例。

We will use the new chat format described [here](https://platform.openai.com/docs/guides/chat/introduction). By default, we encourage all evals to be written using chat formatting if you want to evaluate our new models. Under the hood, we [convert](../evals/prompt/base.py) chat formatted data into raw strings for older non chat models.
我们将使用此处描述的新聊天格式(https://platform.openai.com/docs/guides/chat/introduction)。默认情况下，如果您想评估我们的新模型，我们鼓励使用聊天格式编写所有的评估。在底层，我们[转换](../eval /prompt/base.py)聊天格式的数据为旧的非聊天模型的原始字符串。

To create the toy datasets, in your terminal, type:
```bash
echo -e '{"problem": "2+2=", "answer": "4"}\n{"problem": "4*4=", "answer": "16"}' > /tmp/train.jsonl
echo -e '{"problem": "48+2=", "answer": "50"}\n{"problem": "5*20=", "answer": "100"}' > /tmp/test.jsonl
```

## Create an eval

The next step is to write a Python class that represents the actual evaluation. This class uses your datasets to create prompts, which are passed to the model to generate completions. Evaluation classes generally will inherit from the `evals.Eval` base class (defined in `evals/eval.py`) and will override two methods: `eval_sample` and `run`.
下一步是编写一个表示实际evaluation的Python类。这个类使用您的数据集创建prompts，这些提示被传递给模型以生成completions。评估类通常会继承`eval`。`Eval`基类(在`Eval / Eval .py`中定义)，并将覆盖两个方法:`eval_sample`和`run`。


Let's create a file called `arithmetic.py` under the `evals/elsuite` folder. We'll start by defining the eval class. Its `__init__` method will take in the arguments we need (references to the train and test sets) along with other `kwargs` that will be handled by the base class. We'll also define the `run` method which takes in a `recorder` and returns the final metrics of interest.
让我们在`eval /elsuite`文件夹下创建一个名为`arithtic.py`的文件。我们从定义eval类开始。它的`__init__`方法将接受我们需要的参数(对训练集和测试集的引用)以及将由基类处理的其他`kwargs`。我们还将定义`run`方法，它接受一个“recorder”并返回最终感兴趣的指标。

```python
import random
import textwrap

import evals
import evals.metrics

class Arithmetic(evals.Eval):
    def __init__(self, train_jsonl, test_jsonl, train_samples_per_prompt=2, **kwargs):
        super().__init__(**kwargs)
        self.train_jsonl = train_jsonl
        self.test_jsonl = test_jsonl
        self.train_samples_per_prompt = train_samples_per_prompt

    def run(self, recorder):
        """
        Called by the `oaieval` CLI to run the eval. The `eval_all_samples` method calls `eval_sample`.
        """
        self.train_samples = evals.get_jsonl(self.train_jsonl)
        test_samples = evals.get_jsonl(self.test_jsonl)
        self.eval_all_samples(recorder, test_samples)

        # Record overall metrics
        return {
            "accuracy": evals.metrics.get_accuracy(recorder.get_events("match")),
        }
```

Generally, most `run` methods will follow the same pattern shown here: loading the data, calling `eval_all_samples`, and aggregating the results (in this case, using the `get_accuracy` function in `evals/metrics.py`). `eval_all_samples` takes in both the `recorder` and the `test_samples` and, under the hood, will call the `eval_sample` method on each sample in `test_samples`. So let's write that `eval_sample` method now:
一般来说，大多数`run`方法将遵循这里所示的相同模式:加载数据，调用`eval_all_samples `，并汇总结果(在本例中，使用`eval /metrics.py`中的`get_accuracy`函数)。 `eval_all_samples`同时接收`recorder`和`test_samples`，并且在底层，将对`test_samples`中的每个样本调用`eval_sample`方法。现在让我们写这个`eval_sample`方法:

```python
    def eval_sample(self, test_sample, rng: random.Random):
        """
        Called by the `eval_all_samples` method to evaluate a single sample.

        ARGS
        ====
        `test_sample`: a line from the JSONL test file
        `rng`: should be used for any randomness that is needed during evaluation

        This method does the following:
        1. Generate a prompt that contains the task statement, a few examples, and the test question.
        2. Generate a completion from the model.
        3. Check if the generated answer is correct.
        """
        stuffing = rng.sample(self.train_samples, self.train_samples_per_prompt)

        prompt = [
            {"role": "system", "content": "Solve the following math problems"},
        ]

        for i, sample in enumerate(stuffing + [test_sample]):
            if i < len(stuffing):
                prompt += [
                    {"role": "system", "content": sample["problem"], "name": "example_user"},
                    {"role": "system", "content": sample["answer"], "name": "example_assistant"},
                ]
            else:
                prompt += [{"role": "user", "content": sample["problem"]}]


        result = self.completion_fn(prompt=prompt, temperature=0.0, max_tokens=1)
        sampled = result.get_completions()[0]

        evals.record_and_check_match(prompt=prompt, sampled=sampled, expected=test_sample["answer"])
```
You'll notice that `eval_sample` doesn't take the `recorder` as an argument. This is because `eval_all_samples` sets it to be the default recorder before calling `eval_sample`, and the recording utilities defined in `evals/record.py` use the default recorder. In this example, the `eval_sample` method passes off a lot of the heavy lifting to the `evals.record_and_check_match` utility function, which is defined in `evals/api.py`. This utility function queries the model, defined by `self.model_spec`, with the given `prompt` and checks to see if the result matches the `expected` answer (or one of them, if given a list). It then records these matches (or non matches) using the default recorder.
你会注意到`eval_sample`没有把`recorder`作为参数。这是因为`eval_all_samples`在调用` eval_sample`之前将其设置为默认记录器，并且`eval/record.py`中定义的记录工具程序使用默认记录器。在本例中，`eval_sample`方法将大量繁重的工作交给了`eval.Record_and_check_match`工具函数，在`eval /api.py`中定义。这个工具函数查询由`self.Model_spec`定义的模型，使用给定的`prompt`，并检查结果是否与`excepted`答案匹配(或其中之一，如果给出一个列表)。然后使用默认记录器记录这些匹配(或不匹配)。

`eval_sample` methods may vary greatly based on your use case. If you are building custom evals, it is a good idea to be familiar with the functions available to you in `evals/record.py`, `evals/metrics.py`, and especially `evals/api.py`.
`eval_sample`方法可能会根据你的用例有很大的不同。如果您正在构建自定义评估，那么熟悉`eval /record.py`， `eval /metrics.py`，特别是`eval /api.py`中可用的函数是一个好主意。
## Register your eval

The next step is to register your eval in the registry so that it can be run using the `oaieval` CLI.
下一步是在注册表中注册您的eval，以便可以使用`oaieval` CLI运行它。

Let's create a file called `arithmetic.yaml` under the `evals/registry/evals` folder and add an entry for our eval as follows:
让我们创建一个名为`arithmetic.yaml`的文件，在`evals/registry/evals`文件夹下添加，并为我们的eval添加如下条目:

```yaml
# Define a base eval
arithmetic:
  # id specifies the eval that this eval is an alias for
  # in this case, arithmetic is an alias for arithmetic.dev.match-v1
  # When you run `oaieval davinci arithmetic`, you are actually running `oaieval davinci arithmetic.dev.match-v1`
  id: arithmetic.dev.match-v1
  # The metrics that this eval records
  # The first metric will be considered to be the primary metric
  metrics: [accuracy]
  description: Evaluate arithmetic ability
# Define the eval
arithmetic.dev.match-v1:
  # Specify the class name as a dotted path to the module and class
  class: evals.elsuite.arithmetic:Arithmetic
  # Specify the arguments as a dictionary of JSONL URIs
  # These arguments can be anything that you want to pass to the class constructor
  args:
    train_jsonl: /tmp/train.jsonl
    test_jsonl: /tmp/test.jsonl
```

The `args` field should match the arguments that your eval class `__init__` method expects.
`args`字段应该匹配eval类的`__init__`方法所期望的参数。
## Run your eval

The final step is to run your eval and view the results.
最后一步是运行eval并查看结果。

```sh
pip install .  # you can omit this if you used `pip install -e .` to install
oaieval gpt-3.5-turbo arithmetic
```

If you run with the `gpt-3.5-turbo` model, you should see an output similar to this (we have cleaned up the output here slightly for readability):
如果你使用`gpt-3.5-turbo`模型运行，你应该看到类似于这样的输出(为了可读性，我们在这里稍微清理了一下输出):
```
% oaieval gpt-3.5-turbo arithmetic
... [registry.py:147] Loading registry from .../evals/registry/evals
... [registry.py:147] Loading registry from .../.evals/evals
... [oaieval.py:139] Run started: <run_id>
... [eval.py:32] Evaluating 2 samples
... [eval.py:138] Running in threaded mode with 1 threads!
100%|██████████████████████████████████████████| 2/2 [00:00<00:00,  3.35it/s]
... [record.py:320] Final report: {'accuracy': 1.0}. Logged to /tmp/evallogs/<run_id>_gpt-3.5-turbo_arithmetic.jsonl
... [oaieval.py:170] Final report:
... [oaieval.py:172] accuracy: 1.0
... [record.py:309] Logged 6 rows of events to /tmp/evallogs/<run_id>_gpt-3.5-turbo_arithmetic.jsonl: insert_time=2.038ms
```
