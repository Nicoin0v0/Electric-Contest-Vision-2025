# ============ 摄像头配置 ============
CAMERA_ID = None
# CAMERA_ID = 1  # 摄像头设备号（Linux下通常是1，Windows下通常是0）
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ============ 识别配置 ============
THRESHOLD_VALUE = 180  # 二值化阈值
MIN_AREA = 1000  # 最小轮廓面积

# ============ 串口配置 ============
SERIAL_PORT = 'COM6'  # 请修改成你的实际串口号（如COM3、COM4）
BAUD_RATE = 115200    # 波特率

# ============ 相机参数（需要根据实际标定修改） ============
# 相机内参
FOCAL_LENGTH_X = 640  # 焦距（像素）
FOCAL_LENGTH_Y = 640
CENTER_X = 320        # 图像中心X
CENTER_Y = 240        # 图像中心Y

# 相机外参（相机安装角度）
CAMERA_PITCH = 0.0    # 相机俯仰角（度）
CAMERA_YAW = 0.0      # 相机偏航角（度）

# ============ 云台配置 ============
GIMBAL_PAN_MIN = 0    # 水平舵机最小角度
GIMBAL_PAN_MAX = 180  # 水平舵机最大角度
GIMBAL_TILT_MIN = 0   # 垂直舵机最小角度
GIMBAL_TILT_MAX = 180 # 垂直舵机最大角度

# ============ 舵机配置 ============
SERVO_MIN_PULSE = 500     # 最小脉冲宽度（微秒）
SERVO_MAX_PULSE = 2500    # 最大脉冲宽度（微秒）
SERVO_CENTER_PULSE = 1500 # 中点脉冲宽度（微秒）

# 舵机角度范围（0-180度）
# 0度对应最左边/最下边，180度对应最右边/最上边
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180