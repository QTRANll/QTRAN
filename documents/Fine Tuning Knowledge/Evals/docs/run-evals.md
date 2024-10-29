# How to run evals

We provide two command line interfaces (CLIs): `oaieval` for running a single eval and `oaievalset` for running a set of evals.

我们提供了两个命令行接口(CLIs): `oaieval`用于运行单个eval， `oaievalset`用于运行一组eval。
## Running an eval

When using the `oaieval` command, you will need to provide the completion function you wish to evaluate as well as the eval to run. E.g.,

当使用`oaieval`命令时，您需要提供希望求值的完成函数(completion function)以及要运行的eval。例如,
```sh
oaieval gpt-3.5-turbo test-match
```

The valid eval names are specified in the YAML files under `evals/registry/evals` and their corresponding implementations can be found in `evals/elsuite`.
有效的eval名称在`evals/registry/evals`下的YAML文件中指定，其相应的实现可以在` evals/elsuite`中找到。

In this example, `gpt-3.5-turbo` is an OpenAI model that we dynamically instantiate as a completion function using `OpenAIChatCompletionFn(model=gpt-3.5-turbo)`. Any implementation of the `CompletionFn` protocol can be run against `oaieval`. By default, we support calling `oaieval` with any model available on the OpenAI API or with CompletionFunctions available in [`evals/registry/completion_fns`](../evals/registry/completion_fns/). We are always interested in adding more completion functions and we encourage you to implement your own to reflect specific use cases.
在这个例子中，`gpt-3.5-turbo`是一个OpenAI模型，由我们使用`OpenAIChatCompletionFn(model=gpt-3.5-turbo)`动态实例化为补全函数（completion function）。`CompletionFn`协议的任何实现(implementation)都可以针对`oaieval`运行。默认情况下，我们支持使用OpenAI API上可用的任何模型调用`oaieval`或使用[ evals/registry/completion_fns](../evals/registry/completion_fns/)中可用的CompletionFunctions。我们总是对添加更多的补全函数感兴趣，我们鼓励您实现自己的函数来反映特定的用例。

More details on `CompletionFn` found here: [`completion-fns.md`](completion-fns.md)
关于“CompletionFn”的更多细节请参见:[`completion-fns.md`](completion-fns.md)

These CLIs can accept various flags to modify their default behavior. For example:
- If you wish to log to a Snowflake database (which you have already set up as described in the [README](../README.md)), add `--no-local-run`.
- By default, logging locally or to Snowflake will write to `tmp/evallogs`, and you can change this by setting a different `--record_path`.
这些CLIs可以接受各种flags来修改它们的默认行为。例如:
* 如果你想log到一个Snowflake数据库(你已经根据[README](../README.md)中描述的那样进行设置)，添加`--no-local-run`。
* 默认情况下，log到本地或Snowflake将写入`tmp/evallogs`，你可以通过设置不同的`--record_path`来改变这一点。

You can run `oaieval --help` to see a full list of CLI options.
您可以运行`oaieval——help`来查看CLI选项的完整列表。
## Running an eval set

```sh
oaievalset gpt-3.5-turbo test
```

Similarly, `oaievalset` also expects a model name and an eval set name, for which the valid options are specified in the YAML files under `evals/registry/eval_sets`.
类似地，`oaievalset`也需要一个模型名称和一个eval集名称，其有效选项在` evals/registry/eval_sets`下的YAML文件中指定。

By default we run with 10 threads, and each thread times out and restarts after 40 seconds. You can configure this, e.g.,
默认情况下，我们运行10个线程，每个线程超时并在40秒后重新启动。您可以对此进行配置，例如:

```sh
EVALS_THREADS=42 EVALS_THREAD_TIMEOUT=600 oaievalset gpt-3.5-turbo test
```

Running with more threads will make the eval faster, though keep in mind the costs and your [rate limits](https://platform.openai.com/docs/guides/rate-limits/overview). Running with a higher thread timeout may be necessary if you expect each sample to take a long time, e.g., the data contain long prompts that elicit long responses from the model.
使用更多的线程运行将使eval更快，但请记住成本和您的[速率限制](https://platform.openai.com/docs/guides/rate-limits/overview)。如果您希望每个sample花费较长的时间，例如，数据包含较长的提示，从而从模型中引出较长的响应，则可能需要使用较高的线程超时运行。

If you have to stop your run or your run crashes, we've got you covered! `oaievalset` records the evals that finished in `/tmp/oaievalset/{model}.{eval_set}.progress.txt`. You can simply rerun the command to pick up where you left off. If you want to run the eval set starting from the beginning, delete this progress file.
如果你不得不停止运行或者你的运行崩溃了，我们会帮你的!`oaievalset`在 `/tmp/oaievalset/{model}.{eval_set}.progress.txt`中记录了完成的eval。您可以简单地重新运行该命令，从停止的地方开始。如果要从头开始运行eval集，请删除此进度文件。

Unfortunately, you can't resume a single eval from the middle. You'll have to restart from the beginning, so try to keep your individual evals quick to run.
不幸的是，您不能从中间恢复单个eval。你必须从头开始，所以尽量保持你的个人评估快速运行。
## Logging

By default, `oaieval` [records events](/evals/record.py) into local JSONL logs which can be inspected using a text editor or analyzed programmatically. 3rd-party tools such as [naimenz/logviz](https://github.com/naimenz/logviz) may be helpful to visualize the logs, though we don't provide support or guarantees for their use.
默认情况下，`oaieval`[records events](/evals/record.py)到本地JSONL日志中，可以使用文本编辑器检查或以编程方式分析。第三方工具，如[naimenz/logviz](https://github.com/naimenz/logviz)可能有助于可视化日志，但我们不提供对其使用的支持或保证。