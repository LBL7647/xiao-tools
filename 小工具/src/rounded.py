import ctypes
from ctypes import wintypes


def apply_rounded_corners(hwnd, radius=16):
    """Apply rounded corners to a window using Win32 DWM API."""
    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        preference = wintypes.DWORD(DWMWCP_ROUND)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(preference),
            ctypes.sizeof(preference),
        )
        DWMWA_BORDER_COLOR = 34
        DWMWA_COLOR_DEFAULT = 0xFFFFFFFF
        color = wintypes.DWORD(DWMWA_COLOR_DEFAULT)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_BORDER_COLOR,
            ctypes.byref(color),
            ctypes.sizeof(color),
        )
        return True
    except Exception:
        return False
