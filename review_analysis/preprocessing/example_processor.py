from review_analysis.preprocessing.base_processor import BaseDataProcessor

import pandas as pd
import numpy as np
import os

class ExampleProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)


    def preprocess(self):
        print(f"Preprocessing data from {self.input_path}...")

        df = pd.read_csv(self.input_path)

        # 결측치처리
        # Todo

        # 이상치 처리
        # Todo

        # 텍스트데이터 전처리
        df['content'] = df['content'].str.lower()  # 소문자 변환
        df = df[df['content'].str.len() > 10]  # 10자 이하 리뷰 제거
        df = df[df['content'].str.len() < 2000]  # 2000자 이상 리뷰 제거
        df['content'] = df['content'].str.replace(r'[^\w\s]', '', regex=True) # 특수문자 제거

        for punct in ['.', ',', '!', '?', ';', ':']: # 문장 부호 앞에 공백 추가
            df['content'] = df['content'].str.replace(punct, f' {punct}', regex=False)
        
        self.processed_data = df
    
    def feature_engineering(self):
        print("Performing feature engineering...")
        
        df = self.processed_data

        # 다른 특징추출
        # Todo

        # 텍스트 벡터화
        word_to_id = {}
        id_to_word = []
        window_size = 5

        # word <-> id 매핑 생성
        for review in df['content']:
            words = review.split()
            for i, word in enumerate(words):
                if word not in word_to_id:
                    word_id = len(word_to_id)
                    word_to_id[word] = word_id
                    id_to_word.append(word)
        
        # N*N array 생성
        sz = len(word_to_id)
        co_matrix = np.zeros((sz, sz), dtype=np.int32)
        for review in df['content']:
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
        
        # PPMI
        eps = 1e-8
        W = np.zeros_like(co_matrix, dtype=np.float32)
        N = np.sum(co_matrix)
        S = np.sum(co_matrix, axis=0)

        for i in range(co_matrix.shape[0]):
            for j in range(co_matrix.shape[1]):
                pmi = np.log2((co_matrix[i][j] * N) / (S[i] * S[j]) + eps)
                W[i][j] = max(0, pmi)
        
        from sklearn.utils.extmath import randomized_svd
        U, S, V = randomized_svd(W, n_components=100, n_iter=5, random_state=42)
        word_vectors = U[:, :100]

        # 리뷰 벡터 생성 (단어 벡터의 평균)
        review_vectors = []
        for review in df['content']:
            ret = np.zeros(100, dtype=np.float32)
            words = review.split()
            for word in words:
                if word in word_to_id:
                    word_id = word_to_id[word]
                    ret += word_vectors[word_id]
            ret /= len(words)
            review_vectors.append(ret)
        df['review_vector'] = review_vectors

        self.engineered_data = df

    def save_to_database(self):
        output_path = self.output_dir + "/preprocessed_" + self.input_path.split('/')[-1]
        print(f"Saving processed data to ({output_path}...")

        if self.engineered_data is None:
            print("No engineered data to save.")
            return
        
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        self.engineered_data.to_csv(output_path, index=False)