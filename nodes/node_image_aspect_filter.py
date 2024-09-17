import torch
from PIL import Image
import numpy as np
import base64
from .functions_image import pil2tensor, tensor2pil

class BK_ImageAspectFilter:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "min_aspect_ratio": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.01}),
                "max_aspect_ratio": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 10.0, "step": 0.01}),
                "default_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "filter"
    CATEGORY = "⭐️ Baikong"
    DESCRIPTION = "过滤特定比例的图像"

    def filter(self, images, min_aspect_ratio: float, max_aspect_ratio: float, default_image):
        valid_images = []
        ui_text = []

        # 确保 images 是 4D 张量 (batch, height, width, channels)
        if len(images.shape) != 4:
            raise ValueError(f"输入图像的形状不正确。预期为 (batch, height, width, channels)，实际为 {images.shape}")

        batch_size, height, width, channels = images.shape

        for i in range(batch_size):
            aspect_ratio = width / height

            ui_text.append(f"image {i} - 宽高比: {aspect_ratio:.4f} - 尺寸: ({width}, {height})")

            # 检查宽高比是否在给定范围内
            if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio:
                valid_images.append(images[i].unsqueeze(0))

        if not valid_images:
            ui_text.append("没有图像符合给定的宽高比标准。使用默认图像。")
            valid_images = [default_image]

        # 确保返回的是正确格式的张量
        if len(valid_images) == 1:
            valid_images = valid_images[0]
        else:
            valid_images = torch.cat(valid_images, dim=0)

        ui_text = "\n".join(ui_text)

        return {"ui": {"text": f"text:{valid_images, ui_text}"}, "result": (valid_images, ui_text)}