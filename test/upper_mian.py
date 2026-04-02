import cv2
from minipc.modules.camera_manager import CameraManager
from minipc.modules.object_detector import ObjectDetector
from communication.gimbal_control import GimbalController
import time  # ← 新增

def main():
    print("=" * 70)
    print("        视觉追踪系统")
    print("=" * 70)
    
    # ========== 1. 初始化摄像头 ==========
    print("\n📷 步骤 1：初始化摄像头...")
    camera = CameraManager()
    if not camera.open():
        print("✗ 摄像头打开失败")
        return
    
    # ========== 2. 初始化检测器 ==========
    print("\n🔍 步骤 2：初始化检测器...")
    detector = ObjectDetector()
    
    # ========== 3. 初始化云台（自动归中） ==========
    print("\n🎯 步骤 3：初始化云台...")
    gimbal = GimbalController()
    gimbal.connect()  # ← 这里会自动归中并等待 3 秒
    
    print("\n" + "=" * 70)
    print("系统已就绪！按 'q' 退出，按 'c' 云台归中")
    print("=" * 70 + "\n")
    
    # ========== 新增：启动后等待 2 秒再开始追踪 ==========
    print("⏳ 2 秒后开始追踪...")
    time.sleep(2)
    print("▶ 开始追踪！\n")
    # ==================================================
    
    # ========== 4. 主循环 ==========
    while True:
        frame = camera.read()
        if frame is None:
            break
        
        marked_frame = detector.detect(frame)
        
        if detector.detected:
            gimbal.look_at(detector.x_center, detector.y_center)
            
            info_text = f"Tracking: ({detector.x_center:.0f}, {detector.y_center:.0f})"
            cv2.putText(marked_frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Camera', marked_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 退出程序...")
            break
        elif key == ord('c'):
            gimbal.center()
    
    # ========== 5. 清理资源 ==========
    print("\n🔧 正在关闭...")
    gimbal.disconnect()
    camera.release()
    cv2.destroyAllWindows()
    print("✓ 程序已退出")

if __name__ == '__main__':
    main()