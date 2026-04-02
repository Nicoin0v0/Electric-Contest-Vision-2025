import cv2
import numpy as np
import modules.config as config

class ObjectDetector:
    def __init__(self):
        self.detected = False
        self.x_center = 0.0
        self.y_center = 0.0
        self.width = 0.0
        self.height = 0.0
        
        # --- 新增代码开始 ---
        self.threshold_val = 180  # 默认初始阈值
        self.trackbar_initialized = False # 标记滑动条是否已创建
        # --- 新增代码结束 ---
        
    def on_trackbar_change(self, x):
        """
        滑动条回调函数（OpenCV要求必须有一个回调，虽然我们可以不用它，直接读值）
        """
        pass

    def detect(self, image):
        """检测目标物体并返回中心点坐标"""
        try:
            # --- 新增代码：初始化滑动条 (只执行一次) ---
            if not self.trackbar_initialized:
                # 创建一个名为 'Binary' 的窗口（如果还没创建的话）
                cv2.namedWindow('Binary', cv2.WINDOW_NORMAL)
                
                # 创建滑动条
                # 参数说明: 'Threshold'(条的名字), 'Binary'(所在窗口), 
                # self.threshold_val(初始位置), 255(最大值), self.on_trackbar_change(回调)
                cv2.createTrackbar('Threshold', 'Binary', self.threshold_val, 255, self.on_trackbar_change)
                
                self.trackbar_initialized = True
            # --- 新增代码结束 ---

            # --- 新增代码：获取当前滑动条的值 ---
            # 每次 detect 运行时，都去读取一下滑动条当前的位置
            current_thresh = cv2.getTrackbarPos('Threshold', 'Binary')
            # ---------------------------------------

            # 1. 复制图像用于绘制
            marked_image = image.copy()
            
            # 2. 灰度化
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 3. 二值化：检测黑色
            # 【修改点】：将 config.THRESHOLD_VALUE 替换为 current_thresh
            _, binary = cv2.threshold(gray, current_thresh, 255, cv2.THRESH_BINARY_INV)
            
            # 4. 形态学操作（去噪）
            # kernel = np.ones((5, 5), np.uint8)
            # binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            # binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 5. 查找轮廓
            contours, hierarchy = cv2.findContours(
                binary, 
                cv2.RETR_TREE, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 初始化数据
            self.detected = False
            self.x_center = 0.0
            self.y_center = 0.0
            self.width = 0.0
            self.height = 0.0
            
            # 6. 找内轮廓（黑色边框的内侧边缘）
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                
                # 找所有有父轮廓的子轮廓（内边缘）
                inner_contours = []
                for i, contour in enumerate(contours):
                    if i < len(hierarchy):
                        parent_idx = hierarchy[i][3]  # 父索引
                        if parent_idx != -1:  # 有父轮廓 → 是内轮廓
                            inner_contours.append((contour, i))
                
                if inner_contours:
                    # 找到最大的内轮廓（白色卡片的外边缘）
                    inner_contours.sort(key=lambda x: cv2.contourArea(x[0]), reverse=True)
                    c, idx = inner_contours[0]
                    area = cv2.contourArea(c)
                    
                    # 调试日志
                    # print(f'内轮廓面积：{area:.0f}')
                    
                    # 7. 多边形拟合
                    epsilon = 0.04 * cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, epsilon, True)
                    
                    if len(approx) == 4:
                        # 8. 获取4个角点
                        pts = approx.reshape(4, 2)
                        
                        # 9. 计算两条对角线的真实交点
                        self.x_center, self.y_center = self.get_line_intersection(
                            pts[0], pts[2],
                            pts[1], pts[3]
                        )
                        
                        self.width = float(max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                        self.height = float(min(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                        self.detected = True
                        
                        # ========== 画图 ==========
                        # 10. 画实际轮廓（绿色）
                        cv2.drawContours(marked_image, [c], -1, (0, 255, 0), 2)
                        
                        # 11. 画拟合的四边形（蓝色）
                        cv2.polylines(marked_image, [pts], True, (255, 0, 0), 2)
                        
                        # 12. 画两条对角线（红色）
                        cv2.line(marked_image,
                                (int(pts[0][0]), int(pts[0][1])),
                                (int(pts[2][0]), int(pts[2][1])),
                                (0, 0, 255), 2)
                        cv2.line(marked_image,
                                (int(pts[1][0]), int(pts[1][1])),
                                (int(pts[3][0]), int(pts[3][1])),
                                (0, 0, 255), 2)
                        
                        # 13. 画中心点（黄色）
                        cv2.circle(marked_image, (int(self.x_center), int(self.y_center)), 6, (0, 255, 255), -1)
                        
                        # 14. 画4个角点（紫色）
                        for i, pt in enumerate(pts):
                            cv2.circle(marked_image, (int(pt[0]), int(pt[1])), 4, (255, 0, 255), -1)
                            cv2.putText(marked_image, str(i),
                                       (int(pt[0]) + 5, int(pt[1]) + 5),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                        
                        # 15. 显示信息
                        cv2.putText(marked_image, f'Center: ({self.x_center:.0f}, {self.y_center:.0f})',
                                   (int(self.x_center) - 60, int(self.y_center) - 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        print(f'✓ 检测到卡片！中心: ({self.x_center:.1f}, {self.y_center:.1f})')
                    else:
                        print(f'⚠ 不是四边形（边数：{len(approx)}）')
                        pass
                else:
                    print('⚠ 面积不合适')
                    pass
            else:
                print('⚠ 未找到轮廓')
                pass
            
            # --- 新增代码：在图像上显示当前的阈值数值 ---
            cv2.putText(marked_image, f'Thresh: {current_thresh}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # ---------------------------------------

            # 显示调试窗口
            cv2.imshow('Binary', binary)
            cv2.imshow('Detection', marked_image)
            cv2.waitKey(1)
            
            return marked_image
            
        except Exception as e:
            print(f'✗ 错误：{str(e)}')
            return image
    
    def get_line_intersection(self, p1, p2, p3, p4):
        """计算两条直线的交点"""
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])
        x3, y3 = int(p3[0]), int(p3[1])
        x4, y4 = int(p4[0]), int(p4[1])
        
        # 计算分母
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        # 如果分母为0，说明两条线平行，返回中点
        if denom == 0:
            return float((x1 + x2) / 2), float((y1 + y2) / 2)
        
        # 计算交点
        x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
        
        return float(x), float(y)
    
    def get_detection_data(self):
        """返回检测数据"""
        return {
            'x_center': self.x_center,
            'y_center': self.y_center,
            'width': self.width,
            'height': self.height,
            'detected': self.detected
        }