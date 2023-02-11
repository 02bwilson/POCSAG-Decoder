from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow
from commandhandler import CommandHandler
from dataviewer import DataViewer
from mwwidget import MainWidget


class Window(QMainWindow):
    _VERSION_ = "1.0"

    def __init__(self, args):
        super().__init__()

        # Setup vars
        self.icon = QIcon("images/icon.png")
        self.cmd_handler = None
        if args.terminal == True:
            self.cmd_handler = CommandHandler(args)
        self.setWindowTitle("POCSAG Decoder v{}".format(self._VERSION_))
        self.setWindowIcon(self.icon)
        self.setFixedSize(1200, 700)
        if args.dataviewer:
            self.data_view = DataViewer()
            self.mwwidget = MainWidget(dataviewer=self.data_view)
        else:
            self.mwwidget = MainWidget()
        self.setCentralWidget(self.mwwidget)
