import cv2
import time
import modules.config as config
from modules.camera_manager import CameraManager
from modules.object_detector import ObjectDetector
from modules.gimbal_control import GimbalController
from modules.ui_control import UIControl

def main():
    print("=" * 70)
    print("        视觉追踪系统 v2.0 (带滑动条调试)")
    print("=" * 70)
    
    # 1. 初始化各模块
    print("\n📷 初始化摄像头...")
    camera = CameraManager()
    if not camera.open():
        print("✗ 摄像头打开失败")
        return
    
    print("🔍 初始化检测器...")
    detector = ObjectDetector()
    
    print("🎯 初始化云台...")
    gimbal = GimbalController()
    gimbal.connect()
    
    # 2. 初始化 UI 控制面板
    print("🎛️  初始化控制面板...")
    ui = UIControl()
    ui.create_trackbars('Controls')
    
    print("\n" + "=" * 70)
    print("系统已就绪！")
    print("💡 提示：拖动 'Controls' 窗口滑动条可实时调整检测参数")
    print("按 'q' 退出，按 'c' 云台归中")
    print("=" * 70 + "\n")
    
    time.sleep(2)
    print("▶ 开始运行！\n")
    
    # 3. 主循环
    while True:
        frame = camera.read()
        if frame is None:
            break
        
        # 获取参数并同步给检测器
        thresh, min_area, max_area = ui.get_values()
        detector.update_params(thresh, min_area, max_area)
        
        # 执行检测
        marked_frame, binary = detector.detect(frame)
        
        # 云台控制与状态提示
        if detector.detected:
            gimbal.look_at(detector.x_center, detector.y_center)
            cv2.putText(marked_frame, f"Tracking: ({detector.x_center:.0f}, {detector.y_center:.0f})", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(marked_frame, "Searching...", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 图像拼接
        if binary is not None:
            binary_resized = cv2.resize(binary, (marked_frame.shape[1], marked_frame.shape[0]))
            binary_bgr = cv2.cvtColor(binary_resized, cv2.COLOR_GRAY2BGR)
            display_frame = cv2.vconcat([marked_frame, binary_bgr])
        else:
            display_frame = marked_frame
            
        # 显示主画面
        cv2.imshow('Vision System', display_frame)
        
        # 📌 关键补充：刷新滑动条面板（自绘控件必须手动调用 imshow 才能显示与交互）
        ui.show()
        
        # 按键响应
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 退出程序...")
            break
        elif key == ord('c'):
            print("🔄 云台归中")
            gimbal.center()
    
    # 4. 清理资源
    print("\n🔧 正在关闭硬件...")
    ui.destroy()
    gimbal.disconnect()
    camera.release()
    cv2.destroyAllWindows()
    print("✓ 程序已安全退出")

if __name__ == '__main__':
    main()