export function getBestTextColor(hexColor) {
    // 将 HEX 颜色转换为 RGB
    const rgb = parseInt(hexColor.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = (rgb >> 0) & 0xff;

    // 将 RGB 分量转换为相对亮度
    const [red, green, blue] = [r, g, b].map((channel) => {
        const c = channel / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    // 计算背景色的相对亮度
    const backgroundLuminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue;

    // 定义白色和黑色的亮度
    const whiteLuminance = 1.0;
    const blackLuminance = 0.0;

    // 计算与白色、黑色的对比度
    const contrastWithWhite = (whiteLuminance + 0.05) / (backgroundLuminance + 0.05);
    const contrastWithBlack = (backgroundLuminance + 0.05) / (blackLuminance + 0.05);

    // 返回对比度较高的颜色
    return contrastWithWhite > contrastWithBlack ? '#FFFFFF' : '#000000';
}