import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class DataProcessor(QThread):
    _VERSION_ = "1.0"

    preamble = pyqtSignal(str)
    framesync = pyqtSignal()
    fs_exdata = pyqtSignal(str)
    message = pyqtSignal(str)
    msg_batch_over = pyqtSignal()
    addr = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.speed = 1200
        self.fs = 48000
        self.cnt = int(self.fs / self.speed)
        self.cur_pre_framesync = ""
        self.cur_data = ""
        self.start = 0
        self.cur_msg = ""

    def process(self, data):
        # https://habr.com/en/post/438906/
        for p in range(2 * self.cnt):
            if data[p] < - 50 and data[p + 1] > 50:
                self.start = p
                break
        bits = np.zeros(data.size)
        for p in range(0, data.size, self.cnt):
            bits[self.start + p] = 500
        bits_str = ""
        for p in range(0, data.size, self.cnt):
            s = 0
            for p1 in range(p, p + self.cnt):
                s += data[p]
            bits_str += "1" if s < 0 else "0"
        return bits_str

    def await_preamble(self, bitstr):
        if bitstr == "10101010101010100101010101010101":
            print("!!! Preamble Detected !!! \n AWAITING FRAME SYNC")
            self.preamble.emit(bitstr)

    def await_msg(self, bitstr):
        # POSSIBLE FRAME SYNCS??? INCONSISTENT
        #print(bitstr)
        match_str = "011111001101001000"
        check_str = self.cur_pre_framesync + bitstr
        print(bitstr)
        #print(check_str)
        if match_str in check_str:
            print("!!! FRAME SYNC DETECTED !!! \n AWAITING MESSAGE")
            extra_data = check_str[check_str.rfind(match_str) + len(match_str):len(check_str)]
            self.cur_pre_framesync = ""
            self.framesync.emit()
            self.fs_exdata.emit(extra_data)
        else:
            self.cur_pre_framesync += bitstr

            #print(bitstr)

    def build_msg(self, bitstr):
        self.cur_data += bitstr
        full_msg = ""
        if len(self.cur_data) == 512:
            for cw in range(16):
                cws = self.cur_data[32 * cw:32 * (cw + 1)]
                if cws[0] == "0":
                    addr = cws[1:19]
                    #print("  Addr:" + addr)
                    self.addr.emit(addr)
                else:
                    msg = cws[1:21]
                    #print("  Msg: " + msg)
                    size = 4
                    s = ""
                    for ind in range(0, len(msg), size):
                        bcd_s = msg[ind:ind + size]
                        value = int(bcd_s, 2)
                        symbols = "0123456789*U -)("
                        s += symbols[value]
                    full_msg += s
                    #print("    1", s)
            print(full_msg)
            self.message.emit(full_msg)
            self.cur_data = ""
            self.msg_batch_over.emit()
            print()