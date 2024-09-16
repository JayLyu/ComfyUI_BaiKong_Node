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
    OUTPUT_NODE = False
    DESCRIPTION = "生成指定尺寸的渐变图像，支持水平或垂直方向，可调整起始位置、结束位置和颜色"

    @staticmethod
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

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

        r, g, b = self.hex_to_rgb(hex_color)

        is_horizontal = direction == 'horizontal'
        size = width if is_horizontal else height
        start = int(size * start_position)
        end = int(size * end_position)

        for i in range(start, end):
            alpha = int(255 * (i - start) / (end - start))
            color = (r, g, b, alpha)
            if is_horizontal:
                draw.line((i, 0, i, height), fill=color)
            else:
                draw.line((0, i, width, i), fill=color)

        # 填充剩余部分
        fill_area = [end, 0, size, height] if is_horizontal else [0, end, width, size]
        draw.rectangle(fill_area, fill=(r, g, b, 255))

        if reverse:
            image = image.rotate(180)

        return (pil2tensor(image),)


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
