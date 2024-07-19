import datetime

from PyQt5 import QtCore, QtWidgets, uic
import sys
import easygui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.calculate = self.findChild(QtWidgets.QPushButton, 'save_button')
        self.date.setText(str(datetime.date.today()))
        self.show()
        self.open.clicked.connect(self.showDialog)
        self.calculate.clicked.connect(self.doCalculation)

    def showDialog(self):
        input_file = easygui.fileopenbox(filetypes=["*.docx"])
        self.file = self.findChild(QtWidgets.QTextBrowser, 'file_name')
        self.file.setPlainText(input_file)

    def doCalculation(self):
        if self.file.toPlainText() != None:
            print(input_file)
            self.table = f.open(self.file)
        else:
            print("Error")
        print(300)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()
