import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

class SavedWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Уведомление")
        self.setGeometry(200, 200, 500, 200)

        layout = QVBoxLayout()

        # Надпись "Изменения сохранены"
        self.label = QLabel("Изменения сохранены", self)
        self.label.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.label.setFont(font)

        layout.addWidget(self.label)
        self.setLayout(layout)

        # Таймер на 2 секунды, после чего окно закрывается
        QTimer.singleShot(2000, self.close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SavedWindow()
    window.show()
    sys.exit(app.exec_())
