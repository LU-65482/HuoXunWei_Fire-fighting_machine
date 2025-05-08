import asyncio
import websockets
import json
from robot_commander import * #导入需要用到的接口
# 配置参数
SERVER_HOST = "10.42.0.1"  # WebSocket服务器的主机地址
SERVER_PORT = 9090         # WebSocket服务器的端口

# 解析接收到的JSON数据
def parse_json(message):
    """解析JSON格式的消息"""
    try:
        data = json.loads(message)
        return data
    except json.JSONDecodeError as e:
        print(f"解析JSON失败: {e}")
        return None

# 发送JSON格式的消息
async def send_json(websocket, message):
    """发送JSON格式的消息"""
    try:
        data = json.dumps(message)
        await websocket.send(data)
        print(f"发送消息: {data}")
    except Exception as e:
        print(f"发送消息失败: {e}")
        
# 接收JSON格式的消息
async def receive_json(websocket):
    """接收并解析JSON格式的消息"""
    try:
        message = await websocket.recv()
        print(f"接收到消息: {message}")
        return parse_json(message)
    except Exception as e:
        print(f"接收消息失败: {e}")
        return None

async def set_speed(websocket,x,y,run_time):
    for i in range(run_time):
        await send_json(websocket,publish_velocity(x,y))#速度发布线速度
        print("发布了",i,"次速度")
        await asyncio.sleep(0.6)# 等待5秒
    

# 客户端连接到服务器并发送消息
async def connect_to_server():
    """连接到WebSocket服务器并发送消息"""
    try:
        # 连接到WebSocket服务器
        async with websockets.connect(f"ws://{SERVER_HOST}:{SERVER_PORT}") as websocket:
            # 发送消息
            await send_json(websocket, advertise_velocity_control())#广播一下
            await set_speed(websocket,0.0, 0.5, 4) #发布一个原地旋转速度发布4次
            await send_json(websocket, advertise_geometry_msgs_velocity_control())  # 广播导航控制
            #await send_json(websocket, publish_navi_goal_id(17.4, 3.3))#导航到目标点
            
            # 发布停止命令
            #await send_json(websocket, publish_velocity(0, 0))  # 停止命令
            # 接收响应
            response = await receive_json(websocket)
            print(f"收到响应: {response}")

    except Exception as e:
        print(f"连接失败: {e}")

# 启动WebSocket客户端
def run_client():
    """启动客户端的入口函数"""
    asyncio.run(connect_to_server())

# 启动客户端
if __name__ == "__main__":
    run_client()
