import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class DataProcessor(QThread):
    _VERSION_ = "1.0"

    ret_data = pyqtSignal(str)
    ret_msg = pyqtSignal(str)
    ret_addr = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.speed = 1200
        self.fs = 24000
        self.cnt = int(self.fs / self.speed)
        self.start = 0

    def process(self, data):
        if np.random.rand() * 10 > 9:
            for p in range(2 * self.cnt):
                if data[p] < - 50 and data[p + 1] > 50:
                    self.start = p
                    break
            bits = np.zeros(data.size)
            for p in range(0, data.size - self.cnt, self.cnt):
                bits[self.start + p] = 500
            bits_str = ""
            for p in range(0, data.size - self.cnt + 1, self.cnt):
                s = 0
                for p1 in range(p, p + self.cnt):
                    s += data[p]
                bits_str += "1" if s < 0 else "0"

            self.ret_data.emit(bits_str)

    def parse_msg(self, block):
        msgs = ""
        for cw in range(16):
            cws = block[32 * cw:32 * (cw + 1)]
            # Skip the idle word
            if cws.startswith("0111101010"):
                continue

            if cws[0] == "0":
                addr, type = cws[1:19], cws[19:21]
                self.ret_addr.emit(addr, type)
            else:
                msg = cws[1:21]
                msgs += msg

        # Split long string to 7 chars blocks
        bits = [msgs[i:i + 7] for i in range(0, len(msgs), 7)]

        # Get the message
        msg = ""
        for b in bits:
            b1 = b[::-1]  # Revert string
            value = int(b1, 2)
            msg += chr(value)
        self.ret_msg.emit(msg)