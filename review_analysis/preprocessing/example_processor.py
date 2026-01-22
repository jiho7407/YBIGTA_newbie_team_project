from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing import wiseyy as common_utils

import pandas as pd
import numpy as np
import os

class ExampleProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)


    def preprocess(self):
        """
        데이터 로드 및 전처리 (결측치/이상치 처리)
        """
        print(f"Processing {self.input_path}...")
        
        # 1. 데이터 로드
        self.df = pd.read_csv(self.input_path)
        
        # 2. 날짜 형식 변환 (문자열 -> datetime)
        self.df['date'] = pd.to_datetime(self.df['date'], format='%Y.%m.%d', errors='coerce')

        # [EDA 실행] (필요시 주석 해제하여 확인)
        # common_utils.check_outliers_eda(self.df)
        # common_utils.plot_distributions(self.df) 

        # 3. 공통 모듈을 사용해 전처리 수행
        # (1) 결측치 처리
        self.df = common_utils.process_missing_values(self.df)
        
        # (2) 이상치 처리 (클리핑, 삭제, 자르기)
        self.df = common_utils.process_outliers(self.df)

        # 텍스트데이터 전처리
        self.df['content'] = self.df['content'].str.lower()  # 소문자 변환
        self.df = self.df[self.df['content'].str.len() > 10]  # 10자 이하 리뷰 제거
        self.df = self.df[self.df['content'].str.len() < 2000]  # 2000자 이상 리뷰 제거
        self.df['content'] = self.df['content'].str.replace(r'[^\w\s]', '', regex=True) # 특수문자 제거
        for punct in ['.', ',', '!', '?', ';', ':']: # 문장 부호 앞에 공백 추가
            self.df['content'] = self.df['content'].str.replace(punct, f' {punct}', regex=False)
        
        self.processed_data = self.df
    
    def feature_engineering(input_file, output_file, rating_col, text_col):
        try:
            # 1. CSV 파일 읽기
           
            df = pd.read_csv(input_file)
            print(f"'{input_file}' loaded.")
            
            
            # 2. 텍스트 길이 계산 (결측치는 빈 문자열로 처리 후 계산)
            # 텍스트 컬럼을 문자열로 변환 후 길이 측정
            text_length = df[text_col].astype(str).str.len()

            # 3. 파생변수 계산
            rating_deviation_sq = (df[rating_col] - 2.5) ** 2
            
            
            # 두 값을 곱하여 새로운 컬럼 생성
            new_col_name = 'Extreme_score' # 새로 저장될 컬럼명
            df[new_col_name] = rating_deviation_sq * text_length

            # 4. 결과 저장
            # 한글 깨짐 방지를 위해 utf-8-sig 인코딩 사용 권장
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"작업이 완료. 결과가 '{output_file}'에 저장되었습니다.")
            


        except FileNotFoundError:
            print("파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        except KeyError as e:
            print(f"컬럼 이름을 찾을 수 없습니다: {e}")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
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