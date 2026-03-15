

import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import pyttsx3
from translate import Translator
import time
from datetime import datetime

GOODBYES    = {"bywaj", "do widzenia", "koniec", "zakończ",
               "good bye", "goodbye", "bye", "exit", "quit"}
SWITCH_PL   = {"polski", "po polsku", "język polski", "zmień na polski"}
SWITCH_EN   = {"angielski", "po angielsku", "english", "język angielski", "zmień na angielski"}

PAUSE_THRESHOLD  = 0.9
LISTEN_TIMEOUT   = 10
PHRASE_TIMEOUT   = 6
ENERGY_THRESHOLD = 300


class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Translator Głosowy  PL ↔ EN")
        self.geometry("560x500")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self.protocol("WM_DELETE_WINDOW", self._quit)

        self.source_lang = "pl"
        self.running     = True

        self.engine     = None
        self.recognizer = None
        self.mic        = None

        self._build_ui()
        self.after(200, self._start)


    def _build_ui(self):
        BG   = "#1e1e2e"
        CARD = "#16213e"
        FG   = "#c0c0e0"
        FG2  = "#8888aa"
        MONO = ("Consolas", 10)
        SANS = ("Segoe UI", 10)

        hdr = tk.Frame(self, bg="#2a2a3e", pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎙  Translator Głosowy  PL ↔ EN",
                 bg="#2a2a3e", fg=FG,
                 font=("Segoe UI", 13, "bold")).pack()
        tk.Label(hdr, text="Steruj wyłącznie głosem",
                 bg="#2a2a3e", fg=FG2,
                 font=("Segoe UI", 9)).pack()

        body = tk.Frame(self, bg=BG, padx=16, pady=12)
        body.pack(fill="both", expand=True)

        mode_frame = tk.Frame(body, bg=CARD, pady=8, padx=12)
        mode_frame.pack(fill="x", pady=(0, 10))

        tk.Label(mode_frame, text="Aktywny tryb:",
                 bg=CARD, fg=FG2, font=SANS).pack(side="left")
        self.mode_var = tk.StringVar(value="🇵🇱  Polski  →  🇬🇧 English")
        self.mode_lbl = tk.Label(mode_frame, textvariable=self.mode_var,
                                 bg=CARD, fg="#a0a0ff",
                                 font=("Segoe UI", 11, "bold"))
        self.mode_lbl.pack(side="left", padx=12)

        io = tk.Frame(body, bg=BG)
        io.pack(fill="x", pady=(0, 10))
        io.columnconfigure(1, weight=1)

        for row, label, attr, color in [
            (0, "Rozpoznano:", "input_var",  "#c0c0e0"),
            (1, "Tłumaczenie:", "output_var", "#4ade80"),
        ]:
            tk.Label(io, text=label, bg=BG, fg=FG2,
                     font=SANS, anchor="w").grid(
                row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Entry(io, textvariable=var, state="readonly",
                     bg="#0f172a", fg=color, readonlybackground="#0f172a",
                     insertbackground=color, relief="flat", bd=4,
                     font=MONO).grid(row=row, column=1, sticky="ew", pady=4)

        sf = tk.Frame(body, bg="#0f172a", pady=6, padx=10)
        sf.pack(fill="x", pady=(0, 10))
        self.dot = tk.Label(sf, text="●", fg="#4ade80",
                            bg="#0f172a", font=("Segoe UI", 13))
        self.dot.pack(side="left")
        self.status_var = tk.StringVar(value="Uruchamianie…")
        tk.Label(sf, textvariable=self.status_var,
                 bg="#0f172a", fg="#6a9fb5",
                 font=MONO).pack(side="left", padx=8)

        tk.Label(body, text="Dziennik:", bg=BG, fg=FG2,
                 font=SANS).pack(anchor="w")
        self.log = scrolledtext.ScrolledText(
            body, height=9, bg="#0a0f1a", fg="#8888aa",
            insertbackground="#8888aa", relief="flat", bd=4,
            font=("Consolas", 9), state="disabled", wrap="word"
        )
        self.log.pack(fill="both", expand=True)
        for tag, color in [("ok","#4ade80"),("info","#60a5fa"),
                           ("warn","#fbbf24"),("err","#f87171"),
                           ("time","#3a3a55")]:
            self.log.tag_config(tag, foreground=color)


    def _log(self, tag, label, msg):
        def _do():
            ts = datetime.now().strftime("[%H:%M:%S]")
            self.log.configure(state="normal")
            self.log.insert("end", ts + " ", "time")
            self.log.insert("end", f"{label:<6}", tag)
            self.log.insert("end", f"  {msg}\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _do)

    def _set_status(self, color, text):
        self.after(0, lambda: (
            self.dot.configure(fg=color),
            self.status_var.set(text)
        ))

    def _set_mode(self):
        if self.source_lang == "pl":
            self.after(0, lambda: self.mode_var.set("🇵🇱  Polski  →  🇬🇧 English"))
        else:
            self.after(0, lambda: self.mode_var.set("🇬🇧  English  →  🇵🇱 Polski"))

    def _set_input(self, t):
        self.after(0, lambda: self.input_var.set(t))

    def _set_output(self, t):
        self.after(0, lambda: self.output_var.set(t))


    def _start(self):
        threading.Thread(target=self._init_and_run, daemon=True).start()

    def _init_and_run(self):
        # TTS
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 155)
            self.engine.setProperty("volume", 1.0)
            self._log("ok", "TTS", "Silnik mowy gotowy")
        except Exception as e:
            self._log("err", "TTS", f"Błąd TTS: {e}")
            self._set_status("#f87171", "Błąd TTS!")
            return

        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.pause_threshold  = PAUSE_THRESHOLD
            self.recognizer.energy_threshold = ENERGY_THRESHOLD
            self.mic = sr.Microphone()
            self._log("ok", "MIC", "Mikrofon wykryty")
        except OSError as e:
            self._log("err", "MIC", f"Brak mikrofonu: {e}")
            self._set_status("#f87171", "Brak mikrofonu!")
            self._speak("Nie wykryto mikrofonu. Sprawdź podłączenie.", "pl")
            return

        self._ask_language()

        self._main_loop()


    def _ask_language(self):
        self._set_status("#fbbf24", "Wybierz język głosem…")
        while self.running:
            self._speak("Powiedz 'polski' lub 'angielski', aby wybrać język.", "pl")
            self._log("info", "LANG", "Oczekuję na wybór języka…")
            text = self._listen_once("pl-PL")

            if text is None:
                self._speak("Nie usłyszałem. Powiedz 'polski' lub 'angielski'.", "pl")
                continue

            if any(k in text for k in SWITCH_PL):
                self.source_lang = "pl"
                self._set_mode()
                self._speak("Wybrałeś język polski. Tłumaczę na angielski.", "pl")
                self._log("ok", "LANG", "Tryb: PL → EN")
                return

            if any(k in text for k in SWITCH_EN):
                self.source_lang = "en"
                self._set_mode()
                self._speak("English selected. I will translate to Polish.", "en")
                self._log("ok", "LANG", "Tryb: EN → PL")
                return

            self._speak("Nie rozpoznałem. Powiedz 'polski' lub 'angielski'.", "pl")


    def _main_loop(self):
        while self.running:
            lang  = self.source_lang
            lcode = "pl-PL" if lang == "pl" else "en-US"
            t_to  = "en"    if lang == "pl" else "pl"

            self._set_status("#4ade80", "Nasłuchuję…")
            self._log("info", "MIC", "Słucham…")

            text = self._listen_once(lcode)

            if text is None:
                self._speak(
                    "Nie zrozumiałem. Spróbuj ponownie." if lang == "pl"
                    else "I didn't understand. Please try again.",
                    lang
                )
                continue

            self._log("ok", "STT", f'"{text}"')
            self._set_input(text)
            self._set_output("")

            if text in GOODBYES:
                self._speak("Do widzenia! Goodbye!", "pl")
                self._log("warn", "EXIT", "Zakończono na komendę głosową")
                self.after(1000, self._quit)
                return

            if any(k in text for k in SWITCH_PL):
                self.source_lang = "pl"
                self._set_mode()
                self._speak("Przełączono na język polski.", "pl")
                self._log("info", "LANG", "Tryb: PL → EN")
                continue
            if any(k in text for k in SWITCH_EN):
                self.source_lang = "en"
                self._set_mode()
                self._speak("Switched to English.", "en")
                self._log("info", "LANG", "Tryb: EN → PL")
                continue

            self._speak(text, lang)

            self._set_status("#60a5fa", "Tłumaczę…")
            self._log("info", "API", "Tłumaczenie…")
            translated = self._translate(text, lang, t_to)

            if translated is None:
                self._speak(
                    "Błąd tłumaczenia." if lang == "pl" else "Translation error.",
                    lang
                )
            else:
                self._log("ok", "OUT", f'"{translated}"')
                self._set_output(translated)
                self._speak(translated, t_to)

            time.sleep(0.3)


    def _listen_once(self, lang_code):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIMEOUT
                )
            return self.recognizer.recognize_google(
                audio, language=lang_code
            ).strip().lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            self._log("err", "STT", f"Google API niedostępne: {e}")
            return None
        except Exception as e:
            self._log("err", "MIC", str(e))
            return None

    def _translate(self, text, from_lang, to_lang):
        try:
            return Translator(from_lang=from_lang, to_lang=to_lang).translate(text)
        except Exception as e:
            self._log("err", "TRANSL", str(e))
            return None

    def _speak(self, text, lang="pl"):
        if self.engine is None:
            return
        try:
            voices = self.engine.getProperty("voices")
            lc = "pl" if lang == "pl" else "en"
            for v in voices:
                if lc in v.id.lower() or lc in (v.name or "").lower():
                    self.engine.setProperty("voice", v.id)
                    break
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self._log("err", "TTS", str(e))


    def _quit(self):
        self.running = False
        self._log("warn", "EXIT", "Zamykanie…")
        self.after(400, self.destroy)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()