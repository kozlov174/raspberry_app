import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QPushButton
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor, QPalette


class TimerApp(QWidget):
    def __init__(self, duration):
        super().__init__()
        self.duration = duration
        self.remaining_time = duration  # Остальное время

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Таймер")
        self.setGeometry(100, 100, 300, 300)

        # Установка палитры для фона
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)

        self.layout = QVBoxLayout()

        # Заголовок
        self.label = QLabel("")
        self.label.setFont(QFont("Arial", 18))
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        # Поле для отображения оставшегося времени
        self.remaining_label = QLabel("Осталось: ")
        self.remaining_label.setFont(QFont("Arial", 14))
        self.remaining_label.setAlignment(Qt.AlignCenter)
        self.remaining_label.hide()  # Скрываем по умолчанию
        self.layout.addWidget(self.remaining_label)

        self.setLayout(self.layout)

        # Показать сообщение о настройках
        self.label.setText("Прибор принимает команды настройки")
        self.show()

        # Таймер на 10 секунд для настройки
        self.setup_timer = QTimer(self)
        self.setup_timer.setSingleShot(True)
        self.setup_timer.timeout.connect(self.start_measurement)
        self.setup_timer.start(10000)  # 10 секунд

    def start_measurement(self):
        self.label.setText("Выполняются измерения")
        self.remaining_time = self.duration

        # Показываем поле "Осталось"
        self.remaining_label.show()

        # Обновляем оставшееся время каждую секунду
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_remaining_time)
        self.update_timer.start(1000)  # Обновление каждую секунду

        self.measurement_timer = QTimer(self)
        self.measurement_timer.setSingleShot(True)
        self.measurement_timer.timeout.connect(self.end_measurement)
        self.measurement_timer.start(self.duration * 1000)  # Таймер на заданное количество секунд

    def update_remaining_time(self):
        if self.remaining_time > 0:
            self.remaining_label.setText(f"Осталось: {self.remaining_time} секунд")
            self.remaining_time -= 1

    def end_measurement(self):
        self.update_timer.stop()  # Остановить таймер обновления
        self.remaining_label.hide()  # Скрываем поле "Осталось"
        self.label.setText("Выполняются вычисления")
        self.calculation_timer = QTimer(self)
        self.calculation_timer.setSingleShot(True)
        self.calculation_timer.timeout.connect(self.close_app)
        self.calculation_timer.start(10000)  # 10 секунд

    def close_app(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Получение количества секунд из аргументов командной строки
    if len(sys.argv) != 2:
        QMessageBox.critical(None, "Ошибка", "Необходимо указать количество секунд.")
        sys.exit(1)

    try:
        seconds = int(sys.argv[1])
        if seconds <= 0:
            raise ValueError("Время должно быть положительным.")
    except ValueError as e:
        QMessageBox.critical(None, "Ошибка", str(e))
        sys.exit(1)

    ex = TimerApp(seconds)
    sys.exit(app.exec_())
