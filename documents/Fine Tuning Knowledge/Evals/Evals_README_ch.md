# OpenAI Evals

**Evals为评估大型语言模型(llm)或使用llm构建的系统提供了一个框架。** 我们提供了一个现有的评估注册表(an existing registry of evals)来测试OpenAI模型的不同维度，**并能够为您关心的用例编写自己的自定义评估。** 您还可以使用您的数据来构建私有eval，这些eval代表工作流中常见的llm模式，而无需公开任何数据。

**如果你在利用LLMs搭建，创建高质量的评估是你能做的最有影响力的事情之一。如果没有评估，理解不同的模型版本如何影响您的用例是非常困难和耗时的。** 用OpenAI总裁Greg Brockman的话来说(https://twitter.com/gdb/status/1733553161884127435):

<img width="596" alt="https://x.com/gdb/status/1733553161884127435?s=20" src="https://github.com/openai/evals/assets/35577566/ce7840ff-43a8-4d88-bb2f-6b207410333b">

## Setup
如何使用PyCharm配置pyproject.toml？： https://cloud.tencent.com/developer/ask/sof/107342827

要运行eval，你需要设置并指定你的[OpenAI API密钥](https://platform.openai.com/account/api-keys)。获取API密钥后，使用[' OPENAI_API_KEY '环境变量](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key)指定它。请注意运行evals时与使用API相关的[成本](https://openai.com/pricing)。**你也可以使用[权重和偏差](https://wandb.ai/wandb_fc/openai-evals/reports/OpenAI-Evals-Demo-Using-W-B-Prompts-to-Run-Evaluations--Vmlldzo0MTI4ODA3)运行和创建评估。**

**最低要求版本:Python 3.9**

### Downloading evals

我们的evals registry是使用[Git-LFS](https://git-lfs.com/)存储的。一旦你下载并安装了LFS，你就可以用以下方法获取eval(从你本地的eval repo拷贝中):
```sh
cd evals
git lfs fetch --all
git lfs pull
```
这将填充`eval/registry/data`下的所有pointer files。

您可能只想为一个特定的eval获取数据。您可以通过以下方式实现:

```sh
git lfs fetch --include=evals/registry/data/${your eval}
git lfs pull
```

### Making evals

如果你要创建eval，我们建议直接从GitHub克隆这个repo，并使用以下命令安装需求:

```sh
pip install -e .
```

使用`-e`，您对eval所做的更改将立即反映出来，而无需重新安装。

可选的，你可以安装预提交的格式化程序:

```sh
pip install -e .[formatters]
```

然后运行`pre-commit install`将pre-commit安装到你的git hooks中。pre-commit 现在将在每次提交时运行。

如果你想手动运行存储库上的所有pre-commit hooks，请运行`pre-commit run——all-files`。要运行单个hook，请使用`pre-commit run <hook_id>`。

## Running evals

**如果你不想贡献新的eval，只是想在本地运行它们，你可以通过pip安装eval包:**
```sh
pip install evals
```

**你可以在文件[[run-evals]]中找到运行现有eval的完整指令，在文件[[eval-templates]]中找到我们现有的eval模板（eval templates）。** 对于更高级的用例，如提示链（prompt chain）或工具使用代理（tool-using agents），您可以使用我们的[[completion-fns]]。

如果您有一个或希望设置一个，我们为您提供了将您的eval结果记录到Snowflake数据库的选项。对于这个选项，您将必须进一步指定`SNOWFLAKE_ACCOUNT`， `SNOWFLAKE_DATABASE`，` SNOWFLAKE_USERNAME`和`SNOWFLAKE_PASSWORD`这些环境变量。

## Writing evals

我们建议从以下几点开始:

* 遍历构建eval的过程:[[build-eval]]
* 探索一个实现自定义eval逻辑的例子:[[custom-eval]]
* 编写自己的补全函数:[[completion-fns]]
* 回顾我们编写evals的入门指南:[开始使用OpenAI评估](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals)

请注意，我们目前不接受自定义代码的eval !虽然我们要求您现在不要提交这样的evals，但是您仍然可以提交带有自定义模型分级的YAML文件的模型分级评估。

如果你认为你有一个有趣的评估，请打开一个拉请求与您的贡献。OpenAI员工在考虑对即将推出的模型进行改进时，会积极审查这些评估。

## FAQ

**你有关于如何从头到尾构建eval的例子吗?**
* 是的!这些都在`examples` 文件夹中。我们建议您通读[[build-eval]]，以便更深入地理解这些示例中发生的事情。


你有以多种不同方式实现eval的例子吗?
* 是的!特别是，请参阅`evals/registry/evals/coqa.yaml`。我们已经为各种eval模板实现了[CoQA](https://stanfordnlp.github.io/coqa/)数据集的小子集，以帮助说明差异。


当我运行eval时，它有时会挂起(在最终报告之后)。这是怎么呢？

* 这是一个已知的问题，但你应该能够安全地中断它，eval应该立即结束。


**这里有很多代码，我只想快速启动一个eval。帮助吗?或者,我是一个世界级的prompt 工程师。我选择不编码。我怎样才能贡献我的智慧?**

* 如果您遵循现有的[[eval-templates]]来构建基本的或模型分级的eval，您根本不需要编写任何评估代码!**只需提供JSON格式的数据，并在YAML中指定eval参数。** [[build-eval]]指导您完成这些步骤，您可以使用`examples`文件夹中的Jupyter笔记本来补充这些说明的相关内容，以帮助您快速入门。但是请记住，一个好的评估不可避免地需要仔细的思考和严格的实验!

## Disclaimer
通过参与评估，您同意将您的评估逻辑和数据置于与此存储库相同的MIT许可下。您必须有足够的权利上传eval中使用的任何数据。OpenAI保留在将来对我们的产品进行服务改进时使用这些数据的权利。对OpenAI评估的贡献将遵守我们通常的使用政策:https://platform.openai.com/docs/usage-policies。