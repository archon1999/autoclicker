import datetime
import tkinter
import threading
import traceback
import time
import win32api
import win32con
import keyboard
import pyautogui

from tkinter import END, ttk
from tkinter.font import BOLD


class StoppableThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def mouse_click(x, y):
    pyautogui.click(x, y)


class Item():
    def __init__(self):
        self.is_active_var = tkinter.IntVar(value=1)
        self.is_active = tkinter.Checkbutton(variable=self.is_active_var)
        self.is_active.select()
        self.path = tkinter.Text(width=30, height=1)
        self.minutes = tkinter.Text(width=6, height=1)
        self.x = tkinter.Text(width=7, height=1)
        self.y = tkinter.Text(width=7, height=1)
        self.hotkey = ttk.Combobox(root, values=['F5', 'F6'], width=7)
        self.hotkey.current(0)
        self.last_go = None

    def go(self):
        path = self.path.get("1.0", END).strip()
        minutes = int(self.minutes.get("1.0", END).strip())
        if self.last_go:
            seconds = (datetime.datetime.now() - self.last_go).total_seconds()
            if seconds // 60 < minutes:
                return

        self.last_go = datetime.datetime.now()
        x = int(self.x.get("1.0", END).strip())
        y = int(self.y.get("1.0", END).strip())
        with open(path, 'r') as file:
            text = file.read().strip()
            if text == '2':
                self.is_active_var.set(0)
            elif text == '1':
                pass
            elif text == '0':
                mouse_click(x, y)

        hotkey = self.hotkey.get().strip()
        keyboard.press(hotkey)


items: list[Item] = []
start_process: StoppableThread = None
root = None
add_button = None
start_button = None
stop_button = None


def start():
    while True:
        for item in items:
            if item.is_active_var.get():
                try:
                    item.go()
                except Exception:
                    traceback.print_exc()

            replace_items()
        time.sleep(10)


def start_button_handler():
    print('start')
    global start_process
    if start_process:
        stop_button_handler()

    start_process = StoppableThread(target=start)
    start_process.start()


def stop_button_handler():
    print('stop')
    global start_process
    if start_process.is_alive():
        start_process.stop()
    start_process = None


def replace_items():
    cur_y = 60
    for item in items:
        item.is_active.place(x=10, y=cur_y)
        item.path.place(x=40, y=cur_y)
        item.minutes.place(x=300, y=cur_y)
        item.x.place(x=400, y=cur_y)
        item.y.place(x=500, y=cur_y)
        item.hotkey.place(x=600, y=cur_y)
        cur_y += 50

    global add_button, start_button, stop_button
    add_button = add_button or tkinter.Button(
        text='Add',
        command=create_new_item,
        width=10
    )
    start_button = start_button or tkinter.Button(
        text='Start',
        command=start_button_handler,
        width=10
    )
    stop_button = stop_button or tkinter.Button(
        text='Stop',
        command=stop_button_handler,
        width=10
    )
    add_button.place(x=40, y=cur_y)
    start_button.place(x=500, y=cur_y)
    stop_button.place(x=600, y=cur_y)


def create_new_item():
    global items
    items.append(Item())
    replace_items()


def main():
    global root
    root = tkinter.Tk()
    root.geometry('700x300')
    tkinter.Label(text='Path:', font=BOLD).place(x=40, y=20)
    tkinter.Label(text='min:', font=BOLD).place(x=300, y=20)
    tkinter.Label(text='X:', font=BOLD).place(x=400, y=20)
    tkinter.Label(text='Y:', font=BOLD).place(x=500, y=20)
    create_new_item()
    root.mainloop()


if __name__ == "__main__":
    main()
