import pandas as pd
import os
import glob

def merge_csv_files():
    file_pattern = 'database/preprocessed_reviews_*.csv' 
    file_list = glob.glob(file_pattern)
    
    if not file_list:
        print("파일 경로 에러")
        return

    combined_df = pd.DataFrame()

    for file_path in file_list:
        try:
            print(f"Reading {file_path}...")
            df = pd.read_csv(file_path)
            
            file_name = os.path.basename(file_path)
            site_name = file_name.replace('preprocessed_reviews_', '').replace('.csv', '')
            
            df['source_site'] = site_name
            
            target_cols = ['content', 'rating', 'date', 'source_site']

            valid_cols = [col for col in target_cols if col in df.columns]
            df = df[valid_cols]
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    if not combined_df.empty:

        combined_df = combined_df.dropna(subset=['content'])
        
        output_path = 'database/total_reviews.csv'
        combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n총 {len(combined_df)}개의 리뷰 병합 완료!")
        print(f"저장된 파일: {output_path}")
        print(combined_df.head())
    else:
        print("병합된 데이터가 없습니다.")

if __name__ == "__main__":
    merge_csv_files()