import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import platform

# -----------------------------
# 한글 폰트 설정
# -----------------------------
if platform.system() == 'Darwin': # 맥
    plt.rc('font', family='AppleGothic')
else: # 윈도우
    plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def get_period(date_obj):
    """기간 분류 로직"""
    if pd.isnull(date_obj):
        return "Unknown"
    
    y = date_obj.year
    m = date_obj.month
    
    if y == 2019:
        if m < 5: return "2019.Pre"
        elif 5 <= m <= 6: return "2019.05~06"
        else: return "2019.07~12"
    else:
        if m <= 6: return f"{y}.01~06"
        else: return f"{y}.07~12"

def create_individual_plot(df, site_name, output_dir):
    """[개별] 사이트별 시각화 (1x3 레이아웃)"""
    
    # 다시 1행 3열로 변경
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(f'{site_name} 데이터 분석 결과', fontsize=20, fontweight='bold')

    # 1. 별점 분포 (Line)
    try:
        rating_counts = df['rating'].value_counts().sort_index()
        axes[0].plot(rating_counts.index, rating_counts.values, marker='o', linestyle='-', color='royalblue')
        axes[0].set_title('1. 별점 분포 (Rating)', fontsize=14)
        axes[0].set_xlabel('점수')
        axes[0].set_ylabel('리뷰 개수')
        axes[0].grid(True, linestyle='--', alpha=0.5)
    except: axes[0].set_title('별점 데이터 없음')

    # 2. 리뷰 길이 분포 (Histogram + KDE)
    try:
        doc_lens = df['content'].astype(str).apply(len)
        sns.histplot(doc_lens, kde=True, ax=axes[1], color='forestgreen')
        axes[1].set_title('2. 리뷰 길이 분포 (글자 수)', fontsize=14)
        axes[1].set_xlabel('글자 수')
        axes[1].set_ylabel('빈도수')
    except: axes[1].set_title('길이 데이터 없음')

    # 3. 기간별 추이 (Bar)
    try:
        if not np.issubdtype(df['date'].dtype, np.datetime64):
            df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d', errors='coerce')
        df['period'] = df['date'].apply(get_period)
        period_counts = df['period'].value_counts().sort_index()
        axes[2].bar(period_counts.index, period_counts.values, color='orange', alpha=0.7, edgecolor='black')
        axes[2].set_title('3. 기간별 리뷰 작성 추이', fontsize=14)
        axes[2].set_xlabel('기간')
        axes[2].tick_params(axis='x', rotation=45)
        axes[2].grid(axis='y', linestyle='--', alpha=0.5)
    except: axes[2].set_title('기간 데이터 없음')

    plt.tight_layout()
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, f"viz_{site_name}.png"), dpi=300)
    plt.close()

def create_comparison_plot(data_dict, output_dir):
    """[통합] 3개 사이트 비교 시각화 (1x3 레이아웃)"""
    print("\n비교 분석 그래프 생성 중... (Generating comparison plot)")
    
    # 다시 1행 3열로 변경
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('사이트별 비교 분석 (IMDb vs Metacritic vs RottenTomatoes)', fontsize=20, fontweight='bold')
    
    colors = {'imdb': 'red', 'metacritic': 'blue', 'rottentomato': 'green'}
    
    # 1. 별점 분포 비교 (KDE)
    axes[0].set_title('1. 별점 분포 비교 (밀도)', fontsize=14)
    for site, df in data_dict.items():
        try:
            sns.kdeplot(data=df, x='rating', label=site, ax=axes[0], 
                        color=colors.get(site, 'black'), linewidth=2, fill=True, alpha=0.1)
        except: pass
    axes[0].set_xlabel('점수')
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # 2. 리뷰 길이 분포 비교 (KDE)
    axes[1].set_title('2. 리뷰 길이 분포 비교 (밀도)', fontsize=14)
    for site, df in data_dict.items():
        try:
            doc_lens = df['content'].astype(str).apply(len)
            sns.kdeplot(x=doc_lens, label=site, ax=axes[1], 
                        color=colors.get(site, 'black'), linewidth=2)
        except: pass
    axes[1].set_xlabel('글자 수')
    axes[1].set_xlim(0, 3000)
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # 3. 기간별 추이 비교 (Line)
    axes[2].set_title('3. 기간별 추이 비교', fontsize=14)
    all_periods = set()
    period_data = {}

    for site, df in data_dict.items():
        try:
            if not np.issubdtype(df['date'].dtype, np.datetime64):
                df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d', errors='coerce')
            df['period'] = df['date'].apply(get_period)
            counts = df['period'].value_counts()
            period_data[site] = counts
            all_periods.update(counts.index)
        except: continue
    
    sorted_periods = sorted(list(all_periods))
    for site, counts in period_data.items():
        y_values = [counts.get(p, 0) for p in sorted_periods]
        axes[2].plot(sorted_periods, y_values, marker='o', label=site, 
                     color=colors.get(site, 'black'), linewidth=2)

    axes[2].set_xlabel('기간')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].legend()
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    plt.savefig(os.path.join(output_dir, "viz_comparison.png"), dpi=300)
    print(f"비교 그래프 저장 완료: {os.path.join(output_dir, 'viz_comparison.png')}")
    plt.close()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "..", "..", "database")
    plots_dir = os.path.join(base_dir, "..", "plots")

    target_files = [
        "reviews_imdb.csv",
        "reviews_metacritic.csv",
        "reviews_rottentomatoes.csv"
    ]

    all_data = {} 

    print("=== 시각화 시작 ===")
    
    for filename in target_files:
        file_path = os.path.join(db_dir, filename)
        
        if os.path.exists(file_path):
            print(f"\n처리 중: {filename}...")
            try:
                df = pd.read_csv(file_path)
                site_name = filename.replace("reviews_", "").replace(".csv", "")
                
                # 1. 개별 그래프
                create_individual_plot(df, site_name, plots_dir)
                print(f"{site_name} 개별 그래프 저장 완료")
                
                all_data[site_name] = df
                
            except Exception as e:
                print(f"{filename} 처리 중 오류 발생: {e}")
        else:
            print(f"\n파일을 찾을 수 없음: {filename} (건너뜀)")

    if len(all_data) > 0:
        create_comparison_plot(all_data, plots_dir)

    print("\n=== 모든 시각화 완료 ===")

if __name__ == "__main__":
    main()