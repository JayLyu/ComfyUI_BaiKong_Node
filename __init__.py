from .BK_Img2Color import BK_Img2Color
from .BK_ColorSelector import BK_ColorSelector
from .BK_GradientImage import BK_GradientImage
from .BK_ColorLimit import BK_ColorLimit
from .BK_ColorContrast import BK_ColorContrast
from .BK_ColorLuminance import BK_ColorLuminance
from .BK_ImageAspectFilter import BK_ImageAspectFilter

NODE_CLASS_MAPPINGS = {
    "BK_Img2Color": BK_Img2Color,
    "BK_ColorSelector": BK_ColorSelector,
    "BK_GradientImage": BK_GradientImage,
    "BK_ColorLimit": BK_ColorLimit,
    "BK_ColorContrast":  BK_ColorContrast,
    "BK_ColorLuminance":  BK_ColorLuminance,
    "BK_ImageAspectFilter": BK_ImageAspectFilter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BK_Img2Color": "BK Img To Color",
    "BK_ColorSelector": "BK Color Selector",
    "BK_GradientImage": "BK Gradient Image",
    "BK_ColorLimit": "BK Color Limit",
    "BK_ColorContrast":  "BK Color Contrast",
    "BK_ColorLuminance":  "BK Color Luminance",
    "BK_ImageAspectFilter": "BK Image Aspect Filter"
}

WEB_DIRECTORY = "./web"