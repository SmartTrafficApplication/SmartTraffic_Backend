# extract_stream_url.py (selenium을 활용한 동적 크롤링)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def get_stream_url(page_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않음
    chrome_service = Service(executable_path='C:/chromedriver-win64/chromedriver.exe')  # chromedriver 경로

    with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
        driver.get(page_url)
        try:
            # 대기하면서 <video> 태그를 찾습니다
            video_tag = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            source_tag = video_tag.find_element(By.TAG_NAME, 'source')
            if source_tag and source_tag.get_attribute('src'):
                return source_tag.get_attribute('src')
            else:
                raise Exception("No video URL found in the page")
        finally:
            driver.quit()

page_url = 'http://www.utic.go.kr/view/map/openDataCctvStream.jsp?key=P5Av8fGLGztQQSuwPrnaRiWIhDDLanE0QFBa6QE4SCaCgnUVZXqChtReiKcsPTr6LAizzENcn6KDO9jDw&cctvid=L933107&cctvName=%25EC%2584%259C%25EC%259A%25B8%2520%25EA%25B0%2595%25EB%2582%25A8%2520%25EA%25B0%2595%25EB%2582%25A8%25EB%258C%2580%25EB%25A1%259C&kind=KB&cctvip=9999&cctvch=null&id=null&cctvpasswd=null&cctvport=null'
stream_url = get_stream_url(page_url)
print(f"Stream URL: {stream_url}")
