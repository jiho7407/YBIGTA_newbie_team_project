import os
import glob
import pandas as pd
from pymongo.errors import ConnectionFailure
import sys

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.mongodb_connection import mongo_client
except ImportError:
    print("Could not import mongo_client. Make sure the path is correct.")
    sys.exit(1)

DB_NAME = "review_db"

def load_csv_to_mongodb():
    """
    'database' 폴더의 모든 'reviews_*.csv' 파일을 읽어 MongoDB에 저장합니다.
    """
    try:
        # MongoDB 서버에 연결 확인
        mongo_client.admin.command('ping')
        print("MongoDB connection successful.")
    except ConnectionFailure:
        print("MongoDB connection failed. Please check your connection settings.")
        return

    db = mongo_client.get_database(DB_NAME)
    csv_files = glob.glob(os.path.join(os.path.dirname(__file__), "reviews_*.csv"))

    if not csv_files:
        print("No 'reviews_*.csv' files found in the 'database' directory.")
        return

    for csv_file in csv_files:
        collection_name = os.path.splitext(os.path.basename(csv_file))[0]
        print(f"Processing {csv_file} into collection '{collection_name}'...")

        try:
            df = pd.read_csv(csv_file)
            # 위에 10줄만 남기기
            df = df.head(10)
            # MongoDB에 적합한 형태로 데이터 변환 (e.g., NaN -> None)
            df = df.where(pd.notnull(df), None)
            records = df.to_dict('records')

            # 기존 컬렉션 삭제
            db[collection_name].drop()
            print(f"Dropped existing collection: '{collection_name}'")

            # 데이터 삽입
            if records:
                db[collection_name].insert_many(records)
                print(f"Successfully inserted {len(records)} documents into '{collection_name}'.")
            else:
                print(f"No data to insert for '{collection_name}'.")

        except Exception as e:
            print(f"An error occurred while processing {csv_file}: {e}")

if __name__ == "__main__":
    load_csv_to_mongodb()
