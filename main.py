import cv2
from camera.camera_manager import CameraManager
from detector.object_detector import ObjectDetector
from communication.gimbal_control import GimbalController

def main():
    print("=" * 70)
    print("        视觉追踪系统")
    print("=" * 70)
    
    # ========== 1. 初始化摄像头 ==========
    print("\n📷 步骤1：初始化摄像头...")
    camera = CameraManager()
    if not camera.open():
        print("✗ 摄像头打开失败")
        return
    
    # ========== 2. 初始化检测器 ==========
    print("\n🔍 步骤2：初始化检测器...")
    detector = ObjectDetector()
    
    # ========== 3. 初始化云台 ==========
    print("\n🎯 步骤3：初始化云台...")
    gimbal = GimbalController()
    gimbal.connect()
    
    print("\n" + "=" * 70)
    print("系统已就绪！按 'q' 退出，按 'c' 云台归中")
    print("=" * 70 + "\n")
    
    # ========== 4. 主循环 ==========
    while True:
        # 读取图像
        frame = camera.read()
        if frame is None:
            break
        
        # 检测目标
        marked_frame = detector.detect(frame)
        
        # 如果检测到目标，让云台看向目标
        if detector.detected:
            # 调用 gimbal 的函数（所有云台逻辑都在 gimbal 里）
            gimbal.look_at(detector.x_center, detector.y_center)
            
            # 在画面上显示信息
            info_text = f"Tracking: ({detector.x_center:.0f}, {detector.y_center:.0f})"
            cv2.putText(marked_frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 显示窗口
        cv2.imshow('Camera', marked_frame)
        
        # 按键处理
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