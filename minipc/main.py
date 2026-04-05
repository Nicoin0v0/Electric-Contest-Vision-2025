import cv2
import time
import modules.config as config
from modules.camera_manager import CameraManager
from modules.object_detector import ObjectDetector
from modules.gimbal_control import GimbalController
from modules.ui_control import UIControl  # 1. 导入 UI 控制模块

def main():
    print("=" * 70)
    print("        视觉追踪系统 v2.0 (带滑动条调试)")
    print("=" * 70)
    
    # ========== 1. 初始化各模块 ==========
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
    
    # ✅ 2. 初始化 UI 控制面板（滑动条）
    print("🎛️  初始化控制面板...")
    ui = UIControl()
    ui.create_trackbars('Controls')  # 这会弹出一个叫 Controls 的窗口
    
    print("\n" + "=" * 70)
    print("系统已就绪！")
    print("💡 提示：拖动 'Controls' 窗口滑动条可实时调整检测参数")
    print("按 'q' 退出，按 'c' 云台归中")
    print("=" * 70 + "\n")
    
    time.sleep(2)
    print("▶ 开始运行！\n")
    
    # ========== 3. 主循环 ==========
    while True:
        frame = camera.read()
        if frame is None:
            break
        
        # ✅ 3. 从滑动条获取最新参数，并同步给检测器
        thresh, min_area, max_area = ui.get_values()
        detector.update_params(thresh, min_area, max_area)
        
        # ✅ 4. 执行检测（注意：现在接收两个返回值！）
        # marked_frame: 画了框的图
        # binary: 二值化黑白图
        marked_frame, binary = detector.detect(frame)
        
        # ✅ 5. 云台控制
        if detector.detected:
            gimbal.look_at(detector.x_center, detector.y_center)
            cv2.putText(marked_frame, f"Tracking: ({detector.x_center:.0f}, {detector.y_center:.0f})", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(marked_frame, "Searching...", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # ✅ 6. 图像拼接与显示
        if binary is not None:
            # 将二值化图调整到与主图相同高度，方便拼接
            # 注意：binary 是单通道灰度图，需要转成 BGR 三通道才能和 marked_frame 拼接
            binary_resized = cv2.resize(binary, (marked_frame.shape[1], marked_frame.shape[0]))
            binary_bgr = cv2.cvtColor(binary_resized, cv2.COLOR_GRAY2BGR)
            
            # 上下拼接：上面是检测结果，下面是二值化原图
            display_frame = cv2.vconcat([marked_frame, binary_bgr])
        else:
            display_frame = marked_frame
            
        # 显示拼接后的大图
        cv2.imshow('Vision System', display_frame)
        
        # ✅ 7. 按键响应
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 退出程序...")
            break
        elif key == ord('c'):
            print("🔄 云台归中")
            gimbal.center()
    
    # ========== 4. 清理资源 ==========
    print("\n🔧 正在关闭硬件...")
    ui.destroy()          # 关闭滑动条窗口
    gimbal.disconnect()
    camera.release()
    cv2.destroyAllWindows()
    print("✓ 程序已安全退出")

if __name__ == '__main__':
    main()