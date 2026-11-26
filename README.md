# DeskBuddy (Bit)

Asistente de escritorio con IA: cara animada, voz, personalidad y herramientas simples
(hora, clima, temporizadores). Cerebro: Claude. Pensado para correr primero en tu PC y
luego migrar a hardware (Raspberry Pi / ESP32).

## Uso
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python -m deskbuddy            # voz + cara
python -m deskbuddy --text     # escribes en vez de hablar
python -m deskbuddy --no-face  # sin ventana
```
Variables: `DESKBUDDY_MODEL` (por defecto `claude-opus-5-5`; prueba `claude-haiku-5-5` para más rapidez), `DESKBUDDY_NAME`.
Requiere `tkinter` (en Linux: `sudo apt install python3-tk`) y `portaudio` para PyAudio.

## Estructura
- `brain.py` conversación con Claude y bucle de herramientas
- `tools.py` hora, clima (Open-Meteo), temporizadores, expresiones
- `face.py` cara animada (parpadeo, mirada, boca al hablar)
- `voice.py` micrófono (SpeechRecognition) y voz (pyttsx3)

## Siguientes pasos
Hardware: ESP32 + pantalla + servos de cabeza; `face.py` se reemplaza por la pantalla y
`set_expression` también moverá servos.
