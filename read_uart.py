import serial
import time

# Настройка UART
ser = serial.Serial(
    port='/dev/serial0',  # Для Raspberry Pi 3/4/5 UART порт обычно '/dev/serial0' или '/dev/ttyS0'
    baudrate=9600,  # Скорость передачи (должна совпадать с отправителем)
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

try:
    print("Ожидание данных UART...")
    while True:
        if ser.in_waiting > 0:  # Если есть данные в буфере
            command = ser.readline().decode('utf-8').rstrip()  # Читаем строку
            print(f"Получена команда: {command}")
        time.sleep(0.1)  # Небольшая пауза для снижения нагрузки на CPU

except KeyboardInterrupt:
    print("Программа остановлена пользователем")
finally:
    ser.close()  # Всегда закрываем соединение при выходе