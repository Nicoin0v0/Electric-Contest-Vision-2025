from machine import Pin, PWM
import time

print("=" * 60)
print("        舵机测试 - GPIO12 & GPIO11")
print("=" * 60)

# ========== 初始化舵机 ==========
# 频率 50Hz = 20ms 周期
yaw_servo = PWM(Pin(12), freq=50)
pitch_servo = PWM(Pin(11), freq=50)

print("✓ 舵机初始化完成 (freq=50Hz)")
print()

# ========== 角度转 duty cycle ==========
def angle_to_duty(angle):
    """
    角度 (-90° 到 90°) → duty cycle
    0.5ms → 25
    1.5ms → 512 (中点)
    2.5ms → 1023
    """
    # 限制角度范围
    angle = max(-90, min(90, angle))
    
    # 转换公式
    duty = int(((angle + 90) * 2 / 180 + 0.5) / 20 * 1023)
    return duty

# ========== 测试函数 ==========
def test_servo(name, servo, angle):
    duty = angle_to_duty(angle)
    print(f"{name:6} 角度: {angle:4}° → duty: {duty:4}")
    servo.duty(duty)

# ========== 开始测试 ==========
print("测试顺序：")
print("  1. 归中 (0°)")
print("  2. 左/上 (-90°)")
print("  3. 右/下 (90°)")
print("  4. 归中 (0°)")
print()
print("按 Ctrl+C 停止\n")

try:
    # 归中
    print("【归中】")
    test_servo("YAW", yaw_servo, 0)
    test_servo("PITCH", pitch_servo, 0)
    time.sleep(2)
    
    # -90度
    print("\n【-90°】")
    test_servo("YAW", yaw_servo, -90)
    test_servo("PITCH", pitch_servo, -90)
    time.sleep(2)
    
    # 90度
    print("\n【90°】")
    test_servo("YAW", yaw_servo, 90)
    test_servo("PITCH", pitch_servo, 90)
    time.sleep(2)
    
    # 归中
    print("\n【归中】")
    test_servo("YAW", yaw_servo, 0)
    test_servo("PITCH", pitch_servo, 0)
    time.sleep(1)
    
    print("\n✅ 测试完成")

except KeyboardInterrupt:
    print("\n\n⚠️  测试中断")
    # 归中
    yaw_servo.duty(512)
    pitch_servo.duty(512)

# 清理
yaw_servo.deinit()
pitch_servo.deinit()
print("✓ 舵机已释放")