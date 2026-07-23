#!/usr/bin/env python3
"""
Video/Audio Downloader — powered by yt-dlp
Supporte YouTube, Vimeo, Twitter/X, Instagram, TikTok et des centaines d'autres sites.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import re
import subprocess

# ── Try importing yt-dlp ──────────────────────────────────────────────────────
try:
    import yt_dlp
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp",
                           "--break-system-packages", "-q"])
    import yt_dlp


# ═══════════════════════════════════════════════════════════════════════════════
#  PALETTE / THEME
# ═══════════════════════════════════════════════════════════════════════════════
BG        = "#1a1b2e"
BG2       = "#16213e"
BG3       = "#0f3460"
ACCENT    = "#e94560"
ACCENT2   = "#533483"
TEXT      = "#eaeaea"
TEXT_DIM  = "#7f8c8d"
SUCCESS   = "#2ecc71"
WARNING   = "#f39c12"
ERROR     = "#e74c3c"
FONT_MAIN = ("Segoe UI", 10)
FONT_BIG  = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 9)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER — taille lisible
# ═══════════════════════════════════════════════════════════════════════════════
def human_size(b):
    if b is None:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(b) < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def human_speed(bps):
    if bps is None:
        return ""
    return f"{human_size(bps)}/s"


# ═══════════════════════════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
class DownloaderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎬  Video Downloader")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self._center_window(700, 580)

        self._download_thread: threading.Thread | None = None
        self._cancel_flag = threading.Event()

        self._build_ui()

    # ── Window centering ──────────────────────────────────────────────────────
    def _center_window(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=20, pady=8)

        # ── Header ──
        header = tk.Frame(self.root, bg=BG3, height=64)
        header.pack(fill="x")
        tk.Label(header, text="🎬  Video Downloader",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG3, fg=TEXT).pack(side="left", padx=24, pady=14)
        tk.Label(header, text="yt-dlp · ffmpeg",
                 font=FONT_MONO, bg=BG3, fg=TEXT_DIM).pack(side="right", padx=24)

        body = tk.Frame(self.root, bg=BG, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # ── URL ──
        self._section_label(body, "🔗  Lien de la vidéo")
        url_frame = tk.Frame(body, bg=BG2, bd=0, highlightthickness=2,
                             highlightbackground=ACCENT2,
                             highlightcolor=ACCENT)
        url_frame.pack(fill="x", pady=(4, 10))

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                  font=("Segoe UI", 11),
                                  bg=BG2, fg=TEXT, insertbackground=ACCENT,
                                  relief="flat", bd=10,
                                  selectbackground=ACCENT2)
        self.url_entry.pack(side="left", fill="x", expand=True)
        self.url_entry.bind("<FocusIn>",  lambda e: url_frame.config(highlightbackground=ACCENT))
        self.url_entry.bind("<FocusOut>", lambda e: url_frame.config(highlightbackground=ACCENT2))

        btn_clear = tk.Button(url_frame, text="✕", font=("Segoe UI", 10, "bold"),
                              bg=BG2, fg=TEXT_DIM, relief="flat", bd=0,
                              activebackground=BG2, activeforeground=ACCENT,
                              cursor="hand2",
                              command=lambda: self.url_var.set(""))
        btn_clear.pack(side="right", padx=8)

        # Placeholder
        self.url_entry.insert(0, "Colle ton lien ici…")
        self.url_entry.config(fg=TEXT_DIM)
        self.url_entry.bind("<FocusIn>",  self._url_focus_in)
        self.url_entry.bind("<FocusOut>", self._url_focus_out)

        # ── Mode (Vidéo / Audio) ──
        self._section_label(body, "🎵  Format de sortie")
        mode_frame = tk.Frame(body, bg=BG)
        mode_frame.pack(fill="x", pady=(4, 10))

        self.mode_var = tk.StringVar(value="video")
        for val, icon, label, sub in [
            ("video", "🎬", "Vidéo  MP4", "Meilleure qualité vidéo + audio"),
            ("audio", "🎧", "Audio  MP3", "Extraction audio uniquement"),
        ]:
            card = tk.Frame(mode_frame, bg=BG2, bd=0,
                            highlightthickness=2, highlightbackground=BG3,
                            cursor="hand2")
            card.pack(side="left", fill="x", expand=True, padx=(0, 8 if val == "video" else 0))

            rb = tk.Radiobutton(card, text=f"  {icon}  {label}",
                                variable=self.mode_var, value=val,
                                font=("Segoe UI", 11, "bold"),
                                bg=BG2, fg=TEXT,
                                activebackground=BG2, activeforeground=ACCENT,
                                selectcolor=BG2,
                                indicatoron=False, relief="flat", bd=0,
                                command=self._on_mode_change)
            rb.pack(fill="x", padx=14, pady=(10, 4))
            tk.Label(card, text=sub, font=("Segoe UI", 8),
                     bg=BG2, fg=TEXT_DIM).pack(padx=14, pady=(0, 10), anchor="w")

        self._mode_cards = mode_frame.winfo_children()
        self._on_mode_change()

        # ── Dossier de destination ──
        self._section_label(body, "📁  Dossier de destination")
        folder_frame = tk.Frame(body, bg=BG2, bd=0, highlightthickness=2,
                                highlightbackground=ACCENT2)
        folder_frame.pack(fill="x", pady=(4, 10))

        # Default: user's Downloads folder
        default_dir = os.path.expanduser("~/Downloads")
        self.folder_var = tk.StringVar(value=default_dir)
        tk.Entry(folder_frame, textvariable=self.folder_var,
                 font=FONT_MAIN, bg=BG2, fg=TEXT,
                 insertbackground=ACCENT, relief="flat", bd=10,
                 state="readonly", readonlybackground=BG2).pack(side="left", fill="x", expand=True)

        tk.Button(folder_frame, text="  Parcourir…  ",
                  font=FONT_MAIN, bg=ACCENT2, fg=TEXT,
                  activebackground=ACCENT, activeforeground=TEXT,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._browse_folder).pack(side="right", padx=4, pady=4)

        # ── Barre de progression ──
        self._section_label(body, "⬇️  Progression")

        prog_outer = tk.Frame(body, bg=BG)
        prog_outer.pack(fill="x", pady=(4, 4))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=BG2, background=ACCENT,
                        lightcolor=ACCENT, darkcolor=ACCENT,
                        bordercolor=BG2, thickness=18)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(prog_outer, variable=self.progress_var,
                                            maximum=100, length=100,
                                            style="Custom.Horizontal.TProgressbar",
                                            mode="determinate")
        self.progress_bar.pack(fill="x")

        stats_frame = tk.Frame(body, bg=BG)
        stats_frame.pack(fill="x", pady=(2, 8))
        self.pct_label   = tk.Label(stats_frame, text="0 %", font=FONT_MONO,
                                    bg=BG, fg=ACCENT)
        self.pct_label.pack(side="left")
        self.speed_label = tk.Label(stats_frame, text="", font=FONT_MONO,
                                    bg=BG, fg=TEXT_DIM)
        self.speed_label.pack(side="left", padx=16)
        self.eta_label   = tk.Label(stats_frame, text="", font=FONT_MONO,
                                    bg=BG, fg=TEXT_DIM)
        self.eta_label.pack(side="left")
        self.size_label  = tk.Label(stats_frame, text="", font=FONT_MONO,
                                    bg=BG, fg=TEXT_DIM)
        self.size_label.pack(side="right")

        # ── Log ──
        self.log_text = tk.Text(body, height=4, font=FONT_MONO,
                                bg=BG2, fg=TEXT_DIM,
                                insertbackground=TEXT, relief="flat",
                                wrap="word", state="disabled", bd=10)
        self.log_text.pack(fill="x", pady=(0, 12))
        # colour tags
        self.log_text.tag_config("ok",      foreground=SUCCESS)
        self.log_text.tag_config("warn",    foreground=WARNING)
        self.log_text.tag_config("err",     foreground=ERROR)
        self.log_text.tag_config("neutral", foreground=TEXT_DIM)

        # ── Bouton principal ──
        self.action_btn = tk.Button(body, text="⬇️   Télécharger",
                                    font=("Segoe UI", 13, "bold"),
                                    bg=ACCENT, fg="white",
                                    activebackground="#c0392b", activeforeground="white",
                                    relief="flat", bd=0, height=2,
                                    cursor="hand2",
                                    command=self._on_action_btn)
        self.action_btn.pack(fill="x")

    # ── Section label ─────────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(6, 0))

    # ── Placeholder behaviour ─────────────────────────────────────────────────
    def _url_focus_in(self, event):
        if self.url_entry.get() == "Colle ton lien ici…":
            self.url_entry.delete(0, "end")
            self.url_entry.config(fg=TEXT)
        parent = self.url_entry.master
        parent.config(highlightbackground=ACCENT)

    def _url_focus_out(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "Colle ton lien ici…")
            self.url_entry.config(fg=TEXT_DIM)
        parent = self.url_entry.master
        parent.config(highlightbackground=ACCENT2)

    # ── Mode toggle ───────────────────────────────────────────────────────────
    def _on_mode_change(self):
        mode = self.mode_var.get()
        for card in self._mode_cards:
            rb = card.winfo_children()[0]
            is_sel = (rb.cget("value") == mode)
            card.config(highlightbackground=ACCENT if is_sel else BG3)

    # ── Browse folder ─────────────────────────────────────────────────────────
    def _browse_folder(self):
        current = self.folder_var.get()
        if not os.path.isdir(current):
            current = os.path.expanduser("~")
        folder = filedialog.askdirectory(initialdir=current,
                                         title="Choisir le dossier de destination")
        if folder:
            self.folder_var.set(folder)

    # ── Log helper ────────────────────────────────────────────────────────────
    def _log(self, msg, tag="neutral"):
        def _do():
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg + "\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, _do)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ── Action button dispatcher ──────────────────────────────────────────────
    def _on_action_btn(self):
        if self._download_thread and self._download_thread.is_alive():
            self._cancel_flag.set()
            self._log("⏹  Annulation demandée…", "warn")
            self.action_btn.config(text="Annulation…", state="disabled")
        else:
            self._start_download()

    # ── Start download ────────────────────────────────────────────────────────
    def _start_download(self):
        url = self.url_var.get().strip()
        if not url or url == "Colle ton lien ici…":
            messagebox.showwarning("Lien manquant", "Colle un lien avant de lancer le téléchargement.")
            return

        dest = self.folder_var.get().strip()
        if not dest or not os.path.isdir(dest):
            messagebox.showwarning("Dossier invalide",
                                   "Choisis un dossier de destination valide.")
            return

        self._cancel_flag.clear()
        self._clear_log()
        self._reset_progress()

        self.action_btn.config(text="⏹   Annuler", bg="#c0392b")
        self._log(f"🔍  Analyse du lien…", "neutral")

        self._download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, dest, self.mode_var.get()),
            daemon=True
        )
        self._download_thread.start()

    # ── Download worker (background thread) ──────────────────────────────────
    def _download_worker(self, url: str, dest: str, mode: str):
        is_audio = (mode == "audio")

        def progress_hook(d):
            if self._cancel_flag.is_set():
                raise yt_dlp.utils.DownloadError("Annulé par l'utilisateur")

            status = d.get("status")

            if status == "downloading":
                total   = d.get("total_bytes") or d.get("total_bytes_estimate")
                dl      = d.get("downloaded_bytes", 0)
                speed   = d.get("speed")
                eta     = d.get("eta")

                pct = (dl / total * 100) if total else 0

                self.root.after(0, self._update_progress,
                                pct, speed, eta, dl, total)

            elif status == "finished":
                self.root.after(0, self._update_progress, 100, None, 0, None, None)
                name = os.path.basename(d.get("filename", ""))
                self._log(f"✅  Terminé : {name}", "ok")

        ydl_opts = {
            "outtmpl":         os.path.join(dest, "%(title)s.%(ext)s"),
            "progress_hooks":  [progress_hook],
            "quiet":           True,
            "no_warnings":     False,
            "ffmpeg_location": "/usr/bin",
            "noplaylist":      True,   # single video by default
        }

        if is_audio:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   "mp3",
                "preferredquality": "0",          # VBR best quality
            }]
            self._log("🎧  Mode audio — conversion MP3 en cours…", "neutral")
        else:
            ydl_opts["format"]               = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
            ydl_opts["merge_output_format"]  = "mp4"
            ydl_opts["postprocessors"]       = [{
                "key":            "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }]
            self._log("🎬  Mode vidéo — téléchargement MP4 max qualité…", "neutral")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", url)
                self._log(f"📺  {title}", "neutral")
                ydl.download([url])

            ext = "MP3" if is_audio else "MP4"
            self._log(f"🎉  Fichier {ext} enregistré dans : {dest}", "ok")
            self.root.after(0, self._on_done, True)

        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "Annulé" in msg or "cancelled" in msg.lower():
                self._log("⏹  Téléchargement annulé.", "warn")
            else:
                self._log(f"❌  Erreur : {msg[:200]}", "err")
            self.root.after(0, self._on_done, False)
        except Exception as e:
            self._log(f"❌  Erreur inattendue : {e}", "err")
            self.root.after(0, self._on_done, False)

    # ── UI update helpers (called from main thread via root.after) ────────────
    def _update_progress(self, pct, speed, eta, downloaded, total):
        self.progress_var.set(pct)
        self.pct_label.config(text=f"{pct:.1f} %")
        self.speed_label.config(text=human_speed(speed) if speed else "")
        if eta is not None and eta > 0:
            m, s = divmod(int(eta), 60)
            self.eta_label.config(text=f"ETA {m:02d}:{s:02d}")
        elif eta == 0:
            self.eta_label.config(text="")
        if downloaded and total:
            self.size_label.config(text=f"{human_size(downloaded)} / {human_size(total)}")

    def _reset_progress(self):
        self.progress_var.set(0)
        self.pct_label.config(text="0 %")
        self.speed_label.config(text="")
        self.eta_label.config(text="")
        self.size_label.config(text="")

    def _on_done(self, success: bool):
        self.action_btn.config(text="⬇️   Télécharger", bg=ACCENT,
                               state="normal")
        if success:
            self.progress_var.set(100)
            self.pct_label.config(text="100 %")


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = DownloaderApp(root)
    root.mainloop()
