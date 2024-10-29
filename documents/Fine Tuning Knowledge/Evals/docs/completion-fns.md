# Completion Functions

## What are completion functions
In [run-evals.md](run-evals.md), we learned how to make calls to `oaieval` to run an eval against a completion function. Completion Functions are generalizations of model completions, where a "completion" is some text output that would be our answer to the prompt. For example, if "Who played the girl elf in the hobbit?" is our prompt, the correct completion is "Evangeline Lilly". While we can just test a model directly to see if it generates "Evangeline Lilly", we can imagine doing numerous other operations under the hood to improve our ability to answer this question, like giving the model access to a browser to look up the answer before responding. Making it easy to implement this kind of under-the-hood operators before responding is the motivation behind building Completion Functions.

在[run-eval .md](run-eval .md)中，我们学习了如何调用`oaieval`来运行特定completion functions的eval。**补全函数（Completion Functions）是模型补全的泛化，其中的“补全”是一些文本输出，将是我们对提示的回答。例如，如果“谁在《霍比特人》中扮演精灵女孩?”是我们的提示，那么正确的补全应该是“Evangeline Lilly”。虽然我们可以直接测试一个模型，看看它是否生成“Evangeline Lilly”，但我们可以想象在hood执行许多其他操作来提高我们回答这个问题的能力，比如让模型访问浏览器，以便在响应之前查找答案。在响应之前实现这种under-the-hood operators是构建Completion Functions背后的动机。**


## How to implement completion functions
A completion function needs to implement some interfaces that make it usable within Evals. At its core, it is just standardizing inputs to be a text string or [Chat conversation](https://platform.openai.com/docs/guides/chat), and the output to be a list of text strings. Implementing this interface will allow you to run your Completion Function against any eval in Evals.
补全函数需要实现一些接口，使其在eval中可用。核心要点是，它只是将输入标准化为文本字符串或[Chat conversation](https://platform.openai.com/docs/guides/chat)，输出标准化为文本字符串列表。实现这个接口将允许你对eval中的任何eval运行你的Completion Function。

The exact interfaces needed are described in detail in [completion-fn-protocol.md](completion-fn-protocol.md)
所需的确切接口在[completion-fn-protocol.md](completion-fn-protocol.md)中有详细描述。

We include some example implementations inside `evals/completion_fns`. For example, the [`LangChainLLMCompletionFn`](../evals/completion_fns/langchain_llm.py) implements a way to generate completions from [LangChain LLMs](https://python.langchain.com/en/latest/modules/models/llms/getting_started.html). We can then use these completion functions with `oaieval`:
我们在`eval/completion_fns`中包含了一些示例实现。例如, [ LangChainLLMCompletionFn](../evals/completion_fns/langchain_llm.py)实现了一种从[LangChain llm](https://python.langchain.com/en/latest/modules/models/llms/getting_started.html)生成completions的方法。然后我们可以通过`oaieval`来使用这些补全函数
```
oaieval langchain/llm/flan-t5-xl test-match
```

## Registering Completion Functions
Once you have written a completion function, we need to make the class visible to the `oaieval` CLI. Similar to how we register our evals, we also register Completion Functions inside `evals/registry/completion_fns` as `yaml` files. Here is the registration for our langchain LLM completion function:
一旦你写了一个补全函数，我们需要让这个类对`oaieval`CLI可见。与我们注册eval的方式类似，我们也将`eval/registry/completion_fns`中的Completion Functions注册为`yaml`文件。下面是我们的langchain LLM补全函数的注册:

```yaml
langchain/llm/flan-t5-xl:
  class: evals.completion_fns.langchain_llm:LangChainLLMCompletionFn
  args:
    llm: HuggingFaceHub
    llm_kwargs:
      repo_id: google/flan-t5-xl
```

Here is how it breaks down
`langchain/llm/flan-t5-xl`: This is the top level key that will be used to access this completion function with `oaieval`.
`class`: This is the path to your implementation of the completion function protocol. This class needs to be importable within your python environment.
`args`:  These are arguments that are passed to your completion function when it is instantiated.

它是如何分解的:
`langchain/llm/flan-t5-xl`:这是用于访问`oaieval`补全函数的顶级键。
`class`:这是你实现补全函数协议的路径。该类需要在python环境中可导入。
`args`:这些是在实例化完成函数时传递给它的参数。


### Developing Completion Functions outside of Evals(可以忽略)
It is possible to register CompletionFunctions without directly modifying the registry or code inside `Evals` by using the `--registry_path` argument. As an example, let's say I want to use `MyCompletionFn` located inside `~/my_project/`:
可以注册CompletionFunctions，而不直接修改`eval`中的注册表或代码，这需要使用`--registry_path`参数。举个例子，假设我想使用位于`~/my_project/`中的`MyCompletionFn ：

```
my_project
├── my_completion_fn.py
└── completion_fns
    └── my_completion_fn.yaml
```

If `my_project` is importable within the python environment (accessible via PYTHONPATH), we can structure `my_completion_fn.yaml` as:
如果`my_project`在python环境中是可导入的(通过PYTHONPATH访问)，我们可以构造`my_completion_fn.yaml`:
```
my_completion_fn:
  class: my_project.my_completion_fn:MyCompletionFn
```
Then, we can make calls to `oaieval` using:
然后，我们可以使用以下命令调用`oaieval`:
```
oaieval my_completion_fn test-match --registry_path ~/my_project
```
