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
        self.fs_status = None
        self.curaddr = None
        self.curmsg = None
        self.curtype = None
        self.plot_line = None
        self.preamble_status = None
        self.bit_data = None
        self.cur_addr = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.audio_select = QtWidgets.QComboBox()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.graphWidget.setYRange(max=1, min=-1)
        self.setup_table()

        self.bit_data = ""
        self.cur_addr = ""
        self.preamble_status = False
        self.fs_status = False

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.data_processor = DataProcessor()
        self.data_processor.preamble.connect(self.preamble_handler)
        self.data_processor.framesync.connect(self.fs_handler)
        self.data_processor.addr.connect(self.addr_handler)
        self.data_processor.fs_exdata.connect(self.add_extra_data)
        self.data_processor.message.connect(self.msg_handler)
        self.data_processor.msg_batch_over.connect(self.msg_over)

        self.audio_sampler = AudioSampler(mw=self)
        self.audio_sampler.update.connect(self.recv_data)
        self.audio_devices = self.audio_sampler.get_audio_devices()

        self.audio_select.addItems(self.audio_devices)
        self.audio_select.currentIndexChanged.connect(self.change_audio_device)

        self.layout.addWidget(self.audio_select)
        self.layout.addWidget(self.graphWidget)
        self.plot_line = self.graphWidget.plot([0])

        self.setLayout(self.layout)

    def addr_handler(self, data):
        self.cur_addr = data

    def msg_handler(self):
        if self.cur_addr != None:
            self.add_msg()

    def add_msg(self):
        print(self.cur_addr, self.curmsg)

    def preamble_handler(self):
        self.preamble_status = True

    def add_extra_data(self, data):
        self.bit_data = data

    def fs_handler(self):
        self.fs_status = True

    def msg_over(self):
        self.fs_status = False

    def recv_data(self, data):
        self.plot_data(data)
        bitstr = self.data_processor.process(data)
        self.bit_data += bitstr
        if len(self.bit_data) == 32:
            if not self.bit_data.startswith("01111") and not self.bit_data.endswith("01111"):
                if not self.preamble_status:
                    self.data_processor.await_preamble(self.bit_data)
                elif self.fs_status:
                    self.data_processor.build_msg(self.bit_data)
                else:
                    self.data_processor.await_msg(self.bit_data)
            if "0000000000000000" in self.bit_data:
                # print("<<<END OF MESSAGE>>>")
                self.preamble_status = False
            else:
                pass
                # print("IDLE BLOCK :: SKIPPING \n")
            self.bit_data = ""

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
