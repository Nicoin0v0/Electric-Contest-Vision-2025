# ============ 摄像头配置 ============
CAMERA_ID = None  # 摄像头设备号，None表示自动选择
# CAMERA_ID = 1  # 摄像头设备号（Linux下通常是1，Windows下通常是0）
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# ============ 识别配置 ============
THRESHOLD_VALUE = 87  # 二值化阈值
MIN_AREA = 7837        # 最小轮廓面积
MAX_AREA = 248648      # 最大轮廓面积

# ============ 串口配置 ============
SERIAL_PORT = '/dev/ttyS7'   # 请修改成你的实际串口号
BAUD_RATE = 115200     # 波特率

# ============ 相机内参（用于角度计算） ============
FOCAL_LENGTH_X = 640  # 焦距（像素）
FOCAL_LENGTH_Y = 640
CENTER_X = 320        # 图像中心X
CENTER_Y = 240        # 图像中心Y

# ============ 滑动条范围限制 ============
THRESHOLD_MAX = 255           # 二值化阈值最大只能是255
MIN_AREA_TRACKBAR_MAX = 100000   # 最小面积滑动条上限
MAX_AREA_TRACKBAR_MAX = 500000   # 最大面积滑动条上限

# ========== 卡尔曼滤波参数 ==========
KALMAN_DT = 0.033              # 初始时间间隔（30fps）
KALMAN_MAX_LOST_FRAMES = 30     # 最大允许丢失帧数
KALMAN_DT_MAX  = 0.5        # 允许的最大 dt (防卡顿预测爆炸)

# Q矩阵参数（过程噪声）
KALMAN_PROCESS_NOISE_POS = 0.1   # 位置的过程噪声
KALMAN_PROCESS_NOISE_VEL = 0.1   # 速度的过程噪声

# R矩阵参数（观测噪声）
# 设小一点：检测到时更相信视觉，减少平滑滞后
KALMAN_MEASUREMENT_NOISE = 0.5   

# 初始误差协方差
KALMAN_INITIAL_ERROR_COV = 100.0

# ========== Tracker 业务参数 ==========
TRACKER_DEADBAND = 0.8          # 角度死区(度)，防电机微抖
TRACKER_LASER_OFFSET_X = 0.0    # 激光笔水平视差补偿(像素)，未标定时填0
TRACKER_LASER_OFFSET_Y = 0.0    # 激光笔垂直视差补偿(像素)
TRACKER_DRAW_DEBUG = True       # 是否显示黄蓝点调试画面

# ========== 终端打印与调试配置 ==========
PRINT_SKIP_FRAMES = 3          # 检测到目标时，每隔几帧打印一次 (1=每帧, 3≈0.1秒, 5≈0.17秒)
ENABLE_DEBUG_PRINT = True      # 是否开启终端坐标/角度打印 (True/False)