from machine import Pin
import time

# 假设蜂鸣器的正极连接到GPIO 13
buzzer_pin = 13

# 初始化蜂鸣器
buzzer = Pin(buzzer_pin, Pin.OUT)

def alarm_sound(duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        # 模拟警报声的短促响声
        buzzer.on()
        time.sleep(0.5)  # 蜂鸣器响0.1秒
        buzzer.off()
        time.sleep(0.5)  # 休止0.1秒

while True:
    # 让蜂鸣器报警5秒作为示例
    alarm_sound(5)
    # 休息5秒，然后再次报警
    time.sleep(5)