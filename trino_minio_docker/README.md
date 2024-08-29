# Deploy MinIO and Trino on docker

## First, create the trino-network in docker
```bash
docker create network trino-network
```

## Setup MINIO (run in port 9000)

First, clone my project to local:
```bash
git clone https://github.com/thinh661/minio_trino_docker_evn.git
```

Then, Pull and run all services with:

```bash
docker-compose up
```

Finally, Access to port 9000 and check
Login with:
``` bash
"minio_access_key" : "minio_access_key"
"minio_secret_key" : "minio_secret_key" 
```

If you see the bucket iris and stock-data, you finish setup MINIO

## Setup TRINO (run in port 8088)

start Trino CLI:
```
java -jar "./trino-cli-352-executable.jar --server http://localhost:8088 " (use absolute path if you can't run it)
```

Create schema and create table with: (important: "minio" is schema (iceberg) in Trino)

```bash
./trino --execute "
SHOW SCHEMAS FROM minio;

CREATE SCHEMA IF NOT EXISTS minio.iris
WITH (location = 's3a://iris/');

CREATE TABLE IF NOT EXISTS minio.iris.iris_parquet (
  sepal_length DOUBLE,
  sepal_width  DOUBLE,
  petal_length DOUBLE,
  petal_width  DOUBLE,
  class        VARCHAR
)
WITH (
  external_location = 's3a://iris/',
  format = 'PARQUET'
);"
```

Query the newly created table with:

```bash
./trino --execute "
SHOW TABLES IN minio.iris;
SELECT * FROM minio.iris.iris_parquet LIMIT 5;"
```

And you try create schema for `all_stock_data_part_*.parquet` in MINIO by TRINO.
