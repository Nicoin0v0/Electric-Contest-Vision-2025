#!/usr/bin/env python3
# pil_slider.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

class PILSlider:
    def __init__(self, title="Controls", width=400, height=150):
        self.title = title
        self.width = width
        self.height = height
        self.sliders = {}  # 存储滑动条状态
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.dragging = None  # 当前拖拽的滑动条名称
        
        # 加载字体（兼容香橙派）
        self.font_path = None
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
            if os.path.exists(p):
                self.font_path = p
                break
        self.font = ImageFont.truetype(self.font_path, 16) if self.font_path else ImageFont.load_default()

        # 注册 OpenCV 鼠标事件
        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(title, self._on_mouse)

    def add_slider(self, name, min_val, max_val, default_val, y_pos=40):
        """添加滑动条"""
        self.sliders[name] = {
            "min": min_val, "max": max_val,
            "val": default_val,
            "y": y_pos,
            "track_h": 20,
            "thumb_w": 10,
            "track_x": 20,
            "track_w": self.width - 40
        }
        self._redraw()

    def get_value(self, name):
        """获取当前滑动条值"""
        return self.sliders[name]["val"]

    def _val_to_x(self, name, val):
        s = self.sliders[name]
        ratio = (val - s["min"]) / (s["max"] - s["min"])
        return s["track_x"] + int(ratio * (s["track_w"] - s["thumb_w"]))

    def _x_to_val(self, name, x):
        s = self.sliders[name]
        ratio = max(0, min(1, (x - s["track_x"]) / (s["track_w"] - s["thumb_w"])))
        return int(s["min"] + ratio * (s["max"] - s["min"]))

    def _on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            for name, s in self.sliders.items():
                thumb_x = self._val_to_x(name, s["val"])
                if (s["track_x"] <= x <= s["track_x"] + s["track_w"] and
                    s["y"] - 5 <= y <= s["y"] + s["track_h"] + 5):
                    self.dragging = name
                    s["val"] = self._x_to_val(name, x)
                    self._redraw()
                    break
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            s = self.sliders[self.dragging]
            s["val"] = self._x_to_val(self.dragging, x)
            self._redraw()
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = None

    def _redraw(self):
        """用 PIL 重绘整个面板"""
        img_pil = Image.fromarray(self.canvas)
        draw = ImageDraw.Draw(img_pil)
        
        # 背景
        draw.rectangle([0, 0, self.width, self.height], fill=(30, 30, 30))
        draw.text((10, 10), self.title, font=self.font, fill=(255, 255, 255))

        for name, s in self.sliders.items():
            y = s["y"]
            h = s["track_h"]
            # 轨道
            draw.rectangle([s["track_x"], y, s["track_x"] + s["track_w"], y + h], fill=(80, 80, 80))
            # 滑块
            thumb_x = self._val_to_x(name, s["val"])
            draw.rectangle([thumb_x, y-2, thumb_x + s["thumb_w"], y + h + 2], fill=(0, 200, 100))
            # 标签与数值
            draw.text((s["track_x"], y - 18), f"{name}: {s['val']}", font=self.font, fill=(200, 200, 200))

        # PIL → OpenCV
        self.canvas = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def show(self):
        cv2.imshow(self.title, self.canvas)

# ================= 使用示例 =================
if __name__ == "__main__":
    panel = PILSlider("Controls", width=420, height=120)
    panel.add_slider("Threshold", 0, 255, 120, y_pos=30)
    panel.add_slider("Gain", 10, 100, 50, y_pos=80)

    while True:
        panel.show()
        # 读取当前值
        thr = panel.get_value("Threshold")
        gain = panel.get_value("Gain")
        print(f"\rThreshold={thr:3d}, Gain={gain:3d}", end="", flush=True)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cv2.destroyAllWindows()