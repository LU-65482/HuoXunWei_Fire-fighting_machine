from machine import Pin
import time

# 将推杆链接到GPIO 13
put_push_rod_hight_pin = 13
put_push_rod_low_pin = 12
# 初始化
put_push_rod_hight = Pin(put_push_rod_hight_pin, Pin.OUT)
put_push_rod_low= Pin(put_push_rod_low_pin, Pin.OUT)
while True:
    #上
    print("up")
    put_push_rod_hight.on()
    put_push_rod_low.off()    
    time.sleep(1)
    #下
    print("down")
    put_push_rod_hight.off()
    put_push_rod_low.on()    
    time.sleep(1)
    #停止
    print("stop")
    put_push_rod_hight.off()
    put_push_rod_low.off()   
    time.sleep(1)