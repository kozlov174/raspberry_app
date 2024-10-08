import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Настройки прибора")
        self.setGeometry(100, 100, 250, 250)

        layout = QVBoxLayout()

        label = QLabel("Выполняются настройки прибора", self)
        label.setAlignment(Qt.AlignCenter)

        # Установка большего шрифта
        font = QFont()
        font.setPointSize(14)  # Увеличьте размер шрифта по вашему усмотрению
        label.setFont(font)

        layout.addWidget(label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
