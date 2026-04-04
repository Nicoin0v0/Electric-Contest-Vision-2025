import cv2
import modules.config as config

class UIControl:
    def __init__(self):
        # 从 config 读取初始值（决定滑动条启动时停在哪里）
        self.threshold = config.THRESHOLD_VALUE
        self.min_area = config.MIN_AREA
        self.max_area = config.MAX_AREA
        self.initialized = False
        
    def create_trackbars(self, window_name='Controls'):
        """创建滑动条窗口"""
        if not self.initialized:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            # 1. 二值化阈值滑动条 (0-255)
            cv2.createTrackbar(
                'Threshold',           # 滑动条名字
                window_name,            # 窗口名字
                self.threshold,         # 初始位置（从 config 来）
                255,                    # 最大值（灰度图上限）
                self._dummy_callback    # 回调函数
            )
            
            # 2. 最小面积滑动条
            cv2.createTrackbar(
                'MinArea',
                window_name,
                self.min_area,          # 初始位置（从 config 来）
                100000,                 # 最大值（可以根据需要调整）
                self._dummy_callback
            )
            
            # 3. 最大面积滑动条
            cv2.createTrackbar(
                'MaxArea',
                window_name,
                self.max_area,          # 初始位置（从 config 来）
                500000,                 # 最大值（可以根据需要调整）
                self._dummy_callback
            )
            
            self.initialized = True
    
    def _dummy_callback(self, x):
        """滑动条回调函数（OpenCV 要求必须有，可以空着）"""
        pass
    
    def get_values(self):
        """
        获取当前滑动条的值
        返回: (threshold, min_area, max_area)
        """
        if self.initialized:
            self.threshold = cv2.getTrackbarPos('Threshold', 'Controls')
            self.min_area = cv2.getTrackbarPos('MinArea', 'Controls')
            self.max_area = cv2.getTrackbarPos('MaxArea', 'Controls')
        
        return self.threshold, self.min_area, self.max_area
    
    def destroy(self):
        """销毁窗口"""
        cv2.destroyWindow('Controls')