import os
from PIL import Image

# 常量定义
MAX_FILE_SIZE_MB = 5
ICON_SIZE_MIN = 16
ICON_SIZE_MAX = 256
DEFAULT_ICON_SIZE = 64


class PngToIcoConverterCore:
    """PNG到ICO转换器核心类"""
    
    @staticmethod
    def convert(png_path: str, ico_path: str, size: int = DEFAULT_ICON_SIZE) -> tuple[bool, str]:
        """
        将PNG文件转换为ICO文件
        
        Args:
            png_path: PNG文件路径
            ico_path: ICO文件保存路径
            size: 图标尺寸
            
        Returns:
            tuple: (是否成功, 消息)
        """
        try:
            if not os.path.exists(png_path):
                return False, f"未找到文件: {png_path}"

            # 打开图片（Pillow）
            with Image.open(png_path) as img:
                # 保留透明通道并转换为 RGBA
                img = img.convert("RGBA")

                # 高质量缩放到目标尺寸
                target_size = (size, size)
                resized = img.resize(target_size, Image.LANCZOS)

                # 确保目标目录存在
                os.makedirs(os.path.dirname(ico_path) or ".", exist_ok=True)

                # 保存为 ICO，指定格式并传入 sizes 以确保正确生成
                resized.save(ico_path, format='ICO', sizes=[target_size])

            return True, "转换成功"
        except Exception as e:
            # 捕获所有异常并返回友好消息
            return False, f"转换失败: {str(e)}"