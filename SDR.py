from rtlsdr import *


class SDR:
    _VERSION_ = "1.0"

    def __init__(self, sample_rate=2e6, center_freq=95e6, freq_correction=45, gain='auto'):

        # Instantiate sdr object
        self.sdr_obj = RtlSdr()

        # Set params
        self.set_sample_rate(sample_rate)
        self.set_center_freq(center_freq)
        self.set_freq_correction(freq_correction)
        self.set_gain(gain)

    def read_samples(self, size):
        return self.sdr_obj.read_samples(size)

    def close(self):
        self.sdr_obj.close()

    def set_sample_rate(self, rate):
        try:
            self.sdr_obj.sample_rate = rate
        except:
            print("Invalid Sample Rate!")

    def set_center_freq(self, freq):
        try:
            self.sdr_obj.center_freq = freq
        except Exception as e:
            print(e)
            print("Invalid Center Freq!")

    def set_freq_correction(self, rate):
        try:
            self.sdr_obj.freq_correction = rate
        except:
            print("Invalid Freq Correction!")

    def set_gain(self, gain):
        try:
            self.sdr_obj.gain = gain
        except:
            print("Invalid Gain!")
