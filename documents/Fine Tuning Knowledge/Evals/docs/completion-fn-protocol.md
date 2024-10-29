### The Completion Function Protocol

Here are the interfaces needed to implement the completion function protocol. Any implementation of this interface can be used inside `oaieval`.
下面是实现完成函数协议所需的接口。这个接口的任何实现都可以在`oaieval`中使用。

Reference implementations:
- [OpenAICompletionFn](../evals/completion_fns/openai.py)
- [LangChainLLMCompletionFn](../evals/completion_fns/langchain_llm.py)

#### CompletionFn
Completion functions should implement the `CompletionFn` interface:
补全函数应该实现`CompletionFn`接口:
```python
class CompletionFn(Protocol):
    def __call__(
        self,
        prompt: Union[str, list[dict[str, str]]],
        **kwargs,
    ) -> CompletionResult:
```

We take a `prompt` representing a single sample from an eval. These prompts can be represented as either a text string or a list of messages in [OpenAI Chat format](https://platform.openai.com/docs/guides/chat/introduction). To work with the existing evals, Completion Function implementations would need to handle both types of inputs, but we provide helper functionality to convert Chat formatted messages into a text string if that is the preferred input for your program:
**我们从eval中取一个代表单个样本的`prompt`。这些提示可以表示为文本字符串或[OpenAI聊天格式](https://platform.openai.com/docs/guides/chat/introduction)的消息列表。为了处理现有的evals, Completion Function实现需要处理这两种类型的输入，但是我们提供了辅助功能来将Chat格式的消息转换为文本字符串，如果这是您的程序的首选输入:**
```python
from evals.prompt.base import CompletionPrompt

# chat_prompt: list[dict[str, str]] -> text_prompt: str
text_prompt = CompletionPrompt(chat_prompt).to_formatted_prompt()
```

#### CompletionResult
The completion function should return an object implementing the `CompletionResult` interface:
completion函数应该返回一个实现CompletionResult接口的对象:
```python
class CompletionResult(ABC):
    @abstractmethod
    def get_completions(self) -> list[str]:
        pass
```
The `get_completions` method returns a list of string completions. Each element should be considered a unique completion (in most cases this will be a list of length 1).
`get_completions` 方法的作用是:返回一个字符串补全。每个元素应该被视为一个唯一的补全(在大多数情况下，这将是一个长度为1的列表)。
#### Using your CompletionFn
This is all that's needed to implement a Completion function that works with our existing Evals, allowing you to more easily evaluate your end-to-end logic on tasks.
这就是实现与现有eval一起工作的Completion函数所需要的全部内容，允许您更轻松地评估任务上的端到端逻辑。

See [completion-fns.md](completion-fns.md) to see how to register and use your completion function with `oaieval`.
参见[completion-fns.md](completion-fns.md)了解如何注册和使用带有`oaieval`的补全函数。