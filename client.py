# client.py
'''
terminal => pip install imageio-ffmpeg ffmpeg-python
'''
import requests # HTTP 요청을 보내기 위한 모듈
import subprocess # Python에서 새로운 프로세스를 생성하고 그 프로세스와 상호작용하기 위해 사용하는 모듈
import imageio_ffmpeg as ffmpeg # 멀티미디어 데이터의 녹화, 변환, 스트리밍 등을 수행하는 강력한 오픈 소스 소프트웨어
from extract_stream_url import get_stream_url

page_url = 'http://www.utic.go.kr/view/map/openDataCctvStream.jsp?key=P5Av8fGLGztQQSuwPrnaRiWIhDDLanE0QFBa6QE4SCaCgnUVZXqChtReiKcsPTr6LAizzENcn6KDO9jDw&cctvid=L933107&cctvName=%25EC%2584%259C%25EC%259A%25B8%2520%25EA%25B0%2595%25EB%2582%25A8%2520%25EA%25B0%2595%25EB%2582%25A8%25EB%258C%2580%25EB%25A1%259C&kind=KB&cctvip=9999&cctvch=null&id=null&cctvpasswd=null&cctvport=null'  # 스트리밍 URL을 여기에 입력하세요
streaming_url = get_stream_url(page_url)
flask_server_url = 'http://localhost:5000/upload'

ffmpeg_exe = ffmpeg.get_ffmpeg_exe()  # ffmpeg의 절대 경로를 가져옵니다
ffmpeg_command = [
    ffmpeg_exe,
    '-i', streaming_url,
    '-t', '600',  # 600초(10분) 동안 캡처
    '-c', 'copy',
    '-f', 'mpegts',  # MPEG-TS 포맷으로 변경
    'pipe:1'
]

# FFmpeg 프로세스를 실행하고 표준 출력과 표준 오류를 캡처
process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

response = requests.post(flask_server_url, data=process.stdout, headers={'Content-Type': 'application/octet-stream'})

# 에러 메시지 출력
stderr_output = process.stderr.read().decode()
print(stderr_output)

# 서버 응답 출력
print(response.text)


'''
terminal => python client.py
'''