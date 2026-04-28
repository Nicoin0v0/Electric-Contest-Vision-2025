import cv2
import numpy as np
import math
from . import config
from enum import IntEnum
from .kalman import KalmanFilter

class Status(IntEnum):
    LOST = 0
    TMP_LOST = 1
    TRACK = 2

class Tracker:
    def __init__(self):
        self.kf = KalmanFilter()
        self.status = Status.LOST
        self._last_kf_px = None

    def _convert_to_angles(self, px, py):
        """ 核心：像素坐标转云台偏航/俯仰角 (小孔成像模型)"""
        dx = px - config.CENTER_X
        dy = py - config.CENTER_Y
        
        # 水平偏航(Pan) & 垂直俯仰(Tilt)。图像Y向下，云台Y向上需取反
        yaw   = math.degrees(np.arctan2(dx, config.FOCAL_LENGTH_X))
        pitch = math.degrees(np.arctan2(dy, config.FOCAL_LENGTH_Y)) * -1.0
        
        #  安全限幅：防止舵机超程或指令越界
        return float(np.clip(yaw, -90.0, 90.0)), float(np.clip(pitch, -90.0, 90.0))
    
    def _estimate_distance_cm(self, target_pixel_height):
        """动态测距：用靶子像素高度反推真实距离 (Z轴)"""
        if target_pixel_height is None or target_pixel_height < 5:
            return config.DIST_EST_DEFAULT_CM
        dist = (config.TARGET_REAL_HEIGHT_CM * config.FOCAL_LENGTH_Y) / target_pixel_height
        return float(np.clip(dist, 20.0, 500.0))

    def _calc_laser_angles(self, px, py, dist_cm):
        """激光角度换算：3D坐标平移 + 视差修正"""
        # 像素 → 相机3D坐标
        X_cam = (px - config.CENTER_X) * dist_cm / config.FOCAL_LENGTH_X
        Y_cam = (config.CENTER_Y - py) * dist_cm / config.FOCAL_LENGTH_Y  # Y轴翻转
        Z_cam = dist_cm
        # 减去激光笔物理偏移
        X_rel = X_cam - config.LASER_PHYS_OFFSET_X_CM
        Y_rel = Y_cam - config.LASER_PHYS_OFFSET_Y_CM
        Z_rel = Z_cam
        # 反算激光所需角度
        yaw   = math.degrees(np.arctan2(X_rel, Z_rel))
        pitch = math.degrees(np.arctan2(Y_rel, Z_rel))
        return float(np.clip(yaw, -90.0, 90.0)), float(np.clip(pitch, -90.0, 90.0))

    def process(self, detect_px=None, target_h_px=None):
        """主处理流：状态拦截 → 卡尔曼滤波 → 坐标切换 → 角度转换 → 死区防抖"""
        #  拦截连续丢失，防止卡尔曼重置导致状态跳变
        if self.status == Status.LOST and detect_px is None:
            return 0.0, 0.0, self.status

        #  更新卡尔曼预测
        self._last_kf_px = self.kf.step(detect_px)
        
        #  坐标切换：检测到用实测值，丢失用预测值
        if detect_px is not None:
            out_px = detect_px
            self.status = Status.TRACK
        else:
            out_px = self._last_kf_px
            self.status = Status.TMP_LOST if out_px is not None else Status.LOST
            if self.status == Status.LOST:
                return 0.0, 0.0, self.status
        
        #  提取滤波后坐标
        fx, fy = out_px[0], out_px[1]
        
        #  角度转换：根据配置选择纯相机模型或激光补偿模型
        if config.USE_LASER_MODE:
            dist = self._estimate_distance_cm(target_h_px) if config.ENABLE_DIST_ESTIMATION else config.DIST_EST_DEFAULT_CM
            yaw, pitch = self._calc_laser_angles(fx, fy, dist)
        else:
            yaw, pitch = self._convert_to_angles(fx, fy)
        
        #  死区防抖：中心微小抖动不输出
        if abs(yaw) < config.TRACKER_DEADBAND: yaw = 0.0
        if abs(pitch) < config.TRACKER_DEADBAND: pitch = 0.0
        
        return yaw, pitch, self.status

    def draw_debug(self, frame, detect_px=None):
        if not config.TRACKER_DRAW_DEBUG or frame is None:
            return frame
        
        vis = frame.copy()
        cv2.circle(vis, (int(config.CENTER_X), int(config.CENTER_Y)), 4, (0, 0, 255), -1)
        
        #  画卡尔曼预测点（仅在有值时绘制）
        if self._last_kf_px is not None:
            fx, fy = int(self._last_kf_px[0]), int(self._last_kf_px[1])
            color = (255, 0, 0)
            cv2.line(vis, (fx-8, fy), (fx+8, fy), color, 2)
            cv2.line(vis, (fx, fy-8), (fx, fy+8), color, 2)
            cv2.circle(vis, (fx, fy), 3, color, -1)
            
        #  画状态文字
        y_pos = 25
        status_map = {
            Status.TRACK:    ("Status: TRACK", (0, 255, 0)),
            Status.TMP_LOST: ("Status: PREDICTING", (0, 165, 255)),
            Status.LOST:     ("Status: LOST", (0, 0, 255))
        }
        text, color = status_map.get(self.status, ("Status: UNKNOWN", (128, 128, 128)))
        cv2.putText(vis, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        #  显示发送坐标（仅在有值时显示）
        if self._last_kf_px is not None:
            cv2.putText(vis, f'Send: ({self._last_kf_px[0]:.0f}, {self._last_kf_px[1]:.0f})', 
                       (10, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                           
        return vis

    def get_filtered_position(self):
        return self._last_kf_px