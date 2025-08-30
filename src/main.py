import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication
from .gui import PngToIcoConverterGUI

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    converter = PngToIcoConverterGUI()
    converter.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()