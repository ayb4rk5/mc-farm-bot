import keyboard
import time
import threading
import socket
import sys
import win32gui
import win32con
import win32api

# ===== Ayarlar (saniye cinsinden) =====
KEY_HOLD = 0.01          # tuş basılı süresi (down->up)
RCLICK_HOLD = 0.02      # sağ tık basılı süresi

# Tuş gecikmeleri
C_DELAY = 1.5          # 'c'
Z_DELAY = 4.0          # 'z'
V_DELAY = 10.0         # 'v'

# Sağ tık pulse aralığı (basılı tutuyormuş hissi için)
RCLICK_DELAY = 0.35

# Zamanlayıcılar
POLL_DELAY = 0.01
WINDOW_REFRESH_DELAY = 0.2

# Aynı anda spam olmasın: global minimum aralık
PRESS_GAP = 0.20

# Kullanıcı çok küçük değer girerse spam olmasın diye clamp
MIN_C_DELAY = 0.8
MIN_Z_DELAY = 2.0
MIN_V_DELAY = 4.0
MIN_RCLICK_DELAY = 0.15
MIN_PRESS_GAP = 0.12

# Tek instance kilidi (aynı anda birden fazla çalışmasın)
_LOCK_PORT = 47653

running = False
target_hwnd = None

_lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    _lock_sock.bind(("127.0.0.1", _LOCK_PORT))
except OSError:
    print("cod1.py zaten calisiyor. Once eskiyi kapat (Ctrl+C).", flush=True)
    sys.exit(1)


def find_minecraft_window():
    def callback(hwnd, windows):
        try:
            title = win32gui.GetWindowText(hwnd)
        except Exception:
            return
        if any(name in title for name in ("Zulu", "Minecraft", "Lunar", "Badlion")):
            windows.append(hwnd)

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def press_key(hwnd, key_char: str):
    vk = ord(key_char.upper())
    scan = win32api.MapVirtualKey(vk, 0)

    lparam_down = 1 | (scan << 16)
    lparam_up = lparam_down | (1 << 30) | (1 << 31)

    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, lparam_down)
    time.sleep(KEY_HOLD)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk, lparam_up)


def press_right_click(hwnd):
    # Client rect icinden merkeze yakın bir nokta seç.
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    x = max(1, (right - left) // 2)
    y = max(1, (bottom - top) // 2)
    lparam = (y << 16) | x

    # Bazi client'larda hareket olayi ile baslamak gerekiyor.
    win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
    time.sleep(RCLICK_HOLD)
    win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)

    # Fallback (daha uyumlu istemciler icin): cok nadir ikinci kez dene.
    # Not: bu ikinci deneme çift klik hissi yaratabilir; gerekirse kaldırabiliriz.
    try:
        win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lparam)
        win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, lparam)
    except Exception:
        pass


def refresh_target_window():
    global target_hwnd
    while True:
        if not target_hwnd or not win32gui.IsWindow(target_hwnd):
            target_hwnd = find_minecraft_window()
        time.sleep(WINDOW_REFRESH_DELAY)


def toggle():
    global running
    running = not running
    print("Durum:", "AÇIK" if running else "KAPALI", flush=True)
    if running:
        hwnd = find_minecraft_window()
        if hwnd:
            print(f"Pencere bulundu: HWND={hwnd}", flush=True)
        else:
            print("Minecraft/Zulu penceresi bulunamadi.", flush=True)


def key_scheduler():
    # clamp (spam engelleme)
    c_delay = max(float(C_DELAY), MIN_C_DELAY)
    z_delay = max(float(Z_DELAY), MIN_Z_DELAY)
    v_delay = max(float(V_DELAY), MIN_V_DELAY)
    rclick_delay = max(float(RCLICK_DELAY), MIN_RCLICK_DELAY)
    press_gap = max(float(PRESS_GAP), MIN_PRESS_GAP)

    base = time.perf_counter()
    next_c = base
    next_z = base + c_delay / 4.0
    next_v = base + c_delay / 2.0
    next_rclick = base + 0.10

    last_press = 0.0

    while True:
        if running:
            hwnd = target_hwnd
            if not hwnd or not win32gui.IsWindow(hwnd):
                time.sleep(WINDOW_REFRESH_DELAY)
                continue

            now = time.perf_counter()

            # Her turda sadece 1 aksiyon isle (yakın zamanlılar çakışmasın).
            schedule = [
                ("c", next_c),
                ("z", next_z),
                ("v", next_v),
                ("rclick", next_rclick),
            ]
            action, due_at = min(schedule, key=lambda item: item[1])

            if now >= due_at and (now - last_press) >= press_gap:
                # Tek tuş/tek aksiyon
                if action == "c":
                    press_key(hwnd, "c")
                    next_c = now + c_delay
                elif action == "z":
                    press_key(hwnd, "z")
                    next_z = now + z_delay
                elif action == "v":
                    press_key(hwnd, "v")
                    next_v = now + v_delay
                else:
                    press_right_click(hwnd)
                    next_rclick = now + rclick_delay

                last_press = time.perf_counter()

        time.sleep(POLL_DELAY)


threading.Thread(target=refresh_target_window, daemon=True).start()
threading.Thread(target=key_scheduler, daemon=True).start()

keyboard.add_hotkey("F7", toggle)
print("F7 ile ac/kapat (Minecraft'a gonderir, fokus almaz)", flush=True)

while True:
    time.sleep(1)