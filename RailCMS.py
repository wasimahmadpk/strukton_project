#!/usr/bin/env python
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import QDateTime, Qt, QTimer, QSize
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog, QMessageBox, QFormLayout, QDialogButtonBox)

import numpy as np
import csv
from raildefects_main import RailDefects
from data_processing import pre_processing


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.resize(1000, 750)
        self.fileName = None
        self.ppfile = None
        self.abafile = None
        self.syncfile = None
        self.segfile = None
        self.poifile = None
        self.key = None
        self.ppdata = 0.0
        self.output = np.array([])
        self.counter = 0
        self.initUI()

    def initUI(self):

        self.setWindowIcon(QIcon('srail.jpg'))
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
        # self.createProgressBar()

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
        # mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
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

        loadabaButton.clicked.connect(self.browse_aba)
        loadsyncButton.clicked.connect(self.browse_sync)
        loadsegButton.clicked.connect(self.browse_seg)
        loadpoiButton.clicked.connect(self.browse_poi)

        self.abaEdit = QLineEdit()
        self.abaEdit.setText("ABA file")
        self.abaEdit.setReadOnly(True)
        self.syncEdit = QLineEdit()
        self.syncEdit.setReadOnly(True)
        self.syncEdit.setText("SYNC file")
        self.segEdit = QLineEdit()
        self.segEdit.setText("SEG file")
        self.segEdit.setReadOnly(True)
        self.poiEdit = QLineEdit()
        self.poiEdit.setText("POI file")
        self.poiEdit.setReadOnly(True)

        self.pprocessButton = QPushButton("Start")
        self.pprocessButton.setStyleSheet("height: 15px;width: 24px;")
        self.pprocessButton.clicked.connect(self.processing)
        self.pprocessButton.setToolTip('Click to start pre-processing')

        self.savefileButton = QPushButton("Save")
        self.savefileButton.setStyleSheet("height: 15px;width: 24px;")
        self.savefileButton.clicked.connect(self.save_pdata)
        self.savefileButton.setToolTip("Click to save the results")
        self.savefileButton.setVisible(False)

        layout = QFormLayout()
        layout.addRow(loadabaButton, self.abaEdit)
        layout.addRow(loadsyncButton, self.syncEdit)
        layout.addRow(loadsegButton, self.segEdit)
        layout.addRow(loadpoiButton, self.poiEdit)
        layout.addWidget(self.pprocessButton)
        layout.addWidget(self.savefileButton)

        self.topLeftGroupBox.setLayout(layout)

    def createTopRightGroupBox(self):

        self.topRightGroupBox = QGroupBox("Anomaly detection")

        loadpfileButton = QPushButton("Browse")
        loadpfileButton.clicked.connect(self.browse_file)

        self.processedEdit = QLineEdit()
        self.processedEdit.setText("Pre-processed file")
        self.processedEdit.setReadOnly(True)

        loadsegButton = QPushButton("Browse")
        loadsegButton.clicked.connect(self.browse_seg1)

        self.segEdit1 = QLineEdit()
        self.segEdit1.setText("SEG file")
        self.segEdit1.setReadOnly(True)

        self.fqbox = QComboBox()
        self.fqbox.addItems(['RMS', 'Kurtosis', 'Crest factor', 'Impulse factor', 'Skewness', 'Peak-to-peak', 'All'])
        self.fqbox.currentIndexChanged.connect(self.selection_change)

        self.swinqbox = QComboBox()
        self.swinqbox.addItems(['500', '1000', '1500', '2000', '2500', '3000', '3500', '4000', '5000', '500'])
        self.swinqbox.currentIndexChanged.connect(self.selection_change)

        swinsbox = QSpinBox()
        swinsbox.stepBy(1000)
        swinsbox.setMinimum(1000)
        swinsbox.setMaximum(6000)

        self.detectanomButton = QPushButton("Start")
        self.detectanomButton.setStyleSheet("height: 15px;width: 24px;")
        self.detectanomButton.clicked.connect(self.detect_anomalies)
        self.detectanomButton.setToolTip("Click to start anomaly detection")

        self.saveButton = QPushButton("Save")
        self.saveButton.setStyleSheet("height: 15px;width: 24px;")
        self.saveButton.clicked.connect(self.save_results)
        self.saveButton.setToolTip("Click to save the results")
        self.saveButton.setVisible(False)

        layout = QFormLayout()
        layout.addRow(loadpfileButton, self.processedEdit)
        layout.addRow(loadsegButton, self.segEdit1)
        layout.addRow(QLabel("No. of features:"), self.fqbox)
        layout.addRow(QLabel("Sliding window:"), self.swinqbox)
        layout.addWidget(self.detectanomButton)
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
        textEdit.isReadOnly()
        textEdit.setPlainText("Train axle-box acceleration data\n"
                              "has been used to find incipient defects\n" 
                              "rail defects.\n\n"
                              "Blue color in results represents incipient ABA anomaly.\n"
                              "Yellow color in results represents intermediate ABA anomaly.\n"
                              "Red color in results represents severe ABA anomaly.\n")

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

        self.tbox = QComboBox()
        self.tbox.addItems(['25', '50', '100', '150', '200', '250'])
        self.tbox.currentIndexChanged.connect(self.selection_change)

        self.ispinBox = QSpinBox(self.bottomRightGroupBox)
        self.ispinBox.setValue(0)
        self.ispinBox.setMinimum(0)
        self.ispinBox.setMaximum(15)
        self.ispinBox.valueChanged.connect(self.selection_change)

        self.stbox = QComboBox()
        self.stbox.addItems(['16', '32', '64', '128', '256', '512'])
        self.stbox.currentIndexChanged.connect(self.selection_change)


        slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
        slider.setValue(40)
        slider.show()

        layout = QGridLayout()
        layout.addWidget(QLabel("Impurity ratio (%):"), 0, 0, 1, 3)
        layout.addWidget(self.ispinBox, 0, 1, 1, 3)
        layout.addWidget(QLabel("Sub-sampling size:"), 1, 0, 1, 3)
        layout.addWidget(self.stbox, 1, 1, 1, 3)
        layout.addWidget(QLabel("No. of trees:"), 2, 0, 1, 3)
        layout.addWidget(self.tbox, 2, 1, 1, 3)
        layout.addWidget(slider, 3, 0, 1, 4)
        # layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

# ///////////////////// System functions /////////////////////////

    def openFileNameDialog(self, type=None):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                          "All Files (*);;Python Files (*.py)", options=options)

        if fileName:
            if self.type == 'anomaly' and not str(fileName).endswith('.h5'):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("File Error")
                msg.setInformativeText('Please select the file with .h5 format!')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif self.type != 'anomaly' and not str(fileName).endswith('.csv'):
                if self.type == 'aba' and not str(fileName).endswith('.h5'):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("File Error")
                    msg.setInformativeText('Please select the file with .h5 format!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                elif self.type!= 'aba':
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("File Error")
                    msg.setInformativeText('Please select the file with .csv format!')
                    msg.setWindowTitle("Error")
                    msg.exec_()

        if self.type == 'anomaly':
                print(fileName)
                self.ppfile = fileName
                self.processedEdit.setText(str(fileName))

        elif self.type == 'aba':
                print(fileName)
                self.abafile = fileName
                self.abaEdit.setText(str(fileName))
                # self.tableWidget.setItem(0, 1, QTableWidgetItem(str(123)))
                # self.close()
        elif self.type == 'sync':
                print(fileName)
                self.syncfile = fileName
                self.syncEdit.setText(str(fileName))
        elif self.type == 'poi':
                print(fileName)
                self.poifile = fileName
                self.poiEdit.setText(str(fileName))
        elif self.type == 'seg':
                print(fileName)
                self.segfile = fileName
                self.segEdit.setText(str(fileName))
        elif self.type == 'seg1':
                print(fileName)
                self.segfile = fileName
                self.segEdit1.setText(str(fileName))


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
                                          "All Files (*); MS Excel Files (*.csv); ; hdf5 (*.h5)", options=options)

        if fileName:
            print(fileName)
            self.savefile = fileName


    def selection_change(self):

        self.feature = self.fqbox.currentText()
        print(self.feature)
        self.swin = int(self.swinqbox.currentText())
        self.impurity = float(self.ispinBox.value() / 100)
        print(self.impurity)
        self.sssize = int(self.stbox.currentText())
        self.trees = int(self.tbox.currentText())


    def processing(self):

        if self.abafile and self.syncfile and self.segfile and self.poifile:

           self.ppdata = pre_processing(self.abafile, self.syncfile, self.segfile, self.poifile, None)
           self.savefileButton.setVisible(True)
           self.pprocessButton.setVisible(False)
           self.abaEdit.setText("ABA file")
           self.syncEdit.setText("SYNC file")
           self.segEdit.setText("SEG file")
           self.poiEdit.setText("POI file")

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("File Error")
            msg.setInformativeText('Please load all the required files...')
            msg.setWindowTitle("File missing!")
            msg.exec_()

    def detect_anomalies(self):

        if self.ppfile == None:

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("File Error")
            msg.setInformativeText('Please load the pre-processed file!')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            obj = RailDefects(1)
            self.output = obj.anomaly_detection(self.ppfile, self.segfile, self.feature, self.swin, self.sssize, self.impurity)
            loc = self.output[0, 0]
            cnt = self.output[0, 1]
            sev = self.output[0, 2]
            print("First Anomaly: ", loc, cnt, sev)
            # self.output = np.array([[2], [3], [5]])
            self.saveButton.setVisible(True)
            self.detectanomButton.setVisible(False)
            self.processedEdit.setText("Pre-processed file")
            self.segEdit.setText("SEG file")

            # Populate the table
            if len(self.output) > 0:
                for i in range(75):
                    for j in range(3):
                        val = self.output[i, j]
                        print("Value:", val)
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                        if j == 2:
                            if self.output[i, 2] <= 0.4:
                                self.tableWidget.item(i, 2).setBackground(QColor(Qt.blue))
                            elif self.output[i, 2] > 0.4 and self.output[i, 2] <= 0.75:
                                self.tableWidget.item(i, 2).setBackground(QColor(Qt.yellow))
                            else:
                                self.tableWidget.item(i, 2).setBackground(QColor(Qt.red))

    def browse_aba(self):

        self.type = 'aba'
        self.openFileNameDialog(self.type)

    def browse_sync(self):

        self.type = 'sync'
        self.openFileNameDialog(self.type)

    def browse_poi(self):

        self.type = 'poi'
        self.openFileNameDialog(self.type)

    def browse_seg(self):

        self.type = 'seg'
        self.openFileNameDialog(self.type)

    def browse_seg1(self):

        self.type = 'seg1'
        self.openFileNameDialog(self.type)

    def browse_file(self):

        self.type = 'anomaly'
        self.openFileNameDialog(self.type)

    def save_results(self):

        self.key = None
        self.saveFileDialog()

        with open(self.savefile + '.csv', 'w', newline='') as file:
            try:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['positions', 'counters', 'severity'])
                for pos, cnt, sev in self.output:
                    writer.writerow([pos, cnt, sev])
            finally:
                file.close()

        self.detectanomButton.setVisible(True)
        self.saveButton.setVisible(False)
        self.tableWidget.clearContents()

    def save_pdata(self):

        self.key = 'processed'
        self.saveFileDialog()
        self.ppdata.to_hdf(self.savefile + '.h5', key='processed', mode='w')
        self.pprocessButton.setVisible(True)
        self.savefileButton.setVisible(False)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())