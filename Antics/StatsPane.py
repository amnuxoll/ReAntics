import tkinter
import RedoneWidgets as wgt
from Constants import *
import random
import os

#
# class StatsPane
#
# This class contains all the UI code to render the game
# board and interfaces for human control.
#
#

F_BORDER = 5

FL_COLOR = "black"
FL_TEXT_COLOR = "white"
FL_BD = 5
FL_STYLE = "ridge"
FL_FONT = ( "Harrington", 16, "bold")

class StatsPane:

    def __init__(self, handler, parent):
        self.parent = parent
        self.handler = handler

        ## make GameLog display frame
        self.gLFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.gLFrame.grid(column=0, row=0, sticky=tkinter.E + tkinter.W + tkinter.S + tkinter.N, padx =5)
        self.gameLog = tkinter.StringVar()
        self.gameLog.set("Game Log")
        self.gameLogLabel = tkinter.Label(self.gLFrame, textvar=self.gameLog, fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT)
        self.gameLogLabel.grid(column=0, row=0)
        self.gameLogLabel.pack(side = tkinter.TOP, fill=tkinter.X)
        self.gLFrame.columnconfigure(0, weight=1)

        self.logTextLabel = tkinter.Label(self.gLFrame, text="Game Log stuff here", fg ="black", bg="white", borderwidth=FL_BD, font= ("Herculanum", 12))
        self.logTextLabel.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx = 2)
        self.gLFrame.columnconfigure(0, weight=1)


        ## make totals display frame
        self.tFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.tFrame.grid(column=1, row=0, sticky=tkinter.E + tkinter.W + tkinter.S + tkinter.N, padx = 5)
        self.totals = tkinter.StringVar()
        self.totals.set("Totals")
        self.totalsLabel = tkinter.Label(self.tFrame, textvar=self.totals, fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT)
        self.totalsLabel.grid(column=3, row=0)
        self.totalsLabel.pack(side=tkinter.TOP, fill=tkinter.X)
        self.tFrame.columnconfigure(3, weight=1)

        self.totalsTextLabel = tkinter.Label(self.tFrame, text="Totals stuff here", fg="black", bg="white", borderwidth=FL_BD, font=("Herculanum", 12))
        self.totalsTextLabel.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=2)
        self.tFrame.columnconfigure(0, weight=1)

        ## make time display frame
        self.timeHeaderFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.timeHeaderFrame.grid(columnspan=2, column=0, row=1, sticky=tkinter.W+tkinter.E+tkinter.N, padx = 5, pady = 5)
        self.timeInfo = tkinter.StringVar()
        self.timeInfo.set("Time")
        self.timeInfoLabel = tkinter.Label(self.timeHeaderFrame, textvar = self.timeInfo, fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT)
        self.timeInfoLabel.grid(column=2, row=2)
        self.timeInfoLabel.pack(side=tkinter.TOP, fill = tkinter.X)
        self.timeHeaderFrame.columnconfigure(0, weight=1)

        self.timeLabel = tkinter.Label(self.timeHeaderFrame, text=0, fg="black", bg="white", borderwidth=FL_BD, font=("Herculanum", 12))
        self.timeLabel.pack(side=tkinter.TOP, fill=tkinter.X, padx=2)
        self.timeHeaderFrame.columnconfigure(0, weight =1)



        ## Make control buttons
        self.buttonFrame = tkinter.Frame(self.parent)
        self.buttonFrame.grid(column = 3, row = 0, rowspan = 2, sticky = tkinter.N + tkinter.S)

        self.buttonText = tkinter.StringVar()


        self.blue = "#8bbcda"
        font = ("Times New Roman", 24)

        self.UIbutton = wgt.ColoredButton(self.buttonFrame, text="Show UI", command=self.UIbuttonPressed)
        self.UIbutton.config(bg=self.blue, fg='white', font=font, width=12, pady=3)
        self.UIbutton.grid()

        self.endTurnButton = wgt.ColoredButton(self.buttonFrame, text="End Turn", command=self.endTurnPressed)
        self.endTurnButton.config(bg=self.blue, fg='white', font=font, width=12, pady=3)
        self.endTurnButton.grid(row=1)

        self.pauseVar = tkinter.StringVar()
        self.pauseVar.set("Play")
        self.pauseButton = wgt.ColoredButton(self.buttonFrame, command=self.pausePressed)
        self.pauseButton.config(textvar=self.pauseVar)
        self.pauseButton.config(bg='green', fg='white', font=font, width=12, pady=3)
        self.pauseButton.grid(row=2)
        self.paused = True

        self.stepButton = wgt.ColoredButton(self.buttonFrame, text="Step", command=self.stepPressed)
        self.stepButton.config(bg=self.blue, fg='white', font=font, width=12, pady=3)
        self.stepButton.grid(row=3)

        self.statsText = tkinter.StringVar()
        self.statsText.set("Print Stats On")
        self.statsButton = wgt.ColoredButton(self.buttonFrame, command=self.statsPressed)
        self.statsButton.config(textvar=self.statsText)
        self.statsButton.config(bg=self.blue, fg='white', font=font, width=12, pady=3)
        self.statsButton.grid(row=4)
        self.stats = False

        self.killButton = wgt.ColoredButton(self.buttonFrame, text="Kill Game", command=self.killPressed)
        self.killButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.killButton.grid(row=5)

        self.restartButton = wgt.ColoredButton(self.buttonFrame, text="Restart All", command=self.restartPressed)
        self.restartButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.restartButton.grid(row=6)

        self.settingsButton = wgt.ColoredButton(self.buttonFrame, text="Settings", command=self.settingsPressed)
        self.settingsButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.settingsButton.grid(row=7)

        # make buttons space out a bit
        for i in range(8):
            self.buttonFrame.rowconfigure(i, weight=1)


    def UIbuttonPressed(self):
        self.handler.showFrame(2)

    def endTurnPressed(self):
        print("End Turn")

    def pausePressed(self):
        if self.paused:
            self.paused = False
            self.pauseVar.set("Pause")
            self.pauseButton.config(bg = self.blue)
        else:
            self.paused = True
            self.pauseVar.set("Play")
            self.pauseButton.config(bg = 'green')

    def stepPressed(self):
        print("Step")

    def statsPressed(self):
        if self.stats:
            self.stats = False
            self.statsText.set("Print Stats On")
        else:
            self.stats = True
            self.statsText.set("Print Stats Off")

    def killPressed(self):
        print("Kill")

    def restartPressed(self):
        self.killPressed()
        print("Restart")

    def settingsPressed(self):
        self.killPressed()
        self.handler.showFrame(0)

    def boardButtonPressed(self, x, y):
        print("Board Clicked x: %d, y: %d" % (x, y))

