import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CalculationsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Вычисления")
        self.setGeometry(100, 100, 600, 600)  # Устанавливаем размер окна 300x300

        layout = QVBoxLayout()

        # Добавляем надпись "Выполняются вычисления"
        self.label = QLabel("Выполняются вычисления", self)
        self.label.setAlignment(Qt.AlignCenter)

        # Установка шрифта
        font = QFont()
        font.setPointSize(36)  # Увеличиваем размер шрифта
        font.setBold(True)      # Устанавливаем жирный шрифт
        self.label.setFont(font)

        layout.addWidget(self.label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculationsWindow()
    window.show()
    sys.exit(app.exec_())
