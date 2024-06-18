import torch
import numpy as np
from PIL import Image, ImageDraw

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0) 

class BK_GradientImage:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#FFFFFF"}),
                "width": ("INT", {"default": 512,  "min": 0, }),
                "height": ("INT", {"default": 512,  "min": 0, }),
                "start_position": (
                    "FLOAT",
                    {"default": 0,  "display": "slider",
                        "min": 0, "max": 1, "step": 0.01, }
                ),
                "end_position": (
                    "FLOAT",
                    {"default": 1,  "display": "slider",
                        "min": 0, "max": 1, "step": 0.01, }
                ),
                "direction": (
                    ["horizontal", "vertical"],
                    {"default": "horizontal"},
                ),
                "reverse": (
                    "BOOLEAN",
                    {"default": False}
                )
            },
        }

    CATEGORY = "⭐️Baikong"
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    OUTPUT_NODE = True

    def main(
        self,
        hex_color: str = "#FFFFFF",
        width: int = 512,
        height: int = 512,
        start_position: float = 0,
        end_position: float = 1,
        direction: str = "horizontal",
        reverse: bool = False
    ):
        image = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(image)

        r, g, b = int(hex_color[1:3], 16), int(
            hex_color[3:5], 16), int(hex_color[5:7], 16)
        
        if direction == 'horizontal':
            start_x = int(width * start_position)
            midpoint_x = int(width * end_position)
            for x in range(start_x, midpoint_x):
                alpha = int(255 * (x - start_x) / (midpoint_x - start_x))
                draw.line((x, 0, x, height), fill=(r, g, b, alpha))
            # Fill the rest from midpoint_x to the end with solid color
            draw.rectangle([midpoint_x, 0, width, height], fill=(r, g, b, 255))
        else:  # vertical
            start_y = int(height * start_position)
            midpoint_y = int(height * end_position)
            for y in range(start_y, midpoint_y):
                alpha = int(255 * (y - start_y) / (midpoint_y - start_y))
                draw.line((0, y, width, y), fill=(r, g, b, alpha))
            # Fill the rest from midpoint_y to the end with solid color
            draw.rectangle([0, midpoint_y, width, height], fill=(r, g, b, 255))

        if reverse:
            image = image.rotate(180)
        image_out = pil2tensor(image)

        return (image_out,)


# 示例使用
# hex_color = "#34C3EB"
# size = (400, 400)
# start_position = 0.5  # 渐变从10%的位置开始
# end_position = 0.7  # 渐变在90%的位置结束
# direction = 'vertical'  # 渐变方向为垂直

# image = generate_gradient_image(
#     hex_color, size, start_position, end_position, direction)
# image.show()
