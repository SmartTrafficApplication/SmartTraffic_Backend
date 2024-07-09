# client.py
'''
terminal => pip install imageio-ffmpeg ffmpeg-python
'''
# client.py
import requests
import subprocess
import imageio_ffmpeg as ffmpeg
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