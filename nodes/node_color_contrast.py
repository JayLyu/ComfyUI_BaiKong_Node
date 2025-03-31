from .functions_color import relative_luminance, contrast_ratio

class BK_ColorContrast:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "bg_hex_color": ("STRING", { "default": "#FF0036" }),
                "WCAG_level": (["AA", "AAA"], { "default": "AA" }),
            },
            "optional": {
                "light_text_hex_color": ("STRING", { "default": "" }),
                "dark_text_hex_color": ("STRING", { "default": "" }),
            }
        }

    CATEGORY = "⭐️ Baikong/Color"
    RETURN_TYPES = ( "STRING", "STRING", )
    RETURN_NAMES = ("BG_COLOR", "TEXT_COLOR", )
    FUNCTION = "exec"
    OUTPUT_NODE = True
    DESCRIPTION = "计算颜色对比度，小于阈值返回亮色，大于阈值返回暗色"

    @staticmethod
    def parse_hex_color(hex_color, default="#FFFFFF", name="color"):
        """Safely parse a hex color string to RGB values"""
        # Ensure proper format with leading #
        if not hex_color.startswith('#'):
            hex_color = f"#{hex_color}"
        
        # Validate length
        if len(hex_color) != 7:
            print(f"[BK_ColorContrast] ├ WARNING Invalid {name} format: {hex_color}. Using {default} instead.")
            hex_color = default
            
        try:
            # Extract RGB components
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return hex_color, (r, g, b)
        except ValueError:
            print(f"[BK_ColorContrast] ├ WARNING Could not parse {name}: {hex_color}. Using {default} instead.")
            # Parse the default color instead
            r = int(default[1:3], 16)
            g = int(default[3:5], 16)
            b = int(default[5:7], 16)
            return default, (r, g, b)

    @staticmethod
    def get_luminance_and_contrast(bg_rgb, text_rgb):
        """Calculate luminance and contrast ratio between background and text colors"""
        # Calculate luminance values
        bg_luminance = relative_luminance(*bg_rgb)
        text_luminance = relative_luminance(*text_rgb)
        
        # Calculate contrast ratio
        contrast = contrast_ratio(text_luminance, bg_luminance)
        return bg_luminance, text_luminance, contrast

    def exec(
        self,
        bg_hex_color,
        WCAG_level = "AA",
        light_text_hex_color = "",
        dark_text_hex_color = "",
    ):
        """
        Calculate contrast ratio between background and text colors.
        Returns appropriate text color based on WCAG accessibility standards.
        """
        # Set default values if not provided
        light_text_hex_color = light_text_hex_color or "#FFFFFF"
        dark_text_hex_color = dark_text_hex_color or "#000000"
        
        # Log input
        print(f"[BK_ColorContrast] ○ INPUT Background color: {bg_hex_color}")
        
        # Parse colors with validation
        bg_hex_color, bg_rgb = self.parse_hex_color(bg_hex_color, default="#FF0036", name="background color")
        light_hex, light_rgb = self.parse_hex_color(light_text_hex_color, default="#FFFFFF", name="light text color")
        dark_hex, dark_rgb = self.parse_hex_color(dark_text_hex_color, default="#000000", name="dark text color")
        
        # Calculate background luminance
        bg_luminance, _, _ = self.get_luminance_and_contrast(bg_rgb, bg_rgb)
        print(f"[BK_ColorContrast] ├ PROCE Background luminance: {bg_luminance:.4f}")
        
        # Calculate luminance and contrast for light and dark text options
        _, light_luminance, light_contrast = self.get_luminance_and_contrast(bg_rgb, light_rgb)
        _, dark_luminance, dark_contrast = self.get_luminance_and_contrast(bg_rgb, dark_rgb)
        
        # Log contrast values
        print(f"[BK_ColorContrast] ├ PROCE Light contrast: {light_contrast:.2f}, Dark contrast: {dark_contrast:.2f}")
        
        # Determine WCAG contrast threshold
        threshold = 7.0 if WCAG_level == "AAA" else 4.5
        print(f"[BK_ColorContrast] ├ PROCE Using WCAG {WCAG_level} level, threshold: {threshold}")
        
        # Choose best text color based on contrast
        if light_contrast >= threshold and light_contrast >= dark_contrast:
            selected_color = light_hex
            contrast_value = light_contrast
            print(f"[BK_ColorContrast] ○ OUTPUT Selected light text color: {selected_color} (contrast: {contrast_value:.2f})")
        elif dark_contrast >= threshold:
            selected_color = dark_hex
            contrast_value = dark_contrast
            print(f"[BK_ColorContrast] ○ OUTPUT Selected dark text color: {selected_color} (contrast: {contrast_value:.2f})")
        else:
            # If neither meets threshold, choose the better one
            if light_contrast > dark_contrast:
                selected_color = light_hex
                contrast_value = light_contrast
            else:
                selected_color = dark_hex
                contrast_value = dark_contrast
                
            print(f"[BK_ColorContrast] ○ OUTPUT Neither contrast meets threshold. Selected {selected_color} with better contrast: {contrast_value:.2f}")
        
        # Return UI information and result
        return {
            "ui": {
                "text": [{
                    "bg_color": bg_hex_color,
                    "front_color": selected_color
                }],
            }, 
            "result": (bg_hex_color, selected_color)
        }

# if __name__ == "__main__":
#     process_node = BK_ColorContrast()
#     print(
#         process_node.exec(
#             bg_hex_color="#FF6500",
#             WCAG_level = "AAA",
#             light_text_hex_color = "#dbb8bf",
#             dark_text_hex_color = "#4b3e41",
#         )
#     )
