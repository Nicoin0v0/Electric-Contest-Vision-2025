import cv2
import time
import modules.config as config
from modules.camera_manager import CameraManager
from modules.object_detector import ObjectDetector
from modules.tracker import Tracker, Status
from modules.serial_comm import SerialComm
from modules.ui_control import UIControl

def main():
    print("=" * 70)
    print("        视觉追踪系统")
    print("=" * 70)

    # 初始化
    print("\n 初始化摄像头...")
    camera = CameraManager()
    if not camera.open(): return
    
    print(" 初始化检测器...")
    detector = ObjectDetector()
    
    print(" 初始化 Tracker...")
    tracker = Tracker()
    
    print(" 初始化串口通信...")
    serial = SerialComm()
    if not serial.connect(): return
    
    print("  初始化控制面板...")
    ui = UIControl()
    ui.create_trackbars('Controls')
    
    print("\n 系统已就绪！按 'q' 退出")
    print("=" * 70 + "\n")

    #放在 while True: 之前（仅初始化一次）
    frame_cnt = 0
    last_printed_status = None  # 运行时状态变量，记录上次打印的状态，防丢失时刷屏

    while True:
        frame = camera.read()
        if frame is None: break
        
        thresh, min_area, max_area = ui.get_values()
        detector.update_params(thresh, min_area, max_area)
        marked_frame, binary = detector.detect(frame)
        detect_px = (detector.x_center, detector.y_center) if detector.detected else None
        
        #  Tracker 处理
        yaw, pitch, status = tracker.process(detect_px)

        # 1 串口发送（始终执行，不受打印开关影响）
        if status != Status.LOST:
            serial.send_angle(yaw, pitch)

        # 2 终端打印（受 config 控制，按你的要求：检测时持续发，丢失只发一次）
        if config.ENABLE_DEBUG_PRINT:
            if status != Status.LOST:
                send_px = tracker.get_filtered_position()
                coord_str = f"({send_px[0]:.0f}, {send_px[1]:.0f})" if send_px else "N/A"
                
                frame_cnt += 1
                if frame_cnt % config.PRINT_SKIP_FRAMES == 0:
                    print(f"[{status.name}] 坐标: {coord_str} -> 角度: yaw={yaw:6.2f}°, pitch={pitch:6.2f}°")
            else:
                # 丢失时：仅当状态首次变为 LOST 时打印一次
                if last_printed_status != Status.LOST:
                    print(f"[{status.name}] 目标丢失，暂停发送。等待重新识别...")
                    last_printed_status = status

        # 3 画面显示（保持不变）
        debug_frame = tracker.draw_debug(marked_frame, detect_px)
        if binary is not None:
            binary_resized = cv2.resize(binary, (debug_frame.shape[1], debug_frame.shape[0]))
            binary_bgr = cv2.cvtColor(binary_resized, cv2.COLOR_GRAY2BGR)
            display_frame = cv2.vconcat([debug_frame, binary_bgr])
        else:
            display_frame = debug_frame
            
        cv2.imshow('Vision System', display_frame)
        ui.show()
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 退出")
            break
    
    #  清理
    serial.disconnect()
    ui.destroy()
    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()