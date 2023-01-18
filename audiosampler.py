import time

import pyaudio
import numpy as np


class AudioSampler:
    _VERSION_ = "1.0"

    def __init__(self, channels=2, rate=44100):
        p = pyaudio.PyAudio()

        self.CHANNELS = channels
        self.RATE = rate

        stream = p.open(format=pyaudio.paFloat32,
                        channels=self.CHANNELS,
                        rate=self.wRATE,
                        output=True,
                        input=True,
                        stream_callback=self.callback)

        stream.start_stream()

        while stream.is_active():
            time.sleep(20)
            stream.stop_stream()
            print("Stream is stopped")

        stream.close()

        p.terminate()

    def callback(in_data, frame_count, time_info, flag):
        # using Numpy to convert to array for processing
        # audio_data = np.fromstring(in_data, dtype=np.float32)
        return in_data, pyaudio.paContinue
