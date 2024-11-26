This document illustrates how to create and run Docker images to build databases(clickhouse, duckdb, mariadb, monetdb, mysql, postgres, sqlite, tidb)  for QTRAN. Follow these steps to replicate the environment.
## Docker
Ensure you have the latest version of Docker installed.
## Step 1: Create and Run Docker Images

1. Navigate to the QTRAN Director
    
    Change to the `QTRAN` directory where the example is located:
    
    ```shell
    cd QTRAN
    ```
    
2. Build the Docker Image
    
    In `QTRAN` directory, build the image using the Dockerfile:
    
    ```shell
    docker-compose up --build -d
    ```

## Step 2: Run Docker Images

Start container instancs with the following command:

```shell
docker-compose up -d
```

## Step 3: Database 

Some databases require permission changes or configuration. The specific steps are as follows. Please follow the steps below for configuration.
### ClickHouse

Enter the ClickHouse container:

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

### DuckDB

The official DuckDB does not maintain its image, so we cannot use a Docker container to build it. For DuckDB, it uses a file path (like `<host_file_path>/db_name.duckdb`) to access the database, rather than the typical "host/database" format.

### MariaDB

### MonetDB

Examples of creating and deleting a database:

```
monetdb create PINOLO_MonetDB # Create the database
monetdb release PINOLO_MonetDB # Unlock the permissions so the database can be deleted later
monetdb start PINOLO_MonetDB  # Start the database
monetdb stop PINOLO_MonetDB  # Stop the database

monetdb lock db_name  # Lock the database, then proceed to delete it
monetdb destroy db_name  # Delete the database
```

Log in to the MonetDB database using `mclient` (default username is `monetdb`, default password is `monetdb`):

```
mclient -u monetdb -d PINOLO_MonetDB
```

Change the root password (optional, the default password is `monetdb`, or you can choose not to change it):

```
ALTER USER SET PASSWORD '123456' USING OLD PASSWORD 'monetdb';
```

### MySQL

### PostgreSQL

### SQLite
The database **sqlite** doesn't requiring building.Because almost all versions of Linux operating systems come with SQLite pre-installed, we can directly use the system's built-in version without additional building. Note the following points:

1. **Switching Databases**: SQLite does not require the `USE` statement. You can directly specify the database file path.
2. **Deleting Database Files**: To simulate `DROP DATABASE` in SQLite, you need to delete the `db_name.db` file using file system commands (e.g., `rm db_name.db` in Python, Shell, etc.).
3. **Creating a New Database**: In SQLite, creating a new database means creating a new database file. This can be done by connecting to a new database file `db_name.db` using the SQLite CLI or a program.

### TiDB

1. Download and install TiUP:

```
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
```

If you see the following response, the installation was successful. It shows the absolute path of the Shell profile file `/root/.bashrc` (make a note of this path as it will be used in the next steps).

```
Successfully set mirror to https://tiup-mirrors.pingcap.com
Detected shell: bash
Shell profile:  /root/.bashrc
Installed path: /root/.tiup/bin/tiup
===============================================
Have a try:     tiup playground
===============================================
```

2. Declare the global environment variable, where `{your_shell_profile}` is the absolute path of the Shell profile file obtained in the previous step:

```
source ${your_shell_profile}
```

3. Install the TiUP cluster component:

```
tiup cluster # install
tiup update --self && tiup update cluster # update
```

4. Increase SSHD connection limit for multi-machine deployment simulation by adjusting the SSH service settings:

- Modify `/etc/ssh/sshd_config` to set `MaxSessions` to 20:
    ```
    MaxSessions 20
    ```
- Restart the SSHD service:
    ```sh
    service sshd restart
    sudo systemctl enable ssh.service
    ```
    
5. Create and start the cluster:

    Follow the configuration template below to create the configuration file, named `topo.yaml`. The template and the explanation for its parameters are as follows:
- `user: "tidb"`: This means the internal management of the cluster will be done by the `tidb` system user (which will be automatically created during deployment). The default SSH port is 22 to log into the target machine.
- `replication.enable-placement-rules`: This PD parameter is set to ensure that TiFlash operates properly.
- `host`: Set this to the IP of the current deployment machine. Make sure to replace all `host` entries in the template with the IP of the deployment machine.
- Before proceeding, create the `deploy_dir` and `data_dir` folders under `/home/TiDB`:
```sh
    mkdir -p /home/TiDB/deploy_dir
    mkdir -p /home/TiDB/data_dir
```

 **The configuration template is as follows:**
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
        - host: 127.0.0.1

tidb_servers:
        - host: 127.0.0.1

tikv_servers:
        - host: 127.0.0.1
          port: 20160
          status_port: 20180
          config:
                  server.labels: { host: "logic-host-1" }


        - host: 127.0.0.1
          port: 20161
          status_port: 20181
          config:
                  server.labels: { host: "logic-host-2" }

        - host:127.0.0.1
          port: 20162
          status_port: 20182
          config:
                  server.labels: { host: "logic-host-3" }

tiflash_servers:
        - host: 127.0.0.1

monitoring_servers:
        - host: 127.0.0.1

grafana_servers:
        - host: 127.0.0.1
```

6. Execute the cluster deployment command:

```
tiup cluster deploy tidb_QTRAN 8.3.0 ./topo.yaml --user root -p 123456
```
- The parameter `<cluster-name>` sets the cluster name.
- The parameter `<version>` sets the cluster version, such as `v8.4.0`. You can check the supported TiDB versions for deployment by running `tiup list tidb`.
- The `-p` parameter is used to log in to the target machine using a password.
- If the host uses SSH key authentication, use the `-i` parameter to specify the key file path. Note that `-i` and `-p` cannot be used together.

Follow the prompts, input "y" and the root password to complete the deployment:

```
    Do you want to continue? [y/N]:  y
    Input SSH password:
```

7. Start/Stop the cluster:

```
tiup cluster start tidb_QTRAN --initn # first time
tiup cluster start tidb_QTRAN

tiup cluster stop tidb_QTRAN
```

8. Access the TiDB database with an empty password:

```
mysql -h172.24.89.100 -P 4000 -u root -p
```


## Others
- **Stop all containers**: `docker-compose down`
- **View container status**: `docker-compose ps`
- **View container logs**: `docker-compose logs`
