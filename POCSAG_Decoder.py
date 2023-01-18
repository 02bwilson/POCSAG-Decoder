import sys
import argparse

from PyQt6.QtWidgets import QApplication

from mainwindow import Window





if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='POCSAG Decoder',
        description='Decodes POCSAG signals.')

    parser.add_argument('-t', '--terminal',
                        action='store_true',
                        help='Run the program in the terminal.')
    parser.add_argument('-r', '--rtlsdr',
                        action='store_true',
                        help='If you are using a RTLSDR, you can control it through commands.')

    args = parser.parse_args()

    app = QApplication([])

    window = Window(args)
    if(args.terminal == False):
        window.show()

    sys.exit(app.exec())