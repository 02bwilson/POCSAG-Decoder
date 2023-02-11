from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class DataViewer(QWidget):
    _VERSION_ = "1.0"

    def __init__(self):
        super().__init__()

        self.table = None
        self.table_model = None
        self.layout = None

        self.setWindowTitle("Data Viewer")

        self.layout = QVBoxLayout()
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(['32 BIT RECV', ])

        self.table = QTableView()
        self.table.setModel(self.table_model)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.show()

    def add(self, bitstr):
        self.table_model.appendRow([QStandardItem(bitstr)])
