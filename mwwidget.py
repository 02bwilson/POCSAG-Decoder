from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QHeaderView


class MainWidget(QtWidgets.QWidget):
    _VERSION_ = "1.0"

    def __init__(self):
        super().__init__()

        self.layout = None
        self.decode_modle = None
        self.decode_table = None
        self.form_layout = None

        # Setup basic stuff
        self.layout = QtWidgets.QVBoxLayout()
        self.form_layout = QtWidgets.QFormLayout()
        self.setup_table()

        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

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
