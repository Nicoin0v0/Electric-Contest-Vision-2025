import cv2
import modules.config as config
from modules.camera_manager import CameraManager
from modules.object_detector import ObjectDetector
from modules.tracker import Tracker, Status
from modules.serial_comm import SerialComm
from modules.ui_control import UIControl

def main():
    print("=" * 70)
    print("        视觉追踪系统 v2.0")
    print("=" * 70)

    #  1. 模块初始化
    camera  = CameraManager()
    if not camera.open(): return
    detector = ObjectDetector()
    tracker  = Tracker()
    serial   = SerialComm()
    if not serial.connect(): return
    ui       = UIControl()
    ui.create_trackbars('Controls')
    
    print("\n✅ 系统已就绪！按 'q' 退出")
    print("=" * 70)

    #  2. 运行状态追踪（防终端刷屏）
    frame_cnt = 0
    last_status = None

    while True:
        frame = camera.read()
        if frame is None: break
        
        # 更新检测参数
        thresh, min_area, max_area, otsu_val = ui.get_values()
        detector.update_params(thresh, min_area, max_area, use_otsu=bool(otsu_val))
        
        # 目标检测 (修复原代码重复调用两次的问题)
        marked_frame, binary = detector.detect(frame)
        detect_px = (detector.x_center, detector.y_center) if detector.detected else None
        
        # 获取靶子像素高度（根据你的 detector 实际属性名调整，通常是 .height 或 .h）
        h_px = detector.height if detector.detected else None
        
        # Tracker处理 (传入高度用于动态测距)
        yaw, pitch, status = tracker.process(detect_px, target_h_px=h_px)

        # 串口下发 (非LOST状态始终发送预测/实测角度)
        if status != Status.LOST:
            serial.send_angle(yaw, pitch)

        # 终端打印 (受config控制，跟踪时周期打印，丢失仅打印一次)
        if config.ENABLE_DEBUG_PRINT:
            if status != Status.LOST:
                frame_cnt += 1
                if frame_cnt % config.PRINT_SKIP_FRAMES == 0:
                    px = tracker.get_filtered_position()
                    coord = f"({px[0]:.0f}, {px[1]:.0f})" if px is not None else "N/A"
                    print(f"[{status.name}] 像素: {coord} -> 角度: yaw={yaw:6.2f}°, pitch={pitch:6.2f}°")
            else:
                if last_status != Status.LOST:
                    print(f"[{status.name}] 目标丢失，暂停发送。等待重新识别...")
            last_status = status  #  每帧更新状态记录，防止状态切换时重复打印

        # 画面渲染与显示
        debug_frame = tracker.draw_debug(marked_frame, detect_px)
        if binary is not None:
            bin_resized = cv2.resize(binary, (debug_frame.shape[1], debug_frame.shape[0]))
            display_frame = cv2.vconcat([debug_frame, cv2.cvtColor(bin_resized, cv2.COLOR_GRAY2BGR)])
        else:
            display_frame = debug_frame
            
        cv2.imshow('Vision System', display_frame)
        ui.show()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n👋 安全退出")
            break

    # 资源释放
    serial.disconnect()
    ui.destroy()
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()