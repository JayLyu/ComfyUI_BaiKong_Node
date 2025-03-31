from PIL import Image, ImageDraw
import numpy as np
import torch
from torchvision.transforms import ToPILImage

from .functions_image import pil2tensor


class BK_GradientImage:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#FFFFFF"}),
                "width": ("INT", {"default": 512,  "min": 0, }),
                "height": ("INT", {"default": 512,  "min": 0, }),
                "start_position": (
                    "FLOAT",
                    {"default": 0,  "display": "slider",
                        "min": 0, "max": 1, "step": 0.01, }
                ),
                "end_position": (
                    "FLOAT",
                    {"default": 1,  "display": "slider",
                        "min": 0, "max": 1, "step": 0.01, }
                ),
                "direction": (
                    ["horizontal", "vertical"],
                    {"default": "horizontal"},
                ),
                "reverse": (
                    "BOOLEAN",
                    {"default": False}
                )
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    OUTPUT_NODE = False
    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = "生成指定尺寸的渐变图像，支持水平或垂直方向，可调整起始位置、结束位置和颜色"

    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color string to RGB tuple"""
        # Handle both formats: #FFFFFF or FFFFFF
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            # Default to white if incorrect format
            print(f"[BK_GradientImage] ├ WARNING Invalid hex color format: {hex_color}. Using white instead.")
            hex_color = "FFFFFF"
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            print(f"[BK_GradientImage] ├ WARNING Could not parse hex color: {hex_color}. Using white instead.")
            return (255, 255, 255)

    def create_gradient_array(self, width, height, rgb, start_pos, end_pos, direction, reverse):
        """Create gradient array using numpy for better performance"""
        # Create empty RGBA array (values 0-255)
        gradient = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Set RGB channels
        gradient[:, :, 0] = rgb[0]
        gradient[:, :, 1] = rgb[1]
        gradient[:, :, 2] = rgb[2]
        
        # Determine gradient direction
        is_horizontal = direction == 'horizontal'
        size = width if is_horizontal else height
        
        # Calculate positions in pixels
        start = max(0, min(size-1, int(size * start_pos)))
        end = max(start+1, min(size, int(size * end_pos)))
        
        # Create alpha gradient
        alpha_range = np.linspace(0, 255, end - start).astype(np.uint8)
        
        # Apply alpha to the correct dimension
        if is_horizontal:
            for i, alpha in enumerate(alpha_range):
                pos = start + i
                if pos < width:
                    gradient[:, pos, 3] = alpha
            # Fill remaining area with full opacity
            if end < width:
                gradient[:, end:, 3] = 255
        else:
            for i, alpha in enumerate(alpha_range):
                pos = start + i
                if pos < height:
                    gradient[pos, :, 3] = alpha
            # Fill remaining area with full opacity
            if end < height:
                gradient[end:, :, 3] = 255
        
        # Reverse if needed
        if reverse:
            if is_horizontal:
                gradient = gradient[:, ::-1, :]
            else:
                gradient = gradient[::-1, :, :]
        
        return gradient

    def main(
        self,
        hex_color: str = "#FFFFFF",
        width: int = 512,
        height: int = 512,
        start_position: float = 0,
        end_position: float = 1,
        direction: str = "horizontal",
        reverse: bool = False
    ):
        """Generate a gradient image with the specified parameters"""
        # Input validation
        width = max(1, width)
        height = max(1, height)
        start_position = max(0.0, min(1.0, start_position))
        end_position = max(start_position + 0.01, min(1.0, end_position))
        
        # Convert hex color to RGB
        rgb = self.hex_to_rgb(hex_color)
        
        # Create gradient using numpy array
        gradient_array = self.create_gradient_array(
            width, height, rgb, start_position, end_position, direction, reverse
        )
        
        # Convert numpy array to PIL Image
        image = Image.fromarray(gradient_array, 'RGBA')
        
        # Convert to tensor and return
        return (pil2tensor(image),)


# if __name__ == "__main__":
#     BK_GradientImage = BK_GradientImage()
#     image = BK_GradientImage.main(
#         hex_color="#34C3EB",
#         width=512,
#         height=512,
#         start_position=0.5,
#         end_position=1,
#         direction='vertical',
#         reverse=False
#     )
#     # 把 Tensor 转化回 PIL 图片
#     image_pil = ToPILImage()(image[0].squeeze(0) * 255).convert('RGBA')
#     # 显示图片
#     image_pil.show()
