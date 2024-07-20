import datetime
import sys
import pandas as pd
import numpy as np
import xlrd
from PyQt5 import QtCore, QtWidgets, uic
import easygui
import openpyxl


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

        print(I_test, C_test)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
