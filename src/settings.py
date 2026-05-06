"""Persistent settings and settings panel."""

import json
import os
import customtkinter as ctk

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULTS = {
    "mimo_cookie": "",
    "ds_api_key": "",
    "theme": "dark",
    "alpha": 0.88,
    "refresh_interval": 2,
    "hotkey": "Ctrl+Alt+Q",
}

_cache = None


def load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    data = dict(DEFAULTS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            data.update(saved)
        except Exception:
            pass
    _cache = data
    return data


def save(data: dict):
    global _cache
    _cache = data
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get(key: str, default=None):
    return load().get(key, default)


def set(key: str, value):
    data = load()
    data[key] = value
    save(data)


class SettingsPanel(ctk.CTkToplevel):
    """Settings popup for editing MIMO cookie, DeepSeek API key, and hotkey."""

    def __init__(self, master, on_save):
        super().__init__(master)
        self.on_save = on_save
        self.title("设置")
        self.geometry("500x440")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0e0e18")
        self.protocol("WM_DELETE_WINDOW", self._close)

        data = load()

        ctk.CTkLabel(self, text="设置", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#7b8cff").pack(pady=(16, 12))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(0, 8))
        form.grid_columnconfigure(1, weight=1)

        # ── MIMO Cookie ──
        ctk.CTkLabel(form, text="MIMO Cookie", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#eeeeff").grid(row=0, column=0, sticky="nw", padx=(0, 12), pady=(6, 0))
        self.mimo_entry = ctk.CTkTextbox(form, height=70, fg_color="#1a1a2e",
                                         border_color="#2a2a45", border_width=1,
                                         text_color="#eeeeff", font=ctk.CTkFont(size=10),
                                         corner_radius=8)
        self.mimo_entry.grid(row=0, column=1, sticky="ew", pady=4)
        if data.get("mimo_cookie"):
            self.mimo_entry.insert("1.0", data["mimo_cookie"])

        # ── DeepSeek API Key ──
        ctk.CTkLabel(form, text="DeepSeek Key", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#eeeeff").grid(row=1, column=0, sticky="nw", padx=(0, 12), pady=(6, 0))
        self.ds_entry = ctk.CTkTextbox(form, height=40, fg_color="#1a1a2e",
                                       border_color="#2a2a45", border_width=1,
                                       text_color="#eeeeff", font=ctk.CTkFont(size=10),
                                       corner_radius=8)
        self.ds_entry.grid(row=1, column=1, sticky="ew", pady=4)
        if data.get("ds_api_key"):
            self.ds_entry.insert("1.0", data["ds_api_key"])

        # ── Hotkey ──
        ctk.CTkLabel(form, text="显示/隐藏快捷键", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#eeeeff").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=(10, 0))

        hk_frame = ctk.CTkFrame(form, fg_color="transparent")
        hk_frame.grid(row=2, column=1, sticky="ew", pady=(10, 0))

        current_hk = data.get("hotkey", DEFAULTS["hotkey"])
        parts = [p.strip() for p in current_hk.split("+")]
        key_part = parts[-1] if parts else "Q"
        mod_parts = parts[:-1] if len(parts) > 1 else ["Ctrl", "Alt"]

        # modifier checkboxes
        self._mod_vars = {}
        mod_frame = ctk.CTkFrame(hk_frame, fg_color="transparent")
        mod_frame.pack(side="left")
        for mod in ["Ctrl", "Alt", "Shift", "Win"]:
            var = ctk.BooleanVar(value=mod in mod_parts)
            self._mod_vars[mod] = var
            cb = ctk.CTkCheckBox(mod_frame, text=mod, variable=var,
                                 font=ctk.CTkFont(size=10),
                                 text_color="#eeeeff", fg_color="#2a2a45",
                                 border_color="#3a3a5a", hover_color="#7b8cff",
                                 checkmark_color="#eeeeff", width=20, height=20,
                                 corner_radius=4)
            cb.pack(side="left", padx=(0, 8))

        # key dropdown
        from hotkey import AVAILABLE_KEYS
        self._key_var = ctk.StringVar(value=key_part)
        key_menu = ctk.CTkOptionMenu(hk_frame, values=AVAILABLE_KEYS,
                                     variable=self._key_var,
                                     width=80, height=28,
                                     fg_color="#1a1a2e", button_color="#2a2a45",
                                     button_hover_color="#3a3a5a",
                                     dropdown_fg_color="#1a1a2e",
                                     dropdown_hover_color="#2a2a45",
                                     font=ctk.CTkFont(size=10),
                                     corner_radius=6)
        key_menu.pack(side="left", padx=(8, 0))

        # hint
        ctk.CTkLabel(form, text="留空则使用程序内置默认值 · 快捷键修改后需重启生效",
                     font=ctk.CTkFont(size=9),
                     text_color="#666688").grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 4))

        # ── Buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(4, 16))

        ctk.CTkButton(btn_frame, text="保存", width=100, height=32,
                      fg_color="#7b8cff", hover_color="#9aa5ff",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, command=self._save).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_frame, text="取消", width=100, height=32,
                      fg_color="#2a2a45", hover_color="#3a3a55",
                      font=ctk.CTkFont(size=12),
                      corner_radius=8, command=self._close).pack(side="right")

        self.grab_set()
        self.focus_force()

    def _build_hotkey_str(self):
        mods = [m for m, v in self._mod_vars.items() if v.get()]
        key = self._key_var.get()
        if not mods:
            mods = ["Ctrl", "Alt"]
        return "+".join(mods + [key])

    def _save(self):
        data = load()
        data["mimo_cookie"] = self.mimo_entry.get("1.0", "end-1c").strip()
        data["ds_api_key"] = self.ds_entry.get("1.0", "end-1c").strip()
        data["hotkey"] = self._build_hotkey_str()
        save(data)
        self.on_save()
        self._close()

    def _close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
