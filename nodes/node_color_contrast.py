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

    def exec(
        self,
        bg_hex_color,
        WCAG_level = "AA",
        light_text_hex_color = "",
        dark_text_hex_color = "",
    ):
        # Set default values if not provided
        light_text_hex_color = light_text_hex_color or "#FFFFFF"
        dark_text_hex_color = dark_text_hex_color or "#000000"
        
        print(f"[BK_ColorContrast] ○ Input bg_hex_color: {bg_hex_color}")
        
        # Parse HEX colors to RGB
        r, g, b = int(bg_hex_color[1:3], 16), int(bg_hex_color[3:5], 16), int(bg_hex_color[5:7], 16)

        # Calculate background luminance
        background_luminance = relative_luminance(r, g, b)
        print(f"[BK_ColorContrast] ├ PROCE luminance: {background_luminance:.4f}")

        # Calculate text color luminance
        light_luminance = relative_luminance(
            int(light_text_hex_color[1:3], 16),
            int(light_text_hex_color[3:5], 16),
            int(light_text_hex_color[5:7], 16)
        )
        dark_luminance = relative_luminance(
            int(dark_text_hex_color[1:3], 16),
            int(dark_text_hex_color[3:5], 16),
            int(dark_text_hex_color[5:7], 16)
        )

        # Calculate contrast ratios
        light_contrast = contrast_ratio(light_luminance, background_luminance)
        dark_contrast = contrast_ratio(dark_luminance, background_luminance)
        print(f"[BK_ColorContrast] ├ PROCE Light contrast: {light_contrast:.2f}, Dark contrast: {dark_contrast:.2f}")

        # Set contrast threshold
        threshold = 7.0 if WCAG_level == "AAA" else 4.5
        print(f"[BK_ColorContrast] ├ PROCE Using WCAG {WCAG_level} level, threshold: {threshold}")

        # Choose best text color based on contrast
        if light_contrast >= threshold:
            out = light_text_hex_color
            print(f"[BK_ColorContrast] ○ OUTPUT light_text_color: {out}")
        elif dark_contrast >= threshold:
            out = dark_text_hex_color
            print(f"[BK_ColorContrast] ○ OUTPUT dark_text_color: {out}")
        else:
            out = dark_text_hex_color  # Default to dark color
            print(f"[BK_ColorContrast] Neither contrast meets threshold. Defaulting to dark color: {out}")

        return {
            "ui": {
                "text": [{
                    "bg_color": bg_hex_color,
                    "front_color": out
                }],
            }, 
            "result": (bg_hex_color, out)
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
