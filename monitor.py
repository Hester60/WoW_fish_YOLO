import win32gui
from screeninfo import get_monitors
import pyautogui

def get_window_handle(window_name):
    def callback(hwnd, extra):
        if window_name in win32gui.GetWindowText(hwnd):
            extra.append(hwnd)

    hwnd_list = []
    win32gui.EnumWindows(callback, hwnd_list)
    return hwnd_list


def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    return rect


def find_monitor_for_window(window_name):
    hwnd_list = get_window_handle(window_name)

    if not hwnd_list:
        return None, None
    hwnd = hwnd_list[0]
    window_rect = get_window_rect(hwnd)

    for monitor in get_monitors():
        if (monitor.x <= window_rect[0] <= monitor.x + monitor.width and
                monitor.y <= window_rect[1] <= monitor.y + monitor.height):
            return monitor, window_rect
    return None, window_rect

# Focus the game Window
def focus_window(game_name):
    window = pyautogui.getWindowsWithTitle(game_name)[0]
    window.activate()


# Retrieves position and resolution of the screen that contain the provided game name
def get_monitor_dict(game_name):
    monitor, rect = find_monitor_for_window(game_name)

    if monitor:
        monitor_dict = {
            "top": rect[1],
            "left": rect[0],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1]
        }

        return monitor_dict
    else:
        return None