import cv2
import numpy as np
import modules.config as config


class ObjectDetector:
    """矩形目标检测器：二值化 + 轮廓筛选"""
    
    def __init__(self):
        self.threshold_val = config.THRESHOLD_VALUE
        self.min_area = config.MIN_AREA
        self.max_area = config.MAX_AREA
        self.detected = False
        self.x_center = 0.0
        self.y_center = 0.0
        self.width = 0.0
        self.height = 0.0
        self.last_center = None
        
    def update_params(self, threshold=None, min_area=None, max_area=None, use_otsu=None):
        if threshold is not None: self.threshold_val = threshold
        if min_area is not None: self.min_area = min_area
        if max_area is not None: self.max_area = max_area
        if use_otsu is not None: self.use_otsu = use_otsu  # 记录开关状态

    def detect(self, image):
        try:
            marked_image = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. 二值化开关
            if getattr(self, 'use_otsu', False):
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            else:
                _, binary = cv2.threshold(gray, self.threshold_val, 255, cv2.THRESH_BINARY_INV)
            
            # 形态学闭运算（先膨胀后腐蚀，专门连接断裂缝隙）
            # 核大小建议 (5,5) 或 (3,3)。越大连接力越强，但可能把相邻噪点连成一片
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            binary_closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # 2. 找轮廓
            contours, hierarchy = cv2.findContours(binary_closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            self.detected = False
            self.x_center = 0.0
            self.y_center = 0.0
            
            if hierarchy is not None:
                hierarchy = hierarchy[0]
                
                # 优先内轮廓，没有则用外轮廓
                inner = [(i,c) for i,c in enumerate(contours) if i<len(hierarchy) and hierarchy[i][3]!=-1]
                targets = inner if inner else [(i,c) for i,c in enumerate(contours) if i<len(hierarchy) and hierarchy[i][3]==-1]
                
                candidates = []
                for _, contour in targets:
                    area = cv2.contourArea(contour)
                    if self.min_area < area < self.max_area:
                        peri = cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                        
                        if len(approx) == 4:
                            pts = self._sort_corners(approx.reshape(4, 2))
                            # 防退化检查
                            if len(set(map(tuple, pts.astype(int)))) < 4:
                                continue
                            
                            # 长宽比过滤 (0.707 ± 0.15)
                            w = float(max(np.ptp(pts[:,0]), np.ptp(pts[:,1])))
                            h = float(min(np.ptp(pts[:,0]), np.ptp(pts[:,1])))
                            ratio = min(w, h) / max(w, h)
                            #if not (0.55 < ratio < 0.85):  # 拦截过于细长或过于方正的轮廓
                            #    continue
                            
                            x_c, y_c = self._get_intersection(pts[0], pts[2], pts[1], pts[3])
                            if x_c is None: continue
                            
                            candidates.append({
                                'contour': contour, 'pts': pts,
                                'center': (x_c, y_c), 'area': area, 
                                'width': w, 'height': h
                            })
                
                #  决策输出
                if candidates:
                    # 按面积从大到小排
                    candidates.sort(key=lambda x: x['area'], reverse=True)
                    best = candidates[0]
                    
                    # 防跳变：如果最大候选离上一帧太远(>200px)，且后面有候选，则选次大的
                    # if self.last_center and len(candidates) > 1:
                    #     dist = np.hypot(best['center'][0]-self.last_center[0], best['center'][1]-self.last_center[1])
                    #     if dist > 300:
                    #         best = candidates[1]
                    
                    self.detected = True
                    self.x_center, self.y_center = best['center']
                    self.width, self.height = best['width'], best['height']
                    self.last_center = best['center']
                    
                    self._draw_contours(marked_image, best['contour'], best['pts'])
                else:
                    # 没找到时清空记忆，让卡尔曼接管预测
                    self.last_center = None
                    
            return marked_image, binary_closed
            
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
         # 降级检查：如果排序后出现重复点
        if len(set(map(tuple, rect.astype(int)))) < 4:
            rect[0] = pts[np.argmin(pts[:,0])]  # 最左
            rect[2] = pts[np.argmax(pts[:,0])]  # 最右
            rect[1] = pts[np.argmin(pts[:,1])]  # 最上
            rect[3] = pts[np.argmax(pts[:,1])]  # 最下
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