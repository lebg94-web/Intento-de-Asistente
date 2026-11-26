"""Cerebro con varios backends. Por defecto GRATIS: reglas locales + Ollama (modelo local).

DESKBUDDY_BRAIN = ollama (defecto) | rules (sin modelo) | claude (de pago, opcional)
"""
import json
import os
import random
import re
import urllib.request

from .intents import FALLBACK, handle
from .tools import Tools, TOOL_SCHEMAS, EXPRESSIONS

NAME = os.environ.get("DESKBUDDY_NAME", "Bit")
BACKEND = os.environ.get("DESKBUDDY_BRAIN", "ollama")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("DESKBUDDY_MODEL", "qwen2.5:3b")
CLAUDE_MODEL = os.environ.get("DESKBUDDY_CLAUDE_MODEL", "claude-opus-5-5")

SYSTEM = f"""Eres {NAME}, un pequeño robot de escritorio. Personalidad: curioso, cálido, un poco travieso.
Hablas en español. Respondes en 1-2 frases cortas, sin markdown, sin listas, sin emojis.
Empieza SIEMPRE con una etiqueta de emoción entre corchetes: una de {', '.join(EXPRESSIONS)}. Ej: [happy] ¡Qué buena idea!"""


class Brain:
    def __init__(self, tools: Tools):
        self.tools = tools
        self.history: list[dict] = []
        self.backend = BACKEND
        if self.backend == "ollama" and not self._ollama_up():
            print("[cerebro] Ollama no responde; usando solo reglas locales (gratis).")
            self.backend = "rules"
        if self.backend == "claude":
            import anthropic
            self.client = anthropic.Anthropic()
        print(f"[cerebro] backend: {self.backend}")

    def _ollama_up(self) -> bool:
        try:
            urllib.request.urlopen(OLLAMA_URL, timeout=2)
            return True
        except Exception:
            return False

    def ask(self, text: str) -> tuple[str, str]:
        """Devuelve (expresion, respuesta)."""
        local = handle(text, self.tools)
        if local:
            return local
        if self.backend == "ollama":
            return self._ollama(text)
        if self.backend == "claude":
            return self._claude(text)
        return random.choice(FALLBACK)

    def _parse(self, raw: str) -> tuple[str, str]:
        m = re.match(r"\s*\[(\w+)\]\s*(.*)", raw, re.S)
        if m and m.group(1) in EXPRESSIONS:
            return m.group(1), m.group(2).strip()
        return "neutral", raw.strip()

    def _ollama(self, text: str):
        self.history.append({"role": "user", "content": text})
        self.history = self.history[-12:]
        body = json.dumps({"model": OLLAMA_MODEL, "stream": False,
                           "messages": [{"role": "system", "content": SYSTEM}, *self.history],
                           "options": {"num_predict": 120}}).encode()
        req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", body, {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = json.load(r)["message"]["content"]
        self.history.append({"role": "assistant", "content": raw})
        return self._parse(raw)

    def _claude(self, text: str):
        self.history.append({"role": "user", "content": text})
        resp = self.client.messages.create(
            model=CLAUDE_MODEL, max_tokens=300, system=SYSTEM, messages=self.history,
            output_config={"effort": "low"})
        raw = "".join(b.text for b in resp.content if b.type == "text")
        self.history.append({"role": "assistant", "content": raw})
        return self._parse(raw)
