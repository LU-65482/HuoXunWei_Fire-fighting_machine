#MG996舵机
import machine
import time

# 初始化PWM到GPIO15，频率50Hz
pwm = machine.PWM(machine.Pin(15))
pwm.freq(50)

# 定义函数将角度转换为PWM占空比
def angle_to_duty(angle):
    # 舵机脉冲宽度范围：20度到160度对应的角度范围
    # 一般情况下，180度对应2500us，0度对应500us
    # 转换为纳秒
    min_duty = 500000  # 500us对应0度
    max_duty = 2500000 # 2500us对应180度
    # 计算线性比例
    duty = min_duty + (angle / 180) * (max_duty - min_duty)
    return int(duty)

# 舵机循环动作
try:
    while True:
        # 设置舵机到50度
        pwm.duty_ns(angle_to_duty(50))
        print("50")
        time.sleep(1)
        # 设置舵机到100度
        pwm.duty_ns(angle_to_duty(100))
        print("100")
        time.sleep(1)
except KeyboardInterrupt:
    pwm.duty_ns(0)  # 停止PWM信号