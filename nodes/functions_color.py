import colorsys

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


# 将 rgb 元组转换成 hsl
def rgb_to_hsl(rgb):
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return h, s, l


# 将 hsl 元组转换成 rgb
def hsl_to_rgb(hsl):
    h, s, l = hsl
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = int(r * 255.0)
    g = int(g * 255.0)
    b = int(b * 255.0)
    return r, g, b

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
