import tkinter as tk
from tkinter import ttk
import threading
import tts


class TTSApp:
    def __init__(self, root):
        self.speech = tts.Speech()
        self.pre = ''
        self.speaking = False

        root.title("TTS Speaker")
        root.geometry("500x300")
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

        # Buttons
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(pady=5)

        self.speak_btn = ttk.Button(btn_frame, text="Speak",
                                    command=self.on_speak)
        self.speak_btn.pack(side="left", padx=5)

        self.repeat_btn = ttk.Button(btn_frame, text="Repeat",
                                     command=self.on_repeat)
        self.repeat_btn.pack(side="left", padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Clear",
                                    command=self.on_clear)
        self.clear_btn.pack(side="left", padx=5)

        # Status
        self.status = ttk.Label(root, text="Ready", style="Status.TLabel")
        self.status.pack(pady=(5, 10))

    def on_enter(self):
        self.on_speak()
        return 'break'

    def on_speak(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text or self.speaking:
            return
        self.pre = text
        self._speak_async(text)

    def on_repeat(self):
        if self.pre and not self.speaking:
            self._speak_async(self.pre)

    def on_clear(self):
        self.text_input.delete("1.0", tk.END)

    def _speak_async(self, text):
        self.speaking = True
        self.status.config(text="Speaking...")
        self.speak_btn.config(state='disabled')

        def run():
            self.speech.speak(text)
            self.speaking = False
            self.status.config(text="Ready")
            self.speak_btn.config(state='normal')

        threading.Thread(target=run, daemon=True).start()