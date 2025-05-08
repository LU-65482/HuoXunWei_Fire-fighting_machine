import asyncio
import websockets
import json
import socket
import struct
import threading
import time
from robot_commander import *
from collections import defaultdict

# 服务器配置
SERVER_HOST = "10.42.0.1"  # WebSocket服务器主机地址  #与机器人的ip
SERVER_PORT = 9090         # WebSocket服务器端口

SERVER_IP = "10.42.0.94"   # 服务器（电脑）IP地址
SERVER_TCP_PORT = 8080     # TCP服务器端口，用于与ESP32通信

# ESP32客户端的IP地址
SMOKE1_SENSOR_IP = "10.42.0.122"  # 烟雾传感器1ESP32的IP
SMOKE2_SENSOR_IP = "10.42.0.51"  # 烟雾传感器2ESP32的IP
SMOKE3_SENSOR_IP = "10.42.0.23"  # 烟雾传感器3ESP32的IP

#XY_FIRE_TEST_IP = "10.42.0.171" #双火焰传感器ip

FIRE_SENSOR_IP = "10.42.0.171"    # 火焰传感器ESP32的IP
EXTINGUISHER_ESP32_IP = "10.42.0.177"  # 灭火装置控制的ESP32 IP 

PUSH_ROD_IP = "10.42.0.80"#推杆的IP
COMPUTER_IP="10.42.0.38"  #控制台的IP

# 使用defaultdict来存储每个客户端的状态，默认值为False
client_states = defaultdict(lambda: {"smoke_detected1": False, 
                                    "smoke_detected2": False, 
                                    "smoke_detected3": False, 
                                    "fire_detected": False, 
                                    "put_out": put,
                                    "computer":None,
                                    "navigating": "WAITING", 
                                    "siren":siren,
                                    "push_rod":push_rod,
                                    "servo":servo})


# 导航状态码
NAV_STATUS = {
    "WAITING": 600,  # 等待
    "NAVIGATING": 601,  # 导航进行中
    "FAILED": 602,  # 导航取消
    "SUCCESS": 603,  # 导航成功
    "CANCELLED": 604  # 导航失败
}
# 发送JSON格式的消息到WebSocket
async def send_json(websocket, message):
    """发送JSON格式的消息"""
    try:
        await websocket.send(json.dumps(message))
    except Exception as e:
        print(f"发送消息失败: {e}")

# 接收JSON格式的消息
async def receive_json(websocket):
    """接收并解析JSON格式的消息"""
    try:
        message = await websocket.recv()
        #print(f"接收到消息: {message}")
        return message
    except Exception as e:
        print(f"接收消息失败: {e}")
        return None

'''
《发布底盘速度函数》
【set_speed(websocket,x,y,run_time):】
            websocket:websocket
            x:前进速度 
            y:旋转速度 
            run_time:运行次数
每运行一次底盘发布0.6秒的速度
'''
async def set_speed(websocket,x,y,run_time): 

    for i in range(run_time):
        await send_json(websocket,publish_velocity(x,y))#速度发布线速度
        print("发布了",i,"次速度")
        await asyncio.sleep(0.6)
    

async def handle_messages(websocket):
    global put
    global siren
    global push_rod
    global servo
    global nav
    global fire
    global find_fire_num
    global duration
    global msg

    """处理来自ESP32的消息"""
    while True:
        msg = "等待火焰报警中"
        for client_ip, state in list(client_states.items()):
            #如果想要直接看到火就直接灭火就取消以下注释
            ## ----------------------------------------
            if client_ip == FIRE_SENSOR_IP:
               if state["fire_detected"] == True:
                   print("设置put为True")
                   put = True           
               if state["fire_detected"] == False:
                   print("设置put为False")
                   put = False
            # ----------------------------------------
            # 如果检测到烟雾且未开始导航，开始导航
            if state["smoke_detected1"] and nav == 0:   #如果烟雾1报警了，则发布导航
                msg = "开始发布导航点"
                siren = True  #警报灯响起
                servo = "servo_low" #低头
                await send_json(websocket, publish_navi_goal_id(1.09,-1.74))                
                print(f"客户端 {client_ip} 开始导航到目标点1")
                if state["navigating"] !=  NAV_STATUS["NAVIGATING"]:
                    msg = "请在手机检查机器人状态,是否被急停,或者重启服务器"
                    print("导航状态：",state["navigating"],"请在手机检查机器人状态,是否被急停,或者重启服务器")
                else:
                    msg = "出发到灭火点"
                    nav = 1  
            elif state["smoke_detected2"] and nav == 0: #如果烟雾2报警了，则发布导航
                siren = True
                servo = "servo_low"
                await send_json(websocket, publish_navi_goal_id(2.21,0.61))
                print(f"客户端 {client_ip} 开始导航到目标点2")
                if state["navigating"] !=  NAV_STATUS["NAVIGATING"]:
                    print("导航状态：",state["navigating"],"请在手机检查机器人状态,是否被急停,或者重启服务器")
                else:
                    nav = 1  
            elif state["smoke_detected3"] and nav == 0:   #如果烟雾3报警了，则发布导航
                siren = True
                servo = "servo_low"
                await send_json(websocket, publish_navi_goal_id(1.09,-1.74))
                print(f"客户端 {client_ip} 开始导航到目标点3")
                if state["navigating"] !=  NAV_STATUS["NAVIGATING"]:
                    print("导航状态：",state["navigating"],"请在手机检查机器人状态,是否被急停,或者重启服务器")
                else:
                    nav = 1  
                
            if state["navigating"] == NAV_STATUS["SUCCESS"] and nav == 1:  # 如果导航成功了 
                msg = "导航成功开始寻找火焰"
                if state["fire_detected"]:#如果看到了火焰
                    msg = "看到火焰了！开始灭火"
                    print(f"客户端 {client_ip} 发现火焰")       
                    push_rod = "stop"   #停止推杆
                    put = True          #打开水泵
                    #发布底盘需要的操作
                    await set_speed(websocket,0.0,0.3,2)
                    await set_speed(websocket,0.0,-0.3,3)
                    await set_speed(websocket,0.0,0.3,3)
                    await set_speed(websocket,0.0,-0.3,3)
                    fire = 1 #为了做完灭火动作在进行判断一次
                    
                else:
                    start_find_fire_time = time.time()#开始计时
                    msg = "还没看到火开始寻找火焰"
                    while True:
                        current_time = time.time()#记录现在的时间
                        duration = int(current_time - start_find_fire_time) #计算持续时间 = 当前时间 - 一开始的时间
                        msg = "开始记录时间"
                        if duration >= 3:
                            msg = "摆动头时间大于3秒"
                            find_fire_num += 1
                            #每检查3秒取反，实现舵机上下摆动
                            if state["servo"] == "servo_down" or state["servo"] == "servo_low" or state["servo"] == "servo_rest" or state["servo"] == "servo_stop":
                                msg = "发布舵机抬头寻找火源"
                                servo = "servo_up"
                                start_find_fire_time = time.time()
                            elif state["servo"] == "servo_up" or state["servo"] == "servo_low" or state["servo"] == "servo_rest" or state["servo"] == "servo_stop":
                                msg = "发布舵机低下头寻找火源"
                                servo = "servo_down"
                                start_find_fire_time = time.time()
                            #舵机上下摆动，还没看到火移动一次低盘
                            if find_fire_num >= 3:
                                msg = "没看到移动一次底盘"
                                find_fire_num = 0
                                await send_json(websocket, publish_velocity(0.0, -0.5))
                                await asyncio.sleep(0.6)
                                #start_find_fire_time = time.time()
                        if state["fire_detected"]:
                            msg = "看到火了"
                            servo = "servo_stop"
                            start_find_fire_time = time.time()
                            while True:     
                                msg = "发现火了,开始判断是上面看到火还是下面"
                                current_time = time.time()#记录现在的时间
                                duration = int(current_time - start_find_fire_time) #计算持续时间 = 当前时间 - 一开始的时间
                                if state["servo"] == "servo_down":
                                    start_find_fire_time = time.time()
                                    break
                                elif state["servo"] == "servo_up":#如果舵机抬头看到火
                                    servo = "servo_low"#先把舵机低头
                                    push_rod = "up"#开始升起推杆
                                    while state["fire_detected"]:#如果看到了火
                                        push_rod_total_time = duration
                                        push_rod = "stop"#就停止推杆
                                        break
                                    break
                            break   
                    await asyncio.sleep(0.1)
                        # 如果上下都没找到火焰，旋转底盘一次
            if fire == 1:#如果做完灭火动作还有火，就继续灭火
                msg = "再次判断"
                if state["fire_detected"] == True:
                    put = True
                    await set_speed(websocket,0.0,-0.3,3)
                    await set_speed(websocket,0.0,0.3,2)
                    await set_speed(websocket,0.0,-0.3,2)
                    await set_speed(websocket,0.0,0.3,3)                    
                else:#如果做完灭火动作没有火了，就取消灭火等待导航
                    msg = "已经都没有火啦"
                    servo = "servo_rest"
                    put = False #关闭水泵
                    fire = 0    #判断置零
                    nav = 0     #导航置零 
                    siren = False #关闭警报器
                    push_rod = "down" 
                    await asyncio.sleep(push_rod_total_time)#把推杆回位置推杆启动时间
                    push_rod = "stop" 
                    push_rod_total_time = 0
        await asyncio.sleep(0.5)  # 每秒检查一次状态      

async def connect_to_server():#与机器人链接
    """连接到WebSocket服务器并发送消息"""
    try:
        async with websockets.connect(f"ws://{SERVER_HOST}:{SERVER_PORT}", ping_interval=2, ping_timeout=20) as websocket:
            await send_json(websocket, advertise_velocity_control())  # 广播速度控制
            await send_json(websocket, subscribe_robot_status())  # 订阅机器人状态
            await send_json(websocket, advertise_geometry_msgs_velocity_control())  # 广播导航控制
            await send_json(websocket, advertise_cancel_goal())  # 广播取消导航控制
            await send_json(websocket, publish_velocity(0.0, 0.0))  # 发布初始速度
            asyncio.create_task(handle_messages(websocket))  # 在后台处理消息
            while True:
                response = await receive_json(websocket)
                #print(response)
                if response:
                    data = json.loads(response)
                    nav_status = data["msg"]["nav_status"]  # 获取导航状态
                    current_building_name = data["msg"]["current_building_name"] # 获取地图名字
                    #print('导航地图名：',current_building_name,'导航状态：',nav_status)
                    for client_ip in client_states:
                        client_states[client_ip]['navigating'] = nav_status  # 更新导航状态
    except Exception as e:
        print(f"连接失败: {e}")
        await asyncio.sleep(5)

def handle_client(conn,addr):#主机电脑与客户端链接
    """处理单个客户端的连接和消息接收"""
    client_ip = addr[0]
    global siren
    global put
    global push_rod
    global computer_message
    global fire_message
    global servo
    global nav
    global fire
    global find_fire_num
    global duration
    global msg
    try:
        with conn:
            #print(f"ESP32 连接来自 {client_ip}")
            client_states[client_ip] = {"smoke_detected1": False, 
                                        "smoke_detected2": False, 
                                        "smoke_detected3": False, 
                                        "fire_detected": False, 
                                        "put_out": put,
                                        "computer":None,
                                        "navigating": NAV_STATUS["WAITING"],
                                        "siren":siren,
                                        "push_rod":push_rod,
                                        "servo":servo}
            while True:
                try:
                    print("烟雾1",client_states[client_ip]["smoke_detected1"],
                        "烟雾2",client_states[client_ip]["smoke_detected2"],
                        "烟雾3",client_states[client_ip]["smoke_detected3"],
                        "火焰传感器",client_states[client_ip]["fire_detected"],
                        ":水枪状态",client_states[client_ip]["put_out"],
                        "计算机状态",client_states[client_ip]["computer"],
                        "机器人导航状态",client_states[client_ip]["navigating"],
                        "警报器状态",client_states[client_ip]["siren"],
                        "推杆状态",client_states[client_ip]["push_rod"],
                        "舵机角度状态",client_states[client_ip]["servo"],
                        "nav",nav,"fire",fire,"duration",duration,"find_fire_num",find_fire_num,"msg",msg)
                    
                    # 发送连接状态给ESP32
                    ##############################【舵机云台 状态处理】#########################
                    if client_states[client_ip]["servo"] == "servo_up":
                        conn.sendall(b"set_servo_up\n")
                        #print("----------------发送升高舵机云台")
                    elif client_states[client_ip]["servo"] == "servo_down":
                        conn.sendall(b"set_servo_down\n")
                        #print("----------------发送下降舵机云台")
                    elif client_states[client_ip]["servo"] == "servo_stop":
                        conn.sendall(b"set_servo_stop\n")
                        #print("----------------发送停止舵机云台")  
                    elif client_states[client_ip]["servo"] == "servo_low":
                        conn.sendall(b"set_servo_low\n")
                        #print("----------------发送低头舵机云台")  
                    elif client_states[client_ip]["servo"] == "servo_rest":
                        conn.sendall(b"set_servo_rest\n")
                        #print("----------------发送复位舵机云台")  
                    ####################################################################### 
                                        
                    ##############################【推杆 状态处理】#########################
                    if client_states[client_ip]["push_rod"] == "up":
                        conn.sendall(b"set_up\n")
                        #print("----------------发送升高推杆")
                    elif client_states[client_ip]["push_rod"] == "down":
                        conn.sendall(b"set_down\n")
                        #print("----------------发送下降推杆")
                    elif client_states[client_ip]["push_rod"] == "stop":
                        conn.sendall(b"set_stop\n")
                        #print("----------------发送停止推杆")
                        
                    #######################################################################  
                    
                    ##############################【水泵 状态处理】###########################
                    if client_states[client_ip]["put_out"]:
                        conn.sendall(b"put_fire\n")
                        #print("-------------发送打开水泵")
                    else:
                        conn.sendall(b"stop_put\n")
                        #print("发送关闭水泵-------------")
                    #######################################################################   
                    
                    ##############################【警报灯 状态处理】##########################
                    if client_states[client_ip]["siren"]:
                        conn.sendall(b"siren_open\n")
                        #print("-------------发送信号启动警报")
                    else:
                        conn.sendall(b"siren_close\n")
                        #print("发送信号关闭警报-------------")
                    #######################################################################   
                    
                    ##############################【烟雾报警器】#############################
                    if client_states[client_ip]["computer"] == "oneopen":
                        #print("发送oneopen")
                        conn.sendall(b"oneopen\n")
                    elif client_states[client_ip]["computer"] == "oneclose":
                        conn.sendall(b"oneclose\n")
                        #print("发送oneclose")

                    elif client_states[client_ip]["computer"] == "twoopen":
                        conn.sendall(b"twoopen\n")
                        #print("发送twoopen")
                    elif client_states[client_ip]["computer"] == "twoclose":
                        conn.sendall(b"twoclose\n")
                        #print("发送twoclose")
                        
                    elif client_states[client_ip]["computer"] == "threeopen":
                        conn.sendall(b"threeopen\n")
                        #print("发送threeopen")
                    elif client_states[client_ip]["computer"] == "threeclose":
                        conn.sendall(b"threeclose\n")
                        #print("发送threeclose")
                    ########################################################################
                    
                    #################################【推杆】################################
                    elif client_states[client_ip]["computer"] == "set_up":
                        push_rod = "up"
                        client_states[client_ip]["push_rod"] = "up"
                        conn.sendall(b"set_up\n")
                        #print("发送set_up")
                    elif client_states[client_ip]["computer"] == "set_down":
                        push_rod = "down"
                        client_states[client_ip]["push_rod"] = "down"
                        conn.sendall(b"set_down\n")
                        #print("发送set_down")
                    elif client_states[client_ip]["computer"] == "set_stop":
                        push_rod = "stop"
                        client_states[client_ip]["push_rod"] = "stop"
                        conn.sendall(b"set_stop\n")
                        #print("发送set_stop")
                    ########################################################################
                    
                    #################################【舵机云台】#############################
                    elif client_states[client_ip]["computer"] == "set_servo_up":
                        servo = "servo_up"
                        client_states[client_ip]["servo"] = "servo_up"
                        conn.sendall(b"set_servo_up\n")
                        #print("发送set_servo_up")
                    elif client_states[client_ip]["computer"] == "set_servo_down":
                        servo = "servo_down"
                        client_states[client_ip]["servo"] = "servo_down"
                        conn.sendall(b"set_servo_down\n")
                        #print("发送set_servo_down")
                    elif client_states[client_ip]["computer"] == "set_servo_stop":
                        servo = "servo_stop"
                        client_states[client_ip]["servo"] = "servo_stop"
                        conn.sendall(b"set_servo_stop\n")
                        #print("发送set_servo_stop")                    
                    elif client_states[client_ip]["computer"] == "servo_low":
                        servo = "servo_low"
                        client_states[client_ip]["servo"] = "servo_low"
                        conn.sendall(b"set_servo_low\n")
                        #print("----------------发送低头舵机云台")  
                    elif client_states[client_ip]["computer"] == "servo_rest":
                        servo = "servo_rest"
                        client_states[client_ip]["servo"] = "servo_rest"
                        conn.sendall(b"set_servo_rest\n")
                        #print("----------------发送复位舵机云台")  
                    #########################################################################
                    
                    #################################【水泵】#################################
                    elif client_states[client_ip]["computer"] == "put_fire":
                        put = True
                        client_states[client_ip]["put_out"] = put
                        conn.sendall(b"put_fire\n")
                    elif client_states[client_ip]["computer"] == "stop_put":
                        put = False
                        client_states[client_ip]["put_out"] = put
                        conn.sendall(b"stop_put\n")
                    #########################################################################
                    
                    #################################【警报灯】#################################
                    elif client_states[client_ip]["computer"] == "siren_open":
                        siren = True
                        client_states[client_ip]["siren"] = siren
                        conn.sendall(b"siren_open\n")
                    elif client_states[client_ip]["computer"] == "siren_close":
                        siren = False
                        client_states[client_ip]["siren"] = siren
                        conn.sendall(b"siren_close\n")               
                    #########################################################################
                    
                    # 接收数据，1024字节足够处理大多数消息
                    data = conn.recv(1024)
                    if not data:
                        break  # 没有数据表示连接关闭
                    # 解码接收到的数据
                    message = data.decode('utf-8')
                    #print(f"接收到来自 {client_ip}的消息: {message}")
                    # 根据消息和IP地址更新状态
                    if client_ip == SMOKE1_SENSOR_IP:
                        if message == "smoke_warning1!":
                            print("烟雾报警器1报警")
                            client_states[client_ip]["smoke_detected1"] = True
                        elif message == "not_smoke_warning1!":
                            client_states[client_ip]["smoke_detected1"] = False
                            
                    elif client_ip == SMOKE2_SENSOR_IP:
                        if message == "smoke_warning2!":
                            print("烟雾报警器2报警")
                            client_states[client_ip]["smoke_detected2"] = True
                        elif message == "not_smoke_warning2!":
                            client_states[client_ip]["smoke_detected2"] = False
                            
                    elif client_ip == SMOKE3_SENSOR_IP:
                        if message == "smoke_warning3!":
                            print("烟雾报警器3报警")
                            client_states[client_ip]["smoke_detected3"] = True
                        elif message == "not_smoke_warning3!":
                            client_states[client_ip]["smoke_detected3"] = False
                            
                    if client_ip == FIRE_SENSOR_IP:
                        if message == "find_fire!":
                            #print("发现了火焰")
                            fire_message = client_states[client_ip]["fire_detected"] = True
                        elif message == "not_find_fire!":
                            #print("没有发现火焰")
                            fire_message = client_states[client_ip]["fire_detected"] = False
                            
                    if client_ip == COMPUTER_IP:
                        computer_message = message
                        
                    client_states[client_ip]["push_rod"] = push_rod   
                    client_states[client_ip]["computer"] = computer_message
                    client_states[client_ip]["fire_detected"] = fire_message
                    client_states[client_ip]["put_out"] = put
                    client_states[client_ip]["siren"] = siren       
                    client_states[client_ip]["servo"] = servo             
                except Exception as e:
                    print(f"处理客户端 {client_ip}时出现错误: {e}")
                    break  # 发生错误时退出该客户端的处理循环
    finally:
        print(f"客户端 {client_ip}断开连接")

def tcp_server():
    """启动TCP服务器,管理多个客户端连接"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_IP, SERVER_TCP_PORT))
        s.listen()
        print(f"电脑服务器正在监听 {SERVER_IP}:{SERVER_TCP_PORT}")
        while True:
            conn, addr = s.accept()  # 接受新连接
            # 为每个新连接创建一个线程来处理
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    computer_message = None # 电脑信息
    fire_message = False    # 火焰信息
    put = False             # 水泵信息
    siren = False           # 警报器信息
    servo = "servo_stop"    # 舵机信息
    push_rod = "stop"       # 推杆信息
    find_fire_num = 0       # 寻找火焰次数
    duration = 0            # 寻找火焰时间
    push_rod_total_time = 0 # 记录总推杆启动时间
    nav = 0                 # 导航辅助变量，用于处理导航中的问题
    fire = 0                # 再次灭完火再次判断
    msg = None              # 消息日志
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    tcp_thread.start()
    asyncio.run(connect_to_server())
    
