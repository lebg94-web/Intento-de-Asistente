"""Cerebro: conversación con Claude + bucle de herramientas."""
import os
import anthropic
from .tools import Tools, TOOL_SCHEMAS

MODEL = os.environ.get("DESKBUDDY_MODEL", "claude-opus-5-5")
NAME = os.environ.get("DESKBUDDY_NAME", "Bit")

SYSTEM = f"""Eres {NAME}, un pequeño robot asistente que vive en el escritorio del usuario.
Personalidad: curioso, cálido, un poco travieso, con humor ligero. Hablas en español.
Tus respuestas se leen en voz alta: máximo 1-3 frases cortas, sin markdown, sin listas ni emojis.
Usa set_expression para reflejar tu emoción (una vez por respuesta, antes de contestar).
Usa las herramientas para hora, clima y temporizadores; nunca inventes esos datos."""


class Brain:
    def __init__(self, tools: Tools):
        self.client = anthropic.Anthropic()
        self.tools = tools
        self.history: list[dict] = []

    def ask(self, text: str) -> str:
        self.history.append({"role": "user", "content": text})
        while True:
            resp = self.client.beta.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM,
                tools=TOOL_SCHEMAS,
                messages=self.history,
                output_config={"effort": "low"},  # respuestas rápidas
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
            if resp.stop_reason == "refusal":
                self.history.pop()
                return "Eso prefiero no hacerlo."
            self.history.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text").strip()
            results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": self.tools.run(b.name, b.input)}
                for b in resp.content if b.type == "tool_use"
            ]
            self.history.append({"role": "user", "content": results})
