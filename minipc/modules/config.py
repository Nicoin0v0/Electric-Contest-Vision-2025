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

# ============预处理参数============
GAUSSIAN_BLUR_KSIZE = 5          # 高斯模糊核大小（必须为奇数）
MORPH_CLOSE_KERNEL_SIZE = 3      # 闭运算核大小
MORPH_CLOSE_ITERATIONS = 2       # 闭运算迭代次数