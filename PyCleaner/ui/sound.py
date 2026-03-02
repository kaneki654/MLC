import os
import threading
import platform

def play_sound(type="click"):
    def _play():
        try:
            sys = platform.system()
            if sys == "Linux":
                # Requires 'sox' or beep, fallback to terminal bell
                print('\a') 
            elif sys == "Windows":
                import winsound
                if type == "click": winsound.Beep(1000, 50)
                elif type == "success": winsound.Beep(800, 100); winsound.Beep(1200, 200)
        except: pass
    threading.Thread(target=_play, daemon=True).start()
