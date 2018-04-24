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
LIGHT_PURPLE = "#c9b6e3"



#############################################################################
FLASH_COLOR = "#425261"
FLASH_TIME = 0.05

#### button creation ####
# wgt.ColoredButton ( <frame>, <text>, <background color>, <text color>, <command>  )
# self.command = <set the command and keep the flash>


class ColoredButton(tk.Label):
    def __init__(self, parent = None, text = "", backgroundcolor = "green",
                 textcolor = "black", command = None, flash = False):
        # initialize UI object
        tk.Label.__init__(self, parent)
        # store event handler to close later
        self.parent = parent
        self.disabled = False
        self.bg = backgroundcolor

        self.command = command
        self.flash = flash # no longer needed, before needed for mac compatibility issues

        self.config(text = text, bg = backgroundcolor, fg = textcolor,
                    activebackground = FLASH_COLOR, borderwidth=5, relief="raised")
        self.bind("<Button-1>", self.pressed)

    def pressed(self, thing):
        if self.disabled:
            return
        self.flashButton()
            
        if self.command:
            self.command()

    def flashButton(self):
        self.config(state = "active")
        self.update_idletasks()
        time.sleep(FLASH_TIME)
        self.config(state = "normal")

    def disable(self):
        self.config(bg = "gray")
        self.disabled = True

    def enable(self):
        self.config(bg = self.bg)
        self.disabled = False


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

    def set_scrollregion(self, event=None, vertical_buff = 0):
        x = self.canvas.bbox('all')
        new_bbox = (x[0], x[1], x[2], x[3]+vertical_buff)
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=new_bbox)

# https://stackoverflow.com/questions/46287270/trying-to-grab-current-time-from-a-stopwatch-widget-when-i-hit-a-button-tkinte
class StopWatch(tk.Frame):
    """ Implements a stop watch frame widget. """
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self._start = 0.0
        self._elapsedtime = 0
        self._running = 0
        self.timestr = tk.StringVar()
        self.label = None
        self.makeWidgets()
        self._timer = None
        self.game_over = False

    def makeWidgets(self):
        """ Make the time label. """
        self.label  = tk.Label(self, textvariable=self.timestr)
        self._setTime(self._elapsedtime, self.timestr)
        self.label.pack(fill=tk.X, expand=tk.NO, pady=2, padx=2)


    def _update(self, string_obj, rate):
        """ Update the label with elapsed time. """
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime * rate, string_obj)
        if self._running:
           self._timer = self.after(50, self._update, string_obj, rate)

    def _setTime(self, elap, string_obj):
        """ Set the time string to Minutes:Seconds:Hundreths """
        hours = int(elap/3600)                                           #without the hours below
        minutes = int(elap/60 - hours*60)                                #int(elap/60)
        seconds = int(elap - hours*3600 - minutes*60.0)                  #int(elap - minutes*60.0)
        hseconds = int((elap - hours*3600 - minutes*60.0 - seconds)*100) #int((elap - minutes*60.0 - seconds)*100)
        string_obj.set('%02d:%02d:%02d.%02d' % (hours, minutes, seconds, hseconds))

    def Start(self):
        """ Start the stopwatch, ignore if running, or the game/event is over. """
        if self._running or self.game_over:
            return
            #''' make self.start the time now - zero'''
        self._start = time.time() - self._elapsedtime
            
        self._running = 1
        self._update(self.timestr, 1.0)

    def Stop(self):
        #print("in stop")
        """ Stop the stopwatch, ignore if stopped or the game/event is over. """
        if not self._running:
            return
        self.after_cancel(self._timer)
        self._timer = None
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime,self.timestr)
        self._running = 0

    def Reset(self):
        """ Reset the stopwatch. """
        self._start = time.time()
        self._elapsedtime = 0.0
        self._setTime(self._elapsedtime,self.timestr)
        self.game_over = False

    def PermanentlyStop(self) :
        self.game_over = True

###########################################################################
# standard message dialogs... showinfo, showwarning, showerror
# http://tk-happy.sourceforge.net/tk_dialogs.html
#
# added param "root" - this is handler.root

def ShowInfo(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update_idletasks()
        messagebox.showinfo( title, message )
    
    return
def ShowWarning(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update_idletasks()
        messagebox.showwarning( title, message )
    return
def ShowError(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update_idletasks()
        messagebox.showerror( title, message )
    return

def askOKCancel(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update_idletasks()
        return messagebox.askokcancel( title, message )

def askQuestion(title='Title', message='your message here.', root = None):
    if root is not None:
        root.update_idletasks()
        return messagebox.askquestion( title, message )

