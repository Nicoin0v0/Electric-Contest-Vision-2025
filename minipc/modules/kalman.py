import cv2
import numpy as np
import time
from . import config

class KalmanFilter:
    def __init__(self):
        self.dt = config.KALMAN_DT                # 当前时间步长
        self._last_time = None                    # 记录上次调用时间
        self.lost_count = 0                       # 连续丢失帧计数
        self.kf_x = self._init_1d_kf()            # 初始化X轴滤波器
        self.kf_y = self._init_1d_kf()            # 初始化Y轴滤波器

    def _init_1d_kf(self):
        kf = cv2.KalmanFilter(2, 1)               # 状态2维(位置,速度)，观测1维(位置)
        kf.transitionMatrix = np.array([[1, self.dt], [0, 1]], np.float32)  # 状态转移矩阵F
        kf.measurementMatrix = np.array([[1, 0]], np.float32)               # 观测矩阵H
        # 过程噪声协方差Q矩阵(对角阵)
        kf.processNoiseCov = np.diag([config.KALMAN_PROCESS_NOISE_POS, config.KALMAN_PROCESS_NOISE_VEL]).astype(np.float32)
        kf.measurementNoiseCov = np.array([[config.KALMAN_MEASUREMENT_NOISE]], np.float32)  # 观测噪声R
        kf.errorCovPost = np.eye(2, dtype=np.float32) * config.KALMAN_INITIAL_ERROR_COV     # 初始误差协方差P
        return kf

    def _update_dt(self, dt=None):
        if dt is None:
            now = time.time()                     # 获取当前系统时间
            if self._last_time is not None:
                dt = now - self._last_time        # 计算真实流逝间隔
                dt = min(dt, config.KALMAN_DT_MAX)# 限制最大间隔防预测发散
            else:
                dt = self.dt                      # 首次调用使用初始值
            self._last_time = now                 # 更新时间戳
        self.dt = dt                              # 保存当前dt
        self.kf_x.transitionMatrix[0, 1] = dt     # 动态更新F矩阵的dt参数
        self.kf_y.transitionMatrix[0, 1] = dt

    def predict(self, dt=None):
        self._update_dt(dt)                       # 计算并应用最新dt
        self.kf_x.predict()                       # 执行X轴预测
        self.kf_y.predict()                       # 执行Y轴预测
        return self.kf_x.statePre[0, 0], self.kf_y.statePre[0, 0]  # 返回预测坐标

    def update(self, measure):
        # 构造观测向量并修正X轴状态
        self.kf_x.correct(np.array([[np.float32(measure[0])]]))
        # 构造观测向量并修正Y轴状态
        self.kf_y.correct(np.array([[np.float32(measure[1])]]))
        return self.kf_x.statePost[0, 0], self.kf_y.statePost[0, 0]  # 返回修正后最优值

    def reset(self):
        self.kf_x.statePost = np.zeros((2, 1), np.float32)            # X轴状态归零
        self.kf_y.statePost = np.zeros((2, 1), np.float32)            # Y轴状态归零
        self.kf_x.errorCovPost = np.eye(2, dtype=np.float32) * config.KALMAN_INITIAL_ERROR_COV  # X轴P重置
        self.kf_y.errorCovPost = np.eye(2, dtype=np.float32) * config.KALMAN_INITIAL_ERROR_COV  # Y轴P重置
        self.lost_count = 0                       # 丢失计数清零
        self._last_time = None                    # 时间戳重置

    def step(self, measure=None):
        pred_x, pred_y = self.predict()           # 第一步：先预测
        if measure is not None:                   # 有检测数据则修正
            self.lost_count = 0                   # 重置丢失计数
            return self.update(measure)           # 返回修正后坐标
        else:                                     # 无检测数据则补帧
            self.lost_count += 1                  # 丢失计数+1
            if self.lost_count < config.KALMAN_MAX_LOST_FRAMES:
                return pred_x, pred_y             # 容忍范围内返回预测值
            else:
                self.reset()                      # 超限则重置滤波器
                return None                       # 停止输出