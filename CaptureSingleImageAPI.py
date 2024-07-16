# integrated.py
import os
import time
import cv2
import requests
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

'''
요청을 보낼 때 응답이 되돌아오는 데 시간이 걸리는 이유는 Selenium을 사용하여 페이지에서 비디오 태그(비디오 URL)에 접근하는 과정과 OpenCV를 사용하여 비디오 프레임을 캡처하는 과정이 시간이 많이 소요되기 때문이다.

가능한 최적화 방법:
비디오 URL 캐싱: 비디오 URL을 매번 가져오지 않고 한 번 가져온 후 일정 시간 동안 캐싱한다.. 이렇게 하면 매번 Selenium을 사용하지 않아도 된다. (경찰청 제공 CCTV 송출 영상은 30초마다 변경됨)
비디오 프레임 캡처 최적화: 비디오 URL을 얻는 시간이 줄어들면 프레임 캡처에만 집중할 수 있게 된다.

정확히 말하면 비디오 URL이 자주 바뀌지 않는 한 일정 시간 동안 캐싱된 URL을 사용함으로써 
매번 크롤링을 수행하는 대신 캐싱된 URL을 재사용하여 응답 시간을 단축하는 것이다. 그러나 만약 URL이 자주 바뀐다면 이 캐싱 전략이 문제가 될 수 있다. 
'''
app = Flask(__name__)
output_dir = 'D:/PycharmProjects/received_images'  # 실시간 CCTV 영상 캡처 이미지를 저장할 경로
page_url = 'http://www.utic.go.kr/view/map/openDataCctvStream.jsp?key=P5Av8fGLGztQQSuwPrnaRiWIhDDLanE0QFBa6QE4SCaCgnUVZXqChtReiKcsPTr6LAizzENcn6KDO9jDw&cctvid=L933107&cctvName=%25EC%2584%259C%25EC%259A%B8%2520%25EA%25B0%2595%25EB%2582%A8%2520%25EA%25B0%2595%25EB%2582%A8%25EB%258C%2580%25EB%A1%259C&kind=KB&cctvip=9999&cctvch=null&id=null&cctvpasswd=null&cctvport=null'

video_url = None  # 비디오 URL 캐싱을 위한 전역 변수
last_fetched_time = 0  # 마지막으로 비디오 URL을 가져온 시간
url_cache_duration = 300  # URL 캐시 지속 시간 (초)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory {output_dir}")

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")  # 현재 시간 반환

def get_stream_url(page_url):
    global video_url, last_fetched_time
    current_time = time.time()

    # 캐시된 URL이 유효한 경우 캐시된 URL 반환
    if video_url and (current_time - last_fetched_time) < url_cache_duration:
        return video_url

    # 비디오 URL을 새로 가져와 캐싱
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Selenium을 활용한 크롤링시 브라우저를 표시하지 않음
    chrome_service = Service(executable_path='C:/chromedriver-win64/chromedriver.exe')  # chromedriver 경로

    with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
        driver.get(page_url)
        try:
            # <video> 태그가 로드될 때까지 대기
            video_tag = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            # <source> 태그가 로드될 때까지 대기
            source_tag = WebDriverWait(video_tag, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'source'))
            )

            # source 태그의 src 속성을 반환
            if source_tag and source_tag.get_attribute('src'):
                video_url = source_tag.get_attribute('src')
                last_fetched_time = current_time  # 마지막으로 가져온 시간 업데이트
                return video_url
            else:
                raise Exception("No video URL found in the page")
        finally:
            driver.quit()

def capture_frame(video_url):  # OpenCV를 활용하여 실시간 CCTV 영상 캡쳐 (단일 이미지 생성)
    cap = cv2.VideoCapture(video_url)
    ret, frame = cap.read()
    cap.release()
    if ret:  # ret이 존재하면 frame 반환
        return frame
    else:
        raise Exception("Failed to capture frame from video")

def send_image_to_upload(image):
    _, buffer = cv2.imencode('.jpg', image)  # .jpg 확장자로 인코딩
    files = {
        'image': ('capture.jpg', buffer.tobytes(), 'image/jpeg')
    }
    print("Sending image to /upload...")  # 로그 메시지 추가
    response = requests.post('http://localhost:5000/upload', files=files)
    if response.status_code == 200:
        print(f"Successfully sent image to /upload at {time.strftime('%Y-%m-%d %H:%M:%S')}")  # 성공 메시지 출력
    else:
        print(f"Failed to send image to /upload: {response.content}")  # 실패 메시지 출력

@app.route('/capture', methods=['GET'])
def capture_and_send_image():
    try:
        video_url = get_stream_url(page_url)  # 비디오 URL 동적 크롤링 또는 캐싱된 URL 사용
        frame = capture_frame(video_url)  # 비디오 프레임 캡처
        send_image_to_upload(frame)  # /upload 엔드포인트로 이미지 전송
        return jsonify({'message': 'Image captured and sent to /upload'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']
    print(f"Received file: {file.filename}")  # 파일 이름 출력

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    timestamp = get_timestamp()
    filename = f'received_image_{timestamp}.jpg'
    filepath = os.path.join(output_dir, filename)
    print(f"Saving file to {filepath}...")  # 파일 저장 전 메시지 출력

    try:
        file.save(filepath)
        print(f"File saved to {filepath}")  # 파일 저장 후 메시지 출력
    except Exception as e:
        print(f"Failed to save file: {e}")  # 파일 저장 실패 메시지 출력
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': f'Image saved to {filepath}'}), 200

'''
본 모듈이 import 되면 name이 main이 아니라 모듈명이 되고, import 되지 않고 실행되면 name이 main이 된다.
'''
if __name__ == "__main__":
    # 서버 시작 전에 비디오 URL을 미리 가져옴
    print("Fetching initial video URL...")
    video_url = get_stream_url(page_url)
    last_fetched_time = time.time()  # 서버 시작 시 마지막으로 가져온 시간 업데이트
    print(f"Initial video URL: {video_url}")
    app.run(host='0.0.0.0', port=5000)
