import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# 한글 폰트 설정 (필요시 운영체제에 맞게 변경)
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 1. EDA 파트 (분포 파악, 시각화)
# ==========================================

def plot_distributions(df):
    """별점, 텍스트 길이, 날짜 분포를 시각화합니다."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    # 1-1. 별점 분포 (꺾은선 그래프)
    # 0.5점 단위까지 포함된 분포 확인
    rating_counts = df['rating'].value_counts().sort_index()
    axes[0].plot(rating_counts.index, rating_counts.values, marker='o', linestyle='-', color='b')
    axes[0].set_title('별점 분포 (Rating)')
    axes[0].set_xlabel('Score')
    axes[0].set_ylabel('Count')
    axes[0].grid(True)

    # 1-2. 텍스트 길이 분포 (꺾은선 그래프)
    # 길이 빈도수를 히스토그램 느낌의 선으로 표현
    len_counts = df['content'].str.len().value_counts().sort_index()
    # 데이터가 너무 많으므로 구간(Bin)을 나누어 꺾은선으로 표현하는 것이 더 깔끔함
    sns.histplot(df['content'].str.len(), kde=True, element="poly", ax=axes[1], color='g') 
    axes[1].set_title('리뷰 길이 분포 (Text Length)')
    
    # 1-3. 날짜 분포 (커스텀 구간 막대 그래프)
    def get_period(date_obj):
        y = date_obj.year
        m = date_obj.month
        
        # 영화 개봉일(2019.05.30) 고려하여 첫 구간 설정
        if y == 2019 and 5 <= m <= 6:
            return "2019.05~06"
        elif m <= 6:
            return f"{y}.01~06"
        else:
            return f"{y}.07~12"

    # 날짜 컬럼이 datetime 형식이 아니면 변환
    if not np.issubdtype(df['date'].dtype, np.datetime64):
        df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d', errors='coerce')

    df['period'] = df['date'].apply(get_period)
    
    # 기간 순서 정렬을 위해 리스트업
    periods = sorted(df['period'].unique())
    period_counts = df['period'].value_counts().reindex(periods, fill_value=0)
    
    period_counts.plot(kind='bar', ax=axes[2], color='orange')
    axes[2].set_title('기간별 리뷰 작성 추이')
    axes[2].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


def check_outliers_eda(df):
    """이상치 현황을 출력합니다. (제거 X, 확인용)"""
    print("=== [EDA] 이상치 현황 파악 ===")
    
    # 1. 별점 이상치 (0~5점 범위 밖)
    rating_outliers = df[(df['rating'] < 0) | (df['rating'] > 5)]
    print(f"1. 별점 범위(0~5) 벗어난 리뷰: {len(rating_outliers)}개")

    # 2. 리뷰 길이 이상치 (10자 미만 or 2000자 초과)
    length = df['content'].str.len()
    len_outliers = df[(length < 10) | (length > 2000)]
    print(f"2. 길이 이상치 (10자 미만/2000자 초과): {len(len_outliers)}개")

    # 3. 날짜 이상치 (개봉일 2019-05-30 이전)
    release_date = pd.Timestamp("2019-05-30")
    date_outliers = df[df['date'] < release_date]
    print(f"3. 개봉일({release_date.date()}) 이전 작성 리뷰: {len(date_outliers)}개")
    print("==============================\n")


# ==========================================
# 2. 전처리/FE 파트 (결측치, 이상치 처리)
# ==========================================

def process_missing_values(df):
    """결측치 처리: 별점, 날짜, 내용이 비어있는 행 삭제"""
    initial_len = len(df)
    # dropna: 하나라도 비어있으면 삭제
    df = df.dropna(subset=['rating', 'date', 'content'])
    print(f"[결측치 처리] 삭제된 행: {initial_len - len(df)}개")
    return df

def process_outliers(df):
    """이상치 처리: 클리핑, 삭제, 잘라내기"""
    
    # 1. 별점 클리핑 (0 미만 -> 0, 5 초과 -> 5)
    df['rating'] = df['rating'].clip(lower=0, upper=5)
    
    # 2. 날짜 필터링 (개봉일 이전 삭제)
    release_date = pd.Timestamp("2019-05-30")
    if not np.issubdtype(df['date'].dtype, np.datetime64):
        df['date'] = pd.to_datetime(df['date'])
    
    initial_len = len(df)
    df = df[df['date'] >= release_date]
    print(f"[날짜 이상치] 개봉일 이전 리뷰 삭제: {initial_len - len(df)}개")

    # 3. 텍스트 길이 처리
    # (1) 10자 미만 삭제
    initial_len = len(df)
    df = df[df['content'].str.len() >= 10]
    print(f"[길이 이상치] 10자 미만 삭제: {initial_len - len(df)}개")

    # (2) 2000자 초과: 2000자 직전 문장까지만 남기기
    def truncate_text(text):
        if len(text) <= 2000:
            return text
        
        # 2000자까지 자름
        truncated = text[:2000]
        
        # 마지막 문장 부호(., !, ?) 위치 찾기
        # 정규식으로 마지막 문장 끝나는 지점 탐색
        match = list(re.finditer(r'[.!?]', truncated))
        if match:
            last_idx = match[-1].end()
            return truncated[:last_idx]
        else:
            return truncated # 문장 부호 없으면 그냥 2000자에서 자름
    
    df['content'] = df['content'].apply(truncate_text)
    
    return df