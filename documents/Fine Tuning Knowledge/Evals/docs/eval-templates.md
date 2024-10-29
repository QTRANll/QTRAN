# Existing templates for evals

In using Evals, we have discovered several "templates" that accommodate many different benchmarks. We have implemented these templates in `evals/elsuite` in order to simplify the development of new evals. We believe that, with these templates, many evals will not require any coding to implement! Instead, you'll pick one of the existing templates and simply specify the dataset and parameters.

在使用eval的过程中，我们发现了几个“templates”，可以适应许多不同的benchmarks。我们在`eval /elsuite`中实现了这些模板，以简化新eval的开发。我们相信，有了这些模板，许多eval将不需要任何编码来实现!相反，您将选择一个现有模板并简单地指定数据集和参数。
## Basic eval templates

In cases where the desired model response has very little variation, such as answering multiple choice questions or simple questions with a straightforward answer, we have found the following templates to be useful.
**在期望的模型响应变化很小的情况下，例如回答多项选择题或简单的问题，并给出一个直接的答案，我们发现以下模板很有用。**


For a model completion `a` and a reference list of correct answers `B`, the following evals implement:
对于模型completion`a`和正确答案的参考列表`B`，执行以下eval:
- [`basic/match.py:Match`](../evals/elsuite/basic/match.py): `any([a.startswith(b) for b in B])`
```
检查字符串 a 是否以 B 列表中的任意一个元素作为前缀。如果 a 以 B 中的任意一个元素开头,则返回 True,否则返回 False。
```
- [`basic/includes.py:Includes`](../evals/elsuite/basic/includes.py): `any([(b in a) for b in B])`
```
检查字符串 a 是否包含 B 列表中的任意一个元素。如果 a 包含 B 中的任意一个元素,则返回 True,否则返回 False。
```
- [`basic/fuzzy_match.py:FuzzyMatch`](../evals/elsuite/basic/fuzzy_match.py): `any([(a in b or b in a) for b in B])`
```
检查字符串 a 是否与 B 列表中的任意一个元素存在包含关系,即 a 是否是 B 中任意一个元素的子字符串,或者 B 中任意一个元素是否是 a 的子字符串。如果存在这样的关系,则返回 True,否则返回 False。
```


To compare a model completion `a` in *JSON format* to a reference list of correct answers `B` also formatted in JSON, use the following eval:
要将JSON格式的模型completion`a`与同样JSON格式的正确答案`B`的参考列表进行比较，请使用以下eval:
- [`basic/json_match.py:JsonMatch`](../evals/elsuite/basic/json_match.py) yields a match if `a` is identical to at least one answer from `B`. Two JSON objects are identical if they have the same set of keys and the values for each key are identical. Key order is not significant, and whitespace outside values is ignored. Invalid JSON never matches.
- [basic/json_match.py:JsonMatch ](../evals/elsuite/basic/json_match.py) 如果`a`至少与`B`的一个答案相同，则产生匹配。如果两个JSON对象具有相同的键集并且每个键的值相同，则它们是相同的。键顺序不重要，值外的空白将被忽略。无效的JSON永远不匹配。


Which eval template you use will depend on your use case. It is always recommended that you inspect the completions from your model, as this will help you determine how and whether to tweak your prompt (or your reference answers) and pick your eval template. Academic benchmarks oftentimes fit the mold of these basic evals, and we have implemented several end-to-end examples of academic evals as Jupyter notebooks in the `examples` folder.
**使用哪个eval模板取决于您的用例。始终建议您检查模型中的completions，因为这将帮助您确定如何以及是否调整提示(或参考答案)并选择eval模板。学术benchmarks通常符合这些基本评估的模式，我们已经实现了几个端到端的学术评估示例，作为Jupyter笔记本中的`examples`文件夹。**

Sometimes, [custom eval logic](custom-eval.md) will better suit your needs. One example of this is the [machine translation](../evals/elsuite/translate.py) eval [example](../examples/lafand-mt.ipynb), in which there is a unique and clearly defined metric that we wish to use in our eval. You should use your best judgment when deciding between custom eval logic, using a basic eval template, or using model-graded evals as described next.
有时，[custom eval logic](custom-eval.md) 会更好地满足您的需求。这方面的一个例子是[machine translation](../evals/elsuite/ translation .py) eval [example](../examples/lafand-mt.ipynb)，其中有一个我们希望在eval中使用的唯一且明确定义的度量。在决定是使用自定义eval逻辑、使用基本的eval模板，还是使用模型分级的eval(如下所述)时，您应该做出最好的判断。




---
下面的内容暂未使用到
## The model-graded eval template

In cases where the desired model response can contain significant variation, such as answering an open-ended question, we have found that using the model to grade itself is a viable strategy for automated evaluation. In general, the evaluation model and the model being evaluated don't have to be the same, though we will assume that they are here for ease of explanation.
在期望的模型响应可能包含显著变化的情况下，例如回答一个开放式问题，我们发现使用模型对自身进行评分是自动评估的可行策略。一般来说，评估模型和被评估的模型不必相同，尽管我们假设它们在这里是为了便于解释。

[`modelgraded/classify.py:ModelBasedClassify`](../evals/elsuite/modelgraded/classify.py) implements the main logic behind our model-graded eval template. In short, we get the model's completion to the original prompt, wrap it in an evaluation prompt, and get the model's completion to the evaluation prompt, which we parse into our metrics of interest. Crucially, the evaluation prompt should prime the model to answer in such a way that is easily parsable, e.g., in multiple choice format or with a simple yes/no. We describe some example model-graded evals below, but first we specify the parameters for this eval template.
[modelgraded/classify.py: modelbasedclassifier](../evals/elsuite/modelgraded/classify.py) 实现了模型分级eval模板背后的主要逻辑。简而言之，我们获得原始提示的模型完成，将其包装在评估提示中，并获得评估提示的模型完成，我们将其解析为我们感兴趣的指标。至关重要的是，评估提示应该让模型以一种容易解析的方式回答问题，例如，以多项选择的形式或简单的是/否。下面我们将描述一些模型分级的示例eval，但首先我们为这个eval模板指定参数。
### Parameters for model-graded evals

Refer to the [`classify.py:ModelBasedClassify`](../evals/elsuite/modelgraded/classify.py) class to see how these parameters are used in the code.
参考[classifier .py: modelbasedclassifier](../evals/elsuite/modelgraded/ classifier .py)类来查看这些参数在代码中是如何使用的。

- `prompt`: The evaluation prompt which should take in the model's completion to the original prompt, potentially along with some other information, and steer the model to provide an evaluation that is easily parsable. Portions denoted by curly braces (i.e., `{key}`) are filled in either from the data `input_outputs` or the additional `args` (see below).
- `prompt`:评估提示，它应该将模型的completion与原始提示结合起来，可能还会附带一些其他信息，并引导模型提供易于解析的评估。用花括号表示的部分(即`{key}`)可以从数据`input_outputs`或额外的`args`(见下文)填充。
- `input_outputs`: A mapping specifying which inputs to use to generate which completions. For many evals, there will only be a single input-completion pair, though there can be more, e.g., when comparing two completions against each other.
- `input_outputs`:一个映射，指定使用哪些输入来生成哪些补全。对于许多evals，只有一个输入-完成对，尽管可能有更多，例如，在相互比较两个completion时。
- `choice_strings`: The choices that we expect the model completion to contain given the evaluation prompt. For example, `"ABCDE"` or `["Yes", "No", "Unsure"]`. Any other choices returned by the model are parsed into `"__invalid__"`.
-  `choice_strings`:给定评估提示，我们期望模型completion包含的选项。例如,`"ABCDE"` or `["Yes", "No", "Unsure"]`。模型返回的任何其他选项都被解析为`"__invalid__"`。
- `choice_scores` (optional): A mapping of each choice to its score, which is logged as a metric. For example, if a response of `"Yes"` (resp. `"No"`) indicates that the model's original completion was good (resp. bad), we may assign this choice a score of 1 (resp. 0).
- `choice_scores`(可选):每个选择到它的分数的映射，它被记录为一个度量。例如，如果一个`"Yes"`的响应表示模型的原始完成情况良好(如:不好的情况下，我们可以给这个选择打1)。
- `eval_type` (optional): How we expect the model to format its response to the evaluation prompt. Currently the supported options are:
  - `"cot_classify"` ("chain-of-thought then classify", i.e., reason then answer) expects that the parsable portion of the response (i.e., the portion containing the choice) will be at the end of the completion. We recommend this as the default as it typically provides the most accurate model-graded evaluations.
  - `"classify_cot"` (answer then reason) expects that the model response will contain the choice first.
  - `"classify"` expects that the model response will only contain the choice.

- `eval_type`(可选):我们希望模型如何格式化其对评估提示的响应。目前支持的选项有:
 - `cot_classifier`(“chain-of-thought then classified”，即推理然后回答)期望响应的可解析部分(即包含选择的部分)将在完成的末尾。我们建议将其作为默认值，因为它通常提供最准确的模型分级评估。
 - `classify_cot`(答案然后原因)期望模型响应将首先包含选择。
 - `"classify"期望模型响应只包含选择。

  There are two ways to specify `eval_type`. The recommended way is in the `evals/registry/evals` YAML file. If done this way, an instruction will automatically be appended to `prompt` to steer the model towards the expected format (see `ANSWER_PROMPTS` in [the code](../evals/elsuite/modelgraded/classify.py)). Alternatively, you may specify `eval_type` in the `evals/registry/modelgraded` YAML, but you will need to include an appropriate instruction directly in the `prompt`.
- `output_template` (optional): If specified, determines how the model's output (or outputs, if `n > 1`) will be formatted within the completion.
有两种方法可以指定`eval_type`。推荐的方法是在`evals/registry/evals`YAML文件中。如果这样做，一条指令将自动附加到`prompt`以引导模型朝着预期的格式(参见[代码](../evals/elsuite/modelgraded/classify.py)中的' ANSWER_PROMPTS ')。或者，你可以在`evals/registry/modelgraded`YAML中指定`eval_type`，但你需要在`prompt`中直接包含一个适当的指令。
- `output_template`(可选):如果指定，确定如何在补全中格式化模型的输出(或输出，如果` n > 1`)。
### Example model-graded evals

To instantiate model-graded evals, create a YAML file in `evals/registry/modelgraded` which specifies values for the arguments described above. We have provided a few examples, which illustrate the process for creating a model-graded eval, but which we also believe are general enough to be useful out of the box for many evals.
要实例化模型分级的eval，请在`evals/registry/modelgraded`中创建一个YAML文件，该文件为上面描述的参数指定值。我们已经提供了一些示例，这些示例说明了创建模型分级评估的过程，但是我们也认为这些示例足够通用，对于许多评估都是开箱即用的。

[`fact.yaml`](../evals/registry/modelgraded/fact.yaml): a factual consistency eval which, given a completion `a` and reference answer `b`, returns:
- `"A"` if `a` $\subseteq$ `b`, i.e., the submitted answer is a subset of the expert answer and is fully consistent with it.
- `"B"` if `a` $\supseteq$ `b`, i.e., the submitted answer is a superset of the expert answer and is fully consistent with it.
- `"C"` if `a` $=$ `b`, i.e., the submitted answer contains all the same details as the expert answer.
- `"D"` if `a` $\neq$ `b`, i.e., there is a disagreement between the submitted answer and the expert answer.
- `"E"` if `a` $\approx$ `b`, i.e., the answers differ, but these differences don't matter from the perspective of factuality.
[fact.yaml](../evals/registry/modelgraded/fact.yaml):一个 事实一致性评估，给定completion`a`和参考答案`b`，返回:
- `"A"` if `a` $\subseteq$ `b`，即提交的答案是专家答案的一个子集，并且与专家答案完全一致。
- `"B"` if `a` $\supseteq$ `b`，即提交的答案是专家答案的超集，并且与专家答案完全一致。
- `"C"` if `a` $=$ `b`，即提交的答案包含与专家答案相同的所有细节。
- `"D"` if `a` $\neq$ `b`，即提交的答案与专家的答案不一致。
- `"E"` if `a` $\approx$ `b`，即答案不同，但从事实的角度来看，这些差异并不重要。

[`closedqa.yaml`](../evals/registry/modelgraded/closedqa.yaml): a question answering eval, which, given a prompt containing a question and the necessary information to answer the question, checks whether the model's answer is:
- relevant, i.e., extracted from the information provided in the prompt,
- concise, i.e., did not contain unnecessary details or information, and
- correct, i.e., uses the extracted information to come to the right conclusion.

[closedqa.yaml](../evals/registry/modelgraded/closedqa.yaml):一个回答问题的eval，给出一个包含问题和回答问题所需信息的提示，检查模型的答案是否为:
- 相关，即从提示提供的信息中提取;
- 简洁，即不包含不必要的细节或信息
- 正确，即使用提取的信息来得出正确的结论。


Note that this eval is implemented more generally as a "criteria-checking" eval, which specifies the evaluation prompt as checking a given criterion and feeding in the above desiderata one by one. We believe that many other evals can be implemented by specifying a "rubric" detailing the criteria of interest and following the same prompt and yes/no choices.
请注意，这个eval更一般地实现为“标准检查”eval，它将评估提示指定为检查给定的标准并逐一输入上述所需数据。我们认为，许多其他评估可以通过指定一个“标题”来实现，详细说明感兴趣的标准，并遵循相同的提示和是/否选项。

[`battle.yaml`](../evals/registry/modelgraded/battle.yaml): a head-to-head eval which compares two model completions for two potentially different prompts. `choice_scores` is used here to log how often the first completion is judged to be better than the second.
[' battle.yaml '](. /evals/registry/modelgraded/battle.yaml):一个头对头的eval，比较两个模型完成的两个可能不同的提示。' choice_scores '在这里用于记录第一次完成被认为比第二次完成更好的频率。

We include additional examples which test more specific model capabilities (such as humor) and are thus less generalizable to other evals. However, these examples still serve to illustrate different ways to write evaluation prompts and set up model-graded evals. See [this section](build-eval.md#for-model-graded-evals-a-step-by-step-workflow) for more detailed steps on building model-graded evals.

我们包含了额外的例子来测试更具体的模型功能(如幽默)，因此不太适用于其他评估。然而，这些示例仍然用于说明编写评估提示和设置模型分级评估的不同方法。请参阅[本节](build-eval.md#for-model-graded-eval -a-step-by-step-workflow)了解构建模型分级评估的更详细步骤。
