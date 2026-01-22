import pandas as pd
import os
from review_analysis.preprocessing.base_processor import BaseDataProcessor
# 공통 모듈 임포트 (common_utils.py)
from review_analysis.preprocessing import wiseyy as common_utils

class IMDbProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df = None

    def preprocess(self):
        """
        데이터 로드 및 전처리 (결측치/이상치 처리)
        """
        print(f"Processing IMDb data from {self.input_path}...")
        
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

        print("Preprocessing completed.")

    def feature_engineering(self):
        pass

    def save_to_database(self):
        """
        요청하신 경로(review_analysis/crawling/result)와 파일명 형식으로 저장
        """
        if self.df is None:
            print("No data to save. Run preprocess() first.")
            return

        # 1. 저장 경로 설정
        # 실행 위치(preprocessing) 기준: ../../database
        target_dir = os.path.join("..", "..", "database")
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 2. 파일명 설정 (preprocessed_reviews_imdb.csv)
        # input_path가 '.../reviews_imdb.csv'라고 가정할 때,
        # 파일명에서 'reviews_' 뒷부분(사이트명)을 가져오거나, 그냥 하드코딩해도 됩니다.
        # 여기서는 가장 확실하게 하드코딩합니다.
        filename = "preprocessed_reviews_imdb.csv"
        
        filepath = os.path.join(target_dir, filename)
        
        self.df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Saved preprocessed data to {filepath}")