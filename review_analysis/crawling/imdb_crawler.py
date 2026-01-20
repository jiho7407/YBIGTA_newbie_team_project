import time
import pandas as pd
import re
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from review_analysis.crawling.base_crawler import BaseCrawler
import os
from datetime import datetime

class IMDbCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.driver = None
        self.reviews_data: List[Dict] = []
        self.target_url = "https://www.imdb.com/title/tt6751668/reviews/?sort=submissionDate&dir=desc&ratingFilter=0"

        # [원상복구] 잘 작동하던 '리뷰 내용 박스'를 다시 메인 기준으로 잡습니다.
        self.SELECTOR_REVIEW_BOX = "div.ipc-list-card--border-speech"
        
        # [옆집 태그] 날짜가 들어있는 헤더 박스 (현종님이 찾아주신 태그)
        self.SELECTOR_DATE_HEADER = "div.sc-f5d9bc9e-1"

        self.SELECTOR_25_MORE_BTN = "//span[contains(@class, 'ipc-see-more')]//button"
        self.SELECTOR_SPOILER_BTN = "//button[contains(., 'Spoiler')]"
        self.SELECTOR_RATING = "span.ipc-rating-star--rating"
        self.SELECTOR_CONTENT = "div.ipc-html-content-inner-div"

    def start_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.get(self.target_url)
        print(f"Browser started. Navigate to {self.target_url}")
        time.sleep(3)

    def scrape_reviews(self):
        if not self.driver:
            self.start_browser()

        wait = WebDriverWait(self.driver, 15)
        target_count = 500

        print(f"Collecting reviews... Target: {target_count}")

        # 1. [데이터 로딩]
        while True:
            reviews = self.driver.find_elements(By.CSS_SELECTOR, self.SELECTOR_REVIEW_BOX)
            curr_cnt = len(reviews)
            print(f"Currently loaded: {curr_cnt} / {target_count}")

            if curr_cnt >= target_count:
                print("Target count reached! Stopping load.")
                break

            try:
                more_btn = wait.until(EC.element_to_be_clickable((By.XPATH, self.SELECTOR_25_MORE_BTN)))
                self.driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(1.5)
            except Exception:
                print("No more '25 more' button found. Stopping.")
                break

        # 2. [스포일러 펼치기]
        print("Expanding spoiler contents...")
        try:
            spoiler_btns = self.driver.find_elements(By.XPATH, self.SELECTOR_SPOILER_BTN)
            for btn in spoiler_btns:
                try:
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.05)
                except: pass
        except: pass

        # 3. [파싱]
        print("\nParsing reviews...")
        # 여기서 '리뷰 내용 박스'들을 가져옵니다. (이전과 동일)
        reviews = self.driver.find_elements(By.CSS_SELECTOR, self.SELECTOR_REVIEW_BOX)
        
        # 날짜 정규식 패턴
        date_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{1,2}),\s(\d{4})')

        for idx, review in enumerate(reviews[:target_count]):
            try:
                # [1] 내용 (기존 방식 그대로 - review 변수 안에서 찾음)
                try: 
                    content_el = review.find_element(By.CSS_SELECTOR, self.SELECTOR_CONTENT)
                    content = content_el.get_attribute('innerText').strip()
                except: content = ""

                # [2] 별점 (기존 방식 그대로)
                try: rating = review.find_element(By.CSS_SELECTOR, self.SELECTOR_RATING).text
                except: rating = None

                # [3] 날짜 (★ 핵심 변경: 부모를 통해 옆집 찾기)
                date = ""
                try:
                    # XPath 설명: ./.. (내 부모로 올라가서) //div[...] (그 안의 날짜 박스를 찾아라)
                    # 이렇게 하면 '리뷰 내용 박스' 기준으로 '날짜 박스'를 찾아낼 수 있습니다.
                    date_header_box = review.find_element(By.XPATH, f"./..//div[contains(@class, 'sc-f5d9bc9e-1')]")
                    
                    header_text = date_header_box.get_attribute('innerText')
                    
                    # 정규식으로 날짜 추출
                    match = date_pattern.search(header_text)
                    if match:
                        date_str = match.group(0)
                        date_obj = datetime.strptime(date_str, "%b %d, %Y")
                        date = date_obj.strftime("%Y%m%d")
                except Exception:
                    date = ""

                if content:
                    self.reviews_data.append({
                        "rating": rating,
                        "date": date,
                        "content": content
                    })
                
            except Exception:
                continue
        
        print(f"Total parsed reviews: {len(self.reviews_data)}")
        self.driver.quit()

    def save_to_database(self):
        if not self.reviews_data:
            print("No data to save.")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        filename = "reviews_imdb.csv"
        filepath = os.path.join(self.output_dir, filename)

        df = pd.DataFrame(self.reviews_data)
        df = df[['rating', 'date', 'content']]
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Saved {len(df)} reviews to {filepath}")