import pyaudio
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class AudioSampler(QThread):
    _VERSION_ = "1.0"

    update = pyqtSignal(np.ndarray)

    def __init__(self, mw=None, channels=1, rate=24000):
        super().__init__()

        self.stream = None
        self.data = [0]
        self.p = pyaudio.PyAudio()
        self.mw = mw
        self.CHANNELS = channels
        self.RATE = rate
        self.audio_cache = []

    def stop_stream(self):
        if self.stream.is_active():
            self.stream.stop_stream()
            print("Stream is stopped")

        self.stream.close()

        self.p.terminate()

    def update_data(self, data):
        self.update.emit(data)

    def get_audio_devices(self):
        devices = []
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                devices += [str((str(i) + " - " + self.p.get_device_info_by_host_api_device_index(0, i).get('name')))]
        return devices

    def set_audio_device(self, id):
        if self.stream is not None:
            self.stop_stream()
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=False,
                                  input=True,
                                  input_device_index=int(id),
                                  stream_callback=self.callback)

    def callback(self, in_data, frame_count, time_info, flag):
        audio_data = np.fromstring(in_data, dtype=np.float32)
        self.update_data(audio_data)
        return in_data, pyaudio.paContinue


