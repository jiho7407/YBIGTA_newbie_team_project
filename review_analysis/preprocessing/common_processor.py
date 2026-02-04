from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing import wiseyy as common_utils
from pymongo import MongoClient
import pandas as pd
import numpy as np
import os

class CommonProcessor(BaseDataProcessor):
    def __init__(self, db_client: MongoClient, db_name: str, site_name: str):
        self.db_client = db_client
        self.db = self.db_client[db_name]
        self.site_name = site_name
        self.raw_collection_name = f"reviews_{site_name}"
        self.processed_collection_name = f"preprocessed_reviews_{site_name}"
        self.df = None
        self.processed_data = None
        self.engineered_data = None

    def preprocess(self):
        """
        데이터 로드 및 전처리 (결측치/이상치 처리)
        """
        print(f"Processing {self.raw_collection_name} from MongoDB...")
        
        # 1. 데이터 로드 from MongoDB
        raw_collection = self.db[self.raw_collection_name]
        data = list(raw_collection.find({}, {'_id': 0}))
        if not data:
            raise ValueError(f"No data found in collection '{self.raw_collection_name}'")
        
        self.df = pd.DataFrame(data)
        
        # 2. 날짜 형식 변환 (문자열 -> datetime)
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

        # 3. 공통 모듈을 사용해 전처리 수행
        self.df = common_utils.process_missing_values(self.df)
        self.df = common_utils.process_outliers(self.df)

        # 텍스트데이터 전처리
        self.df['content'] = self.df['content'].str.lower()
        self.df = self.df[self.df['content'].str.len() > 10]
        self.df = self.df[self.df['content'].str.len() < 2000]
        self.df['content'] = self.df['content'].str.replace(r'[^\w\s]', '', regex=True)
        for punct in ['.', ',', '!', '?', ';', ':']:
            self.df['content'] = self.df['content'].str.replace(punct, f' {punct}', regex=False)
        
        self.processed_data = self.df

    def feature_engineering(self):
        if self.processed_data is None:
            print("No processed data to engineer. Run preprocess() first.")
            return
            
        df = self.processed_data.copy()

        # 파생변수 생성
        text_length = df['content'].astype(str).str.len()
        rating_deviation_sq = (df['rating'] - 2.5) ** 2
        df['Extreme_score'] = rating_deviation_sq * text_length

        # 텍스트 벡터화 (기존 로직과 동일)
        word_to_id = {}
        for review in df['content'].dropna():
            words = review.split()
            for word in words:
                if word not in word_to_id:
                    word_to_id[word] = len(word_to_id)
        
        id_to_word = {i: w for w, i in word_to_id.items()}
        
        sz = len(word_to_id)
        co_matrix = np.zeros((sz, sz), dtype=np.int32)
        window_size = 5

        for review in df['content'].dropna():
            words = review.split()
            for i, word in enumerate(words):
                word_id = word_to_id[word]
                for j in range(1, window_size + 1):
                    if i - j >= 0:
                        left_word_id = word_to_id[words[i - j]]
                        co_matrix[word_id][left_word_id] += 1
                    if i + j < len(words):
                        right_word_id = word_to_id[words[i + j]]
                        co_matrix[word_id][right_word_id] += 1
        
        eps = 1e-8
        W = np.zeros_like(co_matrix, dtype=np.float32)
        N = np.sum(co_matrix)
        S = np.sum(co_matrix, axis=0)

        total_sum = np.sum(S)
        if total_sum > 0:
            for i in range(co_matrix.shape[0]):
                for j in range(co_matrix.shape[1]):
                    if S[i] > 0 and S[j] > 0:
                        pmi = np.log2((co_matrix[i][j] * N) / (S[i] * S[j]) + eps)
                        W[i][j] = max(0, pmi)
        
        from sklearn.utils.extmath import randomized_svd
        U, S_svd, V = randomized_svd(W, n_components=100, n_iter=5, random_state=42)
        word_vectors = U[:, :100]

        notna_content_df = df[df['content'].notna()].copy()
        review_vectors = []
        for review in notna_content_df['content']:
            ret = np.zeros(100, dtype=np.float32)
            words = review.split()
            count = 0
            for word in words:
                if word in word_to_id:
                    word_id = word_to_id[word]
                    ret += word_vectors[word_id]
                    count += 1
            if count > 0:
                ret /= count
            review_vectors.append(ret.tolist())
        
        notna_content_df['review_vector'] = review_vectors
        df = df.merge(notna_content_df[['review_vector']], left_index=True, right_index=True, how='left')

        self.engineered_data = df

    def save_to_database(self):
        print(f"Saving processed data to MongoDB collection ({self.processed_collection_name})...")

        if self.engineered_data is None:
            print("No engineered data to save.")
            return
        
        processed_collection = self.db[self.processed_collection_name]
        processed_collection.drop()
        
        # NaN 값을 None으로 변환
        records = self.engineered_data.where(pd.notnull(self.engineered_data), None).to_dict('records')
        
        if records:
            processed_collection.insert_many(records)
            print(f"Successfully saved {len(records)} documents.")

    # BaseDataProcessor의 추상 메서드를 구현하기 위해 추가
    def __init__(self, input_path: str = None, output_dir: str = None, db_client: MongoClient = None, db_name: str = None, site_name: str = None):
        if db_client and db_name and site_name:
            self.db_client = db_client
            self.db = self.db_client[db_name]
            self.site_name = site_name
            self.raw_collection_name = f"reviews_{site_name}"
            self.processed_collection_name = f"preprocessed_reviews_{site_name}"
        
        self.df = None
        self.processed_data = None
        self.engineered_data = None
