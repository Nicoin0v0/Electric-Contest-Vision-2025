from machine import UART, Pin, PWM
import time

# 串口初始化
uart = UART(1, 115200, rx=9, tx=10)

# 舵机初始化
yaw_servo = PWM(Pin(11), freq=50)
pitch_servo = PWM(Pin(12), freq=50)

# 角度转 duty
def Servo(servo, angle):
    angle = max(-90, min(90, angle))
    duty = int(((angle + 90) * 2 / 180 + 0.5) / 20 * 1023)
    servo.duty(duty)
    return duty

# 当前位置 & 目标位置
current_yaw = 0.0
current_pitch = 0.0
target_yaw = 0.0
target_pitch = 0.0

# ========== 分段线性控制参数 (已调优防抽动) ==========
THRESH_FAST = 30.0
THRESH_MID  = 10.0
DEADBAND    = 1.2   # 覆盖舵机机械虚位与轻微抖动，避免反复微调

# YAW轴
KP_YAW_FAST = 0.85
KP_YAW_MID  = 0.45
KP_YAW_SLOW = 0.18  # 提升保持力，消除"漂移-慢补"现象

# PITCH轴
KP_PITCH_FAST = 0.5
KP_PITCH_MID  = 0.3
KP_PITCH_SLOW = 0.15

MAX_STEP = 1.5      # 略放宽防快速段卡顿
# ================================================

# ✅ 已删除开机归中代码，直接等待信号
print("✓ 系统就绪 (分段线性控制，取消开机归中)")

while True:
    if uart.any():
        try:
            data = uart.readline()
            if data is None: continue
            command = data.decode().strip()
            
            if command.startswith("ANGLE:"):
                values = command.split(":")[1].split(",")
                # 使用 -= 累加（相对运动模式）
                target_yaw -= float(values[0])
                target_pitch -= float(values[1])
                
                target_yaw = max(-90.0, min(90.0, target_yaw))
                target_pitch = max(-90.0, min(90.0, target_pitch))
                
        except Exception as e:
            print(f"Err: {e}")
    
    # ── YAW轴 ──
    err_yaw = target_yaw - current_yaw
    if abs(err_yaw) > DEADBAND:
        kp = KP_YAW_FAST if abs(err_yaw) > THRESH_FAST else (KP_YAW_MID if abs(err_yaw) > THRESH_MID else KP_YAW_SLOW)
        step = max(-MAX_STEP, min(MAX_STEP, err_yaw * kp))
        current_yaw += step
        current_yaw = max(-90.0, min(90.0, current_yaw))
        Servo(yaw_servo, current_yaw)
        
    # ── PITCH轴 ──
    err_pitch = target_pitch - current_pitch
    if abs(err_pitch) > DEADBAND:
        kp = KP_PITCH_FAST if abs(err_pitch) > THRESH_FAST else (KP_PITCH_MID if abs(err_pitch) > THRESH_MID else KP_PITCH_SLOW)
        step = max(-MAX_STEP, min(MAX_STEP, err_pitch * kp))
        current_pitch += step
        current_pitch = max(-90.0, min(90.0, current_pitch))
        Servo(pitch_servo, current_pitch)
        
    time.sleep(0.01)