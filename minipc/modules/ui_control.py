import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import modules.config as config

class UIControl:
    def __init__(self):
        self.window_name = 'Controls'
        self.width, self.height = 420, 160
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.dragging = None
        
        # 字体加载（与测试代码完全一致）
        self.font_path = None
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
            if os.path.exists(p):
                self.font_path = p
                break
        self.font = ImageFont.truetype(self.font_path, 16) if self.font_path else ImageFont.load_default()
        
        # 📌 滑动条配置：完全从 config 读取
        self.sliders = {}
        self._add_slider('Threshold', 0, config.THRESHOLD_MAX, config.THRESHOLD_VALUE, 45)
        self._add_slider('MinArea',   0, config.MIN_AREA_TRACKBAR_MAX, config.MIN_AREA, 85)
        self._add_slider('MaxArea',   0, config.MAX_AREA_TRACKBAR_MAX, config.MAX_AREA, 125)
        
        self.initialized = False

    def _add_slider(self, name, min_val, max_val, default_val, y_pos):
        """内部封装：保持与测试代码完全一致的数据结构"""
        self.sliders[name] = {
            "min": min_val, "max": max_val, "val": default_val,
            "y": y_pos, "track_h": 20, "thumb_w": 10,
            "track_x": 20, "track_w": self.width - 40
        }

    def create_trackbars(self, window_name='Controls'):
        self.window_name = window_name
        if not self.initialized:
            # 🛑 关键修复：改用 AUTOSIZE，禁止窗口缩放，保证 PIL 像素级渲染
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
            cv2.setMouseCallback(self.window_name, self._on_mouse)
            self._redraw()
            self.initialized = True

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

    def _val_to_x(self, name, val):
        s = self.sliders[name]
        ratio = (val - s["min"]) / (s["max"] - s["min"])
        return s["track_x"] + int(ratio * (s["track_w"] - s["thumb_w"]))

    def _x_to_val(self, name, x):
        s = self.sliders[name]
        ratio = max(0, min(1, (x - s["track_x"]) / (s["track_w"] - s["thumb_w"])))
        return int(s["min"] + ratio * (s["max"] - s["min"]))

    def _redraw(self):
        """📌 严格复用测试代码的成功渲染逻辑"""
        img_pil = Image.fromarray(self.canvas)
        draw = ImageDraw.Draw(img_pil)
        
        draw.rectangle([0, 0, self.width, self.height], fill=(30, 30, 30))
        draw.text((10, 10), self.window_name, font=self.font, fill=(255, 255, 255))

        for name, s in self.sliders.items():
            y = s["y"]
            h = s["track_h"]
            draw.rectangle([s["track_x"], y, s["track_x"] + s["track_w"], y + h], fill=(80, 80, 80))
            thumb_x = self._val_to_x(name, s["val"])
            draw.rectangle([thumb_x, y-2, thumb_x + s["thumb_w"], y + h + 2], fill=(0, 200, 100))
            draw.text((s["track_x"], y - 18), f"{name}: {s['val']}", font=self.font, fill=(200, 200, 200))

        self.canvas = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def show(self):
        cv2.imshow(self.window_name, self.canvas)

    def get_values(self):
        return (
            self.sliders['Threshold']['val'],
            self.sliders['MinArea']['val'],
            self.sliders['MaxArea']['val']
        )

    def destroy(self):
        cv2.destroyWindow(self.window_name)
        self.initialized = False