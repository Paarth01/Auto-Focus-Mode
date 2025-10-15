import subprocess
import psutil

def get_active_app():
    try:
        win_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
        wm_class = subprocess.check_output(['xprop', '-id', win_id, 'WM_CLASS']).decode().strip()
        app_name = wm_class.split(',')[-1].replace('"', '').strip().lower()
        return app_name
    except Exception:
        return None
