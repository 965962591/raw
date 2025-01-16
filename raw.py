import cv2
import numpy as np

def read_raw10(raw_path, width, height, bayer_pattern='GRBG'):
    """
    优化后的函数：读取 10 位 MIPI RAW 图像并转换为 RGB 图像。
    
    :param raw_path: 输入 RAW 文件路径
    :param width: 图像宽度
    :param height: 图像高度
    :param bayer_pattern: Bayer 格式（'RGGB', 'BGGR', 'GRBG', 'GBRG'）
    :return: 转换后的 RGB 图像  
    """
    try:
        # 使用内置的文件读取方式，并确保文件被正确关闭
        with open(raw_path, 'rb') as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint8)
    except IOError as e:
        raise IOError(f"无法读取文件 {raw_path}: {e}")

    # 定义 stride，如果需要可以将其作为参数传入
    stride = 5120

    # 检查数据大小是否匹配
    expected_size = stride * height
    if raw_data.size != expected_size:
        raise ValueError(f"读取的 RAW 数据大小 ({raw_data.size}) 与期望的大小 ({expected_size}) 不匹配。请检查图像尺寸和 stride。")

    # 将数据重塑为 16 位以处理 10 位数据，然后提取有效位
    raw_image = raw_data.reshape((height, stride))
    raw_image = raw_image[:, :width]
    raw_image = raw_image.astype(np.uint16) << 2  # 假设原始数据是 10 位，左移2位

    # 将 10 位数据缩放到 8 位
    raw_image_8bit = cv2.convertScaleAbs(raw_image, alpha=(255.0/1023.0))

    # 根据 Bayer 格式选择 OpenCV 转换代码
    bayer_conversion_codes = {
        'RGGB': cv2.COLOR_BayerRG2RGB,
        'BGGR': cv2.COLOR_BayerBG2RGB,
        'GRBG': cv2.COLOR_BayerGR2RGB,
        'GBRG': cv2.COLOR_BayerGB2RGB
    }
    conversion_code = bayer_conversion_codes.get(bayer_pattern.upper())
    if conversion_code is None:
        raise ValueError(f"未知的 Bayer 格式: {bayer_pattern}")

    # 使用 OpenCV 进行去马赛克处理
    rgb_image = cv2.cvtColor(raw_image_8bit, conversion_code)

    # 将图像缩放到原来的0.1倍
    scale_factor = 0.2
    rgb_image = cv2.resize(rgb_image, (0, 0), fx=scale_factor, fy=scale_factor)

    return rgb_image

# if __name__ == "__main__":
#     # 优化后的示例用法
#     raw_path = r"C:\Users\chenyang3\Desktop\raw\test\dcim\IMG_20250115_231916.raw"
#     width = 4096  # 替换为实际图像宽度
#     height = 3072  # 替换为实际图像高度
#     bayer_pattern = 'GRBG'  # 替换为实际的 Bayer 格式

#     try:
#         rgb_image = read_raw10(raw_path, width, height, bayer_pattern)
#         cv2.imshow("RGB Image", rgb_image)
#         cv2.waitKey(0)
#     except Exception as e:
#         print(f"处理图像时出错: {e}")
#     finally:
#         cv2.destroyAllWindows()