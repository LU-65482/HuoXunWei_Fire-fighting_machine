from machine import Pin, PWM
import time

# 假设引脚定义如下，你需要根据实际连接调整
red_pin = 18  # 红
green_pin = 19  # 绿
blue_pin = 21  # 蓝

# 设置PWM频率为1000Hz以防止闪烁
red = PWM(Pin(red_pin), freq=1000, duty=0)
green = PWM(Pin(green_pin), freq=1000, duty=0)
blue = PWM(Pin(blue_pin), freq=1000, duty=0)

def set_color(red_duty, green_duty, blue_duty):
    red.duty(red_duty)
    green.duty(green_duty)
    blue.duty(blue_duty)

while True:
    # 红色
    set_color(1023, 0, 0)  # 全亮度红色
    time.sleep(1)
    
    # 绿色
    set_color(0, 1023, 0)  # 全亮度绿色
    time.sleep(1)
    
    # 蓝色
    set_color(0, 0, 1023)  # 全亮度蓝色
    time.sleep(1)
