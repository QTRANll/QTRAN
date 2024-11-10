# SQLite

https://sqlite.org/src/doc/trunk/README.md

仓库里还包含一些测试用例, 不过大部分测试用例是在仓库外单独管理的.

## fossil版本控制

<font color="red">SQLite的源码通过Fossil管理. GitHub上的只是个镜像. </font>

Fossil可执行文件(独立文件, 可直接使用): https://fossil-scm.org/home/uv/download.html

使用:

```shell
../fossil-linux-x64-2.19/fossil clone https://www.sqlite.org/src ./sqlite.fossil
Round-trips: 18   Artifacts sent: 0  received: 101108
Clone done, wire bytes sent: 4755  received: 80323733  ip: 45.33.6.223
Rebuilding repository meta-data...
  100.0% complete...
Extra delta compression... 
Vacuuming the database... 
project-id: 2ab58778c2967968b94284e989e43dc11791f548
server-id:  f702a63692793c8f2dabc706bd43cf3f1794961b
admin-user: aosp (password is "d2XEUM8QrD")
../fossil-linux-x64-2.19/fossil open ./sqlite.fossil
```

更新至最新版本:

```shell
fossil update trunk   ;# latest trunk check-in
fossil update release ;# latest official release
# 获取最新commit的话应该用update trunk
aosp@dell-PowerEdge-T640:~/projects/sql/DBMS/SQLite$ ../fossil-linux-x64-2.19/fossil update trunk
Pull from https://www.sqlite.org/src
Round-trips: 1   Artifacts sent: 0  received: 0
Pull done, wire bytes sent: 313  received: 638  ip: 45.33.6.223
-------------------------------------------------------------------------------
checkout:     73c4c68d3b4c16caf8281dabddd7365d24691e5e 2022-09-09 17:50:29 UTC
tags:         trunk
comment:      Fix harmless compiler warning seen with MSVC. (user: mistachkin)
```

目前的commit id是:`73c4c68d3b4c16caf8281dabddd7365d24691e5e 2022-09-09 17:50:29 UTC`

也可以使用status命令查看commit id:

```shell
aosp@dell-PowerEdge-T640:~/projects/sql/DBMS/SQLite$ ../fossil-linux-x64-2.19/fossil status
repository:   /home/aosp/projects/sql/DBMS/SQLite/sqlite.fossil
local-root:   /home/aosp/projects/sql/DBMS/SQLite/
config-db:    /home/aosp/.config/fossil.db
checkout:     73c4c68d3b4c16caf8281dabddd7365d24691e5e 2022-09-09 17:50:29 UTC
parent:       42105eb43a916a7cd839fa6c582eaffaef17f50b 2022-09-07 20:11:22 UTC
tags:         trunk
comment:      Fix harmless compiler warning seen with MSVC. (user: mistachkin)
```

可以使用branch查看当前分支, 这里位于trunk分支.

## 编译

推荐copy到新目录进行编译, 目录名为commit id前7位.

```shell
./configure
make                     ;#  Run the makefile.
# make sqlite3.c           ;#  Build the "amalgamation" source file
# make test                ;#  Run some tests (requires Tcl)
```

注意检查configure的执行过程中是否报错, 比如我这里提示缺失tclsh:

https://blog.51cto.com/u_13161667/3402969

```shell
sudo apt-get install tcl8.6
sudo apt-get install tcl8.6-dev
```

然而make有大量错误, 尝试用sqlite3.c进行编译:

**sqlite3.c**

根据SQLite文档(https://sqlite.org/src/doc/trunk/README.md)的描述, 推荐使用合并文件sqlite3.c进行编译. sqlite3.c将所有c代码和头文件合并到一个文件中, 有助于编译器做更多编译优化. 据统计, 从sqlite3.c中编译出的sqlite比普通的sqlite快5%.

可以用`make sqlite3.c`构建出合并文件sqlite3.c(只是创建, 不编译).

接着参考文档, 编译sqlite3.c:

https://www.sqlite.org/howtocompile.html

需要以下三个文件:

* sqlite3.c: The SQLite amalgamation source file
* sqlite3.h: The header files that accompanies sqlite3.c and defines the C-language interfaces to SQLite.
* shell.c: The command-line interface program itself. This is the C source code file that contains the definition of the main() routine and the loop that prompts for user input and passes that input into the SQLite database engine for processing. 

执行`make sqlite3.c`时上述3个文件就已生成.

接着执行下面的命令完成编译(需要pthread多线程库和dl动态加载库):

```shell
gcc shell.c sqlite3.c -lpthread -ldl -lm -o sqlite3
```

编译产物为当前目录下的sqlite3, 完成!

# MySQL

https://dev.mysql.com/doc/mysql-sourcebuild-excerpt/8.0/en/

## 安装官方构建好的产物

### 下载

首先先下个构建好的产物, 在docs/INFO_BIN里看一下如何编译, 编译选项的配置会影响产品的正确性, 比较重要.

https://dev.mysql.com/doc/refman/8.0/en/binary-installation.html

从tar中安装MySQL(安装完整版mysql-VERSION-OS.tar.xz, 不要安最小版本mysql-VERSION-OS-GLIBCVER-ARCH-minimal.tar.xz):

> 注意:
>
> 如果之前用apt安装过mysql, 需要完全卸载. 删除/etc/my.cnf, /etc/mysql等文件. <font color="red">这里为避免冲突使用docker隔离.</font>
>
> apt-cache search libaio # search for info
>
> apt-get install libaio1 # install library

mysql server, 或者说mysqld是数据库服务, 管理硬盘/内存数据的访问, 核心. mysql client负责连接mysql server, 使用mysql server提供的服务. 这里我们需要下载https://dev.mysql.com/downloads/的MySQL Community Server.

这里下载了mysql-8.0.30-linux-glibc2.12-x86_64.tar.xz

### 配置容器

开启容器(为了能够正常使用apt, 先配置一下代理: https://blog.csdn.net/m0_59092234/article/details/123873682, 进去以后先apt update一下):

```shell
docker run -itd -e HTTP_PROXY=http://127.0.0.1:8889 -e HTTPS_PROXY=https://127.0.0.1:8889 -e NO_PROXY=127.0.0.1 -p 13306:3306 --name mysql-8.0.30-linux-glibc2.12-x86_64 --privileged=true ubuntu
```

将压缩文件拷贝到容器的/usr/local下:

```shell
sudo docker cp mysql-8.0.30-linux-glibc2.12-x86_64.tar.xz 86370c428cf6:/usr/local
```

容器里的tar可能不支持xz, 建议在外面解压, 然后压缩成tar, 就能在容器里正常解压了.

```shell
tar -xvf mysql-8.0.30-linux-glibc2.12-x86_64.tar
```

解压后的内容为:

![image-20220912145425008](DBMS%20repository.assets/image-20220912145425008.png)

之前介绍的官方编译选项在docs/INFO_BIN中 <font color="red">这里其实配置cmake的-DBUILD_CONFIG=mysql_release就可以使用官方配置了.</font>

为了方便创建符号链接:

```shell
ln -s /usr/local/mysql-8.0.30-linux-glibc2.12-x86_64 mysql
```

### 安装依赖

```shell
apt update
apt-get install -y libaio1
apt install -y lsof
apt install -y vim
# bin/mysqld --initialize-insecure  --user=root依赖的库:
apt install -y libnuma1
apt install -y libnuma-dev
# ./mysql -u root --skip-password依赖的库:
# https://stackoverflow.com/questions/48674104/clang-error-while-loading-shared-libraries-libtinfo-so-5-cannot-open-shared-o
apt install -y libncurses5
```

### Mysql初始化

创建mysql用户组与用户(<font color="green">这里好像不是必要的, 因为是在容器里后面我们都会用root用户</font>):

```shell
root@86370c428cf6:/usr/local# groupadd mysql
root@86370c428cf6:/usr/local# useradd -r -g mysql -s /bin/false mysql
```

接下来进行一些安装后的设置, 包括权限, 数据目录, 启动mysql server, 设置配置文件等.

https://dev.mysql.com/doc/refman/8.0/en/postinstallation.html

主要做这几件事情:

* 初始化数据目录并创建Mysql授权表. APT安装的MySQL会自动完成这一步.
* 启动mysql server.
* 若数据目录初始化时没给root分配密码, 这里需要为其创建密码(可选, 为了方便测试推荐root无密码).

#### 初始化数据目录

https://dev.mysql.com/doc/refman/8.0/en/data-directory-initialization.html

> 注意, 8.0中, root@localhost的密码默认使用 caching_sha2_password, 而不是mysql_native_password

```shell
cd /usr/local/mysql
# 根据secure_file_priv系统变量, 数据库的import和export操作必须要在特定的目录下进行, 创建相关目录:
mkdir mysql-files
# 相关用户授权, 这里由于是在容器里, 直接用root用户, 就不用mysql用户了
chown root:root mysql-files
&& chmod 750 mysql-files
# 初始化数据目录, 创建root@localhost, 创建数据目录, 创建一些表
bin/mysqld --initialize-insecure  --user=root
# 这里可以用--initialize和--initialize-insecure, 前者创建的root用户有初始密码, 初始密码在控制台打印, 识别起来比较麻烦, 因此采用insecure模式, 不生成初始密码.
# 通过user给指定用户授权, 这里由于在容器里就直接用root了, 不用mysql
# 如果mysql无法确定安装目录和数据目录的正确位置, 需要手动指定:
#  --basedir=/opt/mysql/mysql
#  --datadir=/opt/mysql/mysql/data
# 或者在/opt/mysql/mysql/etc/my.cnf中指定:
#  [mysqld]
#  basedir=/opt/mysql/mysql
#  datadir=/opt/mysql/mysql/data
# 然后使用这个cnf:
# --defaults-file=/opt/mysql/mysql/etc/my.cnf
```

#### 启动mysql server

我们不是apt安装的, 不支持systemctl, 这里使用mysqld_safe启动:

```shell
root@6e325b94540e:/usr/local/mysql/bin# ./mysqld_safe --user=root &
[1] 991
root@6e325b94540e:/usr/local/mysql/bin# 2022-09-12T09:30:41.224704Z mysqld_safe Logging to '/usr/local/mysql/data/6e325b94540e.err'.
2022-09-12T09:30:41.259160Z mysqld_safe Starting mysqld daemon with databases from /usr/local/mysql/data

# ps看一下
root@6e325b94540e:/usr/local/mysql/bin# ps -ef | grep mysqld
root        991      9  0 09:30 pts/1    00:00:00 /bin/sh ./mysqld_safe --user=root

# lsof 3306看一下
root@6e325b94540e:/usr/local/mysql/bin# lsof -i:3306
COMMAND  PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
mysqld  1066 root   23u  IPv6 7323264      0t0  TCP *:3306 (LISTEN)
```

同样, 这里user为了方便直接用root, 不用mysql

#### 修改root用户密码(可选)

由于上面用了--initialize-insecure, 这里要用--skip-password登陆root用户:

```shell
root@6e325b94540e:/usr/local/mysql/bin# ./mysql -u root --skip-password
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.30 MySQL Community Server - GPL

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.00 sec)
```

修改密码:

```shell
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

再次登陆--skip-password就失效了, 要用-p 123456.

### 配置远程登陆

<font color="red">这里创建个新的用户, 给所有权限, 配置远程连接.</font>

```shell
USE mysql;
CREATE USER 'hzy'@'%' IDENTIFIED BY '123';
# DBA的话在后面加WITH GRANT OPTION, 一般不用
GRANT ALL PRIVILEGES ON *.* TO 'hzy'@'%';
```

**补充: 通过脚本配置用户**

```shell
# 为了避免输入密码, 还是推荐root无密码登陆.
mysql -u root --skip-password < test.sql

#test.sql, 提前docker cp到容器内部:
USE mysql;
CREATE USER 'hzy'@'%' IDENTIFIED BY '123';
# DBA的话在后面加WITH GRANT OPTION, 一般不用
GRANT ALL PRIVILEGES ON *.* TO 'hzy'@'%';
```

外部测试一下, mysql -h 1270.0.1 -P 13306(自己设置的容器端口映射) -u hzy -p 123, 是成功的.

## 编译安装源码

### 编译

github地址:

https://github.com/mysql/mysql-server

使用8.0分支的commit  fbdaa4def30d269bc4de5b85de61de34b11c0afc  on 7 Jul 2022

推荐把当前commit导出, 不包括.git, 单独编译:

```shell
rsync -a --exclude ".git"  mysql-server/ mysql-server-8.0-fbdaa4d
```

然后编译出类似上面那样的二进制文件:

```shell
mkdir build
cd build
# 需要安装gcc-8, g++-8
# -DBUILD_CONFIG=mysql_release: 使用和release一样的编译选项
# -DCPACK_MONOLITHIC_INSTALL=1: make package只生成一个压缩包, 不过不加的话一般也就一个
cmake -DBUILD_CONFIG=mysql_release -DCPACK_MONOLITHIC_INSTALL=1 ../
# 错误:需要安装boost库
cmake -DBUILD_CONFIG=mysql_release -DDOWNLOAD_BOOST=1 -DWITH_BOOST=../../boost/ ../
...
-- Downloading boost_1_77_0.tar.bz2 to /home/aosp/projects/sql/DBMS/MySQL/boost
-- [download 0% complete]
-- [download 1% complete]
...
# 编译, 不加-j是串行编译, 非常慢
make -j 96
# 22:00~22:10, 10分钟
# 大小:5.2GB
# 打包成tar.gz
make package
```

现在可以在目录下看到` mysql-8.0.30-linux-x86_64.tar.gz`, 接着按照上述方式安装即可.

<font color="red">注意, 编译出来的mysql的lib里没有libssl.so.1.1以及libcrypto.so.1.1, 我们从mysql提供的编译产物中提出这两个库, 导入自己编译出来的lib里面. 同时配置LD_LIBRARY_PATH为mysql的lib/private.</font>

<font color="red">为了方便, 我们将整个过程做成一个dockerfile. </font>

### dockerfile

#### mysql-env

```dockerfile
FROM ubuntu

COPY create_user_hzy.sql /usr/local/mysql-env/
COPY libcrypto.so.1.1 /usr/local/mysql-env/
COPY libssl.so.1.1 /usr/local/mysql-env/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/mysql-env/

COPY mysql-init.sh /usr/local/mysql-env/

RUN echo "create mysql-env" \
&& apt update \
&& apt install -y libaio1 \
&& apt install -y lsof \
&& apt install -y vim \
&& apt install -y libnuma1 \
&& apt install -y libnuma-dev \
&& apt install -y libncurses5 \
&& chmod 777 /usr/local/mysql-env/mysql-init.sh
```

mysql-init.sh:

```shell
cd /usr/local
ln -s /usr/local/mysql-8.0.30-linux-x86_64 mysql
cd mysql
mkdir mysql-files
chown root:root mysql-files
chmod 750 mysql-files
cd bin
./mysqld --initialize-insecure --user=root
./mysqld_safe --user=root &
sleep 3s
./mysql -u root --skip-password < /usr/local/mysql-env/create_user_hzy.sql
```

create_user_hzy.sql

```sql
USE mysql;
CREATE USER 'hzy'@'%' IDENTIFIED BY '123';
GRANT ALL PRIVILEGES ON *.* TO 'hzy'@'%';
```

build.sh:

```shell
sudo docker build -t mysql-env:v1 .
```

#### mysql-server-xxx-xxx

```dockerfile
FROM mysql-env:v1

ADD mysql-8.0.30-linux-x86_64.tar.gz /usr/local/

RUN /usr/local/mysql-env/mysql-init.sh

CMD /usr/local/mysql/bin/mysqld_safe --user=root
```

build.sh:

```shell
sudo docker build -t docker-mysql-8.0-fbdaa4d .
```

run.sh

```shell
sudo docker run -itd -e HTTP_PROXY=http://127.0.0.1:8889 -e HTTPS_PROXY=https://127.0.0.1:8889 -e NO_PROXY=127.0.0.1 --name mysql-8.0-fbdaa4d -p 13306:3306 --privileged=true docker-mysql-8.0-fbdaa4d
```

## 官方docker镜像

```shell
sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30
```

# OceanBase

OceanBase: https://github.com/oceanbase/oceanbase

**branch:** master, **commit id:** 053d54bc59144169a0ecf26e694415af4991bada (Sep 21, 2022)

## 编译

https://github.com/oceanbase/oceanbase/wiki/Build-from-source-code

```shell
apt-get install -y git wget rpm rpm2cpio cpio make build-essential binutils m4
or yum install -y git wget rpm* cpio make glibc-devel glibc-headers binutils m4
```

编译rpm

```shell
bash build.sh rpm --init && cd build_rpm && make -j16 rpm
```

编译release:

```
sh build.sh init
# Run the predefined command for building the release version in the source code directory.
sh build.sh release

# Enter the generated directory for building the release edition.
cd build_release

# Start building.
make -j{N} observer

# Check the product.
stat src/observer/observer
```

## 从rpm包安装

https://open.oceanbase.com/quickStart

https://www.oceanbase.com/en/docs/community-obd-en-10000000000213146

https://blog.csdn.net/carefree2005/article/details/125408455

制作dockerfile

### oceanbase-env

```dockerfile
FROM centos

COPY create_user_hzy.sql /usr/local/oceanbase-env/

RUN echo "create oceanbase-env" \
&& sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-* \
&& sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.epel.cloud|g' /etc/yum.repos.d/CentOS-Linux-* \
&& yum update -y \
&& yum install -y lsof \
&& yum install -y vim \
&& yum install -y yum-utils \
&& yum-config-manager --add-repo https://mirrors.aliyun.com/oceanbase/OceanBase.repo \
&& sudo yum install -y ob-deploy \
&& sudo yum install -y obclient
&& mkdir /usr/local/oceanbase
```

### oceanbase-xxx-xxx

```dockerfile
FROM oceanbase-env:v1

COPY oceanbase-ce-3.1.5-1.x86_64.rpm /usr/local
COPY oceanbase-ce-devel-3.1.5-1.x86_64.rpm /usr/local
COPY oceanbase-ce-libs-3.1.5-1.x86_64.rpm /usr/local
COPY oceanbase-ce-utils-3.1.5-1.x86_64.rpm /usr/local
COPY quick_start_demo.yaml /usr/local/oceanbase-env/

COPY init.sh /usr/local/oceanbase-env/
COPY start.sh /usr/local/oceanbase-env/

RUN chmod 777 /usr/local/oceanbase-env/init.sh \
&& chmod 777 /usr/local/oceanbase-env/start.sh \s
&& /usr/local/oceanbase-env/init.sh

CMD /usr/local/oceanbase-env/start.sh
```

init.sh:

```shell
obd mirror disable remote
obd mirror clone /usr/local/oceanbase-ce-3.1.5-1.x86_64.rpm
obd mirror clone /usr/local/oceanbase-ce-devel-3.1.5-1.x86_64.rpm
obd mirror clone /usr/local/oceanbase-ce-libs-3.1.5-1.x86_64.rpm
obd mirror clone /usr/local/oceanbase-ce-utils-3.1.5-1.x86_64.rpm
obd cluster deploy myob -c /usr/local/oceanbase-env/quick_start_demo.yaml
obd cluster display myob
obd cluster start myob
obclient -h 127.0.0.1 -P 2881 -u root < /usr/local/oceanbase-env/create_user_hzy.sql
```

start.sh:

```shell
obd cluster display myob
obd cluster start myob
tail -f /dev/null
```

## 官方docker镜像

```shell
sudo docker run -itd --name oceanbasetest -p 2881:2881 oceanbase/oceanbase-ce:4.0.0.0
SET PASSWORD = PASSWORD('123456');
```

启动预计需要 2-5 分钟。执行以下命令，如果返回 boot success!，则启动成功。

```shell
$ docker logs obstandalone | tail -1
boot success!
```

可以用mysql连接.

# MariaDB

https://github.com/MariaDB/server

https://mariadb.org/get-involved/getting-started-for-developers/get-code-build-test/

## 编译

```shell
mkdir build
cd build
cmake ..
make -j 80
```

## 从源码安装(非make install)

https://mariadb.org/get-involved/getting-started-for-developers/get-code-build-test/

### mariadb-env

```dockerfile
FROM ubuntu

COPY create_user_hzy.sql /usr/local/mariadb-env/

RUN echo "create mariadb-env" \
&& apt update \
&& apt install -y lsof \
&& apt install -y vim \
&& apt install -y wget \
&& apt install -y libncurses5 \
&& cd /usr/local/mariadb-env \
&& wget http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb \
&& dpkg -i *.deb
```

### mariadb-xxx-xxx

先把源码连同里面的build打包, 推荐用tar, tar.gz很慢.

```dockerfile
FROM mariadb-env:v1

COPY MariaDB-10.11-49cee4e.tar /usr/local/
COPY mariadb.cnf /root

COPY init.sh /usr/local/mariadb-env/

RUN chmod 777 /usr/local/mariadb-env/init.sh \
&& /usr/local/mariadb-env/init.sh

CMD /usr/local/MariaDB-10.11-49cee4e/build/sql/mariadbd --defaults-file=~/mariadb.cnf --user=root
```

init.sh:

```shell
cd /usr/local
tar -xf MariaDB-10.11-49cee4e.tar
rm MariaDB-10.11-49cee4e.tar
mkdir data
cd MariaDB-10.11-49cee4e/build
./scripts/mariadb-install-db --srcdir=.. --defaults-file=~/mariadb.cnf
./sql/mariadbd --defaults-file=~/mariadb.cnf --user=root &
sleep 3s
./client/mariadb -u root < /usr/local/mariadb-env/create_user_hzy.sql
```

## 官方docker镜像

https://mariadb.com/kb/en/installing-and-using-mariadb-via-docker/

```
sudo docker run -itd --name mariadbtest -p 23306:3306 -e MYSQL_ROOT_PASSWORD=123456 --privileged=true mariadb:10.11.1-rc
```

# TiDB

https://github.com/pingcap/tidb

## 编译

https://pingcap.github.io/tidb-dev-guide/get-started/build-tidb-from-source.html

提前安装好golang

直接`make`即可.

需要用golang1.19

## 安装

tidb是最省心的, 直接运行bin/tidb-server就可以, 默认端口4000, root无密码. 简单做个docker镜像:

### tidb-env

```dockerfile
FROM ubuntu

COPY create_user_hzy.sql /usr/local/tidb-env/

RUN echo "create tidb-env" \
&& apt update \
&& apt install -y lsof \
&& apt install -y vim \
&& apt install -y default-mysql-client
```

### tidb-xxx-xxx

```dockerfile
FROM tidb-env:v1

COPY tidb-server /usr/local/

COPY init.sh /usr/local/tidb-env/

RUN chmod 777 /usr/local/tidb-env/init.sh \
&& /usr/local/tidb-env/init.sh

CMD /usr/local/tidb-server
```

init.sh:

```shell
cd /usr/local
./tidb-server &
sleep 6s
mysql -h 127.0.0.1 -P 4000 -u root < /usr/local/tidb-env/create_user_hzy.sql
```

## 官方docker镜像

https://developer.aliyun.com/article/138312

```shell
sudo docker run -itd --name tidbtest -p 4000:4000 pingcap/tidb:v6.4.0
SET PASSWORD = '123456'
```

