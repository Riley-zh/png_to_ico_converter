import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QSpinBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image

# 常量定义
MAX_FILE_SIZE_MB = 5
ICON_SIZE_MIN = 16
ICON_SIZE_MAX = 256
DEFAULT_ICON_SIZE = 64


class ConvertThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, png_path: str, ico_path: str, size: int):
        super().__init__()
        self.png_path = png_path
        self.ico_path = ico_path
        self.size = size
        self._is_running = True

    def run(self):
        try:
            if not os.path.exists(self.png_path):
                self.finished.emit(False, f"未找到文件: {self.png_path}")
                return

            self.progress.emit(5)

            # 打开图片（Pillow）
            with Image.open(self.png_path) as img:
                if not self._is_running:
                    self.finished.emit(False, "已取消")
                    return

                self.progress.emit(20)

                # 保留透明通道并转换为 RGBA
                img = img.convert("RGBA")
                self.progress.emit(40)

                # 高质量缩放到目标尺寸
                target_size = (self.size, self.size)
                resized = img.resize(target_size, Image.LANCZOS)
                self.progress.emit(65)

                # 确保目标目录存在
                os.makedirs(os.path.dirname(self.ico_path) or ".", exist_ok=True)

                # 保存为 ICO，指定格式并传入 sizes 以确保正确生成
                resized.save(self.ico_path, format='ICO', sizes=[target_size])
                self.progress.emit(100)

            self.finished.emit(True, "转换成功")
        except Exception as e:
            # 捕获所有异常并返回友好消息
            self.finished.emit(False, f"转换失败: {str(e)}")
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False
        try:
            self.quit()
        except Exception:
            pass


class PngToIcoConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_png_path = None
        self.current_pixmap = None
        self.convert_thread = None
        self.progress_dialog = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PNG -> ICO 转换器')
        # 尝试设置图标（若资源不存在则忽略）
        if os.path.exists('app_icon.png'):
            self.setWindowIcon(QIcon('app_icon.png'))

        self.setGeometry(300, 300, 480, 360)
        self.setAcceptDrops(True)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # 图片预览
        self.image_label = QLabel('图片预览')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.image_label.setFixedHeight(220)
        self.layout.addWidget(self.image_label)

        # 尺寸选择
        self.size_layout = QHBoxLayout()
        self.size_label = QLabel('图标尺寸:')
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(ICON_SIZE_MIN, ICON_SIZE_MAX)
        self.size_spinbox.setValue(DEFAULT_ICON_SIZE)
        self.size_spinbox.setSuffix(' px')
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_spinbox)
        self.size_layout.addStretch()
        self.layout.addLayout(self.size_layout)

        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.select_button = QPushButton('选择 PNG 文件')
        self.select_button.clicked.connect(self.select_png)
        self.button_layout.addWidget(self.select_button)

        self.convert_button = QPushButton('转换为 ICO')
        self.convert_button.clicked.connect(self.convert_to_ico)
        self.convert_button.setEnabled(False)
        self.button_layout.addWidget(self.convert_button)

        self.layout.addLayout(self.button_layout)

    def select_png(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 PNG 文件", "",
            "PNG 图像 (*.png);;所有文件 (*)",
            options=options
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path: str):
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError("文件不存在")

            # 检查文件大小
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > MAX_FILE_SIZE_MB:
                reply = QMessageBox.question(
                    self, '警告',
                    f'选择的图像较大 ({file_size:.1f}MB)，可能会影响性能。是否继续?',
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise Exception("无法加载图像，可能不是有效的 PNG 文件")

            self.current_png_path = file_path
            self.current_pixmap = pixmap
            self.convert_button.setEnabled(True)
            self.update_image_preview()
        except Exception as e:
            self.reset_ui_state()
            QMessageBox.warning(self, "错误", f"加载图像失败: {str(e)}")

    def update_image_preview(self):
        if not self.current_pixmap:
            return
        scaled_pixmap = self.current_pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def reset_ui_state(self):
        self.current_png_path = None
        self.current_pixmap = None
        self.convert_button.setEnabled(False)
        self.image_label.clear()
        self.image_label.setText('图片预览')

    def convert_to_ico(self):
        if not self.current_png_path:
            return

        size = self.size_spinbox.value()
        default_name = os.path.splitext(os.path.basename(self.current_png_path))[0] + ".ico"
        default_dir = os.path.dirname(self.current_png_path) or "."

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存 ICO 文件",
            os.path.join(default_dir, default_name),
            "ICO 图标 (*.ico)",
            options=options
        )

        if not save_path:
            return

        # 自动补齐扩展名
        if not save_path.lower().endswith('.ico'):
            save_path += '.ico'

        self.start_conversion(self.current_png_path, save_path, size)

    def start_conversion(self, png_path: str, ico_path: str, size: int):
        # 创建进度对话框
        self.progress_dialog = QProgressDialog("正在转换...", "取消", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.canceled.connect(self.cancel_conversion)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

        # 启动线程
        self.convert_thread = ConvertThread(png_path, ico_path, size)
        self.convert_thread.finished.connect(self.conversion_finished)
        self.convert_thread.progress.connect(self.update_progress)
        self.convert_thread.start()

    def update_progress(self, value: int):
        if self.progress_dialog:
            self.progress_dialog.setValue(int(value))
            QApplication.processEvents()

    def conversion_finished(self, success: bool, message: str):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)

        if self.convert_thread:
            try:
                self.convert_thread.quit()
                self.convert_thread.wait(2000)
            except Exception:
                pass
            self.convert_thread = None

    def cancel_conversion(self):
        if self.convert_thread:
            self.convert_thread.stop()
            try:
                self.convert_thread.wait(2000)
            except Exception:
                pass
            self.convert_thread = None

        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        QMessageBox.warning(self, "取消", "转换已取消")

    def closeEvent(self, event):
        if self.convert_thread and self.convert_thread.isRunning():
            self.convert_thread.stop()
            try:
                self.convert_thread.wait(2000)
            except Exception:
                pass

        if self.progress_dialog:
            self.progress_dialog.close()

        super().closeEvent(event)

    # 拖放支持
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.png'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.png'):
                self.load_image(file_path)

    # 窗口大小改变时更新预览
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_preview()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    converter = PngToIcoConverter()
    converter.show()
    sys.exit(app.exec_())
