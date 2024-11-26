import json
import subprocess
import time
import os

current_file_path = os.path.abspath(__file__)
# 获取当前文件所在目录
current_dir = os.path.dirname(current_file_path)

with open(os.path.join(current_dir, "docker_create_commands.json"), "r", encoding="utf-8") as r:
    docker_commands = json.load(r)

def get_database_connector_args(dbType):
    with open(os.path.join(current_dir, "database_connector_args.json"), "r", encoding="utf-8") as r:
        database_connection_args = json.load(r)
    if dbType.lower() in database_connection_args:
        return database_connection_args[dbType.lower()]

def run_command(command, capture_output=True, shell=True):
    """
    执行命令并打印结果。
    :param command: 要执行的命令列表。
    :param capture_output: 是否捕获输出。
    :param shell: 是否通过 shell 执行。
    """
    command_str = ' '.join(command)
    print(f"执行命令: {command_str}")
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", command_str],  # 使用 wsl -d 指定进入 Ubuntu，展开列表命令
        text=True,  # 以文本模式返回输出
        capture_output=capture_output,  # 捕获标准输出和标准错误
        shell=shell
    )
    """
    result = subprocess.run(
        ["wsl", "-e", "bash", "-c", "cd ~ && " + command_str],  # 使用 wsl -d 指定进入 Ubuntu，展开列表命令
        text=True,  # 以文本模式返回输出
        capture_output=capture_output,  # 捕获标准输出和标准错误
        shell=shell
    )
    """
    print(f"命令输出: {result.stdout}")
    print(f"命令错误: {result.stderr}")
    """
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    """
    print('---------------------------------------------------')
    return result


def check_container_running(container_name):
    """
    检查容器是否存在。
    :param container_name: 容器名称。
    :return: 如果容器存在，返回 True，否则返回 False。
    """
    # result = run_command(["docker", "ps", "-a", "-q", "-f", f"name={container_name}"])
    result = run_command(["docker", "ps", "-a", "-q", "-f", f"name={container_name}"])
    return bool(result.stdout.strip())  # 如果 stdout 非空，表示容器存在



def check_image_exists(image_name):
    """
    检查镜像是否存在。
    :param image_name: 镜像名称（例如 mysql:8.0.39）。
    :return: 如果镜像存在，返回 True，否则返回 False。
    """
    result = run_command(["docker", "images", "-q", image_name])
    return bool(result.stdout.strip())  # 如果 stdout 非空，表示镜像存在



def format_dict_strings(data, **args):
    """
    递归地遍历字典或列表，将其中的字符串项替换为 format 格式化后的字符串。
    """
    if isinstance(data, dict):
        return {key: format_dict_strings(value, **args) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_dict_strings(item, **args) for item in data]
    elif isinstance(data, str):
        # 检查字符串中是否包含占位符
        if any(f"{{{key}}}" in data for key in args):
            return data.format(**args)
        return data
    else:
        return data  # 如果既不是字典、列表，也不是字符串，原样返回

def is_container_running(container_name):
    result = run_command(["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"])
    return container_name in result.stdout   # 如果 stdout 非空，表示镜像存在


def docker_create_databases(tool, exp, dbType):
    if dbType.lower() not in docker_commands:
        return
    commands = docker_commands[dbType.lower()]
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    commands_formatted = format_dict_strings(commands, **args)

    try:
        if dbType.lower() == "tidb":
            # run_tidb
            run_command(commands_formatted["run_container"])
            # exec_into_container, login_mysql, create_databases
            for sql in commands_formatted["create_databases"]:
                run_command(commands_formatted["enter_container"] + commands_formatted["login_in"] + ["'" + sql + "'"])
        elif dbType.lower() == "clickhouse":
            # pull_docker
            if not check_image_exists(commands_formatted["docker_name"]):
                run_command(commands_formatted["pull_docker"])
            # run_docker_container
            if not is_container_running(commands_formatted["container_name"]):
                run_command(commands_formatted["run_container"])
                time.sleep(15)
            # enable access
            if "vim" not in run_command(commands_formatted["enter_container"] + ["dpkg", "-l", "|", "grep", "vim"]).stdout:
                for cmd in commands_formatted["access_enable"]:
                    run_command(commands_formatted["enter_container"] + cmd)
            # create admin user
            for cmd in commands_formatted["create_admin_login_in"]:
                run_command(commands_formatted["enter_container"] + cmd)
            # exec_into_container, login_mysql, create_databases
            for sql in commands_formatted["create_databases"]:
                if isinstance(sql, list):
                    run_command(commands_formatted["enter_container"] + commands_formatted["login_in"] + sql)
                elif isinstance(sql, str):
                    run_command(commands_formatted["enter_container"] + commands_formatted["login_in"] + ["'" + sql + "'"])
        else:
            # pull_docker
            if not check_image_exists(commands_formatted["docker_name"]):
                run_command(commands_formatted["pull_docker"])
            # run_docker_container
            if not is_container_running(commands_formatted["container_name"]):
                run_command(commands_formatted["run_container"])
                time.sleep(15)
            # exec_into_container, login_mysql, create_databases
            for sql in commands_formatted["create_databases"]:
                if isinstance(sql, list):
                    run_command(commands_formatted["enter_container"] + commands_formatted["login_in"] + sql)
                elif isinstance(sql, str):
                    run_command(
                        commands_formatted["enter_container"] + commands_formatted["login_in"] + ["'" + sql + "'"])

    except subprocess.CalledProcessError as e:
        print(f"命令执行失败：{e}")
        print(f"标准输出: {e.output}")
        print(f"标准错误: {e.stderr}")


def run_container(tool, exp, dbType):
    if dbType.lower() not in docker_commands:
        return
    commands = docker_commands[dbType.lower()]
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    commands_formatted = format_dict_strings(commands, **args)
    try:
        if dbType.lower() == "tidb":
            # run_tidb
            run_command(commands_formatted["run_container"])
        else:
            # run_docker_container
            run_command(["docker", "start", commands_formatted["container_name"]])
            time.sleep(15)
            """
            if not is_container_running(commands_formatted["container_name"]):
                run_command(["docker", "start", commands_formatted["container_name"]])
                time.sleep(12)
            """
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败：{e}")
        print(f"标准输出: {e.output}")
        print(f"标准错误: {e.stderr}")

