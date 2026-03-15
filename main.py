

import speech_recognition as sr
import pyttsx3
from translate import Translator
import time
import sys

GOODBYES_PL = {"bywaj", "do widzenia", "koniec", "zakończ", "żegnaj"}
GOODBYES_EN = {"good bye", "goodbye", "bye", "exit", "quit", "farewell"}

LANG_SWITCH_PL = {"polski", "po polsku", "zmień na polski", "język polski"}
LANG_SWITCH_EN = {"angielski", "po angielsku", "zmień na angielski", "english", "język angielski"}

PHRASE_TIMEOUT   = 5
LISTEN_TIMEOUT   = 8
PAUSE_THRESHOLD  = 0.9
ENERGY_THRESHOLD = 300


def init_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)
    return engine


def speak(engine, text, lang="pl"):

    voices = engine.getProperty("voices")
    chosen = None
    lang_code = "pl" if lang == "pl" else "en"
    for v in voices:
        if lang_code in v.id.lower() or lang_code in (v.name or "").lower():
            chosen = v.id
            break
    if chosen:
        engine.setProperty("voice", chosen)
    print(f"[TTS/{lang.upper()}] {text}")
    engine.say(text)
    engine.runAndWait()



def listen(recognizer, mic, lang_code="pl-PL", timeout=LISTEN_TIMEOUT, phrase_timeout=PHRASE_TIMEOUT):

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            print("  [MIC] Słucham...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_timeout)
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio, language=lang_code)
        return text.strip().lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"  [BŁĄD] Usługa Google Speech niedostępna: {e}")
        return None



def translate_text(text, from_lang, to_lang):
    try:
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"  [BŁĄD TŁUMACZENIA] {e}")
        return None



def ask_for_language(engine, recognizer, mic):
    while True:
        speak(engine, "Powiedz 'polski' lub 'angielski', aby wybrać język źródłowy.", lang="pl")
        text = listen(recognizer, mic, lang_code="pl-PL")
        if text is None:
            speak(engine, "Nie usłyszałem. Spróbuj ponownie.", lang="pl")
            continue

        if any(k in text for k in LANG_SWITCH_PL):
            speak(engine, "Wybrałeś język polski. Będę tłumaczyć na angielski.", lang="pl")
            return "pl"
        if any(k in text for k in LANG_SWITCH_EN):
            speak(engine, "Wybrałeś angielski. Będę tłumaczyć na polski.", lang="pl")
            return "en"

        speak(engine, "Nie rozpoznałem języka. Powiedz 'polski' lub 'angielski'.", lang="pl")



def main():
    print("=" * 55)
    print("  TRANSLATOR GŁOSOWY  PL <-> EN")
    print("  Powiedz 'bywaj' / 'good bye', aby zakończyć.")
    print("=" * 55)

    try:
        engine = init_tts()
    except Exception as e:
        print(f"[BŁĄD] Nie można uruchomić syntezatora mowy: {e}")
        sys.exit(1)

    try:
        recognizer = sr.Recognizer()
        recognizer.pause_threshold  = PAUSE_THRESHOLD
        recognizer.energy_threshold = ENERGY_THRESHOLD
        mic = sr.Microphone()
    except OSError as e:
        speak(engine, "Nie wykryto mikrofonu. Sprawdź podłączenie.", lang="pl")
        print(f"[BŁĄD MIKROFONU] {e}")
        sys.exit(1)

    source_lang = ask_for_language(engine, recognizer, mic)

    if source_lang == "pl":
        listen_lang = "pl-PL"
        translate_from, translate_to = "pl", "en"
        prompt_speak = "Mów po polsku."
        prompt_notunderstood = "Nie zrozumiałem. Spróbuj ponownie."
        prompt_transerr = "Błąd tłumaczenia."
    else:
        listen_lang = "en-US"
        translate_from, translate_to = "en", "pl"
        prompt_speak = "Speak in English."
        prompt_notunderstood = "I didn't understand. Please try again."
        prompt_transerr = "Translation error."

    speak(engine, prompt_speak, lang=source_lang)

    while True:
        text = listen(recognizer, mic, lang_code=listen_lang)

        if text is None:
            speak(engine, prompt_notunderstood, lang=source_lang)
            continue

        print(f"  [WEJŚCIE] {text}")

        if text in GOODBYES_PL or text in GOODBYES_EN:
            speak(engine, "Do widzenia! Goodbye!", lang="pl")
            break

        if any(k in text for k in LANG_SWITCH_PL | LANG_SWITCH_EN):
            source_lang = ask_for_language(engine, recognizer, mic)
            if source_lang == "pl":
                listen_lang = "pl-PL"
                translate_from, translate_to = "pl", "en"
                prompt_speak = "Mów po polsku."
                prompt_notunderstood = "Nie zrozumiałem. Spróbuj ponownie."
                prompt_transerr = "Błąd tłumaczenia."
            else:
                listen_lang = "en-US"
                translate_from, translate_to = "en", "pl"
                prompt_speak = "Speak in English."
                prompt_notunderstood = "I didn't understand. Please try again."
                prompt_transerr = "Translation error."
            speak(engine, prompt_speak, lang=source_lang)
            continue

        speak(engine, text, lang=source_lang)


        print("  [TŁUMACZENIE] Proszę czekać...")
        translated = translate_text(text, translate_from, translate_to)
        if translated is None:
            speak(engine, prompt_transerr, lang=source_lang)
            continue

        print(f"  [WYNIK] {translated}")
        speak(engine, translated, lang=translate_to)

        time.sleep(0.4)


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()