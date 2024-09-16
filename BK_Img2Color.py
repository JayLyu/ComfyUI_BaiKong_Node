# 参考自 https://github.com/christian-byrne/img2colors-comfyui-node

from typing import Tuple, List
import sys
import os
import torch
import webcolors
from PIL import Image, ImageDraw, ImageFont
from colornamer import get_color_from_rgb
from numpy import ndarray
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib
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
    CATEGORY = "⭐️Baikong"
    FUNCTION = "main"
    OUTPUT_NODE = True
    DESCRIPTION = "从输入图像中提取主要颜色，可指定颜色数量，支持排除特定颜色，并可选择生成互补色"

    def __init__(self):
        self.webcolor_dict = {**webcolors.CSS3_HEX_TO_NAMES, **webcolors.CSS2_HEX_TO_NAMES,
                              **webcolors.CSS21_HEX_TO_NAMES, **webcolors.HTML4_HEX_TO_NAMES}

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

    def generate_color_blocks(self, color_string: str) -> np.ndarray:
        colors = color_string.split(', ')
        fig, axs = plt.subplots(1, len(colors), figsize=(
            len(colors)*2, 2), squeeze=False)
        axs = axs.flatten()  # 将 axs 转换为一维数组，便于迭代

        for ax, color in zip(axs, colors):
            ax.imshow(np.full((10, 10, 3), np.array(
                matplotlib.colors.to_rgb(color))))
            ax.axis('off')

        plt.tight_layout()
        # plt.savefig('d:\\color_blocks.png')

        return plt

    def generate_palette(self, img: torch.Tensor, n_colors=16, cell_size=128, padding=0, font_path=None, font_size=15, mode='chart'):

        img = img.resize((img.width // 2, img.height // 2),
                         resample=Image.BILINEAR)
        pixels = np.array(img)
        pixels = pixels.reshape((-1, 3))
        kmeans = KMeans(n_clusters=n_colors, random_state=0,
                        n_init='auto').fit(pixels)
        cluster_centers = np.uint8(kmeans.cluster_centers_)

        # Get the sorted indices based on luminance
        luminance = np.sqrt(np.dot(cluster_centers, [0.299, 0.587, 0.114]))
        sorted_indices = np.argsort(luminance)

        # Rearrange the cluster centers and luminance based on sorted indices
        cluster_centers = cluster_centers[sorted_indices]
        luminance = luminance[sorted_indices]

        # Group colors by their individual types
        reds = []
        greens = []
        blues = []
        others = []

        for i in range(n_colors):
            color = cluster_centers[i]
            color_type = np.argmax(color)  # Find the dominant color component

            if color_type == 0:
                reds.append((color, luminance[i]))
            elif color_type == 1:
                greens.append((color, luminance[i]))
            elif color_type == 2:
                blues.append((color, luminance[i]))
            else:
                others.append((color, luminance[i]))

        # Sort each color group by luminance
        reds.sort(key=lambda x: x[1])
        greens.sort(key=lambda x: x[1])
        blues.sort(key=lambda x: x[1])
        others.sort(key=lambda x: x[1])

        # Combine the sorted color groups
        sorted_colors = reds + greens + blues + others

        if mode == 'back_to_back':
            # Calculate the size of the palette image based on the number of colors
            palette_width = n_colors * cell_size
            palette_height = cell_size
        else:
            # Calculate the number of rows and columns based on the number of colors
            num_rows = int(np.sqrt(n_colors))
            num_cols = int(np.ceil(n_colors / num_rows))

            # Calculate the size of the palette image based on the number of rows and columns
            palette_width = num_cols * cell_size
            palette_height = num_rows * cell_size

        palette_size = (palette_width, palette_height)

        palette = Image.new('RGB', palette_size, color='white')
        draw = ImageDraw.Draw(palette)
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()

        hex_palette = []
        for i, (color, _) in enumerate(sorted_colors):
            if mode == 'back_to_back':
                cell_x = i * cell_size
                cell_y = 0
            else:
                row = i % num_rows
                col = i // num_rows
                cell_x = col * cell_size
                cell_y = row * cell_size

            cell_width = cell_size
            cell_height = cell_size

            color = tuple(color)

            cell = Image.new('RGB', (cell_width, cell_height), color=color)
            palette.paste(cell, (cell_x, cell_y))

            if mode != 'back_to_back':
                text_x = cell_x + (cell_width / 2)
                text_y = cell_y + cell_height + padding

                draw.text((text_x + 1, text_y + 1),
                          f"R: {color[0]} G: {color[1]} B: {color[2]}", font=font, fill='black', anchor='ms')
                draw.text(
                    (text_x, text_y), f"R: {color[0]} G: {color[1]} B: {color[2]}", font=font, fill='white', anchor='ms')

            hex_palette.append('#%02x%02x%02x' % color)

        return palette, '\n'.join(hex_palette)


if __name__ == "__main__":
    bk_img2color = BK_Img2Color()
    input_path = r"E:\\ComfyUI\\input\\ice.png"
    input_image = Image.open(input_path)
    input_tensor = torch.from_numpy(
        np.array(input_image)).permute(2, 0, 1).float() / 255.0
    result = bk_img2color.main(input_tensor, num_colors=3, accuracy=80,
                               get_complementary_color=False, exclude_colors="", select_color=2)
    print(f"所有颜色: {result[0]}")
    print(f"选中的颜色: {result[1]}")
