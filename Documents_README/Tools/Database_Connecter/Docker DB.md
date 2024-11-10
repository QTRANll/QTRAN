[Dialects — SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/dialects/)

备注：
* 在docker客户端进行启动：mysql，mariadb，postgres
* 在wsl终端启动：tidb，monetdb（每次端口可能还不一样）
* 不需要特殊操作：sqlite，duckdb
* 设置容器容器：docker update --restart=always 容器ID(或者容器名)
# Docker DB

## WSL Docker 启动

```
sudo service docker start
```

## MySQL（可行）

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
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE PINOLO_MySQL;

CREATE DATABASE SQLancer_MySQL;
```


```
USE SQLancer_MySQL;
show tables;
```



## MariaDB(可行)

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
CREATE DATABASE SQLancer_MariaDB;
```



## TiDB（不可行）

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

使用 *命令行工具* 登录到 TiDB 数据库：

```

mysql -h 127.0.0.1 -P 4000 -u root -p
```

修改 root 密码：

```
ALTER USER root IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE PINOLO_TiDB;
CREATE DATABASE SQLancer_TiDB;
```


## TiDB（可行）
[TiDB 数据库快速上手指南 | TiDB 文档中心 (pingcap.com)](https://docs.pingcap.com/zh/tidb/dev/quick-start-with-tidb?_gl=1*ca4w1m*_gcl_au*MjY3Njg4MzM4LjE3MjY5OTE3ODc.*_ga*MTQyNDIyMDQ3Mi4xNzI2OTkxNzg2*_ga_3JVXJ41175*MTcyNjk5MTc4Ni4xLjEuMTcyNjk5MTc5OS40Ny4wLjE1OTQ5MDg3NA..*_ga_CPG2VW1Y41*MTcyNjk5MTc4OC4xLjAuMTcyNjk5MTc4OC4wLjAuMA..#%E5%9C%A8%E5%8D%95%E6%9C%BA%E4%B8%8A%E6%A8%A1%E6%8B%9F%E9%83%A8%E7%BD%B2%E7%94%9F%E4%BA%A7%E7%8E%AF%E5%A2%83%E9%9B%86%E7%BE%A4)

https://blog.csdn.net/Jamesbond_/article/details/123419317

```
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh

Successfully set mirror to https://tiup-mirrors.pingcap.com
Detected shell: bash
Shell profile:  /root/.bashrc
Installed path: /root/.tiup/bin/tiup
===============================================
Have a try:     tiup playground
===============================================

提示对应 Shell profile 文件的绝对路径:/root/.bashrc
```

```
source ${your_shell_profile}
改为
source /root/.bashrc
```

```
tiup cluster
或者更新
tiup update --self && tiup update cluster
```

![[Pasted image 20241021085624.png]]


![[Pasted image 20241021085923.png]]

```
global:
        user: "tidb"
        ssh_port: 22
        deploy_dir: "/home/TiDB/deploy"
        data_dir: "/home/TiDB/data"
monitored:
        node_exporter_port: 9100
        blackbox_exporter_port: 9115
server_configs:
        tidb:
                instance.tidb_slow_log_threshold: 300
        tikv:
                readpool.storage.use-unified-pool: false
                readpool.coprocessor.use-unified-pool: true
        pd:
                replication.enable-placement-rules: true
                replication.location-labels: ["host"]
        tiflash:
                logger.level: "info"

pd_servers:
        - host: 172.20.163.66

tidb_servers:
        - host: 172.20.163.66

tikv_servers:
        - host: 172.20.163.66
          port: 20160
          status_port: 20180
          config:
                  server.labels: { host: "logic-host-1" }


        - host: 172.20.163.66
          port: 20161
          status_port: 20181
          config:
                  server.labels: { host: "logic-host-2" }

        - host: 172.20.163.66
          port: 20162
          status_port: 20182
          config:
                  server.labels: { host: "logic-host-3" }

tiflash_servers:
        - host: 172.20.163.66

monitoring_servers:
        - host: 172.20.163.66

grafana_servers:
        - host: 172.20.163.66
```



```
 tiup cluster deploy tidb-test 8.3.0 ./topo.yaml --user root -p 123456
```

启动集群（TIDB需要每次打开启动集群）
```
首次：tiup cluster start tidb-test --initn 

后续：tiup cluster start tidb-test
```

访问 TiDB 数据库，密码为空：
```
mysql -h 172.19.42.242 -P 4000 -u root -p
123456
```

创建数据库：
```
CREATE DATABASE PINOLO_TiDB;
```


## PostgreSQL（可行）

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
CREATE DATABASE PINOLO_PostgresSQL;
CREATE DATABASE SQLancer_PostgresSQL;
```


关于下面问题的解决：
https://github.com/sqlalchemy/sqlalchemy/discussions/10592

## SQLite（可行）

目前，几乎所有版本的 Linux 操作系统都附带 SQLite。

```
sqlite3
```

```
"sqlite": {  
    "db_type": "sqlite",  
    "host": "",  
    "port": 0,  
    "username": "",  
    "password": "",  
    "dbname": "..\\DLL_Info\\PINOLO_SQLite.db",  
    "ddl_filename": "ddl_duckdb.json"  
},
```



```
[  
    "USE temp;",  
    "DROP DATABASE IF EXISTS db_name;",  
    "CREATE DATABASE db_name;"  
]

-- 切换数据库：SQLite 不需要 "USE" 语句，直接指定数据库文件路径即可。

-- 删除数据库文件（在 SQLite 中模拟 DROP DATABASE）
-- 需要通过文件系统命令删除 .db 文件，比如：
-- 在 Python、Shell 等环境中可以用：
-- rm db_name.db

-- 创建新数据库（在 SQLite 中是创建一个新的数据库文件）
-- 通过 SQLite CLI 或程序连接新数据库文件：
sqlite3 db_name.db

```

## DuckDB(参照SQlite，可行)

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



## MonetDB（可行）

文件中添加以下python代码
下面的连接不用看
[MonetDB/sqlalchemy-monetdb: A SQLAlchemy dialect for MonetDB](https://github.com/MonetDB/sqlalchemy-monetdb)
[sqlalchemy-monetdb · PyPI](https://pypi.org/project/sqlalchemy-monetdb/)
[MonetDB/e for Python | MonetDB Docs](https://www.monetdb.org/documentation-Aug2024/dev-guide/mbedded-python/)

拉取MonetDB Docker镜像：

```
docker pull monetdb/monetdb
修改为
docker pull monetdb/monetdb-r-docker
```

运行MonetDB容器：

```
docker volume create monetdb_data # 创建数据卷，用于映射MonetDB内存放数据的文件夹（可选）
docker run -d --name monetdbtest -v monentdb_data:/var/monetdb5/dbfarm -p 5000:5000 monetdb/monetdb

修改为

docker run -d -P --name monetdbtest -p 50000:50000 monetdb/monetdb-r-docker
```

进入MonetDB容器：

```
docker exec -it monetdbtest bash
```

创建TEST数据库：

```
monetdb create PINOLO_MonetDB # 创建数据库
monetdb release PINOLO_MonetDB 
monetdb start PINOLO_MonetDB  # 一定要启动数据库
monetdb stop PINOLO_MonetDB



monetdb create SQLancer_MonetDB # 创建数据库
monetdb release SQLancer_MonetDB
monetdb start SQLancer_MonetDB  # 一定要启动数据库
monetdb stop SQLancer_MonetDB

monetdb lock db_name
monetdb destory db_name
```

使用mclient登录到MonetDB数据库（默认用户名为monetdb，默认密码为monetdb）：

```
mclient -u monetdb -d PINOLO_MonetDB

mclient -u monetdb -d SQLancer_MonetDB
```

修改root密码：

```
ALTER USER SET PASSWORD '123456' USING OLD PASSWORD 'monetdb';
```



```
SELECT name FROM sys.tables WHERE system = false;
```

## ClickHouse(可行)

拉取ClickHouse Docker镜像：

```
docker pull clickhouse/clickhouse-server
```

运行ClickHouse容器：

```
docker run -d --name clickhousetest -p 8123:8123 -p 9000:9000 -v <宿主机的文件路径>:/var/lib/clickhouse clickhouse/clickhouse-server

docker run -d --name clickhousetest -p 8123:8123 -p 9000:9000  clickhouse/clickhouse-server
```

进入ClickHouse容器：

```
docker exec -it clickhousetest bash
```

为默认账号开启管理员权限：
[user `default` doesn't have enough grants for creating another user \ role \ row policy for 20.4 and 20.5 · Issue #13057 · ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse/issues/13057)

```
apt-get update # 更新apt-get（可选）
apt-get install vim # 安装vim（可选）
vim /etc/clickhouse-server/users.xml # 修改用户配置

# 找到<default>标签内的注释如下，取消掉该行注释：
<!-- <access_management>1</access_management> -->

<yandex>
    <users>
        <default>
            <access_management>1</access_management>
            <named_collection_control>1</named_collection_control>
            <show_named_collections>1</show_named_collections>
            <show_named_collections_secrets>1</show_named_collections_secrets>
        </default>
    </users>
</yandex>
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
CREATE DATABASE PINOLO_ClickHouse;
```

[【Python】 使用 SQLAlchemy 连接 ClickHouse 数据库_python sqlalchemy clickhouse-CSDN博客](https://blog.csdn.net/qq_35240081/article/details/141114048)





## OceanBase

拉取 OceanBase Docker 镜像：

```
sudo docker pull oceanbase/oceanbase-ce
```

【WSL部署Oceanbase会遇到的问题： https://blog.csdn.net/weixin_43647393/article/details/125907978 】

- 确保您的机器至少提供 2 核 10GB 以上的可用资源。

运行 OceanBase 容器：

```
sudo docker run -p 2881:2881 --name oceanbasetest -d oceanbase/oceanbase-ce


sudo docker run --name oceanbasetest -e OCEANBASE_ROOT_PASSWORD='123456' -p 2881:2881 -d oceanbase/oceanbase-ce
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
> **虚拟内存和文件描述符数量**  
> sudo sysctl -w vm.max_map_count=655360
> sudo sysctl -w fs.file-max=6573688
>
> **AI/O 最大数量**  sudo sysctl -w fs.aio-max-nr=1048576



进入 OceanBase 容器：

```
docker exec -it oceanbasetest bash
```

使用 MySQL 客户端进入 OceanBase 的 SQL 命令行工具：

```
mysql -h 127.0.0.1 -P 2881 -u root -p

obclient -u[用户名]@[租户名]#[集群名称] -P[端口号] -h[ip地址] -p[密码] -D[数据库名] -c

obclient -h127.0.0.1 -P2881 -uroot -p prootPWD123

obclient -h127.0.0.1 -P2881 -uroot@sys -c -A oceanbase


```

修改 root 密码：

```
ALTER USER root IDENTIFIED BY '123456';
```

创建名为 TEST 的数据库：

```
CREATE DATABASE TEST3;
```


oceanbase： https://blog.csdn.net/suixinfeixiangfei/article/details/131207121



---

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


