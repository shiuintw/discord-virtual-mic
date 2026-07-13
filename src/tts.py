import sounddevice as sd
import numpy as np
from gtts import gTTS
import edge_tts, asyncio
from io import BytesIO
from pydub import AudioSegment
import difflib # 引入內建的模糊比對庫
from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


@dataclass(frozen=True)
class VoiceModel:
    id: str
    name: str
    kind: str
    path: Path | None = None

class Speech:
    def __init__(self):
        self.device = -1
        self.sr = 48000
        self.project_root = Path(__file__).resolve().parents[1]
        self.voice_models = self._discover_voice_models()
        self.selected_model = self.voice_models[0]
        self.rvc_pitch = int(os.getenv("RVC_PITCH", "0"))
        
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

    def available_voice_models(self):
        return self.voice_models

    def set_voice_model(self, model_id):
        for model in self.voice_models:
            if model.id == model_id:
                self.selected_model = model
                return
        raise ValueError(f"Unknown voice model: {model_id}")

    def set_rvc_pitch(self, pitch):
        self.rvc_pitch = int(pitch)

    def speak(self, text_input, lang='en'):
        audio = self._synthesize(text_input, lang=lang)
        self._play_audio(audio, device=self.device)

    def preview(self, text_input, lang='en'):
        audio = self._synthesize(text_input, lang=lang)
        self._play_audio(audio, device=None)

    def _synthesize(self, text_input, lang='en'):
        tts = gTTS(text_input, lang=lang)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio = AudioSegment.from_mp3(buf)
        return self._apply_voice_model(audio)

    def speak_tw(self, text_input, voice='zh-TW-HsiaoChenNeural'):
        audio = self._synthesize_tw(text_input, voice=voice)
        self._play_audio(audio, device=self.device)

    def preview_tw(self, text_input, voice='zh-TW-HsiaoChenNeural'):
        audio = self._synthesize_tw(text_input, voice=voice)
        self._play_audio(audio, device=None)

    def _synthesize_tw(self, text_input, voice='zh-TW-HsiaoChenNeural'):
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
        return self._apply_voice_model(audio)

    def _play_audio(self, audio, device):
        audio = audio.set_frame_rate(self.sr).set_channels(1)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
        sd.play(samples, samplerate=self.sr, device=device)
        sd.wait()

    def _discover_voice_models(self):
        models = [VoiceModel(id="default", name="Default TTS", kind="default")]
        models_dir = self.project_root / "models"
        if not models_dir.exists():
            return models

        for path in sorted(models_dir.rglob("*.pth")):
            relative_path = path.relative_to(self.project_root)
            model_id = relative_path.as_posix()
            model_name = f"{path.parent.name} / {path.stem}"
            models.append(VoiceModel(
                id=model_id,
                name=model_name,
                kind="rvc",
                path=path,
            ))
        return models

    def _apply_voice_model(self, audio):
        if self.selected_model.kind == "default":
            return audio
        if self.selected_model.kind == "rvc":
            return self._convert_with_rvc(audio, self.selected_model)
        raise ValueError(f"Unsupported voice model type: {self.selected_model.kind}")

    def _convert_with_rvc(self, audio, model):
        with tempfile.TemporaryDirectory(prefix="discord-virtual-mic-rvc-") as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.wav"
            output_path = temp_path / "output.wav"

            audio = audio.set_frame_rate(self.sr).set_channels(1)
            audio.export(input_path, format="wav")

            command = self._build_rvc_command(input_path, output_path, model)
            subprocess.run(command, check=True)

            if not output_path.exists():
                raise RuntimeError(f"RVC command did not create output file: {output_path}")
            return AudioSegment.from_wav(output_path)

    def _build_rvc_command(self, input_path, output_path, model):
        command_template = os.getenv("RVC_INFER_COMMAND")
        if command_template:
            command = command_template.format(
                input=str(input_path),
                output=str(output_path),
                model=str(model.path),
                pitch=str(self.rvc_pitch),
            )
            return shlex.split(command)

        rvc_python = self.project_root / ".venv-rvc" / "bin" / "python"
        rvc_script = self.project_root / "scripts" / "rvc_infer.py"
        if rvc_python.exists() and rvc_script.exists():
            return [
                str(rvc_python),
                str(rvc_script),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
                "--model",
                str(model.path),
                "--device",
                os.getenv("RVC_DEVICE", "cpu:0"),
                "--version",
                os.getenv("RVC_VERSION", "v2"),
                "--pitch",
                str(self.rvc_pitch),
            ]

        raise RuntimeError(
            "RVC model selected, but no RVC backend is available. "
            "Run `python3.10 -m venv .venv-rvc` and install `requirements-rvc.txt`, "
            "or set RVC_INFER_COMMAND."
        )
