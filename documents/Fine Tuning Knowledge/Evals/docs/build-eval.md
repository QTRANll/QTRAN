# Building an eval

**Important: Please note that we are currently not accepting Evals with custom code!** While we ask you to not submit such evals at the moment, you can still submit modelgraded evals with custom modelgraded YAML files.
**重要:请注意，我们目前不接受自定义代码的eval !** 虽然我们要求您现在不要提交这样的评估，但您仍然可以提交带有自定义模型分级的YAML文件的模型分级评估。

This document walks through the end-to-end process for building an eval, which is a dataset and a choice of eval class. The `examples` folder contains Jupyter notebooks that follow the steps below to build several academic evals, thus helping to illustrate the overall process.
本文介绍了构建eval的端到端过程，它是一个数据集和eval类的选择。`examples`文件夹包含Jupyter笔记本，它们按照以下步骤构建几个学术评估，从而帮助说明整个过程。

The steps in this process are building your dataset, registering a new eval with your dataset, and running your eval. Crucially, we assume that you are using an [existing eval template]   ([[eval-templates]]) out of the box (if that's not the case, see [this example of building a custom eval] ([[custom-eval]])). If you are interested in contributing your eval publicly, we also include some criteria at the bottom for what we think makes an interesting eval.
这个过程的步骤是构建数据集，向数据集注册一个新的eval，然后运行eval。至关重要的是，我们假设您正在使用现成的[现有的eval模板][[eval-templates]](如果不是这种情况，请参阅[构建自定义eval的示例]  ([[custom-eval]]))。如果您有兴趣公开贡献您的评估，我们还在底部提供了一些我们认为有趣的评估的标准。

We are looking for evals in the following categories:
我们正在寻找以下类别的评估:
- Over-refusals
- Safety
- System message steerability
- In-the-wild hallucinations
- Math / logical / physical reasoning
- Real-world use case (please describe in your PR how this capability would be used in a product)
- Other foundational capability

If you have an eval that falls outside this category but still is a diverse example, please contribute it!
如果你有一个不属于这个类别的eval，但仍然是一个多样化的例子，请贡献它!

## Formatting your data

Once you have an eval in mind that you wish to implement, you will need to convert your samples into the right JSON lines (JSONL) format. A JSONL file is just a JSON file with a unique JSON object per line.
一旦您心中有了希望实现的eval，就需要将示例转换为正确的JSON行(JSONL)格式。JSONL文件就是每行有一个唯一JSON对象的JSON文件。

You can use the `openai` CLI (available with [OpenAI-Python](https://github.com/openai/openai-python)) to transform data from some common file types into JSONL:
你可以使用`openai`命令行(可与[openai-python](https://github.com/openai/openai-python))将数据从一些常见的文件类型转换为JSONL:
``` 
openai tools fine_tunes.prepare_data -f data[.csv, .json, .txt, .xlsx or .tsv]
```

We include some examples of JSONL eval files in [[Evals_Data_Format_README]]
我们在[[Evals_Data_Format_README]]中包含了一些JSONL eval文件的例子。

Each JSON object will represent one data point in your eval. The keys you need in the JSON object depend on the eval template. All templates expect an `"input"` key, which is the prompt, ideally specified in [chat format](https://platform.openai.com/docs/guides/chat/introduction) (though strings are also supported). We recommend chat format even if you are evaluating non-chat models. If you are evaluating both chat and non-chat models, we handle the conversion between chat-formatted prompts and raw string prompts (see the conversion logic [here](../evals/prompt/base.py)).
**每个JSON对象表示eval中的一个数据点。JSON对象中需要的键取决于eval模板。所有模板都需要一个`"input"`键，这是提示，理想情况下以[chat格式](https://platform.openai.com/docs/guides/chat/introduction)指定(尽管也支持字符串)。** 即使您正在评估非聊天模型，我们也建议使用聊天格式。如果您正在评估聊天和非聊天模型，我们将处理聊天格式提示和原始字符串提示之间的转换(参见转换逻辑[这里](../evals/prompt/base.py))。

For the basic evals `Match`, `Includes`, and `FuzzyMatch`, the other required key is `"ideal"`, which is a string (or a list of strings) specifying the correct reference answer(s). For model-graded evals, the required keys vary based on the eval but is determined by the `{key}`s in the evaluation `prompt` that are not covered by the (optional) `args`.
**对于基本evals `"Match"`、`"Includes"`和`"FuzzyMatch"`，另一个必需的键是`"ideal"`，它是一个字符串(或字符串列表)，指定正确的引用答案。** 对于模型分级的评估，所需的键根据评估而变化，但由评估`提示`中的`"{key}"`决定，这些`"{key}"`不包含在(可选)`"参数"`。

We have implemented small subsets of the [CoQA](https://stanfordnlp.github.io/coqa/) dataset for various eval templates to illustrate how the data should be formatted. See [`coqa/match.jsonl`](../evals/registry/data/coqa/match.jsonl) for an example of data that is suitable for the `Match` basic eval template and [`coqa/samples.jsonl`](../evals/registry/data/coqa/samples.jsonl) for data that is suitable for `fact` and `closedqa` model-graded evals. Note that even though these two model-graded evals expect different keys, we can include the superset of keys in our data in order to support both evals.
我们已经为各种eval模板实现了[CoQA](https://stanfordnlp.github.io/coqa/)数据集的小子集，以说明数据应该如何格式化。请参阅[coqa/ Match.jsonl](../evals/registry/data/coqa/ Match .jsonl)获取适合`Match`基本eval模板的数据示例，以及[' coqa/samples.jsonl '](../evals/registry/data/coqa/samples.jsonl)获取适合' fact '和' closedqa '模型分级eval的数据。请注意，即使这两个模型分级的值期望不同的键，我们也可以在数据中包含键的超集，以便支持这两个值。


If the dataset file is on your local machine, put the `jsonl` file in `evals/registry/data/<eval_name>/samples.jsonl`. If it is in Cloud Object Storage, we support path-style URLs for the major clouds (for your personal use only, we will not accept PRs with cloud URLs).
**如果数据集文件在本地机器上，将`jsonl`文件放在`eval /registry/data/<eval_name>/samples.jsonl`中。** 如果是在云对象存储中，我们支持主要云的路径式url(仅供您个人使用，我们不接受带有云url的pr)。
## Registering the eval

Register the eval by adding a file to `evals/registry/evals/<eval_name>.yaml` using the elsuite registry format. For example, for a `Match` eval, it would be:
通过在`evals/registry/evals/<eval_name>.yaml`中添加一个文件来注册eval。使用elsuite注册表格式。例如，对于`Match` eval，它将是:
```
<eval_name>:
  id: <eval_name>.dev.v0
  description: <description>
  metrics: [accuracy]

<eval_name>.dev.v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: <eval_name>/samples.jsonl
```

Upon running the eval, the data will be searched for in `evals/registry/data`. For example, if `test_match/samples.jsonl` is the provided filepath, the data is expected to be in `evals/registry/data/test_match/samples.jsonl`.
运行eval后，数据将在`eval /registry/data`中搜索。例如，如果`test_match/samples. jsonl`是提供的文件路径，数据应该在`eval/registry/data/test_match/samples.jsonl`中。

The naming convention for evals is in the form `<eval_name>.<split>.<version>`.
- `<eval_name>` is the eval name, used to group evals whose scores are comparable.
- `<split>` is the data split, used to further group evals that are under the same `<base_eval>`. E.g., "val", "test", or "dev" for testing.
- `<version>` is the version of the eval, which can be any descriptive text you'd like to use (though it's best if it does not contain `.`).
eval的命名约定为`<eval_name>.<split>.<version>`。
* `<eval_name>`是eval的名称，用于对评分可比较的eval进行分组。
- `<split>`是数据分割，用于进一步分组相同`<base_eval>`下的值。例如，“val”、“test”或“dev”表示测试。
- `<version>`是eval的版本，它可以是你想使用的任何描述性文本(但最好不包含`.`)。

In general, running the same eval name against the same model should always give similar results so that others can reproduce it. Therefore, when you change your eval, you should bump the version.
一般来说，对相同的模型运行相同的eval名称应该总是得到类似的结果，以便其他人可以复制它。因此，当您更改eval时，应该更改版本。

## Running the eval

You can now run your eval on your data from the CLI with your choice of model or completion function:
现在你可以在CLI中使用你选择的模型或完成函数对你的数据运行eval:
```
oaieval gpt-3.5-turbo <eval_name>
```
Congratulations, you have built your eval! Keep iterating on it until you are confident in the results.
祝贺您，您已经构建了您的eval!不断迭代，直到你对结果有信心。

## For model-graded evals: a step-by-step workflow

We expect that the existing model-graded evals such as `fact`, `closedqa`, and `battle` will fit many use cases. However, other use cases may benefit from more customization, e.g., a different evaluation prompt. For these, there will be a bit more work involved, but generally still no coding required!

1. If you can't use an existing model-graded eval, create a new YAML or create a new entry to an existing YAML in `evals/registry/modelgraded` to specify the [parameters](eval-templates.md#parameters-for-model-graded-evals) of your eval. See [`humor.yaml`](../evals/registry/modelgraded/humor.yaml) for an example.
    - Note that, even if you are creating a new YAML, you may find it easiest to copy an existing YAML as a starting point. For example, model-graded evals which check a model completion against a rubric can copy `closedqa.yaml` and just edit the `args`.
2. Next, you will create your dataset and register your eval, as described above. See [`joke_fruits_labeled.jsonl`](../evals/registry/data/test_metaeval/joke_fruits_labeled.jsonl) and [`joke-fruits`](../evals/registry/evals/test-modelgraded.yaml), for example.
    - Note that it is recommended to specify `eval_type` at this step, when you register your eval, rather than step 1.
3. Run your eval, e.g., `oaieval gpt-3.5-turbo joke-fruits`.
4. (Recommended) Add a meta-eval for the model-graded eval! Each model-graded eval comes with a few knobs to tune, mainly `prompt` but also `eval_type`. In order to make sure the eval is of high quality, we recommend each model-graded eval contribution come with "choice labels", which are basically human-provided labels for which evaluation choice the model should have made. As an example (pretending that these jokes are actually funny), see the `"choice"` keys in [`joke_fruits_labeled.jsonl`](../evals/registry/data/test_metaeval/joke_fruits_labeled.jsonl), which are not used by the `joke-fruits` eval but are used by the [`joke-fruits-meta`](../evals/registry/evals/test-modelgraded.yaml) meta-eval right below it . After running the meta-eval, e.g., `oaieval gpt-3.5-turbo joke-fruits-meta`, the report will output `metascore/` accuracies, which should be close to "1.0" for a good model-graded eval.

## Criteria for contributing an eval

Important: if you are contributing code, make sure to run `pip install pre-commit; pre-commit install` before committing and pushing to ensure that `black`, `isort`, and `autoflake` are run.
重要:如果您正在贡献代码，请确保运行`pip install pre-commit`;在提交和推送之前预提交安装，以确保运行“black”、“isort”和“autoflake”。

We are interested in curating a diverse and interesting set of evals on which to improve our models going forward. Here are some criteria for what we consider a good eval:
- [ ] The eval should be thematically consistent. We'd like to see a number of prompts all revolving around the same use case, subject domain, failure mode, etc.
- [ ] The eval should be challenging. If GPT-4 or GPT-3.5-Turbo do well on all of the prompts, this is not as interesting. Of course, the eval should also be possible given the models' limitations and constraints. Oftentimes, a good rule of thumb is whether a human (potentially a subject expert) could do well on the prompts.
- [ ] The eval should be directionally clear. The data should include good signal around what is the right behavior. This means, for example, high-quality reference answers or an exhaustive rubric for evaluating answers.
- [ ] The eval should be carefully crafted. Before you submit, you should think through whether you have engineered your prompts for good performance, whether you are using the best eval template, whether you have spot checked your results to ensure accuracy, etc.

我们有兴趣策划一套多样化和有趣的评估，以改进我们的模型向前发展。以下是我们认为好的eval的一些标准:
- [ ] eval应该在主题上保持一致。我们希望看到许多提示都围绕着相同的用例、主题域、故障模式等。
- [ ] 评估应该具有挑战性。如果GPT-4或GPT-3.5-Turbo在所有提示中都表现良好，那么这就不那么有趣了。当然，考虑到模型的限制和约束，评估也应该是可能的。通常，一个好的经验法则是一个人(可能是一个学科专家)是否能很好地完成提示。
- [ ] eval应该有明确的方向。数据应该包含关于什么是正确行为的良好信号。这意味着，例如，高质量的参考答案或一个详尽的评估答案的准则。
- [ ] eval应该精心编写。在提交之前，您应该仔细考虑是否设计了具有良好性能的提示，是否使用了最佳的eval模板，是否对结果进行了抽查以确保准确性等。

Once you are ready to contribute your eval publicly, submit a PR and the OpenAI team will be happy to look it over. Make sure to fill out all parts of the template that is prepopulated into the PR message. Note that submitting a PR does not guarantee that OpenAI will eventually merge it. We will run our own checks and use our best judgment when considering which evals to follow up with.
一旦你准备好公开贡献你的评估，提交一份PR, OpenAI团队会很乐意查看它。请确保填写了预先填充到PR消息中的模板的所有部分。请注意，提交PR并不能保证OpenAI最终会合并它。我们将进行自己的检查，并在考虑跟进哪些评估时使用我们最好的判断。