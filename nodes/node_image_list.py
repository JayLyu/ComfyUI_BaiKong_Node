import torch
import comfy.utils
from .functions_image import tensor2pil, pil2tensor

class BK_ImageList:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
            },
            "optional": {
                "image3": ("IMAGE",),
                "image4": ("IMAGE",), 
            }
        }

    RETURN_TYPES = ("IMAGE",)
    # OUTPUT_IS_LIST = (True,)
    FUNCTION = "doit"

    CATEGORY = "⭐️ Baikong/Image"

    def doit(self, image1, image2, image3=None, image4=None):
        images = []

        images.append(image1)
        images.append(image2)
        
        if image3 is not None:
            images.append(image3)
        if image4 is not None:
            images.append(image4)
        
        return (images,)