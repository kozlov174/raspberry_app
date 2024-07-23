import datetime
import sys
import pandas as pd
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic
import easygui
import openpyxl
import matplotlib.pyplot as plt


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open_button = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.calculate_button = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.file_name_display = self.findChild(QtWidgets.QTextBrowser, 'file_name')

        self.date.setText(str(datetime.date.today()))
        self.show()

        self.open_button.clicked.connect(self.showDialog)
        self.calculate_button.clicked.connect(self.doCalculation)
        self.input_file = None  # Инициализация переменной для пути к файлу

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
        time = 600
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
        I_apr = np.polyval(np.polyfit(Tizm[21:], I_t[21:], 4), Tizm)

        graph_1 = plt.plot(Tizm, R_meas, label='R_meas', linewidth=3)
        plt.plot(Tizm, R_apr, label='R_apr', linewidth=3)

        plt.show()

        graph = self.findChild(QtWidgets.QGraphicsView, 'graph')
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(graph_1)
        graph.setScene(graph_1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
