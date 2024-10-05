import datetime
import math
import re
import sys
import asyncio
from time import sleep

import serial
import RPi.GPIO as GPIO
from PyQt5.QtCore import QIODevice, QThread, pyqtSignal, QTimer
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic, QtSerialPort
import easygui
import openpyxl
import pyqtgraph as pg
import subprocess
import time

from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLabel


class MainWindow(QtWidgets.QMainWindow):
    update_status_signal = QtCore.pyqtSignal(str)
    def __init__(self):

        super(MainWindow, self).__init__()
        self.position_v = None
        uic.loadUi('main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open_button = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.file_name_display = self.findChild(QtWidgets.QTextBrowser, 'file_name')
        self.open_settings = self.findChild(QtWidgets.QPushButton, 'open_settings')
        self.keyboard = self.findChild(QtWidgets.QPushButton, 'keyboard_button')
        self.sheetName = self.findChild(QtWidgets.QPlainTextEdit, 'sheet_name')
        self.calculate = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.saveSheetButton = self.findChild(QtWidgets.QPushButton, 'save_button_2')
        self.time_izm = self.findChild(QtWidgets.QComboBox, 'time_izm')
        self.status = self.findChild(QtWidgets.QTextBrowser, 'status')
        self.position_V = 500
        self.R_itog_array = []

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        try:
            GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
            GPIO.setup(16, GPIO.IN, GPIO.PUD_UP)
            GPIO.setup(20, GPIO.IN, GPIO.PUD_UP)
            GPIO.setup(21, GPIO.IN, GPIO.PUD_UP)
        except Exception as e:
            print(f"Error setting up GPIO: {e}")
        if GPIO.input(16) == 0:
            self.position_V = 500
            print("500В")
        if GPIO.input(20) == 0:
            self.position_V = 1000
            print("1000В")
        if GPIO.input(21) == 0:
            self.position_V = 2500
            print("2500В")
        self.graphWidget = self.findChild(pg.PlotWidget, 'graphWidget')  # Ensure this is initialized
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabel('left', 'Сопротивление, Ом', **{'font-size': '20pt'})
        self.graphWidget.setLabel('bottom', 'Время, сек', **{'font-size': '20pt'})
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.getAxis('left').setPen(pg.mkPen(color='k'))
        self.graphWidget.getAxis('bottom').setPen(pg.mkPen(color='k'))
        self.graphWidget.getAxis('left').setTextPen('k')
        self.graphWidget.getAxis('bottom').setTextPen('k')
        legend = self.graphWidget.addLegend(offset=(400, 300))
        legend.labelTextColor = pg.mkColor('k')

        self.basic_flag = 0
        self.position_v = self.findChild(QtWidgets.QTextBrowser, 'position_V')
        self.position_v.setText(str(self.position_V))
        self.date.setText(str(datetime.date.today()))

        self.open_button.clicked.connect(self.showDialog)
        self.calculate.clicked.connect(self.doCalculation)
        self.input_file = None  # Инициализация переменной для пути к файлу
        self.saveSheetButton.clicked.connect(self.saveSheet)
        self.open_settings.clicked.connect(self.open_window_settings)
        self.update_status_signal.connect(self.update_status)

        self.R15 = self.findChild(QtWidgets.QTextBrowser, 'R15')
        self.R60 = self.findChild(QtWidgets.QTextBrowser, 'R60')
        self.Kabs = self.findChild(QtWidgets.QTextBrowser, 'Kabs')
        self.PI = self.findChild(QtWidgets.QTextBrowser, 'PI')
        self.DAR = self.findChild(QtWidgets.QTextBrowser, 'DAR')
        self.DD = self.findChild(QtWidgets.QTextBrowser, 'DD')
        self.W = self.findChild(QtWidgets.QTextBrowser, 'W')
        self.DP = self.findChild(QtWidgets.QTextBrowser, 'DP')
        self.Res = self.findChild(QtWidgets.QTextBrowser, 'Res')
        self.C = 0
        self.I = 0

        # Start the touch button coroutine
        self.loop = asyncio.get_event_loop()

        # Используем QTimer для запуска асинхронных задач
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_async_tasks)
        self.timer.start(100)  # Проверяем каждые 100 мс

        self.show()

    def update_status(self, message):
        # Метод для обновления текста в QTextBrowser
        self.status.append(message)

    def open_window_settings(self):
        try:
            self.second_window = SettingsWindow()
            self.second_window.show()
        except Exception as e:
            print(f"Ошибка при открытии окна настроек {e}")

    def run_async_tasks(self):
        self.loop.run_until_complete(self.touch_button())

    async def touch_button(self):

        if GPIO.input(5) == 0:
            await self.start_com()

    def convert_farads(self, value):
        units = [
            (1e-12, 'pФ)'),
            (1e-9, 'nФ'),
            (1e-6, 'µФ'),
            (1e-3, 'mФ'),
            (1, 'фарад (Ф)')
        ]

        for factor, unit in units:
            if value >= factor:
                converted_value = value / factor
                return f"{converted_value:.12g} {unit}"

        return f"{value} фарад (Ф)"

    def convert_amperes(self, value):
        units = [
            (1e-12, 'pА'),
            (1e-9, 'nА'),
            (1e-6, 'µА'),
            (1e-3, 'mА'),
            (1, 'А')
        ]

        for factor, unit in units:
            if value >= factor:
                converted_value = value / factor
                return f"{converted_value:.12g} {unit}"

        return f"{value} ампер (А)"

    def showDialog(self):
        self.input_file = easygui.fileopenbox()
        if self.input_file:  # Если файл был выбран
            self.file_name_display.setPlainText(self.input_file)
        else:
            self.file_name_display.setPlainText("No file selected")

    def showKeyboard(self):
        print("click button")
        subprocess.run(['florence'])

    def doCalculation(self):
        book = openpyxl.load_workbook(filename=self.input_file)
        sheet = book['Лист1']
        U_test = sheet['J2'].value  # считываем значение тестового напряжения из ячейки U(Volt)
        DAR_test = sheet['K2'].value  # считываем параметр DAR
        PI_test = sheet['L2'].value  # считываем параметр PI
        DD_test = sheet['O2'].value  # считываем параметр DD

        Tg = 45  # Время жизни трансформатора - Константа в годах

        I = sheet['N2'].value
        n = len(I)
        I_test = float(I[:n - 3])
        data = {
            'Unit': ['p', 'n', 'µ', 'm', ' ', 'k', 'M', 'G', 'T'],
            'Value': [0.000000000001, 0.000000001, 0.000001, 0.001, 1, 1000, 1000000, 1000000000, 1000000000000]
        }
        Razmernost = pd.DataFrame(data)
        unit = I[n - 2]  # Символ, который нужно найти в таблице
        unit_index = Razmernost[Razmernost['Unit'] == unit].index
        value = Razmernost.loc[unit_index[0], 'Value']
        I_test = float(I[:n - 3]) * value

        Cap = sheet['M2'].value
        n = len(Cap)
        C_test = float(Cap[:n - 3])
        unit = Cap[n - 2]  # Символ, который нужно найти в таблице
        unit_index = Razmernost[Razmernost['Unit'] == unit].index
        value = Razmernost.loc[unit_index[0], 'Value']
        C_test = float(Cap[:n - 3]) * value

        # self.time = self.findChild(QtWidgets.QSpinBox, 'time')
        time = 600
        Tizm = []
        Uizm = []
        R_meas = []

        for i in range(time // 5 + 1):
            Tizm.append(int(sheet['R' + str(i + 2)].value))
            Uizm.append(int(sheet['S' + str(i + 2)].value))
            R_meas.append(int(sheet['T' + str(i + 2)].value) * 10 ** 6)

        I_t = np.array(Uizm) / np.array(R_meas)

        p = np.polyfit(Tizm, R_meas, 4)
        R_apr = np.polyval(p, Tizm)
        if time > 100:
            I_apr = np.polyval(np.polyfit(Tizm[21:], I_t[21:], 4), Tizm)

        self.graphWidget.clear()
        self.graphWidget.plot(Tizm, R_meas, pen=pg.mkPen(color='b', width=3), name='R измеренное ')
        self.graphWidget.plot(Tizm, R_apr, pen=pg.mkPen(color='k', width=3), name='R апроксимированное')

        DAR = R_apr[12] / R_apr[6]
        self.DAR.setText(str(round(DAR, 3)))
        if (time // 5 + 1 < 121):
            PI = 0
            DD = 0
        else:
            PI = R_apr[120] / R_apr[12]
            DD = 1000 * (R_apr[120] - R_apr[10]) / (R_apr[12] * R_apr[120] * C_test)

        self.PI.setText(str(round(PI, 3)))
        self.DD.setText(str(round(DD, 3)))

        if PI == 0:
            W = 0
            TPI = 0
            Res = 0
        else:
            W = 3.275 - 4.819 * math.log10(PI)
            TPI = 59.029 * PI - 56.391
            Res = (70 - Tg) * ((TPI / 3) ** 0.251 - 1)

        self.W.setText(str(round(W, 3)))
        self.Res.setText(str(math.trunc(Res)))

        Kabs = R_apr[12] / R_apr[3]
        self.Kabs.setText(str(round(Kabs, 3)))
        DP = 200 * TPI ** 0.251
        self.DP.setText(str(math.trunc(DP)))
        R15 = R_apr[3] / 10 ** 9
        self.R15.setText(str(round(R15, 3)))
        R60 = R_apr[12] / 10 ** 9
        self.R60.setText(str(round(R60, 3)))
        if time > 100:
            I_ut = min(I_apr)
            I_spectr = (I_apr - I_ut) * time  # особое внимание этой строчке

    def saveSheet(self):
        sheet = openpyxl.Workbook()
        book = sheet['Sheet']

        # присваивание статических значений первой строки
        book['A1'].value = "Obj:Tst"
        book['B1'].value = "Description"
        book['C1'].value = "Location"
        book['D1'].value = "Date"
        book['E1'].value = "Time"
        book['F1'].value = "Function"
        book['G1'].value = "R"

        book['H1'].value = "Unit"
        book['I1'].value = "R (T° corrected)"
        book['J1'].value = "U (Volt)"
        book['J2'].value = self.position_V
        book['K1'].value = "DAR"
        book['K2'].value = self.DAR.toPlainText()
        book['L1'].value = "PI"
        book['L2'].value = self.PI.toPlainText()
        book['M1'].value = "C"
        book['M2'].value = int(self.C)
        book['N1'].value = "I"
        book['N2'].value = int(self.I)

        book['O1'].value = "DD"
        book["O2"].value = self.DD.toPlainText()
        book['P1'].value = "Comments"
        book['Q1'].value = "Next Test"
        book['R1'].value = "Time"
        book['S1'].value = "U (Volt)"
        book['T1'].value = "R (MOhm)"
        book['U1'].value = "R (MOhm)T° corrected:40C"

        R_izm = self.R_itog_array

        # присваивание динамических значений второй и последующих строк
        time = int(self.time_izm.currentText()) * 60
        book['D2'].value = datetime.datetime.now().strftime('%d-%m-%Y')
        book['E2'].value = datetime.datetime.now().strftime('%H:%M:%S')

        default_position = 0
        default_time_position = 0
        # заполнение ячеек со значениями
        for i in range(2, len(R_izm) + 1):
            column = "R" + str(i)
            book[column].value = default_time_position
            column = "S" + str(i)
            book[column].value = self.position_V
            column = "T" + str(i)
            book[column].value = R_izm[default_position] // 1000000
            column = "U" + str(i)
            book[column].value = R_izm[default_position]
            default_position = default_position + 1
            default_time_position = default_time_position + 5

        book = sheet.create_sheet('Метаданные')
        with open("./metadata.txt", "r") as file:
            content = file.readlines()
            upd_cont = content[0].split(":")
            book['A1'] = upd_cont[0]
            book['A2'] = upd_cont[1]
            upd_cont = content[1].split(":")
            book['B1'] = upd_cont[0]
            book['B2'] = upd_cont[1]
            upd_cont = content[2].split(":")
            book['C1'] = upd_cont[0]
            book['C2'] = upd_cont[1]
            upd_cont = content[3].split(":")
            book['D1'] = upd_cont[0]
            book['D2'] = upd_cont[1]
            sheet_name = str(book['A2'].value) + " " + str(book['C2'].value) + " " + str(book['D2'].value)
        sheet.save(sheet_name + ".xlsx")
        sheet.close()

    async def start_com(self):
        try:

            port_name = "COM4"
            # Открытие последовательного порта
            with serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1) as ser:
                time.sleep(1)  # Подождите, пока порт откроется
                print(f"Serial port {port_name} open")
                time_izm = int(self.time_izm.currentText())
                self.update_status_signal.emit("Выполняется отправка команд")
                self.update()
                start_commands = [
                    "40526E0D0A",
                    "4055660D0A",
                    "49640D0A",
                    "4054720D0A",
                    "45723030300D0A",
                    "45723030310D0A",
                    "45723030320D0A",
                    "40547332342E30382E31342031323A35330D0A",
                    "54720D0A"
                ]
                if self.basic_flag == 0:
                    for cmd in start_commands:
                        hex_cmd = bytes.fromhex(cmd)
                        print(f"Sending command: {cmd}")
                        ser.write(hex_cmd)
                        ser.flush()  # Убедитесь, что данные записаны в порт
                        output = ser.readline()
                        print(f"Received output: {output}")
                        time.sleep(1)  # Пауза между командами (если необходимо)
                    self.basic_flag = 1
                commands = []
                if self.position_V == 500 and time_izm == 1:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303041303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383030343630303035303030410D0A",
                        "4466666666660D0A",
                        "467332310D0A",
                        "42640D0A"
                    ]
                elif self.position_V == 1000 and time_izm == 1:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303041303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383030343630303035303030410D0A",
                        "4466666666660D0A",
                        "467332320D0A",
                        "42640D0A"
                    ]
                elif self.position_V == 2500 and time_izm == 1:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303041303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383030343630303035303030410D0A",
                        "4466666666660D0A",
                        "467332330D0A",
                        "42640D0A"
                    ]
                elif self.position_V == 500 and time_izm == 10:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032363230303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "4466666666660D0A",
                        "467332310D0A",
                        "42640D0A"
                    ]
                elif self.position_V == 1000 and time_izm == 10:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032363230303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "4466666666660D0A",
                        "467332320D0A",
                        "42640D0A"
                    ]
                elif self.position_V == 2500 and time_izm == 10:
                    commands = [
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032363230303035303030410D0A",
                        "404045723030300D0A",
                        "457730303030453033334233433033314530303343303235383032353830303035303030410D0A",
                        "4466666666660D0A",
                        "467332330D0A",
                        "42640D0A"
                    ]
                # Отправка команд
                for cmd in commands:
                    hex_cmd = bytes.fromhex(cmd)
                    print(f"Sending command: {cmd}")
                    ser.write(hex_cmd)
                    ser.flush()  # Убедитесь, что данные записаны в порт
                    output = ser.readline().decode("utf-8")
                    while "EC" in output:
                        time.sleep(1)
                        ser.write(hex_cmd)
                        time.sleep(1)
                        output = ser.readline().decode("utf-8")
                    print(f"Received output: {output}")
                    time.sleep(3)  # Пауза между командами (если необходимо)

                # Чтение данных после отправки команд
                print("Reading data from serial port...")
                time.sleep(2)  # Дайте время устройству для отправки данных
                time_array = []
                R_array = []
                for i in range(time_izm * 60 + 5):
                    self.update_status_signal.emit("Идёт измерение. Осталось: " + str(time_izm * 60 + 5 - i) + " секунд")
                    self.update()
                    time.sleep(1)
                end_output = ""
                while len(end_output) < 50:
                    ser.write(bytes.fromhex("4044700D0A"))
                    sleep(2)
                    end_output = ser.readline()
                    print(end_output)
                sleep(1)
                time_array = []
                volt_array = []
                R_array = []
                base_index = 2
                decoded_output = end_output.decode("utf-8")
                end_array = decoded_output.split(";")
                print('Array length' + " " + str(len(end_array)))
                for i in range(0, time_izm * 60, 5):
                    volt_array.append(int(self.position_V))
                    time_array.append(i)
                    R = end_array[base_index].split("E")
                    if i == time_izm * 60:
                        R[0] = R[0][1:]
                        itogR = float(R[0]) * 10 ** int(R[1][:-4])
                    else:
                        R[0] = R[0][1:]
                        itogR = float(R[0]) * 10 ** int(R[1])
                    R_array.append(itogR)
                    base_index += 2
                print(R_array)
                self.R_itog_array = R_array
                print(R_array)

                print("считывание финального измерения")
                ser.write(bytes.fromhex("44670D0A"))
                sleep(2)
                output = ser.readline()
                print(f"Received output: {output}")
                output = output.decode("utf-8")
                result_array = output.split(";")
                C = result_array[12].split("E")
                C[0] = C[0][1:]
                C_itog = float(C[0]) * 10 ** int(C[1])
                self.C = C_itog
                I = result_array[8].split("E")
                I[0] = I[0][1:]
                I_itog = float(I[0]) * 10 ** int(I[1])
                self.I = I_itog
                # ток в степени -8(элемент 8)
                ser.close()
                time_array.pop(1)
                time_array.pop(0)
                volt_array.pop(0)
                volt_array.pop(1)
                R_array.pop(1)
                R_array.pop(0)
                p = np.polyfit(time_array, R_array, 4)
                R_apr = np.polyval(p, time_array)
                self.graphWidget.plot(time_array, R_array, pen=pg.mkPen(color='b', width=3), name='R измеренное')
                self.graphWidget.plot(time_array, R_apr, pen=pg.mkPen(color='k', width=3), name='R апроксимированное')
                self.calculate_itog(time_array, volt_array, R_array)

                with open("./metadata.txt", "r") as file:
                    lines = file.readlines()

                for i, line in enumerate(lines):
                    if line.startswith('Номер измерения:'):
                        # Извлекаем текущее значение, увеличиваем его на 1 и обновляем строку
                        current_value = int(line.split(': ')[1])
                        new_value = current_value + 1
                        lines[i] = f'Номер измерения: {new_value}\n'
                        break

                with open("./metadata.txt", "w") as file:
                    file.writelines(lines)

                self.status.setText("Serial port closed")
        except serial.SerialException as e:
            print(f"Error: {e}")

    def calculate_itog(self, Tizm, Uizm, R_meas):
        I_t = np.array(Uizm) / np.array(R_meas)

        p = np.polyfit(Tizm, R_meas, 4)
        R_apr = np.polyval(p, Tizm)
        if int(self.time_izm.currentText()) * 60 > 100:
            I_apr = np.polyval(np.polyfit(Tizm[21:], I_t[21:], 4), Tizm)

        if len(R_apr) > 12:
            DAR = R_apr[11] / R_apr[5]
        else:
            DAR = 0
        self.DAR.setText(str(round(DAR, 3)))
        if (int(self.time_izm.currentText()) * 60 // 5 + 1 < 121):
            PI = 0
            DD = 0
        else:
            PI = R_apr[117] / R_apr[9]
            DD = 1000 * (R_apr[117] - R_apr[7]) / (R_apr[9] * R_apr[117] * self.C)

        self.PI.setText(str(round(PI, 3)))
        self.DD.setText(str(round(DD, 3)))

        if PI == 0:
            W = 0
            TPI = 0
            Res = 0
        else:
            W = 3.275 - 4.819 * math.log10(PI)
            TPI = 59.029 * PI - 56.391
            Res = (70 - 45) * ((TPI / 3) ** 0.251 - 1)

        self.W.setText(str(round(W, 3)))
        self.Res.setText(str(math.trunc(Res)))

        Kabs = R_apr[9] / R_apr[1]
        self.Kabs.setText(str(round(Kabs, 3)))
        DP = 200 * TPI ** 0.251
        self.DP.setText(str(math.trunc(DP)))
        R15 = R_meas[1] / 10 ** 9
        self.R15.setText(str(round(R15, 3)))
        R60 = R_meas[9] / 10 ** 9
        self.R60.setText(str(round(R60, 3)))
        if time > 100:
            I_ut = min(I_apr)
            I_spectr = (I_apr - I_ut) * time  # особое внимание этой строчке


class SettingsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        uic.loadUi('secondUI.ui', self)

        self.keyboard = self.findChild(QtWidgets.QPushButton, 'keyboard_button')
        self.name_obj = self.findChild(QtWidgets.QTextEdit, 'name_obj')
        self.location = self.findChild(QtWidgets.QTextEdit, 'location_obj')
        self.date = self.findChild(QtWidgets.QTextEdit, 'date')
        self.operator = self.findChild(QtWidgets.QTextEdit, 'operator_2')
        self.save_button = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.number_measurment = self.findChild(QtWidgets.QTextEdit, 'number_measurment')

        self.keyboard.clicked.connect(self.showKeyboard)
        self.save_button.clicked.connect(self.saveSettings)

        with open("./metadata.txt", "r") as file:
            content = file.readlines()
            upd_cont = content[0].split(":")
            self.name_obj.setText(upd_cont[1])
            upd_cont = content[1].split(":")
            self.location.setText(upd_cont[1])
            self.date.setText(str(datetime.date.today()))
            upd_cont = content[3].split(":")
            self.operator.setText(upd_cont[1])
            upd_cont = content[4].split(":")
            self.number_measurment.setText(upd_cont[1])

    def saveSettings(self):
        with open("./metadata.txt", "r") as file:
            content = file.readlines()

        updated_content = []

        # Наименование объекта измерения
        upd_cont = content[0].split(":", 1)
        upd_cont[1] = " " + self.name_obj.toPlainText()
        updated_content.append(":".join(upd_cont))

        # Место расположения объекта измерения
        upd_cont = content[1].split(":", 1)
        upd_cont[1] = " " + self.location.toPlainText()
        updated_content.append(":".join(upd_cont))

        # Дата измерения
        upd_cont = content[2].split(":", 1)
        upd_cont[1] = " " + datetime.date.today().strftime("%d.%m.%y") + "\n"
        updated_content.append(":".join(upd_cont))

        # Оператор
        upd_cont = content[3].split(":", 1)
        upd_cont[1] = " " + self.operator.toPlainText()
        updated_content.append(":".join(upd_cont))

        # номер измерения
        upd_cont = content[4].split(":", 1)
        upd_cont[1] = " " + self.number_measurment.toPlainText()
        updated_content.append(":".join(upd_cont))

        with open("./metadata.txt", "w") as file:
            file.writelines(updated_content)

    def showKeyboard(self):
        print("click button")
        subprocess.run(['florence'])



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
