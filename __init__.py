from .BK_Img2Color import BK_Img2Color
from .BK_ColorSelector import BK_ColorSelector
from .BK_GradientImage import BK_GradientImage
from .BK_ColorLimit import BK_ColorLimit

NODE_CLASS_MAPPINGS = {
    "BK_Img2Color": BK_Img2Color,
    "BK_ColorSelector": BK_ColorSelector,
    "BK_GradientImage": BK_GradientImage,
    "BK_ColorLimit": BK_ColorLimit
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BK_Img2Color": "BK Img To Color",
    "BK_ColorSelector": "BK Color Selector",
    "BK_GradientImage": "BK Gradient Image",
    "BK_ColorLimit": "BK Color Limit"
}

WEB_DIRECTORY = "./web"