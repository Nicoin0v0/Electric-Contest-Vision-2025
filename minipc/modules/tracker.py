# tracker.py
import cv2
import numpy as np
from . import config
from enum import IntEnum
from .kalman import KalmanFilter
from .transform import pixel_to_angle

class Status(IntEnum):
    LOST = 0
    TMP_LOST = 1
    TRACK = 2

class Tracker:
    def __init__(self):
        self.kf = KalmanFilter()           
        self.status = Status.LOST          
        self._last_kf_px = None            

    def process(self, detect_px=None):
        # 🔒 核心修复：如果已经是 LOST 且没检测到，直接拦截，防止 kf 重置导致状态跳变
        if self.status == Status.LOST and detect_px is None:
            return 0.0, 0.0, self.status

        # 更新卡尔曼内部状态
        self._last_kf_px = self.kf.step(detect_px)
        
        # 坐标切换逻辑
        if detect_px is not None:
            out_px = detect_px          # 检测到：用原始坐标
            self.status = Status.TRACK
        else:
            out_px = self._last_kf_px   # 丢失：用预测坐标
            if out_px is not None:
                self.status = Status.TMP_LOST
            else:
                self.status = Status.LOST
                return 0.0, 0.0, self.status
        
        # 像素转角度
        fx, fy = out_px
        fx += config.TRACKER_LASER_OFFSET_X
        fy += config.TRACKER_LASER_OFFSET_Y
        yaw, pitch = pixel_to_angle(fx, fy)
        
        # 死区防抖
        if abs(yaw) < config.TRACKER_DEADBAND: yaw = 0.0
        if abs(pitch) < config.TRACKER_DEADBAND: pitch = 0.0
        
        return yaw, pitch, self.status

    def draw_debug(self, frame, detect_px=None):
        if not config.TRACKER_DRAW_DEBUG or frame is None:
            return frame
        
        vis = frame.copy()
        
        # 1. 画卡尔曼预测点（蓝色十字）
        if self._last_kf_px is not None:
            fx, fy = int(self._last_kf_px[0]), int(self._last_kf_px[1])
            color = (255, 0, 0)
            cv2.line(vis, (fx-8, fy), (fx+8, fy), color, 2)
            cv2.line(vis, (fx, fy-8), (fx, fy+8), color, 2)
            cv2.circle(vis, (fx, fy), 3, color, -1)
        
        # 2. 画状态文字 
        y_pos = 25
        if self.status == Status.TRACK:
            color = (0, 255, 0)
            text = "Status: TRACK (Raw)"
        elif self.status == Status.TMP_LOST:
            color = (0, 165, 255)
            text = "Status: PREDICTING"
        else:
            color = (0, 0, 255)
            text = "Status: LOST"
            
        cv2.putText(vis, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # 3. 显示当前发送坐标
        if self._last_kf_px is not None:
            cv2.putText(vis, f'Send: ({self._last_kf_px[0]:.0f}, {self._last_kf_px[1]:.0f})', 
                       (10, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                       
        return vis

    def get_filtered_position(self):
        """获取当前卡尔曼滤波后的坐标（用于终端显示）"""
        return self._last_kf_px