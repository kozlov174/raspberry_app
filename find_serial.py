import serial.tools.list_ports


def list_serial_ports():
    """Выводит список всех доступных последовательных портов"""
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("Не найдено ни одного последовательного порта!")
        return

    print("Доступные последовательные порты:")
    for port in ports:
        print(f"Порт: {port.device}")
        print(f"  Описание: {port.description}")
        print(f"  Производитель: {port.manufacturer}")
        print(f"  HWID: {port.hwid}")
        print("-" * 40)


if __name__ == "__main__":
    list_serial_ports()