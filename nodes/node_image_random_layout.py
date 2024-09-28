import torch
import numpy as np
from PIL import Image
import random
from scipy.ndimage import sobel

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
            },
            "optional": {
                "image_1": ("IMAGE",),
                "mask_1": ("MASK",),
                "image_2": ("IMAGE",),
                "mask_2": ("MASK",),
                "image_3": ("IMAGE",),
                "mask_3": ("MASK",),
                "image_4": ("IMAGE",),
                "mask_4": ("MASK",),
                "image_5": ("IMAGE",),
                "mask_5": ("MASK",),
                "num_images": ("INT", {"default": 5, "min": 1, "max": 100, "step": 1}),
                "max_offset": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                "max_rotation": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 0.1}),
                "min_scale": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1}),
                "max_scale": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 5.0, "step": 0.1}),
            }
        }

    CATEGORY = "⭐️ Baikong/Image"

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("IMAGE", "PATH_PREVIEW")
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

    def exec(self, path_image, num_images=5, max_offset=20, max_rotation=45.0, min_scale=0.5, max_scale=1.5,
             image_1=None, mask_1=None, image_2=None, mask_2=None, image_3=None, mask_3=None,
             image_4=None, mask_4=None, image_5=None, mask_5=None):

        batch_images = []

        for img, mask in [(image_1, mask_1), (image_2, mask_2), (image_3, mask_3),
                          (image_4, mask_4), (image_5, mask_5)]:
            if img is not None:
                if mask is not None:
                    alpha = 1 - mask.unsqueeze(-1)
                    img_with_alpha = torch.cat([img, alpha], dim=-1)
                else:
                    alpha = torch.ones(
                        (img.shape[0], img.shape[1], img.shape[2], 1), dtype=img.dtype, device=img.device)
                    img_with_alpha = torch.cat([img, alpha], dim=-1)
                batch_images.append(img_with_alpha)

        if not batch_images:
            return (path_image, path_image)

        path_img = tensor2pil(path_image[0])

        if path_img is None:
            path_img = Image.new('RGB', (512, 512), color='white')

        path = self.extract_path(path_img)
        canvas = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        canvas_with_path = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        
        path_img_rgba = path_img.convert('RGBA')
        canvas_with_path.alpha_composite(path_img_rgba, (0, 0))

        for _ in range(num_images):
            img = random.choice(batch_images)
            print(f"Original image shape: {img.shape}")

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
            canvas_with_path.alpha_composite(pil_img, (paste_x, paste_y))

        result = pil2tensor(canvas)
        result_with_path = pil2tensor(canvas_with_path)
        return (result, result_with_path)


# if __name__ == "__main__":
#     import os
#     import traceback
#     try:

#         selector_node = BK_ImageRandomLayout()

#         test_images = []
#         for i in range(1, 4):
#             img_path = f"../test/test{i}.png"
#             if os.path.exists(img_path):
#                 pil_img = Image.open(img_path).convert("RGB")
#                 img_tensor = pil2tensor(pil_img)
#                 if img_tensor is not None:
#                     test_images.append(img_tensor)
#                 else:
#                     print(f"Warning: Unable to convert {img_path} to tensor")
#             else:
#                 print(f"Warning: Image {img_path} not found")

#         if not test_images:
#             print("Error: No test images found")
#         else:
#             path_img_path = "../test/path.png"
#             if os.path.exists(path_img_path):
#                 path_pil_img = Image.open(path_img_path).convert("RGB")
#                 path_img_tensor = pil2tensor(path_pil_img)
#                 if path_img_tensor is None:
#                     raise ValueError("Unable to convert path image to tensor")
#             else:
#                 raise FileNotFoundError(
#                     f"Error: Path image {path_img_path} not found")

#             result = selector_node.exec(test_images, path_img_tensor)
#             if result[0] is not None:
#                 print("Test completed, output image shape:", result[0].shape)

#                 output_img = tensor2pil(result[0])
#                 if output_img:
#                     output_img.save("../test/output_test.png")
#                     print("Result image saved as output_test.png")
#                 else:
#                     print("Unable to save result image")
#             else:
#                 print("Execution failed, no output result")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         print(traceback.format_exc())
