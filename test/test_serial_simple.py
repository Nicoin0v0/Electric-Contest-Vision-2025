import sys
import os
# 添加项目根目录到路径，这样才能从 test 文件夹导入 modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.serial_comm import SerialComm
import time

print("🔧 串口通信测试（角度模式）")
print("=" * 50)

ser = SerialComm()
if not ser.connect():
    print("✗ 串口连接失败")
    exit()

print("\n发送测试命令...")
print("观察舵机是否转动\n")

# 测试 1：归中（0 度）
print("测试 1：归中 (0°, 0°)")
ser.send_angle(0, 0)
time.sleep(2)

# 测试 2：向右（正角度）
print("测试 2：向右 (30°, 0°)")
ser.send_angle(30, 0)
time.sleep(2)

# 测试 3：向左（负角度）
print("测试 3：向左 (-30°, 0°)")
ser.send_angle(-30, 0)
time.sleep(2)

# 测试 4：向上（正角度）
print("测试 4：向上 (0°, 30°)")
ser.send_angle(0, 30)
time.sleep(2)

# 测试 5：向下（负角度）
print("测试 5：向下 (0°, -30°)")
ser.send_angle(0, -30)
time.sleep(2)

# 归中
print("测试 6：归中 (0°, 0°)")
ser.send_angle(0, 0)
time.sleep(1)

print("\n✅ 测试完成，已归中")

ser.disconnect()