import sounddevice as sd
import numpy as np
from gtts import gTTS
import edge_tts, asyncio
from io import BytesIO
from pydub import AudioSegment
import difflib # 引入內建的模糊比對庫

class Speech:
    def __init__(self):
        self.device = -1
        self.sr = 48000
        
        devices = sd.query_devices()
        device_names = [d['name'] for d in devices]
        
        target_keywords = ["VB-Cable", "CABLE Input", "Virtual Cable"]
        
        best_match = None
        for keyword in target_keywords:
            matches = difflib.get_close_matches(keyword, device_names, n=1, cutoff=0.3)
            if matches:
                best_match = matches[0]
                break
        
        if best_match:
            for i, d in enumerate(devices):
                if d['name'] == best_match:
                    self.device = i
                    print(f"fuzzy detect succeed：connected to {best_match} (Index: {i})")
                    break
        
        if self.device == -1:
            print('Error: Cannot find VB Cable.')
            print("All detected devices：")
            for i, d in enumerate(device_names):
                print(f"{i}: {d}")
            exit()

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

    def speak_tw(self, text_input, voice='zh-TW-HsiaoChenNeural'):
        async def _run():
            tts = edge_tts.Communicate(text_input, voice=voice)
            buf = BytesIO()
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf

        buf = asyncio.run(_run())
        buf.seek(0)
        audio = AudioSegment.from_mp3(buf)
        audio = audio.set_frame_rate(self.sr).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        sd.play(samples, samplerate=self.sr, device=self.device)
        sd.wait()
