import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMessageBox, QSpinBox, QProgressDialog)
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

    def __init__(self, png_path, ico_path, size):
        super().__init__()
        self.png_path = png_path
        self.ico_path = ico_path
        self.size = size
        self._is_running = True

    def run(self):
        try:
            # 打开图片
            self.progress.emit(10)
            img = Image.open(self.png_path)
            self.progress.emit(30)
            # 保存为ICO文件
            img.save(self.ico_path, sizes=[(self.size, self.size)])
            self.progress.emit(100)
            self.finished.emit(True, "转换成功")
        except FileNotFoundError:
            self.finished.emit(False, f"未找到文件: {self.png_path}")
        except Exception as e:
            self.finished.emit(False, f"转换失败: {str(e)}")
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False
        self.quit()

class PngToIcoConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_png_path = None
        self.convert_thread = None
        self.progress_dialog = None
        
    def initUI(self):
        self.setWindowTitle('png_to_ico_converter')
        self.setWindowIcon(QIcon(':/icons/app_icon.png'))
        self.setGeometry(300, 300, 400, 300)
        
        # 主窗口部件
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # 布局
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # 图片预览
        self.image_label = QLabel('图片预览')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.image_label.setFixedHeight(200)
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
        
        # 选择文件按钮
        self.select_button = QPushButton('选择PNG文件')
        self.select_button.clicked.connect(self.select_png)
        self.button_layout.addWidget(self.select_button)
        
        # 转换按钮
        self.convert_button = QPushButton('转换为ICO')
        self.convert_button.clicked.connect(self.convert_to_ico)
        self.convert_button.setEnabled(False)
        self.button_layout.addWidget(self.convert_button)
        
        self.layout.addLayout(self.button_layout)
        
    def select_png(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PNG文件", "", 
            "PNG图像 (*.png)", 
            options=options
        )
        
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            # 检查文件大小
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > MAX_FILE_SIZE_MB:  # 大于5MB警告
                reply = QMessageBox.question(
                    self, '警告', 
                    f'选择的图像较大({file_size:.1f}MB)，可能会影响性能。是否继续?',
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            # 加载图像
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.current_png_path = file_path
                self.convert_button.setEnabled(True)
                self.update_image_preview(pixmap)
            else:
                raise Exception("无法加载图像")
        except Exception as e:
            self.reset_ui_state()
            QMessageBox.warning(self, "错误", f"加载图像失败: {str(e)}")

    def update_image_preview(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def reset_ui_state(self):
        self.current_png_path = None
        self.convert_button.setEnabled(False)
        self.image_label.clear()
        self.image_label.setText('图片预览')
    
    def convert_to_ico(self):
        if not self.current_png_path:
            return
            
        size = self.size_spinbox.value()
        default_name = os.path.splitext(os.path.basename(self.current_png_path))[0] + ".ico"
        default_dir = os.path.dirname(self.current_png_path)
        
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存ICO文件", 
            os.path.join(default_dir, default_name),
            "ICO图标 (*.ico)",
            options=options
        )
        
        if save_path:
            self.start_conversion(self.current_png_path, save_path, size)

    def start_conversion(self, png_path, ico_path, size):
        # 创建进度对话框
        self.progress_dialog = QProgressDialog("正在转换...", "取消", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.canceled.connect(self.cancel_conversion)
        self.progress_dialog.show()
        
        # 创建并启动转换线程
        self.convert_thread = ConvertThread(png_path, ico_path, size)
        self.convert_thread.finished.connect(self.conversion_finished)
        self.convert_thread.progress.connect(self.update_progress)
        self.convert_thread.start()

    def update_progress(self, value):
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            QApplication.processEvents()

    def conversion_finished(self, success, message):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "错误", message)
        
        if self.convert_thread:
            self.convert_thread.quit()
            self.convert_thread.wait()
            self.convert_thread = None

    def cancel_conversion(self):
        if self.convert_thread:
            self.convert_thread.stop()
            self.convert_thread.wait()
            self.convert_thread = None
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        QMessageBox.warning(self, "取消", "转换已取消")

    def closeEvent(self, event):
        # 清理资源
        if self.convert_thread and self.convert_thread.isRunning():
            self.convert_thread.stop()
            self.convert_thread.wait()
        
        if self.progress_dialog:
            self.progress_dialog.close()
        
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    converter = PngToIcoConverter()
    converter.show()
    sys.exit(app.exec_())
