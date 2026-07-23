import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import sys
import os

class FloatingImageViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ImgViewer")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Fenêtre sans bordure
        self.root.configure(bg='#1e1e1e')

        self.locked = False
        self._drag_x = 0
        self._drag_y = 0
        self.current_image = None
        self.photo = None
        self.opacity = 1.0

        # Taille initiale
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"320x280+{screen_w//2 - 160}+{screen_h//2 - 140}")

        self._build_ui()
        self._show_placeholder()

        # Raccourcis clavier
        self.root.bind('<Control-v>', lambda e: self.paste_image())
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        self.root.mainloop()

    def _build_ui(self):
        # --- Barre de contrôle en haut ---
        self.topbar = tk.Frame(self.root, bg='#111111', height=32)
        self.topbar.pack(fill=tk.X, side=tk.TOP)
        self.topbar.pack_propagate(False)

        # Bouton fermer
        btn_close = tk.Button(
            self.topbar, text='✕', command=self.root.destroy,
            bg='#111111', fg='#888888', bd=0, font=('Arial', 11),
            activebackground='#cc3333', activeforeground='white',
            cursor='hand2', padx=6
        )
        btn_close.pack(side=tk.RIGHT, pady=2, padx=2)
        btn_close.bind('<Enter>', lambda e: btn_close.config(fg='white', bg='#cc3333'))
        btn_close.bind('<Leave>', lambda e: btn_close.config(fg='#888888', bg='#111111'))

        # Bouton coller
        btn_paste = tk.Button(
            self.topbar, text='📋', command=self.paste_image,
            bg='#111111', fg='#888888', bd=0, font=('Arial', 11),
            activebackground='#333', activeforeground='white',
            cursor='hand2', padx=6
        )
        btn_paste.pack(side=tk.RIGHT, pady=2, padx=2)
        btn_paste.bind('<Enter>', lambda e: btn_paste.config(fg='white', bg='#333'))
        btn_paste.bind('<Leave>', lambda e: btn_paste.config(fg='#888888', bg='#111111'))

        # Bouton verrouiller
        self.btn_lock = tk.Button(
            self.topbar, text='🔓', command=self.toggle_lock,
            bg='#111111', fg='#888888', bd=0, font=('Arial', 11),
            activebackground='#333', activeforeground='white',
            cursor='hand2', padx=6
        )
        self.btn_lock.pack(side=tk.LEFT, pady=2, padx=2)
        self.btn_lock.bind('<Enter>', lambda e: self.btn_lock.config(fg='white', bg='#333'))
        self.btn_lock.bind('<Leave>', lambda e: self.btn_lock.config(
            fg='#ff9900' if self.locked else '#888888',
            bg='#111111'
        ))

        # Label titre
        self.lbl_title = tk.Label(
            self.topbar, text='ImgViewer', bg='#111111', fg='#444444',
            font=('Arial', 9)
        )
        self.lbl_title.pack(side=tk.LEFT, padx=6)

        # Drag depuis la topbar
        self.topbar.bind('<Button-1>', self._start_drag)
        self.topbar.bind('<B1-Motion>', self._do_drag)
        self.lbl_title.bind('<Button-1>', self._start_drag)
        self.lbl_title.bind('<B1-Motion>', self._do_drag)

        # --- Zone image ---
        self.canvas = tk.Canvas(
            self.root, bg='#1e1e1e', bd=0, highlightthickness=0,
            cursor='fleur'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Drag depuis le canvas (image)
        self.canvas.bind('<Button-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', self._do_drag)

        # Double-clic pour coller
        self.canvas.bind('<Double-Button-1>', lambda e: self.paste_image())

        # --- Barre de statut en bas ---
        self.statusbar = tk.Frame(self.root, bg='#111111', height=20)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.statusbar.pack_propagate(False)

        self.lbl_status = tk.Label(
            self.statusbar, text='Ctrl+V ou double-clic pour coller',
            bg='#111111', fg='#444444', font=('Arial', 8)
        )
        self.lbl_status.pack(side=tk.LEFT, padx=6)

        # Resize handle (coin bas-droite)
        self.resize_grip = tk.Label(
            self.statusbar, text='⠿', bg='#111111', fg='#444',
            font=('Arial', 10), cursor='sizing'
        )
        self.resize_grip.pack(side=tk.RIGHT, padx=2)
        self.resize_grip.bind('<Button-1>', self._start_resize)
        self.resize_grip.bind('<B1-Motion>', self._do_resize)

    def _show_placeholder(self):
        self.canvas.delete('all')
        w = self.canvas.winfo_width() or 320
        h = self.canvas.winfo_height() or 240
        self.canvas.create_text(
            w // 2, h // 2,
            text='📋\n\nCtrl+V pour coller une image\nou double-cliquez ici',
            fill='#444444', font=('Arial', 12), justify=tk.CENTER,
            tags='placeholder'
        )

    def paste_image(self):
        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                self._set_status('❌ Rien dans le presse-papier')
                return
            if isinstance(img, Image.Image):
                self.current_image = img.copy()
                self._display_image()
            elif isinstance(img, list) and len(img) > 0:
                # Fichier image depuis le presse-papier (Windows)
                path = img[0]
                if os.path.isfile(path):
                    self.current_image = Image.open(path)
                    self._display_image()
        except Exception as ex:
            self._set_status(f'❌ Erreur: {ex}')

    def _display_image(self):
        if not self.current_image:
            return

        # Adapter la taille de la fenêtre à l'image (max 800x700)
        img = self.current_image.copy()
        max_w, max_h = 800, 700
        img.thumbnail((max_w, max_h), Image.LANCZOS)

        iw, ih = img.size
        win_w = iw
        win_h = ih + 32 + 20  # + topbar + statusbar

        # Repositionner si nécessaire
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")

        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete('all')
        self.canvas.config(width=iw, height=ih)
        self.canvas.create_image(iw // 2, ih // 2, image=self.photo, anchor=tk.CENTER)

        self._set_status(f'✔ {self.current_image.width}×{self.current_image.height}px')

    def toggle_lock(self):
        self.locked = not self.locked
        if self.locked:
            self.btn_lock.config(text='🔒', fg='#ff9900')
            self.canvas.config(cursor='arrow')
            self._set_status('🔒 Fenêtre verrouillée')
        else:
            self.btn_lock.config(text='🔓', fg='#888888')
            self.canvas.config(cursor='fleur')
            self._set_status('🔓 Fenêtre libre')

    def _set_status(self, msg):
        self.lbl_status.config(text=msg)
        # Remettre le texte par défaut après 3 secondes si on a une image
        if self.current_image:
            self.root.after(3000, lambda: self.lbl_status.config(
                text=f'{self.current_image.width}×{self.current_image.height}px'
            ))

    # --- Drag ---
    def _start_drag(self, event):
        if not self.locked:
            self._drag_x = event.x_root - self.root.winfo_x()
            self._drag_y = event.y_root - self.root.winfo_y()

    def _do_drag(self, event):
        if not self.locked:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            self.root.geometry(f'+{x}+{y}')

    # --- Resize ---
    def _start_resize(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._resize_start_w = self.root.winfo_width()
        self._resize_start_h = self.root.winfo_height()

    def _do_resize(self, event):
        if not self.locked:
            dw = event.x_root - self._resize_start_x
            dh = event.y_root - self._resize_start_y
            new_w = max(150, self._resize_start_w + dw)
            new_h = max(120, self._resize_start_h + dh)
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f'{new_w}x{new_h}+{x}+{y}')
            # Redessiner l'image si présente
            if self.current_image:
                img = self.current_image.copy()
                img.thumbnail((new_w, new_h - 52), Image.LANCZOS)
                iw, ih = img.size
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.delete('all')
                self.canvas.create_image(iw // 2, ih // 2, image=self.photo, anchor=tk.CENTER)

if __name__ == '__main__':
    FloatingImageViewer()
