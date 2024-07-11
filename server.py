# server.py
import socket
import time
import os

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def start_server(host='0.0.0.0', port=9999, output_dir='received_videos'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        start_time = time.time()
        output_file = os.path.join(output_dir, f'received_stream_{get_timestamp()}.mp4')
        f = open(output_file, 'wb')
        print(f"Started new file: {output_file}")

        try:
            while True:
                client_socket.settimeout(10)  # 타임아웃 설정

                try:
                    data = client_socket.recv(16384)  # chunk_size와 동일하게 설정
                except socket.timeout:
                    print("Socket timeout, continuing...")
                    continue

                if not data:
                    print("No data received, closing connection")
                    break
                else:
                    print("Writing Data...")
                    f.write(data)

                current_time = time.time()
                if current_time - start_time > 9:
                    f.close()
                    print(f"Closed file: {output_file}")
                    output_file = os.path.join(output_dir, f'received_stream_{get_timestamp()}.mp4')
                    f = open(output_file, 'wb')
                    start_time = current_time
                    print(f"Started new file: {output_file}")
        finally:
            f.close()
            client_socket.close()
            print(f"Stream saved to {output_file}")

if __name__ == "__main__":
    start_server()
