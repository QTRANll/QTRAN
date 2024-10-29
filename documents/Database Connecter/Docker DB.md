# Docker DB

## WSL Docker 启动

```
sudo service docker start
```

## MySQL

安装MySQL Server

```
sudo apt-get install mysql-server
```

拉取 MySQL Docker 镜像：

```bash
sudo docker pull mysql
```

运行 MySQL 容器：

```
sudo docker run --name mysqltest -e MYSQL_ROOT_PASSWORD=123456 -p 13306:3306 -d mysql
```

进入 MySQL 容器：

```
sudo docker exec -it mysqltest bash
```

使用 MySQL 命令行工具登录到 MySQL 数据库：

```
mysql -u root -p
```

使用 MySQL 客户端连接到 MySQL 数据库：

```
mysql -h 127.0.0.1 -P 13306 -u root -p
```

修改 root 密码：

```
sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE TEST3;
```



## MariaDB

拉取 MariaDB Docker 镜像：

```
docker pull mariadb
```

运行 MariaDB 容器：

```
docker run --name mariadbtest -e MYSQL_ROOT_PASSWORD=123456 -p 9901:3306 -d mariadb
```

进入 MariaDB 容器：

```
docker exec -it mariadbtest bash
```


使用 MariaDB 客户端登录到 MariaDB 数据库：

```
mariadb -u root -p
输入密码：123456
```

修改 root 密码：

```
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE PINOLO_MariaDB;
```



## TiDB

拉取 TiDB Docker 镜像：

```
docker pull pingcap/tidb
```

运行 TiDB 容器：

```
docker run -d --name tidbtest -p 4000:4000 -p 10080:10080 pingcap/tidb
```

进入 TiDB 容器：

```
docker exec -it tidbtest bash
```

使用 TiDB 命令行工具登录到 TiDB 数据库：

```
mysql -h 127.0.0.1 -P 4000 -u root -p
```

修改 root 密码：

```
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE TEST3;
```



## OceanBase

拉取 OceanBase Docker 镜像：

```
sudo docker pull oceanbase/oceanbase-ce
```

【WSL部署Oceanbase会遇到的问题：https://blog.csdn.net/weixin_43647393/article/details/125907978】

- 确保您的机器至少提供 2 核 10GB 以上的可用资源。

运行 OceanBase 容器：

```
sudo docker run -p 2881:2881 --name oceanbasetest -d oceanbase/oceanbase-ce
```

启动预计需要 2-5 分钟。执行以下命令，如果返回 `boot success!`，则启动成功。

```bash
sudo docker logs oceanbasetest | tail -1
```

> 下面是我尝试做的修改
>
> 在C:\Users\你的用户名\   目录下创建一个.wslconfig文件  ；   在.wslconfig文件中录入以下信息后保存文件（详情可参考[微软官方：WSL 中的高级设置配置](https://docs.microsoft.com/zh-cn/windows/wsl/wsl-config#wslconfig)））
>
> ```
> # Settings apply across all Linux distros running on WSL 2
> [wsl2]
> 
> # Limits VM memory to use no more than 4 GB, this can be set as whole numbers using GB or MB
> memory=10GB 
> 
> # Sets the VM to use two virtual processors
> processors=2
> ```
>
> **文件打开数限制**   sudo bash -c 'echo -e "* soft nofile 20000\n* hard nofile 20000" >> /etc/security/limits.conf'
>
> **核心文件大小和栈大小**  sudo bash -c 'echo -e "* soft core unlimited\n* hard core unlimited\n* soft stack unlimited\n* hard stack unlimited" >> /etc/security/limits.conf'
>
> **虚拟内存和文件描述符数量**  sudo sysctl -w vm.max_map_count=655360
> sudo sysctl -w fs.file-max=6573688
>
> **AI/O 最大数量**  sudo sysctl -w fs.aio-max-nr=1048576





进入 OceanBase 容器：

```
docker exec -it oceanbasetest bash
```

使用 MySQL 客户端进入 OceanBase 的 SQL 命令行工具：

```
sudo mysql -h 127.0.0.1 -P 2881 -u root -p
```

修改 root 密码：

```
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE TEST3;
```



## PostgreSQL

拉取 PostgreSQL Docker 镜像：

```
docker pull postgres
```

运行 PostgreSQL 容器：

```
docker run --name postgrestest -e POSTGRES_PASSWORD=123456 -p 5432:5432 -d postgres
```

进入 PostgreSQL 容器：

```
docker exec -it postgrestest bash
```

使用 PostgreSQL 客户端登录到 PostgreSQL 数据库：

```
psql -h 127.0.0.1 -U postgres
```

修改 root 密码：

```
ALTER USER postgres WITH PASSWORD '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE TEST;
```



## SQLite

目前，几乎所有版本的 Linux 操作系统都附带 SQLite。

```
sqlite3
```



## Virtuoso

拉取Virtuoso Docker镜像：

```
docker pull openlink/virtuoso-opensource-7 # 开源版本，无需许可证
# or docker pull openlink/virtuoso-closedsource-7 # 企业版镜像，需要许可证（下同）
# or docker pull openlink/virtuoso-closedsource-8
```

运行Virtuoso容器：

```
docker run -d --name virtuosotest -e DBA_PASSWORD=123456 -p 1111:1111 -p 8890:8890 -v <宿主机的文件路径>:/database openlink/virtuoso-opensource-7
```

进入Virtuoso容器：

```
docker exec -it virtuosotest bash
```

使用isql登录到Virtuoso数据库：

```
isql 1111 dba 123456
```

修改root密码（dba用户的密码）：

```
DB.DBA.USER_CHANGE_PASSWORD('dba', '123456', '123456');
```

创建名为TEST的数据库（Virtuoso通过逻辑命名图（Named Graph）来组织数据）

```
DB.DBA.RDF_GRAPH_GROUP_CREATE ('http://localhost:8090/test', 1);
```



## MonetDB

拉取MonetDB Docker镜像：

```
docker pull monetdb/monetdb
```

运行MonetDB容器：

```
docker volume create monetdb_data # 创建数据卷，用于映射MonetDB内存放数据的文件夹（可选）
docker run -d --name monetdbtest -v monentdb_data:/var/monetdb5/dbfarm -p 5000:5000 monetdb/monetdb
```

进入MonetDB容器：

```
docker exec -it monetdbtest bash
```

创建TEST数据库：

```
monetdb create TEST # 创建数据库
monetdb release TEST # 启动数据库实例
```

使用mclient登录到MonetDB数据库（默认用户名为monetdb，默认密码为monetdb）：

```
mclient -u monetdb -d TEST
```

修改root密码：

```
ALTER USER SET PASSWORD '123456' USING OLD PASSWORD 'monetdb';
```



## DuckDB

拉取DuckDB Docker镜像：

```
docker pull davidgasquez/duckdb
```

以交互模式运行DuckDB容器：

```
docker run -it --name dockdbtest -v <宿主机的文件路径>:/data davidgasquez/duckdb bash
```

创建名为TEST的数据库并启动DuckDB：

```
dockdb /data/TEST.duckdb
```

> 后续可通过链接<宿主机的文件路径>/TEST.duckdb来访问TEST数据库



## ClickHouse

拉取ClickHouse Docker镜像：

```
docker pull clickhouse/clickhouse-server
```

运行ClickHouse容器：

```
docker run -d --name clickhousetest -p 8123:8123 -p 9000:9000 -v <宿主机的文件路径>:/var/lib/clickhouse clickhouse/clickhouse-server
```

进入ClickHouse容器：

```
docker exec -it clickhousetest bash
```

为默认账号开启管理员权限：

```
apt-get update # 更新apt-get（可选）
apt-get install vim # 安装vim（可选）
vim /etc/clickhouse-server/users.xml # 修改用户配置

# 找到<default>标签内的注释如下，取消掉该行注释：
<!-- <access_management>1</access_management> -->
```

使用clickhouse-client登录到ClickHouse数据库（使用默认账号）：

```
clickhouse-client
```

创建管理员账号：

```
CREATE user admin IDENTIFIED WITH sha256_password BY '123456';
```

赋予管理员账号所有权限：

```
GRANT ALL PRIVILEGES ON *.* TO admin WITH GRANT OPTION;
```

退出登录

```
exit
```

使用clickhouse-client登录到ClickHouse数据库（使用管理员账号，在这之前可以关闭默认账号的权限，即恢复相应的注释）：

```
clickhouse-client -u admin --password 123456
```

修改管理员账号密码：

```
ALTER USER admin IDENTIFIED WITH plaintext_password BY '123456';
```

创建名为TEST的数据库：

```
CREATE DATABASE TEST;
```

