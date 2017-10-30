import tkinter
import os
import time
from GamePane import GamePane
from SettingsPane import GameSettingsFrame
from Game import Game
from GameState import GameState
from Location import Location
from Ant import Ant
from Building import Building
from Construction import Construction


#########################################################
# Class GUIHandler
#
# This class is to be instantiated by the game engine
# whenever the ReAntics GUI is needed. This class will
# handle all interactions with GUI threads and methods
# and needed callbacks to the game engine.
#
# The goal of this class is to keep the UI as separate as
# possible from the game engine so that the game can be
# easily configured to run without a GUI if desired.
#########################################################
class GUIHandler:

    def __init__(self, game: [Game, None]):
        self.game: Game = game

        # bookKeeping
        self.currentFrame = 0
        self.currentState: GameState = None
        self.setup = False

        # set up tkinter things
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("ReAntics")
        self.baseFrame = tkinter.Frame(self.root)
        self.settingsFrame = tkinter.Frame(self.baseFrame )
        self.statsFrame = tkinter.Frame(self.baseFrame)
        self.gameFrame = tkinter.Frame(self.baseFrame)

        # TODO implement and attach these handlers
        self.settingsHandler = GameSettingsFrame(self, self.settingsFrame)
        self.statsHandler = None
        self.gameHandler = GamePane(self, self.gameFrame)

        # we want the game to start on the settings screen, so show it first
        self.settingsFrame.pack(fill="both")

        # pack main GUI
        self.baseFrame.pack(fill="both")

        self.count = 0
        self.closed = False
        self.setup = True
        print("Setup")

    ##
    # is called when the program is closed
    # to clean up
    #
    def onClose(self):
        os._exit(0)



    ##
    # showFrame
    #
    # The GUI handler never destroys the windows in order to
    # be memory and CPU efficient. This method shows whichever
    # frame needs to be present and hides the others.
    #
    #   @param frameNum - integer representing which frame to show
    #       0: settings frame
    #       1: stats frame
    #       2: game frame
    ##
    def showFrame(self, frameNum):
        if frameNum not in [0, 1, 2]:
            return

        if frameNum == self.currentFrame:
            return

        self.currentFrame = frameNum

        self.settingsFrame.pack_forget()
        self.statsFrame.pack_forget()
        self.gameFrame.pack_forget()

        if frameNum == 0:
            self.settingsFrame.pack(fill="both")
        elif frameNum == 1:
            self.statsFrame.pack(fill="both")
        else:
            self.gameFrame.pack(fill="both")
            if self.currentState is not None:
                self.gameHandler.setToGameState(self.currentState)

    ##
    # showState
    #
    # updates the current gameState of the GUI and updates the
    # GUI itself if appropriate to do so
    #
    def showState(self, state: GameState):
        self.currentState = state

        if self.currentFrame == 2 and self.currentState is not None:
            self.gameHandler.setToGameState(state)

# test code to check GUI without running the game itself

if __name__ == "__main__":
    handler = GUIHandler(None)
    handler.root.mainloop()
