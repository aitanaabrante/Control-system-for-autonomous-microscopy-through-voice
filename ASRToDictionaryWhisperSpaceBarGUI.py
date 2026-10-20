import tkinter as tk
from tkinter import filedialog
import sounddevice as sd
import numpy as np
import whisper
from InitialConnection import connect
from DictionaryCode import Dictionary
import threading
import queue
import warnings
import re
import time
import json
import os
from contextlib import redirect_stdout

# =====================================================
# CONFIG
# =====================================================

CONFIG_FILE = "config_paths.json"

DEFAULT_CONFIG = {
    "script_folder": "",
    "template_folder": "",
    "image_folder": ""
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

for k, v in DEFAULT_CONFIG.items():
    if k not in config:
        config[k] = v

save_config(config)

# =====================================================
# DERIVED PATHS
# =====================================================

def build_paths():
    global LOAD_INITIAL_SCRIPT, SAVE_SCRIPT, LOAD_NEW_SCRIPT
    global ACQUIRE_SCRIPT, SAVE_IMAGE_SCRIPT
    global LRP_FILE, IMAGE_FOLDER

    LOAD_INITIAL_SCRIPT = os.path.join(config["script_folder"], "Example_LoadExperiment.py")
    SAVE_SCRIPT = os.path.join(config["script_folder"], "Example_SaveExperiment.py")
    LOAD_NEW_SCRIPT = os.path.join(config["script_folder"], "Example_LoadNewExperiment.py")
    ACQUIRE_SCRIPT = os.path.join(config["script_folder"], "Example_AcquireSingleImage.py")
    SAVE_IMAGE_SCRIPT = os.path.join(config["script_folder"], "Example_SaveCurrentSelectedImage.py")

    LRP_FILE = os.path.join(
        config["template_folder"],
        "{ScanningTemplate}NewSpectralDetectorExperiment.lrp"
    )

    IMAGE_FOLDER = config["image_folder"]

build_paths()

# =====================================================
# WHISPER
# =====================================================

fs = 16000
canales = 1

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

print("Loading Whisper Model...")
model = whisper.load_model("small")

audio_queue = queue.Queue()
grabando = False
frames = []

# =====================================================
# UI
# =====================================================

BG = "#0f172a"
CARD = "#111827"
TEXT = "#e5e7eb"
ACCENT = "#22c55e"
LISTEN = "#3b82f6"
PROCESS = "#f59e0b"

root = tk.Tk()
root.title("Voice Assistant")
root.geometry("750x700")
root.configure(bg=BG)

estado_var = tk.StringVar(value="READY")
texto_var = tk.StringVar(value="")

# =====================================================
# HEADER
# =====================================================

tk.Label(
    root,
    text="🎙 Voice Assistant",
    bg=BG,
    fg=TEXT,
    font=("Arial", 20, "bold")
).pack(pady=10)

estado_label = tk.Label(
    root,
    textvariable=estado_var,
    bg=BG,
    fg=ACCENT,
    font=("Arial", 14, "bold")
)
estado_label.pack(pady=5)

# =====================================================
# TOP PATH BAR (3 ROUTES ALWAYS VISIBLE)
# =====================================================

top_frame = tk.Frame(root, bg=BG)
top_frame.pack(fill="x", padx=10, pady=10)

def create_path_row(parent, label, key):

    row = tk.Frame(parent, bg=BG)
    row.pack(fill="x", pady=3)

    tk.Label(
        row,
        text=label,
        bg=BG,
        fg=TEXT,
        width=25,
        anchor="w"
    ).pack(side="left")

    entry = tk.Entry(row)
    entry.insert(0, config.get(key, ""))
    entry.pack(side="left", fill="x", expand=True)

    def browse():
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, tk.END)
            entry.insert(0, folder)

            config[key] = folder
            save_config(config)
            build_paths()

    tk.Button(
        row,
        text="Browse",
        command=browse,
        bg="#1f2937",
        fg="white"
    ).pack(side="left", padx=5)

    return entry

script_entry = create_path_row(top_frame, "Python Scripts Folder", "script_folder")
template_entry = create_path_row(top_frame, "Template Folder (.lrp)", "template_folder")
image_entry = create_path_row(top_frame, "Image Output Folder", "image_folder")

# =====================================================
# RECOGNIZED TEXT
# =====================================================

frame_texto = tk.Frame(root, bg=CARD)
frame_texto.pack(fill="x", padx=15, pady=10)

tk.Label(frame_texto, text="Recognized:", bg=CARD, fg="#9ca3af").pack(anchor="w")

tk.Label(
    frame_texto,
    textvariable=texto_var,
    bg=CARD,
    fg=TEXT,
    wraplength=700,
    justify="left",
    font=("Arial", 11),
).pack(anchor="w", padx=10, pady=5)

# =====================================================
# OUTPUT 
# =====================================================

frame_output = tk.Frame(root, bg=CARD)
frame_output.pack(fill="both", expand=True, padx=15, pady=10)

tk.Label(frame_output, text="Output:", bg=CARD, fg="#9ca3af").pack(anchor="w")

resultado_text = tk.Text(
    frame_output,
    bg="#020617",
    fg="#22c55e",
    wrap="word",
    font=("Consolas", 10)
)
resultado_text.pack(fill="both", expand=True)

# =====================================================
# REAL-TIME STREAMING REDIRECT
# =====================================================

class LiveRedirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert("end", text)
        self.widget.see("end")
        self.widget.update_idletasks()  # 🔥 live render

    def flush(self):
        pass

# =====================================================
# COMMAND EXECUTION
# =====================================================

def ejecutar_comando(cmd):

    redirector = LiveRedirect(resultado_text)

    try:
        with redirect_stdout(redirector):
            Dictionary[cmd]()

    except Exception as e:
        resultado_text.insert("end", f"\nERROR: {e}\n")
        resultado_text.see("end")

# =====================================================
# AUDIO SYSTEM
# =====================================================

def callback(indata, frames_count, time_info, status):
    if grabando:
        audio_queue.put(indata.copy())

def empezar_grabacion(event=None):
    global grabando, frames
    if not grabando:
        estado_var.set("🎤 LISTENING")
        estado_label.config(fg=LISTEN)
        texto_var.set("")
        resultado_text.delete("1.0", tk.END)
        grabando = True
        frames = []

def parar_grabacion(event=None):
    global grabando
    if grabando:
        estado_var.set("⏳ PROCESSING")
        estado_label.config(fg=PROCESS)
        grabando = False

# =====================================================
# AUDIO LOOP
# =====================================================

def audio_loop():
    global frames

    connect()

    with sd.InputStream(samplerate=fs, channels=canales, callback=callback):
        while True:

            if not grabando:
                time.sleep(0.05)
                continue

            while grabando:
                time.sleep(0.01)

            while not audio_queue.empty():
                frames.append(audio_queue.get())

            if len(frames) == 0:
                continue

            audio = np.concatenate(frames, axis=0)
            audio = np.squeeze(audio)

            result = model.transcribe(audio, language="en")
            texto = result["text"].lower()
            texto = re.sub(r"[^\w\s]", "", texto).strip()

            texto_var.set(texto)

            if "stop" in texto and "program" in texto:

                estado_var.set("GOODBYE")
                estado_label.config(fg="#ef4444")

                texto_var.set(texto)

                resultado_text.insert(tk.END, "\nBye. Voice System shutting down...\n")
                resultado_text.see(tk.END)

                root.quit()
                break

            comandos_encontrados = []

            for comando in Dictionary:

                palabras = comando.split()

                if all(p in texto for p in palabras):

                    posiciones = [texto.find(p) for p in palabras]

                    comandos_encontrados.append(
                        (min(posiciones), comando)
                    )

            comandos_encontrados.sort(key=lambda x: x[0])

            if comandos_encontrados:

                for _, comando in comandos_encontrados:
                    root.after(0, ejecutar_comando, comando)

            else:

                resultado_text.insert("end", "Command not recognized\n")
                resultado_text.see("end")

            estado_var.set("READY")
            estado_label.config(fg=ACCENT)

# =====================================================
# BINDINGS
# =====================================================

root.bind("<KeyPress-space>", empezar_grabacion)
root.bind("<KeyRelease-space>", parar_grabacion)
root.focus_set()

# =====================================================
# THREAD
# =====================================================

threading.Thread(target=audio_loop, daemon=True).start()

root.mainloop()