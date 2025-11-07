import subprocess

def apply_focus_mode():
    subprocess.call(['gsettings', 'set', 'org.gnome.shell.extensions.dash-to-dock', 'dock-fixed', 'false'])
    subprocess.call(['gsettings', 'set', 'org.gnome.desktop.notifications', 'show-banners', 'false'])
    subprocess.call(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '1'])

def disable_focus_mode():
    subprocess.call(['gsettings', 'set', 'org.gnome.desktop.notifications', 'show-banners', 'true'])
    subprocess.call(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'])
