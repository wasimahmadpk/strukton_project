#!/usr/bin/env python
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QDialog, QFileDialog, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton,
    QSizePolicy, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

import numpy as np

from railai.io_utils import write_csv
from railai.pipeline import RailDefects
from railai.preprocessing import pre_processing


APP_STYLESHEET = """
QDialog#RailCMS {
    background: #e7edf3;
}
QFrame#Header {
    background: #14324f;
    border: none;
}
QLabel#AppTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
QLabel#AppSubtitle {
    color: #b7c8d8;
    font-size: 12px;
}
QLabel#AppBadge {
    color: #d7e6f2;
    font-size: 11px;
    padding: 4px 10px;
    background: #1d4669;
    border-radius: 10px;
}
QFrame#Card {
    background: #ffffff;
    border: 1px solid #cfd8e1;
    border-radius: 8px;
}
QLabel#CardTitle {
    color: #14324f;
    font-size: 13px;
    font-weight: 700;
}
QLabel#CardHint {
    color: #6b7c8d;
    font-size: 11px;
}
QLabel#FieldLabel {
    color: #3d4f61;
    font-size: 11px;
    font-weight: 600;
}
QLineEdit {
    background: #f6f8fb;
    border: 1px solid #c5d0da;
    border-radius: 4px;
    padding: 6px 8px;
    color: #1c2b39;
    selection-background-color: #1a6f8b;
}
QLineEdit:focus {
    border: 1px solid #1a6f8b;
    background: #ffffff;
}
QComboBox, QSpinBox {
    background: #ffffff;
    border: 1px solid #c5d0da;
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 22px;
}
QComboBox:focus, QSpinBox:focus {
    border: 1px solid #1a6f8b;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #b7c4d0;
    border-radius: 4px;
    padding: 6px 12px;
    color: #1c2b39;
    font-weight: 600;
}
QPushButton:hover {
    background: #f3f7fa;
    border-color: #1a6f8b;
}
QPushButton:pressed {
    background: #e4eef3;
}
QPushButton#Primary {
    background: #1a6f8b;
    color: #ffffff;
    border: 1px solid #155a71;
}
QPushButton#Primary:hover {
    background: #155a71;
}
QPushButton#Save {
    background: #2d6a4f;
    color: #ffffff;
    border: 1px solid #24563f;
}
QPushButton#Save:hover {
    background: #24563f;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f4f7fa;
    border: 1px solid #cfd8e1;
    border-radius: 6px;
    gridline-color: #e4ebf1;
    selection-background-color: #d7e8f0;
    selection-color: #14324f;
}
QHeaderView::section {
    background: #f0f4f8;
    color: #14324f;
    border: none;
    border-bottom: 1px solid #cfd8e1;
    padding: 8px 10px;
    font-weight: 700;
}
QLabel#ResultsTitle {
    color: #14324f;
    font-size: 15px;
    font-weight: 700;
}
QLabel#ResultsMeta {
    color: #5b6d7d;
    font-size: 12px;
}
QLabel#Legend {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 9px;
}
QLabel#LegendIncipient {
    background: #dbe4f8;
    color: #1d3f8f;
}
QLabel#LegendMedium {
    background: #f8efc8;
    color: #7a5b10;
}
QLabel#LegendSevere {
    background: #f6d5d5;
    color: #8a1f1f;
}
QLabel#Footnote {
    color: #6b7c8d;
    font-size: 11px;
}
"""


def _format_result(column, value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if column == 0:
        return "%.2f" % number
    if column == 1:
        return str(int(number))
    return "%.2f" % number


def _error(title, text, informative):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setInformativeText(informative)
    msg.setWindowTitle(title)
    msg.exec_()


def _card(title, hint=None):
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("CardTitle")
    layout.addWidget(heading)
    if hint:
        note = QLabel(hint)
        note.setObjectName("CardHint")
        note.setWordWrap(True)
        layout.addWidget(note)
    return frame, layout


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.setObjectName("RailCMS")
        self.resize(1240, 800)
        self.setMinimumSize(980, 680)
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
        self.setStyleSheet(APP_STYLESHEET)
        icon = _REPO_ROOT / "res" / "srail.jpg"
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(16, 16, 16, 16)
        body_layout.setSpacing(14)
        body_layout.addWidget(self._build_sidebar(), 0)
        body_layout.addWidget(self._build_results(), 1)
        root.addWidget(body, 1)

        self.setWindowTitle("RailCMS — Rail Condition Monitoring")
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowCloseButtonHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )
        self.selection_change()

    def _build_header(self):
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(72)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 10, 22, 10)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Rail Condition Monitoring System")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Axle-box acceleration  ·  Isolation Forest  ·  Track localisation")
        subtitle.setObjectName("AppSubtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)

        badge = QLabel("Strukton Rail  ·  University of Twente")
        badge.setObjectName("AppBadge")

        layout.addLayout(titles, 1)
        layout.addWidget(badge, 0, Qt.AlignRight | Qt.AlignVCenter)
        return header

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(360)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomRightGroupBox()

        layout.addWidget(self.topLeftGroupBox)
        layout.addWidget(self.topRightGroupBox)
        layout.addWidget(self.bottomRightGroupBox)
        layout.addStretch(1)
        return sidebar

    def _build_results(self):
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        heading = QHBoxLayout()
        title = QLabel("Results")
        title.setObjectName("ResultsTitle")
        self.resultsMeta = QLabel("No detections yet")
        self.resultsMeta.setObjectName("ResultsMeta")
        heading.addWidget(title)
        heading.addStretch(1)
        heading.addWidget(self.resultsMeta)
        layout.addLayout(heading)

        legend = QHBoxLayout()
        legend.setSpacing(8)
        for text, name in (
            ("Incipient  ≤ 0.40", "LegendIncipient"),
            ("Intermediate  ≤ 0.75", "LegendMedium"),
            ("Severe  > 0.75", "LegendSevere"),
        ):
            chip = QLabel(text)
            chip.setObjectName(name)
            chip.setProperty("class", "legend")
            legend.addWidget(chip)
        legend.addStretch(1)
        layout.addLayout(legend)

        self.createBottomLeftTabWidget(self.output)
        layout.addWidget(self.tableWidget, 1)

        note = QLabel(
            "Train axle-box acceleration is used to find incipient rail defects. "
            "Blue is incipient, yellow is intermediate, and red is severe."
        )
        note.setObjectName("Footnote")
        note.setWordWrap(True)
        layout.addWidget(note)
        return panel

    def _file_field(self, caption, placeholder, on_browse):
        box = QWidget()
        col = QVBoxLayout(box)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        label = QLabel(caption)
        label.setObjectName("FieldLabel")
        field = QLineEdit()
        field.setReadOnly(True)
        field.setPlaceholderText(placeholder)
        browse = QPushButton("Browse")
        browse.clicked.connect(on_browse)
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(field, 1)
        row.addWidget(browse)
        col.addWidget(label)
        col.addLayout(row)
        return box, field

    def _primary_row(self, start_button, save_button):
        row = QHBoxLayout()
        row.setSpacing(8)
        start_button.setObjectName("Primary")
        start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        save_button.setObjectName("Save")
        save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.addWidget(start_button)
        row.addWidget(save_button)
        return row

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox, layout = _card(
            "1  Pre-processing",
            "Load ABA, SYNC, SEG and POI files, then write a processed HDF5 file.",
        )

        aba_row, self.abaEdit = self._file_field("ABA measurement", "ABA file (.h5)", self.browse_aba)
        sync_row, self.syncEdit = self._file_field("SYNC counters", "SYNC file (.csv)", self.browse_sync)
        seg_row, self.segEdit = self._file_field("SEG route", "SEG file (.csv)", self.browse_seg)
        poi_row, self.poiEdit = self._file_field("POI switches", "POI file (.csv)", self.browse_poi)

        self.pprocessButton = QPushButton("Start pre-processing")
        self.pprocessButton.clicked.connect(self.processing)
        self.pprocessButton.setToolTip("Click to start pre-processing")

        self.savefileButton = QPushButton("Save processed file")
        self.savefileButton.clicked.connect(self.save_pdata)
        self.savefileButton.setToolTip("Click to save the results")
        self.savefileButton.setVisible(False)

        layout.addWidget(aba_row)
        layout.addWidget(sync_row)
        layout.addWidget(seg_row)
        layout.addWidget(poi_row)
        layout.addLayout(self._primary_row(self.pprocessButton, self.savefileButton))

    def createTopRightGroupBox(self):
        self.topRightGroupBox, layout = _card(
            "2  Anomaly detection",
            "Score a processed recording and map anomalies to track kilometres.",
        )

        processed_row, self.processedEdit = self._file_field(
            "Processed recording", "Pre-processed file (.h5)", self.browse_file
        )
        seg_row, self.segEdit1 = self._file_field("SEG route", "SEG file (.csv)", self.browse_seg1)

        self.fqbox = QComboBox()
        self.fqbox.addItems(
            ["RMS", "Kurtosis", "Crest factor", "Impulse factor", "Skewness", "Peak-to-peak", "All"]
        )
        self.fqbox.currentIndexChanged.connect(self.selection_change)

        self.swinqbox = QComboBox()
        self.swinqbox.addItems(
            ["500", "1000", "1500", "2000", "2500", "3000", "3500", "4000", "5000", "500"]
        )
        self.swinqbox.currentIndexChanged.connect(self.selection_change)

        options = QFormLayout()
        options.setContentsMargins(0, 4, 0, 0)
        options.setSpacing(8)
        options.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        feat_label = QLabel("Features")
        feat_label.setObjectName("FieldLabel")
        win_label = QLabel("Sliding window")
        win_label.setObjectName("FieldLabel")
        options.addRow(feat_label, self.fqbox)
        options.addRow(win_label, self.swinqbox)

        self.detectanomButton = QPushButton("Start detection")
        self.detectanomButton.clicked.connect(self.detect_anomalies)
        self.detectanomButton.setToolTip("Click to start anomaly detection")

        self.saveButton = QPushButton("Save results")
        self.saveButton.clicked.connect(self.save_results)
        self.saveButton.setToolTip("Click to save the results")
        self.saveButton.setVisible(False)

        layout.addWidget(processed_row)
        layout.addWidget(seg_row)
        layout.addLayout(options)
        layout.addLayout(self._primary_row(self.detectanomButton, self.saveButton))

    def createBottomLeftTabWidget(self, output):
        self.tableWidget = QTableWidget(0, 3)
        self.tableWidget.setHorizontalHeaderLabels(["Position (km)", "Counter", "Severity"])
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setDefaultSectionSize(28)

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox, layout = _card(
            "3  Model parameters",
            "Isolation Forest settings used when detection starts.",
        )

        self.tbox = QComboBox()
        self.tbox.addItems(["25", "50", "100", "150", "200", "250"])
        self.tbox.currentIndexChanged.connect(self.selection_change)

        self.ispinBox = QSpinBox()
        self.ispinBox.setValue(0)
        self.ispinBox.setMinimum(0)
        self.ispinBox.setMaximum(15)
        self.ispinBox.valueChanged.connect(self.selection_change)

        self.stbox = QComboBox()
        self.stbox.addItems(["16", "32", "64", "128", "256", "512"])
        self.stbox.currentIndexChanged.connect(self.selection_change)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)
        for text, widget in (
            ("Impurity ratio (%)", self.ispinBox),
            ("Sub-sampling size", self.stbox),
            ("No. of trees", self.tbox),
        ):
            label = QLabel(text)
            label.setObjectName("FieldLabel")
            form.addRow(label, widget)
        layout.addLayout(form)

    def _fill_results_table(self, rows):
        n_rows = min(75, len(rows))
        self.tableWidget.setRowCount(n_rows)
        for i in range(n_rows):
            for j in range(3):
                val = rows[i, j]
                item = QTableWidgetItem(_format_result(j, val))
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(i, j, item)
                if j == 2:
                    severity = rows[i, 2]
                    if severity <= 0.4:
                        item.setBackground(QColor(Qt.blue))
                        item.setForeground(QColor(Qt.white))
                    elif severity > 0.4 and severity <= 0.75:
                        item.setBackground(QColor(Qt.yellow))
                    else:
                        item.setBackground(QColor(Qt.red))
                        item.setForeground(QColor(Qt.white))
        if n_rows == 1:
            self.resultsMeta.setText("1 detection")
        else:
            self.resultsMeta.setText("%d detections" % n_rows)

    # ///////////////////// System functions /////////////////////////

    def openFileNameDialog(self, type=None):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                          "All Files (*);;Python Files (*.py)", options=options)

        if fileName:
            if self.type == 'anomaly' and not str(fileName).endswith('.h5'):
                _error("Error", "File Error", "Please select the file with .h5 format!")

            elif self.type != 'anomaly' and not str(fileName).endswith('.csv'):
                if self.type == 'aba' and not str(fileName).endswith('.h5'):
                    _error("Error", "File Error", "Please select the file with .h5 format!")
                elif self.type != 'aba':
                    _error("Error", "File Error", "Please select the file with .csv format!")

        if self.type == 'anomaly':
                print(fileName)
                self.ppfile = fileName
                self.processedEdit.setText(str(fileName))

        elif self.type == 'aba':
                print(fileName)
                self.abafile = fileName
                self.abaEdit.setText(str(fileName))
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
        if not hasattr(self, "tbox"):
            return
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
           self.abaEdit.clear()
           self.syncEdit.clear()
           self.segEdit.clear()
           self.poiEdit.clear()

        else:
            _error("File missing!", "File Error", "Please load all the required files...")

    def detect_anomalies(self):

        if self.ppfile is None:
            _error("Error", "File Error", "Please load the pre-processed file!")
        else:
            obj = RailDefects(1)
            self.output = obj.anomaly_detection(self.ppfile, self.segfile, self.feature, self.swin, self.sssize, self.impurity)
            loc = self.output[0, 0]
            cnt = self.output[0, 1]
            sev = self.output[0, 2]
            print("First Anomaly: ", loc, cnt, sev)
            self.saveButton.setVisible(True)
            self.detectanomButton.setVisible(False)
            self.processedEdit.clear()
            self.segEdit1.clear()

            if len(self.output) > 0:
                self._fill_results_table(self.output)

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

        write_csv(self.savefile + '.csv', ['positions', 'counters', 'severity'], self.output)

        self.detectanomButton.setVisible(True)
        self.saveButton.setVisible(False)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.resultsMeta.setText("No detections yet")

    def save_pdata(self):

        self.key = 'processed'
        self.saveFileDialog()
        self.ppdata.to_hdf(self.savefile + '.h5', key='processed', mode='w')
        self.pprocessButton.setVisible(True)
        self.savefileButton.setVisible(False)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    font = QFont()
    font.setFamily(font.defaultFamily())
    font.setPointSize(11)
    app.setFont(font)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
