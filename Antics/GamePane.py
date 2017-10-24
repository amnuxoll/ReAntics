import tkinter

#
# class GamePane
#
# This class contains all the UI code to render the game
# board and interfaces for human control.
#
#


class GamePane:

    def __init__(self, handler, parent):
        self.parent = parent
        self.handler = handler

        # make game board
        self.boardFrame = tkinter.Frame(self.parent)
        self.boardIcons = []

        # game board is based on a 10*10 grid of tiles
        self.terrain = tkinter.PhotoImage(file = "Textures/terrain.gif")
        for i in range(10):
            tmp = []
            for j in range(10):
                button = BoardButton(self.boardFrame, self, j, i, self.terrain)
                tmp.append(button)
            self.boardIcons.append(tmp)
        self.boardFrame.grid(column = 1, row = 0)

        # make player displays
        self.playerInfoFrame = tkinter.Frame(self.parent, relief = tkinter.GROOVE, borderwidth = 2)

        # make tkinter variables with default values (should be overwritten before display)
        self.p1Name = tkinter.StringVar()
        self.p1Name.set("Player 1")
        self.p1Food = tkinter.IntVar()
        self.p1Food.set(0)
        self.p2Name = tkinter.StringVar()
        self.p2Name.set("Player 2")
        self.p2Food = tkinter.IntVar()
        self.p2Food.set(0)

        # make labels Wraplength = 1 causes text to be displayed vertically
        textFont = ("Times New Roman", 16)
        self.p1Label = tkinter.Label(self.playerInfoFrame, textvar = self.p1Name, wraplength = 1, font = textFont)
        self.p1Label.grid(column = 0, row = 0)
        self.p1FoodLabel = tkinter.Label(self.playerInfoFrame, textvar = self.p1Food)
        self.p1FoodLabel.grid(column = 0, row = 1)
        self.p2FoodLabel = tkinter.Label(self.playerInfoFrame, textvar = self.p2Food)
        self.p2FoodLabel.grid(column = 0, row = 2)
        self.p2Label = tkinter.Label(self.playerInfoFrame, textvar = self.p2Name, wraplength = 1, font = textFont)
        self.p2Label.grid(column = 0, row = 3)

        # set weights so player labels are centered properly
        self.playerInfoFrame.rowconfigure(0, weight = 1)
        self.playerInfoFrame.rowconfigure(3, weight = 1)

        self.playerInfoFrame.grid(column = 0, row = 0, sticky = tkinter.N + tkinter.S)
        self.parent.rowconfigure(0, weight = 1)

        # Make message pane
        self.messageFrame = tkinter.Frame(self.parent, bg = "white", relief = tkinter.RIDGE, bd = 2)
        self.messageText = tkinter.StringVar()
        self.messageText.set("Please Win")
        self.messageLabel = tkinter.Label(self.messageFrame, textvar = self.messageText, bg = "white")
        self.messageLabel.grid()
        self.messageFrame.grid(column = 1, row = 1, sticky = tkinter.E + tkinter.W)
        self.messageFrame.columnconfigure(0, weight = 1)

        # Make control buttons
        # TODO: make them look fancy
        self.blue = "#8bbcda"
        font = ("Times New Roman", 24)
        
        self.buttonFrame = tkinter.Frame(self.parent)
        self.buttonFrame.grid(column = 2, row = 0, rowspan = 2, sticky = tkinter.N + tkinter.S)

        self.UIbutton = tkinter.Button(self.buttonFrame, text = "Close UI", command = self.UIbuttonPressed)
        self.UIbutton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.UIbutton.grid()

        self.endTurnButton = tkinter.Button(self.buttonFrame, text = "End Turn", command = self.endTurnPressed)
        self.endTurnButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.endTurnButton.grid(row = 1)

        self.pauseVar = tkinter.StringVar()
        self.pauseVar.set("Play")
        self.pauseButton = tkinter.Button(self.buttonFrame, textvar = self.pauseVar, command = self.pausePressed)
        self.pauseButton.config(bg = 'green', fg = 'white', font = font, width = 12, pady = 3)
        self.pauseButton.grid(row = 2)
        self.paused = True

        self.stepButton = tkinter.Button(self.buttonFrame, text = "Step", command = self.stepPressed)
        self.stepButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.stepButton.grid(row = 3)

        self.statsText = tkinter.StringVar()
        self.statsText.set("Print Stats On")
        self.statsButton = tkinter.Button(self.buttonFrame, textvar = self.statsText, command = self.statsPressed)
        self.statsButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.statsButton.grid(row = 4)
        self.stats = False

        self.killButton = tkinter.Button(self.buttonFrame, text = "Kill Game", command = self.killPressed)
        self.killButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.killButton.grid(row = 5)

        self.restartButton = tkinter.Button(self.buttonFrame, text = "Restart All", command = self.restartPressed)
        self.restartButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.restartButton.grid(row = 6)

        self.settingsButton = tkinter.Button(self.buttonFrame, text = "Settings", command = self.settingsPressed)
        self.settingsButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.settingsButton.grid(row =7)

        # make buttons space out a bit
        for i in range(8):
            self.buttonFrame.rowconfigure(i, weight = 1)

    #
    # button handling functions
    # some of these should be replaced by references to the GUI handler
    #
    def UIbuttonPressed(self):
        self.handler.showFrame(1)

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
        print("Restart")

    def settingsPressed(self):
        print("Settings")

    def boardButtonPressed(self, x, y):
        print("Board Clicked x: %d, y: %d" % (x, y))

class BoardButton:

    def __init__(self, parent, handler, x, y, image):
        self.x = x
        self.y = y
        self.handler = handler
        self.parent = parent

        # borderwidth has to be 0 to make seamless grid
        # TODO not seamless with buttons, fix
        self.button = tkinter.Button(self.parent, image = image, bd = 0, command = self.pressed)
        self.button.grid(column = self.x, row = self.y)

    def pressed(self):
        self.handler.boardButtonPressed(self.x, self.y)




