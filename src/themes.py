"""Theme registry and theme picker panel with opacity slider."""

import customtkinter as ctk

PALETTE = {
    "dark":       {"bg": "#0f0f1a", "card": "#1a1a2e", "border": "#2a2a45", "hdr": "#12121f", "fg": "#eeeeff", "dim": "#7878a0", "accent": "#7b8cff", "green": "#4ade80", "yellow": "#fbbf24", "red": "#f87171", "bar": "#252540", "a": 0.88},
    "glass":      {"bg": "#080814", "card": "#10102a", "border": "#303060", "hdr": "#0a0a1e", "fg": "#d8d8ff", "dim": "#5555aa", "accent": "#8888ff", "green": "#55ffaa", "yellow": "#ffdd55", "red": "#ff5577", "bar": "#1a1a40", "a": 0.72},
    "light":      {"bg": "#f0f0f6", "card": "#ffffff", "border": "#d8d8e8", "hdr": "#e8e8f0", "fg": "#2a2a40", "dim": "#9090b0", "accent": "#5566dd", "green": "#22aa66", "yellow": "#cc9900", "red": "#dd3344", "bar": "#e0e0ee", "a": 0.94},
    "cyber":      {"bg": "#0a0a0a", "card": "#111111", "border": "#224422", "hdr": "#0d0d0d", "fg": "#00ff88", "dim": "#006633", "accent": "#00ffcc", "green": "#00ff88", "yellow": "#ffcc00", "red": "#ff0044", "bar": "#1a1a1a", "a": 0.90},
    "purple":     {"bg": "#12091e", "card": "#1a1030", "border": "#3a2860", "hdr": "#150b24", "fg": "#e8d8ff", "dim": "#7868a0", "accent": "#b888ff", "green": "#88ff88", "yellow": "#ffcc66", "red": "#ff6688", "bar": "#251845", "a": 0.86},
    "ocean":      {"bg": "#0a1628", "card": "#0f2040", "border": "#1a3a60", "hdr": "#0c1a30", "fg": "#c8e0ff", "dim": "#4a70a0", "accent": "#44aaff", "green": "#44ddaa", "yellow": "#ffbb44", "red": "#ff5566", "bar": "#152a50", "a": 0.86},
    "sunset":     {"bg": "#1a0f0a", "card": "#2a1810", "border": "#4a2a18", "hdr": "#201208", "fg": "#ffe8d8", "dim": "#a07050", "accent": "#ff8844", "green": "#66cc66", "yellow": "#ffcc44", "red": "#ff4455", "bar": "#3a2010", "a": 0.86},
    "rose":       {"bg": "#1a0f14", "card": "#2a1520", "border": "#4a2538", "hdr": "#200f18", "fg": "#ffd8e8", "dim": "#a06880", "accent": "#ff66aa", "green": "#66dd88", "yellow": "#ffbb44", "red": "#ff4466", "bar": "#3a1828", "a": 0.86},
    "mint":       {"bg": "#0a1a14", "card": "#102a20", "border": "#1a4a38", "hdr": "#0c201a", "fg": "#d8fff0", "dim": "#50a080", "accent": "#44ddaa", "green": "#55ffaa", "yellow": "#ffdd44", "red": "#ff5566", "bar": "#153a2a", "a": 0.86},
    "nord":       {"bg": "#2e3440", "card": "#3b4252", "border": "#434c5e", "hdr": "#2e3440", "fg": "#eceff4", "dim": "#7b88a0", "accent": "#88c0d0", "green": "#a3be8c", "yellow": "#ebcb8b", "red": "#bf616a", "bar": "#434c5e", "a": 0.90},
    "dracula":    {"bg": "#282a36", "card": "#343746", "border": "#44475a", "hdr": "#282a36", "fg": "#f8f8f2", "dim": "#6272a4", "accent": "#bd93f9", "green": "#50fa7b", "yellow": "#f1fa8c", "red": "#ff5555", "bar": "#44475a", "a": 0.90},
    "catppuccin": {"bg": "#1e1e2e", "card": "#282840", "border": "#383858", "hdr": "#1e1e2e", "fg": "#cdd6f4", "dim": "#6c7086", "accent": "#cba6f7", "green": "#a6e3a1", "yellow": "#f9e2af", "red": "#f38ba8", "bar": "#313244", "a": 0.90},
}

NAMES = list(PALETTE.keys())


def make_theme(name: str) -> dict:
    p = PALETTE[name]
    return {
        "window_bg": p["bg"], "card_bg": p["card"], "card_border": p["border"],
        "header_bg": p["hdr"], "fg": p["fg"], "fg_dim": p["dim"],
        "accent": p["accent"], "accent_hover": p["accent"],
        "green": p["green"], "yellow": p["yellow"], "red": p["red"],
        "bar_bg": p["bar"],
        "bar_green": p["green"], "bar_yellow": p["yellow"], "bar_red": p["red"],
        "alpha": p["a"],
    }


def _bind_click(widget, callback):
    """Recursively bind left-click on a widget and all its children."""
    widget.bind("<Button-1>", callback, add="+")
    widget.configure(cursor="hand2")
    for child in widget.winfo_children():
        _bind_click(child, callback)


class ThemePanel(ctk.CTkToplevel):
    """Theme picker with opacity slider, anchored below the trigger button."""

    def __init__(self, master, current: str, on_pick, on_alpha, anchor_x: int, anchor_y: int):
        super().__init__(master)
        self.on_pick = on_pick
        self.on_alpha = on_alpha
        self._done = False
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0e0e18")

        COLS = 4
        sw = 52
        pad = 5
        n = len(NAMES)
        rows = (n + COLS - 1) // COLS
        w = COLS * (sw + pad) + pad * 2
        slider_h = 56
        title_h = 30
        grid_h = rows * (sw + 20 + pad) + pad
        h = title_h + grid_h + slider_h + pad * 2

        px = max(0, min(anchor_x - w // 2, self.winfo_screenwidth() - w))
        py = anchor_y + 4
        if py + h > self.winfo_screenheight():
            py = max(0, anchor_y - h - 4)
        self.geometry(f"{w}x{h}+{px}+{py}")

        # title bar with close
        title_bar = ctk.CTkFrame(self, fg_color="transparent")
        title_bar.pack(fill="x", padx=8, pady=(6, 2))
        title_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_bar, text="主题", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#8888ff").grid(row=0, column=0)
        close_btn = ctk.CTkLabel(title_bar, text="✕", font=ctk.CTkFont(size=11),
                                 text_color="#666688", cursor="hand2", width=20)
        close_btn.grid(row=0, column=1)
        close_btn.bind("<Button-1>", lambda e: self._close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(text_color="#ff5577"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(text_color="#666688"))

        # grid of theme swatches
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(padx=pad)

        for i, name in enumerate(NAMES):
            r, c = divmod(i, COLS)
            p = PALETTE[name]

            swatch = ctk.CTkFrame(grid, fg_color=p["card"], corner_radius=8,
                                  border_width=1, border_color=p["border"],
                                  width=sw, height=sw + 20)
            swatch.grid(row=r, column=c, padx=pad // 2, pady=pad // 2)
            swatch.grid_propagate(False)

            dots = ctk.CTkFrame(swatch, fg_color="transparent")
            dots.pack(pady=(6, 1))
            for color in [p["accent"], p["green"], p["yellow"], p["red"]]:
                ctk.CTkLabel(dots, text="●", font=ctk.CTkFont(size=6),
                             text_color=color, width=10).pack(side="left")

            lbl = ctk.CTkLabel(swatch, text=name, font=ctk.CTkFont(size=8, weight="bold"),
                               text_color=p["fg"])
            lbl.pack()

            if name == current:
                ctk.CTkLabel(swatch, text="✓", font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=p["accent"]).place(relx=1.0, x=-4, y=1, anchor="ne")

            # bind click on swatch AND all children inside it
            _bind_click(swatch, lambda e, tn=name: self._pick(tn))

        # opacity slider
        sep = ctk.CTkFrame(self, fg_color="#2a2a45", height=1)
        sep.pack(fill="x", padx=12, pady=(4, 2))

        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=12, pady=(0, 8))
        sf.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sf, text="透明度", font=ctk.CTkFont(size=10),
                     text_color="#8888ff").grid(row=0, column=0, padx=(0, 8))

        self._alpha_val = ctk.CTkLabel(sf, text=f"{int(PALETTE[current]['a'] * 100)}%",
                                       font=ctk.CTkFont(size=10, weight="bold"),
                                       text_color="#eeeeff", width=36)
        self._alpha_val.grid(row=0, column=2, padx=(6, 0))

        self._slider = ctk.CTkSlider(
            sf, from_=0.4, to=1.0, number_of_steps=30,
            command=self._on_slide,
            fg_color="#252540", progress_color="#7b8cff",
            button_color="#8888ff", button_hover_color="#aaaaff",
            height=14, button_length=14,
        )
        self._slider.set(PALETTE[current]["a"])
        self._slider.grid(row=0, column=1, sticky="ew")

        # grab all input so clicks outside can close us
        self.after(100, self._grab)

    def _grab(self):
        try:
            self.grab_set()
        except Exception:
            pass
        self.focus_force()

    def _on_slide(self, val):
        pct = int(float(val) * 100)
        self._alpha_val.configure(text=f"{pct}%")
        self.on_alpha(float(val))

    def _pick(self, name):
        if self._done:
            return
        self._done = True
        self.on_pick(name)
        self._close()

    def _close(self):
        if self._done:
            return
        self._done = True
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
