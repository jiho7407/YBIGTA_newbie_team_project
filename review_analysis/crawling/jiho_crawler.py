from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import csv
import re
from datetime import datetime, timedelta

from review_analysis.crawling.base_crawler import BaseCrawler

class JihoCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.rottentomatoes.com/m/parasite_2019/reviews/all-audience'
        self.driver = None
        
    def start_browser(self):
        """브라우저 시작 메서드 구현"""
        chrome_service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service)
        self.driver.get(self.base_url)
        time.sleep(2) # 혹시모르니께

    def convert_date(date_str):
        now = datetime.now()
        date_str = date_str.lower().strip()

        try:
            if 'd' in date_str: # 1d ~ 6d 전
                target_date = now - timedelta(days=int(date_str.replace('d', '')))
            elif 'h' in date_str:
                target_date = now
            elif '/' not in date_str: # 올해
                target_date = datetime.strptime(f"{now.year} {date_str}", "%Y %b %d")
            else:
                target_date = datetime.strptime(date_str, "%m/%d/%Y")
            return target_date.strftime("%Y.%m.%d")
        except Exception as e:
            print(f"날짜 변환 오류: {e} - 입력값: {date_str}")
            return date_str

    
    def scrape_reviews(self):
        if self.driver is None:
            self.start_browser()

        driver = self.driver
        data = []

        # Privacy Policy 동의 버튼 클릭
        privacy_button = driver.find_element("css selector", 'button#onetrust-accept-btn-handler')
        privacy_button.click()
        time.sleep(2)

        while len(driver.find_elements("css selector", 'review-card')) < 500:
            try:
                # 스크롤
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # load more 버튼 찾아서 누르기
                btn = driver.execute_script("""
                    return document.querySelector('rt-button[data-qa="load-more-btn"]') || 
                           document.querySelector('[data-qa="load-more-btn"]') ||
                           Array.from(document.querySelectorAll('rt-button')).find(b => b.textContent.includes('Load More'));
                """)

                if btn:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)
                    print("더 보기 클릭 성공, 다음 데이터 로딩 중...")
                    time.sleep(2)
                else:
                    print("더 이상 클릭할 버튼이 없습니다.")
                    break
            except Exception as e:
                print(f"로딩 중단: {e}")
                break


        # review-card 요소들 수집
        review_host_cards = driver.find_elements("css selector", 'review-card')
        
        for host in review_host_cards:
            try:
                # 별점, 날짜, 내용 추출
                rating = host.find_element("css selector", '[slot="rating"]').get_attribute("score").strip()
                date = host.find_element("css selector", '[slot="timestamp"]').text.strip()
                date = JihoCrawler.convert_date(date)
                raw_content = host.find_element("css selector", '[slot="review"]').text
                content = raw_content.split("Content collapsed")[0].replace("See More", "").strip()
                
                if content:
                    data.append({
                        'rating': rating,
                        'date': date,
                        'content': content
                    })
                    print(f"수집 성공: {date} | {rating}")
            except Exception as e:
                # 정보가 누락된 카드는 건너뜁니다
                print(f"수집 실패: {e}")
                continue

        print(f"총 {len(data)}개의 리뷰 수집")
        self.data = data
        return data

            
    def save_to_database(self):
        keys = self.data[0].keys()
        filename = "reviews_rotten.csv"
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.data)
        print(f"{filename}에 {len(self.data)}개의 리뷰 저장 완료.")

if __name__ == "__main__":
    crawler = JihoCrawler(output_dir='../../database')
    # crawler.start_browser()
    crawler.scrape_reviews()
    crawler.save_to_database()