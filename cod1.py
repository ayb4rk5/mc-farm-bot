import keyboard
import time
import threading
import win32gui
import win32con
import win32api

running = False
target_hwnd = None
KEY_HOLD = 0.01
C_DELAY = 0.08
Z_DELAY = 1.0
V_DELAY = 2.5

def find_minecraft_window():
    def callback(hwnd, windows):
        title = win32gui.GetWindowText(hwnd)
        if any(name in title for name in ("Zulu", "Minecraft", "Lunar", "Badlion")):
            windows.append(hwnd)
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None

def press_key(hwnd, key):
    vk = ord(key.upper())
    scan = win32api.MapVirtualKey(vk, 0)
    lparam_down = 1 | (scan << 16)
    lparam_up = lparam_down | (1 << 30) | (1 << 31)
    # Fokus almadan sadece hedef pencereye tus mesaji gonder.
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, lparam_down)
    time.sleep(KEY_HOLD)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk, lparam_up)

def refresh_target_window():
    global target_hwnd
    while True:
        target_hwnd = find_minecraft_window()
        time.sleep(1)

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

keyboard.add_hotkey("F7", toggle)

def press_c():
    while True:
        if running:
            hwnd = target_hwnd
            if hwnd:
                press_key(hwnd, 'c')
        time.sleep(C_DELAY)
def press_z():
    while True:
        if running:
            hwnd = target_hwnd
            if hwnd:
                press_key(hwnd, 'z')
        time.sleep(Z_DELAY)

def press_v():
    while True:
        if running:
            hwnd = target_hwnd
            if hwnd:
                press_key(hwnd, 'v')
        time.sleep(V_DELAY)

threading.Thread(target=refresh_target_window, daemon=True).start()
threading.Thread(target=press_c, daemon=True).start()
threading.Thread(target=press_v, daemon=True).start()
threading.Thread(target=press_z, daemon=True).start()                                                               
print("F7 ile ac/kapat (sadece Minecraft'a gonderir, fokus almaz)", flush=True)

while True:
    time.sleep(1)