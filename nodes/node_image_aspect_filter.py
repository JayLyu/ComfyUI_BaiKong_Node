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
    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = "过滤特定比例的图像"

    def filter(self, images, min_aspect_ratio: float, max_aspect_ratio: float, default_image):
        print(f"[BK_ImageAspectFilter] ○ INPUT min_aspect_ratio: {min_aspect_ratio}, max_aspect_ratio: {max_aspect_ratio}")
        
        valid_images = []
        ui_text = []

        # 确保 images 是 4D 张量 (batch, height, width, channels)
        if len(images.shape) != 4:
            print(f"[BK_ImageAspectFilter] ├ ERROR Invalid input shape: {images.shape}")
            raise ValueError(f"[BK_ImageAspectFilter] Invalid input shape. Expected (batch, height, width, channels), got {images.shape}")

        batch_size, height, width, channels = images.shape
        print(f"[BK_ImageAspectFilter] ├ PROCE Input batch size: {batch_size}")

        for i in range(batch_size):
            aspect_ratio = width / height
            ui_text.append(f"image {i} - aspect ratio: {aspect_ratio:.4f} - size: ({width}, {height})")

            # 检查宽高比是否在给定范围内
            if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio:
                valid_images.append(images[i].unsqueeze(0))
                print(f"[BK_ImageAspectFilter] ├ PROCE Image {i} accepted: aspect ratio {aspect_ratio:.4f}")
            else:
                print(f"[BK_ImageAspectFilter] ├ PROCE Image {i} rejected: aspect ratio {aspect_ratio:.4f}")

        if not valid_images:
            print("[BK_ImageAspectFilter] ├ PROCE No images meet the aspect ratio criteria. Using default image.")
            ui_text.append("No images meet the aspect ratio criteria. Using default image.")
            valid_images = [default_image]

        # 确保返回的是正确格式的张量
        if len(valid_images) == 1:
            valid_images = valid_images[0]
        else:
            valid_images = torch.cat(valid_images, dim=0)

        print(f"[BK_ImageAspectFilter] ○ OUTPUT Valid images: {len(valid_images)}")
        ui_text = "\n".join(ui_text)

        return {"ui": {"text": f"text:{valid_images, ui_text}"}, "result": (valid_images, ui_text)}
