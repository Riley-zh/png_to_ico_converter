# PNG 转 ICO 工具

## 简介
一个基于 PyQt5 + Pillow 的桌面工具，用于将 PNG 图像转换为 ICO 图标。包含图像预览、拖放导入、转换进度与取消、保留透明通道等实用改进。

## 项目结构
```
png_to_ico_converter/
├── src/                 # 源代码目录
│   ├── __init__.py      # Python包初始化文件
│   ├── converter.py     # 核心转换逻辑
│   ├── gui.py           # 图形界面
│   └── main.py          # 程序入口
├── tests/               # 测试文件目录
├── docs/                # 文档目录
├── requirements.txt     # 项目依赖
└── README.md           # 项目说明
```

## 功能特性
- 保留 PNG 透明通道（RGBA）并使用高质量重采样（LANCZOS）。
- 支持自定义图标尺寸（16–256 px）。
- 支持拖放加载 PNG 文件。
- 转换在后台线程执行，带有进度对话框与"取消"功能。
- 自动在保存文件名末尾补全 `.ico` 扩展名。
- 当 PNG 文件过大（默认 5MB）时提示用户。
- 运行时窗口调整会自动缩放预览图像。
- 更完善的错误处理与用户提示。

## 运行要求
- Python 3.7+
- Windows / 其它平台均可运行

## 安装依赖
在命令行中运行：
```bash
pip install -r requirements.txt
```

## 快速使用
1. 进入项目目录：
   ```bash
   cd png_to_ico_converter
   ```
2. 运行程序（任选其一）：
   ```bash
   python -m src.main
   ```
   或者：
   ```bash
   python run.py
   ```
3. 在窗口中：
   - 点击"选择 PNG 文件"或直接将 PNG 文件拖入窗口加载预览。
   - 设置所需图标尺寸（像素）。
   - 点击"转换为 ICO"，在保存对话框选择保存位置并确认（程序会自动补全 .ico 后缀）。
   - 转换过程中可点击"取消"终止操作。

## 注意事项与常见问题
- 文件大小提示阈值默认 5MB，超过时会询问是否继续。
- 程序会尽量保留 PNG 的透明通道；若输入非标准 PNG，生成结果可能有差异。
- 若出现 "无法加载图像" 或 GUI 无法启动，确认依赖是否正确安装。
- 若要在无 GUI 环境运行，可使用核心转换逻辑构建命令行工具。

## 许可证
该项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。