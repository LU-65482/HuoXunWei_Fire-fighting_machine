from machine import ADC, Pin, PWM
import time
import network
import socket

# 烟雾传感器配置
smoke_level = 1000  # 烟雾浓度阈值
smoke_pin = ADC(Pin(35))  # 使用GPIO32作为烟雾传感器的输入
smoke_pin.atten(ADC.ATTN_11DB)  # 11dB衰减，使测量范围大致变为：0 ~ 3.3V

# LED指示灯配置
red_pin = 18  # 红
green_pin = 19  # 绿
blue_pin = 21  # 蓝

# 蜂鸣器正极连接到GPIO 13
buzzer_pin = 13

# 初始化蜂鸣器
buzzer = Pin(buzzer_pin, Pin.OUT)

# 设置PWM频率为1000Hz以防止闪烁
red = PWM(Pin(red_pin), freq=1000, duty=0)
green = PWM(Pin(green_pin), freq=1000, duty=0)
blue = PWM(Pin(blue_pin), freq=1000, duty=0)

def beep(times):
    for _ in range(times):
        buzzer.on()
        time.sleep(0.3)  # 蜂鸣器响0.1秒
        buzzer.off()
        time.sleep(0.3)  # 休止0.1秒

def breathe_led(led, delay=0.01):
    for i in range(0, 1024, 16):  # 从暗到亮
        led.duty(i)
        time.sleep(delay)
    for i in range(1023, -1, -16):  # 从亮到暗
        led.duty(i)
        time.sleep(delay)

def set_color(red_duty, green_duty, blue_duty):
    """设置LED的颜色"""
    red.duty(red_duty)
    green.duty(green_duty)
    blue.duty(blue_duty)

# 蓝色灯提示开始连接WiFi
set_color(0, 0, 1023)
beep(1)
time.sleep(0.5)
set_color(1023, 0, 0)
beep(1)
time.sleep(0.5)
set_color(0, 1023, 0)
beep(1)
time.sleep(0.5)
while 1:
    smoke_value = smoke_pin.read()
    print("模拟信号值:", smoke_value, "输出电压:", round(smoke_value / 4095 * 3.3, 2), "V")

    if smoke_value > smoke_level:
        print("smoke_level > ", smoke_level, "Warning! Warning! Smoke alarm!")
        print("发送了烟雾警告消息")
        # 持续蜂鸣和呼吸灯效果
        buzzer.on()
        set_color(1023,0,0)
    else:
        set_color(0,0,0)
        buzzer.off()
        
    time.sleep(0.5)

