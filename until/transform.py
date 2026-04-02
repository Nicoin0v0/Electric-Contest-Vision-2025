import numpy as np
import config

def pixel_to_angle(pixel_x, pixel_y):
    """像素坐标 → 角度"""
    dx = pixel_x - config.CENTER_X
    dy = pixel_y - config.CENTER_Y
    
    pan_angle = np.arctan2(dx, config.FOCAL_LENGTH_X) * 180 / np.pi
    tilt_angle = -np.arctan2(dy, config.FOCAL_LENGTH_Y) * 180 / np.pi
    
    pan_angle = max(-90, min(90, pan_angle))
    tilt_angle = max(-90, min(90, tilt_angle))
    
    return pan_angle, tilt_angle


def pixel_to_esp32_command(pixel_x, pixel_y):
    """只返回角度，不返回 duty"""
    pan_angle, tilt_angle = pixel_to_angle(pixel_x, pixel_y)
    
    return {
        'pan_angle': pan_angle,
        'tilt_angle': tilt_angle,
    }