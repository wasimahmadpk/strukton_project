import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize
from raildefects_main import raildefects_main

class App(QWidget):

    def __init__(self):

        super().__init__()
        self.title = 'Rail Condition Monitoring System'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.fileName = 0
        self.initUI()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.browse_btn = QPushButton('Browse', self)
        self.browse_btn.clicked.connect(self.browseFile)
        self.browse_btn.resize(100, 32)
        self.browse_btn.move(50, 50)

        self.detect_btn = QPushButton('Detect', self)
        self.detect_btn.clicked.connect(self.detectAnomalies)
        self.detect_btn.resize(100, 32)
        self.detect_btn.move(200, 50)
        self.detect_btn.setVisible(False)

        # self.openFileNameDialog()
        # self.openFileNamesDialog()
        # self.saveFileDialog()
        self.show()

    def browseFile(self):
        self.openFileNameDialog()

    def detectAnomalies(self):
        obj = raildefects_main(1)
        anomaly_positions = obj.anomaly_detection(self.fileName)
        passage_1 = anomaly_positions[0]
        passage_2 = anomaly_positions[1]
        plt.figure(9)
        plt.plot(passage_1, 'r*')
        plt.plot(passage_2, 'g*')

    def openFileNameDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                          "All Files (*);;Python Files (*.py)", options=options)

        if fileName:
            print(fileName)
            self.fileName = fileName
            self.detect_btn.setVisible(True)
            # self.close()


    def openFileNamesDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                        "All Files (*);;Python Files (*.py)", options=options)

        if files:
            print(files)
            self.close()


    def saveFileDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                          "All Files (*);;Text Files (*.txt)", options=options)

        if fileName:
            print(fileName)
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())