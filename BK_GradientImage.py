import torch
import numpy as np
from PIL import Image, ImageDraw
from torchvision.transforms import ToPILImage


def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


class BK_GradientImage:

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

        # 旋转图像
        if reverse:
            image = image.rotate(180)

        image_out = pil2tensor(image)

        return (image_out,)


if __name__ == "__main__":
    BK_GradientImage = BK_GradientImage()
    image = BK_GradientImage.main(
        hex_color="#34C3EB",
        width=512,
        height=512,
        start_position=0.5,
        end_position=1,
        direction='vertical',
        reverse=False
    )
    # 把 Tensor 转化回 PIL 图片
    image_pil = ToPILImage()(image[0].squeeze(0) * 255).convert('RGBA')
    # 显示图片
    image_pil.show()
