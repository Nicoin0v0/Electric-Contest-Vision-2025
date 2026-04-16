import serial
import time
import struct
import modules.config as config

class SerialComm:
    """上位机串口通信"""

    def __init__(self):
        self.ser = None

    def connect(self):
        """打开串口"""
        try:
            self.ser = serial.Serial(
                port=config.SERIAL_PORT,
                baudrate=config.BAUD_RATE,
                timeout=1
            )

            print(f"✅ 串口已打开：{config.SERIAL_PORT}")
            return True
        except Exception as e:
            print(f"❌ 串口打开失败：{e}")
            return False

    def send_angle(self, pan_angle, tilt_angle):
        """发送角度值给电控模块（二进制 int16 格式）"""
        if self.ser is None or not self.ser.is_open:
            print("❌ 串口未打开")
            return False

        try:
            # 1. 浮点数转 int16 (系数 100，保留 2 位小数)
            pan_int16 = int(pan_angle * 100)
            tilt_int16 = int(tilt_angle * 100)

            # 2. 限制 int16 范围 [-32768, 32767]
            pan_int16 = max(-32768, min(32767, pan_int16))
            tilt_int16 = max(-32768, min(32767, tilt_int16))

            # 3. 打包二进制帧：帧头(0xAA) + PAN(2字节) + TILT(2字节) = 5字节
            frame_header = b'\xAA'
            # '<hh' 表示小端序 + 两个有符号16位整数
            data = struct.pack('<hh', pan_int16, tilt_int16)
            packet = frame_header + data

            # 4. 发送
            self.ser.write(packet)
            # print(f"→ 发送: PAN={pan_angle:.1f}°({pan_int16}), TILT={tilt_angle:.1f}°({tilt_int16}) | {len(packet)}B")
            return True

        except Exception as e:
            print(f"❌ 发送失败：{e}")
            return False

    # ========== 旧版文本格式（已停用，保留参考） ==========
    # def send_angle(self, pan_angle, tilt_angle):
    #     """【旧版】发送文本格式 (如 ANGLE:3.14,-2.56\n)"""
    #     if self.ser is None or not self.ser.is_open:
    #         print("❌ 串口未打开")
    #         return False
    #     try:
    #         command = f"ANGLE:{pan_angle:.1f},{tilt_angle:.1f}\n"
    #         self.ser.write(command.encode('utf-8'))
    #         return True
    #     except Exception as e:
    #         print(f"❌ 发送失败：{e}")
    #         return False

    def disconnect(self):
        """关闭串口"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("✅ 串口已关闭")