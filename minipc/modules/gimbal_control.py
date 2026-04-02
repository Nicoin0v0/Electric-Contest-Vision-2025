from modules.serial_comm import SerialComm
from modules.transform import pixel_to_esp32_command
import time

class GimbalController:
    """云台控制器"""
    
    def __init__(self):
        self.serial = SerialComm()
        self.connected = False
        self.last_send_time = 0
    
    def connect(self):
        """连接云台（自动归中）"""
        print("🔌 正在连接云台...")
        self.connected = self.serial.connect()
        
        if self.connected:
            print("✓ 云台已连接")
            print("🔄 正在归中到 0 度位置...")
            
            # 发送归中角度
            self.serial.send_angle(0, 0)
            
            # ========== 增加等待时间，让你能观察到 ==========
            print("⏳ 等待 3 秒，请观察舵机是否归中...")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print("✓ 归中完成！")
            # ================================================
        else:
            print("⚠ 云台连接失败")
        
        return self.connected
    
    def look_at(self, pixel_x, pixel_y):
        """让云台看向目标"""
        if not self.connected:
            return
        
        # 计算角度
        result = pixel_to_esp32_command(pixel_x, pixel_y)
        
        # 限制发送频率
        current_time = time.time()
        if current_time - self.last_send_time < 0.3:
            return
        
        # 发送角度
        self.serial.send_angle(result['pan_angle'], result['tilt_angle'])
        self.last_send_time = current_time
        
        print(f"→ 发送角度：PAN={result['pan_angle']:.1f}°, TILT={result['tilt_angle']:.1f}°")
    
    def center(self):
        """云台归中"""
        if self.connected:
            self.serial.send_angle(0, 0)
            print("🔄 云台归中")
    
    def disconnect(self):
        """断开连接"""
        self.serial.disconnect()