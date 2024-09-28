import torch
import numpy as np
from PIL import Image
import random
from scipy.ndimage import sobel
from .functions_image import tensor2pil, pil2tensor


class BK_ImageLayout:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path_image": ("IMAGE",),
                "batch_images": ("IMAGE",),
            },
            "optional": {
                "num_images": ("INT", {"default": 5, "min": 1, "max": 100, "step": 1}),
                "max_offset": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                "max_rotation": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                "min_scale": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1}),
                "max_scale": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 5.0, "step": 0.1}),
                "draw_path_image": ("BOOLEAN", {"default": False, "label": "Draw Path Image"}),
            }
        }

    CATEGORY = "⭐️ Baikong/Image"

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "exec"
    OUTPUT_NODE = False
    DESCRIPTION = """
Extract black lines from path_image as a path, and randomly scatter batch images along this path.
从 path_image 中提取黑色线条作为路径，并将 batch_images 随机散布在该路径上.  
"""

    @staticmethod
    def simple_path_extraction(binary_array):
        edges_x = sobel(binary_array, axis=0)
        edges_y = sobel(binary_array, axis=1)
        edges = np.hypot(edges_x, edges_y)
        path = np.column_stack(np.where(edges > edges.mean()))
        return path

    def extract_path(self, image):
        try:
            gray = image.convert('L')
            binary = gray.point(lambda x: 0 if x > 128 else 255, '1')
            binary_array = np.array(binary)

            return self.simple_path_extraction(binary_array)
        except Exception as e:
            print(f"extract_path 错误: {e}")
            return np.array([])

    def exec(self, batch_images, path_image, num_images=5, max_offset=20, max_rotation=45.0, min_scale=0.5, max_scale=1.5, draw_path_image=False):
        if not isinstance(path_image, torch.Tensor):
            print(f"错误：path_image 不是张量。类型：{type(path_image)}")
            return (None,)

        # 确保 batch_images 是列表
        if not isinstance(batch_images, list):
            batch_images = [batch_images]

        path_img = tensor2pil(path_image[0])

        if path_img is None:
            path_img = Image.new('RGB', (512, 512), color='white')

        path = self.extract_path(path_img)
        canvas = Image.new('RGBA', path_img.size, (255, 255, 255, 0))

        if draw_path_image:
            path_img_rgba = path_img.convert('RGBA')
            canvas.alpha_composite(path_img_rgba, (0, 0))

        for _ in range(num_images):
            img = random.choice(batch_images)
            print(f"Original image shape: {img.shape}")

            if img.shape[-1] == 3:
                # 创建一个全不透明的 alpha 通道
                alpha = torch.ones((img.shape[0], img.shape[1], img.shape[2], 1), dtype=img.dtype, device=img.device)
                img = torch.cat([img, alpha], dim=-1)
        
            print(f"Converted image shape: {img.shape}")

            if len(path) > 0:
                point = random.choice(path)
                x, y = point[1], point[0]
            else:
                x, y = random.randint(
                    0, path_img.width-1), random.randint(0, path_img.height-1)

            x += random.uniform(-max_offset, max_offset)
            y += random.uniform(-max_offset, max_offset)
            rotation = random.uniform(-max_rotation, max_rotation)
            scale = random.uniform(min_scale, max_scale)

            pil_img = tensor2pil(img)

            if pil_img.mode != 'RGBA':
                pil_img = pil_img.convert('RGBA')

            pil_img = pil_img.rotate(
                rotation, expand=True, resample=Image.BICUBIC)
            new_size = (int(pil_img.width * scale),
                        int(pil_img.height * scale))
            pil_img = pil_img.resize(new_size, Image.LANCZOS)

            paste_x = int(x - pil_img.width // 2)
            paste_y = int(y - pil_img.height // 2)

            canvas.alpha_composite(pil_img, (paste_x, paste_y))

        result = pil2tensor(canvas)
        return (result,)


if __name__ == "__main__":
    import os
    import traceback
    try:

        selector_node = BK_ImageLayout()

        test_images = []
        for i in range(1, 4):
            img_path = f"../test/test{i}.png"
            if os.path.exists(img_path):
                pil_img = Image.open(img_path).convert("RGB")
                img_tensor = pil2tensor(pil_img)
                if img_tensor is not None:
                    test_images.append(img_tensor)
                else:
                    print(f"Warning: Unable to convert {img_path} to tensor")
            else:
                print(f"Warning: Image {img_path} not found")

        if not test_images:
            print("Error: No test images found")
        else:
            path_img_path = "../test/path.png"
            if os.path.exists(path_img_path):
                path_pil_img = Image.open(path_img_path).convert("RGB")
                path_img_tensor = pil2tensor(path_pil_img)
                if path_img_tensor is None:
                    raise ValueError("Unable to convert path image to tensor")
            else:
                raise FileNotFoundError(
                    f"Error: Path image {path_img_path} not found")

            result = selector_node.exec(test_images, path_img_tensor)
            if result[0] is not None:
                print("Test completed, output image shape:", result[0].shape)

                output_img = tensor2pil(result[0])
                if output_img:
                    output_img.save("../test/output_test.png")
                    print("Result image saved as output_test.png")
                else:
                    print("Unable to save result image")
            else:
                print("Execution failed, no output result")
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
