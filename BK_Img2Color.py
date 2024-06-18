
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
    CATEGORY = "⭐️Baikong"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_image": ("IMAGE",),
                "num_colors": ("INT", {"default": 3, "min": 1}),
                "get_complementary": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_off": "Get Original Colors",
                        "label_on": "Get Complementary Colors",
                    },
                ),
                "k_means_algorithm": (
                    ["lloyd", "elkan"],
                    {
                        "default": "lloyd",
                    },
                ),
                "accuracy": (
                    "INT",
                    {
                        "default": 60,
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
            },
        }

    RETURN_TYPES = (
        "STRING",
        # "IMAGE"
    )
    # RETURN_NAMES = (
    #     "hex_colors",
    #     "preview"
    # )
    FUNCTION = "main"
    OUTPUT_NODE = True

    def main(
        self,
        input_image: torch.Tensor,
        num_colors: int = 5,
        k_means_algorithm: str = "lloyd",
        accuracy: int = 80,
        get_complementary: bool = False,
        exclude_colors: str = "",
    ) -> Tuple[str, ...]:
        
        # print(input_image)

        if exclude_colors.strip():
            self.exclude = exclude_colors.strip().split(",")
            self.exclude = [color.strip().lower() for color in self.exclude]
        else:
            self.exclude = []

        self.num_iterations = int(512 * (accuracy / 100))
        self.algorithm = k_means_algorithm
        self.webcolor_dict = webcolors.CSS3_HEX_TO_NAMES
        self.webcolor_dict.update(webcolors.CSS2_HEX_TO_NAMES,)
        self.webcolor_dict.update(webcolors.CSS21_HEX_TO_NAMES,)
        self.webcolor_dict.update(webcolors.HTML4_HEX_TO_NAMES,)
        print(self.webcolor_dict)

        original_colors = self.interrogate_colors(input_image, num_colors)
        rgb = self.ndarrays_to_rgb(original_colors)

        if get_complementary:
            rgb = self.rgb_to_complementary(rgb)

        hex_colors = [
            f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}" for color in rgb]

        # color_blocks = self.generate_color_blocks(
        #     self.join_and_exclude(hex_colors))
        
        # palette_image, palette = self.generate_palette(
        #     img = input_image, 
        #     n_colors=num_colors, 
        #     cell_size=128, 
        #     padding=10, 
        #     font_path="", 
        #     font_size=15, 
        #     mode=mode.lower()
        #     )

        return (
            self.join_and_exclude(hex_colors), 
            # color_blocks
            )

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
        colors = (
            KMeans(
                n_clusters=num_colors,
                algorithm=self.algorithm,
                max_iter=self.num_iterations,
            )
            .fit(pixels)
            .cluster_centers_
            * 255
        )
        return colors

    def generate_color_blocks(self, color_string: str) -> np.ndarray:
        colors = color_string.split(', ')
        fig, axs = plt.subplots(1, len(colors), figsize=(len(colors)*2, 2), squeeze=False)
        axs = axs.flatten()  # 将 axs 转换为一维数组，便于迭代

        for ax, color in zip(axs, colors):
            ax.imshow(np.full((10, 10, 3), np.array(
                matplotlib.colors.to_rgb(color))))
            ax.axis('off')

        plt.tight_layout()
        plt.savefig('d:\\color_blocks.png')

        return plt
    
    def generate_palette(self, img:torch.Tensor, n_colors=16, cell_size=128, padding=0, font_path=None, font_size=15, mode='chart'):

        img = img.resize((img.width // 2, img.height // 2), resample=Image.BILINEAR)
        pixels = np.array(img)
        pixels = pixels.reshape((-1, 3))
        kmeans = KMeans(n_clusters=n_colors, random_state=0, n_init='auto').fit(pixels)
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

                draw.text((text_x + 1, text_y + 1), f"R: {color[0]} G: {color[1]} B: {color[2]}", font=font, fill='black', anchor='ms')
                draw.text((text_x, text_y), f"R: {color[0]} G: {color[1]} B: {color[2]}", font=font, fill='white', anchor='ms')

            hex_palette.append('#%02x%02x%02x' % color)

        return palette, '\n'.join(hex_palette)


# test = BK_Img2Color()
# input = "E:\ComfyUI\input\ice.png"
# print(test.main(input,  5, "lloyd", 80, False, "", None, None))