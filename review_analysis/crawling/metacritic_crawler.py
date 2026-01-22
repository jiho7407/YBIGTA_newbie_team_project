import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import re
import os
import csv

from review_analysis.crawling.base_crawler import BaseCrawler

class MetacriticCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://www.metacritic.com/movie/parasite/user-reviews/"
        self.driver = None
        self.target_count = 500
        self.data: list = []
    
    def start_browser(self):
        pass

    def scrape_reviews(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        reviews_data = []
        page = 0

        print(f"크롤링을 시작합니다... (목표: {self.target_count}개)")

        while True:
            if len(reviews_data) >= self.target_count:
                break

            url = f"{self.base_url}?page={page}"
            print(f"페이지 {page} 조회 중... (현재 유효 수집: {len(reviews_data)}/{self.target_count}개)")
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"페이지 접속 불가 (상태 코드: {response.status_code})")
                    break
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                review_elements = soup.find_all('div', class_='c-siteReview')
                
                if not review_elements:
                    print("더 이상 리뷰가 없습니다.")
                    break
                    
                for review in review_elements:
                    if len(reviews_data) >= self.target_count:
                        break

                    try:
                        # 1. 텍스트 및 스포일러 필터링
                        text_div = review.find('div', class_='c-siteReview_quote')
                        review_text = text_div.text.strip() if text_div else ""

                        if not review_text or "[SPOILER ALERT" in review_text:
                            continue
                        
                        # 2. 날짜 추출 (Regex)
                        date_pattern = re.search(r'[A-Z][a-z]{2}\s\d{1,2},\s\d{4}', review.text)
                        formatted_date = "N/A"
                        if date_pattern:
                            raw_date = date_pattern.group()
                            try:
                                dt_obj = datetime.strptime(raw_date, '%b %d, %Y')
                                formatted_date = dt_obj.strftime('%Y.%m.%d')
                            except ValueError:
                                formatted_date = raw_date
                        
                        # 3. 점수 추출 및 환산 (여기가 수정됨!)
                        score_div = review.find('div', class_='c-siteReviewScore')
                        raw_score = score_div.find('span').text.strip() if score_div else "0"
                        
                        try:
                            # 점수를 실수형(float)으로 변환 후 2로 나누기
                            final_score = float(raw_score) / 2
                            
                            # 소수점 끝이 .0이면 정수처럼 보이게 하기 (선택사항, 예: 5.0 -> 5)
                            # 원치 않으시면 아래 두 줄을 지우셔도 됩니다.
                            if final_score.is_integer():
                                final_score = int(final_score)
                                
                        except ValueError:
                            # 숫자가 아닌 경우 (예: tbd) 처리
                            final_score = "N/A"
                        
                        reviews_data.append({
                            "rating": final_score,
                            "date": formatted_date,
                            "content": review_text
                        })
                        
                    except Exception as e:
                        continue
                
                page += 1
                time.sleep(random.uniform(0.5, 1.2))
                
            except Exception as e:
                print(f"에러 발생: {e}")
                break
        self.data = reviews_data

    def save_to_database(self):
        if not self.data:
            print("저장할 데이터가 없습니다.")
            return

        # 폴더가 없을 시 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        keys = self.data[0].keys()
        filename = os.path.join(self.output_dir, 'reviews_metacritic.csv')
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"{filename}에 {len(self.data)}개의 리뷰 저장 완료.")