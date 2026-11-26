"""Cara animada con tkinter: parpadeo, mirada, expresiones y boca al hablar."""
import math
import random
import time
import tkinter as tk

W, H = 480, 320
BG, FG, ACCENT = "#0b1020", "#7fe7ff", "#ff8fb1"

# expresión -> (alto de ojo 0..1, curva de boca -1..1, inclinación de ceja)
LOOKS = {
    "neutral":   (1.0,  0.2,  0),
    "happy":     (0.8,  1.0, -4),
    "sad":       (0.8, -0.8, 12),
    "surprised": (1.3,  0.0, -8),
    "thinking":  (0.7,  0.0,  6),
    "sleepy":    (0.3,  0.0,  0),
    "angry":     (0.7, -0.5, 16),
    "love":      (1.0,  1.0,  0),
    "listening": (1.15, 0.1, -3),
}


class Face:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bit")
        self.c = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0)
        self.c.pack()
        self.expression = "neutral"
        self.speaking = False
        self._blink_at = time.time() + 2
        self._gaze = (0.0, 0.0)
        self._gaze_at = 0.0
        self._cur_h = 1.0
        self._cur_m = 0.2

    # --- API thread-safe (solo asigna atributos) ---
    def set_expression(self, name: str):
        self.expression = name if name in LOOKS else "neutral"

    def set_speaking(self, v: bool):
        self.speaking = v

    def run(self, worker):
        import threading
        threading.Thread(target=worker, daemon=True).start()
        self._tick()
        self.root.mainloop()

    def _tick(self):
        now = time.time()
        eye_h, mouth, brow = LOOKS[self.expression]
        self._cur_h += (eye_h - self._cur_h) * 0.25
        self._cur_m += (mouth - self._cur_m) * 0.25
        if now > self._blink_at + 0.15:
            self._blink_at = now + random.uniform(2, 5)
        blink = now >= self._blink_at and now < self._blink_at + 0.15
        if now > self._gaze_at:
            self._gaze = (random.uniform(-1, 1), random.uniform(-0.6, 0.6))
            self._gaze_at = now + random.uniform(1, 3)

        c = self.c
        c.delete("all")
        for cx in (150, 330):
            h = 70 * self._cur_h * (0.08 if blink else 1)
            cy = 120
            c.create_oval(cx - 45, cy - h, cx + 45, cy + h, fill=FG, outline="")
            if not blink and self.expression != "sleepy":
                px, py = cx + self._gaze[0] * 14, cy + self._gaze[1] * 14
                c.create_oval(px - 14, py - 14, px + 14, py + 14, fill=BG, outline="")
            side = -1 if cx < 240 else 1
            c.create_line(cx - 45, 50 + brow * side * -1, cx + 45, 50 + brow * side, fill=FG, width=6, capstyle="round")
        # boca
        my = 240
        if self.speaking:
            o = 8 + 14 * abs(math.sin(now * 14))
            c.create_oval(210, my - o, 270, my + o, fill=ACCENT, outline="")
        else:
            k = self._cur_m * 25
            c.create_line(195, my, 240, my + k, 285, my, smooth=True, fill=ACCENT, width=8, capstyle="round")
        if self.expression == "love":
            c.create_text(240, 40, text="♥", fill=ACCENT, font=("Arial", 28))
        self.root.after(33, self._tick)
