from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_stream_url(page_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않음
    chrome_service = Service(executable_path='C:/chromedriver-win64/chromedriver.exe')  # chromedriver 경로

    with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
        driver.get(page_url)
        try:
            # <video> 태그가 로드될 때까지 대기합니다
            video_tag = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            # <source> 태그가 로드될 때까지 대기합니다
            source_tag = WebDriverWait(video_tag, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'source'))
            )

            # source 태그의 src 속성을 반환합니다
            if source_tag and source_tag.get_attribute('src'):
                return source_tag.get_attribute('src')
            else:
                raise Exception("No video URL found in the page")
        finally:
            driver.quit()


page_url = 'http://www.utic.go.kr/view/map/openDataCctvStream.jsp?key=P5Av8fGLGztQQSuwPrnaRiWIhDDLanE0QFBa6QE4SCaCgnUVZXqChtReiKcsPTr6LAizzENcn6KDO9jDw&cctvid=L933107&cctvName=%25EC%2584%259C%25EC%259A%25B8%2520%25EA%25B0%2595%25EB%2582%25A8%2520%25EA%25B0%2595%25EB%2582%25A8%25EB%258C%2580%25EB%25A1%259C&kind=KB&cctvip=9999&cctvch=null&id=null&cctvpasswd=null&cctvport=null'
stream_url = get_stream_url(page_url)
print(f"Stream URL: {stream_url}")
