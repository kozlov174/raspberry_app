import datetime
import math
import sys
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic
import easygui
import openpyxl
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open_button = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.calculate_button = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.file_name_display = self.findChild(QtWidgets.QTextBrowser, 'file_name')

        self.graph = QtWidgets.QGridLayout(self.centralwidget)
        self.graphWidget.setBackground('w')

        self.date.setText(str(datetime.date.today()))
        self.show()

        self.open_button.clicked.connect(self.showDialog)
        self.calculate_button.clicked.connect(self.doCalculation)
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
            print(R_meas[i])

        I_t = np.array(Uizm) / np.array(R_meas)

        p = np.polyfit(Tizm, R_meas, 4)
        R_apr = np.polyval(p, Tizm)
        if time > 100:
            I_apr = np.polyval(np.polyfit(Tizm[21:], I_t[21:], 4), Tizm)


        self.graph.addWidget(self.graphWidget, 0, 0)
        self.graphWidget.clear()
        self.graphWidget.plot(Tizm, R_meas, pen = pg.mkPen(color='b', width=3), label='R_meas')
        self.graphWidget.plot(Tizm, R_apr, pen = pg.mkPen(color='k', width=3), label='R_apr', linewidth=3)

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
        #self.TPI.setText(str(TPI))
        self.Res.setText(str(round(Res, 3)))

        Kabs = R_apr[12]/R_apr[3]
        self.Kabs.setText(str(round(Kabs, 3)))
        DP = 200 * TPI ** 0.251
        self.DP.setText(str(round(DP, 3)))
        R15 = R_apr[3] / 10**9
        self.R15.setText(str(round(R15, 3)))
        R60 = R_apr[12] / 10 ** 9
        self.R60.setText(str(round(R60, 3)))
        if time > 100:
            I_ut = min(I_apr)
            I_spectr = (I_apr - I_ut) * time #особое внимание этой строчке



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
