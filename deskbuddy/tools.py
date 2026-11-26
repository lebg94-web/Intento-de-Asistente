"""Herramientas que Claude puede usar: hora, clima, temporizadores y expresiones."""
import json
import threading
import urllib.parse
import urllib.request
from datetime import datetime

EXPRESSIONS = ["neutral", "happy", "sad", "surprised", "thinking", "sleepy", "angry", "love"]

TOOL_SCHEMAS = [
    {
        "name": "get_time",
        "description": "Devuelve la fecha y hora local actual.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "get_weather",
        "description": "Clima actual de una ciudad (temperatura, viento, condición).",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "Nombre de la ciudad"}},
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "name": "set_timer",
        "description": "Programa un temporizador. Al terminar, el robot avisa en voz alta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {"type": "integer", "description": "Duración en segundos"},
                "label": {"type": "string", "description": "Para qué es el temporizador"},
            },
            "required": ["seconds", "label"],
            "additionalProperties": False,
        },
    },
    {
        "name": "set_expression",
        "description": "Cambia la expresión de la cara del robot para acompañar lo que dices.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "enum": EXPRESSIONS}},
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
]

WMO = {0: "despejado", 1: "mayormente despejado", 2: "parcialmente nublado", 3: "nublado",
       45: "niebla", 48: "niebla", 51: "llovizna", 61: "lluvia ligera", 63: "lluvia",
       65: "lluvia fuerte", 71: "nieve ligera", 73: "nieve", 80: "chubascos", 95: "tormenta"}


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


class Tools:
    def __init__(self, on_expression, on_timer_done):
        self.on_expression = on_expression
        self.on_timer_done = on_timer_done

    def run(self, name: str, args: dict) -> str:
        try:
            return getattr(self, f"_{name}")(**args)
        except Exception as e:  # el error vuelve a Claude como resultado
            return f"Error: {e}"

    def _get_time(self) -> str:
        return datetime.now().strftime("%A %d de %B de %Y, %H:%M")

    def _get_weather(self, city: str) -> str:
        q = urllib.parse.quote(city)
        geo = _get_json(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=es")
        if not geo.get("results"):
            return f"No encontré la ciudad {city}."
        g = geo["results"][0]
        w = _get_json(
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={g['latitude']}&longitude={g['longitude']}&current_weather=true"
        )["current_weather"]
        cond = WMO.get(w["weathercode"], f"código {w['weathercode']}")
        return f"{g['name']}: {w['temperature']}°C, {cond}, viento {w['windspeed']} km/h."

    def _set_timer(self, seconds: int, label: str) -> str:
        t = threading.Timer(seconds, self.on_timer_done, args=(label,))
        t.daemon = True
        t.start()
        return f"Temporizador de {seconds} s para '{label}' iniciado."

    def _set_expression(self, expression: str) -> str:
        self.on_expression(expression)
        return "ok"
