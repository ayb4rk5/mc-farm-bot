import pydirectinput
import keyboard
import time
import threading

running = False

def toggle():
    global running
    running = not running
    print("Durum:", "AÇIK" if running else "KAPALI")

keyboard.add_hotkey("F7", toggle)

def press_loop(key, delay):
    while True:
        if running:
            pydirectinput.keyDown(key)
            time.sleep(0.05)
            pydirectinput.keyUp(key)
        time.sleep(delay)

threading.Thread(target=press_loop, args=("c", 2), daemon=True).start()
threading.Thread(target=press_loop, args=("z", 10), daemon=True).start()
threading.Thread(target=press_loop, args=("v", 30), daemon=True).start()

print("F7 ile aç/kapat")

while True:
    time.sleep(1)