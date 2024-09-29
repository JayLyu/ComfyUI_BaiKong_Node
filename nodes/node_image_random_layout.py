import torch
import numpy as np
from PIL import Image, ImageDraw
import random
import cv2
from skimage.morphology import skeletonize

# Tensor to PIL
def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

# Convert PIL to Tensor
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

class BK_ImageRandomLayout:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path_image": ("IMAGE",),
                "image_list": ("IMAGE_LIST",),
                "placement_mode": (["Random", "Isometric"],),
            },
            "optional": {
                "placement_count": ("INT", {"default": 5, "min": 1, "max": 100, "step": 1}),
                "max_offset": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                "max_rotation": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 0.1, "display": "slider"}),
                "min_scale": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.01, "display": "slider"}),
                "max_scale": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 5.0, "step": 0.01, "display": "slider"}),
            }
        }

    CATEGORY = "⭐️ Baikong/Image"

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("IMAGE", "PATH_PREVIEW", "POINTS_PREVIEW")
    FUNCTION = "exec"
    OUTPUT_NODE = False
    DESCRIPTION = """
Extract black lines from path_image as a path, and randomly scatter batch images along this path.
从 path_image 中提取黑色线条作为路径，并将 image_list 中的图像随机散布在该路径上。
"""

    @staticmethod
    def extract_skeleton_path(binary_array):
        # 使用骨架化算法
        skeleton = skeletonize(binary_array)
        # 获取骨架点的坐标
        path = np.column_stack(np.where(skeleton > 0))
        return path

    def extract_path(self, image):
        try:
            # 转换为灰度图像
            gray = np.array(image.convert('L'))
            
            # 二值化
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
            
            # 使用形态学操作细化线条
            kernel = np.ones((3,3), np.uint8)
            binary = cv2.erode(binary, kernel, iterations=1)
            
            # 提取骨架
            path = self.extract_skeleton_path(binary)
            
            # 如果路径点太少，返回空数组
            if len(path) < 10:
                return np.array([])
            
            # 限制点的数量
            max_points = 1000
            if len(path) > max_points:
                indices = np.linspace(0, len(path) - 1, max_points, dtype=int)
                path = path[indices]
            
            # 交换 x 和 y 坐标，确保画布不会旋转 90 度
            path = path[:, [1, 0]]
            
            return path
        except Exception as e:
            print(f"extract_path 错误: {e}")
            return np.array([])

    def exec(self, path_image, image_list, placement_mode, placement_count=5, max_offset=20, max_rotation=45.0, min_scale=0.5, max_scale=1.5):
        if not isinstance(image_list, list):
            image_list = [image_list]

        path_img = tensor2pil(path_image[0])

        if path_img is None:
            path_img = Image.new('RGB', (512, 512), color='white')

        path = self.extract_path(path_img)
        
        # 创建一个新的图像用于显示路径点
        points_preview = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(points_preview)
        
        # 绘制所有路径点
        for point in path:
            x, y = point
            draw.point((x, y), fill=(255, 0, 0, 255))

        if placement_mode == "Isometric":
            if len(path) >= placement_count:
                indices = np.linspace(0, len(path) - 1, placement_count, dtype=int)
                selected_points = path[indices]
            else:
                selected_points = path
        else:  # 随机模式
            if len(path) >= placement_count:
                selected_points = path[np.random.choice(len(path), placement_count, replace=False)]
            else:
                selected_points = path

        # 在点预览图上标记选中的点
        for point in selected_points:
            x, y = point
            draw.ellipse([x-4, y-4, x+4, y+4], fill=(0, 255, 0, 255))

        canvas = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        canvas_with_path = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        
        path_img_rgba = path_img.convert('RGBA')
        canvas_with_path.alpha_composite(path_img_rgba, (0, 0))

        # 预处理图像列表
        pil_image_list = [tensor2pil(img).convert('RGBA') for img in image_list]

        for point in selected_points:
            pil_img = random.choice(pil_image_list)
            
            x, y = point
            x += random.uniform(-max_offset, max_offset)
            y += random.uniform(-max_offset, max_offset)
            rotation = random.uniform(-max_rotation, max_rotation)
            scale = random.uniform(min_scale, max_scale)

            # 使用更快的重采样方法
            pil_img = pil_img.rotate(rotation, expand=True, resample=Image.BILINEAR)
            new_size = (int(pil_img.width * scale), int(pil_img.height * scale))
            pil_img = pil_img.resize(new_size, Image.BILINEAR)

            paste_x = int(x - pil_img.width // 2)
            paste_y = int(y - pil_img.height // 2)

            canvas.alpha_composite(pil_img, (paste_x, paste_y))
            canvas_with_path.alpha_composite(pil_img, (paste_x, paste_y))

        result = pil2tensor(canvas)
        result_with_path = pil2tensor(canvas_with_path)
        points_preview_tensor = pil2tensor(points_preview)
        return (result, result_with_path, points_preview_tensor)