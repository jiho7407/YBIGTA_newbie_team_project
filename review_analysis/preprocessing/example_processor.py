from review_analysis.preprocessing.base_processor import BaseDataProcessor

class ExampleProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)

    def preprocess(self):
        pass
    
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

    def save_to_database(self):
        pass
