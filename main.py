# '''
# terminal => pip install Flask requests
#
# terminal => pip install torch==1.13.0+cu116 torchvision==0.14.0+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
#
# terminal => pip install opencv-python-headless tensorflow keras matplotlib
#
# terminal => pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cu116/torch1.13/index.html
#
# terminal => pip install opencv-python-headless
#
# terminal =>
# git clone --branch 2.x https://github.com/open-mmlab/mmdetection.git
# cd mmdetection
# python setup.py install
# '''
#
#
# from flask import Flask, Response, stream_with_context
# import requests
# import cv2
# import numpy as np
# import torch
# import tensorflow as tf
# from mmdet.apis import init_detector, inference_detector, show_result_pyplot
# import mmcv
# import tempfile
# from PIL import Image
#
# app = Flask(__name__)
#
# # Initialize mmdetection model
# config_file = '/path/to/faster_rcnn_config.py'  # Update with the path to your config file
# checkpoint_file = '/path/to/faster_rcnn_checkpoint.pth'  # Update with the path to your checkpoint file
# model = init_detector(config_file, checkpoint_file, device='cuda:0')
#
# # Load the autoencoder model
# autoencoder = tf.keras.models.load_model('/path/to/convolutional_autoencoder_result')
#
# # index 경로는 비디오 스트림을 표시하는 비디오 태그가 포함된 HTML 페이지를 반환한다.
# @app.route('/', methods=['GET'])
# def index():
#     return '''
#         <html>
#             <body>
#                 <h1>비디오 스트림</h1>
#                 <video width="640" height="480" controls>
#                     <source src="/video_feed" type="video/mp4">
#                     브라우저가 비디오 태그를 지원하지 않습니다.
#                 </video>
#             </body>
#         </html>
#     '''
#
# # video_feed 경로는 requests 라이브러리를 사용하여 제공된 URL에서 비디오 스트림을 가져와 클라이언트에게 스트리밍한다.
# # # requests 라이브러리를 사용하여 스트리밍된 콘텐츠를 클라이언트에게 전달하기 위해 사용된다. response 객체의 iter_content 메서드를 사용하여 응답 내용을 지정된 크기(여기서는 1024 바이트)로 청크 단위로 반복 처리한다. 이렇게 하면 큰 파일이나 스트림 데이터를 메모리 과부하 없이 처리할 수 있다.
# # stream_with_context 함수는 제너레이터 함수 generate가 Flask 요청 컨텍스트 내에서 실행되도록 보장한다.
# @app.route('/video_feed', methods=['GET'])
# def video_feed():
#     def generate():
#         stream_url = "http://www.utic.go.kr/view/map/cctvStream.jsp?cctvid=L010254&cctvname=%25EC%259D%2584%25EC%25A7%2580%25EB%25A1%259C1%25EA%25B0%2580&kind=Seoul&cctvip=null&cctvch=52&id=169&cctvpasswd=null&cctvport=null&minX=126.97229479455277&minY=37.55911420366164&maxX=126.99102641496832&maxY=37.57294479307399"
#         response = requests.get(stream_url, stream=True)
#
#         byte_stream = b''
#         for chunk in response.iter_content(chunk_size=1024):
#             byte_stream += chunk
#             start_idx = byte_stream.find(b'\xff\xd8')
#             end_idx = byte_stream.find(b'\xff\xd9')
#
#             if start_idx != -1 and end_idx != -1:
#                 jpg = byte_stream[start_idx:end_idx + 2]
#                 byte_stream = byte_stream[end_idx + 2:]
#
#                 # Convert to numpy array
#                 img = np.frombuffer(jpg, dtype=np.uint8)
#                 frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
#
#                 # Perform inference with mmdetection
#                 result = inference_detector(model, frame)
#
#                 # Resize and preprocess the frame for autoencoder
#                 resized_frame = cv2.resize(frame, (300, 300)).astype('float32') / 255.0
#                 resized_frame = np.expand_dims(resized_frame, axis=0)
#
#                 # Get reconstruction from autoencoder
#                 reconstructed_frame = autoencoder.predict(resized_frame)
#
#                 # Calculate reconstruction loss
#                 mse = tf.keras.losses.MeanSquaredError()
#                 reconstruction_loss = mse(resized_frame, reconstructed_frame).numpy()
#
#                 # Visualize detection results using show_result_pyplot
#                 with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
#                     show_result_pyplot(model, frame, result, out_file=temp_file.name)
#                     temp_file.seek(0)
#                     jpeg_data = temp_file.read()
#
#                 # Send the result to the client
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n\r\n')
#
#     return Response(stream_with_context(generate()), content_type='multipart/x-mixed-replace; boundary=frame')
#
# @app.route('/send_to_spring', methods=['GET'])
# def send_to_spring():
#     def generate():
#         stream_url = "http://www.utic.go.kr/view/map/cctvStream.jsp?cctvid=L010254&cctvname=%25EC%259D%2584%25EC%25A7%2580%25EB%25A1%259C1%25EA%25B0%2580&kind=Seoul&cctvip=null&cctvch=52&id=169&cctvpasswd=null&cctvport=null&minX=126.97229479455277&minY=37.55911420366164&maxX=126.99102641496832&maxY=37.57294479307399"
#         response = requests.get(stream_url, stream=True)
#
#         byte_stream = b''
#         for chunk in response.iter_content(chunk_size=1024):
#             byte_stream += chunk
#             start_idx = byte_stream.find(b'\xff\xd8')
#             end_idx = byte_stream.find(b'\xff\xd9')
#
#             if start_idx != -1 and end_idx != -1:
#                 jpg = byte_stream[start_idx:end_idx + 2]
#                 byte_stream = byte_stream[end_idx + 2:]
#
#                 # Convert to numpy array
#                 img = np.frombuffer(jpg, dtype=np.uint8)
#                 frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
#
#                 # Perform inference with mmdetection
#                 result = inference_detector(model, frame)
#
#                 # Resize and preprocess the frame for autoencoder
#                 resized_frame = cv2.resize(frame, (300, 300)).astype('float32') / 255.0
#                 resized_frame = np.expand_dims(resized_frame, axis=0)
#
#                 # Get reconstruction from autoencoder
#                 reconstructed_frame = autoencoder.predict(resized_frame)
#
#                 # Calculate reconstruction loss
#                 mse = tf.keras.losses.MeanSquaredError()
#                 reconstruction_loss = mse(resized_frame, reconstructed_frame).numpy()
#
#                 # Visualize detection results using show_result_pyplot
#                 with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
#                     show_result_pyplot(model, frame, result, out_file=temp_file.name)
#                     temp_file.seek(0)
#                     jpeg_data = temp_file.read()
#
#                     # Send the frame to Spring server
#                     requests.post('http://your-spring-server/video_feed',
#                                   files={'file': ('frame.jpg', jpeg_data, 'image/jpeg')})
#
#                     # Send the result to the client
#                     yield (b'--frame\r\n'
#                            b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n\r\n')
#
#     return Response(stream_with_context(generate()), content_type='multipart/x-mixed-replace; boundary=frame')
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
#
# # terminal => python main.py
# # web browser => http://localhost:5000

##########################################################################################

