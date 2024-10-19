import torch
import numpy as np
from PIL import Image, ImageDraw
import random
import cv2
from .functions_image import tensor2pil, pil2tensor

class BK_ImageRectLayout:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "background_image": ("IMAGE",),
                "image_list": ("IMAGE_LIST",),
            },
            "optional": {
                "aspect_ratio_threshold": ("FLOAT", {"default": 0.25, "min": 0.01, "max": 0.5, "step": 0.01, "display": "slider"}),
                "use_background_if_no_match": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Yes",
                    "label_off": "No"
                }),
            }
        }

    CATEGORY = "⭐️ Baikong/Image"

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE_LIST")
    RETURN_NAMES = ("IMAGE", "RECT_PREVIEW", "REMAINING_IMAGE_LIST")
    FUNCTION = "exec"
    OUTPUT_NODE = False
    DESCRIPTION = """
Find the bounding rectangle of black elements in the input image and place a suitable image from the image list within it.
在输入的白色背景图片中找到所有黑色元素的边界矩形，并将符合该矩形长宽比的图片等比缩放并居中放置其中。
"""

    def find_bounding_rectangle(self, image):
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            rects = [cv2.boundingRect(c) for c in contours]
            x = min(rect[0] for rect in rects)
            y = min(rect[1] for rect in rects)
            x_max = max(rect[0] + rect[2] for rect in rects)
            y_max = max(rect[1] + rect[3] for rect in rects)
            width = x_max - x
            height = y_max - y
            return (x, y, width, height)
        return None

    def fit_image_to_rect(self, image, rect_width, rect_height):
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        rect_aspect = rect_width / rect_height

        if img_aspect > rect_aspect:
            new_width = rect_width
            new_height = int(rect_width / img_aspect)
        else:
            new_height = rect_height
            new_width = int(rect_height * img_aspect)

        resized_img = image.resize((new_width, new_height), Image.LANCZOS)
        return resized_img

    def exec(self, background_image, image_list, aspect_ratio_threshold=0.1, use_background_if_no_match=True):
        background = tensor2pil(background_image[0])
        rect = self.find_bounding_rectangle(background)
        
        if rect is None:
            print("No black elements found in the background image.")
            return (background_image, background_image, image_list)

        x, y, width, height = rect
        target_aspect_ratio = width / height if height != 0 else 0
        
        suitable_indices = []
        
        for i, img in enumerate(image_list):
            pil_img = tensor2pil(img)
            img_aspect_ratio = pil_img.width / pil_img.height
            if abs(img_aspect_ratio - target_aspect_ratio) <= aspect_ratio_threshold:
                suitable_indices.append(i)
        
        if not suitable_indices:
            print("No images found matching the aspect ratio.")
            if use_background_if_no_match:
                return (background_image, background_image, image_list)
            else:
                transparent = Image.new('RGBA', background.size, (0, 0, 0, 0))
                return (pil2tensor(transparent), background_image, image_list)
        
        selected_index = random.choice(suitable_indices)
        selected_image = image_list[selected_index]
        pil_selected = tensor2pil(selected_image)
        
        # Create new remaining_images, exclude the selected image
        remaining_images = [img for i, img in enumerate(image_list) if i != selected_index]
        
        # Scale the image to fit the rect
        fitted_image = self.fit_image_to_rect(pil_selected, width, height)
        
        # Create output RGBA image
        output_image = Image.new('RGBA', background.size, (0, 0, 0, 0))
        
        # Calculate the center position
        paste_x = x + (width - fitted_image.width) // 2
        paste_y = y + (height - fitted_image.height) // 2
        
        # Check 'fitted_image' is RGBA
        if fitted_image.mode != 'RGBA':
            fitted_image = fitted_image.convert('RGBA')
        
        # Paste fitted_image to output_image
        output_image.paste(fitted_image, (paste_x, paste_y), fitted_image)
        
        # Create a rectangular preview image
        rect_preview = background.copy().convert('RGBA')
        rect_preview.paste(fitted_image, (paste_x, paste_y), fitted_image)
        draw = ImageDraw.Draw(rect_preview)
        draw.rectangle([x, y, x+width, y+height], outline=(255, 0, 0), width=2)
        
        # Frame the selected image in green in RECT_PREVIEW
        draw.rectangle([paste_x, paste_y, paste_x+fitted_image.width, paste_y+fitted_image.height], outline=(0, 255, 0), width=2)
        
        # Check 'output_image' is RGBA
        output_image = output_image.convert('RGBA')
        rect_preview = rect_preview.convert('RGBA')
        
        return (pil2tensor(output_image), pil2tensor(rect_preview), remaining_images)
