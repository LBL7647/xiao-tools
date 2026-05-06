"""Global hotkey registration using Win32 API."""

import ctypes
from ctypes import wintypes
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312

VK_MAP = {
    "A": 0x41, "B": 0x42, "C": 0x43, "D": 0x44, "E": 0x45, "F": 0x46,
    "G": 0x47, "H": 0x48, "I": 0x49, "J": 0x4A, "K": 0x4B, "L": 0x4C,
    "M": 0x4D, "N": 0x4E, "O": 0x4F, "P": 0x50, "Q": 0x51, "R": 0x52,
    "S": 0x53, "T": 0x54, "U": 0x55, "V": 0x56, "W": 0x57, "X": 0x58,
    "Y": 0x59, "Z": 0x5A,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73, "F5": 0x74, "F6": 0x75,
    "F7": 0x76, "F8": 0x77, "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "Space": 0x20, "Esc": 0x1B,
    "Insert": 0x2D, "Delete": 0x2E, "Home": 0x24, "End": 0x23,
    "PageUp": 0x21, "PageDown": 0x22,
    "Up": 0x26, "Down": 0x28, "Left": 0x25, "Right": 0x27,
}

MOD_MAP = {
    "Ctrl": MOD_CONTROL,
    "Alt": MOD_ALT,
    "Shift": MOD_SHIFT,
    "Win": MOD_WIN,
}

HOTKEY_ID = 1


def parse_hotkey(hotkey_str: str):
    parts = [p.strip() for p in hotkey_str.split("+")]
    modifiers = 0
    vk = 0
    for part in parts:
        if part in MOD_MAP:
            modifiers |= MOD_MAP[part]
        elif part.upper() in VK_MAP:
            vk = VK_MAP[part.upper()]
        elif part in VK_MAP:
            vk = VK_MAP[part]
    return modifiers | MOD_NOREPEAT, vk


class GlobalHotkey:
    def __init__(self, hotkey_str: str, callback):
        self.callback = callback
        self._running = False
        self._thread = None
        self.hotkey_str = hotkey_str
        self.modifiers, self.vk = parse_hotkey(hotkey_str)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        user32.PostThreadMessageA(self._thread.ident, 0x0010, 0, 0)  # WM_QUIT

    def _loop(self):
        # RegisterHotKey must be called from the thread that pumps messages
        if not user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.vk):
            self._running = False
            return

        msg = wintypes.MSG()
        while self._running:
            # GetMessageA blocks until a message arrives
            ret = user32.GetMessageA(ctypes.byref(msg), None, 0, 0)
            if ret == 0:  # WM_QUIT
                break
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self.callback()

        user32.UnregisterHotKey(None, HOTKEY_ID)


AVAILABLE_KEYS = sorted(VK_MAP.keys())
AVAILABLE_MODS = ["Ctrl", "Alt", "Shift", "Win"]
