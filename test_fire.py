#火焰传感器模块
from machine import ADC, Pin
import time
import network
import socket

# 火焰传感器配置
fire_level = 409  # 这个阈值根据实际情况可能需要调整
fire_pin = ADC(Pin(32)) #使用GPIO32作为火焰传感器的输入
fire_pin.atten(ADC.ATTN_11DB)  # 11dB衰减，使测量范围大致变为：0 ~ 3.3V

while True:
    fire_value = fire_pin.read()
    print("模拟信号值:", fire_value, "输出电压:", round(fire_value / 4095 * 3.3, 2), "V")
    time.sleep(0.2)
#2025.1.12


