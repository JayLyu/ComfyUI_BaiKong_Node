import torch
import comfy.utils
from .functions_image import tensor2pil, pil2tensor

class BK_ImageList:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image1": ("IMAGE", {}), 
            "image2": ("IMAGE", {}), 
            }}

    RETURN_TYPES = ("IMAGE","IMAGE",)
    RETURN_NAMES = ("IMAGE","IMAGE_LIST",)
    OUTPUT_IS_LIST = (False, True,)
    FUNCTION = "doit"

    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = """
Combines images into a batch or list, outputting a batch image as IMAGE.
将图片拼接为批量或列表，输出的 IMAGE 为批量图像。
"""

    def doit(self, image1, image2):
        images = []
        images.append(image1)
        images.append(image2)
        
        # 创建批量图像
        batch_image = images[0]
        for image in images[1:]:
            if batch_image.shape[1:] != image.shape[1:]:
                image = comfy.utils.common_upscale(image.movedim(-1, 1), batch_image.shape[2], batch_image.shape[1], "lanczos", "center").movedim(1, -1)
            batch_image = torch.cat((batch_image, image), dim=0)
        
        # 返回批量图像和图像列表
        return (batch_image, images)