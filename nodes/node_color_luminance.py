from .functions_color import relative_luminance

class BK_ColorLuminance:
    """
    Node for determining appropriate text color based on background color luminance.
    Calculates luminance of a background color and compares with threshold to determine
    if light or dark text should be used for better readability.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bg_hex_color": ("STRING", {"default": "#FF0036"}),
                "luminance_threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "display": "slider"}),
            },
            "optional": {
                "light_text_hex_color": ("STRING", {"default": ""}),
                "dark_text_hex_color": ("STRING", {"default": ""}),
            }
        }

    CATEGORY = "⭐️ Baikong/Color"
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("BG_COLOR", "TEXT_COLOR", )
    FUNCTION = "exec"
    OUTPUT_NODE = True
    DESCRIPTION = "计算颜色明度，明度小于阈值返回亮色，大于阈值返回暗色"

    @staticmethod
    def parse_hex_color(hex_color, default="#FFFFFF", name="color"):
        """Safely parse a hex color string to RGB values"""
        # Ensure proper format with leading #
        if not hex_color.startswith('#'):
            hex_color = f"#{hex_color}"
        
        # Validate length
        if len(hex_color) != 7:
            print(f"[BK_ColorLuminance] ├ WARNING Invalid {name} format: {hex_color}. Using {default} instead.")
            hex_color = default
            
        try:
            # Extract RGB components
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return hex_color, (r, g, b)
        except ValueError:
            print(f"[BK_ColorLuminance] ├ WARNING Could not parse {name}: {hex_color}. Using {default} instead.")
            # Parse the default color instead
            r = int(default[1:3], 16)
            g = int(default[3:5], 16)
            b = int(default[5:7], 16)
            return default, (r, g, b)

    def exec(
        self,
        bg_hex_color,
        luminance_threshold=0.5,
        light_text_hex_color="",
        dark_text_hex_color="",
    ):
        """
        Determine appropriate text color based on background color luminance.
        
        Args:
            bg_hex_color: Background color in hex format
            luminance_threshold: Threshold for determining light vs dark text (0.0-1.0)
            light_text_hex_color: Light text color (default #FFFFFF if empty)
            dark_text_hex_color: Dark text color (default #000000 if empty)
            
        Returns:
            Dictionary containing UI information and result tuple of (bg_color, text_color)
        """
        # Set default values if not provided
        light_text_hex_color = light_text_hex_color or "#FFFFFF"
        dark_text_hex_color = dark_text_hex_color or "#000000"
        
        # Validate luminance threshold
        luminance_threshold = max(0.0, min(1.0, luminance_threshold))
        
        # Log input
        print(f"[BK_ColorLuminance] ○ INPUT Background color: {bg_hex_color}, Threshold: {luminance_threshold:.2f}")
        
        # Parse colors with validation
        bg_hex_color, bg_rgb = self.parse_hex_color(bg_hex_color, default="#FF0036", name="background color")
        light_hex, _ = self.parse_hex_color(light_text_hex_color, default="#FFFFFF", name="light text color")
        dark_hex, _ = self.parse_hex_color(dark_text_hex_color, default="#000000", name="dark text color")
        
        # Calculate background luminance
        bg_luminance = relative_luminance(*bg_rgb)
        print(f"[BK_ColorLuminance] ├ PROCE Background luminance: {bg_luminance:.4f} (Threshold: {luminance_threshold:.2f})")
        
        # Determine appropriate text color based on luminance
        if bg_luminance > luminance_threshold:
            selected_color = dark_hex
            color_type = "dark"
        else:
            selected_color = light_hex
            color_type = "light"
            
        print(f"[BK_ColorLuminance] ○ OUTPUT Selected {color_type} text color: {selected_color}")
        
        # Return UI information and result
        return {
            "ui": {"text": [{"bg_color": bg_hex_color, "front_color": selected_color}], },
            "result": (bg_hex_color, selected_color)
        }

# 测试代码
# if __name__ == "__main__":
#     process_node = BK_ColorLuminance()
#     result = process_node.exec(
#         bg_hex_color="#FF6500",
#         luminance_threshold=0.5,
#         light_text_hex_color="#dbb8bf",
#         dark_text_hex_color="#4b3e41",
#     )
#     print(f"结果: {result['result']}")
