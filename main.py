import datetime
import math
import sys
import time
import serial
import gpiozero as gpio
from PyQt5.QtCore import QIODevice
from gpiozero import Button

import testconn
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic, QtSerialPort
import easygui
import openpyxl
import pyqtgraph as pg
import subprocess
from collections import deque


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open_button = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.calculate_button = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.file_name_display = self.findChild(QtWidgets.QTextBrowser, 'file_name')
        self.keyboard = self.findChild(QtWidgets.QPushButton, 'keyboard_button')
        self.sheetName = self.findChild(QtWidgets.QPlainTextEdit, 'sheet_name')
        self.saveSheetButton = self.findChild(QtWidgets.QPushButton, 'save_button_2')
        self.sendCOM = self.findChild(QtWidgets.QPushButton, 'send_COM')

        self.serial_port = QtSerialPort.QSerialPort("COM4")
        self.serial_port.setBaudRate(9600)
        self.serial_port.open(QtCore.QIODevice.ReadWrite)

        self.graph = QtWidgets.QGridLayout(self.centralwidget)
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

        #start_button = Button(указать пин гпио)

        self.date.setText(str(datetime.date.today()))
        self.show()

        #if (start_button.is_pressed):
            #self.start_measurement()
        self.open_button.clicked.connect(self.showDialog)
        self.calculate_button.clicked.connect(self.doCalculation)
        self.keyboard.clicked.connect(self.showKeyboard)
        self.saveSheetButton.clicked.connect(self.saveSheet)
        self.sendCOM.clicked.connect(self.start_com)
        self.serial_port.readyRead.connect(self.read_from_serial)

        self.input_file = None  # Инициализация переменной для пути к файлу

        self.R15 = self.findChild(QtWidgets.QTextBrowser, 'R15')
        self.R60 = self.findChild(QtWidgets.QTextBrowser, 'R60')
        self.Kabs = self.findChild(QtWidgets.QTextBrowser, 'Kabs')
        self.PI = self.findChild(QtWidgets.QTextBrowser, 'PI')
        self.DAR = self.findChild(QtWidgets.QTextBrowser, 'DAR')
        self.DD = self.findChild(QtWidgets.QTextBrowser, 'DD')
        self.W = self.findChild(QtWidgets.QTextBrowser, 'W')
        self.DP = self.findChild(QtWidgets.QTextBrowser, 'DP')
        self.Res = self.findChild(QtWidgets.QTextBrowser, 'Res')


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

        self.time = self.findChild(QtWidgets.QSpinBox, 'time')
        time = int(self.time.value())
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


        self.graph.addWidget(self.graphWidget, 0, 0)
        self.graphWidget.clear()
        self.graphWidget.plot(Tizm, R_meas, pen = pg.mkPen(color='b', width=3), name='R измеренное ')
        self.graphWidget.plot(Tizm, R_apr, pen = pg.mkPen(color='k', width=3), name='R апроксимированное')

        DAR=R_apr[12]/R_apr[6]
        self.DAR.setText(str(round(DAR, 3)))
        if (time // 5 + 1 < 121):
            PI = 0
            DD = 0
        else:
            PI = R_apr[120]/R_apr[12]
            DD = 1000 * (R_apr[120] - R_apr[10]) / (R_apr[12]*R_apr[120]*C_test)

        self.PI.setText(str(round(PI, 3)))
        self.DD.setText(str(round(DD, 3)))

        if PI == 0:
            W = 0
            TPI = 0
            Res = 0
        else:
            W = 3.275 - 4.819*math.log10(PI)
            TPI = 59.029*PI-56.391
            Res = (70 - Tg) * ((TPI / 3) ** 0.251 - 1)

        self.W.setText(str(round(W, 3)))
        self.Res.setText(str(math.trunc(Res)))

        Kabs = R_apr[12]/R_apr[3]
        self.Kabs.setText(str(round(Kabs, 3)))
        DP = 200 * TPI ** 0.251
        self.DP.setText(str(math.trunc(DP)))
        R15 = R_apr[3] / 10**9
        self.R15.setText(str(round(R15, 3)))
        R60 = R_apr[12] / 10 ** 9
        self.R60.setText(str(round(R60, 3)))
        if time > 100:
            I_ut = min(I_apr)
            I_spectr = (I_apr - I_ut) * time #особое внимание этой строчке

    def saveSheet(self):
        print(self.sheetName.toPlainText())
        sheet = openpyxl.Workbook()
        book = sheet['Sheet']
        report = openpyxl.load_workbook(filename=self.input_file)
        report_sheet = report['Лист1']

        #присваивание статических значений первой строки
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
        book['K1'].value = "DAR"
        book['L1'].value = "PI"
        book['M1'].value = "C"
        book['N1'].value = "I"
        book['O1'].value = "DD"
        book['P1'].value = "Comments"
        book['Q1'].value = "Next Test"
        book['R1'].value = "Time"
        book['S1'].value = "U (Volt)"
        book['T1'].value = "R (MOhm)"
        book['U1'].value = "R (MOhm)T° corrected:40C"


        #присваивание динамических значений второй и последующих строк
        time = self.time.value()
        book['D2'].value = datetime.datetime.now().strftime('%d-%m-%Y')
        book['E2'].value = datetime.datetime.now().strftime('%H:%M:%S')

        #заполнение ячеек со значениями
        for i in range(2, time // 5 + 3):
            column = "R" + str(i)
            book[column].value = 5 * (i-2)
            column = "S" + str(i)
            book[column].value = report_sheet[column].value
            column = "T" + str(i)
            book[column].value = report_sheet[column].value
            column = "U" + str(i)
            book[column].value = int(report_sheet["T" + str(i)].value) / 4



        if (self.sheetName.toPlainText() == ""):
            sheet.save(("new_sheet.xlsx"))
        else:
            sheet.save((self.sheetName.toPlainText() + ".xlsx"))
        sheet.close()

    def measure_real_numbers(self):
        time = int(self.time.value())
        self.time_array = deque(time // 5 + 1)
        self.U_array = deque(time // 5 + 1)
        self.R_array = deque(time // 5 + 1)
        self.R_corr_array = deque(time // 5 + 1)

        for i in range(time // 5 + 1):
            #добавление значений в массив данных с прибора
            self.time_array.append(i * 5)
            self.U_array.append()
            self.R_array.append()
            self.R_corr_array.append()

            #live построение графика на основе данных
            self.graphWidget.clear()
            self.graphWidget.plot(self.time_array, self.R_array, pen=pg.mkPen(color='b', width=3), name='R измеренное ')
            p = np.polyfit(Tizm, R_meas, 4)
            R_apr = np.polyval(p, self.time_array)
            self.graphWidget.plot(self.time_array, R_apr, pen=pg.mkPen(color='b', width=3), name='R измеренное ')

            #рассчёт показателей PI и DAR на основе измерений
            PI = R_apr[120]/R_apr[12]
            DAR = R_apr[12]/R_apr[6]

    # def start_measurement(self):
    #
    #     position500 = Button(17)
    #     position1000 = Button(27)
    #
    #     self.serial_port.write(bytes.fromhex("40 52 6E 0D 0A"))
    #     self.serial_port.write(bytes.fromhex("40 55 66 0D 0A"))
    #     self.serial_port.write(bytes.fromhex("49 64 0D 0A"))
    #     self.serial_port.write(bytes.fromhex("40 54 72 0D 0A"))
    #     self.serial_port.write(bytes.fromhex("45 72 30 30 30 0D 0A"))
    #     self.serial_port.write(bytes.fromhex("457730303030453033334233433033314530303343303235383032353830303041303030410D0A"))
    #     if position500.is_pressed: #1000В
    #         self.serial_port.write(bytes.fromhex("467332310D0A"))
    #     elif position1000.is_active: #2000В
    #         self.serial_port.write(bytes.fromhex("467332320D0A"))
    #     else: #2500В
    #         self.serial_port.write(bytes.fromhex("467332330D0A"))
    #     for i in range(0, 600, 5):
    #         #отрисовка графика в моменте
    #         print("write plot")

    def start_com(self):
        try:
            # Открытие последовательного порта
                time.sleep(1)  # Подождите, пока порт откроется
                print(f"Serial port open")

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
                    self.serial_port.write(hex_cmd)
                    self.serial_port.flush()  # Убедитесь, что данные записаны в порт
                    time.sleep(3)  # Пауза между командами (если необходимо)

                print("All commands sent")

                # Чтение данных после отправки команд
                print("Reading data from serial port...")
                time.sleep(2)  # Дайте время устройству для отправки данных

                print("Serial port closed")

        except serial.SerialException as e:
            print(f"Error: {e}")

    def read_from_serial(self):
        time.sleep(1)
        self.serial_port.write(bytes.fromhex("44670D0A"))
        output = self.serial_port.read(1024)
        upd_output = output.decode("utf-8")
        print(output.decode("utf-8"))
        print(len(upd_output)) #default от 38



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
