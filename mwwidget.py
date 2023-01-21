import time

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QHeaderView
from audiosampler import AudioSampler
import pyqtgraph as pg

from dataprocessor import DataProcessor


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
        self.data_processor = None
        self.timer = None
        self.curaddr = None
        self.curmsg = None
        self.curtype = None
        self.plot_line = None
        self.bit_data = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.audio_select = QtWidgets.QComboBox()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.setup_table()

        self.bit_data = ""

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.data_processor = DataProcessor()
        self.data_processor.ret_data.connect(self.handle_bit_data)
        self.audio_sampler = AudioSampler(mw=self)
        self.audio_sampler.update.connect(self.recv_data)
        self.audio_devices = self.audio_sampler.get_audio_devices()

        self.audio_select.addItems(self.audio_devices)
        self.audio_select.currentIndexChanged.connect(self.change_audio_device)

        self.layout.addWidget(self.audio_select)
        self.layout.addWidget(self.graphWidget)
        self.plot_line = self.graphWidget.plot([0])

        self.setLayout(self.layout)


    def handle_bit_data(self, bitstr):
        self.bit_data += bitstr
        if len(self.bit_data) == 512:
            self.data_processor.parse_msg(self.bit_data)
            self.bit_data = ""

    def recv_data(self, data):
        self.plot_data(data)
        self.data_processor.process(data)
    def plot_data(self, data):
        self.plot_line.setData(data)

    def change_audio_device(self):
        self.audio_sampler.set_audio_device(self.audio_select.currentText().split(" ")[0])

    def setup_table(self):
        self.decode_model = QtGui.QStandardItemModel()
        self.decode_model.setHorizontalHeaderLabels(['ADDR', 'TYPE', 'MESSAGE'])

        self.decode_table = QtWidgets.QTableView()
        self.decode_table.setModel(self.decode_model)
        header = self.decode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.decode_table.setFixedHeight(200)
        self.layout.addWidget(self.decode_table)
