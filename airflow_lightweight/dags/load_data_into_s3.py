from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pandas as pd
import os
from minio import Minio

# Đường dẫn đến thư mục chứa file CSV
csv_file_path = '/opt/airflow/data/day/all_stock_data_2021_to_present.csv'  

# Thông tin MinIO
minio_endpoint = 'minio:9000'  # Sử dụng tên dịch vụ MinIO trong Docker Compose
minio_access_key = 'minio_access_key'
minio_secret_key = 'minio_secret_key'
minio_bucket_name = 'stock-data-day'

# Tạo kết nối đến MinIO
minio_client = Minio(
    minio_endpoint,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False  # Nếu kết nối qua HTTPS, thì sửa thành `secure=True`
)

# Định nghĩa DAG với Decorator
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    dag_id='csv_to_parquet_minio_no_partition',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Task: Chuyển đổi file CSV sang Parquet và upload lên MinIO
    @task
    def csv_to_parquet_and_upload():
        df = pd.read_csv(csv_file_path)
        
        # Lưu file dưới dạng Parquet
        parquet_file = csv_file_path.replace('.csv', '.parquet')
        df.to_parquet(parquet_file, engine='pyarrow')
        
        # Upload lên MinIO
        with open(parquet_file, 'rb') as file:
            minio_client.put_object(
                minio_bucket_name,
                os.path.basename(parquet_file),
                file,
                length=os.path.getsize(parquet_file),  # Xác định kích thước file
                part_size=10 * 1024 * 1024,
                content_type='application/octet-stream',  # Xác định loại nội dung
                metadata=None
            )
        os.remove(parquet_file)  # Xóa file parquet sau khi upload

    # Gọi Task
    csv_to_parquet_and_upload()

