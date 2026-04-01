from machine import UART, Pin, PWM
import time

print("=" * 50)
print("        ESP32 云台控制系统")
print("=" * 50)

# 串口初始化
uart = UART(1, 115200, rx=9, tx=10)
print("✓ 串口已初始化")

# 舵机初始化
yaw_servo = PWM(Pin(12))
pitch_servo = PWM(Pin(11))
yaw_servo.freq(50)
pitch_servo.freq(50)

print("✓ 舵机已初始化")

# 归中
yaw_servo.duty(512)
pitch_servo.duty(512)
print("🔄 舵机归中")

print("✓ 等待串口数据...")
print("=" * 50)

while True:
    if uart.any():
        try:
            data = uart.readline()
            command = data.decode().strip()
            
            if command.startswith("DUTY:"):
                values = command.split(":")[1].split(",")
                yaw_duty = int(values[0])
                pitch_duty = int(values[1])
                
                yaw_servo.duty(yaw_duty)
                pitch_servo.duty(pitch_duty)
                
                print(f"✓ YAW={yaw_duty}, PITCH={pitch_duty}")
        except Exception as e:
            print(f"✗ 错误：{e}")
    
    time.sleep(0.01)