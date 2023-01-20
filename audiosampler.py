import time

import pyaudio
import numpy as np


class AudioSampler:
    _VERSION_ = "1.0"

    def __init__(self, channels=2, rate=44100):

        self.stream = None

        self.p = pyaudio.PyAudio()

        self.CHANNELS = channels
        self.RATE = rate

    def start_stream(self):

        self.stream = self.p.open(format=pyaudio.paFloat32,
                        channels=self.CHANNELS,
                        rate=self.wRATE,
                        output=True,
                        input=True,
                        stream_callback=callback)

        self.stream.start_stream()

    def stop_stream(self):

        if self.stream.is_active():
            self.stream.stop_stream()
            print("Stream is stopped")

        self.stream.close()

        self.p.terminate()

def callback(in_data, frame_count, time_info, flag):
    # using Numpy to convert to array for processing
    # audio_data = np.fromstring(in_data, dtype=np.float32)
    return in_data, pyaudio.paContinue