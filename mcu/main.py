from machine import UART, Pin, PWM
import time

print("=" * 50)
print("        ESP32 云台控制系统")
print("=" * 50)

# 串口初始化
uart = UART(1, 115200, rx=9, tx=10)
print("✓ 串口已初始化")

# 舵机初始化
yaw_servo = PWM(Pin(12), freq=50)
pitch_servo = PWM(Pin(11), freq=50)
print("✓ 舵机已初始化 (YAW=GPIO12, PITCH=GPIO11)")

# 角度转 duty（带限位）
def Servo(servo, angle):
    angle = max(-90, min(90, angle))
    duty = int(((angle + 90) * 2 / 180 + 0.5) / 20 * 1023)
    servo.duty(duty)
    return duty

# ========== 启动时自动归中 ==========
print("\n🔄 舵机归中到 0 度位置...")
Servo(yaw_servo, 0)
Servo(pitch_servo, 0)
time.sleep(2)  # 等待 2 秒，确保归中完成
print("✓ 归中完成！")
# ===================================

print("\n" + "=" * 50)
print("✓ 系统就绪，等待串口数据...")
print("=" * 50 + "\n")

while True:
    if uart.any():
        try:
            data = uart.readline()
            command = data.decode().strip()
            
            if command.startswith("ANGLE:"):
                values = command.split(":")[1].split(",")
                yaw_angle = float(values[0])
                pitch_angle = float(values[1])
                
                yaw_duty = Servo(yaw_servo, yaw_angle)
                pitch_duty = Servo(pitch_servo, pitch_angle)
                
                print(f"✓ YAW={yaw_angle}°→{yaw_duty}, PITCH={pitch_angle}°→{pitch_duty}")
        
        except Exception as e:
            print(f"✗ 错误：{e}")
    
    time.sleep(0.01)