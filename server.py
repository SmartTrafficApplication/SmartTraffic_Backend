# server.py
# server.py
from flask import Flask, request
app = Flask(__name__)
@app.route('/upload', methods=['POST'])
def upload():
    def generate():
        while True:
            chunk = request.stream.read(8192)
            if not chunk:
                break
            yield chunk

    with open('received_stream.mp4', 'wb') as f:
        for chunk in generate():
            f.write(chunk)

    return 'File received', 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

# terminal => python server.py