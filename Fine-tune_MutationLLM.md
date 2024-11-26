Execute the following command to fine-tune and check the progress of fine-tuning mutation llms.

## Fine-tune

Navigate to the project directory:

```shell
cd <project_directory>
```

The explanations for the **fine-tuning commands** are as follows:

| option                 | description                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `--api_key`            | The LLM key created and set by the user.                                                                          |
| `--training_data_file` | The fine-tuning training set built for NoREC, TLP, PINOLO, and DQE.                                               |
| `--suffix`             | A suffix used to add to the fine-tuned model, which identifies a specific version or use of the fine-tuned model. |

Fine-tune for NoREC:

```shell
python -m src.MutationLlmModelFineTuning.FineTuning_MutationLLM --api_key %OPENAI_API_KEY% --training_data_filename "MutationData/FineTuningTrainingData/norec.jsonl" --suffix "norec"
```

Fine-tune for TLP:

```shell
python -m src.MutationLlmModelFineTuning.FineTuning_MutationLLM --api_key %OPENAI_API_KEY% --training_data_filename "MutationData/FineTuningTrainingData/tlp.jsonl" --suffix "tlp"
```

Fine-tune for PINOLO:

```shell
python -m src.MutationLlmModelFineTuning.FineTuning_MutationLLM --api_key %OPENAI_API_KEY% --training_data_filename "MutationData/FineTuningTrainingData/pinolo.jsonl" --suffix "pinolo"
```

Fine-tune for DQE:

```shell
python -m src.MutationLlmModelFineTuning.FineTuning_MutationLLM --api_key %OPENAI_API_KEY% --training_data_filename "MutationData/FineTuningTrainingData/dqe.jsonl" --suffix "dqe"
```

**Fine-tuning will take some time, so make sure to record the `Fine-tuning Job ID` generated after running the above command. You can use the following command to check the fine-tuning stage.**

## Check Fine-tuning Stage

Use the following command and the `Fine-tuning Job ID` obtained to check the completion stage of the fine-tuning tasks.

```shell
python -m src.MutationLlmModelFineTuning.FineTuning_MutationLLM --api_key %OPENAI_API_KEY% --job_id ${Fine-tuning Job ID}
```

The explanation for the command is as follows:

| option      | description                                                  |
| ----------- | ------------------------------------------------------------ |
| `--api_key` | The LLM key created and set by the user.                     |
| `--job_id`  | The `Fine-tuning Job ID` returned from the fine-tuning task. |

The output result of a successful fine-tuning task will look like this. Be sure to record the fine-tuned model ID `Fine-tuned Model ID` for use in future QTRAN mutation LLM tasks:

```shell
The Fine-tuning Job ${Fine-tuning Job ID} has been finished.
The fine_tuned_model ID is: ${Fine-tuned Model ID}.
```

Please record the `fine_tuned_model ID` to run QTRAN Mutation LLM later.


