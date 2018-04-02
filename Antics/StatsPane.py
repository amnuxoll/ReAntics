import tkinter
import RedoneWidgets as wgt
from Constants import *
import random
import os
import time
from sys import platform

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

# height and width for the totals score card
HEIGHT = 27#20
WIDTH = 35

class StatsPane:

    def __init__(self, handler, parent):
        self.parent = parent
        self.handler = handler

        ## make GameLog display frame
        self.log = []
        self.cur_log = None
        
        self.gLFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.gLFrame.grid(column=0, row=0, columnspan=3, sticky=tkinter.E + tkinter.W + tkinter.S + tkinter.N, padx =5)
        self.gameLog = tkinter.StringVar()
        self.gameLog.set("Game Log")
        self.gameLogLabel = tkinter.Label(self.gLFrame, textvar=self.gameLog, fg = FL_TEXT_COLOR, \
                                          bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT)
        self.gameLogLabel.grid(column=0, row=0)
        self.gameLogLabel.pack(side = tkinter.TOP, fill=tkinter.X)
        self.gLFrame.columnconfigure(0, weight=1)

        self.logTextFrame = wgt.ScrollableFrame ( self.gLFrame )
        self.logTextFrame.canvas.config(height=450)

        self.gLFrame.columnconfigure(0, weight=1)
        self.logTextFrame.pack ( fill="both" )

        ## make totals display frame
        t_width = 475 if platform != "win32" else 600
        t_height = 450
        self.tFrame_outer = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.tFrame_outer.config(bg="white")
        self.tFrame = wgt.ScrollableFrame(self.tFrame_outer)
        self.tFrame.canvas.config(bg="white",width=t_width,height=t_height)
        self.tFrame.set_scrollregion(vertical_buff=1000)
        #self.tFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.tFrame_outer.grid(column=3, row=0, columnspan=3, sticky=tkinter.E + tkinter.W + tkinter.S + tkinter.N)

        self.totals = tkinter.StringVar()
        self.totals.set("Totals")
        self.totalsLabel = tkinter.Label(self.tFrame_outer, textvar=self.totals, fg = FL_TEXT_COLOR, \
                                         bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT, width=WIDTH)
        self.totalsLabel.pack(side=tkinter.TOP, fill=tkinter.X)
        self.tFrame.columnconfigure(3, weight=1)

        self.totalsStrVar =  tkinter.StringVar()
        self.totalsTextLabel = tkinter.Label(self.tFrame.interior, textvar=self.totalsStrVar, fg="black", \
                                             bg="white",  font=("Courier", 15),\
                                             height=HEIGHT,anchor=tkinter.W)
        self.totalsTextLabel.pack(side=tkinter.TOP, fill=tkinter.X)
        self.tFrame.columnconfigure(0, weight=1)

        self.totalsLabel.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self.tFrame.pack()

        # update the totals areanow that the widgets are set
        #self.setScoreRecord ( "Totals stuff here" )
        v_buf = (int(len(self.handler.game.players)/24)+1 if len(self.handler.game.players)%24>0 else 0)
        self.totalsTextLabel.config(height=HEIGHT*v_buf,anchor=tkinter.N)
        self.tFrame.set_scrollregion(vertical_buff=HEIGHT*v_buf)#1000* 
     
        ## make time display frame
        self.timeHeaderFrame = tkinter.Frame(self.parent, highlightthickness = F_BORDER, highlightbackground="black")
        self.timeHeaderFrame.grid(columnspan=6, column=0, row=1, sticky=tkinter.W+tkinter.E+tkinter.N, \
                                  padx = 5, pady = 5)
        self.timeInfo = tkinter.StringVar()
        self.timeInfo.set("Time")
        self.timeInfoLabel = tkinter.Label(self.timeHeaderFrame, textvar = self.timeInfo, fg = FL_TEXT_COLOR,\
                                           bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT)
        self.timeInfoLabel.grid(column=2, row=2)
        self.timeInfoLabel.pack(side=tkinter.TOP, fill = tkinter.X)
        self.timeHeaderFrame.columnconfigure(0, weight=1)

        self.timeLabel = wgt.StopWatch (self.timeHeaderFrame) 
        self.timeLabel.label.config(font=("Courier", 50, "bold"))
        self.timeLabel.pack(side=tkinter.TOP, fill=tkinter.X, padx=2)
        self.timeHeaderFrame.columnconfigure(0, weight =1)

        ## Make control buttons
        self.buttonFrame = tkinter.Frame(self.parent)
        self.buttonFrame.grid(column = 6, row = 0, rowspan = 2, sticky = tkinter.N + tkinter.S)

        self.buttonText = tkinter.StringVar()

        font = ("Times New Roman", 24)

        self.UIbutton = wgt.ColoredButton(self.buttonFrame, text="Show Board", command=self.UIbuttonPressed)
        self.UIbutton.config(bg=self.handler.blue, fg='white', font=font, width=12, pady=3)
        self.UIbutton.grid()

        self.pauseButton = wgt.ColoredButton(self.buttonFrame, command=self.handler.pausePressed)
        self.pauseButton.config(textvar=self.handler.pauseVar)
        self.pauseButton.config(bg=self.handler.blue, fg='white', font=font, width=12, pady=3)
        self.pauseButton.grid(row=1)
        self.paused = True

        self.stepButton = wgt.ColoredButton(self.buttonFrame, text="Step", command=self.handler.stepPressed)
        self.stepButton.config(bg=self.handler.blue, fg='white', font=font, width=12, pady=3)
        self.stepButton.grid(row=2)

        self.statsButton = wgt.ColoredButton(self.buttonFrame, command=self.handler.statsPressed)
        self.statsButton.config(textvar=self.handler.statsText)
        self.statsButton.config(bg=self.handler.blue, fg='white', font=font, width=12, pady=3)
        self.statsButton.grid(row=3)
        self.stats = False

        self.killButton = wgt.ColoredButton(self.buttonFrame, text="Kill Game", command=self.handler.killPressed, backgroundcolor = 'red')
        self.killButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.killButton.grid(row=4)

        self.restartButton = wgt.ColoredButton(self.buttonFrame, text="Restart All", command=self.handler.restartPressed, backgroundcolor = 'red')
        self.restartButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.restartButton.grid(row=5)

        self.settingsButton = wgt.ColoredButton(self.buttonFrame, text="Settings", command=self.handler.settingsPressed, backgroundcolor = 'red')
        self.settingsButton.config(bg='red', fg='white', font=font, width=12, pady=3)
        self.settingsButton.grid(row=6)

        # make buttons space out a bit
        for i in range(7):
            self.buttonFrame.rowconfigure(i, weight=1)

        self.dummyStatLabel = None


    def UIbuttonPressed(self):
        self.handler.showFrame(2)

    def setScoreRecord ( self, s ) :
        #self.tFrame.canvas.config(height=2000)
        self.totalsStrVar.set ( s )

    def addGameToLog ( self ) :
        return

    def addLogItem ( self ) :
        b = PurpleBox(self.logTextFrame.interior)
        b.grid()
        if self.dummyStatLabel is not None:
            self.dummyStatLabel.destroy()
        self.dummyStatLabel = tkinter.Label(self.logTextFrame.interior, bg = "white", text = "\n\n")
        self.dummyStatLabel.grid(sticky=tkinter.W)
        
        self.logTextFrame.set_scrollregion(vertical_buff=300) #can change amount of white space beneath game log records
        self.parent.update_idletasks()

        self.log.append(b)
        self.cur_log = b

        b.myClock.Reset()
        b.myClock.Start()

    def stopCurLogItem(self, game_over = False):
        if self.cur_log is None:
            return
        self.cur_log.myClock.Stop()
        if game_over:
            self.setCurLogItemOver()
            
    def startCurLogItem(self):
        if self.cur_log is None:
            return
        self.cur_log.myClock.Start()

    def setCurLogItemOver(self):
        if self.cur_log is None:
            return
        self.cur_log.myClock.PermanentlyStop()

    def updateCurLogItem(self, s):
        if self.cur_log is None:
            return
        self.cur_log.setTextLines(s)

    def clearLog(self):
        for b in self.log:
            b.destroy()

        self.log = []
        self.cur_log = None



#####
# PurpleBox
#
# used for the game log
#####
class PurpleBox ( tkinter.Frame ) :
    def __init__ ( self, parent = None) :
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        
        self.maxl = 45#38 #for 11

        bc = wgt.LIGHT_PURPLE
        fnt = ( "Courier", 10 )

        self.config ( bg = bc, padx = 2, pady = 2, width = 500 )
        self.config ( highlightbackground="white", highlightcolor="white", highlightthickness=2, bd= 0 )

        self.textLines = []
        self.myText = tkinter.StringVar()
        self.setTextLines ( "" )
        
        self.myTextFrame = tkinter.Frame ( self, bg = bc, padx = 2, pady = 2 )
        self.myTextLabel = tkinter.Label ( self.myTextFrame, textvar = self.myText, anchor=tkinter.W, justify=tkinter.LEFT, bg = bc, font = fnt )
        self.myTextLabel.pack()
        self.myTextFrame.grid ( row = 0, column = 0, columnspan = 8 )

        self.myClock = self.timeLabel = wgt.StopWatch (self)
        self.myClock.grid ( row = 1, column = 0, columnspan = 8 )

    #####
    # setTextLines
    #####
    def setTextLines ( self, textArray ) :
        self.myText.set ( " "*self.maxl + "\n" + textArray )
        return
        
        padded = []
        for l in textArray :
            for i in range ( 0, len(l), self.maxl ) :
                cur = l [i: i+self.maxl ]
                cur = cur + " " * ( self.maxl - len (cur) )
                padded.append ( cur )

        self.myText.set ( "\n".join ( padded ) )




