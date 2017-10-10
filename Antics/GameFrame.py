import tkinter

#
# class GamePane
#
# This class contains all the UI code to render the game
# board and interfaces for human control.
#
#

class GamePane(tkinter.Frame):

    def __init__(self, parent):
        tkinter.Frame.__init__(parent)
        self.parent = parent

        # make game board
        self.boardFrame = tkinter.Frame(self)
        self.boardIcons = []

        terrain = tkinter.PhotoImage("Textures\Terrain.gif")
        for i in range(10):
            tmp = []
            for j in range(10):
                label = tkinter.Label()

        self.pack()