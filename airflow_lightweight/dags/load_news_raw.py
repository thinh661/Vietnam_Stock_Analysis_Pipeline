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
news_bucket_name = 'news-all-symbol'
news_file_name = 'company_news.parquet'

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
    dag_id='update_company_news_in_s3_week',
    default_args=default_args,
    schedule_interval='@monthly',  # Chạy hàng tháng
    catchup=False,
) as dag:

    @task
    def fetch_all_stock_symbols():
        stock_api = Vnstock()
        all_symbols = stock_api.stock(symbol='ACB', source='VCI').listing.all_symbols()
        symbols_df = pd.DataFrame(all_symbols, columns=['ticker', 'organ_name'])
        return symbols_df[0:100]

    @task
    def fetch_company_news(symbols_df: pd.DataFrame):
        news_list = []
        stock_api = Vnstock()
        for symbol in symbols_df['ticker']:
            try:
                company = stock_api.stock(symbol=symbol, source='TCBS').company
                news_df = company.news()
                if not news_df.empty:
                    news_df['ticker'] = symbol
                    news_list.append(news_df)
            except Exception as e:
                print(f"Lỗi khi thu thập tin tức cho {symbol}: {str(e)}")

        if news_list:
            combined_news_df = pd.concat(news_list, ignore_index=True)
            combined_news_df.fillna(value={'price': 0, 'price_change': 0, 'price_change_ratio': 0}, inplace=True)
            return combined_news_df
        else:
            return pd.DataFrame()

    @task
    def save_news_to_minio(news_df: pd.DataFrame):
        if news_df is not None and not news_df.empty:
            if not minio_client.bucket_exists(news_bucket_name):
                minio_client.make_bucket(news_bucket_name)
            
            if object_exists(news_bucket_name, news_file_name):
                response = minio_client.get_object(news_bucket_name, news_file_name)
                existing_data_buffer = io.BytesIO(response.read())  # Đọc toàn bộ dữ liệu vào BytesIO
                existing_data_buffer.seek(0)
                existing_df = pd.read_parquet(existing_data_buffer, engine='pyarrow')
                combined_df = pd.concat([existing_df, news_df], ignore_index=True)
                combined_df['publish_date'] = combined_df['publish_date'].astype(str)
                combined_df_1 = combined_df.drop_duplicates(subset=['id', 'publish_date'], keep='last').copy()
            else:
                combined_df_1 = news_df
   
            combined_data_buffer = io.BytesIO()
            combined_df_1.to_parquet(combined_data_buffer, engine='pyarrow')
            combined_data_buffer.seek(0)
            minio_client.put_object(
                news_bucket_name,
                news_file_name,
                combined_data_buffer,
                length=combined_data_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
            print("Tin tức công ty đã được lưu thành công.")
        else:
            print("Không có dữ liệu mới để lưu.")

    symbols_df = fetch_all_stock_symbols()
    news_df = fetch_company_news(symbols_df)
    save_news_to_minio(news_df)
