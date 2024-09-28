# 参考自 https://github.com/christian-byrne/img2colors-comfyui-node

from typing import Tuple, List
import sys
import os
import torch

from sklearn.cluster import KMeans

from numpy import ndarray
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class BK_Img2Color:

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

    def __init__(self):
        pass

    def main(self, input_image: torch.Tensor, num_colors: int = 5, accuracy: int = 80,
             get_complementary_color: bool = False, exclude_colors: str = "", select_color: int = 1) -> Tuple[str, str]:
        self.exclude = [color.strip().lower() for color in exclude_colors.strip().split(
            ",")] if exclude_colors.strip() else []
        self.num_iterations = int(512 * (accuracy / 100))

        original_colors = self.interrogate_colors(input_image, num_colors)
        rgb = self.ndarrays_to_rgb(original_colors)

        if get_complementary_color:
            rgb = self.rgb_to_complementary(rgb)

        hex_colors = [
            f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}" for color in rgb]
        out = self.join_and_exclude(hex_colors)

        # 处理 select_color
        color_list = out.split(", ")
        selected_color = color_list[-1] if select_color > len(
            color_list) else color_list[select_color - 1]

        # 指定的输出格式 {"ui": {"text": (value1, value2)}, "result":  (value1, value2)}
        return {"ui": {"text": (out, selected_color)}, "result": (out, selected_color)}

    def join_and_exclude(self, colors: List[str]) -> str:
        return ", ".join(
            [str(color)
             for color in colors if color.lower() not in self.exclude]
        )

    def rgb_to_complementary(
        self, colors: List[Tuple[int, int, int]]
    ) -> List[Tuple[int, int, int]]:
        return [(255 - color[0], 255 - color[1], 255 - color[2]) for color in colors]

    def ndarrays_to_rgb(self, colors: List[ndarray]) -> List[Tuple[int, int, int]]:
        return [(int(color[0]), int(color[1]), int(color[2])) for color in colors]

    def interrogate_colors(self, image: torch.Tensor, num_colors: int) -> List[ndarray]:
        pixels = image.view(-1, image.shape[-1]).numpy()
        kmeans = KMeans(n_clusters=num_colors, algorithm="lloyd",
                        max_iter=self.num_iterations, n_init=10)
        colors = kmeans.fit(pixels).cluster_centers_ * 255
        return colors


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
