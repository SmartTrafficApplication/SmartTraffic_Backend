# client.py
import socket
import subprocess
import imageio_ffmpeg as ffmpeg
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def get_stream_url(page_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # 이미지 로드 비활성화

    chrome_service = Service(executable_path='C:/chromedriver-win64/chromedriver.exe')

    with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
        driver.get(page_url)
        try:
            video_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            source_tag = WebDriverWait(video_tag, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'source'))
            )
            if source_tag and source_tag.get_attribute('src'):
                return source_tag.get_attribute('src')
            else:
                raise Exception("No video URL found in the page")
        finally:
            driver.quit()

def stream_video_to_server(stream_url, server_address, chunk_size=16384, stream_duration=9):
    while True:
        print(f"Starting new FFmpeg process at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
        ffmpeg_command = [
            ffmpeg_exe,
            '-re',
            '-i', stream_url,
            '-c', 'copy',
            '-f', 'mpegts',
            'pipe:1'
        ]

        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        start_time = time.time()
        try:
            while True:
                data = process.stdout.read(chunk_size)
                if not data:
                    stderr_output = process.stderr.read().decode()
                    print(stderr_output)  # FFmpeg stderr 출력
                    break
                client_socket.sendall(data)
                print(f"Sent data chunk at {time.strftime('%Y-%m-%d %H:%M:%S')}")

                if time.time() - start_time >= stream_duration:
                    print(f"Restarting FFmpeg process at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    break
        finally:
            client_socket.close()
            process.terminate()
            print("FFmpeg process terminated")

page_url = 'http://www.utic.go.kr/view/map/openDataCctvStream.jsp?key=P5Av8fGLGztQQSuwPrnaRiWIhDDLanE0QFBa6QE4SCaCgnUVZXqChtReiKcsPTr6LAizzENcn6KDO9jDw&cctvid=L933107&cctvName=%25EC%2584%259C%25EC%259A%25B8%2520%25EA%25B0%2595%25EB%2582%25A8%2520%25EA%25B0%2595%25EB%2582%25A8%25EB%258C%2580%25EB%25A1%259C&kind=KB&cctvip=9999&cctvch=null&id=null&cctvpasswd=null&cctvport=null'
streaming_url = get_stream_url(page_url)

# 서버 주소 설정 (예: 로컬 호스트의 9999 포트)
server_address = ('localhost', 9999)

# 실시간 스트림을 서버로 전송
stream_video_to_server(streaming_url, server_address)
