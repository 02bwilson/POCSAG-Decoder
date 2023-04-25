import datetime

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QThread, QModelIndex
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QHeaderView, QTableWidgetItem, QLabel
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
        self.frame_count = None
        self.msg_count = None
        self.status_label = None
        self.raw_data = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.audio_select = QtWidgets.QComboBox()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.setup_table()

        self.data_viewer = dataviewer

        self.prev_bitstr = ""
        self.bit_data = ""
        self.cur_addr = ""
        self.preamble_status = False
        self.fs_status = False
        self.exdata_stat = False

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color:white; text-align:right;")

        self.msg_count = 0
        self.frame_count = 0

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
        self.layout.addWidget(self.status_label)

        self.plot_line = self.graphWidget.plot([0])
        self.setStyleSheet("""QToolTip { 
                                   background-color: black; 
                                   color: white; 
                                   border: black solid 1px
                                   }""")


        self.setLayout(self.layout)

    def addr_handler(self, data):
        self.cur_addr = data

    def msg_handler(self, data, raw_data):
        if self.cur_addr != None:
            self.curmsg = data
            self.raw_data = raw_data
            self.add_msg()
            self.cur_addr = None

    def add_msg(self):
        time, addr, msg = (QStandardItem(datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")),
                                     QStandardItem(str(int(self.cur_addr, 2))), QStandardItem(str(self.curmsg)))
        tt = ""
        length = len(self.raw_data)
        for i in range(0, len(self.raw_data), 16):
            tt += str(hex(int(self.raw_data[i: i + 16]))) + '\n'
        msg.setToolTip(tt)
        self.decode_model.appendRow([time, addr, msg])

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
        self.frame_count += 1
        self.fs_status = True
        self.update_status()

    def update_status(self):
        self.status_label = QLabel("{} | {} M/F".format(self.msg_count, self.frame_count))

    def msg_over(self):
        self.fs_status = False
        self.msg_count += 1
        self.update_status()

    def recv_data(self, data):
        self.plot_data(data)
        bitstr = self.data_processor.process(data)
        self.bit_data += bitstr
        if self.exdata_stat:
            self.bit_data += self.exdata_temp
            self.exdata_stat = False
            self.exdata_temp = ""
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

    def plot_data(self, data):
        self.plot_line.setData(data)

    def change_audio_device(self):
        self.audio_sampler.set_audio_device(self.audio_select.currentText().split(" ")[0])

    def setup_table(self):
        self.decode_model = QtGui.QStandardItemModel()
        self.decode_model.setHorizontalHeaderLabels(['TIME', 'ADDR', 'MESSAGE'])

        self.decode_table = QtWidgets.QTableView()
        self.decode_table.setModel(self.decode_model)
        self.decode_table.verticalHeader().setVisible(False)
        self.decode_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.decode_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.decode_table.setFixedHeight(200)
        self.layout.addWidget(self.decode_table)
