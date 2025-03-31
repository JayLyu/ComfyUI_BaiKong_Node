import torch
import numpy as np
from PIL import Image, ImageDraw
import random
import cv2
from skimage.morphology import skeletonize
from .functions_image import tensor2pil, pil2tensor


class BK_ImageRandomLayout:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "path_image": ("IMAGE",),
                "image_list": ("IMAGE_LIST",),
                "placement_mode": (["Random", "Isometric", "Sequential"],),
            },
            "optional": {
                "placement_count": ("INT", {"default": 5, "min": 1, "max": 100, "step": 1}),
                "max_offset": ("INT", {"default": 20, "min": 0, "max": 100, "step": 1}),
                "max_rotation": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 360.0, "step": 0.1, "display": "slider"}),
                "min_scale": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.01, "display": "slider"}),
                "max_scale": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 5.0, "step": 0.01, "display": "slider"}),
                "preserve_aspect_ratio": ("BOOLEAN", {"default": True}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            }
        }

    CATEGORY = "⭐️ Baikong/Image"

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("IMAGE", "PATH_PREVIEW", "POINTS_PREVIEW")
    FUNCTION = "exec"
    OUTPUT_NODE = False
    DESCRIPTION = """
Extract black lines from path_image as a path, and scatter batch images along this path.
从 path_image 中提取黑色线条作为路径，并将 image_list 中的图像散布在该路径上。
- Random: 随机选择图片放置，确保分布均匀
- Isometric: 沿路径等距离放置图片
- Sequential: 按照输入图片的顺序循环放置
"""

    @staticmethod
    def extract_skeleton_path(binary_array):
        """Extract skeleton path from binary array"""
        # Skeletonize binary image
        skeleton = skeletonize(binary_array)
        # Gets the coordinates of the skeleton point
        path = np.column_stack(np.where(skeleton > 0))
        return path

    def extract_path(self, image):
        """Extract path from image and preprocess it"""
        try:
            # Convert to grayscale and binarize
            gray = np.array(image.convert('L'))
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)

            # Make sure the binary image contains only 0 and 1
            binary = binary.astype(bool).astype(np.uint8)
            
            # Refine lines
            kernel = np.ones((3,3), np.uint8)
            binary = cv2.erode(binary, kernel, iterations=1)
            
            # Extraction skeleton
            path = self.extract_skeleton_path(binary)
            
            if len(path) < 10:
                print("[BK_ImageRandomLayout] ├ ERROR Path too short, need at least 10 points")
                # Return a simple default path (circle) if extraction fails
                t = np.linspace(0, 2*np.pi, 100)
                radius = min(image.width, image.height) // 4
                center_x, center_y = image.width // 2, image.height // 2
                x = center_x + radius * np.cos(t)
                y = center_y + radius * np.sin(t)
                path = np.column_stack([y, x]).astype(int)
                print("[BK_ImageRandomLayout] ├ PROCE Created default circular path with 100 points")
            
            # Limit points and simplify path if it's too complex
            if len(path) > 1000:
                # Use Douglas-Peucker algorithm to simplify path
                max_points = 1000
                indices = np.linspace(0, len(path) - 1, max_points, dtype=int)
                path = path[indices]
                print(f"[BK_ImageRandomLayout] ├ PROCE Simplified path from {len(path)} to {max_points} points")
            
            # Swap the x and y to make sure the CANVAS doesn't rotate 90 degrees
            path = path[:, [1, 0]]
            
            print(f"[BK_ImageRandomLayout] ○ INPUT Extracted path with {len(path)} points")
            return path
        except Exception as e:
            print(f"[BK_ImageRandomLayout] ├ ERROR Extract_path: {e}")
            # Return a simple default path (circle) if extraction fails
            t = np.linspace(0, 2*np.pi, 100)
            radius = 100  # Default radius if image dimensions are unknown
            center_x, center_y = 256, 256  # Default center
            x = center_x + radius * np.cos(t)
            y = center_y + radius * np.sin(t)
            path = np.column_stack([x, y]).astype(int)
            print("[BK_ImageRandomLayout] ├ PROCE Created default circular path due to error")
            return path

    def select_points(self, path, placement_count, placement_mode, rng):
        """Select points on the path based on the placement mode"""
        if len(path) <= 0:
            print("[BK_ImageRandomLayout] ├ ERROR No valid path points found")
            return np.array([[0, 0]])  # Return default point
            
        if placement_mode == "Isometric":
            # Isometric mode: Select points at equal distances along the path
            if len(path) >= placement_count:
                indices = np.linspace(0, len(path) - 1, placement_count, dtype=int)
                selected_points = path[indices]
            else:
                # If fewer points than requested, duplicate some points
                indices = np.arange(placement_count) % len(path)
                selected_points = path[indices]
        elif placement_mode == "Sequential":
            # For Sequential mode, we can use evenly distributed points like Isometric
            # or random points - using evenly distributed for better aesthetics
            if len(path) >= placement_count:
                indices = np.linspace(0, len(path) - 1, placement_count, dtype=int)
                selected_points = path[indices]
            else:
                indices = np.arange(placement_count) % len(path)
                selected_points = path[indices]
        else:  # Random mode
            if len(path) >= placement_count:
                indices = rng.choice(len(path), placement_count, replace=False)
                selected_points = path[indices]
            else:
                # If fewer points than requested, use random points with replacement
                indices = rng.choice(len(path), placement_count, replace=True)
                selected_points = path[indices]
                
        return selected_points

    def select_images(self, pil_image_list, placement_count, placement_mode, rng):
        """Select and arrange images based on the placement mode"""
        num_images = len(pil_image_list)
        if num_images == 0:
            print("[BK_ImageRandomLayout] ├ ERROR No images in image_list")
            # Create a default colored image
            default_img = Image.new('RGBA', (64, 64), (255, 0, 0, 128))
            return [default_img] * placement_count, list(range(placement_count))
            
        if placement_mode == "Random":
            # Improved random mode for more even distribution
            if num_images >= placement_count:
                # Use all images without repetition if possible
                indices = list(range(num_images))
                rng.shuffle(indices)
                indices = indices[:placement_count]
                selected_images = [pil_image_list[i] for i in indices]
                image_indices = list(range(placement_count))
                rng.shuffle(image_indices)  # Randomize order
            else:
                # Ensure each image is used at least once before repeating
                selected_images = []
                base_indices = list(range(num_images))
                
                while len(selected_images) < placement_count:
                    if not base_indices:
                        base_indices = list(range(num_images))
                        rng.shuffle(base_indices)
                    
                    img_index = base_indices.pop(0)
                    selected_images.append(pil_image_list[img_index])
                
                image_indices = list(range(placement_count))
                rng.shuffle(image_indices)  # Randomize order
        elif placement_mode == "Sequential":
            # Sequential mode: Place images in order, looping if needed
            selected_images = []
            for i in range(placement_count):
                img_index = i % num_images
                selected_images.append(pil_image_list[img_index])
            image_indices = list(range(placement_count))  # Preserve order
        else:  # Isometric mode
            # For Isometric, make image selection match point distribution pattern
            selected_images = []
            for i in range(placement_count):
                img_index = i % num_images  # Cycle through images like Sequential
                selected_images.append(pil_image_list[img_index])
            
            image_indices = list(range(placement_count))
            if placement_count > 1:  # Only shuffle if more than one image
                rng.shuffle(image_indices)  # Add some randomness
                
        return selected_images, image_indices

    def process_image(self, pil_img, point, max_offset, max_rotation, min_scale, max_scale, preserve_aspect_ratio, rng):
        """Process a single image with rotation, scaling and positioning"""
        x, y = point
        # Add random offset
        x += rng.uniform(-max_offset, max_offset)
        y += rng.uniform(-max_offset, max_offset)
        
        # Apply random rotation
        rotation = rng.uniform(-max_rotation, max_rotation)
        pil_img = pil_img.rotate(rotation, expand=True, resample=Image.BILINEAR)
        
        # Apply random scaling
        scale = rng.uniform(min_scale, max_scale)
        
        if preserve_aspect_ratio:
            # Keep aspect ratio when scaling
            new_width = int(pil_img.width * scale)
            new_height = int(pil_img.height * scale)
        else:
            # Allow different scaling for width and height
            width_scale = rng.uniform(min_scale, max_scale)
            height_scale = rng.uniform(min_scale, max_scale)
            new_width = int(pil_img.width * width_scale)
            new_height = int(pil_img.height * height_scale)
            
        pil_img = pil_img.resize((new_width, new_height), Image.BILINEAR)
        
        # Calculate paste position (centered on point)
        paste_x = int(x - pil_img.width // 2)
        paste_y = int(y - pil_img.height // 2)
        
        return pil_img, paste_x, paste_y

    def draw_preview(self, path, selected_points, canvas_size):
        """Create preview image showing path and selected points"""
        points_preview = Image.new('RGBA', canvas_size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(points_preview)
        
        # Draw all path points in red
        for point in path:
            x, y = point
            draw.point((x, y), fill=(255, 0, 0, 255))
            
        # Draw selected points with green circles
        for point in selected_points:
            x, y = point
            draw.ellipse([x-4, y-4, x+4, y+4], fill=(0, 255, 0, 255))
            
        return points_preview

    def exec(self, path_image, image_list, placement_mode, placement_count=5, max_offset=20, 
             max_rotation=45.0, min_scale=0.5, max_scale=1.5, preserve_aspect_ratio=True, seed=-1):
        """Main execution function"""
        # Input validation
        if not isinstance(image_list, list):
            image_list = [image_list]
            
        if len(image_list) == 0:
            print("[BK_ImageRandomLayout] ├ ERROR Empty image_list provided")
            # Create a default output
            default_img = torch.zeros((1, 3, 512, 512))
            return (default_img, default_img, default_img)
            
        # Setup RNG with seed for reproducibility
        if seed == -1:
            seed = random.randint(0, 2147483647)
        rng = random.Random(seed)
        np_rng = np.random.RandomState(seed)
        
        print(f"[BK_ImageRandomLayout] ├ INFO Using seed: {seed}")
        
        # Process path image
        path_img = tensor2pil(path_image[0])
        if path_img is None:
            path_img = Image.new('RGB', (512, 512), color='white')
            
        # Extract path from image
        path = self.extract_path(path_img)
        print(f"[BK_ImageRandomLayout] ├ PROCE Path extraction complete, {len(path)} points found")
        
        # Select points on the path
        selected_points = self.select_points(path, placement_count, placement_mode, np_rng)
        print(f"[BK_ImageRandomLayout] ├ PROCE Selected {len(selected_points)} points for image placement")
        
        # Create preview image
        points_preview = self.draw_preview(path, selected_points, path_img.size)
        
        # Create canvas
        canvas = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        canvas_with_path = Image.new('RGBA', path_img.size, (255, 255, 255, 0))
        
        # Add path to path preview
        path_img_rgba = path_img.convert('RGBA')
        canvas_with_path.alpha_composite(path_img_rgba, (0, 0))
        
        # Preprocess image list
        pil_image_list = [tensor2pil(img).convert('RGBA') for img in image_list]
        
        # Select images based on mode
        selected_images, image_indices = self.select_images(
            pil_image_list, placement_count, placement_mode, rng
        )
        
        # Place images on canvas
        for i, point in enumerate(selected_points):
            img_idx = image_indices[i % len(image_indices)]
            pil_img = selected_images[img_idx]
            
            # Process image (rotate, scale, position)
            processed_img, paste_x, paste_y = self.process_image(
                pil_img, point, max_offset, max_rotation, 
                min_scale, max_scale, preserve_aspect_ratio, rng
            )
            
            # Paste image on both canvases
            canvas.alpha_composite(processed_img, (paste_x, paste_y))
            canvas_with_path.alpha_composite(processed_img, (paste_x, paste_y))
            
        print(f"[BK_ImageRandomLayout] ○ OUTPUT Placed {placement_count} images on canvas using {placement_mode} mode")
        
        # Convert results to tensors
        result = pil2tensor(canvas)
        result_with_path = pil2tensor(canvas_with_path)
        points_preview_tensor = pil2tensor(points_preview)
        
        return (result, result_with_path, points_preview_tensor)
