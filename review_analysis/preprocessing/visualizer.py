import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# 한글 폰트 설정 (Mac: AppleGothic, Windows: Malgun Gothic)
import platform
if platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def get_period(date_obj):
    """
    기간 분류 로직:
    - 2019.05~06 (개봉 초기)
    - 그 외에는 상반기(01~06) / 하반기(07~12)로 분류
    """
    if pd.isnull(date_obj):
        return "Unknown"
        
    y = date_obj.year
    m = date_obj.month
    
    # 영화 개봉일(2019.05.30) 고려
    if y == 2019:
        if m < 5:
            return "2019.Pre" # 개봉 전
        elif 5 <= m <= 6:
            return "2019.05~06"
        else:
            return "2019.07~12"
    else:
        if m <= 6:
            return f"{y}.01~06"
        else:
            return f"{y}.07~12"

def create_and_save_plot(df, site_name, output_dir):
    """데이터프레임을 받아 그래프를 그리고 저장합니다."""
    
    # 캔버스 설정 (1행 3열)
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(f'{site_name} Data Analysis', fontsize=20, fontweight='bold')

    # -----------------------------
    # 1. 별점 분포 (꺾은선 그래프)
    # -----------------------------
    try:
        # 별점 빈도수 계산 및 정렬
        rating_counts = df['rating'].value_counts().sort_index()
        
        # 꺾은선 그래프
        axes[0].plot(rating_counts.index, rating_counts.values, 
                    marker='o', linestyle='-', color='royalblue', linewidth=2)
        
        # 디자인
        axes[0].set_title('별점 분포 (Rating Distribution)', fontsize=14)
        axes[0].set_xlabel('Score')
        axes[0].set_ylabel('Count')
        axes[0].grid(True, linestyle='--', alpha=0.6)
    except Exception as e:
        print(f"[{site_name}] 별점 그래프 에러: {e}")

    # -----------------------------
    # 2. 리뷰 길이 분포 (히스토그램 + KDE)
    # -----------------------------
    try:
        # 리뷰 길이 계산 (공백 포함)
        doc_lens = df['content'].astype(str).apply(len)
        
        # 히스토그램 & KDE
        sns.histplot(doc_lens, kde=True, ax=axes[1], color='forestgreen', element="step")
        
        # 디자인
        axes[1].set_title('리뷰 길이 분포 (Text Length)', fontsize=14)
        axes[1].set_xlabel('Length (Characters)')
        axes[1].set_ylabel('Frequency')
        axes[1].grid(True, linestyle='--', alpha=0.6)
    except Exception as e:
        print(f"[{site_name}] 길이 그래프 에러: {e}")

    # -----------------------------
    # 3. 날짜별 리뷰 수 (기간별 막대 그래프)
    # -----------------------------
    try:
        # 날짜 변환 (에러 발생 시 NaT 처리)
        # 여러 포맷 대응을 위해 errors='coerce' 사용
        if not np.issubdtype(df['date'].dtype, np.datetime64):
            df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d', errors='coerce')
        
        # 기간(Period) 파생변수 생성
        df['period'] = df['date'].apply(get_period)
        
        # 기간별 개수 집계 및 정렬
        # Unknown이나 Pre 기간은 제외하고 싶으면 여기서 필터링 가능
        period_counts = df['period'].value_counts()
        
        # 정렬: 문자열 기준 정렬 (2019... -> 2020... 순서)
        sorted_periods = sorted(period_counts.index)
        sorted_counts = [period_counts[p] for p in sorted_periods]
        
        # 막대 그래프
        rects = axes[2].bar(sorted_periods, sorted_counts, color='orange', edgecolor='black', alpha=0.7)
        
        # 디자인
        axes[2].set_title('기간별 리뷰 작성 추이 (Trend by Period)', fontsize=14)
        axes[2].set_xlabel('Period')
        axes[2].tick_params(axis='x', rotation=45) # X축 라벨 회전
        axes[2].grid(axis='y', linestyle='--', alpha=0.6)
        
    except Exception as e:
        print(f"[{site_name}] 날짜 그래프 에러: {e}")

    # -----------------------------
    # 저장
    # -----------------------------
    plt.tight_layout()
    
    # plots 폴더가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    save_path = os.path.join(output_dir, f"viz_{site_name}.png")
    plt.savefig(save_path, dpi=300) # 고화질 저장
    print(f"Saved plot to: {save_path}")
    
    plt.close() # 메모리 해제

def main():
    # 경로 설정 (preprocessing 폴더 기준)
    base_dir = os.path.dirname(os.path.abspath(__file__)) # 현재 파일 위치
    db_dir = os.path.join(base_dir, "..", "..", "database") # database 폴더
    plots_dir = os.path.join(base_dir, "..", "plots") # plots 폴더

    # 대상 사이트 파일명 리스트
    target_files = [
        "reviews_imdb.csv",
        "reviews_metacritic.csv",
        "reviews_rottentomatoes.csv"
    ]

    print("=== 시각화 시작 (Visualization Start) ===")
    
    for filename in target_files:
        file_path = os.path.join(db_dir, filename)
        
        # 파일 존재 여부 확인
        if os.path.exists(file_path):
            print(f"\nProcessing: {filename}...")
            try:
                # 데이터 로드
                df = pd.read_csv(file_path)
                
                # 사이트 이름 추출 (reviews_imdb.csv -> imdb)
                site_name = filename.replace("reviews_", "").replace(".csv", "")
                
                # 시각화 및 저장 함수 호출
                create_and_save_plot(df, site_name, plots_dir)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        else:
            print(f"\nFile not found: {filename} (Skipping)")

    print("\n=== 모든 시각화 완료 (All Done) ===")

if __name__ == "__main__":
    main()