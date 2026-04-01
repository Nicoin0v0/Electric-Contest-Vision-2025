import cv2
import config

class CameraManager:
    def __init__(self):
        self.cap = None
        self.camera_id = None  # ← 不在这里检测
        
    def find_camera(self):
        """自动检测外接摄像头"""
        print("🔍 正在检测摄像头...")
        
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                if i >= 1 and fps >= 20:
                    print(f"✓ 找到外接摄像头：设备{i} - {width}x{height} @ {fps:.1f} FPS")
                    return i
        
        # 如果没有外接摄像头，使用第一个可用的
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                print(f"⚠ 使用内置摄像头：设备{i} - {width}x{height} @ {fps:.1f} FPS")
                return i
        
        return None
    
    def open(self):
        """打开摄像头"""
        # 决定使用哪个摄像头ID
        if config.CAMERA_ID is None:
            # 自动检测 ← 在这里才检测，不是 __init__
            self.camera_id = self.find_camera()
        else:
            self.camera_id = config.CAMERA_ID
            print(f"📷 使用手动指定的摄像头：设备{self.camera_id}")
        
        if self.camera_id is None:
            print("✗ 找不到摄像头！")
            return False
        
        self.cap = cv2.VideoCapture(self.camera_id)
        
        # 设置摄像头参数
        #self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        #self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        if not self.cap.isOpened():
            print("✗ 无法打开摄像头！")
            return False
        
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✓ 摄像头已启动：设备{self.camera_id}")
        print(f"  分辨率：{actual_width}x{actual_height} @ {fps:.1f} FPS")
        return True
    
    def read(self):
        """读取一帧图像"""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def release(self):
        """释放摄像头"""
        if self.cap is not None:
            self.cap.release()
            print("摄像头已关闭")