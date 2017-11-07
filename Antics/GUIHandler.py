import tkinter
import os
from Game import *
from GameState import *
from GamePane import *
from SettingsPane import *
from StatsPane import *
from Constants import *

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

    def __init__(self, game):
        self.game: Game = game

        # bookKeeping
        self.currentFrame = 0
        self.currentState: GameState = None
        self.setup = False
        self.waitingForHuman = False
        self.waitingForAttack = False
        self.attackingAntLoc = None
        self.phase = None

        # set up tkinter things
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("ReAntics")
        self.baseFrame = tkinter.Frame(self.root)
        self.settingsFrame = tkinter.Frame(self.baseFrame)
        self.statsFrame = tkinter.Frame(self.baseFrame)
        self.gameFrame = tkinter.Frame(self.baseFrame)

        # shared tkinter variables
        # note these have to be here after root is made
        self.pauseVar = tkinter.StringVar()
        self.pauseVar.set("Play")
        self.statsText = tkinter.StringVar()
        self.statsText.set("Print Stats On")
        self.blue = "#8bbcda"
        self.stats = False
        self.paused = False

        self.settingsFrame.pack_propagate(False)
        self.statsFrame.pack_propagate(False)
        self.gameFrame.pack_propagate(False)

        self.settingsHandler = GameSettingsFrame(self, self.settingsFrame)
        self.statsHandler = StatsPane(self, self.statsFrame)
        self.gameHandler = GamePane(self, self.gameFrame)
        

        # we want the game to start on the settings screen, so show it first
        self.settingsFrame.pack(fill="both")

        # pack main GUI
        self.baseFrame.pack(fill="both")

        self.count = 0
        self.closed = False
        #self.pausePressed()
        self.setup = True

    ##
    # is called when the program is closed
    # to clean up
    #
    def onClose(self):
        # TODO: This is brute forced, should probably find a different way
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

    ##
    # setPlayers
    #
    # sets the name of the current players
    #
    def setPlayers(self, p1, p2):
        self.gameHandler.p1Name.set(p1[0:6] + '..' + p1[-3:] if len(p1) > 6 else p1[0:6])
        self.gameHandler.p2Name.set(p2[0:6] + '..' + p2[-3:] if len(p2) > 6 else p2[0:6])

    ##
    # getHumanMove
    #
    # sets up GUI to receive a game move from a human player
    #
    def getHumanMove(self, phase):
        if phase not in [SETUP_PHASE_1, SETUP_PHASE_2, PLAY_PHASE]:
            print("Game in wrong phase for human move")
            return

        print("Asked for human move: %d" % phase)

        if phase == SETUP_PHASE_1:
            self.gameHandler.setInstructionText("Select where to build your anthill.")
        elif phase == SETUP_PHASE_2:
            self.gameHandler.setInstructionText("Select where to place your enemy's food.")
        else:
            self.gameHandler.setInstructionText("Submit a move.")

        self.waitingForHuman = True
        self.phase = phase

    ##
    # getHumanAttack
    #
    # sets up the GUI to receive an attack from a human player
    # the location passed from the game is already swapped back to P1 at top
    #
    def getHumanAttack(self, location):
        print("Asked for human attack")
        self.gameHandler.setInstructionText("Select an ant to attack.")
        self.waitingForHuman = True
        self.waitingForAttack = True
        self.attackingAntLoc = location
        self.gameHandler.highlightValidAttacks(getAntAt(self.currentState, location))

    ##
    # submitHumanSetup
    #
    #
    #
    def submitHumanSetup(self, locations):
        self.gameHandler.setInstructionText("")
        self.game.submitHumanSetup(locations)
        self.waitingForHuman = False

    ##
    # submitHumanMove
    #
    # sends a given move to the game however it needs to go
    #
    def submitHumanMove(self, move):
        self.gameHandler.setInstructionText("")
        self.game.submitHumanMove(move)
        self.waitingForHuman = False

    ##
    # submitHumanAttack
    #
    #
    def submitHumanAttack(self, attack):
        self.gameHandler.setInstructionText("")
        self.game.submitHumanAttack(attack)
        self.waitingForAttack = False
        self.waitingForHuman = False
        self.attackingAntLoc = None

    ##################################################
    # Button Call Methods
    #
    # here because they need to be synced between stats
    # and game pane
    #
    def pausePressed(self):
        if self.paused:
            self.paused = False
            self.pauseVar.set("Pause")
            self.gameHandler.pauseButton.config(bg = self.blue)
            self.statsHandler.pauseButton.config(bg = self.blue)
            self.game.generalWake()
        else:
            self.paused = True
            self.pauseVar.set("Play")
            self.gameHandler.pauseButton.config(bg = 'green')
            self.statsHandler.pauseButton.config(bg = 'green')

    def stepPressed(self):
        self.game.generalWake()

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
        print("settings")
