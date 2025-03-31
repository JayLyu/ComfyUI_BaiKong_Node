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

    def _process_image_with_mask(self, img, mask):
        """Process a single image with its optional mask and return a 4-channel image tensor"""
        if img is None:
            return None
            
        # Get image properties
        device = img.device
        dtype = img.dtype
        
        # Check number of channels
        if img.shape[-1] == 3:
            # Handle 3-channel RGB image
            if mask is not None and mask.shape[1:3] == img.shape[1:3]:
                # Valid mask with matching dimensions - create alpha from mask
                alpha = (1 - mask).unsqueeze(-1)
                return torch.cat([img, alpha], dim=-1)
            else:
                # No valid mask - use the image as is
                return img
                
        elif img.shape[-1] == 4:
            # Already has alpha channel, use as is
            return img
            
        else:
            # Other format (e.g., single channel) - add alpha channel
            if mask is not None:
                # Use provided mask to create alpha
                alpha = (1 - mask).unsqueeze(-1)
            else:
                # Create opaque alpha channel
                alpha = torch.ones((*img.shape[:2], 1), dtype=dtype, device=device)
                
            return torch.cat([img, alpha], dim=-1)

    def doit(self, 
        image_1=None, mask_1=None, 
        image_2=None, mask_2=None, 
        image_3=None, mask_3=None, 
        image_4=None, mask_4=None,
        image_list=None):
        
        # Initialize output list
        images = []

        # Add existing image_list if provided
        if image_list is not None:
            images.extend(image_list)

        # Process image-mask pairs
        image_mask_pairs = [
            (image_1, mask_1),
            (image_2, mask_2),
            (image_3, mask_3),
            (image_4, mask_4)
        ]
        
        # Process each image-mask pair
        for img, mask in image_mask_pairs:
            processed_img = self._process_image_with_mask(img, mask)
            if processed_img is not None:
                images.append(processed_img)
        
        # Return result, empty list if no images were processed
        return (images,)