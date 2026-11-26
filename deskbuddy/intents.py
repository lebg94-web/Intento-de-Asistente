"""Intenciones locales por reglas (gratis, sin modelo). Devuelve (expresion, respuesta) o None."""
import random
import re
import unicodedata

from .tools import Tools

UNITS = {"segundo": 1, "segundos": 1, "minuto": 60, "minutos": 60, "hora": 3600, "horas": 3600}
NUMS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "quince": 15, "veinte": 20,
        "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip(" .!?¿¡,")


def handle(text: str, tools: Tools):
    t = norm(text)

    m = re.search(r"(?:temporizador|alarma|avisame|recuerdame).*?(\d+|" + "|".join(NUMS) + r")\s+(segundos?|minutos?|horas?)", t)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else NUMS[m.group(1)]
        secs = n * UNITS[m.group(2)]
        tools.run("set_timer", {"seconds": secs, "label": f"{n} {m.group(2)}"})
        return "happy", f"Listo, te aviso en {n} {m.group(2)}."

    if re.search(r"\bque (hora|dia)\b|\bhora es\b|\bfecha\b", t):
        return "neutral", tools.run("get_time", {})

    m = re.search(r"clima (?:en|de)\s+(.+)|(?:temperatura|tiempo) (?:en|de)\s+(.+)|como esta el clima (?:en|de)\s+(.+)", t)
    if m:
        city = next(g for g in m.groups() if g)
        return "thinking", tools.run("get_weather", {"city": city})

    if re.search(r"\b(hola|buenas|hey)\b", t):
        return "happy", random.choice(["¡Hola! Aquí estoy.", "¡Hey! Qué bueno verte.", "¡Hola! ¿Qué hacemos?"])
    if re.search(r"\bgracias\b", t):
        return "love", random.choice(["¡De nada!", "Para eso estoy.", "Con gusto."])
    if re.search(r"como te llamas|quien eres", t):
        return "happy", "Soy Bit, tu robotito de escritorio."
    return None


FALLBACK = [
    ("thinking", "Mmm, eso no lo sé hacer sin un modelo de lenguaje. Pero puedo decirte la hora, el clima o poner un temporizador."),
    ("sad", "No te entendí bien. Prueba con la hora, el clima o un temporizador."),
]
