import cv2
import numpy as np
import modules.config as config


class ObjectDetector:
    """矩形目标检测器：轮廓筛选 + 几何校验"""
    
    def __init__(self):
        """初始化检测参数"""
        # 阈值参数
        self.threshold_val = config.THRESHOLD_VALUE
        self.min_area = config.MIN_AREA
        self.max_area = config.MAX_AREA
        
        # 预处理参数
        self.blur_ksize = config.GAUSSIAN_BLUR_KSIZE
        self.close_kernel_size = config.MORPH_CLOSE_KERNEL_SIZE
        self.close_iterations = config.MORPH_CLOSE_ITERATIONS
        
        # 检测结果
        self.detected = False
        self.x_center = 0.0
        self.y_center = 0.0
        self.width = 0.0
        self.height = 0.0
        
    def update_params(self, threshold=None, min_area=None, max_area=None):
        """外部调用：动态更新检测参数"""
        if threshold is not None:
            self.threshold_val = threshold
        if min_area is not None:
            self.min_area = min_area
        if max_area is not None:
            self.max_area = max_area

    def detect(self, image):
        try:
            marked_image = image.copy()
            
            # 1. 高斯模糊
            blurred = cv2.GaussianBlur(image, (self.blur_ksize, self.blur_ksize), 0)
            gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
            
            # 2. 二值化（灰度逻辑）
            _, binary = cv2.threshold(gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)
            
            # 3. 闭运算
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.close_kernel_size, self.close_kernel_size))
            closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=self.close_iterations)
            
            # 4. 轮廓提取（改用 RETR_CCOMP，匹配参考代码）
            contours, hierarchy = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            # 重置状态（放在检测开始前）
            self.detected = False
            self.x_center = 0.0
            self.y_center = 0.0
            
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                
                # 父子轮廓降级策略
                inner_contours = []
                for i, contour in enumerate(contours):
                    if i < len(hierarchy) and hierarchy[i][3] != -1:
                        inner_contours.append((i, contour))
                
                # 如果没有内轮廓，则使用外轮廓（无父轮廓的轮廓）
                target_contours = inner_contours if inner_contours else \
                    [(i, c) for i, c in enumerate(contours) if i < len(hierarchy) and hierarchy[i][3] == -1]
                
                # 按面积降序排序（保证优先处理最大轮廓，匹配参考代码最终取 max 的效果）
                target_contours.sort(key=lambda x: cv2.contourArea(x[1]), reverse=True)
                
                # 遍历候选轮廓
                for i, contour in target_contours:
                    area = cv2.contourArea(contour)
                    
                    # 面积过滤
                    if self.min_area < area < self.max_area:
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) == 4:
                            pts = approx.reshape(4, 2)
                            
                            # 角点排序
                            s = pts.sum(axis=1)
                            diff = pts[:, 0] - pts[:, 1]
                            rect = np.zeros((4, 2), dtype=np.int32)
                            rect[0] = pts[np.argmin(s)]
                            rect[2] = pts[np.argmax(s)]
                            rect[1] = pts[np.argmax(diff)]
                            rect[3] = pts[np.argmin(diff)]
                            pts = rect
                            
                            # 计算中心与尺寸
                            self.x_center, self.y_center = self._get_intersection(pts[0], pts[2], pts[1], pts[3])
                            self.width = float(max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                            self.height = float(min(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
                            self.detected = True
                            
                            # 绘制结果并退出（找到第一个符合条件的最大轮廓就停）
                            self._draw_contours(marked_image, contour, pts)
                            break
            
            # 确保返回 closed 供主程序显示二值图
            return marked_image, closed
            
        except Exception as e:
            print(f'Detect Error: {str(e)}')
            h, w = image.shape[:2]
            return image, np.zeros((h, w), dtype=np.uint8)

    def _get_intersection(self, p1, p2, p3, p4):
        """计算两条线段交点（对角线求中心）"""
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])
        x3, y3 = int(p3[0]), int(p3[1])
        x4, y4 = int(p4[0]), int(p4[1])
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return float((x1 + x2) / 2), float((y1 + y2) / 2)
        
        x = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
        y = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
        return float(x), float(y)

    def _draw_contours(self, image, contour, pts):
        """绘制检测结果：轮廓/四边形/对角线/角点/中心"""
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)      # 绿色轮廓
        cv2.polylines(image, [pts], True, (255, 0, 0), 2)           # 蓝色四边形
        cv2.line(image, tuple(pts[0]), tuple(pts[2]), (0, 0, 255), 2)  # 红色对角线1
        cv2.line(image, tuple(pts[1]), tuple(pts[3]), (0, 0, 255), 2)  # 红色对角线2
        cv2.circle(image, (int(self.x_center), int(self.y_center)), 6, (0, 255, 255), -1)  # 黄色中心
        
        # 标注角点
        for i, pt in enumerate(pts):
            cv2.circle(image, tuple(pt), 4, (255, 0, 255), -1)
            cv2.putText(image, str(i), (int(pt[0])+5, int(pt[1])+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        
        # 图像中心参考点
        h, w, _ = image.shape
        center = (w//2, h//2)
        cv2.circle(image, center, 3, (255, 255, 255), -1)
        cv2.circle(image, center, 10, (255, 255, 255), 1)
        
        # 信息叠加
        cv2.putText(image, 'Target', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f'({self.x_center:.0f}, {self.y_center:.0f})', (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def get_data(self):
        """返回检测结果字典"""
        return {
            'x': self.x_center, 'y': self.y_center,
            'width': self.width, 'height': self.height,
            'detected': self.detected
        }