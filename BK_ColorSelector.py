
class BK_ColorSelector:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "hex_colors": ("STRING", {
                    "multiline": True,
                    "default": "#FF0036, #FF5000, #0065ff, #3D7FFF"
                }),
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
                # "print_to_screen": (["enable", "disable"],),
            },
        }

    CATEGORY = "⭐️Baikong"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "select_color"
    OUTPUT_NODE = True

    def select_color(self, hex_colors, split_count, symbol, ):
        # if print_to_screen == "enable":
        #     print(f"""Your input contains:
        #         hex_colors: {hex_colors}
        #         split_count: {split_count}
        #     """)
        color_list = hex_colors.split(symbol)
        split_count = max(0, min(split_count - 1, len(color_list) - 1))
        selected_color = color_list[split_count]
        
        selected_color = selected_color.replace(" ", "")

        return (selected_color,)

# selector_node = BK_ColorSelector()
# input_colors = "#FF0036, #FF5000, #0065ff, #3D7FFF"
# print(selector_node.select_color(input_colors,  1, ",",True))
