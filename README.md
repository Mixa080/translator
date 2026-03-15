# 🎙 Hands-Free Voice Translator — Polish ↔ English

A fully voice-controlled translation app built in Python. No keyboard, no mouse — just speak.
The Tkinter window acts as a live display only; everything is controlled by voice commands.

---

## How It Works

1. **Launch** the app — it immediately asks you (via speech) to choose a language
2. **Say** `"polski"` or `"angielski"` to set the translation direction
3. **Speak** a sentence — the app repeats it back, translates it, and reads the result aloud
4. **Switch language** at any time by saying `"polski"` or `"angielski"`
5. **Say** `"bywaj"` or `"good bye"` to exit — no need to touch the keyboard

---

## Features

- 🎤 Continuous voice recognition via Google Speech API
- 🌐 Automatic translation (Polish → English or English → Polish)
- 🔊 Text-to-speech output with language-matched voice
- 🖥️ Live Tkinter display — recognized text, translation, status, event log
- ⚠️ Graceful error handling — microphone missing, API unavailable, unrecognized speech

---

## Voice Commands

| Say | Action |
|-----|--------|
| `polski` / `po polsku` | Switch to Polish → English mode |
| `angielski` / `english` | Switch to English → Polish mode |
| `bywaj` / `do widzenia` | Exit the app |
| `good bye` / `goodbye` | Exit the app |

---

## Requirements

- Python 3.8+
- Microphone and speakers
- Internet connection (Google Speech Recognition + translation)

### Install dependencies

```bash
pip install SpeechRecognition translate pyttsx3 pyaudio
```

> **Windows users:** if `pyaudio` fails to install, try:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

> **Linux users:**
> ```bash
> sudo apt install portaudio19-dev python3-pyaudio
> pip install pyaudio
> ```

---

## Run

```bash
python translator_handsfree.py
```

---

## Project Structure

```
.
├── translator_handsfree.py   # Main app — hands-free, Tkinter display
├── translator_glosowy.py     # Console-only version (no GUI)
└── README.md
```

---

## Libraries Used

| Library | Purpose |
|---------|---------|
| `SpeechRecognition` | Captures and recognizes microphone input via Google API |
| `translate` | Text translation between Polish and English |
| `pyttsx3` | Offline text-to-speech engine |
| `pyaudio` | Audio stream handling for the microphone |
| `tkinter` | Built-in Python GUI — display only, no interaction needed |

---

## Known Limitations

- Speech recognition requires an active internet connection (Google API)
- Translation quality depends on the `translate` library (MyMemory backend) — short phrases work best
- TTS voice quality depends on voices installed in the operating system
- Background noise may affect recognition accuracy — adjust `ENERGY_THRESHOLD` in the source if needed

---

## Configuration

You can tune recognition behavior by editing the constants at the top of the file:

```python
PAUSE_THRESHOLD  = 0.9   # seconds of silence = end of sentence
LISTEN_TIMEOUT   = 10    # max seconds waiting for speech to start
PHRASE_TIMEOUT   = 6     # max length of a single utterance
ENERGY_THRESHOLD = 300   # microphone sensitivity (lower = more sensitive)
```

---

## Academic Context

This project was developed as part of a university exercise exploring voice interfaces and AI libraries in Python, covering:
- speech recognition pipelines
- automatic translation APIs
- text-to-speech synthesis
- error handling in real-time audio applications
