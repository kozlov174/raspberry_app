import serial
import time


def start_com(port_name, baudrate=9600):
    try:
        # Открытие последовательного порта
        with serial.Serial(port_name, baudrate, timeout=1) as ser:
            time.sleep(1)  # Подождите, пока порт откроется
            print(f"Serial port {port_name} open")

            commands = [
                "40526E0D0A",
                "4055660D0A",
                "49640D0A",
                "4054720D0A",
                "45723030300D0A",
                "45723030310D0A",
                "45723030320D0A",
                "40547332342E30382E31342031323A35330D0A",
                "54720D0A",
                "404045723030300D0A",
                "457730303030453033334233433033314530303343303235383032353830303041303030410D0A",
                "404045723030300D0A",
                "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                "404045723030300D0A",
                "457730303030453033334233433033314530303343303235383030336330303035303030410D0A",
                "4466666666660D0A",
                "467332310D0A"
                "42640D0A"
            ]

            # Отправка команд
            for cmd in commands:
                hex_cmd = bytes.fromhex(cmd)
                print(f"Sending command: {cmd}")
                ser.write(hex_cmd)
                ser.flush()# Убедитесь, что данные записаны в порт
                output = ser.read_all()
                print(f"Received output: {output}")
                time.sleep(3)  # Пауза между командами (если необходимо)

            print("All commands sent")

            # Чтение данных после отправки команд
            print("Reading data from serial port...")
            time.sleep(2)  # Дайте время устройству для отправки данных
            response = read_from_serial(ser)

            if response:
                print("Received data:\n" + response)
            else:
                print("No data received.")

            ser.close()
            print("Serial port closed")
            read_from_serial("COM4")

    except serial.SerialException as e:
        print(f"Error: {e}")


def read_from_serial(portname):
    ser = serial.Serial(portname, baudrate = 9600, timeout=1)
    output = []
    while True:
        data = ser.read_all() # Чтение до 1024 байт за раз
        if not data:
            break
        output.append(data.decode(errors='ignore'))  # Игнорирование ошибок декодирования
    return ''.join(output)


if __name__ == "__main__":
    port_name = 'COM4'  # Замените на ваш последовательный порт (например, 'COM3' для Windows или '/dev/ttyS0' для Linux)
    start_com(port_name)
