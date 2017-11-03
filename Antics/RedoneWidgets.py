import tkinter as tk
from tkinter.font import Font
from functools import partial
from tkinter import ttk
from tkinter import messagebox
import time

####
# COLORS - dimmed to be lighter on the eyes
GREEN = "#398e2e"
LIGHT_GREEN = "#80c577"
RED = "#c3473c"
LIGHT_RED = "#b8746e"
LIGHT_BLUE = "#a8d5ff"



#############################################################################
FLASH_COLOR = "#425261"
FLASH_TIME = 0.05

#### button creation ####
# wgt.ColoredButton ( <frame>, <text>, <background color>, <text color>, <command>  )
# self.command = <set the command and keep the flash>


class ColoredButton(tk.Label):
    def __init__(self, parent = None, text = "", backgroundcolor = "green", textcolor = "black", command = None, flash = False):
        # initialize UI object
        tk.Label.__init__(self, parent)
        # store event handler to close later
        self.parent = parent

        self.command = command
        self.flash = flash

        self.config(text = text, bg = backgroundcolor, fg = textcolor, activebackground = FLASH_COLOR, borderwidth=5, relief="raised")
        self.bind("<Button-1>", self.pressed)

    def pressed(self, thing):
        if self.flash :
            self.flashButton()
        if self.command:
            self.command()

    def flashButton (self):
        self.config(state = "active")
        self.update()
        time.sleep(FLASH_TIME)
        self.config(state = "normal")       


#####
# ScrollableFrame
#
# creates a nested frame and canvas to be used as a scroll area
# add widgets to the frame <ScrollableFrame>.interior
#
# source: https://stackoverflow.com/questions/23483629/dynamically-adding-checkboxes-into-scrollable-frame
#####
class ScrollableFrame ( tk.Frame ) :
    def __init__ ( self, master, **kwargs ) :
        tk.Frame.__init__(self, master, **kwargs )

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar ( self, orient=tk.VERTICAL )
        self.vscrollbar.pack ( side='right', fill="y",  expand="false" )
        self.canvas = tk.Canvas ( self,
                                bg='white', bd=0,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set )
        self.canvas.pack ( side="left", fill="both", expand="true" )
        self.vscrollbar.config ( command=self.canvas.yview )

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame ( self.canvas, **kwargs, bg="white", padx = 2, pady = 2 )
        self.canvas.create_window ( 0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)

    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

###########################################################################
# standard message dialogs... showinfo, showwarning, showerror
# http://tk-happy.sourceforge.net/tk_dialogs.html
#
# added param "root" - this is handler.root

def ShowInfo(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update()
        messagebox.showinfo( title, message )
    
    return
def ShowWarning(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update()
        messagebox.showwarning( title, message )
    return
def ShowError(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update()
        messagebox.showerror( title, message )
    return
