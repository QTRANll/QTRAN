# QTRAN: Extending Metamorphic-Oracle based Logical Bug Detection Techniques for Multiple-DBMS Dialect Support

## Abstract
QTRAN mitigates the dependence existing of MOLTs(Metamorphic-Oracle based Logic Bug Detection Techinique) on specific DBMS grammars and enhances their extension capabilities to new DBMSs,which can significantly improve the reliability and testing robustness of diverse DBMSs. 

QTRAN is a novel LLM-powered approach that automatically extends existing MOLTs to various DBMSs. QTRAN ensures that most of transferred SQL statement pairs are suitable for metamorphic testing and discovered 24 previously unknown logical bugs, 16 of which have been confirmed.  

The workflow encompasses two key phases: transfer phase and mutation phase.
## Prerequisites
### Set up Environment
This guide will help you set up the environment for this project using Python 3.11. Follow the steps below to get started.
1. **Python 3.11** or higher is recommended for this project.
2. Clone the repository
``` shell
git clone <repository_url> 
cd <project_directory>
```
3. Activate the Virtual Environment
4. Install Dependencies
``` shell
pip install -r requirements.txt
```
### Build Databases
Before running, ensure that the databases  have been built and configured correctly.You can follow **the instructions in [Docker_Databases](Docker_Databases.md) (mainly using Docker-Compose)** to build the databases, or you can build them or those databases by yourself. 
**Please note that:** After the databases are successfully built, **remember to fill in the correct database configuration information into the file [database_connector_args.json](src/Tools/DatabaseConnect/database_connector_args.json)** to successfully run QTRAN.
### LLM keys
Before running QTRAN, please make sure you have **LLM API keys** so that QTRAN can successfully call the large model during execution.

Set the `api_key` as an environment variable and check if it has been set successfully.QTRAN will use this api key to access openai.

``` shell
SET OPENAI_API_KEY=${your_api_key}
```
### Fine-tune the Mutation LLM

QTRAN has carefully constructed training datasets for fine-tuning Mutation LLM for NoREC, TLP, PINOLO, and DQE. After fine-tuning on these datasets, theMutation LLM achieve high mutation accuracy. Please use the provided training datasets and your LLM keys to fine-tune the model by following fine-tuning instructions(details in [Fine-tune_MutationLLM](Fine-tune_MutationLLM.md) ), and obtain the `Fine-tuned Model ID` for use in the QTRAN tool.

**Notes:**
An LLM's API Key is needed for fine-tuning models. After fine-tuning a model, you still need to use the same API key to call the fine-tuned model. This means you cannot use a different API key to access the fine-tuned model.

Then remember to set the `Fine-tuned Model ID` of MOLTs for Mutation Phase of QTRAN.

``` shell
SET NOREC_MUTATION_LLM_ID = ${your_norec_mutation_llm_id}
SET TLP_MUTATION_LLM_ID = ${your_tlp_mutation_llm_id}
SET PINOLO_MUTATION_LLM_ID = ${your_pinolo_mutation_llm_id}
SET DQE_MUTATION_LLM_ID = ${your_dqe_mutation_llm_id}
```

## Main Process

QTRAN decompose the analysis into two phases: the transfer and mutation phases. It starts with SQL statement pairs from existing MOLTs and extends these pairs to new DBMSs through the two phases.
### Input 

The input file for QTRAN is a JSONL file in the dictionary `Input` , where each line contains a piece of test data in JSON format. Each test data is from existing MOLTs and follows the format shown below. This test data is intended for QTRAN to translate the original SQL statements from `sqlite` (a_db) into `clickhouse` (b_db) SQL statement pairs. The corresponding MOLT is NoREC (molt).
``` json
{  
  "index": 0,  
  "a_db": "sqlite",  
  "b_db": "clickhouse",  
  "molt": "norec",  
  "sqls": [  
    "CREATE TABLE t0(c0 INT UNIQUE);",  
    "INSERT INTO t0(c0) VALUES (1);",  
    "SELECT COUNT(*) FROM t0 WHERE '1' IN (t0.c0); -- unexpected: fetches row"  
  ]  
}
```
### Transfer Phase

Execute the following commands to run QTRAN.The demo input file `demo1.jsonl` is in dictionary `Input`.

Navigate to the project directory:

```shell
cd <project_directory>
```

The explanations for the commands are as follows:

| option              | description                                       |
| ------------------- | ------------------------------------------------- |
| `--input_filename`  | Path to the input file (JSONL format).            |
| `--tool`            | Tool name for MOLTs(such as "sqlancer", "pinolo") |
| `--temperature`     | Temperature for LLM(default: 0.3)                 |
| `--model`           | Model to use for LLM(default: gpt-4o-mini)        |
| `--error_iteration` | Enable error iteration(default: True)             |
| `--iteration_num`   | Number of iterations(default: 4)                  |

Default parameter execution,such as:
``` shell
python -m src.main --input_filename "Input/demo1.jsonl" --tool "sqlancer" --temperature 0.7 --model="gpt-3.5-turbo" --error_iteration=True --iteration_num 5
```

Custom parameter execution:

``` shell
python -m src.main --input_filename "Input/demo1.jsonl" --tool "sqlancer"
```

The intermediate results of the Transfer Phase are stored in the `Output` folder, specifically in `Output/demo1/TransferLLM`. For each test case, information such as `Transfer Result`, `Transfer Cost`, and `Transfer Time` is recorded.

### Mutation Phase

The intermediate results of the Mutation Phase are stored in the `Output` folder, specifically in `Output/demo1/MutationLLM`. For each test case, information such as `Mutation Result`, `Mutation Cost`, and `Mutation Time` as well as `Oracle Check` for MOLT is recorded. 

The suspicious logical bugs detected by QTRAN are stored in the `Output` folder, specifically in `Output/demo1/SuspiciousBugs`, including the final SQL statement pairs extended to new DBMSs through the two phases.






