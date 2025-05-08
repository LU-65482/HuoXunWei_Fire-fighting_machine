from machine import Pin
import time

# 将灭火枪链接到GPIO 13
put_fire_HIGHT_pin = 13
put_fire_LOW_pin = 12
# 初始化灭火枪
put_fire_HIGHT = Pin(put_fire_HIGHT_pin, Pin.OUT)
put_fire_LOW = Pin(put_fire_LOW_pin, Pin.OUT)
while True:
    #上
    print("on")
    put_fire_HIGHT.on()
    put_fire_LOW.off()      
    time.sleep(2)  # 蜂鸣器响0.1秒
    
    #下
    print("off") 
    put_fire_HIGHT.off()
    put_fire_LOW.on()       
    time.sleep(2)  # 休止0.1秒
    put_fire_HIGHT.off()
    put_fire_LOW.off()       
    time.sleep(2)  # 休止0.1秒

