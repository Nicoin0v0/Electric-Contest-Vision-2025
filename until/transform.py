import numpy as np
import config

def pixel_to_angle(pixel_x, pixel_y):
    """
    像素坐标 → 云台偏转角度（-90 到 90 度）
    
    参数:
        pixel_x: 目标 X 像素坐标
        pixel_y: 目标 Y 像素坐标
    
    返回:
        (pan_angle, tilt_angle): 水平和垂直角度（度）
        正数=向右/向上，负数=向左/向下
    """
    # 1. 计算像素偏移
    dx = pixel_x - config.CENTER_X
    dy = pixel_y - config.CENTER_Y
    
    # 2. 转换为角度
    pan_angle = np.arctan2(dx, config.FOCAL_LENGTH_X) * 180 / np.pi
    tilt_angle = -np.arctan2(dy, config.FOCAL_LENGTH_Y) * 180 / np.pi
    
    # 3. 限制范围（-90 到 90 度）
    pan_angle = max(-90, min(90, pan_angle))
    tilt_angle = max(-90, min(90, tilt_angle))
    
    return pan_angle, tilt_angle


def angle_to_esp32_duty(angle):
    """
    角度 → ESP32 duty cycle（和你的 ESP32 代码一致）
    
    参数:
        angle: 角度（-90 到 90 度）
    
    返回:
        duty: ESP32 duty cycle（0-1023）
    """
    # 和你的 ESP32 代码完全一致的算法
    angle = max(-90, min(90, angle))
    step1 = angle + 90
    step2 = step1 * 2 / 180
    step3 = step2 + 0.5
    step4 = step3 / 20
    duty = int(step4 * 1023)
    
    return duty


def pixel_to_esp32_command(pixel_x, pixel_y):
    """
    像素坐标 → ESP32 控制命令（一步到位）
    
    参数:
        pixel_x: 目标 X 像素坐标
        pixel_y: 目标 Y 像素坐标
    
    返回:
        dict: 包含角度和 duty cycle 的字典
    """
    # 1. 像素 → 角度
    pan_angle, tilt_angle = pixel_to_angle(pixel_x, pixel_y)
    
    # 2. 角度 → duty cycle
    pan_duty = angle_to_esp32_duty(pan_angle)
    tilt_duty = angle_to_esp32_duty(tilt_angle)
    
    return {
        'pan_angle': pan_angle,
        'tilt_angle': tilt_angle,
        'pan_duty': pan_duty,
        'tilt_duty': tilt_duty
    }