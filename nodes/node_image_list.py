import torch
import comfy.utils
from .functions_image import tensor2pil, pil2tensor

class BK_ImageList:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {}, 
            "optional": {
                "image_list": ("IMAGE_LIST",),
                "image_1": ("IMAGE",),
                "mask_1": ("MASK",),
                "image_2": ("IMAGE",),
                "mask_2": ("MASK",),
                "image_3": ("IMAGE",),
                "mask_3": ("MASK",),
                "image_4": ("IMAGE",),
                "mask_4": ("MASK",),
            }}

    RETURN_TYPES = ("IMAGE_LIST",)
    RETURN_NAMES = ("image_list",)
    FUNCTION = "doit"

    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = """
Combine images into a list, supporting extension from an existing list. Up to 4 new image groups can be added.
将图片组合成列表，支持从现有列表扩展。最多可添加4组新图像
"""

    def doit(self, 
        image_1=None, mask_1=None, 
        image_2=None, mask_2=None, 
        image_3=None, mask_3=None, 
        image_4=None, mask_4=None,
        image_list=None):

        # 初始化列表
        images = []

        # 如果提供了现有的 image_list，先添加它们
        if image_list is not None:
            images.extend(image_list)

        # 处理新的图像输入
        for img, mask in [(image_1, mask_1), (image_2, mask_2), 
                          (image_3, mask_3), (image_4, mask_4)]:
            if img is not None:
                # 检查图像是否为3通道或4通道
                if img.shape[-1] == 3:
                    # 如果是3通道图像
                    if mask is not None and mask.shape[1:3] == img.shape[1:3]:
                        # 检查 mask 和 img 的形状是否匹配
                        # 如果匹配则合并它们并append
                        alpha = 1 - mask
                        img_with_alpha = torch.cat([img, alpha.unsqueeze(-1)], dim=-1)
                        images.append(img_with_alpha)
                    else:
                        # 如果不匹配则忽略mask，只把 img 给 append
                        images.append(img)
                elif img.shape[-1] == 4:
                    # 如果是4通道图像，保持原样添加到列表中
                    images.append(img)
                else:
                    # 如果是其他情况（比如单通道图像），添加alpha通道
                    if mask is not None:
                        alpha = 1 - mask.unsqueeze(-1)
                        img_with_alpha = torch.cat([img, alpha], dim=-1)
                    else:
                        alpha = torch.ones((*img.shape[:2], 1), dtype=img.dtype, device=img.device)
                        img_with_alpha = torch.cat([img, alpha], dim=-1)
                    images.append(img_with_alpha)
        
        # 如果没有有效的图像输入，返回空列表
        if not images:
            return ([],)
        
        # 返回图像列表
        return (images,)