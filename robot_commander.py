################## 订阅类 ##################
#消息广播 63页
def advertise_velocity_control():#底盘
    message = {
        "op": "advertise",
        "id": "velocity_control",
        "topic": "/cmd_vel_mux/input/teleop",
        "type": "geometry_msgs/Twist"
    }
    # print("已广播速度控制消息")    
    return message

#广播取消导航
def advertise_cancel_goal():
    message = {
        "op": "advertise",
        "id": "cancel_goal",
        "topic": "/move_base/cancel",
        "type": "actionlib_msgs/GoalID" 
    }
    return message

def advertise_geometry_msgs_velocity_control():#导航
    message = {
        "op": "advertise",
        "id": "send_goal",
        "topic": "/navi_goal",
        "type": "geometry_msgs/PoseStamped" 
    }
    return message

def unadvertise_navi_goal_velocity_control():
    message ={
        "op": "unadvertise",
        "id": "send_goal",
        "topic": "/navi_goal" 
    }
    return message

#订阅机器人全局状态 40页
def subscribe_robot_status():
    message = {
        "topic": "/robot_status",
        "type":
        "yutong_assistance/RobotStatus",
        "id": "get_robot_status",
        "op": "subscribe"
    }
    return message

#订阅机器人导航状态
def subscribe_navi_status_robot_status():
    message = {
        "topic": "/navi_status",
        "type": "actionlib_msgs/GoalStatus",
        "id": "get_map",
        "op": "subscribe" 
    }
    return message

#取消订阅机器人全局状态 41页
def unsubscribe_robot_status():
    message = {
        "op": "unadvertise",
        "id": "send_goal",
        "topic": "/navi_goal" 
    } 
    return message



################## 发布类 ##################
#底盘速度发布 63页
def publish_velocity(linear_x, angular_z):
    message = {
        "op": "publish",
        "topic": "/cmd_vel_mux/input/teleop",
        "id": "velocity_control",
        "msg": {
            "angular": {"z": angular_z},
            "linear": {"x": linear_x}
        }
    }
    print(f"发布速度控制: 线速度 {linear_x} m/s, 角速度 {angular_z} rad/s")
    return message

def publish_navi_goal_id(x,y):
    message = {
        "op": "publish",
        "topic": "/navi_goal",
        "id":"send_goal",
        "msg": {
            "header": {
                "frame_id": "map" 
            },
            "pose": {
                "position": {
                "x": x,
                "y": y,
                },
                "orientation": {"x": 0, "y": 0, "z": -0.0844636898107, "w": 0.996426557807}
                }
            }
        }
    return message
# orientation = {"x": 0,
#                 "y": 0,
#                 "z": -0.0844636898107,
#                 "w": 0.996426557807}
# await send_json(websocket, publish_navi_goal_id(4.0,1.5,orientation=orientation))

#取消导航
def publish_cancel_goal():
    message = {
        "op": "publish",
        "topic": "/move_base/cancel",
        "id": "cancel_goal",
        "msg": {
            "stamp": "",
            "id": "" 
            }
        }
    return message


