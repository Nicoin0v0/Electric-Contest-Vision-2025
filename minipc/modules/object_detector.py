import cv2
import numpy as np
import modules.config as config

class ObjectDetector:
    def __init__(self):
        # 从 config 读取参数
        self.threshold_val = config.THRESHOLD_VALUE
        self.min_area = config.MIN_AREA
        # 增加最大面积，防止把整个画面当成目标
        self.max_area = config.MAX_AREA 
        
        self.detected = False
        self.x_center = 0.0
        self.y_center = 0.0
        self.width = 0.0
        self.height = 0.0
        
    def update_params(self, threshold=None, min_area=None, max_area=None):
        """外部调用此方法更新参数"""
        if threshold is not None:
            self.threshold_val = threshold
        if min_area is not None:
            self.min_area = min_area
        if max_area is not None:
            self.max_area = max_area

    def detect(self, image):
        try:
            marked_image = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)
            
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            self.detected = False
            self.x_center = 0.0
            self.y_center = 0.0
            
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                inner_contours = []
                
                for i, contour in enumerate(contours):
                    if i < len(hierarchy):
                        parent_idx = hierarchy[i][3]
                        if parent_idx != -1: 
                            inner_contours.append((contour, i))
                
                if inner_contours:
                    inner_contours.sort(key=lambda x: cv2.contourArea(x[0]), reverse=True)
                    c, idx = inner_contours[0]
                    area = cv2.contourArea(c)
                    
                    # 【修改点】：增加最大面积判断，形成范围过滤
                    if self.min_area < area < self.max_area:
                        epsilon = 0.04 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        
                        if len(approx) == 4:
                            pts = approx.reshape(4, 2)
                            self.x_center, self.y_center = self._get_intersection(pts[0], pts[2], pts[1], pts[3])
                            
                            self.width = float(max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                            self.height = float(min(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                            self.detected = True
                            
                            self._draw_contours(marked_image, c, pts)
            
            return marked_image, binary
            
        except Exception as e:
            print(f'Detect Error: {str(e)}')
            return image, None

    # ... (_get_intersection 和 _draw_contours 代码保持不变) ...
    def _get_intersection(self, p1, p2, p3, p4):
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])
        x3, y3 = int(p3[0]), int(p3[1])
        x4, y4 = int(p4[0]), int(p4[1])
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0: return float((x1 + x2) / 2), float((y1 + y2) / 2)
        x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
        return float(x), float(y)

    def _draw_contours(self, image, contour, pts):
        """绘制检测框、对角线、角点及中心"""
        # 1. 画实际轮廓（绿色）
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
        
        # 2. 画拟合的四边形（蓝色）
        cv2.polylines(image, [pts], True, (255, 0, 0), 2)
        
        # 3. 画两条对角线（红色）
        cv2.line(image, 
                 (int(pts[0][0]), int(pts[0][1])), 
                 (int(pts[2][0]), int(pts[2][1])), 
                 (0, 0, 255), 2)
        cv2.line(image, 
                 (int(pts[1][0]), int(pts[1][1])), 
                 (int(pts[3][0]), int(pts[3][1])), 
                 (0, 0, 255), 2)
        
        # 4. 画目标中心点（黄色）—— 这是算出来的坐标
        cv2.circle(image, (int(self.x_center), int(self.y_center)), 6, (0, 255, 255), -1)
        
        # 5. 画4个角点（紫色）并标序号 
        for i, pt in enumerate(pts):
            cv2.circle(image, (int(pt[0]), int(pt[1])), 4, (255, 0, 255), -1)
            cv2.putText(image, str(i), 
                        (int(pt[0]) + 5, int(pt[1]) + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        # ========== 新增：画图像中心点（白色） ==========
        h, w, _ = image.shape
        center_x, center_y = w // 2, h // 2
        
        # 画一个白色实心点
        cv2.circle(image, (center_x, center_y), 3, (255, 255, 255), -1)
        # 画一个白色空心圈，方便对比偏移量
        cv2.circle(image, (center_x, center_y), 10, (255, 255, 255), 1)
        # ============================================
        
        # 6. 显示目标信息
        cv2.putText(image, f'Target', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f'({self.x_center:.0f}, {self.y_center:.0f})',
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    def get_data(self):
        return {
            'x': self.x_center, 'y': self.y_center,
            'width': self.width, 'height': self.height,
            'detected': self.detected
        }