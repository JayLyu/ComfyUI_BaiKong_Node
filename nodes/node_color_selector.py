
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

    CATEGORY = "⭐️ Baikong/Color"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "select_color"
    OUTPUT_NODE = False
    DESCRIPTION = "从输入的多个十六进制颜色中，根据指定的索引选择一个颜色；输入的内容需使用英文逗号分隔"

    def select_color(
        self,
        hex_colors: str,
        symbol: str = ",",
        split_count: int = 1,
    ) -> dict:
        # 将 str 分割成 list，并去除每个颜色周围的空白
        color_list = [color.strip() for color in hex_colors.split(symbol)]

        # 确保值在有效范围内
        split_count = max(1, min(split_count, len(color_list))) - 1

        # 提取指定颜色
        selected_color = color_list[split_count]

        # 验证颜色格式
        if not self.is_valid_hex_color(selected_color):
            raise ValueError(f"无效的十六进制颜色: {selected_color}")

        return {
            "ui": {"text": [{"bg_color": selected_color, }], },
            "result": (selected_color,)
        }

    @staticmethod
    def is_valid_hex_color(color: str) -> bool:
        import re
        return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color))

# if __name__ == "__main__":
#     selector_node = BK_ColorSelector()
#     print(
#         selector_node.select_color(
#             hex_colors="#FF0036, #FF5000, #0065ff, #3D7FFF",
#             symbol=",",
#             split_count=1,
#         )
#     )
