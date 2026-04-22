import cv2
import modules.config as config


class CameraManager:
    """摄像头管理器：自动检测 + 参数配置 + 帧读取"""
    
    def __init__(self):
        """初始化：延迟检测摄像头设备"""
        self.cap = None              # OpenCV 视频捕获对象
        self.camera_id = None        # 摄像头设备号（None 表示自动检测）
        
    def find_camera(self):
        """自动扫描可用摄像头，优先选择外接高清设备"""
        print("🔍 正在检测摄像头...")
        
        # 1. 优先找外接摄像头（设备号>=1 且帧率>=20）
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                
                if i >= 1 and fps >= 20:
                    print(f"✓ 外接摄像头：设备{i} - {width}x{height} @ {fps:.1f} FPS")
                    return i
        
        # 2. 降级：使用第一个可用的摄像头（含内置）
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
        """打开摄像头并配置参数"""
        # 确定设备号：配置优先，否则自动检测
        if config.CAMERA_ID is None:
            self.camera_id = self.find_camera()
        else:
            self.camera_id = config.CAMERA_ID
            print(f"📷 使用指定摄像头：设备{self.camera_id}")
        
        if self.camera_id is None:
            print("✗ 找不到摄像头！")
            return False
        
        # 创建捕获对象
        self.cap = cv2.VideoCapture(self.camera_id)
        
        # 配置分辨率（其他参数按需启用）
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        if not self.cap.isOpened():
            print("✗ 无法打开摄像头！")
            return False
        
        # 打印实际生效的参数
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✓ 摄像头已启动：设备{self.camera_id}")
        print(f"  分辨率：{actual_width}x{actual_height} @ {fps:.1f} FPS")
        return True
    
    def read(self):
        """读取一帧图像，失败返回 None"""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def release(self):
        """释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()
            print("摄像头已关闭")