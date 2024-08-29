# Airflow-ENV-Docker-for-MINIO-TRINO

## Setup Airflow 

First, clone my project to local:
```bash
git clone https://github.com/thinh661/airflow_lightweight_docker_env
```

Build image (if you update pakage Python enviroment):
``` bash
docker image build
```

Then, Pull and run all services with:

```bash
docker-compose up
```

## Run Airflow Web UI

Run airflow UI on port 8080 : `http://locahost:8088`
Login with:
```
admin : admin
password : admin
```

## Connect TRINO-MINIO
Because the MinIO env I connected in Dockerfile.
We'll connect the Trino conections:

1. Find `Connections` in `Admin` and `Add a new records`
2. Config with params:
- Connection Id: trino_default
- Connection Type: Trino
- Host: trino-minio-docker-trino-1
- Login: admin
- Port: 8088
3. Save it and you can connect to Trino and get data from MinIO by SQL 

## ETL by Airflow

1. Airflow WebUI has a few examples I've done before and you can see it. U can run it (some DAG must trigger to run) to understand the flow if u has the [TRINO-MINIO_DOCKER](https://github.com/thinh661/minio_trino_docker_evn.git) eviroment I'm deployed.
2. In `dags` folder, has a few examples, and you can deverlop it by add DAG python file

## END


