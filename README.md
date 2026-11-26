# DeskBuddy (Bit)

Asistente de escritorio con cara animada, voz y personalidad. **Gratis y local por defecto**: sin API de pago.

## Cómo evita gastar tokens
| Parte | Solución gratis |
|---|---|
| Hora, clima, temporizadores, saludos | Reglas locales (`intents.py`), sin modelo. Clima vía Open-Meteo (API gratuita, sin llave) |
| Conversación libre | [Ollama](https://ollama.com) con un modelo local (`ollama pull qwen2.5:3b`) |
| Sin Ollama | Sigue funcionando con reglas y respuestas enlatadas |
| Voz a texto | Vosk offline (descarga `vosk-model-small-es` y ponlo en `./model`) |
| Texto a voz | pyttsx3 offline |
| Claude (opcional, de pago) | `DESKBUDDY_BRAIN=claude` |

## Uso
```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b        # opcional, para charla libre
python -m deskbuddy --text    # teclado
python -m deskbuddy           # micrófono + cara
```
Variables: `DESKBUDDY_BRAIN` (ollama|rules|claude), `DESKBUDDY_MODEL`, `DESKBUDDY_STT` (vosk|google), `DESKBUDDY_NAME`.
Requiere `tkinter` (Linux: `sudo apt install python3-tk`).
