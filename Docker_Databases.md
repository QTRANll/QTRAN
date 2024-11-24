## ClickHouse

Pull the ClickHouse Docker image:
```
docker pull clickhouse/clickhouse-server:24.9.2.42
```

Run the ClickHouse container:

```
docker run -d --name clickhouse_QTRAN -p 8123:8123 -p 9000:9000  clickhouse/clickhouse-server
```

Enter the ClickHouse container:

```
docker exec -it clickhouse_QTRAN bash
```

[Grant administrator privileges to the default account:](https://github.com/ClickHouse/ClickHouse/issues/13057)

```
apt-get update # install apt-get（optional）
apt-get install vim # install vim（optional）
```

```
vim /etc/clickhouse-server/users.xml # Modify user configuration
```

```
# Find the comment inside the `<default>` tag as follows and uncomment that line
<!-- <access_management>1</access_management> -->   

# Add following configurations after `<access_management>1</access_management>`
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

Log in to the ClickHouse database using `clickhouse-client` (with the default account):

```
clickhouse-client
```

Create an administrator account:

```
CREATE user admin IDENTIFIED WITH sha256_password BY '123456';
```

Grant all privileges to the administrator account:

```
GRANT ALL PRIVILEGES ON *.* TO admin WITH GRANT OPTION;
```

Log out:

```
exit
```

Log in to the ClickHouse database using `clickhouse-client` (with an administrator account, and before doing so, you can revoke the default account's permissions by uncommenting the corresponding settings):

```
clickhouse-client -u admin --password 123456
```


Modify the administrator account password:

```
ALTER USER admin IDENTIFIED WITH plaintext_password BY '123456';
```



## MySQL（可行）


拉取 MySQL Docker 镜像：

```bash
sudo docker pull mysql:8.0.39
```

运行 MySQL 容器：

```
sudo docker run --name mysql_QTRAN -e MYSQL_ROOT_PASSWORD=123456 -p 13306:3306 -d mysql
```

进入 MySQL 容器：

```
sudo docker exec -it mysql_QTRAN bash
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
其他：
USE SQLancer_MySQL;
show tables;
```



## MariaDB(可行)

拉取 MariaDB Docker 镜像：

```
docker pull mariadb:11.5.2
```

运行 MariaDB 容器：

```
docker run --name mariadb_QTRAN -e MYSQL_ROOT_PASSWORD=123456 -p 9901:3306 -d mariadb
```

进入 MariaDB 容器：

```
docker exec -it mariadb_QTRAN bash
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


## TiDB（可行）
[TiDB 数据库快速上手指南 | TiDB 文档中心 (pingcap.com)](https://docs.pingcap.com/zh/tidb/dev/quick-start-with-tidb?_gl=1*ca4w1m*_gcl_au*MjY3Njg4MzM4LjE3MjY5OTE3ODc.*_ga*MTQyNDIyMDQ3Mi4xNzI2OTkxNzg2*_ga_3JVXJ41175*MTcyNjk5MTc4Ni4xLjEuMTcyNjk5MTc5OS40Ny4wLjE1OTQ5MDg3NA..*_ga_CPG2VW1Y41*MTcyNjk5MTc4OC4xLjAuMTcyNjk5MTc4OC4wLjAuMA..#%E5%9C%A8%E5%8D%95%E6%9C%BA%E4%B8%8A%E6%A8%A1%E6%8B%9F%E9%83%A8%E7%BD%B2%E7%94%9F%E4%BA%A7%E7%8E%AF%E5%A2%83%E9%9B%86%E7%BE%A4)

关于SSH密钥： https://blog.csdn.net/Jamesbond_/article/details/123419317

1. 下载并安装 TiUP：
```
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh

Successfully set mirror to https://tiup-mirrors.pingcap.com
Detected shell: bash
Shell profile:  /root/.bashrc
Installed path: /root/.tiup/bin/tiup
===============================================
Have a try:     tiup playground
===============================================

提示对应 Shell profile 文件的绝对路径:/root/.bashrc  (/home/zhuqinglin/.bashrc)
```
2. 声明全局环境变量：
```
source ${your_shell_profile}
改为
source /root/.bashrc
source /home/zhuqinglin/.bashrc
```
3. 安装 TiUP 的 cluster 组件：
```
tiup cluster
或者更新 (如果机器已经安装 TiUP cluster，需要更新软件版本:)
tiup update --self && tiup update cluster
```


5. 由于模拟多机部署，需要通过 root 用户调大 sshd 服务的连接数限制：
* 修改 `/etc/ssh/sshd_config` 将 `MaxSessions` 调至 20。
    
* 重启 sshd 服务：    
    ```sh
    service sshd restart
    sudo systemctl enable ssh.service
    ```


6. 创建并启动集群
按下面的配置模板，编辑配置文件，命名为 `topo.yaml`，其中：
- `user: "tidb"`：表示通过 `tidb` 系统用户（部署会自动创建）来做集群的内部管理，默认使用 22 端口通过 ssh 登录目标机器
- `replication.enable-placement-rules`：设置这个 PD 参数来确保 TiFlash 正常运行
- `host`：设置为本部署主机的 IP
配置模板如下：
* 新建deploy_dir和data_dir

（ip是eth0）
![[Pasted image 20241118111144.png]]
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
        - host: 172.24.89.100 

tidb_servers:
        - host: 172.24.89.100 

tikv_servers:
        - host: 172.24.89.100 
          port: 20160
          status_port: 20180
          config:
                  server.labels: { host: "logic-host-1" }


        - host: 172.24.89.100 
          port: 20161
          status_port: 20181
          config:
                  server.labels: { host: "logic-host-2" }

        - host: 172.24.89.100 
          port: 20162
          status_port: 20182
          config:
                  server.labels: { host: "logic-host-3" }

tiflash_servers:
        - host: 172.24.89.100 

monitoring_servers:
        - host: 172.24.89.100 

grafana_servers:
        - host: 172.24.89.100 
```



7. 执行集群部署命令：

```
tiup cluster deploy <cluster-name> <version> ./topo.yaml --user root -p

tiup cluster deploy tidb_QTRAN 8.3.0 ./topo.yaml --user root -p 123456
```
- 参数 `<cluster-name>` 表示设置集群名称
- 参数 `<version>` 表示设置集群版本，例如 `v8.4.0`。可以通过 `tiup list tidb` 命令来查看当前支持部署的 TiDB 版本
- 参数 `-p` 表示在连接目标机器时使用密码登录
- 如果主机通过密钥进行 SSH 认证，请使用 `-i` 参数指定密钥文件路径，`-i` 与 `-p` 不可同时使用。

按照引导，输入”y”及 root 密码，来完成部署：
```
    Do you want to continue? [y/N]:  y
    Input SSH password:
```


8. 启动集群（TIDB需要每次打开启动集群）
```
首次：tiup cluster start tidb_QTRAN --initn 

后续：tiup cluster start tidb_QTRAN

tiup cluster stop tidb_QTRAN
tiup cluster display tidb_QTRAN
```

访问 TiDB 数据库，密码为空：
```
mysql -h172.24.89.100  -P 4000 -u root -p
123456
```

创建数据库：
```
CREATE DATABASE PINOLO_TiDB;
```


## TiDB（不可行）

拉取 TiDB Docker 镜像：

```
docker pull pingcap/tidb
```

运行 TiDB 容器：

```
docker run -d --name tidb_QTRAN -p 4000:4000 -p 10080:10080 pingcap/tidb
```

进入 TiDB 容器：

```
docker exec -it tidb_QTRAN bash
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


## PostgreSQL（可行）

拉取 PostgreSQL Docker 镜像：

```
docker pull postgres:16.3
```

运行 PostgreSQL 容器：

```
docker run --name postgres_QTRAN -e POSTGRES_PASSWORD=123456 -p 5432:5432 -d postgres
```

进入 PostgreSQL 容器：

```
docker exec -it postgres_QTRAN bash
```

使用 PostgreSQL 客户端登录到 PostgreSQL 数据库：

```
psql -h 127.0.0.1 -U postgres
```

修改 root 密码：(此处不修改密码？)

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



## DuckDB(下面的拉取镜像的内容忽略，参照SQlite，可行)

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
下面的连接不用看：
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

docker run -d -P --name monetdb_QTRAN -p 50000:50000 monetdb/monetdb-r-docker
```

进入MonetDB容器：

```
docker exec -it monetdb_QTRAN bash
```

创建TEST数据库：

```
monetdb create PINOLO_MonetDB # 创建数据库
monetdb release PINOLO_MonetDB # 开启锁定权限，后续才可以删除database
monetdb start PINOLO_MonetDB  # 一定要启动数据库
monetdb stop PINOLO_MonetDB  # 关闭数据库



monetdb create SQLancer_MonetDB # 创建数据库
monetdb release SQLancer_MonetDB
monetdb start SQLancer_MonetDB  # 一定要启动数据库
monetdb stop SQLancer_MonetDB

monetdb lock db_name  # 先lock数据库，下一步删除数据库
monetdb destory db_name  # 删除数据库
```

使用mclient登录到MonetDB数据库（默认用户名为monetdb，默认密码为monetdb）：

```
mclient -u monetdb -d PINOLO_MonetDB

mclient -u monetdb -d SQLancer_MonetDB

打印所有databases：monetdb status
```

修改root密码(可选项，已知默认的密码是monetdb，这里就不改了吧)：

```
ALTER USER SET PASSWORD '123456' USING OLD PASSWORD 'monetdb';
```

```
SELECT name FROM sys.tables WHERE system = false;
```





----

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



