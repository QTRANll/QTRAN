import sys
import os
import openai
import argparse
from src.TransferLLM.translate_sqlancer import sqlancer_qtran_run
from src.TransferLLM.TransferLLM import pinolo_qtran_run
from src.Tools.DatabaseConnect.docker_create import docker_create_databases

environment_variables = os.environ
os.environ["http_proxy"] = environment_variables.get("HTTP_PROXY", "")
os.environ["https_proxy"] = environment_variables.get("HTTPS_PROXY", "")
openai.api_key = os.environ.get('OPENAI_API_KEY', '')

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)


def qtran_run(input_filename, tool, temperature=0.3, model="gpt-4o-mini", error_iteration=True, iteration_num=4,
              FewShot=False, with_knowledge=True):
    if tool.lower() not in ["pinolo", "sqlancer"]:
        print(tool + " hasn't been supported.")
        return
    fuzzers = ["norec", "tlp", "pinolo", "dqe"]
    dbs = ["clickhouse", "duckdb", "mariadb", "monetdb", "mysql", "postgres", "sqlite", "tidb"]
    for db in dbs:
        docker_create_databases(tool, "temp", db)
        for fuzzer in fuzzers:
            docker_create_databases(tool, fuzzer, db)

    if tool.lower() == "sqlancer":
        sqlancer_qtran_run(input_filepath=os.path.join(current_dir, input_filename), tool=tool,
                           temperature=temperature, model=model, error_iteration=error_iteration,
                           iteration_num=iteration_num, FewShot=FewShot, with_knowledge=with_knowledge)
    elif tool.lower() == "pinolo":
        pinolo_qtran_run(input_filename=os.path.join(current_dir, input_filename), tool=tool,
                         temperature=temperature, model=model, error_iteration=error_iteration,
                         iteration_num=iteration_num, FewShot=FewShot, with_knowledge=with_knowledge)


def main():
    parser = argparse.ArgumentParser(description="Run QTRAN for SQL translation.")
    parser.add_argument("--input_filename", type=str, required=True, help="Path to the input file (JSONL format).")
    parser.add_argument("--tool", type=str, required=True, choices=["sqlancer", "pinolo"],
                        help="Tool to use (sqlancer or pinolo).")
    parser.add_argument("--temperature", type=float, default=0.3, help="Temperature for LLM.")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model to use for LLM.")
    parser.add_argument("--error_iteration", type=bool, default=True, help="Enable error iteration.")
    parser.add_argument("--iteration_num", type=int, default=4, help="Number of iterations.")
    parser.add_argument("--FewShot", type=bool, default=False, help="Enable Few-Shot learning.")
    parser.add_argument("--with_knowledge", type=bool, default=True, help="Use knowledge-based processing.")

    args = parser.parse_args()

    qtran_run(
        input_filename=args.input_filename,
        tool=args.tool,
        temperature=args.temperature,
        model=args.model,
        error_iteration=args.error_iteration,
        iteration_num=args.iteration_num,
        FewShot=args.FewShot,
        with_knowledge=args.with_knowledge
    )


if __name__ == "__main__":
    main()
