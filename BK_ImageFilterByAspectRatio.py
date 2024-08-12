# import torch
# from PIL import Image
# import numpy as np

# # Tensor to PIL
# def tensor2pil(image):
#     return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

# # Convert PIL to Tensor
# def pil2tensor(image):
#     return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

# class BK_ImageFilterByAspectRatio:
#     """
#     根据用户定义的宽高比范围过滤图像，并返回布尔条件和筛选后的图像列表。
#     """

#     @classmethod
#     def INPUT_TYPES(s):
#         return {
#             "required": {
#                 "images": ("IMAGE", ),  # Now accepts a list of images
#                 "min_aspect_ratio": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.01}),
#                 "max_aspect_ratio": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 10.0, "step": 0.01}),
#             }
#         }

#     RETURN_TYPES = ("IMAGE", "BOOLEAN")
#     RETURN_NAMES = ("IMAGES", "contains_valid_images")
#     FUNCTION = "exec"
#     CATEGORY = "⭐️Baikong"

#     def exec(self, images, min_aspect_ratio: float, max_aspect_ratio: float):
#         valid_images = []
#         contains_valid_images = False

#         # Process each image
#         for i, img_tensor in enumerate(images):
#             pil_image = tensor2pil(img_tensor)  # Convert Tensor to PIL
#             width, height = pil_image.size
#             aspect_ratio = width / height

#             print(f"Image {i} - Aspect Ratio: {aspect_ratio} - Size: {pil_image.size}")

#             # Check if aspect ratio is within the given range
#             if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio:
#                 valid_images.append(pil2tensor(pil_image))  # Convert back to Tensor
#                 contains_valid_images = True

#         if not valid_images:
#             print("No images matched the given aspect ratio criteria.")
#             valid_images = [torch.empty_like(images[0])]  # Return an empty tensor if no valid images

#         return valid_images, contains_valid_images

# # 示例测试代码，供本地调试使用
# if __name__ == "__main__":
#     dummy_images = torch.randn(3, 3, 512, 512)  # 创建三张随机图像
#     plugin = BK_ImageFilterByAspectRatio()
#     filtered_images, has_valid_images = plugin.exec(
#         images=dummy_images,
#         min_aspect_ratio=1.0,
#         max_aspect_ratio=1.2,
#     )

#     print(f"Filtered images count: {len(filtered_images)}")
#     print(f"Has valid images: {has_valid_images}")