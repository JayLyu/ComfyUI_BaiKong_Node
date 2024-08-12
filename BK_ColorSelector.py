
class BK_ColorSelector:

    @classmethod
    def INPUT_TYPES(s):
        
        return {
            "required": {
                "hex_colors": ("STRING", {
                    "multiline": True,
                    "default": "#FF0036, #FF5000, #0065ff, #3D7FFF"
                }),
            },
            "optional": {
                "symbol": ("STRING", {
                    "multiline": False,
                    "default": ","
                }),
                "split_count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 4096,
                    "step": 1,
                    "display": "number"
                }),
            }
        }

    CATEGORY = "⭐️Baikong"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "select_color"
    OUTPUT_NODE = False

    def select_color(
        self,
        hex_colors,
        symbol: str = ",",
        split_count: int = 1,
    ):
        # 将 str 分割成 list
        color_list = hex_colors.split(symbol)
        # 确保值在有效范围内
        split_count = max(0, min(split_count - 1, len(color_list) - 1))
        # 提取指定颜色
        selected_color = color_list[split_count]
        # 去掉多余的空格
        selected_color = selected_color.replace(" ", "")

        out = selected_color
        return {"ui": {"text": (out,)}, "result": (out,)}


if __name__ == "__main__":
    selector_node = BK_ColorSelector()
    print(
        selector_node.select_color(
            hex_colors="#FF0036, #FF5000, #0065ff, #3D7FFF",
            symbol=",",
            split_count=1,
        )
    )
