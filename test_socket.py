import socket

HOST = '0.0.0.0'  # 监听所有可用接口
PORT = 8080        # 端口

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("服务器正在监听...")
    conn, addr = s.accept()
    with conn:
        print(f"连接来自 {addr}")
        while True:
            conn.sendall(b"hello")  # 发送消息给ESP32
            data = conn.recv(1024)       # 接收来自ESP32的消息
            if not data:
                break
            message = data.decode('utf-8')
            print(f"收到来自ESP32的消息: {message}")
            if message == "在呢":
                conn.sendall(b'im here')
            else:
                break  # 如果接收到非预期的消息，结束连接