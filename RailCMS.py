#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QDateTime, Qt, QTimer, QSize
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog, QMessageBox, QFormLayout, QDialogButtonBox)

import numpy as np
from raildefects_main import RailDefects


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.resize(1000, 750)
        self.fileName = 0
        self.output = np.array([])
        self.counter = 0
        self.initUI()

    def initUI(self):

        self.originalPalette = QApplication.palette()
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget(self.output)
        self.createBottomRightGroupBox()
        self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(0)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("RAIL CONDITION MONITORING SYSTEM")
        self.changeStyle('Fusion')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)


    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Pre-processing")

        radioButton1 = QRadioButton("Radio button 1")
        loadabaButton = QPushButton("Browse")
        loadsyncButton = QPushButton("Browse")
        loadsegButton = QPushButton("Browse")
        loadpoiButton = QPushButton("Browse")
        radioButton1.setChecked(True)

        checkBox = QCheckBox("Tri-state check box")
        checkBox.setTristate(True)
        checkBox.setCheckState(Qt.PartiallyChecked)

        loadabaButton.clicked.connect(self.browse_file)

        self.abaEdit = QLineEdit()
        self.abaEdit.setText("Load ABA file")
        self.abaEdit.setReadOnly(True)
        self.syncEdit = QLineEdit()
        self.syncEdit.setReadOnly(True)
        self.syncEdit.setText("Load SYNC file")
        self.segEdit = QLineEdit()
        self.segEdit.setText("Load SEG file")
        self.segEdit.setReadOnly(True)
        self.poiEdit = QLineEdit()
        self.poiEdit.setText("Load POI file")
        self.poiEdit.setReadOnly(True)

        pprocessButton = QPushButton("Start")
        pprocessButton.setStyleSheet("height: 15px;width: 24px;")
        pprocessButton.clicked.connect(self.browse_file)
        pprocessButton.setToolTip('Click to start pre-processing')

        layout = QFormLayout()
        layout.addRow(loadabaButton, self.abaEdit)
        layout.addRow(loadsyncButton, self.syncEdit)
        layout.addRow(loadsegButton, self.segEdit)
        layout.addRow(loadpoiButton, self.poiEdit)
        layout.addWidget(pprocessButton)

        self.topLeftGroupBox.setLayout(layout)


    def createTopRightGroupBox(self):

        self.topRightGroupBox = QGroupBox("Anomaly detection")

        loadpfileButton = QPushButton("Browse")
        loadpfileButton.clicked.connect(self.browse_file)

        self.processedEdit = QLineEdit()
        self.processedEdit.setText("Load pre-processed file")
        self.processedEdit.setReadOnly(True)

        fqbox = QComboBox()
        fqbox.addItems(['1', '2', '3', '4', '5', 'All'])

        swinsbox = QSpinBox()
        swinsbox.stepBy(1000)
        swinsbox.setMinimum(1000)
        swinsbox.setMaximum(6000)

        detectanomButton = QPushButton("Start")
        detectanomButton.setStyleSheet("height: 15px;width: 24px;")
        detectanomButton.clicked.connect(self.detect_anomalies)
        detectanomButton.setToolTip("Click to start anomaly detection")

        self.saveButton = QPushButton("Start")
        self.saveButton.setStyleSheet("height: 15px;width: 24px;")
        self.saveButton.clicked.connect(self.save_results)
        self.saveButton.setToolTip("Click to save the results")
        self.saveButton.setVisible(False)

        layout = QFormLayout()
        layout.addRow(loadpfileButton, self.processedEdit)
        layout.addRow(QLabel("No. of features:"), fqbox)
        layout.addRow(QLabel("Sliding window:"), swinsbox)
        layout.addWidget(detectanomButton)
        layout.addWidget(self.saveButton)

        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self, output):

        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        self.tableWidget = QTableWidget(100, 3)
        self.tableWidget.setHorizontalHeaderLabels(['Position(km)', 'Counter', 'Severity'])

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(3, 3, 3, 3)
        tab1hbox.addWidget(self.tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n" 
                              "Twinkle, twinkle, little star,\n" 
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomLeftTabWidget.addTab(tab1, "&Results")
        self.bottomLeftTabWidget.addTab(tab2, "Description")


    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Model parameters")
        self.bottomRightGroupBox.setCheckable(True)
        self.bottomRightGroupBox.setChecked(True)

        spinBox = QSpinBox(self.bottomRightGroupBox)
        spinBox.setValue(50)

        dateTimeEdit = QDateTimeEdit(self.bottomRightGroupBox)
        dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
        slider.setValue(40)
        slider.show()

        scrollBar = QScrollBar(Qt.Horizontal, self.bottomRightGroupBox)
        scrollBar.setValue(60)

        dial = QDial(self.bottomRightGroupBox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(spinBox, 0, 0, 1, 1)
        layout.addWidget(dateTimeEdit, 1, 0, 1, 1)
        layout.addWidget(slider, 2, 0)
        layout.addWidget(scrollBar, 3, 0)
        layout.addWidget(dial, 0, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

# ///////////////////// System functions /////////////////////////

    def openFileNameDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                          "All Files (*);;Python Files (*.py)", options=options)

        if fileName:
            if not str(fileName).endswith('.h5'):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("File Error")
                msg.setInformativeText('Please select the right file!')
                msg.setWindowTitle("Error")
                msg.exec_()
            else:
                print(fileName)
                self.fileName = fileName
                self.processedEdit.setText(str(fileName))
                # self.tableWidget.setItem(0, 1, QTableWidgetItem(str(123)))
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
            return fileName
            self.close()

    def detect_anomalies(self):

        obj = RailDefects(1)
        self.output = obj.anomaly_detection(self.fileName)
        loc = self.output[0, 0]
        cnt = self.output[0, 1]
        sev = self.output[0, 2]
        print("First Anomaly: ", loc, cnt, sev)
        # self.output = np.array([[2], [3], [5]])
        self.saveButton.setVisible(True)

        # Populate the table
        if len(self.output) > 0:
            for i in range(50):
                for j in range(3):
                    val = self.output[i, j]
                    print("Value:", val)
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

    def browse_file(self):

        self.openFileNameDialog()

    def save_results(self):

        savefile = self.saveFileDialog()
        obj = RailDefects(1)
        obj.save_output(self.output, savefile)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())