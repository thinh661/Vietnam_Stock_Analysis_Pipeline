from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import pandas as pd
import io
from minio import Minio
from vnstock3 import Vnstock

# Thông tin MinIO
minio_endpoint = 'minio:9000'  
minio_access_key = 'minio_access_key'
minio_secret_key = 'minio_secret_key'
minio_bucket_name = 'stock-data-hour'
parquet_file_name = 'hourly_stock_data_present.parquet'

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
    'start_date': datetime(2024, 8, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='update_stock_data_hourly',
    default_args=default_args,
    schedule_interval=None,  # Chạy mỗi giờ
    catchup=False,
) as dag:

    @task
    def fetch_new_data():
        # Khởi tạo đối tượng Vnstock
        stock_api = Vnstock()

        # Lấy danh sách mã cổ phiếu niêm yết trên sàn HOSE
        hose_symbols = stock_api.stock(symbol='A32', source='VCI').listing.symbols_by_group('HOSE')
        symbols = hose_symbols.tolist()

        new_data = []

        for symbol in symbols:
            try:
                # Khởi tạo đối tượng Vnstock cho mã cổ phiếu hiện tại
                stock = Vnstock().stock(symbol=symbol, source='VCI')
                
                # Lấy dữ liệu giá cổ phiếu theo giờ cho khoảng thời gian hiện tại
                price_data = stock.quote.history(start=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), end=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), interval='1H', count_back=1)
                
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
    def update_parquet_file(new_data_df: pd.DataFrame):
        if new_data_df is not None and not new_data_df.empty:
            # Tải file Parquet hiện có từ MinIO
            if minio_client.bucket_exists(minio_bucket_name):
                if minio_client.object_exists(minio_bucket_name, parquet_file_name):
                    # Tạo một bộ nhớ ảo để đọc dữ liệu từ MinIO
                    existing_data_buffer = io.BytesIO()
                    minio_client.get_object(minio_bucket_name, parquet_file_name).readinto(existing_data_buffer)
                    existing_data_buffer.seek(0)
                    
                    # Đọc dữ liệu Parquet hiện có từ buffer
                    existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')
                    
                    # Kết hợp dữ liệu mới với dữ liệu hiện có
                    combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                    
                    # Lưu dữ liệu kết hợp vào buffer
                    combined_data_buffer = io.BytesIO()
                    combined_df.to_parquet(combined_data_buffer, engine='pyarrow')
                    combined_data_buffer.seek(0)
                    
                    # Ghi dữ liệu đã kết hợp vào MinIO
                    minio_client.put_object(
                        minio_bucket_name,
                        parquet_file_name,
                        combined_data_buffer,
                        length=combined_data_buffer.getbuffer().nbytes,
                        content_type='application/octet-stream'
                    )
                    
                    print("Dữ liệu đã được cập nhật thành công.")
                else:
                    print(f"File Parquet hiện có không tồn tại trong MinIO.")
            else:
                print(f"Bucket {minio_bucket_name} không tồn tại trong MinIO.")
        else:
            print("Không có dữ liệu mới để cập nhật.")

    new_data_df = fetch_new_data()
    update_parquet_file(new_data_df)
