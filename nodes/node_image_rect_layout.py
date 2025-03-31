"""
Image Rectangle Layout Node - Find black regions in background image and place images that match the aspect ratio.
"""
import torch
import numpy as np
from PIL import Image, ImageDraw
import random
import cv2
from .functions_image import tensor2pil, pil2tensor

class BK_ImageRectLayout:
    """
    Find bounding rectangles of black elements in an input image and place suitable images from 
    a provided image list within them, based on aspect ratio matching.
    """
    
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
                "random_select": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Random",
                    "label_off": "Best Match"
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
支持随机选择或基于最佳长宽比匹配选择图像。
"""

    def find_bounding_rectangle(self, image):
        """
        Find the bounding rectangle of black elements in the input image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (x, y, width, height) or None if no contours found
        """
        try:
            # Convert to numpy array if not already
            img_array = np.array(image)
            
            # Check if image is grayscale or color
            if len(img_array.shape) == 2:
                gray = img_array
            else:
                # Convert to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply threshold to get binary image - black elements are foreground
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # If no contours found, return None
            if not contours:
                return None
                
            # If we have contours, find the bounding rectangle that contains all of them
            rects = [cv2.boundingRect(c) for c in contours]
            
            # Filter out very small contours (noise)
            min_area = 10  # Minimum contour area to consider
            rects = [r for r in rects if r[2] * r[3] >= min_area]
            
            if not rects:
                return None
                
            # Find the bounding box containing all contours
            x = min(rect[0] for rect in rects)
            y = min(rect[1] for rect in rects)
            x_max = max(rect[0] + rect[2] for rect in rects)
            y_max = max(rect[1] + rect[3] for rect in rects)
            width = x_max - x
            height = y_max - y
            
            # Ensure minimum dimensions
            width = max(width, 1)
            height = max(height, 1)
            
            return (x, y, width, height)
            
        except Exception as e:
            print(f"[BK_ImageRectLayout] ├ ERROR Failed to find bounding rectangle: {str(e)}")
            return None

    def fit_image_to_rect(self, image, rect_width, rect_height):
        """
        Resize an image to fit within a rectangle while maintaining aspect ratio.
        
        Args:
            image: PIL Image object
            rect_width: Width of the target rectangle
            rect_height: Height of the target rectangle
            
        Returns:
            Resized PIL Image
        """
        try:
            # Ensure positive dimensions
            rect_width = max(1, rect_width)
            rect_height = max(1, rect_height)
            
            img_width, img_height = image.size
            img_aspect = img_width / img_height
            rect_aspect = rect_width / rect_height

            # Calculate new dimensions based on aspect ratio
            if img_aspect > rect_aspect:
                # Image is wider than the rectangle, fit to width
                new_width = rect_width
                new_height = int(rect_width / img_aspect)
            else:
                # Image is taller than the rectangle, fit to height
                new_height = rect_height
                new_width = int(rect_height * img_aspect)

            # Ensure minimum dimensions
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            # Resize image with high-quality resampling
            resampling_method = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.BICUBIC
            resized_img = image.resize((new_width, new_height), resampling_method)
            
            return resized_img
            
        except Exception as e:
            print(f"[BK_ImageRectLayout] ├ ERROR Failed to fit image to rectangle: {str(e)}")
            # Return the original image as fallback
            return image.copy()

    def calculate_aspect_ratio_difference(self, img_aspect, rect_aspect):
        """
        Calculate the absolute difference between two aspect ratios.
        
        Returns:
            Float indicating difference (0 = perfect match)
        """
        if img_aspect <= 0 or rect_aspect <= 0:
            return float('inf')
            
        if img_aspect > rect_aspect:
            return img_aspect / rect_aspect - 1.0
        else:
            return rect_aspect / img_aspect - 1.0

    def select_best_matching_image(self, image_list, target_aspect_ratio, aspect_ratio_threshold):
        """
        Find images that match the target aspect ratio within the given threshold.
        
        Returns:
            List of indices of suitable images and their aspect ratios
        """
        suitable_indices = []
        aspect_ratios = []
        
        for i, img in enumerate(image_list):
            pil_img = tensor2pil(img)
            img_aspect_ratio = pil_img.width / pil_img.height if pil_img.height > 0 else 0
            
            # Calculate difference from target aspect ratio
            difference = self.calculate_aspect_ratio_difference(img_aspect_ratio, target_aspect_ratio)
            
            if difference <= aspect_ratio_threshold:
                suitable_indices.append(i)
                aspect_ratios.append(img_aspect_ratio)
                
        return suitable_indices, aspect_ratios

    def exec(self, background_image, image_list, aspect_ratio_threshold=0.25, use_background_if_no_match=True, random_select=False):
        """
        Main execution function to find black regions and place matching images.
        
        Args:
            background_image: Tensor containing the background image
            image_list: List of tensor images to choose from
            aspect_ratio_threshold: Maximum allowed difference in aspect ratio
            use_background_if_no_match: Whether to return the background if no match is found
            random_select: Whether to randomly select from suitable images instead of using best match
            
        Returns:
            Tuple of (output_image, rectangle_preview, remaining_image_list)
        """
        # Input validation
        if not isinstance(image_list, list) or len(image_list) == 0:
            print("[BK_ImageRectLayout] ├ WARNING Empty image list provided")
            return (background_image, background_image, [])
            
        aspect_ratio_threshold = max(0.01, min(0.5, aspect_ratio_threshold))
        
        # Convert tensor to PIL image
        background = tensor2pil(background_image[0])
        
        # Find bounding rectangle
        rect = self.find_bounding_rectangle(background)
        
        # If no rectangle found, return the original image
        if rect is None:
            print("[BK_ImageRectLayout] ○ INPUT No black elements found in the background image")
            return (background_image, background_image, image_list)

        # Extract rectangle coordinates and calculate aspect ratio
        x, y, width, height = rect
        if height <= 0:
            print("[BK_ImageRectLayout] ├ WARNING Invalid rectangle with zero height")
            return (background_image, background_image, image_list)
            
        target_aspect_ratio = width / height
        print(f"[BK_ImageRectLayout] ○ INPUT Found rectangle: x={x}, y={y}, width={width}, height={height}, aspect ratio={target_aspect_ratio:.2f}")
        
        # Find suitable images based on aspect ratio
        suitable_indices, aspect_ratios = self.select_best_matching_image(image_list, target_aspect_ratio, aspect_ratio_threshold)
        
        print(f"[BK_ImageRectLayout] ├ PROCE Number of images matching aspect ratio: {len(suitable_indices)}")
        
        # If no suitable images found, handle according to settings
        if not suitable_indices:
            print("[BK_ImageRectLayout] ○ OUTPUT No images found matching the aspect ratio")
            if use_background_if_no_match:
                return (background_image, background_image, image_list)
            else:
                transparent = Image.new('RGBA', background.size, (0, 0, 0, 0))
                return (pil2tensor(transparent), pil2tensor(background), image_list)
        
        # Select an image from suitable matches
        if random_select:
            # Randomly select from suitable images
            selected_index = random.choice(suitable_indices)
            print(f"[BK_ImageRectLayout] ├ PROCE Randomly selected image index: {selected_index}")
        else:
            # Select the image with the closest aspect ratio if multiple matches found
            if len(suitable_indices) > 1:
                differences = [abs(ratio - target_aspect_ratio) for ratio in aspect_ratios]
                best_match_idx = differences.index(min(differences))
                selected_index = suitable_indices[best_match_idx]
                print(f"[BK_ImageRectLayout] ├ PROCE Selected best matching image (difference: {differences[best_match_idx]:.4f})")
            else:
                # If only one match found, use it
                selected_index = suitable_indices[0]
            
        # Get the selected image
        selected_image = image_list[selected_index]
        pil_selected = tensor2pil(selected_image)
        print(f"[BK_ImageRectLayout] ├ PROCE Selected image index: {selected_index}, size: {pil_selected.size}")
        
        # Create new remaining_images list, excluding the selected image
        remaining_images = [img for i, img in enumerate(image_list) if i != selected_index]
        
        # Resize the image to fit the rectangle
        fitted_image = self.fit_image_to_rect(pil_selected, width, height)
        
        # Create transparent output image
        output_image = Image.new('RGBA', background.size, (0, 0, 0, 0))
        
        # Calculate center position for the image
        paste_x = x + (width - fitted_image.width) // 2
        paste_y = y + (height - fitted_image.height) // 2
        
        # Ensure image is in RGBA mode for alpha compositing
        if fitted_image.mode != 'RGBA':
            fitted_image = fitted_image.convert('RGBA')
        
        # Paste the fitted image
        output_image.paste(fitted_image, (paste_x, paste_y), fitted_image)
        
        # Create a preview image showing the rectangle and placed image
        rect_preview = background.copy().convert('RGBA')
        rect_preview.paste(fitted_image, (paste_x, paste_y), fitted_image)
        
        # Draw rectangles on the preview
        draw = ImageDraw.Draw(rect_preview)
        # Draw detected rectangle in red
        draw.rectangle([x, y, x+width, y+height], outline=(255, 0, 0), width=2)
        # Draw image bounds in green
        draw.rectangle([paste_x, paste_y, paste_x+fitted_image.width, paste_y+fitted_image.height], outline=(0, 255, 0), width=2)
        
        # Ensure images are in RGBA mode
        output_image = output_image.convert('RGBA')
        rect_preview = rect_preview.convert('RGBA')
        
        print(f"[BK_ImageRectLayout] ├ PROCE Final output image size: {output_image.size}")
        print(f"[BK_ImageRectLayout] ○ OUTPUT Remaining unused images: {len(remaining_images)}")
        print(f"[BK_ImageRectLayout] ○ OUTPUT Selection mode: {'Random' if random_select else 'Best match'}")
        
        # Convert back to tensors and return
        return (pil2tensor(output_image), pil2tensor(rect_preview), remaining_images)
