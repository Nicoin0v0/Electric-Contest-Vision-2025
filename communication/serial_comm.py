import serial
import time
import config

class SerialComm:
    """上位机串口通信 - 发送角度给 ESP32"""
    
    def __init__(self):
        self.ser = None
    
    def connect(self):
        """打开串口"""
        try:
            self.ser = serial.Serial(
                port=config.SERIAL_PORT, #串口号
                baudrate=config.BAUD_RATE, #波特率
                timeout=1
            )
            time.sleep(2)
            print(f"✓ 串口已打开：{config.SERIAL_PORT}")
            return True
        except Exception as e:
            print(f"✗ 打开失败：{e}")
            return False
    
    def send_angle(self, pan_angle, tilt_angle):
        """发送角度值给 ESP32"""
        if self.ser is None or not self.ser.is_open:
            print("✗ 串口未打开")
            return False
        
        try:
            # 发送格式：ANGLE:10.5,-5.2\n
            command = f"ANGLE:{pan_angle:.1f},{tilt_angle:.1f}\n"
            self.ser.write(command.encode())
            return True
        except Exception as e:
            print(f"✗ 发送失败：{e}")
            return False
    
    def disconnect(self):
        """关闭串口"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("串口已关闭")