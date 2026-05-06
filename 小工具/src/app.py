import customtkinter as ctk
import threading
import time
import ctypes
from datetime import datetime
from api import query_mimo, query_deepseek, MimoResult, DeepseekResult
from config import REFRESH_INTERVAL
from themes import NAMES, make_theme, ThemePanel
from rounded import apply_rounded_corners
from settings import SettingsPanel, get as cfg, set as cfg_set
from hotkey import GlobalHotkey


def fmt_token(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.theme_name = cfg("theme") or "dark"
        self.t = make_theme(self.theme_name)
        self.expanded = True
        self._running = True
        self._mimo = None
        self._ds = None
        self._panel = None
        self._settings_win = None
        self._hidden = False

        self._init_window()
        self._rebuild()
        self._bind_drag()
        self._start_poll()
        self._init_hotkey()

    # ── window ───────────────────────────────────────────────────

    def _init_window(self):
        self.title("API 额度监控")
        self.attributes("-topmost", True)
        saved_alpha = cfg("alpha")
        self.attributes("-alpha", saved_alpha if saved_alpha else self.t["alpha"])
        self.overrideredirect(True)
        try:
            self.attributes("-toolwindow", True)
        except Exception:
            pass
        self.W_EXP = 400
        self.W_MINI = 320
        self.geometry(f"{self.W_EXP}x+120+120")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.after(100, self._round)

    def _round(self):
        try:
            hwnd = int(self.winfo_frame(), 16)
            apply_rounded_corners(hwnd)
        except Exception:
            pass

    def _fit(self):
        self.update_idletasks()
        w = self.W_EXP if self.expanded else self.W_MINI
        self.geometry(f"{w}x{self.winfo_reqheight()}")

    # ── drag ─────────────────────────────────────────────────────

    def _bind_drag(self):
        self._dx = self._dy = 0
        self.bind("<Button-1>", self._down)
        self.bind("<B1-Motion>", self._drag)

    def _down(self, e):
        self._dx, self._dy = e.x, e.y

    def _drag(self, e):
        self.geometry(f"+{self.winfo_x() + e.x - self._dx}+{self.winfo_y() + e.y - self._dy}")

    # ── theme ────────────────────────────────────────────────────

    def _open_panel(self):
        if self._panel and self._panel.winfo_exists():
            self._panel.destroy()
            return
        # anchor below the theme button
        btn = self._theme_btn
        bx = btn.winfo_rootx() + btn.winfo_width() // 2
        by = btn.winfo_rooty() + btn.winfo_height()
        self._panel = ThemePanel(
            self, self.theme_name,
            on_pick=self._set_theme,
            on_alpha=self._set_alpha,
            anchor_x=bx, anchor_y=by,
        )

    def _set_theme(self, name):
        self.theme_name = name
        self.t = make_theme(name)
        self.attributes("-alpha", self.t["alpha"])
        cfg_set("theme", name)
        cfg_set("alpha", self.t["alpha"])
        self._rebuild()
        self._bind_drag()

    def _set_alpha(self, val):
        self.attributes("-alpha", val)
        cfg_set("alpha", val)

    def _open_settings(self):
        if self._settings_win and self._settings_win.winfo_exists():
            self._settings_win.focus()
            return
        self._settings_win = SettingsPanel(self, on_save=self._on_settings_saved)

    def _on_settings_saved(self):
        threading.Thread(target=self._do_refresh, daemon=True).start()

    # ── hotkey ───────────────────────────────────────────────────

    def _init_hotkey(self):
        hk_str = cfg("hotkey") or "Ctrl+Alt+Q"
        self._hotkey = GlobalHotkey(hk_str, self._toggle_visibility)
        self._hotkey.start()

    def _toggle_visibility(self):
        # must schedule on main thread
        self.after(0, self._do_toggle_vis)

    def _do_toggle_vis(self):
        if self._hidden:
            self.deiconify()
            self.attributes("-alpha", cfg("alpha") or self.t["alpha"])
            self._hidden = False
        else:
            self.withdraw()
            self._hidden = True

    # ── rebuild ──────────────────────────────────────────────────

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        (self._ui_expanded if self.expanded else self._ui_mini)()
        self.configure(fg_color=self.t["window_bg"])
        self._fit()
        self.after(50, self._round)
        self._restore()

    def _btn(self, parent, text, cmd, size=15):
        t = self.t
        b = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size),
                         text_color=t["fg_dim"], cursor="hand2", width=28, height=28)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(text_color=t["accent"]))
        b.bind("<Leave>", lambda e: b.configure(text_color=t["fg_dim"]))
        return b

    # ── expanded ─────────────────────────────────────────────────

    def _ui_expanded(self):
        t = self.t

        # header
        hdr = ctk.CTkFrame(self, fg_color=t["header_bg"], corner_radius=0, height=48)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="API 额度监控", font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=t["accent"]).pack(side="left", padx=16)

        bb = ctk.CTkFrame(hdr, fg_color="transparent")
        bb.pack(side="right", padx=10)
        self._btn(bb, "⟳", self._refresh_now, 16).pack(side="right", padx=3)

        self._theme_btn = self._btn(bb, "◑", self._open_panel, 16)
        self._theme_btn.pack(side="right", padx=3)

        self._btn(bb, "⚙", self._open_settings, 16).pack(side="right", padx=3)
        self._btn(bb, "—", self._toggle, 18).pack(side="right", padx=3)
        self._btn(bb, "✕", self.destroy, 16).pack(side="right", padx=3)

        # body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(8, 2))
        body.grid_columnconfigure(0, weight=1)

        # MIMO
        mc = ctk.CTkFrame(body, fg_color=t["card_bg"], corner_radius=18,
                          border_width=1, border_color=t["card_border"])
        mc.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        mh = ctk.CTkFrame(mc, fg_color="transparent")
        mh.pack(fill="x", padx=18, pady=(12, 4))
        mh.grid_columnconfigure(2, weight=1)
        ctk.CTkLabel(mh, text="MIMO", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=t["accent"]).grid(row=0, column=0, sticky="w")
        self._m_dot = ctk.CTkLabel(mh, text="●", font=ctk.CTkFont(size=11), text_color=t["yellow"])
        self._m_dot.grid(row=0, column=1, padx=(8, 0), sticky="w")
        self._m_st = ctk.CTkLabel(mh, text="查询中…", font=ctk.CTkFont(size=12), text_color=t["yellow"])
        self._m_st.grid(row=0, column=2, sticky="w", padx=(5, 0))

        mi = ctk.CTkFrame(mc, fg_color="transparent")
        mi.pack(fill="x", padx=18, pady=(0, 4))
        mi.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(mi, text="已用 Token", font=ctk.CTkFont(size=12), text_color=t["fg_dim"]).grid(row=0, column=0, sticky="w", pady=2)
        self._m_used = ctk.CTkLabel(mi, text="—", font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), text_color=t["fg"])
        self._m_used.grid(row=0, column=1, sticky="e", pady=2)

        ctk.CTkLabel(mi, text="总额度", font=ctk.CTkFont(size=12), text_color=t["fg_dim"]).grid(row=1, column=0, sticky="w", pady=2)
        self._m_lim = ctk.CTkLabel(mi, text="—", font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), text_color=t["fg"])
        self._m_lim.grid(row=1, column=1, sticky="e", pady=2)

        bf = ctk.CTkFrame(mc, fg_color="transparent")
        bf.pack(fill="x", padx=18, pady=(6, 0))
        self._m_bar = ctk.CTkProgressBar(bf, height=8, corner_radius=4,
                                         fg_color=t["bar_bg"], progress_color=t["bar_green"])
        self._m_bar.pack(fill="x"); self._m_bar.set(0)
        self._m_pct = ctk.CTkLabel(mc, text="0%", font=ctk.CTkFont(size=11), text_color=t["fg_dim"])
        self._m_pct.pack(anchor="e", padx=18, pady=(2, 12))

        # DS
        dc = ctk.CTkFrame(body, fg_color=t["card_bg"], corner_radius=18,
                          border_width=1, border_color=t["card_border"])
        dc.grid(row=1, column=0, sticky="ew")

        dh = ctk.CTkFrame(dc, fg_color="transparent")
        dh.pack(fill="x", padx=18, pady=(12, 4))
        dh.grid_columnconfigure(2, weight=1)
        ctk.CTkLabel(dh, text="DeepSeek", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=t["accent"]).grid(row=0, column=0, sticky="w")
        self._d_dot = ctk.CTkLabel(dh, text="●", font=ctk.CTkFont(size=11), text_color=t["yellow"])
        self._d_dot.grid(row=0, column=1, padx=(8, 0), sticky="w")
        self._d_st = ctk.CTkLabel(dh, text="查询中…", font=ctk.CTkFont(size=12), text_color=t["yellow"])
        self._d_st.grid(row=0, column=2, sticky="w", padx=(5, 0))

        di = ctk.CTkFrame(dc, fg_color="transparent")
        di.pack(fill="x", padx=18, pady=(0, 4))
        di.grid_columnconfigure(1, weight=1)
        for i, (lab, attr) in enumerate([("账户余额", "_d_tot"), ("赠送余额", "_d_gr"), ("充值余额", "_d_tp"), ("状态", "_d_av")]):
            ctk.CTkLabel(di, text=lab, font=ctk.CTkFont(size=12), text_color=t["fg_dim"]).grid(row=i, column=0, sticky="w", pady=2)
            w = ctk.CTkLabel(di, text="—", font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), text_color=t["fg"])
            w.grid(row=i, column=1, sticky="e", pady=2)
            setattr(self, attr, w)
        ctk.CTkFrame(dc, fg_color="transparent", height=12).pack()

        # footer
        ft = ctk.CTkFrame(self, fg_color="transparent", height=24)
        ft.pack(fill="x", padx=16, pady=(4, 8)); ft.pack_propagate(False)
        self._time = ctk.CTkLabel(ft, text="等待更新…", font=ctk.CTkFont(size=10), text_color=t["fg_dim"])
        self._time.pack(side="left")
        ctk.CTkLabel(ft, text=f"{REFRESH_INTERVAL}s 自动刷新", font=ctk.CTkFont(size=10), text_color=t["fg_dim"]).pack(side="right")

    # ── mini ─────────────────────────────────────────────────────

    def _ui_mini(self):
        t = self.t
        card = ctk.CTkFrame(self, fg_color=t["card_bg"], corner_radius=16,
                            border_width=1, border_color=t["card_border"])
        card.pack(fill="both", expand=True, padx=6, pady=6)
        card.grid_columnconfigure(1, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=4, sticky="ew", padx=12, pady=(10, 4))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="额度监控", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=t["accent"]).grid(row=0, column=0, sticky="w")
        bb = ctk.CTkFrame(top, fg_color="transparent")
        bb.grid(row=0, column=1, sticky="e")
        self._btn(bb, "⟳", self._refresh_now, 12).pack(side="right", padx=2)
        self._btn(bb, "⚙", self._open_settings, 12).pack(side="right", padx=2)
        self._btn(bb, "□", self._toggle, 12).pack(side="right", padx=2)
        self._btn(bb, "✕", self.destroy, 12).pack(side="right", padx=2)

        ctk.CTkLabel(card, text="MIMO", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=t["accent"]).grid(row=1, column=0, sticky="w", padx=(12, 4), pady=3)
        self._mm_val = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), text_color=t["fg"])
        self._mm_val.grid(row=1, column=1, sticky="w", pady=3)
        self._mm_pct = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11), text_color=t["fg_dim"])
        self._mm_pct.grid(row=1, column=2, columnspan=2, sticky="w", padx=(8, 0), pady=3)

        ctk.CTkLabel(card, text="DS", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=t["accent"]).grid(row=2, column=0, sticky="w", padx=(12, 4), pady=3)
        self._md_val = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(family="Consolas", size=14, weight="bold"), text_color=t["fg"])
        self._md_val.grid(row=2, column=1, sticky="w", pady=3)
        self._md_st = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11), text_color=t["fg_dim"])
        self._md_st.grid(row=2, column=2, columnspan=2, sticky="w", padx=(8, 0), pady=3)

        self._mtime = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=9), text_color=t["fg_dim"])
        self._mtime.grid(row=3, column=0, columnspan=4, sticky="w", padx=12, pady=(4, 10))

    # ── data ─────────────────────────────────────────────────────

    def _restore(self):
        if self._mimo:
            self._show_mimo(self._mimo)
        if self._ds:
            self._show_ds(self._ds)

    def _show_mimo(self, r: MimoResult):
        self._mimo = r
        t = self.t
        if self.expanded and hasattr(self, "_m_st"):
            if r.ok:
                self._m_dot.configure(text_color=t["green"])
                self._m_st.configure(text="在线", text_color=t["green"])
                self._m_used.configure(text=fmt_token(r.used))
                self._m_lim.configure(text=fmt_token(r.limit))
                p = min(r.percent / 100 if r.percent > 1 else r.percent, 1.0)
                self._m_bar.set(p)
                self._m_bar.configure(progress_color=t["bar_green"] if p < .5 else t["bar_yellow"] if p < .8 else t["bar_red"])
                self._m_pct.configure(text=f"{p * 100:.2f}%")
            else:
                self._m_dot.configure(text_color=t["red"])
                self._m_st.configure(text=r.error[:15], text_color=t["red"])
        elif not self.expanded and hasattr(self, "_mm_val"):
            if r.ok:
                p = r.percent / 100 if r.percent > 1 else r.percent
                self._mm_val.configure(text=f"{fmt_token(r.used)}/{fmt_token(r.limit)}", text_color=t["green"])
                self._mm_pct.configure(text=f"{p * 100:.1f}%")
            else:
                self._mm_val.configure(text="失败", text_color=t["red"])

    def _show_ds(self, r: DeepseekResult):
        self._ds = r
        t = self.t
        if self.expanded and hasattr(self, "_d_st"):
            if r.ok:
                c = t["green"] if r.is_available else t["red"]
                self._d_dot.configure(text_color=c)
                self._d_st.configure(text="可用" if r.is_available else "不可用", text_color=c)
                self._d_tot.configure(text=f"¥{r.total:.2f}")
                self._d_gr.configure(text=f"¥{r.granted:.2f}")
                self._d_tp.configure(text=f"¥{r.topped_up:.2f}")
                self._d_av.configure(text="可用" if r.is_available else "不可用", text_color=c)
            else:
                self._d_dot.configure(text_color=t["red"])
                self._d_st.configure(text=r.error[:15], text_color=t["red"])
        elif not self.expanded and hasattr(self, "_md_val"):
            if r.ok:
                self._md_val.configure(text=f"¥{r.total:.2f}", text_color=t["green"])
                self._md_st.configure(text="可用" if r.is_available else "不可用")
            else:
                self._md_val.configure(text="失败", text_color=t["red"])

    # ── refresh ──────────────────────────────────────────────────

    def _do_refresh(self):
        mr = query_mimo()
        dr = query_deepseek()
        now = datetime.now().strftime("%H:%M:%S")
        self.after(0, lambda: self._show_mimo(mr))
        self.after(0, lambda: self._show_ds(dr))
        if self.expanded and hasattr(self, "_time"):
            self.after(0, lambda: self._time.configure(text=f"更新于 {now}"))
        if not self.expanded and hasattr(self, "_mtime"):
            self.after(0, lambda: self._mtime.configure(text=f"更新于 {now}"))

    def _refresh_now(self):
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _start_poll(self):
        def loop():
            while self._running:
                self._do_refresh()
                time.sleep(REFRESH_INTERVAL)
        threading.Thread(target=loop, daemon=True).start()

    def _toggle(self):
        self.expanded = not self.expanded
        self._rebuild()
        self._bind_drag()

    def destroy(self):
        self._running = False
        if hasattr(self, "_hotkey"):
            self._hotkey.stop()
        super().destroy()
