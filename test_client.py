import network
import socket
import time

SSID = 'fire_bot'
PASSWORD = '12345678'
SERVER_IP = '10.42.0.11'  # 更改为你的电脑IP
SERVER_PORT = 8080

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('连接到网络...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('网络配置：', wlan.ifconfig())

def client():
    do_connect()  # 确保ESP32连接到WiFi
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    print("连接到服务器成功！")
    
    while True:
        s.send(b"imesp32")
        data = s.recv(1024)  # 等待服务器消息
        if not data:
            break
        message = data.decode('utf-8')
        print(f"从服务器收到的消息: {message}")
        if message == "hello":
            s.send(b'im here')
            response = s.recv(1024)
            if response:
                print(f"从服务器收到的响应: {response.decode('utf-8')}")
           # break  # 完成通信后结束
        time.sleep(0.5)
if __name__ == '__main__':
    client()