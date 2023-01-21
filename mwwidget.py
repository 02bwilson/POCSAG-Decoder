import time

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QHeaderView
from audiosampler import AudioSampler
import pyqtgraph as pg


class MainWidget(QtWidgets.QWidget):
    _VERSION_ = "1.0"

    def __init__(self):
        super().__init__()

        self.layout = None
        self.decode_modle = None
        self.decode_table = None
        self.form_layout = None
        self.audio_sampler = None
        self.audio_devices = None
        self.audio_select = None
        self.graphWidget = None
        self.timer = None
        self.plot_line = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.audio_select = QtWidgets.QComboBox()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.setup_table()

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.audio_sampler = AudioSampler(mw=self)
        self.audio_sampler.update.connect(self.plot_data)
        self.audio_devices = self.audio_sampler.get_audio_devices()

        self.audio_select.addItems(self.audio_devices)
        self.audio_select.currentIndexChanged.connect(self.change_audio_device)

        self.layout.addWidget(self.audio_select)
        self.layout.addWidget(self.graphWidget)
        self.plot_line = self.graphWidget.plot([0])

        self.setLayout(self.layout)

    def plot_data(self, data):
        self.plot_line.setData(data)

    def change_audio_device(self):
        self.audio_sampler.set_audio_device(self.audio_select.currentText().split(" ")[0])

    def setup_table(self):
        self.decode_model = QtGui.QStandardItemModel()
        self.decode_model.setHorizontalHeaderLabels(['POCSAG VERSION', 'TYPE', 'MESSAGE'])

        self.decode_table = QtWidgets.QTableView()
        self.decode_table.setModel(self.decode_model)
        header = self.decode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.decode_table.setFixedHeight(200)
        self.layout.addWidget(self.decode_table)
