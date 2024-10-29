## 参考链接
Fine-tuning官方教程：[Fine-tuning - OpenAI API](https://platform.openai.com/docs/guides/fine-tuning)
Fine-tuning定价： https://openai.com/api/pricing/
Fine-tuning platform: https://platform.openai.com/finetune
[[AI OpenAI-doc] 微调-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/2410927)

## Important Knowledge
* You can also fine-tune a fine-tuned model which is useful if you acquire additional data and don't want to repeat the previous training steps.
* We expect `gpt-4o-mini` to be the right model for most users in terms of performance, cost, and ease of use.

## Fine-tuning Common Use Cases
Some common use cases where fine-tuning can improve results:
- **Setting the style, tone, format, or other qualitative aspects**
- Improving reliability at producing a desired output
- Correcting failures to follow complex prompts
- **Handling many edge cases in specific ways**
- Performing a new skill or task that’s hard to articulate in a prompt

One high-level way to think about these cases is when it’s easier to "show, not tell".
Another scenario where fine-tuning is effective is in reducing costs and / or latency, by replacing GPT-4 or by utilizing shorter prompts, without sacrificing quality. If you can achieve good results with GPT-4, you can often reach similar quality with a fine-tuned `gpt-4o-mini` model by fine-tuning on the GPT-4 completions, possibly with a shortened instruction prompt.
## Fine-tuning Steps
At a high level, fine-tuning involves the following steps:
1. Prepare and upload training data
2. Train a new fine-tuned model
3. Evaluate results and go back to step 1 if needed
4. Use your fine-tuned model


## [Preparing your dataset](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset)
You should create a diverse set of demonstration conversations that are similar to the conversations you will ask the model to respond to at inference time in production.

**Each example in the dataset should be a conversation in the same format as our [Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create), specifically a list of messages where each message has a role, content, and [optional name](https://platform.openai.com/docs/api-reference/chat/create#chat/create-chat/create-messages-name).** At least some of the training examples should directly target cases where the prompted model is not behaving as desired, and the provided assistant messages in the data should be the ideal responses you want the model to provide.

### Examples
``` JSON
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "Paris, as if everyone doesn't know that already."}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who wrote 'Romeo and Juliet'?"}, {"role": "assistant", "content": "Oh, just some guy named William Shakespeare. Ever heard of him?"}]}
{"messages": [{"role": "system", "content": "Marv is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "How far is the Moon from Earth?"}, {"role": "assistant", "content": "Around 384,400 kilometers. Give or take a few, like that really matters."}]}
```


### Example count recommendations
To fine-tune a model, you are required to provide at least 10 examples. We typically see clear improvements from fine-tuning on 50 to 100 training examples with `gpt-4o-mini` and `gpt-3.5-turbo`, but the right number varies greatly based on the exact use case.

### Train and test splits
After collecting the initial dataset, we recommend splitting it into a training and test portion. When submitting a fine-tuning job with both training and test files, we will provide statistics on both during the course of training. These statistics will be your initial signal of how much the model is improving. Additionally, constructing a test set early on will be useful in making sure you are able to evaluate the model after training, by generating samples on the test set.

### [Token limits](https://platform.openai.com/docs/guides/fine-tuning/token-limits)

### [Estimate costs](https://platform.openai.com/docs/guides/fine-tuning/estimate-costs)

GPT-4o mini is free to fine-tune starting today through September 23, 2024. This means each organization will get 2M tokens per 24 hour period to train the model and any overage will be charged at $3.00/1M tokens.

#### [Check data formatting](https://platform.openai.com/docs/guides/fine-tuning/check-data-formatting)
Once you have compiled a dataset and before you create a fine-tuning job, it is important to check the data formatting. To do this, we created a simple Python script which you can use to find potential errors, review token counts, and estimate the cost of a fine-tuning job.

https://cookbook.openai.com/examples/chat_finetuning_data_prep


### [Upload a training file](https://platform.openai.com/docs/guides/fine-tuning/upload-a-training-file)

``` Python
from openai import OpenAI
client = OpenAI()

client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)
```

After you upload the file, it may take some time to process. While the file is processing, you can still create a fine-tuning job but it will not start until the file processing has completed.



## [Create a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/create-a-fine-tuned-model)

After ensuring you have the right amount and structure for your dataset, and have uploaded the file, the next step is to create a fine-tuning job.

``` Python
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="file-abc123", 
  model="gpt-4o-mini"
)
```

In this example, `model` is the name of the model you want to fine-tune (`gpt-4o-mini`, `gpt-3.5-turbo`, `babbage-002`, `davinci-002`, or an existing fine-tuned model) and **`training_file` is the file ID that was returned when the training file was uploaded to the OpenAI API.** You can customize your fine-tuned model's name using the [suffix parameter](https://platform.openai.com/docs/api-reference/fine-tuning/create#fine-tuning/create-suffix).

To set additional fine-tuning parameters like the `validation_file` or `hyperparameters`, please refer to the [API specification for fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning/create).

After you've started a fine-tuning job, it may take some time to complete. Your job may be queued behind other jobs in our system, and training a model can take minutes or hours depending on the model and dataset size. **After the model training is completed, the user who created the fine-tuning job will receive an email confirmation.**



## [Use a fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/use-a-fine-tuned-model)

When a job has succeeded, you will see the `fine_tuned_model` field populated with the name of the model when you retrieve the job details. You may now specify this model as a parameter to in the [Chat Completions](https://platform.openai.com/docs/api-reference/chat) (for `gpt-3.5-turbo`) or [legacy Completions](https://platform.openai.com/docs/api-reference/completions) API (for `babbage-002` and `davinci-002`), and make requests to it using the [Playground](https://platform.openai.com/playground).

After your job is completed, the model should be available right away for inference use. In some cases, it may take several minutes for your model to become ready to handle requests. If requests to your model time out or the model name cannot be found, it is likely because your model is still being loaded. If this happens, try again in a few minutes.
``` Python
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="ft:gpt-4o-mini:my-org:custom_suffix:id",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)
print(completion.choices[0].message)
```

You can start making requests by passing the model name as shown above and in our [GPT guide](https://platform.openai.com/docs/guides/text-generation/chat-completions-api).


## [Use a checkpointed model](https://platform.openai.com/docs/guides/fine-tuning/use-a-checkpointed-model)

In addition to creating a final fine-tuned model at the end of each fine-tuning job, OpenAI will create one full model checkpoint for you at the end of each training epoch. These checkpoints are themselves full models that can be used within our completions and chat-completions endpoints. Checkpoints are useful as they potentially provide a version of your fine-tuned model from before it experienced overfitting.

To access these checkpoints,

1. Wait until a job succeeds, which you can verify by [querying the status of a job.](https://platform.openai.com/docs/api-reference/fine-tuning/retrieve)
2. [Query the checkpoints endpoint](https://platform.openai.com/docs/api-reference/fine-tuning/list-checkpoints) with your fine-tuning job ID to access a list of model checkpoints for the fine-tuning job.

For each checkpoint object, you will see the `fine_tuned_model_checkpoint` field populated with the name of the model checkpoint. You may now use this model just like you would with the [final fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/use-a-fine-tuned-model).

``` Python
{
    "object": "fine_tuning.job.checkpoint",
    "id": "ftckpt_zc4Q7MP6XxulcVzj4MZdwsAB",
    "created_at": 1519129973,
    "fine_tuned_model_checkpoint": "ft:gpt-3.5-turbo-0125:my-org:custom-suffix:96olL566:ckpt-step-2000",
    "metrics": {
        "full_valid_loss": 0.134,
        "full_valid_mean_token_accuracy": 0.874
    },
    "fine_tuning_job_id": "ftjob-abc123",
    "step_number": 2000
}
```


Each checkpoint will specify its:

- `step_number`: The step at which the checkpoint was created (where each epoch is number of steps in the training set divided by the batch size)
- `metrics`: an object containing the metrics for your fine-tuning job at the step when the checkpoint was created.

Currently, only the checkpoints for the last 3 epochs of the job are saved and available for use. We plan to release more complex and flexible checkpointing strategies in the near future.


## [Analyzing your fine-tuned model](https://platform.openai.com/docs/guides/fine-tuning/analyzing-your-fine-tuned-model)

We provide the following training metrics computed over the course of training:
- training loss
- training token accuracy
- valid loss
- valid token accuracy

Valid loss and valid token accuracy are computed in two different ways - on a small batch of the data during each step, and on the full valid split at the end of each epoch. The full valid loss and full valid token accuracy metrics are the most accurate metric tracking the overall performance of your model. **These statistics are meant to provide a sanity check that training went smoothly (loss should decrease, token accuracy should increase).**  While an active fine-tuning jobs is running, you can view an event object which contains some useful metrics:
``` Python
{
    "object": "fine_tuning.job.event",
    "id": "ftevent-abc-123",
    "created_at": 1693582679,
    "level": "info",
    "message": "Step 300/300: training loss=0.15, validation loss=0.27, full validation loss=0.40",
    "data": {
        "step": 300,
        "train_loss": 0.14991648495197296,
        "valid_loss": 0.26569826706596045,
        "total_steps": 300,
        "full_valid_loss": 0.4032616495084362,
        "train_mean_token_accuracy": 0.9444444179534912,
        "valid_mean_token_accuracy": 0.9565217391304348,
        "full_valid_mean_token_accuracy": 0.9089635854341737
    },
    "type": "metrics"
}
```

After a fine-tuning job has finished, you can also see metrics around how the training process went by [querying a fine-tuning job](https://platform.openai.com/docs/api-reference/fine-tuning/retrieve), extracting a file ID from the `result_files`, and then [retrieving that files content](https://platform.openai.com/docs/api-reference/files/retrieve-contents). Each results CSV file has the following columns: `step`, `train_loss`, `train_accuracy`, `valid_loss`, and `valid_mean_token_accuracy`.

```
step,train_loss,train_accuracy,valid_loss,valid_mean_token_accuracy
1,1.52347,0.0,,
2,0.57719,0.0,,
3,3.63525,0.0,,
4,1.72257,0.0,,
5,1.52379,0.0,,
```
While metrics can he helpful, evaluating samples from the fine-tuned model provides the most relevant sense of model quality. We recommend generating samples from both the base model and the fine-tuned model on a test set, and comparing the samples side by side. The test set should ideally include the full distribution of inputs that you might send to the model in a production use case. If manual evaluation is too time-consuming, consider using our [Evals library](https://github.com/openai/evals) to automate future evaluations.

### [Iterating on data quality](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-data-quality)

If the results from a fine-tuning job are not as good as you expected, consider the following ways to adjust the training dataset:

- Collect examples to target remaining issues
    - If the model still isn’t good at certain aspects, add training examples that directly show the model how to do these aspects correctly
- Scrutinize existing examples for issues
    - If your model has grammar, logic, or style issues, check if your data has any of the same issues. For instance, if the model now says "I will schedule this meeting for you" (when it shouldn’t), see if existing examples teach the model to say it can do new things that it can’t do
- Consider the balance and diversity of data
    - If 60% of the assistant responses in the data says "I cannot answer this", but at inference time only 5% of responses should say that, you will likely get an overabundance of refusals
- Make sure your training examples contain all of the information needed for the response
    - If we want the model to compliment a user based on their personal traits and a training example includes assistant compliments for traits not found in the preceding conversation, the model may learn to hallucinate information
- Look at the agreement / consistency in the training examples
    - If multiple people created the training data, it’s likely that model performance will be limited by the level of agreement / consistency between people. For instance, in a text extraction task, if people only agreed on 70% of extracted snippets, the model would likely not be able to do better than this
- Make sure your all of your training examples are in the same format, as expected for inference

### [Iterating on data quantity](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-data-quantity)

Once you’re satisfied with the quality and distribution of the examples, you can consider scaling up the number of training examples. This tends to help the model learn the task better, especially around possible "edge cases". We expect a similar amount of improvement every time you double the number of training examples. You can loosely estimate the expected quality gain from increasing the training data size by:

- Fine-tuning on your current dataset
- Fine-tuning on half of your current dataset
- Observing the quality gap between the two

In general, if you have to make a trade-off, a smaller amount of high-quality data is generally more effective than a larger amount of low-quality data.

### [Iterating on hyperparameters](https://platform.openai.com/docs/guides/fine-tuning/iterating-on-hyperparameters)

We allow you to specify the following hyperparameters:

- epochs
- learning rate multiplier
- batch size

We recommend initially training without specifying any of these, allowing us to pick a default for you based on dataset size, then adjusting if you observe the following:

- If the model does not follow the training data as much as expected increase the number of epochs by 1 or 2
    - This is more common for tasks for which there is a single ideal completion (or a small set of ideal completions which are similar). Some examples include classification, entity extraction, or structured parsing. These are often tasks for which you can compute a final accuracy metric against a reference answer.
- If the model becomes less diverse than expected decrease the number of epochs by 1 or 2
    - This is more common for tasks for which there are a wide range of possible good completions
- If the model does not appear to be converging, increase the learning rate multiplier

You can set the hyperparameters as is shown below:
``` Python
from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="file-abc123", 
  model="gpt-4o-mini", 
  hyperparameters={
    "n_epochs":2
  }
)
```




## [Fine-tuning examples](https://platform.openai.com/docs/guides/fine-tuning/fine-tuning-examples)




## FAQ
[When should I use fine-tuning vs embeddings / retrieval augmented generation?](https://platform.openai.com/docs/guides/fine-tuning/when-should-i-use-fine-tuning-vs-embeddings-retrieval-augmented-generation)

[How do I know if my fine-tuned model is actually better than the base model?](https://platform.openai.com/docs/guides/fine-tuning/how-do-i-know-if-my-fine-tuned-model-is-actually-better-than-the-base-model)


[How can I estimate the cost of fine-tuning a model?](https://platform.openai.com/docs/guides/fine-tuning/how-can-i-estimate-the-cost-of-fine-tuning-a-model)





