import tkinter as tk
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class GUI():
    ancestry_brackets = []

    def __init__(self):
        super().__init__()   
        self.ancestry_bracket = tk.PhotoImage(file=resource_path('imgs/ancestry_bracket.png'))
        GUI.ancestry_brackets.append(self.ancestry_bracket)

    def image_subsample(image_list, x, y):
        GUI.ancestry_brackets.append(image_list[-1].subsample(x,y))

                