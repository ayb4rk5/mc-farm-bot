import keyboard
import time
import threading
import win32gui
import win32con
import win32api

running = False
target_hwnd = None

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
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        # SetForegroundWindow bazi durumlarda izin hatasi verebilir.
        pass

    # Oyunlar genellikle PostMessage yerine fiziksel input benzeri olayi kabul eder.
    win32api.keybd_event(vk, scan, 0, 0)
    time.sleep(0.03)
    win32api.keybd_event(vk, scan, win32con.KEYEVENTF_KEYUP, 0)

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
            hwnd = find_minecraft_window()
            if hwnd:
                press_key(hwnd, 'c')
            else:
                print("C: pencere bulunamadi", flush=True)
        time.sleep(3)
def press_z():
    while True:
        if running:
            hwnd = find_minecraft_window()
            if hwnd:
                press_key(hwnd, 'z')
            else:
                print("Z: pencere bulunamadi", flush=True)
        time.sleep(10)

def press_v():
    while True:
        if running:
            hwnd = find_minecraft_window()
            if hwnd:
                press_key(hwnd, 'v')
            else:
                print("V: pencere bulunamadi", flush=True)
        time.sleep(20)

threading.Thread(target=press_c, daemon=True).start()
threading.Thread(target=press_v, daemon=True).start()
threading.Thread(target=press_z, daemon=True).start()                                                               
print("F7 ile ac/kapat (arka planda sadece Minecraft'a basar)", flush=True)

while True:
    time.sleep(1)