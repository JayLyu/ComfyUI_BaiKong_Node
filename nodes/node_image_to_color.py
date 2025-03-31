"""
Image to Color Node - Extract dominant colors from an input image using K-means clustering.
Allows selecting a specific color from the extraction results.
"""
from typing import Tuple, List, Dict, Any, Union
import torch
import numpy as np
from numpy import ndarray
from sklearn.cluster import KMeans


class BK_Img2Color:
    """
    Extract dominant colors from an input image using K-means clustering.
    Allows selecting specific colors and generating complementary colors.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_image": ("IMAGE",),
            },
            "optional": {
                "num_colors": ("INT", {"default": 1, "min": 1, }),
                "get_complementary_color": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_off": "false",
                        "label_on": "true",
                    },
                ),
                "accuracy": (
                    "INT",
                    {
                        "default": 80,
                        "display": "slider",
                        "min": 1,
                        "max": 100,
                    },
                ),
                "exclude_colors": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
                "select_color": ("INT", {
                    "default": 1,
                    "min": 1,
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("COLORS", "SELECT_COLOR",)
    CATEGORY = "⭐️ Baikong/Color"
    FUNCTION = "main"
    # OUTPUT_NODE = True
    DESCRIPTION = "从输入图像中提取主要颜色，可指定颜色数量，支持排除特定颜色，并可选择生成互补色"

    @staticmethod
    def rgb_to_hex(color: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hexadecimal color string"""
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hexadecimal color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_complementary(colors: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
        """Generate complementary colors by inverting RGB values"""
        return [(255 - color[0], 255 - color[1], 255 - color[2]) for color in colors]

    @staticmethod
    def ndarrays_to_rgb(colors: List[ndarray]) -> List[Tuple[int, int, int]]:
        """Convert numpy arrays of colors to RGB tuples"""
        return [(int(min(255, max(0, color[0]))), 
                 int(min(255, max(0, color[1]))), 
                 int(min(255, max(0, color[2])))) for color in colors]

    def filter_excluded_colors(self, colors: List[str], excluded: List[str]) -> List[str]:
        """Filter out excluded colors from the list"""
        if not excluded:
            return colors
        
        # Perform caseless comparison for exclusion
        return [color for color in colors if color.lower() not in excluded]

    def extract_colors(self, image: torch.Tensor, num_colors: int, max_iterations: int) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from image using K-means clustering"""
        try:
            # Handle potential shape issues
            if len(image.shape) < 3 or image.shape[-1] < 3:
                print(f"[BK_Img2Color] ├ WARNING Invalid image format with shape {image.shape}. Expected RGB/RGBA image.")
                # Create fallback values for grayscale images
                if len(image.shape) == 3 and image.shape[-1] == 1:
                    # Convert grayscale to RGB
                    gray_value = int(image.mean().item() * 255)
                    return [(gray_value, gray_value, gray_value)]
                return [(128, 128, 128)]  # Default gray if completely invalid
                
            # Prepare pixels for clustering
            if image.shape[-1] > 3:  # Handle alpha channel if present
                pixels = image[..., :3].reshape(-1, 3).numpy()  # Use only RGB channels
            else:
                pixels = image.reshape(-1, image.shape[-1]).numpy()
                
            # Calculate appropriate number of init attempts based on accuracy
            n_init = max(1, min(10, int(max_iterations / 100)))
            
            # Perform K-means clustering
            kmeans = KMeans(
                n_clusters=num_colors, 
                algorithm="lloyd",
                max_iter=max_iterations, 
                n_init=n_init,
                random_state=42  # For reproducibility
            )
            
            # Fit and extract colors
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_ * 255
            
            # Sort colors by cluster size (most frequent first)
            color_counts = np.bincount(kmeans.labels_)
            sorted_indices = np.argsort(color_counts)[::-1]
            sorted_colors = colors[sorted_indices]
            
            # Convert to RGB tuples
            return self.ndarrays_to_rgb(sorted_colors)
            
        except Exception as e:
            print(f"[BK_Img2Color] ├ ERROR Failed to extract colors: {str(e)}")
            return [(128, 128, 128)]  # Default gray on error

    def main(self, 
             input_image: torch.Tensor, 
             num_colors: int = 5, 
             accuracy: int = 80,
             get_complementary_color: bool = False, 
             exclude_colors: str = "", 
             select_color: int = 1) -> Dict[str, Any]:
        """
        Extract dominant colors from an input image.
        
        Args:
            input_image: Input tensor image
            num_colors: Number of colors to extract
            accuracy: Processing accuracy (affects k-means iterations)
            get_complementary_color: Whether to generate complementary colors
            exclude_colors: Comma-separated list of hex colors to exclude
            select_color: Index of color to select (1-based)
            
        Returns:
            Dictionary with UI information and result tuple of (all_colors, selected_color)
        """
        # Parameter validation
        num_colors = max(1, min(20, num_colors))  # Limit to reasonable range
        accuracy = max(1, min(100, accuracy))
        select_color = max(1, select_color)
        
        # Calculate k-means iterations based on accuracy
        max_iterations = int(512 * (accuracy / 100))
        
        # Parse excluded colors
        excluded = [color.strip().lower() for color in exclude_colors.strip().split(",") 
                   if color.strip()]
        
        # Log input parameters
        print(f"[BK_Img2Color] ○ INPUT Image shape: {input_image.shape}, "
              f"Extracting {num_colors} colors with accuracy {accuracy}%")
        
        # Extract colors from image
        rgb_colors = self.extract_colors(input_image, num_colors, max_iterations)
        print(f"[BK_Img2Color] ├ PROCE Extracted {len(rgb_colors)} colors")
        
        # Generate complementary colors if requested
        if get_complementary_color:
            rgb_colors = self.rgb_to_complementary(rgb_colors)
            print("[BK_Img2Color] ├ PROCE Generated complementary colors")
        
        # Convert to hex format
        hex_colors = [self.rgb_to_hex(color) for color in rgb_colors]
        
        # Filter excluded colors
        filtered_colors = self.filter_excluded_colors(hex_colors, excluded)
        if len(filtered_colors) < len(hex_colors):
            print(f"[BK_Img2Color] ├ PROCE Excluded {len(hex_colors) - len(filtered_colors)} colors")
        
        # Handle empty result after exclusion
        if not filtered_colors:
            print("[BK_Img2Color] ├ WARNING All colors were excluded. Using default gray.")
            filtered_colors = ["#808080"]  # Default gray
        
        # Join colors as comma-separated string
        color_string = ", ".join(filtered_colors)
        
        # Select specific color
        if select_color > len(filtered_colors):
            selected_color = filtered_colors[-1]  # Last color if index out of range
            print(f"[BK_Img2Color] ├ WARNING Select index {select_color} out of range, using last color")
        else:
            selected_color = filtered_colors[select_color - 1]  # 1-based indexing
        
        print(f"[BK_Img2Color] ○ OUTPUT Selected color: {selected_color}, All colors: {color_string}")
        
        # Return results
        return {
            "ui": {"text": (color_string, selected_color)}, 
            "result": (color_string, selected_color)
        }

# if __name__ == "__main__":
#     bk_img2color = BK_Img2Color()
#     input_path = r"./GetImageColor.png"
#     input_image = Image.open(input_path)
#     input_tensor = torch.from_numpy(
#         np.array(input_image)).permute(2, 0, 1).float() / 255.0
#     result = bk_img2color.main(input_tensor, num_colors=3, accuracy=80,
#                                get_complementary_color=False, exclude_colors="", select_color=2)
#     print(f"所有颜色: {result[0]}")
#     print(f"选中的颜色: {result[1]}")
