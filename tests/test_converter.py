import unittest
import os
import tempfile
from src.converter import PngToIcoConverterCore

class TestPngToIcoConverter(unittest.TestCase):
    
    def test_converter_import(self):
        """测试是否能正确导入转换器"""
        self.assertTrue(hasattr(PngToIcoConverterCore, 'convert'))
        
    def test_constants_exist(self):
        """测试常量是否定义"""
        from src.converter import MAX_FILE_SIZE_MB, ICON_SIZE_MIN, ICON_SIZE_MAX, DEFAULT_ICON_SIZE
        self.assertIsNotNone(MAX_FILE_SIZE_MB)
        self.assertIsNotNone(ICON_SIZE_MIN)
        self.assertIsNotNone(ICON_SIZE_MAX)
        self.assertIsNotNone(DEFAULT_ICON_SIZE)

if __name__ == '__main__':
    unittest.main()