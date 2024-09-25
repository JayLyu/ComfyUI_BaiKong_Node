
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
        # 如果用户没有输入，设置默认值
        light_text_hex_color = light_text_hex_color or "#FFFFFF"
        dark_text_hex_color = dark_text_hex_color or "#000000"
        
        # 解析 HEX 颜色为 RGB
        r = int(bg_hex_color[1:3], 16)
        g = int(bg_hex_color[3:5], 16)
        b = int(bg_hex_color[5:7], 16)

        # 计算背景色的亮度
        background_luminance = relative_luminance(r, g, b)

        # 计算文本颜色的亮度
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

        # 计算与自定义白色和黑色的对比度
        light_contrast = contrast_ratio(light_luminance, background_luminance)
        dark_contrast = contrast_ratio(dark_luminance, background_luminance)

        # 设置对比度阈值
        threshold = 7.0 if WCAG_level == "AAA" else 4.5

        # 根据对比度选择最佳的文字颜色
        if light_contrast >= threshold:
            out = light_text_hex_color
        elif dark_contrast >= threshold:
            out = dark_text_hex_color
        else:
            # 如果都不满足，可以尝试生成一个更合适的颜色
            out = dark_text_hex_color  # 默认黑色
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
