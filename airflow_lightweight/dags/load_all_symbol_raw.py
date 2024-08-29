from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pandas as pd
import io
from minio import Minio
from vnstock3 import Vnstock
from minio.error import S3Error

# Kiểm tra file Parquet hiện có
def object_exists(bucket_name, object_name):
    try:
        minio_client.stat_object(bucket_name, object_name)
        return True
    except S3Error as e:
        if e.code == 'NoSuchKey':
            return False
        else:
            raise

# Thông tin MinIO
minio_endpoint = 'minio:9000'
minio_access_key = 'minio_access_key'
minio_secret_key = 'minio_secret_key'
minio_bucket_name = 'all-symbol'
parquet_file_name = 'all_stock_symbols.parquet'

# Tạo kết nối đến MinIO
minio_client = Minio(
    minio_endpoint,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False  
)

# Định nghĩa DAG 
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 21, 10, 0),
}

with DAG(
    dag_id='update_stock_symbols_in_s3_monthly',
    default_args=default_args,
    schedule_interval='@monthly', 
    catchup=False,
) as dag:

    @task
    def fetch_all_stock_symbols():
        stock_api = Vnstock()
        all_symbols = stock_api.stock(symbol='ACB', source='VCI').listing.all_symbols()
        symbols_df = pd.DataFrame(all_symbols, columns=['ticker', 'organ_name'])
        
        return symbols_df

    @task
    def save_symbols_to_minio(symbols_df: pd.DataFrame):
        if symbols_df is not None and not symbols_df.empty:
            if not minio_client.bucket_exists(minio_bucket_name):
                minio_client.make_bucket(minio_bucket_name)
            
            if object_exists(minio_bucket_name, parquet_file_name):
                response = minio_client.get_object(minio_bucket_name, parquet_file_name)
                existing_data_buffer = io.BytesIO(response.read())  
                existing_data_buffer.seek(0)
                existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')
                combined_df = pd.concat([existing_df, symbols_df], ignore_index=True)
                combined_df_1 = combined_df.drop_duplicates(subset=['ticker'], keep='last').copy()
            else:
                combined_df_1 = symbols_df
            
            # Lưu dữ liệu kết hợp vào buffer    
            combined_data_buffer = io.BytesIO()
            combined_df_1.to_parquet(combined_data_buffer, engine='pyarrow')
            combined_data_buffer.seek(0)
            
            # Ghi dữ liệu đã kết hợp vào MinIO
            minio_client.put_object(
                minio_bucket_name,
                parquet_file_name,
                combined_data_buffer,
                length=combined_data_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
            
            print("Danh sách mã cổ phiếu đã được lưu thành công.")
        else:
            print("Không có dữ liệu mới để lưu.")

    symbols_df = fetch_all_stock_symbols()
    save_symbols_to_minio(symbols_df)
