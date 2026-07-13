import tkinter as tk
from tkinter import ttk
import threading
import tts


class TTSApp:
    def __init__(self, root):
        self.root = root
        self.speech = tts.Speech()
        self.pre = ''
        self.speaking = False
        self.rvc_pitch = tk.IntVar(value=-12)
        self.voice_model_names = {
            model.name: model.id
            for model in self.speech.available_voice_models()
        }
        self.speech.set_rvc_pitch(self.rvc_pitch.get())

        root.title("TTS Speaker")
        root.geometry("560x420")
        root.configure(bg="#1e1e2e")
        root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Consolas", 11), padding=6)
        style.configure("TLabel", font=("Consolas", 12),
                        background="#1e1e2e", foreground="#cdd6f4")
        style.configure("Status.TLabel", font=("Consolas", 10),
                        background="#1e1e2e", foreground="#6c7086")

        # Title
        ttk.Label(root, text="TTS Speaker", font=("Consolas", 18, "bold"),
                  foreground="#89b4fa").pack(pady=(15, 10))

        # Text input
        self.text_input = tk.Text(root, height=4, width=50,
                                  font=("Consolas", 12),
                                  bg="#313244", fg="#cdd6f4",
                                  insertbackground="#cdd6f4",
                                  relief="flat", padx=10, pady=8)
        self.text_input.pack(pady=10, padx=20)
        self.text_input.bind('<Return>', lambda e: self.on_enter())

        # Voice model selector
        model_frame = tk.Frame(root, bg="#1e1e2e")
        model_frame.pack(pady=(0, 8), padx=20, fill="x")

        ttk.Label(model_frame, text="Voice Model").pack(side="left", padx=(0, 8))
        self.model_select = ttk.Combobox(
            model_frame,
            values=list(self.voice_model_names.keys()),
            state="readonly",
            width=34,
        )
        self.model_select.current(0)
        self.model_select.pack(side="left", fill="x", expand=True)
        self.model_select.bind("<<ComboboxSelected>>", self.on_model_select)

        pitch_frame = tk.Frame(root, bg="#1e1e2e")
        pitch_frame.pack(pady=(0, 8), padx=20, fill="x")

        ttk.Label(pitch_frame, text="Transpose").pack(side="left", padx=(0, 8))
        self.pitch_spinbox = ttk.Spinbox(
            pitch_frame,
            from_=-24,
            to=24,
            textvariable=self.rvc_pitch,
            width=6,
            command=self.on_pitch_change,
        )
        self.pitch_spinbox.pack(side="left")
        ttk.Label(pitch_frame, text="semitones").pack(side="left", padx=(8, 0))
        self.pitch_spinbox.bind("<FocusOut>", self.on_pitch_change)
        self.pitch_spinbox.bind("<Return>", self.on_pitch_change)

        # Buttons
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(pady=5)

        self.speak_btn = ttk.Button(btn_frame, text="Speak(EN)",
                                    command=self.on_speak)
        self.speak_btn.pack(side="left", padx=5)

        self.speak_zh_btn = ttk.Button(btn_frame, text="Speak(ZH-TW)",
                                       command=self.on_speak_zh)
        self.speak_zh_btn.pack(side="left", padx=5)

        test_frame = tk.Frame(root, bg="#1e1e2e")
        test_frame.pack(pady=5)

        self.preview_btn = ttk.Button(test_frame, text="Test(EN)",
                                      command=self.on_preview)
        self.preview_btn.pack(side="left", padx=5)

        self.preview_zh_btn = ttk.Button(test_frame, text="Test(ZH-TW)",
                                         command=self.on_preview_zh)
        self.preview_zh_btn.pack(side="left", padx=5)

        self.repeat_btn = ttk.Button(btn_frame, text="Repeat",
                                     command=self.on_repeat)
        self.repeat_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Clear",
                                    command=self.on_clear)
        self.clear_btn.pack(side="left", padx=5)

        # Status
        self.status = ttk.Label(root, text="Ready", style="Status.TLabel", wraplength=460)
        self.status.pack(pady=(5, 10))

    def on_enter(self):
        self.on_speak()
        return 'break'

    def on_model_select(self, _event=None):
        model_name = self.model_select.get()
        model_id = self.voice_model_names.get(model_name)
        if model_id:
            self.speech.set_voice_model(model_id)
            self.status.config(text=f"Selected: {model_name}")

    def on_pitch_change(self, _event=None):
        try:
            pitch = max(-24, min(24, int(self.rvc_pitch.get())))
        except (tk.TclError, ValueError):
            pitch = -12
        self.rvc_pitch.set(pitch)
        self.speech.set_rvc_pitch(pitch)
        self.status.config(text=f"Transpose: {pitch} semitones")

    def on_speak(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text or self.speaking:
            return
        self.pre = text
        self._speak_async(text)

    def on_speak_zh(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text or self.speaking:
            return
        self.pre = text
        self._speak_async(text, zh=True)

    def on_preview(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text or self.speaking:
            return
        self._speak_async(text, preview=True)

    def on_preview_zh(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text or self.speaking:
            return
        self._speak_async(text, zh=True, preview=True)

    def on_repeat(self):
        if self.pre and not self.speaking:
            self._speak_async(self.pre)

    def on_clear(self):
        self.text_input.delete("1.0", tk.END)

    def _speak_async(self, text, zh=False, preview=False):
        self.speaking = True
        self.status.config(text="Testing..." if preview else "Speaking...")
        self._set_controls_state('disabled')

        def run():
            try:
                if preview and zh:
                    self.speech.preview_tw(text)
                elif preview:
                    self.speech.preview(text)
                elif zh:
                    self.speech.speak_tw(text)
                else:
                    self.speech.speak(text)
                status_text = "Ready"
            except Exception as exc:
                status_text = f"Error: {exc}"
            finally:
                self.root.after(0, lambda: self._finish_speaking(status_text))

        threading.Thread(target=run, daemon=True).start()

    def _finish_speaking(self, status_text):
        self.speaking = False
        self.status.config(text=status_text)
        self._set_controls_state('normal')
        self.model_select.config(state='readonly')

    def _set_controls_state(self, state):
        self.speak_btn.config(state=state)
        self.speak_zh_btn.config(state=state)
        self.preview_btn.config(state=state)
        self.preview_zh_btn.config(state=state)
        self.repeat_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.pitch_spinbox.config(state=state)
        self.model_select.config(state='disabled' if state == 'disabled' else 'readonly')
