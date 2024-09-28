# Refrence to: https://github.com/Yanick112/ComfyUI-ToSVG

from server import PromptServer
# import vtracer

import os
import time
import folder_paths
import numpy as np
from PIL import Image
import torch

def tensor2pil(t_image: torch.Tensor) -> Image.Image:
    return Image.fromarray(np.clip(255.0 * t_image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

class BK_ImageToSVG:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            #     "colormode": (["color", "binary"], {"default": "color"}),
            #     "hierarchical": (["stacked", "cutout"], {"default": "stacked"}),
            #     "mode": (["spline", "polygon", "none"], {"default": "spline"}),
            #     "filter_speckle": ("INT", {"default": 4, "min": 0, "max": 100}),
            #     "color_precision": ("INT", {"default": 6, "min": 0, "max": 10}),
            #     "layer_difference": ("INT", {"default": 16, "min": 0, "max": 256}),
            #     "corner_threshold": ("INT", {"default": 60, "min": 0, "max": 180}),
            #     "length_threshold": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 10.0}),
            #     "max_iterations": ("INT", {"default": 10, "min": 1, "max": 70}),
            #     "splice_threshold": ("INT", {"default": 45, "min": 0, "max": 180}),
            #     "path_precision": ("INT", {"default": 3, "min": 0, "max": 10}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("SVG",)
    FUNCTION = "convert_to_svg"
    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = "将输入的图像变为 SVG 输出"

    def __init__(self):
        pass

    # def convert_to_svg(self, image, **kwargs):
    def convert_to_svg(self, image,):
        pil_image = tensor2pil(image)
        
        if pil_image.mode != 'RGBA':
            alpha = Image.new('L', pil_image.size, 255)
            pil_image.putalpha(alpha)
        
        pixels = list(pil_image.getdata())
        size = pil_image.size

        # svg_str = vtracer.convert_pixels_to_svg(
        #     pixels,
        #     size=size,
        #     # **kwargs
        # )

        return (pixels,)

# if __name__ == "__main__":
#     process_node = BK_ImageToSVG()
#     print(
#         process_node.convert_to_svg(
#             image = "../test_image.png"
#         )
#     )
