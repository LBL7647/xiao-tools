import tkinter as tk
from tkinter import font as tkfont
import requests
import threading
import time
from datetime import datetime

MIMO_URL = "https://platform.xiaomimimo.com/api/v1/tokenPlan/usage"
MIMO_COOKIE = 'cookie-preferences=%7B%22analytical%22%3Afalse%2C%22functional%22%3Afalse%7D; api-platform_serviceToken="yVHEDQlNiFT1WavLtPFnezgniFL7QG9QG6y5wnSX8tEQ6/HJ8F1s3gJPXPp6oUYCF+TFKeXpIyzRFVgx6Hzd97TF2Ui1ebZ1TXJiv1Q1v2aqhE2+gv7qDJ4qqcxe3evL1jVbDn2LL2hIIyMEUxbeFu0uF6fcJqWH2VU0ieTNkP+CzBXzuVhjSGSIsmts8nK86m2UYHQ7cI9vqKH+tPjjwlhXMtbftnKldkyZEcmrVaGw0iR59Sbi3dbVbcCA20uzIivjUGMNfZXYQY5CtBkkLZoa5VM5O7LjbOE3WmnrcPaRxxO2FzjqrpSV4uhwNUJT0VWx3HiqOCIq0sD3q3QeaNh+1leApDNequmMjohOv8g="; userId=1323241875; api-platform_slh="opRqhehpnBSbxhjkWfEj9iHfl3c="; api-platform_ph="vlyXfCB4KR6oi9fS+7U1uA=="'
DS_URL = "https://api.deepseek.com/user/balance"
DS_TOKEN = "Bearer sk-03770f45145247698247b963a75945c0"
NO_PROXY = {"http": None, "https": None}

THEMES = {
    "dark": {
        "bg": "#16161e",
        "card": "#222233",
        "border": "#333348",
        "fg": "#e0e0e0",
        "fg_dim": "#888899",
        "accent": "#7c8cf8",
        "green": "#66d9a0",
        "yellow": "#f0c050",
        "red": "#f06070",
        "bar_bg": "#2a2a3a",
        "title": "#a0a8ff",
        "alpha": 0.88,
    },
    "glass": {
        "bg": "#0e0e1a",
        "card": "#1a1a30",
        "border": "#3a3a55",
        "fg": "#e0e0ff",
        "fg_dim": "#7777aa",
        "accent": "#8888ff",
        "green": "#55ffaa",
        "yellow": "#ffdd55",
        "red": "#ff5577",
        "bar_bg": "#2a2a44",
        "title": "#bbbbff",
        "alpha": 0.78,
    },
    "light": {
        "bg": "#eaeaf0",
        "card": "#ffffff",
        "border": "#cccce0",
        "fg": "#2a2a3a",
        "fg_dim": "#8888aa",
        "accent": "#5566dd",
        "green": "#22aa66",
        "yellow": "#cc9900",
        "red": "#dd3344",
        "bar_bg": "#dddde8",
        "title": "#4455bb",
        "alpha": 0.92,
    },
}


def rounded_rect(canvas, x, y, w, h, r, **kwargs):
    points = [
        x + r, y, x + w - r, y, x + w, y, x + w, y + r,
        x + w, y + h - r, x + w, y + h, x + w - r, y + h,
        x + r, y + h, x, y + h, x, y + h - r, x, y + r, x, y,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class GlassCard(tk.Frame):
    def __init__(self, parent, theme, **kw):
        super().__init__(parent, bg=theme["bg"], **kw)
        self.theme = theme
        self.canvas = tk.Canvas(self, bg=theme["bg"], highlightthickness=0, height=0)
        self.canvas.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg="")
        self.canvas_window = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.canvas.configure(height=event.height)
        self.canvas.coords(self.canvas_window, 0, 0)
        self.canvas.itemconfig(self.canvas_window, width=event.width, height=event.height)
        self.canvas.delete("bg")
        t = self.theme
        rounded_rect(self.canvas, 1, 1, event.width - 2, event.height - 2, 14,
                     fill=t["card"], outline=t["border"], width=1, tags="bg")
        self.canvas.tag_lower("bg")


class BalanceWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("API 额度监控")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-toolwindow", True)

        self.theme_name = "dark"
        self.theme = THEMES["dark"]
        self.expanded = True
        self.width = 340
        self.height_expanded = 310
        self.height_mini = 46
        self.width_mini = 160

        self.root.configure(bg=self.theme["bg"])
        self.root.attributes("-alpha", self.theme["alpha"])
        self.root.geometry(f"{self.width}x{self.height_expanded}+120+120")

        self._drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<Double-Button-1>", lambda e: self._toggle_mini())

        self._build_ui()
        self._apply_theme()
        self._start_refresh()

    def _build_ui(self):
        t = self.theme
        self.root_bg = tk.Frame(self.root, bg=t["bg"])
        self.root_bg.pack(fill="both", expand=True)

        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self):
        t = self.theme
        self.header = tk.Frame(self.root_bg, bg=t["bg"])
        self.header.pack(fill="x", padx=12, pady=(10, 4))

        self.title_label = tk.Label(self.header, text="API 额度监控", font=("Segoe UI Semibold", 12),
                                    bg=t["bg"], fg=t["title"])
        self.title_label.pack(side="left")

        btn_frame = tk.Frame(self.header, bg=t["bg"])
        btn_frame.pack(side="right")

        self.btn_theme = tk.Label(btn_frame, text="◑", font=("Segoe UI", 13), bg=t["bg"],
                                  fg=t["fg_dim"], cursor="hand2")
        self.btn_theme.pack(side="right", padx=(6, 0))
        self.btn_theme.bind("<Button-1>", lambda e: self._cycle_theme())
        self.btn_theme.bind("<Enter>", lambda e: self.btn_theme.config(fg=t["accent"]))
        self.btn_theme.bind("<Leave>", lambda e: self.btn_theme.config(fg=t["fg_dim"]))

        self.btn_mini = tk.Label(btn_frame, text="—", font=("Segoe UI", 11, "bold"), bg=t["bg"],
                                 fg=t["fg_dim"], cursor="hand2")
        self.btn_mini.pack(side="right", padx=(6, 0))
        self.btn_mini.bind("<Button-1>", lambda e: self._toggle_mini())
        self.btn_mini.bind("<Enter>", lambda e: self.btn_mini.config(fg=t["accent"]))
        self.btn_mini.bind("<Leave>", lambda e: self.btn_mini.config(fg=t["fg_dim"]))

        self.btn_refresh = tk.Label(btn_frame, text="⟳", font=("Segoe UI", 14), bg=t["bg"],
                                    fg=t["fg_dim"], cursor="hand2")
        self.btn_refresh.pack(side="right", padx=(6, 0))
        self.btn_refresh.bind("<Button-1>", lambda e: self._manual_refresh())
        self.btn_refresh.bind("<Enter>", lambda e: self.btn_refresh.config(fg=t["accent"]))
        self.btn_refresh.bind("<Leave>", lambda e: self.btn_refresh.config(fg=t["fg_dim"]))

        self.btn_close = tk.Label(btn_frame, text="✕", font=("Segoe UI", 11), bg=t["bg"],
                                  fg=t["fg_dim"], cursor="hand2")
        self.btn_close.pack(side="right", padx=(6, 0))
        self.btn_close.bind("<Button-1>", lambda e: self.root.destroy())
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(fg=t["red"]))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(fg=t["fg_dim"]))

    def _build_body(self):
        t = self.theme
        self.body = tk.Frame(self.root_bg, bg=t["bg"])
        self.body.pack(fill="both", expand=True, padx=10, pady=(2, 2))

        # --- MIMO card ---
        self.mimo_card = GlassCard(self.body, t)
        self.mimo_card.pack(fill="x", pady=(0, 6))
        mf = self.mimo_card.inner
        mf.configure(bg=t["card"])

        mh = tk.Frame(mf, bg=t["card"])
        mh.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(mh, text="MIMO", font=("Segoe UI Semibold", 10), bg=t["card"], fg=t["accent"]).pack(side="left")
        self.mimo_status = tk.Label(mh, text="查询中…", font=("Segoe UI", 8), bg=t["card"], fg=t["yellow"])
        self.mimo_status.pack(side="right")

        mi = tk.Frame(mf, bg=t["card"])
        mi.pack(fill="x", padx=12, pady=(0, 1))
        tk.Label(mi, text="已用", font=("Segoe UI", 9), bg=t["card"], fg=t["fg_dim"]).pack(side="left")
        self.mimo_used = tk.Label(mi, text="—", font=("Consolas", 10, "bold"), bg=t["card"], fg=t["fg"])
        self.mimo_used.pack(side="right")

        ml = tk.Frame(mf, bg=t["card"])
        ml.pack(fill="x", padx=12, pady=(0, 1))
        tk.Label(ml, text="额度", font=("Segoe UI", 9), bg=t["card"], fg=t["fg_dim"]).pack(side="left")
        self.mimo_limit = tk.Label(ml, text="—", font=("Consolas", 10, "bold"), bg=t["card"], fg=t["fg"])
        self.mimo_limit.pack(side="right")

        bar_f = tk.Frame(mf, bg=t["card"])
        bar_f.pack(fill="x", padx=12, pady=(6, 2))
        self.mimo_bar_bg = tk.Frame(bar_f, bg=t["bar_bg"], height=6)
        self.mimo_bar_bg.pack(fill="x")
        self.mimo_bar_bg.pack_propagate(False)
        self.mimo_bar = tk.Frame(self.mimo_bar_bg, bg=t["green"], height=6)

        self.mimo_percent = tk.Label(mf, text="0%", font=("Segoe UI", 8), bg=t["card"], fg=t["fg_dim"])
        self.mimo_percent.pack(anchor="e", padx=12, pady=(0, 10))

        # --- DeepSeek card ---
        self.ds_card = GlassCard(self.body, t)
        self.ds_card.pack(fill="x")
        df = self.ds_card.inner
        df.configure(bg=t["card"])

        dh = tk.Frame(df, bg=t["card"])
        dh.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(dh, text="DeepSeek", font=("Segoe UI Semibold", 10), bg=t["card"], fg=t["accent"]).pack(side="left")
        self.ds_status = tk.Label(dh, text="查询中…", font=("Segoe UI", 8), bg=t["card"], fg=t["yellow"])
        self.ds_status.pack(side="right")

        db = tk.Frame(df, bg=t["card"])
        db.pack(fill="x", padx=12, pady=(0, 1))
        tk.Label(db, text="余额", font=("Segoe UI", 9), bg=t["card"], fg=t["fg_dim"]).pack(side="left")
        self.ds_total = tk.Label(db, text="—", font=("Consolas", 10, "bold"), bg=t["card"], fg=t["fg"])
        self.ds_total.pack(side="right")

        dg = tk.Frame(df, bg=t["card"])
        dg.pack(fill="x", padx=12, pady=(0, 1))
        tk.Label(dg, text="赠送", font=("Segoe UI", 9), bg=t["card"], fg=t["fg_dim"]).pack(side="left")
        self.ds_granted = tk.Label(dg, text="—", font=("Consolas", 10, "bold"), bg=t["card"], fg=t["fg"])
        self.ds_granted.pack(side="right")

        self.ds_avail = tk.Label(df, text="", font=("Segoe UI", 8), bg=t["card"], fg=t["fg_dim"])
        self.ds_avail.pack(anchor="e", padx=12, pady=(0, 10))

    def _build_footer(self):
        t = self.theme
        self.footer = tk.Frame(self.root_bg, bg=t["bg"])
        self.footer.pack(fill="x", padx=12, pady=(2, 8))
        self.update_time = tk.Label(self.footer, text="等待更新…", font=("Segoe UI", 8), bg=t["bg"], fg=t["fg_dim"])
        self.update_time.pack(side="left")
        self.auto_label = tk.Label(self.footer, text="2s 自动刷新", font=("Segoe UI", 8), bg=t["bg"], fg=t["fg_dim"])
        self.auto_label.pack(side="right")

    def _build_mini_ui(self):
        t = self.theme
        self.mini_frame = tk.Frame(self.root_bg, bg=t["bg"])
        self.mini_frame.pack(fill="both", expand=True, padx=8, pady=6)

        top = tk.Frame(self.mini_frame, bg=t["bg"])
        top.pack(fill="x")
        tk.Label(top, text="额度", font=("Segoe UI Semibold", 10), bg=t["bg"], fg=t["title"]).pack(side="left")

        self.mini_expand = tk.Label(top, text="□", font=("Segoe UI", 10), bg=t["bg"],
                                    fg=t["fg_dim"], cursor="hand2")
        self.mini_expand.pack(side="right")
        self.mini_expand.bind("<Button-1>", lambda e: self._toggle_mini())
        self.mini_expand.bind("<Enter>", lambda e: self.mini_expand.config(fg=t["accent"]))
        self.mini_expand.bind("<Leave>", lambda e: self.mini_expand.config(fg=t["fg_dim"]))

        self.mini_close = tk.Label(top, text="✕", font=("Segoe UI", 10), bg=t["bg"],
                                   fg=t["fg_dim"], cursor="hand2")
        self.mini_close.pack(side="right", padx=(0, 6))
        self.mini_close.bind("<Button-1>", lambda e: self.root.destroy())
        self.mini_close.bind("<Enter>", lambda e: self.mini_close.config(fg=t["red"]))
        self.mini_close.bind("<Leave>", lambda e: self.mini_close.config(fg=t["fg_dim"]))

        row = tk.Frame(self.mini_frame, bg=t["bg"])
        row.pack(fill="x", pady=(6, 0))

        self.mini_mimo = tk.Label(row, text="MIMO: —", font=("Consolas", 9), bg=t["bg"], fg=t["fg"])
        self.mini_mimo.pack(side="left")
        self.mini_ds = tk.Label(row, text="DS: —", font=("Consolas", 9), bg=t["bg"], fg=t["fg"])
        self.mini_ds.pack(side="right")

    def _toggle_mini(self):
        self.expanded = not self.expanded
        for w in self.root_bg.winfo_children():
            w.destroy()
        if self.expanded:
            self.root.geometry(f"{self.width}x{self.height_expanded}")
            self._build_ui()
        else:
            self.root.geometry(f"{self.width_mini}x{self.height_mini}")
            self._build_mini_ui()
        self._apply_theme()

    def _cycle_theme(self):
        names = list(THEMES.keys())
        idx = (names.index(self.theme_name) + 1) % len(names)
        self.theme_name = names[idx]
        self.theme = THEMES[self.theme_name]
        self.root.attributes("-alpha", self.theme["alpha"])
        for w in self.root_bg.winfo_children():
            w.destroy()
        if self.expanded:
            self._build_ui()
        else:
            self._build_mini_ui()
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        self.root.configure(bg=t["bg"])
        self.root_bg.configure(bg=t["bg"])
        for attr in ["header", "body", "footer"]:
            if hasattr(self, attr):
                getattr(self, attr).configure(bg=t["bg"])
        if hasattr(self, "mini_frame"):
            self.mini_frame.configure(bg=t["bg"])

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _fmt(self, n):
        if n >= 1_000_000_000:
            return f"{n / 1_000_000_000:.2f}B"
        if n >= 1_000_000:
            return f"{n / 1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)

    def _query_mimo(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*", "Content-Type": "application/json",
                "Referer": "https://platform.xiaomimimo.com/console/plan-manage",
                "Cookie": MIMO_COOKIE, "x-timezone": "Asia/Hong_Kong",
            }
            resp = requests.get(MIMO_URL, headers=headers, timeout=15, proxies=NO_PROXY)
            data = resp.json()
            if data.get("code") == 0:
                usage = data["data"]["usage"]
                item = next((i for i in usage["items"] if i["name"] == "plan_total_token"), usage["items"][0])
                return {"ok": True, "used": item["used"], "limit": item["limit"], "percent": usage["percent"]}
            return {"ok": False, "error": data.get("message", "未知错误")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _query_ds(self):
        try:
            headers = {"Accept": "application/json", "Authorization": DS_TOKEN}
            resp = requests.get(DS_URL, headers=headers, timeout=15, proxies=NO_PROXY)
            data = resp.json()
            if "balance_infos" in data and data["balance_infos"]:
                info = data["balance_infos"][0]
                return {"ok": True, "is_available": data.get("is_available", False),
                        "total": float(info["total_balance"]), "granted": float(info["granted_balance"]),
                        "topped_up": float(info["topped_up_balance"])}
            return {"ok": False, "error": "无余额数据"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _update_mimo(self, r):
        t = self.theme
        if r["ok"]:
            self.mimo_status.config(text="在线", fg=t["green"])
            self.mimo_used.config(text=self._fmt(r["used"]))
            self.mimo_limit.config(text=self._fmt(r["limit"]))
            pct = r["percent"] / 100 if r["percent"] > 1 else r["percent"]
            color = t["green"] if pct < 0.5 else t["yellow"] if pct < 0.8 else t["red"]
            self.mimo_bar.config(bg=color)
            self.mimo_bar_bg.update_idletasks()
            w = max(1, int(self.mimo_bar_bg.winfo_width() * min(pct, 1.0)))
            self.mimo_bar.place(x=0, y=0, relheight=1.0, width=w)
            self.mimo_percent.config(text=f"{pct * 100:.2f}%")
        else:
            self.mimo_status.config(text="失败", fg=t["red"])
            self.mimo_used.config(text="—")
            self.mimo_limit.config(text="—")
            self.mimo_percent.config(text=r.get("error", "")[:30])

    def _update_ds(self, r):
        t = self.theme
        if r["ok"]:
            st = "可用" if r["is_available"] else "不可用"
            sc = t["green"] if r["is_available"] else t["red"]
            self.ds_status.config(text=st, fg=sc)
            self.ds_total.config(text=f"¥{r['total']:.2f}")
            self.ds_granted.config(text=f"¥{r['granted']:.2f}")
            self.ds_avail.config(text=f"充值 ¥{r['topped_up']:.2f}")
        else:
            self.ds_status.config(text="失败", fg=t["red"])
            self.ds_total.config(text="—")
            self.ds_granted.config(text="—")
            self.ds_avail.config(text=r.get("error", "")[:30])

    def _update_mini(self, mr, dr):
        t = self.theme
        if mr["ok"]:
            self.mini_mimo.config(text=f"MIMO: {self._fmt(mr['used'])}/{self._fmt(mr['limit'])}", fg=t["green"])
        else:
            self.mini_mimo.config(text="MIMO: 失败", fg=t["red"])
        if dr["ok"]:
            self.mini_ds.config(text=f"DS: ¥{dr['total']:.2f}", fg=t["green"])
        else:
            self.mini_ds.config(text="DS: 失败", fg=t["red"])

    def _refresh(self):
        mr = self._query_mimo()
        dr = self._query_ds()
        now = datetime.now().strftime("%H:%M:%S")
        if self.expanded and hasattr(self, "mimo_status"):
            self.root.after(0, lambda: self._update_mimo(mr))
            self.root.after(0, lambda: self._update_ds(dr))
            self.root.after(0, lambda: self.update_time.config(text=f"更新于 {now}"))
        elif not self.expanded and hasattr(self, "mini_mimo"):
            self.root.after(0, lambda: self._update_mini(mr, dr))

    def _manual_refresh(self):
        threading.Thread(target=self._refresh, daemon=True).start()

    def _start_refresh(self):
        def loop():
            while True:
                self._refresh()
                time.sleep(2)

        threading.Thread(target=loop, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BalanceWidget()
    app.run()
