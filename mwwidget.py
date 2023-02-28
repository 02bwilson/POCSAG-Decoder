import datetime

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QThread, QModelIndex
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem
from audiosampler import AudioSampler
import pyqtgraph as pg

from dataprocessor import DataProcessor


class MainWidget(QtWidgets.QWidget):
    _VERSION_ = "1.0"

    def __init__(self, dataviewer=None):
        super().__init__()

        self.layout = None
        self.decode_model = None
        self.decode_table = None
        self.data_viewer = None
        self.audio_sampler = None
        self.audio_devices = None
        self.audio_select = None
        self.graphWidget = None
        self.data_processor = None
        self.timer = None
        self.fs_status = None
        self.curmsg = None
        self.prev_bitstr = None
        self.exdata_temp = None
        self.curtype = None
        self.exdata_stat = None
        self.plot_line = None
        self.preamble_status = None
        self.bit_data = None
        self.cur_addr = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.audio_select = QtWidgets.QComboBox()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.graphWidget.setYRange(max=1, min=-1)
        self.setup_table()

        self.data_viewer = dataviewer

        self.prev_bitstr = ""
        self.bit_data = ""
        self.cur_addr = ""
        self.preamble_status = False
        self.fs_status = False
        self.exdata_stat = False

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

    def msg_handler(self, data):
        if self.cur_addr != None:
            self.curmsg = data
            self.add_msg()
            self.cur_addr = None

    def add_msg(self):
        self.decode_model.appendRow([QStandardItem(datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")),
                                     QStandardItem(str(int(self.cur_addr, 2))), QStandardItem(str(self.curmsg))])

    def preamble_handler(self):
        self.preamble_status = True

    def add_extra_data(self, data):
        self.exdata_stat = True
        self.exdata_temp = data

    def fs_handler(self):
        if self.fs_status:
            print("NEW Framesync detected !!! New Batch started... \n")
            self.add_msg()
            self.curmsg = None
            self.cur_addr = None
        self.fs_status = True

    def msg_over(self):
        self.fs_status = False

    def recv_data(self, data):
        self.plot_data(data)
        bitstr = self.data_processor.process(data)
        self.bit_data += bitstr
        if len(self.bit_data) >= 32:
            curdata = self.bit_data[:32]
            self.bit_data = self.bit_data.replace(curdata, '')

            if not self.preamble_status:
                self.data_processor.await_preamble(curdata)
            else:
                self.data_processor.await_fs(curdata)
                if self.fs_status:
                    self.data_processor.build_msg(curdata)

            if "000000000000" in curdata or "111111111111" in curdata:
                self.preamble_status = False
                self.fs_status = False
                self.bit_data = ""


    # def recv_data(self, data):
    #     self.plot_data(data)
    #     bitstr = self.data_processor.process(data)
    #     self.bit_data += bitstr
    #     if len(self.bit_data) >= 32:
    #         curdata = self.bit_data[:32]
    #         self.bit_data = self.bit_data.replace(curdata, '')
    #         print(curdata)
    #         if self.data_viewer != None and self.fs_status:
    #             self.data_viewer.add(curdata)
    #
    #         if curdata.count("01111") < 2:
    #             if not self.preamble_status:
    #                     self.data_processor.await_preamble(curdata)
    #             else:
    #                 self.data_processor.await_msg(curdata)
    #                 if "010101010101010101010" not in curdata and "011110101000" not in curdata:
    #                     #print("Building msg with: \t %s" % curdata)
    #                     self.data_processor.build_msg(curdata)
    #         if "11111111111111111111" in curdata or "0000000000000000" in curdata:
    #             # print("<<<END OF MESSAGE>>>")
    #             self.preamble_status = False
    #             self.fs_status = False
    #         else:
    #             pass
    #         self.bit_data = ""
    #         if self.exdata_stat:
    #             self.bit_data = self.exdata_temp
    #             self.exdata_stat = False


    def plot_data(self, data):
        self.plot_line.setData(data)


    def change_audio_device(self):
        self.audio_sampler.set_audio_device(self.audio_select.currentText().split(" ")[0])


    def setup_table(self):
        self.decode_model = QtGui.QStandardItemModel()
        self.decode_model.setHorizontalHeaderLabels(['TIME', 'ADDR', 'MESSAGE'])

        self.decode_table = QtWidgets.QTableView()
        self.decode_table.setModel(self.decode_model)
        # self.decode_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        header = self.decode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.decode_table.setFixedHeight(200)
        self.layout.addWidget(self.decode_table)
