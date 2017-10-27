import tkinter as tk
from tkinter.font import Font
from functools import partial
from tkinter import ttk
import time


FLASH_COLOR = "blue"
FLASH_TIME = 0.05

#### button creation ####
# wgt.ColoredButton ( <frame>, <text>, <background color>, <text color>, <command>  )
# self.command = <set the command and keep the flash>


class ColoredButton(tk.Label):
    def __init__(self, parent = None, text = "", backgroundcolor = "green", textcolor = "black", command = None):
        # initialize UI object
        tk.Label.__init__(self, parent)
        # store event handler to close later
        self.parent = parent

        self.command = command

        self.config(text = text, bg = backgroundcolor, fg = textcolor, activebackground = FLASH_COLOR, borderwidth=5, relief="raised")
        self.bind("<Button-1>", self.pressed)

    def pressed(self, thing):
        self.config(state = "active")
        self.update()
        time.sleep(FLASH_TIME)
        self.config(state = "normal")

        if self.command:
            self.command()
