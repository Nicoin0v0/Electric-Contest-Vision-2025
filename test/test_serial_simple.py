import sys
import os

# 1. 获取当前文件 (test_serial_simple.py) 的绝对路径
current_file = os.path.abspath(__file__)
# 2. 获取所在文件夹 (test)
test_dir = os.path.dirname(current_file)
# 3. 获取上一级文件夹 (camera_detector)
root_dir = os.path.dirname(test_dir)
# 4. 拼接 minipc 文件夹的路径 (因为 modules 在 minipc 里面)
minipc_path = os.path.join(root_dir, 'minipc')

# 5. 将 minipc 路径加入到系统路径的最前面
sys.path.insert(0, minipc_path)

# 现在就可以正常导入了
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