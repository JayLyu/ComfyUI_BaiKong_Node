import math
from PIL import Image, ImageDraw
# from .functions_color import rgb_to_hsl, hsl_to_rgb
# from .functions_image import pil2tensor, tensor2pil

import colorsys
import torch
import numpy as np
# 将 rgb 元组转换成 hsv
def rgb_to_hsv(rgb):
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return h, s, v

# 将 hsv 元组转换成 rgb
def hsv_to_rgb(hsv):
    h, s, v = hsv
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r = int(r * 255.0)
    g = int(g * 255.0)
    b = int(b * 255.0)
    return r, g, b

# Tensor to PIL
def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

# Convert PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 

class BK_ColorLimit:

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "hex_color": ("STRING", {
                    "default": "#FF0036"
                }),
            },
            "optional": {
                "saturation_start": ("FLOAT", {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "saturation_end": ("FLOAT", {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "brightness_start": ("FLOAT", {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "brightness_end": ("FLOAT", {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    CATEGORY = "⭐️ Baikong/Color"
    RETURN_TYPES = ("STRING", "IMAGE",)
    RETURN_NAMES = ("STRING", "PREVIEW")
    FUNCTION = "color_limit"
    DESCRIPTION = """
Input a HEX color and generate a new color based on the set saturation and brightness range limits
输入十六进制颜色，并根据设定的饱和度和亮度范围限制，生成新的颜色
"""

    def color_limit(
        self,
        hex_color,
        saturation_start: float = 0,
        saturation_end: float = 1,
        brightness_start: float = 0,
        brightness_end: float = 1,
    ):
        
        # Convert hex_color to rgb tuple
        rgb_color = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # Convert rgb to hsv
        h, s, v = rgb_to_hsv(rgb_color)

        # Round to six decimal places
        h, s, v = round(h, 6), round(s, 6), round(v, 6)

        # Adjust s and v within specified ranges
        s_new = max(saturation_start, min(s, saturation_end))
        v_new = max(brightness_start, min(v, brightness_end))

        # Convert hsv values to rgb
        rgb_new = hsv_to_rgb((h, s_new, v_new))

        # Construct new hex representation
        hex_new = '#{:02x}{:02x}{:02x}'.format(*rgb_new)
        
        print(f"[BK_ColorLimit] ○ INPUT hex_color: {hex_color}")
        print(f"[BK_ColorLimit] ├ PROCE HSV: ({h:.4f}, {s:.4f}, {v:.4f}) -> ({h:.4f}, {s_new:.4f}, {v_new:.4f})")
        print(f"[BK_ColorLimit] ○ OUTPUT hex_color: {hex_new}")
        
        # Draw color domain image and mark before and after positions
        img_size = 512
        img = Image.new('RGB', (img_size, img_size), color='white')
        draw = ImageDraw.Draw(img)

        # Draw color domain
        for x in range(img_size):
            for y in range(img_size):
                s = x / (img_size - 1)
                v = 1 - y / (img_size - 1)
                rgb = hsv_to_rgb((h, s, v))
                draw.point((x, y), fill=rgb)
        
        # 在绘制标记之前，添加绘制白色虚线框的函数
        def draw_dashed_rectangle(draw, bbox, color='white', width=1, dash_length=4):
            x0, y0, x1, y1 = bbox
            for i in range(x0, x1, dash_length * 2):
                draw.line([(i, y0), (min(i + dash_length, x1), y0)], fill=color, width=width)
                draw.line([(i, y1), (min(i + dash_length, x1), y1)], fill=color, width=width)
            for i in range(y0, y1, dash_length * 2):
                draw.line([(x0, i), (x0, min(i + dash_length, y1))], fill=color, width=width)
                draw.line([(x1, i), (x1, min(i + dash_length, y1))], fill=color, width=width)

        # 计算虚线框的位置
        x1 = int(saturation_start * (img_size - 1))
        x2 = int(saturation_end * (img_size - 1))
        y1 = int((1 - brightness_end) * (img_size - 1))
        y2 = int((1 - brightness_start) * (img_size - 1))

        # 绘制白色虚线框
        draw_dashed_rectangle(draw, (x1, y1, x2, y2), color='white', width=1, dash_length=4)

        # 标记 before 位置
        x_before = int(s * (img_size - 1))
        y_before = int(v * (img_size - 1))
        
        draw = ImageDraw.Draw(img)
        dot_size = 12
        dot_width = 4
        arrow_gap = 12  # 箭头与圆圈之间的距离

        # 标记 before 位置
        draw.ellipse([x_before-dot_size, y_before-dot_size, x_before+dot_size, y_before+dot_size], outline='white', width=dot_width)

        # 标记 after 位置
        x_after = int(s_new * (img_size - 1))
        y_after = int((1-v_new) * (img_size - 1))
        draw.ellipse([x_after-dot_size, y_after-dot_size, x_after+dot_size, y_after+dot_size], outline='white', width=dot_width)

        # 绘制箭头
        arrow_width = 2
        angle = math.atan2(y_after - y_before, x_after - x_before)
        
        # 计算箭头起点和终点
        start_x = x_before + (dot_size + arrow_gap) * math.cos(angle)
        start_y = y_before + (dot_size + arrow_gap) * math.sin(angle)
        end_x = x_after - (dot_size + arrow_gap) * math.cos(angle)
        end_y = y_after - (dot_size + arrow_gap) * math.sin(angle)
        
        # 绘制箭头主体
        draw.line([start_x, start_y, end_x, end_y], fill='white', width=arrow_width)
        
        # 绘制箭头头部
        arrow_head_length = 7
        draw.line([end_x, end_y, end_x - arrow_head_length * math.cos(angle - math.pi/6), end_y - arrow_head_length * math.sin(angle - math.pi/6)], fill='white', width=arrow_width)
        draw.line([end_x, end_y, end_x - arrow_head_length * math.cos(angle + math.pi/6), end_y - arrow_head_length * math.sin(angle + math.pi/6)], fill='white', width=arrow_width)

        # Convert image to tensor
        img_tensor = pil2tensor(img.convert('RGB'))

        return {
            "ui": {"text": [{"bg_color": hex_new, }], },
            "result": (hex_new, img_tensor)
        }


# if __name__ == "__main__":
#     selector_node = BK_ColorLimit()
#     selector_node.color_limit(
#             hex_color="#FF6500",
#             saturation_start=0.25,
#             saturation_end=0.5,
#             brightness_start=0,
#             brightness_end=0.5,
#         )
