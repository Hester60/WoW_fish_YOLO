from monitor import get_monitor_dict, focus_window
import time
import random
import pyautogui
from ultralytics import YOLO
import mss
import numpy as np
import cv2
import keyboard
import pyfiglet
from colorama import init as initColor, Fore

initColor()

GAME_NAME = "World of Warcraft"
CAST_DUREATION_SEC = 20
FONT = pyfiglet.Figlet()

fishing_key = 'f'
is_fishing = False
total = 0
monitor_dict = get_monitor_dict(GAME_NAME)

print('Loading model...')
model = YOLO('best.pt')
model.to('cpu')
print('Model loaded! The CPU will be used to predict.')


def show_start_text():
    ascii_text = pyfiglet.figlet_format('WoW_Fish_YOLO')
    colored_text = Fore.CYAN + ascii_text + Fore.RESET
    print(colored_text)
    print(
        Fore.RED + "Please attach your fishing rod to the “f” key. Do not move your window. Make sure you have enabled the auto-loot feature in the game settings." + Fore.RESET)
    print(
        Fore.RED + "Additionally, for best results, zoom into the first person view and hide the UI by pressing ALT+W (or ALT+Z on QWERTY)." + Fore.RESET)
    print("You can stop the bot by pressing CTRL+C.")


def get_prediction():
    with mss.mss() as sct:

        sct_img = sct.grab(monitor_dict)
        img = np.array(sct_img)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=img_rgb, conf=0.8, verbose=False)

        if results:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                x_center_screen = monitor_dict['left'] + x_center
                y_center_screen = monitor_dict['top'] + y_center

                return x_center_screen, y_center_screen

        return None, None


# Right click on the bobber to loot the fish, player must enable automatic looting
def catch_fish(x_center, y_center):
    global total

    time.sleep(0.1)
    pyautogui.moveTo(x_center, y_center)
    print(Fore.GREEN + f'Fish caught at position x: {x_center}, y: {y_center} !' + Fore.RESET)
    time.sleep(0.1)
    pyautogui.click(button='right')
    total += 1


def cast():
    global is_fishing

    print(Fore.CYAN + '\nStart fishing.' + Fore.RESET)
    pyautogui.press(fishing_key)

    print(Fore.CYAN + 'Waiting for a fish...' + Fore.RESET)

    start_time = time.time()
    caught = False
    while (time.time() - start_time < CAST_DUREATION_SEC) and is_fishing:
        x_center, y_center = get_prediction()

        if (x_center is not None and y_center is not None):
            catch_fish(x_center, y_center)
            caught = True
            stop()
            break

    if (not caught):
        print(
            Fore.MAGENTA + "No fish caught :( Sometimes the bot can miss. Be sure you are in first person view, have hidden your UI and the bobber is visible on screen" + Fore.RESET)

    restart()


def start():
    global is_fishing
    is_fishing = True

    try:
        focus_window(GAME_NAME)
    except Exception:
        print(Fore.RED + f"No screens with the {GAME_NAME} window were found. Did you launch the game?" + Fore.RESET)
        exit(1)

    cast()


def stop():
    global is_fishing
    is_fishing = False
    print(f"You caught {total} fish this session.")


def restart():
    time.sleep(2)
    start()


def init():
    try:
        start()
    except KeyboardInterrupt:
        print(Fore.RED + 'Keyboard interrupt received. Exiting...' + Fore.RESET)
        stop()
    finally:
        print(Fore.RED + 'Clean up and exit.' + Fore.RESET)


if __name__ == "__main__":
    show_start_text()
    init()
