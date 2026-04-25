import cv2
import numpy as np
import modules.config as config


class ObjectDetector:
    """矩形目标检测器：纯二值化 + 轮廓筛选"""
    
    def __init__(self):
        self.threshold_val = config.THRESHOLD_VALUE
        self.min_area = config.MIN_AREA
        self.max_area = config.MAX_AREA
        self.detected = False
        self.x_center = 0.0
        self.y_center = 0.0
        self.width = 0.0
        self.height = 0.0
        
    def update_params(self, threshold=None, min_area=None, max_area=None):
        if threshold is not None: self.threshold_val = threshold
        if min_area is not None: self.min_area = min_area
        if max_area is not None: self.max_area = max_area

    def detect(self, image):
        try:
            marked_image = image.copy()  # 保留原图用于画框
            
            # 1. 灰度 + 二值化（核心检测用）
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)
            
            # 2. 找轮廓（直接在二值图上）
            contours, hierarchy = cv2.findContours(binary, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            # 重置状态
            self.detected = False
            self.x_center = 0.0
            self.y_center = 0.0
            
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                # 优先内轮廓，没有则用外轮廓
                inner = [(i,c) for i,c in enumerate(contours) if i<len(hierarchy) and hierarchy[i][3]!=-1]
                targets = inner if inner else [(i,c) for i,c in enumerate(contours) if i<len(hierarchy) and hierarchy[i][3]==-1]
                targets.sort(key=lambda x: cv2.contourArea(x[1]), reverse=True)
                
                for _, contour in targets:
                    area = cv2.contourArea(contour)
                    if self.min_area < area < self.max_area:
                        approx = cv2.approxPolyDP(contour, 0.02*cv2.arcLength(contour,True), True)
                        if len(approx) == 4:
                            pts = self._sort_corners(approx.reshape(4,2))
                            if len(set(map(tuple,pts))) < 4: continue  # 防退化
                            
                            # 计算中心
                            self.x_center, self.y_center = self._get_intersection(pts[0],pts[2],pts[1],pts[3])
                            self.width = float(max(np.ptp(pts[:,0]), np.ptp(pts[:,1])))
                            self.height = float(min(np.ptp(pts[:,0]), np.ptp(pts[:,1])))
                            self.detected = True
                            
                            # 在原图上画框（marked_image）
                            self._draw_contours(marked_image, contour, pts)
                            break
            
            return marked_image, binary  # 🔽 返回：原图画框 + 纯二值图
            
        except Exception as e:
            print(f'Detect Error: {e}')
            h,w = image.shape[:2]
            return image, np.zeros((h,w), dtype=np.uint8)

    def _sort_corners(self, pts):
        """角点排序：左上→左下→右下→右上"""
        s = pts.sum(axis=1)
        diff = pts[:,0] - pts[:,1]
        rect = np.zeros((4,2), dtype=np.int32)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        rect[1] = pts[np.argmax(diff)]
        rect[3] = pts[np.argmin(diff)]
        return rect

    def _get_intersection(self, p1,p2,p3,p4):
        """对角线交点 = 中心"""
        x1,y1 = p1; x2,y2 = p2; x3,y3 = p3; x4,y4 = p4
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(denom)<1e-10: return (x1+x2)/2, (y1+y2)/2
        x = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / denom
        y = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / denom
        return float(x), float(y)

    def _draw_contours(self, img, contour, pts):
        """在原图上绘制检测结果"""
        cv2.drawContours(img, [contour], -1, (0,255,0), 2)
        cv2.polylines(img, [pts], True, (255,0,0), 2)
        cv2.line(img, tuple(pts[0]), tuple(pts[2]), (0,0,255), 2)
        cv2.line(img, tuple(pts[1]), tuple(pts[3]), (0,0,255), 2)
        cv2.circle(img, (int(self.x_center),int(self.y_center)), 6, (0,255,255), -1)
        for i,pt in enumerate(pts):
            cv2.circle(img, tuple(pt), 4, (255,0,255), -1)
            cv2.putText(img, str(i), (pt[0]+5,pt[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)
        # 画面信息
        cv2.putText(img, 'Target', (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(img, f'({self.x_center:.0f},{self.y_center:.0f})', (10,120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    def get_data(self):
        return {'x':self.x_center,'y':self.y_center,'w':self.width,'h':self.height,'detected':self.detected}