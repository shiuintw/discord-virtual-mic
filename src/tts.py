import sounddevice as sd
import numpy as np
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment

# device search
class Speech:
    def __init__(self):
        self.device = -1
        for i, s in enumerate(str(sd.query_devices()).split('\n')):
            if 'CABLE Input' in s:
                self.device = i
                break

        if self.device == -1:
            print('no device detected')
            exit()

        self.sr = 48000

    # speak
    def speak(self, text_input, lang='en'):
        tts = gTTS(text_input, lang=lang)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio = AudioSegment.from_mp3(buf)
        audio = audio.set_frame_rate(self.sr).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        sd.play(samples, samplerate=self.sr, device=self.device)
        sd.wait()