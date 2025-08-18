import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont


class TimerWindow(QWidget):
    def __init__(self, countdown_time):
        super().__init__()
        self.countdown_time = countdown_time

        self.setWindowTitle("Таймер")
        self.setGeometry(100, 100, 600, 600)  # Устанавливаем размер окна 300x300

        layout = QVBoxLayout()

        # Добавляем надпись "Выполняются измерения"
        self.title_label = QLabel("Выполняются измерения", self)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Установка шрифта
        title_font = QFont()
        title_font.setPointSize(36)  # Увеличиваем размер шрифта
        title_font.setBold(True)  # Устанавливаем жирный шрифт
        self.title_label.setFont(title_font)

        layout.addWidget(self.title_label)

        # Добавляем метку для оставшегося времени
        self.timer_label = QLabel(f"Осталось: {self.countdown_time} секунд", self)
        self.timer_label.setAlignment(Qt.AlignCenter)

        # Установка шрифта
        timer_font = QFont()
        timer_font.setPointSize(30)  # Увеличиваем размер шрифта
        timer_font.setBold(True)  # Устанавливаем жирный шрифт
        self.timer_label.setFont(timer_font)

        layout.addWidget(self.timer_label)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1 секунда

    def update_timer(self):
        if self.countdown_time > 0:
            self.countdown_time -= 1
            self.timer_label.setText(f"Осталось: {self.countdown_time} секунд")
        else:
            self.timer.stop()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python timer_window.py <время в секундах>")
        sys.exit(1)

    try:
        countdown_time = int(sys.argv[1])
    except ValueError:
        print("Пожалуйста, введите целое число.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = TimerWindow(countdown_time)
    window.show()
    sys.exit(app.exec_())
