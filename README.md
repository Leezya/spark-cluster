# Hadoop + Spark Docker Cluster with ZeroTier

This project runs a distributed data-processing cluster using:

* **Hadoop HDFS** — distributed storage
* **Apache Spark** — distributed data processing
* **Spark Master** — Spark cluster manager
* **Spark Worker** — compute node
* **Docker** — containerization
* **ZeroTier** — virtual network for communication between machines
* **PySpark** — Python API for Spark jobs

---

# 1. Architecture

The cluster uses **ZeroTier** as the network connecting the physical machines.

The Hadoop Master and Spark Master machine has the following ZeroTier IP:

```text
10.68.71.113
```

Therefore, other machines in the ZeroTier network can communicate with the Hadoop Master and Spark Master using:

```text
10.68.71.113
```

Architecture:

```text
                         ZeroTier Network
                         10.68.71.0/24
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
             ▼                                     ▼
      SERVER 1                               SERVER 2
  ZeroTier IP:                              ZeroTier IP:
  10.68.71.113                              10.68.71.xxx
             │                                     │
      ┌──────┴──────┐                       ┌──────┴──────┐
      │             │                       │             │
      ▼             ▼                       ▼             ▼
 Hadoop Master  Spark Master           Hadoop Worker  Spark Worker
      │             │                       │             │
      │             │                       │             │
      │             └─────── :7077 ─────────┘             │
      │                     Spark                         │
      │                                                   │
      └──────────────── HDFS :8020 ───────────────────────┘
```

---

# 2. Network Configuration

ZeroTier provides a virtual network between the machines.

Instead of using the local LAN IP:

```text
192.168.80.227
```

the cluster uses the ZeroTier IP:

```text
10.68.71.113
```

This is especially useful when the machines are:

* On different physical networks
* Connected through different routers
* Not in the same LAN
* Located in different locations

The machines communicate through the ZeroTier virtual network.

---

# 3. ZeroTier IP Address

The Hadoop Master and Spark Master machine:

```text
ZeroTier IP:

10.68.71.113
```

This IP should be used for services that need to be accessed by other machines.

For example:

### Hadoop NameNode RPC

```text
10.68.71.113:8020
```

### Hadoop NameNode Web UI

```text
http://10.68.71.113:9870
```

### Spark Master

```text
spark://10.68.71.113:7077
```

### Spark Master Web UI

```text
http://10.68.71.113:8080
```

---

# 4. Verify ZeroTier Connection

On every machine, check the ZeroTier interface:

```bash
ip addr
```

or:

```bash
ip -br addr
```

You should see a ZeroTier interface with an IP similar to:

```text
10.68.71.xxx
```

For example, the Master machine:

```text
10.68.71.113
```

---

# 5. Test ZeroTier Connectivity

From the Spark Worker / Hadoop Worker machine:

```bash
ping 10.68.71.113
```

Example:

```text
PING 10.68.71.113
64 bytes from 10.68.71.113
64 bytes from 10.68.71.113
64 bytes from 10.68.71.113
```

If the ping works, the machines can communicate through ZeroTier.

However, ping alone does not guarantee that Hadoop or Spark ports are accessible.

---

# 6. Test Hadoop NameNode Port

From a Worker machine:

```bash
nc -zv 10.68.71.113 8020
```

Expected:

```text
Connection to 10.68.71.113 8020 port [tcp/*] succeeded!
```

---

# 7. Test Spark Master Port

From a Spark Worker machine:

```bash
nc -zv 10.68.71.113 7077
```

Expected:

```text
Connection to 10.68.71.113 7077 port [tcp/*] succeeded!
```

This is important because Spark Worker must be able to connect to the Spark Master.

---

# 8. Hadoop Configuration with ZeroTier

The Hadoop cluster should use:

```text
10.68.71.113
```

as the NameNode address.

For example:

```text
hdfs://10.68.71.113:8020
```

Therefore, Spark jobs can access HDFS using:

```text
hdfs://10.68.71.113:8020/data/input
```

---

# 9. Spark Master Configuration

The Spark Master should advertise its ZeroTier IP:

```text
10.68.71.113
```

Docker Compose:

```yaml
services:

  spark-master:
    image: apache/spark:3.5.3

    container_name: spark-master

    hostname: spark-master

    command: >
      /opt/spark/bin/spark-class
      org.apache.spark.deploy.master.Master
      --host 10.68.71.113
      --port 7077
      --webui-port 8080

    ports:
      - "7077:7077"
      - "8080:8080"

    volumes:
      - ./jobs:/opt/spark/jobs

    restart: unless-stopped
```

The important configuration is:

```yaml
--host 10.68.71.113
--port 7077
```

The Spark Master URL becomes:

```text
spark://10.68.71.113:7077
```

---

# 10. Start Spark Master

Run:

```bash
docker compose -f docker-compose-master.yml up -d
```

Check:

```bash
docker ps
```

Check logs:

```bash
docker logs spark-master
```

You should see the Spark Master running on:

```text
10.68.71.113:7077
```

---

# 11. Spark Master Web UI

Open:

```text
http://10.68.71.113:8080
```

The Spark Master UI should show:

```text
URL: spark://10.68.71.113:7077
```

When a Worker connects, it should appear in the Workers section.

---

# 12. Spark Worker Configuration

The Spark Worker is independent from the Spark Master.

It connects to:

```text
spark://10.68.71.113:7077
```

Example:

```yaml
services:

  spark-worker:
    image: apache/spark:3.5.3

    container_name: spark-worker

    hostname: spark-worker

    command: >
      /opt/spark/bin/spark-class
      org.apache.spark.deploy.worker.Worker
      spark://10.68.71.113:7077
      --webui-port 8081

    ports:
      - "8081:8081"

    restart: unless-stopped
```

Notice:

```text
spark://10.68.71.113:7077
```

instead of:

```text
spark://spark-master:7077
```

The ZeroTier IP is used because the Worker may be running on another physical machine.

---

# 13. Start Spark Worker

On the Worker machine:

```bash
docker compose -f docker-compose-worker.yml up -d
```

Check:

```bash
docker ps
```

Check logs:

```bash
docker logs spark-worker
```

If successful, the Worker registers with:

```text
Spark Master:

10.68.71.113:7077
```

---

# 14. Verify Spark Cluster

Open:

```text
http://10.68.71.113:8080
```

The Spark Master should show the Worker.

For example:

```text
Workers: 1

Worker ID:
worker-...

Address:
10.68.71.xxx

Status:
ALIVE
```

---

# 15. Spark Jobs Directory

The project uses a `jobs/` directory:

```text
spark-cluster/
│
├── docker-compose-master.yml
├── docker-compose-worker.yml
│
├── jobs/
│   ├── test.py
│   ├── hdfs_test.py
│   └── wordcount.py
│
└── README.md
```

The Master Compose mounts:

```yaml
volumes:
  - ./jobs:/opt/spark/jobs
```

Therefore:

```text
Host
│
└── jobs/
      │
      └── test.py
              │
              │ Docker volume
              ▼
Container
│
└── /opt/spark/jobs/test.py
```

---

# 16. Example Spark Job

Create:

```bash
nano jobs/test.py
```

Use:

```python
from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("TestSparkJob") \
    .getOrCreate()


data = [
    ("Alice", 20),
    ("Bob", 25),
    ("Charlie", 30),
    ("David", 35)
]

df = spark.createDataFrame(
    data,
    ["name", "age"]
)


print("===== DATA =====")

df.show()


print("===== AVERAGE AGE =====")

df.selectExpr(
    "avg(age) as average_age"
).show()


spark.stop()
```

---

# 17. Submit Spark Job

The Spark Master machine can submit the job using:

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  --conf spark.driver.host=10.68.71.113 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.driver.port=4041 \
  --conf spark.blockManager.port=4042 \
  /opt/spark/jobs/test.py
```

The important part is:

```text
--master spark://10.68.71.113:7077
```

This tells Spark:

```text
Submit the application to:

Spark Master
     │
     └── 10.68.71.113:7077
```

---

# 18. Job Execution Workflow

The complete Spark workflow is:

```text
Developer
    │
    │ spark-submit
    ▼
┌────────────────────────────┐
│       Spark Master         │
│                            │
│ 10.68.71.113:7077          │
│ Web UI :8080               │
└────────────┬───────────────┘
             │
             │ schedule application
             ▼
┌────────────────────────────┐
│       Spark Worker         │
│                            │
│ ZeroTier: 10.68.71.xxx     │
│ Web UI :8081               │
└────────────┬───────────────┘
             │
             │ launch
             ▼
        ┌───────────┐
        │ Executor  │
        └─────┬─────┘
              │
              │ execute tasks
              ▼
          Spark Job
```

---

# 19. Spark + Hadoop HDFS Workflow

When the Spark application needs data from HDFS:

```text
                         ZeroTier
                            │
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
      Spark Master                     Hadoop Master
      10.68.71.113                    10.68.71.113
          :7077                            :8020
            │                               │
            │                               │
            ▼                               ▼
      Spark Worker                    Hadoop DataNode
            │                               │
            │                               │
            └──────────────┬────────────────┘
                           │
                           ▼
                         HDFS
```

Spark reads data using:

```text
hdfs://10.68.71.113:8020
```

For example:

```text
hdfs://10.68.71.113:8020/data/input/data.csv
```

---

# 20. Example: Read HDFS with PySpark

Create:

```bash
nano jobs/hdfs_test.py
```

Use:

```python
from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("HDFSExample") \
    .getOrCreate()


input_path = (
    "hdfs://10.68.71.113:8020"
    "/data/input/data.csv"
)


df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)


print("===== DATA =====")

df.show()


print("===== SCHEMA =====")

df.printSchema()


spark.stop()
```

Submit:

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  --conf spark.driver.host=10.68.71.113 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.driver.port=4041 \
  --conf spark.blockManager.port=4042 \
  /opt/spark/jobs/test.py
```

---

# 21. Example: Read and Write HDFS

Spark can read data from HDFS, process it, and write the result back to HDFS.

Example:

```python
from pyspark.sql import SparkSession


spark = SparkSession.builder \
    .appName("HDFSProcessing") \
    .getOrCreate()


input_path = (
    "hdfs://10.68.71.113:8020"
    "/data/input/data.csv"
)

output_path = (
    "hdfs://10.68.71.113:8020"
    "/data/output"
)


df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(input_path)


result = df.groupBy("category").count()


result.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)


spark.stop()
```

Workflow:

```text
HDFS
 │
 │ read
 ▼
Spark Worker
 │
 │ process
 ▼
Spark Executor
 │
 │ write
 ▼
HDFS
```

---

# 22. Create HDFS Directory

Create an input directory:

```bash
hdfs dfs -mkdir -p /data/input
```

Check:

```bash
hdfs dfs -ls /data
```

Upload data:

```bash
hdfs dfs -put data.csv /data/input/
```

Check:

```bash
hdfs dfs -ls /data/input
```

---

# 23. Submit Job from Spark Master

The recommended command is:

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  --conf spark.driver.host=10.68.71.113 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.driver.port=4041 \
  --conf spark.blockManager.port=4042 \
  /opt/spark/jobs/test.py
```

For HDFS:

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  --conf spark.driver.host=10.68.71.113 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.driver.port=4041 \
  --conf spark.blockManager.port=4042 \
  /opt/spark/jobs/test.py
```

---

# 24. Monitor Spark Applications

Open the Spark Master UI:

```text
http://10.68.71.113:8080
```

You can monitor:

* Workers
* Applications
* Application status
* CPU cores
* Memory
* Running applications
* Completed applications

Worker UI:

```text
http://WORKER-ZEROTIER-IP:8081
```

---

# 25. Test the Network Before Running Spark

Before starting the Spark Worker, test:

```bash
ping 10.68.71.113
```

Then:

```bash
nc -zv 10.68.71.113 7077
```

For Hadoop:

```bash
nc -zv 10.68.71.113 8020
```

Expected:

```text
Connection succeeded
```

If port `7077` cannot be reached, the Spark Worker cannot register with the Spark Master.

If port `8020` cannot be reached, Spark cannot communicate with the Hadoop NameNode through that address.

---

# 26. Firewall

If the machines use `ufw`, check:

```bash
sudo ufw status
```

The Spark Master machine must allow communication to:

```text
7077/tcp
```

The Hadoop NameNode machine must allow:

```text
8020/tcp
```

The Web UIs use:

```text
8080/tcp
9870/tcp
```

The Worker Web UI uses:

```text
8081/tcp
```

For a multi-machine Spark cluster, additional Spark worker/executor ports may also need to be reachable depending on the network configuration.

---

# 27. Important: Docker and ZeroTier

ZeroTier runs on the **host machine**, while Spark and Hadoop run inside Docker containers.

Therefore, there are two different network layers:

```text
Physical Machine
│
├── ZeroTier
│      │
│      └── 10.68.71.113
│
└── Docker
       │
       └── Spark / Hadoop containers
```

Do not assume that the Docker hostname:

```text
spark-master
```

can be resolved by a container on another physical machine.

For multi-machine communication, use the reachable ZeroTier address:

```text
10.68.71.113
```

For example:

```text
Spark:

spark://10.68.71.113:7077


HDFS:

hdfs://10.68.71.113:8020
```

---

# 28. Complete Startup Workflow

## Hadoop Master

Start Hadoop Master first:

```bash
docker compose up -d master
```

Check:

```bash
docker ps
```

---

## Hadoop Worker

On the Worker machine:

```bash
docker compose up -d worker
```

Check:

```bash
docker logs worker
```

---

## Spark Master

On the machine with ZeroTier IP `10.68.71.113`:

```bash
docker compose -f docker-compose-master.yml up -d
```

Check:

```bash
docker logs spark-master
```

---

## Spark Worker

On the Worker machine:

```bash
docker compose -f docker-compose-worker.yml up -d
```

Check:

```bash
docker logs spark-worker
```

---

## Check Spark Master

Open:

```text
http://10.68.71.113:8080
```

Verify that the Spark Worker is:

```text
ALIVE
```

---

## Submit Job

Finally:

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  /opt/spark/jobs/test.py
```

---

# 29. Final Cluster

The final cluster is:

```text
                         ZeroTier
                    10.68.71.0/24
                             │
              ┌──────────────┴──────────────┐
              │                             │
              │                             │
              ▼                             ▼
       MASTER MACHINE                 WORKER MACHINE
       10.68.71.113                   10.68.71.xxx
              │                             │
      ┌───────┴────────┐            ┌───────┴────────┐
      │                │            │                │
      ▼                ▼            ▼                ▼
 Hadoop Master    Spark Master   Hadoop Worker   Spark Worker
      │                │            │                │
      │                │            │                │
      │             :7077           │                │
      │                │            │                │
      │                └────────────┤────────────────┘
      │                             │
      │                             │
      │          HDFS :8020         │
      └────────────────────────────┘
                    │
                    ▼
                  HDFS


Spark Job:

jobs/test.py
     │
     │ spark-submit
     ▼
Spark Master
10.68.71.113:7077
     │
     ▼
Spark Worker
     │
     ▼
Executor
     │
     │ read/write
     ▼
HDFS
10.68.71.113:8020
```

---

# 30. Quick Commands

### Check containers

```bash
docker ps
```

### Start Spark Master

```bash
docker compose -f docker-compose-master.yml up -d
```

### Stop Spark Master

```bash
docker compose -f docker-compose-master.yml down
```

### Start Spark Worker

```bash
docker compose -f docker-compose-worker.yml up -d
```

### Stop Spark Worker

```bash
docker compose -f docker-compose-worker.yml down
```

### Master logs

```bash
docker logs -f spark-master
```

### Worker logs

```bash
docker logs -f spark-worker
```

### Test ZeroTier

```bash
ping 10.68.71.113
```

### Test Spark Master

```bash
nc -zv 10.68.71.113 7077
```

### Test Hadoop NameNode

```bash
nc -zv 10.68.71.113 8020
```

### Submit PySpark job

```bash
docker exec -it spark-master \
  /opt/spark/bin/spark-submit \
  --master spark://10.68.71.113:7077 \
  --conf spark.driver.host=10.68.71.113 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.driver.port=4041 \
  --conf spark.blockManager.port=4042 \
  /opt/spark/jobs/test.py
```

### Spark Master UI

```text
http://10.68.71.113:8080
```

### Hadoop NameNode UI

```text
http://10.68.71.113:9870
```

---

# 31. Key Addresses

| Service             | Address                     |
| ------------------- | --------------------------- |
| ZeroTier Master     | `10.68.71.113`              |
| Hadoop NameNode RPC | `10.68.71.113:8020`         |
| Hadoop NameNode UI  | `http://10.68.71.113:9870`  |
| Spark Master        | `spark://10.68.71.113:7077` |
| Spark Master UI     | `http://10.68.71.113:8080`  |
| Spark Worker        | `WORKER-ZEROTIER-IP:8081`   |

The most important addresses are:

```text
HDFS:
hdfs://10.68.71.113:8020

Spark:
spark://10.68.71.113:7077
```
