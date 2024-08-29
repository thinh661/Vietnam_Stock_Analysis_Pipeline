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
minio_bucket_name = 'insider-deals'
parquet_file_name = 'insider_deals.parquet'

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

# Định nghĩa DAG với Decorator
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 8, 21, 10, 0),
}

with DAG(
    dag_id='update_insider_deals_in_s3_monthly',
    default_args=default_args,
    schedule_interval=None,  # Chạy hàng tuần
    catchup=False,
) as dag:

    @task
    def fetch_all_insider_deals():
        stock_api = Vnstock()
        all_symbols = stock_api.stock(symbol='ACB', source='VCI').listing.symbols_by_group('HOSE')
        symbols_df = pd.DataFrame(all_symbols, columns=['symbol']) 
        print(f"Lấy được {len(symbols_df)} mã cổ phiếu.")
        all_insider_deals = []
        for index, symbol_info in symbols_df.iterrows():
            symbol = symbol_info['symbol']
            try:
                print(f"Đang thu thập dữ liệu cho mã {symbol}...")
                company = stock_api.stock(symbol=symbol, source='TCBS').company
                insider_deals = company.insider_deals()
                print(f"Dữ liệu cho {symbol}: {insider_deals}")
                if not insider_deals.empty:
                    insider_deals['symbol'] = symbol
                    all_insider_deals.append(insider_deals)
            except Exception as e:
                print(f"Lỗi khi thu thập dữ liệu cho {symbol}: {str(e)}")
        if all_insider_deals:
            combined_insider_deals_df = pd.concat(all_insider_deals, ignore_index=True)
            print(f"Thu thập được {len(combined_insider_deals_df)} dòng dữ liệu.")
            return combined_insider_deals_df
        else:
            print("Không có giao dịch nội bộ nào.")
            return pd.DataFrame() 

    @task
    def save_insider_deals_to_minio(insider_deals_df: pd.DataFrame):
        if insider_deals_df is not None and not insider_deals_df.empty:
            if not minio_client.bucket_exists(minio_bucket_name):
                minio_client.make_bucket(minio_bucket_name)
            if object_exists(minio_bucket_name, parquet_file_name):
                response = minio_client.get_object(minio_bucket_name, parquet_file_name)
                existing_data_buffer = io.BytesIO(response.read())  # Đọc toàn bộ dữ liệu vào BytesIO
                existing_data_buffer.seek(0)
                existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')
                combined_df = pd.concat([existing_df, insider_deals_df], ignore_index=True)
                combined_df['deal_announce_date'] = combined_df['deal_announce_date'].astype(str)
                combined_df_1 = combined_df.drop_duplicates( keep='last').copy()
            else:
                combined_df_1 = insider_deals_df
 
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
            
            print("Dữ liệu giao dịch nội bộ đã được lưu thành công.")
        else:
            print("Không có dữ liệu mới để lưu.")
    
    symbols_df = fetch_all_insider_deals()
    save_insider_deals_to_minio(symbols_df)
