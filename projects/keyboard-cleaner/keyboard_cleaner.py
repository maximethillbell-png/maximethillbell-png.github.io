#!/usr/bin/env python3
"""
Keyboard Cleaner
Désactive le clavier pour le nettoyer en toute tranquillité.
Cliquez sur la fenêtre pour réactiver le clavier.
"""

import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

# Auto-installation de pynput si nécessaire
try:
    from pynput import keyboard
except ImportError:
    print("Installation de pynput (première utilisation)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput", "--quiet"])
    from pynput import keyboard


class KeyboardCleaner:
    def __init__(self):
        self.listener = None

        self.root = tk.Tk()
        self.setup_window()
        self.start_suppression()
        self.root.mainloop()

    def setup_window(self):
        self.root.title("Keyboard Cleaner")
        self.root.configure(bg="#0f172a")

        w, h = 500, 340
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Empêche la fermeture via la croix (doit cliquer dans la fenêtre)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # --- Contenu ---
        frame = tk.Frame(self.root, bg="#0f172a", cursor="hand2")
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        tk.Label(
            frame, text="⌨️", font=("Arial", 52), bg="#0f172a"
        ).pack()

        tk.Label(
            frame,
            text="Clavier désactivé",
            font=("Arial", 22, "bold"),
            fg="#f8fafc",
            bg="#0f172a",
        ).pack(pady=(8, 4))

        tk.Label(
            frame,
            text="Nettoyez votre clavier en toute tranquillité.\nCliquez n'importe où ici pour le réactiver.",
            font=("Arial", 13),
            fg="#94a3b8",
            bg="#0f172a",
            justify="center",
        ).pack()

        # Indicateur coloré
        self.indicator = tk.Label(
            frame,
            text="● VERROUILLÉ",
            font=("Arial", 11, "bold"),
            fg="#ef4444",
            bg="#0f172a",
            cursor="hand2",
        )
        self.indicator.pack(pady=(20, 0))

        # Bind clic sur toute la fenêtre
        for widget in [self.root, frame] + frame.winfo_children():
            widget.bind("<Button-1>", self.unlock)

    def start_suppression(self):
        try:
            self.listener = keyboard.Listener(suppress=True)
            self.listener.start()
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de désactiver le clavier.\n\n"
                f"Sur macOS : autorisez l'accès dans\n"
                f"Réglages Système > Confidentialité > Accessibilité\n\n"
                f"Erreur : {e}",
            )
            self.root.destroy()

    def unlock(self, event=None):
        if self.listener and self.listener.running:
            self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    KeyboardCleaner()
