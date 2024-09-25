blue = "\033[34m"
green = "\033[92m"
color_end = "\033[0m"

try:
    from .nodes.node_image_to_color import *
    from .nodes.node_color_selector import *
    from .nodes.node_gradient_image import *
    from .nodes.node_color_limit import *
    from .nodes.node_color_contrast import *
    from .nodes.node_color_luminance import *
    from .nodes.node_image_aspect_filter import *
except ImportError:
    print(f"{blue}ComfyUI Baikong Node:{green} Failed to load nodes{color_end}")


NODE_CLASS_MAPPINGS = {
    # 颜色提取
    "BK_Img2Color": BK_Img2Color,
    "BK_ColorSelector": BK_ColorSelector,
    # 颜色处理
    "BK_ColorLimit": BK_ColorLimit,
    "BK_ColorContrast":  BK_ColorContrast,
    "BK_ColorLuminance":  BK_ColorLuminance,
    # 图像生成
    "BK_GradientImage": BK_GradientImage,
    # 图像过滤
    # "BK_ImageAspectFilter": BK_ImageAspectFilter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # 颜色提取
    "BK_Img2Color": "BK Img To Color",
    "BK_ColorSelector": "BK Color Selector",
    # 颜色处理
    "BK_ColorLimit": "BK Color Limit",
    "BK_ColorContrast":  "BK Color Contrast",
    "BK_ColorLuminance":  "BK Color Luminance",
    # 图像生成
    "BK_GradientImage": "BK Gradient Image",
    # 图像过滤
    # "BK_ImageAspectFilter": "BK Image Aspect Filter"
}