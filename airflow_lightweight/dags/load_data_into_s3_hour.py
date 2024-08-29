from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import pandas as pd
import os
from minio import Minio
from vnstock3 import Vnstock
from pyarrow import parquet as pq
import pyarrow as pa
import io

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
minio_bucket_name = 'stock-data-hour'
parquet_file_name = 'hourly_stock_data_persent.parquet'

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
    'start_date': datetime(2024, 8, 21, 10, 0),
}

with DAG(
    dag_id='update_stock_data_hour_into_s3_123',
    default_args=default_args,
    schedule_interval='1 2-8 * * 1-5',
    catchup=False,
) as dag:

    @task
    def fetch_new_data_1():
        stock_api = Vnstock()
        hose_symbols = stock_api.stock(symbol='A32', source='VCI').listing.symbols_by_group('HOSE')
        symbols = hose_symbols.tolist()
        new_data = []
        for symbol in symbols:
            try:
                stock = Vnstock().stock(symbol=symbol, source='VCI')
                
                price_data = stock.quote.history(start='2024-1-10', end=datetime.now().strftime('%Y-%m-%d'), interval='1H',count_back=1)
                
                if not price_data.empty:
                    price_data['symbol'] = symbol
                    new_data.append(price_data)
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu cho mã cổ phiếu {symbol}: {e}")
        
        if new_data:
            new_data_df = pd.concat(new_data, ignore_index=True)
            return new_data_df
        return None

    @task
    def update_parquet_file_1(new_data_df: pd.DataFrame):
        if new_data_df is not None and not new_data_df.empty:
            if minio_client.bucket_exists(minio_bucket_name):
                if object_exists(minio_bucket_name, parquet_file_name):
                    response = minio_client.get_object(minio_bucket_name, parquet_file_name)
                    existing_data_buffer = io.BytesIO(response.read())  # Đọc toàn bộ dữ liệu vào BytesIO
                    existing_data_buffer.seek(0)
                    existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')

                    combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                    combined_df['time'] = combined_df['time'].astype(str)
                    # Lấy phần ngày từ cột 'time' (giả sử định dạng của 'time' là 'YYYY-MM-DD HH:MM:SS')
                    # combined_df['date'] = combined_df['time'].str.slice(0, 10)  # Lấy 10 ký tự đầu tiên (YYYY-MM-DD)

                    # Lọc trùng lặp chỉ theo ngày và symbol
                    combined_df_1 = combined_df.drop_duplicates(subset=['time', 'symbol'],keep='last').copy()

                    # Sau khi lọc, bạn có thể xóa cột 'date' nếu không cần thiết
                    # combined_df_1.drop(columns=['date'], inplace=True)
                                          
                    combined_data_buffer = io.BytesIO()
                    
                    combined_df_1.to_parquet(combined_data_buffer, engine='pyarrow')
                    combined_data_buffer.seek(0)

                    minio_client.put_object(
                        minio_bucket_name,
                        parquet_file_name,
                        combined_data_buffer,
                        length=combined_data_buffer.getbuffer().nbytes,
                        content_type='application/octet-stream'
                    )
                    print("Dữ liệu đã được cập nhật thành công.")
                else:
                    print("File Parquet hiện có không tồn tại trong MinIO.")
            else:
                print(f"Bucket {minio_bucket_name} không tồn tại trong MinIO.")
        else:
            print("Không có dữ liệu mới để cập nhật.")


    new_data_df = fetch_new_data_1()
    update_parquet_file_1(new_data_df)