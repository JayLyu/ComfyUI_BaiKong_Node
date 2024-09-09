# 计算颜色亮度
def relative_luminance(r, g, b):
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0

    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b

# 计算颜色对比度
def contrast_ratio(l1, l2):
    # l1 是亮度较大的颜色，l2 是较小的亮度
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


class BK_ColorLuminance:

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

    CATEGORY = "⭐️Baikong"
    RETURN_TYPES = ("STRING", "STRING", )
    RETURN_NAMES = ("BG_COLOR", "TEXT_COLOR", )
    FUNCTION = "exec"
    OUTPUT_NODE = False
    DESCRIPTION = "计算颜色明度，明度小于阈值返回亮色，大于阈值返回暗色"

    def exec(
        self,
        bg_hex_color,
        luminance_threshold=0.5,
        light_text_hex_color="",
        dark_text_hex_color="",
    ):
        light_text_hex_color = light_text_hex_color or "#FFFFFF"
        dark_text_hex_color = dark_text_hex_color or "#000000"

        bg_r, bg_g, bg_b = int(bg_hex_color[1:3], 16), int(
            bg_hex_color[3:5], 16), int(bg_hex_color[5:7], 16)
        bg_luminance = relative_luminance(bg_r, bg_g, bg_b)

        print(
            f"背景: {bg_hex_color}, 明度: {bg_luminance:.4f}, 阈值: {luminance_threshold}")

        if bg_luminance > luminance_threshold:
            text_color = dark_text_hex_color
            print(f"选择暗色文本: {text_color}")
        else:
            text_color = light_text_hex_color
            print(f"选择亮色文本: {text_color}")

        return {"ui": {"text": (bg_hex_color, text_color)}, "result": (bg_hex_color, text_color)}


# 测试代码
if __name__ == "__main__":
    process_node = BK_ColorLuminance()
    result = process_node.exec(
        bg_hex_color="#FF6500",
        luminance_threshold=0.5,
        light_text_hex_color="#dbb8bf",
        dark_text_hex_color="#4b3e41",
    )
    # print(f"结果: {result['result']}")
