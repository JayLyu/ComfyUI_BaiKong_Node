import importlib

# define colors
blue = "\033[34m"
green = "\033[92m"
color_end = "\033[0m"

node_module_mappings = {
    'node_image_to_color': 'BK_Img2Color',
    'node_color_selector': 'BK_ColorSelector',
    'node_gradient_image': 'BK_GradientImage',
    'node_color_limit': 'BK_ColorLimit',
    'node_color_contrast': 'BK_ColorContrast',
    'node_color_luminance': 'BK_ColorLuminance',
    'node_image_aspect_filter': 'BK_ImageAspectFilter',
    'node_image_to_svg': 'BK_ImageToSVG',
    'node_svg_layout': 'BK_SvgLayout',
    'node_image_layout': "BK_ImageLayout",
    'node_image_list': 'BK_ImageList'
}

imported_classes = {}

for module_name, class_name in node_module_mappings.items():
    try:
        module = importlib.import_module(f'.nodes.{module_name}', package=__package__)
        imported_class = getattr(module, class_name)
        imported_classes[class_name] = imported_class
    except ImportError as e:
        print(f"{blue}ComfyUI Baikong Node:{green} 导入模块 {module_name} 失败: {str(e)}{color_end}")
    except AttributeError:
        print(f"{blue}ComfyUI Baikong Node:{green} 在模块 {module_name} 中找不到类 {class_name}{color_end}")


NODE_CLASS_MAPPINGS = {class_name: imported_classes.get(class_name) for class_name in node_module_mappings.values()}


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
    "BK_ImageToSVG": "BK Image To SVG",
    "BK_SvgLayout": "BK SVG Layout",
    "BK_ImageLayout": "BK Image Layout",
    "BK_ImageList": "BK Image List"
}