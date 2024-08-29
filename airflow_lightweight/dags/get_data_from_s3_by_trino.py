from airflow import DAG
from airflow.decorators import task
from airflow.providers.trino.hooks.trino import TrinoHook
from datetime import datetime
import pandas as pd
import os
from minio import Minio
import pyarrow.parquet as pq
import pyarrow as pa
import io

# Thông tin MinIO
minio_endpoint = 'minio:9000'
minio_access_key = 'minio_access_key'
minio_secret_key = 'minio_secret_key'
source_bucket_name = 'stock-data'
destination_bucket_name = 'iris'
source_file_name = 'all_stock_data_part1.parquet'
destination_file_name = 'stock-data-part1_100.parquet'

# Tạo kết nối đến MinIO
minio_client = Minio(
    minio_endpoint,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False
)

# Định nghĩa DAG với Decorator
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    dag_id='trino_to_parquet_minio',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    @task
    def create_schema_and_table():
        trino_hook = TrinoHook(trino_conn_id='trino_default')
        conn = trino_hook.get_conn()
        cursor = conn.cursor()

        # Tạo schema trực tiếp trên MinIO
        cursor.execute("CREATE SCHEMA IF NOT EXISTS minio.stock WITH (location = 's3a://stock-data/')")
        
        # Tạo bảng
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS minio.stock.stock_day_table (
            time VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            symbol VARCHAR
        )
        WITH (
            format = 'PARQUET',
            external_location = 's3a://{source_bucket_name}/'
        )
        """
        cursor.execute(create_table_query)

    @task
    def trino_to_parquet_and_upload():
        trino_hook = TrinoHook(trino_conn_id='trino_default')
        sql_query = f"""
        SELECT * 
        FROM minio.stock.stock_day_table
        LIMIT 100
        """

        conn = trino_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()

        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        table = pa.Table.from_pandas(df)
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)

        minio_client.put_object(
            destination_bucket_name,
            destination_file_name,
            buffer,
            length=buffer.getbuffer().nbytes,
            part_size=10 * 1024 * 1024,
            content_type='application/octet-stream',
            metadata=None
        )

    # Thực thi các task
    create_schema_and_table() >> trino_to_parquet_and_upload()
