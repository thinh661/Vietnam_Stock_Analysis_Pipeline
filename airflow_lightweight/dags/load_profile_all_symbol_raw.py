from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pandas as pd
import io
from minio import Minio
from vnstock3 import Vnstock
from minio.error import S3Error

# Thông tin MinIO
minio_endpoint = 'minio:9000'
minio_access_key = 'minio_access_key'
minio_secret_key = 'minio_secret_key'
minio_bucket_name = 'profile-all-symbol'
parquet_file_name = 'company_profiles.parquet'

# Tạo kết nối đến MinIO
minio_client = Minio(
    minio_endpoint,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False  
)

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

# Định nghĩa DAG 
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 21, 10, 0),
}

with DAG(
    dag_id='update_company_profiles_in_s3_year_123',
    default_args=default_args,
    schedule_interval=None,  # Chạy hàng tháng
    catchup=False,
) as dag:

    @task
    def fetch_all_stock_symbols():
        stock_api = Vnstock()
        all_symbols = stock_api.stock(symbol='ACB', source='VCI').listing.all_symbols()
        symbols_df = pd.DataFrame(all_symbols, columns=['ticker', 'organ_name'])
        
        return symbols_df

    @task
    def fetch_company_profiles(symbols_df: pd.DataFrame):
        profiles = []
        stock_api = Vnstock()

        for symbol in symbols_df['ticker']:
            try:
                company = stock_api.stock(symbol=symbol, source='TCBS').company
                profile = company.profile()
                if not profile.empty:
                    profiles.append(profile.assign(ticker=symbol))
            except Exception as e:
                print(f"Lỗi khi thu thập hồ sơ công ty cho {symbol}: {str(e)}")
        
        # Kết hợp tất cả hồ sơ công ty thành một DataFrame
        if profiles:
            combined_profiles_df = pd.concat(profiles, ignore_index=True)
            return combined_profiles_df
        else:
            return pd.DataFrame()

    @task
    def save_profiles_to_minio(profiles_df: pd.DataFrame):
        if profiles_df is not None and not profiles_df.empty:
            if not minio_client.bucket_exists(minio_bucket_name):
                minio_client.make_bucket(minio_bucket_name)
            
            if object_exists(minio_bucket_name, parquet_file_name):
                response = minio_client.get_object(minio_bucket_name, parquet_file_name)
                existing_data_buffer = io.BytesIO(response.read()) 
                existing_data_buffer.seek(0)
                existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')
                combined_df = pd.concat([existing_df, profiles_df], ignore_index=True)
                combined_df_1 = combined_df.drop_duplicates(subset=['ticker'], keep='last').copy()
            else:
                combined_df_1 = profiles_df
            
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
            
            print("Hồ sơ công ty đã được lưu thành công.")
        else:
            print("Không có dữ liệu mới để lưu.")

    symbols_df = fetch_all_stock_symbols()
    profiles_df = fetch_company_profiles(symbols_df)
    save_profiles_to_minio(profiles_df)
