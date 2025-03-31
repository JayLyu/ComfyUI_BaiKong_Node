import math
import colorsys
import numpy as np
import torch
from PIL import Image, ImageDraw
# from .functions_color import rgb_to_hsl, hsl_to_rgb
# from .functions_image import pil2tensor, tensor2pil

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
    """
    Node for limiting a color's saturation and brightness values within specified ranges.
    Provides a visual representation of the color domain with the before/after positions.
    """

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

    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color string to RGB tuple"""
        # Ensure proper format with leading #
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            # Default to red if incorrect format
            print(f"[BK_ColorLimit] ├ WARNING Invalid hex color format: {hex_color}. Using default red color.")
            hex_color = "FF0036"
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            print(f"[BK_ColorLimit] ├ WARNING Could not parse hex color: {hex_color}. Using default red color.")
            return (255, 0, 54)  # Default red color

    @staticmethod
    def rgb_to_hsv(rgb):
        """Convert RGB tuple to HSV values"""
        r, g, b = rgb
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return h, s, v

    @staticmethod
    def hsv_to_rgb(hsv):
        """Convert HSV values to RGB tuple"""
        h, s, v = hsv
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255.0), int(g * 255.0), int(b * 255.0)

    @staticmethod
    def pil2tensor(image):
        """Convert PIL image to tensor"""
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

    def create_color_domain_image(self, h, img_size):
        """Create a color domain image for a given hue using numpy for efficiency"""
        # Create coordinate grids for S and V
        x = np.linspace(0, 1, img_size)
        y = np.linspace(1, 0, img_size)
        s_grid, v_grid = np.meshgrid(x, y)
        
        # Create empty image array
        img_array = np.zeros((img_size, img_size, 3), dtype=np.uint8)
        
        # Create HSV arrays with broadcasting
        hsv_array = np.dstack([
            np.full_like(s_grid, h),
            s_grid,
            v_grid
        ])
        
        # Convert HSV to RGB efficiently
        for y in range(img_size):
            for x in range(img_size):
                hsv = hsv_array[y, x]
                img_array[y, x] = self.hsv_to_rgb(hsv)
        
        return Image.fromarray(img_array)

    def draw_dashed_rectangle(self, draw, bbox, color='white', width=1, dash_length=4):
        """Draw a dashed rectangle on the image"""
        x0, y0, x1, y1 = bbox
        # Draw dashed horizontal lines
        for i in range(x0, x1, dash_length * 2):
            draw.line([(i, y0), (min(i + dash_length, x1), y0)], fill=color, width=width)
            draw.line([(i, y1), (min(i + dash_length, x1), y1)], fill=color, width=width)
        # Draw dashed vertical lines
        for i in range(y0, y1, dash_length * 2):
            draw.line([(x0, i), (x0, min(i + dash_length, y1))], fill=color, width=width)
            draw.line([(x1, i), (x1, min(i + dash_length, y1))], fill=color, width=width)

    def draw_arrow(self, draw, start_point, end_point, color='white', width=2, head_length=7):
        """Draw an arrow between two points"""
        x1, y1 = start_point
        x2, y2 = end_point
        
        # Calculate angle
        angle = math.atan2(y2 - y1, x2 - x1)
        
        # Draw line
        draw.line([x1, y1, x2, y2], fill=color, width=width)
        
        # Draw arrow head
        draw.line([x2, y2, x2 - head_length * math.cos(angle - math.pi/6), y2 - head_length * math.sin(angle - math.pi/6)], 
                 fill=color, width=width)
        draw.line([x2, y2, x2 - head_length * math.cos(angle + math.pi/6), y2 - head_length * math.sin(angle + math.pi/6)], 
                 fill=color, width=width)

    def color_limit(
        self,
        hex_color,
        saturation_start: float = 0,
        saturation_end: float = 1,
        brightness_start: float = 0,
        brightness_end: float = 1,
    ):
        """
        Limit a color's saturation and brightness values within specified ranges.
        Generates a new color and a visual preview of the color domain.
        """
        # Input validation and normalization
        saturation_start = max(0.0, min(1.0, saturation_start))
        saturation_end = max(saturation_start, min(1.0, saturation_end))
        brightness_start = max(0.0, min(1.0, brightness_start))
        brightness_end = max(brightness_start, min(1.0, brightness_end))
        
        # Ensure hex_color starts with #
        if not hex_color.startswith('#'):
            hex_color = f"#{hex_color}"
        
        # Parse and convert colors
        rgb_color = self.hex_to_rgb(hex_color)
        h, s, v = self.rgb_to_hsv(rgb_color)
        
        # Round to six decimal places
        h, s, v = round(h, 6), round(s, 6), round(v, 6)
        
        # Apply saturation and brightness limits
        s_new = max(saturation_start, min(s, saturation_end))
        v_new = max(brightness_start, min(v, brightness_end))
        
        # Generate new color
        rgb_new = self.hsv_to_rgb((h, s_new, v_new))
        hex_new = '#{:02x}{:02x}{:02x}'.format(*rgb_new)
        
        # Log information
        print(f"[BK_ColorLimit] ○ INPUT Original color: {hex_color}")
        print(f"[BK_ColorLimit] ├ PROCE HSV: ({h:.4f}, {s:.4f}, {v:.4f}) -> ({h:.4f}, {s_new:.4f}, {v_new:.4f})")
        print(f"[BK_ColorLimit] ○ OUTPUT New color: {hex_new}")
        
        # Create visualization
        img_size = 512
        img = self.create_color_domain_image(h, img_size)
        draw = ImageDraw.Draw(img)
        
        # Calculate positions for visualization elements
        x1 = int(saturation_start * (img_size - 1))
        x2 = int(saturation_end * (img_size - 1))
        y1 = int((1 - brightness_end) * (img_size - 1))
        y2 = int((1 - brightness_start) * (img_size - 1))
        
        # Draw constraint rectangle
        self.draw_dashed_rectangle(draw, (x1, y1, x2, y2), color='white', width=1, dash_length=4)
        
        # Calculate and draw before/after positions
        dot_size = 12
        dot_width = 4
        arrow_gap = 12
        
        # Original color position
        x_before = int(s * (img_size - 1))
        y_before = int((1 - v) * (img_size - 1))
        x_before = min(max(0, x_before), img_size - 1)
        y_before = min(max(0, y_before), img_size - 1)
        
        # New color position
        x_after = int(s_new * (img_size - 1))
        y_after = int((1 - v_new) * (img_size - 1))
        x_after = min(max(0, x_after), img_size - 1)
        y_after = min(max(0, y_after), img_size - 1)
        
        # Draw indicators
        draw.ellipse([x_before-dot_size, y_before-dot_size, x_before+dot_size, y_before+dot_size], 
                    outline='white', width=dot_width)
        draw.ellipse([x_after-dot_size, y_after-dot_size, x_after+dot_size, y_after+dot_size], 
                    outline='white', width=dot_width)
        
        # Only draw arrow if positions are different
        if (x_before, y_before) != (x_after, y_after):
            # Calculate arrow points with padding
            angle = math.atan2(y_after - y_before, x_after - x_before)
            start_x = x_before + (dot_size + arrow_gap) * math.cos(angle)
            start_y = y_before + (dot_size + arrow_gap) * math.sin(angle)
            end_x = x_after - (dot_size + arrow_gap) * math.cos(angle)
            end_y = y_after - (dot_size + arrow_gap) * math.sin(angle)
            
            # Draw arrow
            self.draw_arrow(draw, (start_x, start_y), (end_x, end_y), color='white', width=2, head_length=7)
        
        # Convert image to tensor
        img_tensor = self.pil2tensor(img.convert('RGB'))
        
        # Return results
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
