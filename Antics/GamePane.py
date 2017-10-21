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


        ## make game board
        self.boardFrame = tkinter.Frame(self.parent)
        self.boardIcons = []

        # game board is based on a 10*10 grid of tiles
        self.terrain = tkinter.PhotoImage(file = "Textures/terrain.gif")
        for i in range(10):
            tmp = []
            for j in range(10):
                # currently displaying as a label, likely needs to be changed
                # borderwidth has to be 0 to make seamless grid
                label = tkinter.Label(self.boardFrame, image = self.terrain, bd = 0)
                tmp.append(label)
                label.grid(column = j, row = i)
            self.boardIcons.append(tmp)
        self.boardFrame.grid(column = 1, row = 0)


        ## make player displays
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

        ## Make message pane
        self.messageFrame = tkinter.Frame(self.parent,bg = "white", relief = tkinter.RIDGE, bd = 2)
        self.messageText = tkinter.StringVar()
        self.messageText.set("Please Win")
        self.messageLabel = tkinter.Label(self.messageFrame, textvar = self.messageText, bg = "white")
        self.messageLabel.grid()
        self.messageFrame.grid(column = 1, row = 1, sticky = tkinter.E + tkinter.W)
        self.messageFrame.columnconfigure(0, weight = 1)

        ## Make control buttons
        self.buttonFrame = tkinter.Frame(self.parent)




