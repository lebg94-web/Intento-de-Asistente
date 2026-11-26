"""Uso: python -m deskbuddy [--text] [--no-face]"""
import argparse
import queue
import sys

from .brain import Brain, NAME
from .tools import Tools
from .voice import Voice


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", action="store_true", help="usar teclado en vez de micrófono")
    p.add_argument("--no-face", action="store_true", help="sin ventana (solo terminal)")
    a = p.parse_args()

    face = None
    if not a.no_face:
        try:
            from .face import Face
            face = Face()
        except Exception as e:
            print(f"[cara] no disponible ({e}); continuando sin ventana.")

    voice = Voice(text_mode=a.text)
    pending: "queue.Queue[str]" = queue.Queue()
    set_expr = face.set_expression if face else (lambda e: None)
    tools = Tools(on_expression=set_expr, on_timer_done=lambda label: pending.put(label))
    brain = Brain(tools)

    def say(text, keep=False):
        if face:
            face.set_speaking(True)
        voice.speak(text)
        if face:
            face.set_speaking(False)
            if not keep:
                set_expr("neutral")

    def loop():
        say(f"Hola, soy {NAME}. ¿En qué te ayudo?")
        while True:
            while not pending.empty():
                set_expr("surprised")
                say(f"¡Tiempo! Se acabó el temporizador de {pending.get()}.")
            set_expr("listening")
            heard = voice.listen()
            if heard is None:
                break
            if not heard:
                continue
            if heard.lower().strip(" .!") in {"salir", "adiós", "adios"}:
                set_expr("sleepy")
                say("Hasta luego.")
                break
            set_expr("thinking")
            try:
                expr, reply = brain.ask(heard)
            except Exception as e:
                expr, reply = "sad", "Uy, tuve un problema para pensar eso."
                print(f"[error] {e}", file=sys.stderr)
            set_expr(expr)
            say(reply, keep=True)
        if face:
            face.root.after(0, face.root.destroy)

    if face:
        face.run(loop)
    else:
        loop()


if __name__ == "__main__":
    main()
