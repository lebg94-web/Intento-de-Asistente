"""Voz: escuchar (STT) y hablar (TTS). Cae a texto si no hay micrófono/librerías."""


class Voice:
    def __init__(self, text_mode: bool = False):
        self.mic = None
        self.tts = None
        if not text_mode:
            try:
                import speech_recognition as sr
                self.sr = sr
                self.rec = sr.Recognizer()
                self.mic = sr.Microphone()
                with self.mic as src:
                    self.rec.adjust_for_ambient_noise(src, duration=0.8)
            except Exception as e:
                print(f"[voz] micrófono no disponible ({e}); usando teclado.")
                self.mic = None
        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 175)
            for v in self.tts.getProperty("voices"):
                if "es" in (v.id + v.name).lower() or "spanish" in v.name.lower():
                    self.tts.setProperty("voice", v.id)
                    break
        except Exception as e:
            print(f"[voz] TTS no disponible ({e}); solo texto.")

    def listen(self) -> str | None:
        if self.mic is None:
            try:
                return input("Tú: ").strip() or None
            except EOFError:
                return None
        with self.mic as src:
            try:
                audio = self.rec.listen(src, timeout=10, phrase_time_limit=15)
            except self.sr.WaitTimeoutError:
                return ""
        try:
            return self.rec.recognize_google(audio, language="es-MX")
        except self.sr.UnknownValueError:
            return ""

    def speak(self, text: str):
        print(f"Bit: {text}")
        if self.tts:
            self.tts.say(text)
            self.tts.runAndWait()
