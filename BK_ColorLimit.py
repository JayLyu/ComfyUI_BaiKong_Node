import colorsys


def rgb_to_hsl(rgb):
    # 将 rgb 元组转换成 hsl
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return h, s, l


def hsl_to_rgb(hsl):
    # 将 hsl 元组转换成 rgb
    h, s, l = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = int(r * 255.0)
    g = int(g * 255.0)
    b = int(b * 255.0)
    return r, g, b


class BK_ColorLimit:

    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "hex_color": ("STRING", {
                    "default": "#FF0036"
                }),
            },
            "optional": {
                "saturation_start": ("FLOAT", {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "saturation_end": ("FLOAT", {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "brightness_start": ("FLOAT", {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
                "brightness_end": ("FLOAT", {
                    "default": 0.5,
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "display": "slider"
                }),
            }
        }

    CATEGORY = "⭐️Baikong"
    RETURN_TYPES = (
        "STRING",
        # "STRING","STRING"
    )
    # RETURN_NAMES = ("hex", "rgb", "hsl", )
    FUNCTION = "color_limit"
    # OUTPUT_NODE = True

    def color_limit(
        self,
        hex_color,
        saturation_start: float = 0,
        saturation_end: float = 1,
        brightness_start: float = 0,
        brightness_end: float = 0.5,
    ):
        # 将 hex_color 转换成 rgb 元组
        hex_color = hex_color.lstrip('#')
        rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # 将 rgb 转换成 hsl
        h, s, l = rgb_to_hsl(rgb_color)

        # 四舍五入到小数点后两位
        h = round(h, 6)
        s = round(s, 6)
        l = round(l, 6)

        # s 的值必须在 saturation_start 和 saturation_end 之间
        s_new = max(saturation_start, min(s, saturation_end))

        # l 的值必须在 brightness_start 和 brightness_end 之间
        l_new = max(brightness_start, min(l, brightness_end))

        # print(f"hue:{h}")
        # print(
        #     f"saturation:{saturation_start} ~ {saturation_end}, value:{s}→{s_new}")
        # print(
        #     f"brightness:{brightness_start} ~ {brightness_end}, value:{l}→{l_new}")

        # 将 hsl 的值转换为 rgb
        rgb_new = hsl_to_rgb((h, s_new, l_new))

        # 构造新的 hex 表示
        hex_new = '#{:02x}{:02x}{:02x}'.format(*rgb_new)

        # 构造 RGB 的字符串表示
        rgb_string = f"({rgb_new[0]}, {rgb_new[1]}, {rgb_new[2]})"

        # 构造 HSL 的字符串表示
        hsl_string = f"({h}, {s_new}, {l_new})"

        return (
            hex_new,
            # rgb_string, hsl_string,
        )


if __name__ == "__main__":
    selector_node = BK_ColorLimit()
    print(
        selector_node.color_limit(
            hex_color="#FF0036",
            saturation_start=0,
            saturation_end=1,
            brightness_start=0,
            brightness_end=1,
        )
    )
