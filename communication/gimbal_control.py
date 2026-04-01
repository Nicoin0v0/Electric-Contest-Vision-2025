from communication.serial_comm import SerialComm
from until.transform import pixel_to_esp32_command
import time

class GimbalController:
    """云台控制器 - 所有云台相关逻辑都在这里"""
    
    def __init__(self):
        self.serial = SerialComm()
        self.connected = False
        self.last_send_time = 0
    
    def connect(self):
        """连接云台（初始化串口 + 归中）"""
        print("🔌 正在连接云台...")
        self.connected = self.serial.connect()
        
        if self.connected:
            print("✓ 云台已连接")
            print("🔄 云台归中...")
            self.serial.send_duty(512, 512)
            time.sleep(1)
        else:
            print("⚠ 云台连接失败，将仅显示数据")
        
        return self.connected
    
    def look_at(self, pixel_x, pixel_y):
        """
        让云台看向目标位置
        
        参数:
            pixel_x: 目标 X 像素坐标
            pixel_y: 目标 Y 像素坐标
        """
        if not self.connected:
            return
        
        # 1. 像素坐标 → 角度 → duty（调用 transform.py）
        result = pixel_to_esp32_command(pixel_x, pixel_y)
        
        # 2. 限制发送频率（每 0.3 秒发一次，避免过快）
        current_time = time.time()
        if current_time - self.last_send_time < 0.3:
            return
        
        # 3. 通过串口发送给 ESP32
        self.serial.send_duty(result['pan_duty'], result['tilt_duty'])
        self.last_send_time = current_time
        
        # 4. 打印信息
        print(f"→ 发送：YAW={result['pan_duty']}, PITCH={result['tilt_duty']}")
    
    def center(self):
        """云台归中"""
        if self.connected:
            self.serial.send_duty(512, 512)
            print("🔄 云台归中")
    
    def disconnect(self):
        """断开连接"""
        self.serial.disconnect()
        print("串口已关闭")