# 链接
[How To Best Leverage OpenAI’s Evals Framework | by Aparna Dhinakaran | Towards Data Science](https://towardsdatascience.com/how-to-best-leverage-openais-evals-framework-c38bcef0ec47)


根据最近的一项[调查](https://arize.com/blog/survey-massive-retooling-around-large-language-models-underway/)，近一半 （43%） 的数据科学和工程团队正在计划在明年进行大型语言模型 （LLM） 的生产部署。LLMs的时代已经到来;然而，评估这些模型通常具有挑战性，研究人员需要开发可靠的方法来比较不同模型的性能。

几个月前，OpenAI 开源了他们的框架，用于根据一系列基准评估 LLM。该框架在 OpenAI 内部使用，以确保其模型的新版本性能良好。**OpenAI 的 Eval Framework 是一种工具，旨在帮助研究人员和从业者评估他们的 LLM，并将它们与其他最先进的模型进行比较。**

# How Does the Eval Framework Work?

现在，在这一点上，你可能会想，“哇，这似乎是一个评估LLM的非常有用的工具，但是什么是评估，我该如何使用它？让我们深入了解具体细节！

**“eval”是指用于衡量语言模型在特定领域的性能的特定评估任务，例如问答或情感分析。这些评估通常是标准化的基准测试（benchmarks），允许比较不同的语言模型。** Eval 框架提供了一个标准化的接口，用于运行这些评估并收集结果。

**从本质上讲，eval 是在 YAML 文件中定义的数据集和 eval 类。** 下面显示了一个 eval 示例（摘自[用于评估的 Github 仓库](https://github.com/openai/evals)）：

```
test-match:
  id: test-match.s1.simple-v0
  description: Example eval that checks sampled text matches the expected output.
  disclaimer: This is an example disclaimer.
  metrics: [accuracy]
test-match.s1.simple-v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: test_match/samples.jsonl
```

让我们来分析一下上述的含义：

- test-match：这是评估程序的名称（别名）
- id：这是 test-match 作为别名的 eval 的全名（全名）
- description：评估的描述。
- metrics：评估的指标。
- class：指定 eval 的module/class的路径。
- args：要传递给类构造函数的任何内容。
- samples_jsonl：指向样本所在的位置，在本例中位于 test_match/samples.jsonl 中


为了让您了解samples的外观，以下是 **_test_match/samples.jsonl_** 文件中的示例：

```
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "Once upon a "}], "ideal": "time"}
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "The first US president was "}], "ideal": "George Washington"}
{"input": [{"role": "system", "content": "Complete the phrase as concisely as possible."}, {"role": "user", "content": "OpenAI was founded in 20"}], "ideal": "15"}
```

**在 JSONL 文件（只是一个 JSON 文件，每行都有一个唯一的 JSON 对象）中，我们可以看到 eval 的样本。** 每个 JSON 对象表示模型要完成的任务，并在评估中计为 1 个数据点。**有关 JSONL 文件的更多示例，您可以转到 Eval Github 仓库中的 [registry/data/README.md](https://github.com/openai/evals/blob/main/evals/registry/data/README.md)。[[Evals_Data_Format_README]]**

在下面的部分中，我们将介绍如何运行 test-match eval。



# How can I run an eval?

我们可以使用一个简单的命令运行上述评估：
```
oaieval gpt-3.5-turbo test-match
```

**在这里，我们使用 oaieval CLI 来运行此评估。我们指定了完成函数( completion function)的名称 （gpt-3.5-turbo） 和 eval 的名称 （test-match）。就这么简单！** 我们将在下面的部分中更深入地介绍完成函数( completion function)以及如何构建评估。**运行该命令后，您将看到打印到控制台的最终准确性报告，以及包含完整报告的临时文件的文件路径。** 这只是表明使用此框架快速评估 LLM 是多么容易。**接下来，让我们学习如何构建自己的评估，而不是使用注册表中已有的评估。**

# How can I build my own eval?
在本节中，我们将介绍如何从已有模板构建 eval，并解释完成函数( completion function)以及如何构建自己的 eval 函数。

# Building Evals

## Building Samples
在这里，我们将介绍如何使用[[eval-templates]]  (https://github.com/openai/evals/blob/main/docs/eval-templates.md)构建自定义评估以加快工作速度。（如果您想构建一个完全自定义的评估，这里是 Eval Github 存储库中的[[custom-eval]]  (https://github.com/openai/evals/blob/main/docs/custom-eval.md)。

构建 eval 的第一步是构建样本（samples）。**示例需要包含某些字段，具体取决于您选择使用的模板（template）。每个示例都需要包含一个代表prompt的“input”字段，建议以[聊天格式](https://platform.openai.com/docs/guides/chat/introduction)指定。其他字段取决于您选择用于评估的模板。** **例如，让我们使用 _Match_ 模板。在这种情况下，我需要以聊天格式指定字段“input”和“ideal”。这可能如下所示**：
```
{
"input": [
{"role": "system", "content": "Complete the phrase as concisely as possible."}, 
{"role": "user", "content": "ABC AI is a company specializing in ML "}
],
"ideal": "observability"
}
```

这是告诉系统”尽可能简洁地完成这句话“，我们提供的短语是“ABC AI 是一家专门从事 ML 的公司”，预期的答案是“可观察性”。

如果您的样本（sample）的文件格式与 JSONL 不同，OpenAI 会提供一个 CLI 来将这些样本转换为 JSONL 文件。您可以使用 [Evals 存储库](https://github.com/openai/evals/blob/main/docs/build-eval.md#formatting-your-data)提供的以下代码来实现此目的：
```
openai tools fine_tunes.prepare_data -f data[.csv, .json, .txt, .xlsx or .tsv]
```

太好了，我们的样本在一个 JSONL 文件中！下一步是注册我们的评估。

## Registering your eval

要注册 eval，我们需要在 _evals/registry/evals/<eval_name>.yaml_ 中添加一个文件。**此文件的格式与上述示例 _test-match_ eval  [[#How Does the Eval Framework Work?]]的格式相同。** 它需要包含 eval 
的name, id, optional description, metrics, class, and args（用于指定样本文件的位置）。一旦我们注册了 eval，我们就可以继续运行它，就像我们运行 _test-match_ eval 一样。这就是设置您自己的评估所需的全部内容！
```
test-match:
  id: test-match.s1.simple-v0
  description: Example eval that checks sampled text matches the expected output.
  disclaimer: This is an example disclaimer.
  metrics: [accuracy]
test-match.s1.simple-v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: test_match/samples.jsonl
```

# Building Completion Functions

## What is a completion function?

在[[#How can I run an eval?]]部分中，我们简要提到了您需要指定一个完成函数(completion function)来运行 oaieval 命令。首先，让我们从什么是completion开始。**completion是模型对prompt的输出。例如，如果我们给出模型的prompt是“告诉我加利福尼亚州的首府是什么”，我们预计的completion为“萨克拉门托”。** 但是，某些prompts可能需要访问 Internet 或其他一些操作来帮助模型准确回答问题，这就是completion function发挥作用的地方。通过completion function，您可以定义模型可能需要执行的这些操作。**oaieval 命令中的completion function参数可以是 CompletionFn URL，也可以是 OpenAI API 中的模型名称或注册表中的键。** 有关completion function的更多信息，请参见[此处](https://github.com/openai/evals/blob/main/docs/completion-fns.md)。

## How can I build my own completion function?
在本节中，我们将介绍如何构建自己的completion function。为了使您的completion function与所有 eval 兼容，它需要实现一些接口。这些接口本质上只是标准化了评估的输入和输出。如果您想获取有关这些接口的更多信息，请[在此处查看有关完成函数协议的文档](https://github.com/openai/evals/blob/main/docs/completion-fn-protocol.md)。

**一旦你的completion function被实现，你需要像我们注册eval一样注册它们**。注册completion function后，它就可以被 **oaieval** CLI 使用。下面显示了从 [Evals 存储库](https://github.com/openai/evals/blob/main/evals/registry/completion_fns/cot.yaml)中获取的注册示例：

```
cot/gpt-3.5-turbo:
  class: evals.completion_fns.cot:ChainOfThoughtCompletionFn
  args:
    cot_completion_fn: gpt-3.5-turbo
```
让我们分解一下上面的内容：

**cot/gpt-3.5-turbo**：这是 oaieval 将使用的完成函数的全名

**class**：这是完成函数实现的类路径

**args**：初始化时传递给完成函数的参数

**-> cot_completion_fn**：这是传递给 ChainOfThoughtCompletionFn 类的参数



# Advantages of Using the Eval Framework
评估框架为研究人员和从业人员提供了几个好处。

**标准化的评估指标和基准（**Standardized evaluation metrics and benchmarks**）** ：Eval框架提供了一套标准化的评估指标，研究人员可以使用这些指标来比较其模型的性能。这使研究人员可以在相同的基准上将他们的模型与其他最先进的模型进行比较。

**易于使用**：Eval 框架旨在易于使用。您可以使用现有模板快速构建自己的评估，并且只需几行代码即可启动和运行，如上所示。

**灵活**：评估框架非常灵活，可用于评估各种任务和不同基准的模型。

**开源**：Eval 框架是开源的，这意味着研究人员/从业者可以根据他们的特定需求使用和修改它。此外，任何人都可以向 [openai/evals Github 存储库](https://github.com/openai/evals)做出贡献，这将有助于众包更多可以在整个社区共享的基准测试。

## Conclusion
OpenEvals 是[评估 LLM 的](https://arize.com/blog-course/evals-openai-simplifying-llm-evaluation/)强大工具，为研究人员和从业者提供了一套标准化的评估指标和任务，用于将他们的模型与其他最先进的模型进行比较。鉴于其优点，随着LLM的不断改进，该框架在未来可能会成为评估和比较模型性能的有用工具。祝您评估愉快！