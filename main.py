import datetime

from PyQt5 import QtCore, QtWidgets, uic
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('Main.ui', self)
        self.date = self.findChild(QtWidgets.QTextBrowser, 'date')
        self.open = self.findChild(QtWidgets.QPushButton, 'open_button')
        self.date.setText(str(datetime.date.today()))
        self.show()
        self.open.clicked.connect(self.showDialog)
    def showDialog(self):
        options = QFileDialog.Options()
        options = QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Выбрать файл", "", "Все файлы (*);;Python файлы (*.py)", options=options)
        if fileName:
            print(f'Выбранный файл: {fileName}')

    def openFile(self):
        print("test")
        options = QFileDialog.Options()
        options = QFileDialog.ReadOnly
        self.file = QFileDialog.getOpenFileName(self, "Open File", options=options)
        self.filename = self.findChild(QtWidgets.QTextBrowser, 'file_name')
        self.filename.setText(str(self.file[0]))
        #func for open file

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exec_()
