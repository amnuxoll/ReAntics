import tkinter
import os
from sys import platform
from Game import *
from GameState import *
from GamePane import *
from SettingsPane import *
from StatsPane import *
from Constants import *
import RedoneWidgets
import base64
import pickle
import datetime
import re


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
#
# This could be accomplished by replacing all referenced to
# UI in the main thread with if self.ui is not None: {do thing}.
#########################################################
class GUIHandler:

    def __init__(self, game):
        self.game = game

        # bookKeeping
        self.currentFrame = 0
        self.currentState = None
        self.setup = False
        self.waitingForHuman = False
        self.waitingForAttack = False
        self.attackingAntLoc = None
        self.phase = None

        # set up tkinter things
        self.root = tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.title("ReAntics")
        icon = tkinter.PhotoImage(file="Textures/queenRed.gif")
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon)

        self.baseFrame = tkinter.Frame(self.root)
        self.settingsFrame = tkinter.Frame(self.baseFrame)
        self.statsFrame = tkinter.Frame(self.baseFrame)
        self.gameFrame = tkinter.Frame(self.baseFrame)

        # shared tkinter variables
        # note these have to be here after root is made
        self.pauseVar = tkinter.StringVar()
        self.pauseVar.set("Pause")
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

        menubar = tkinter.Menu(self.root)

        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Reload Agents", command=self.reloadAgentPressed)
        menubar.add_cascade(label="File", menu=filemenu)

        ###
        # help menu - hot keys, ant stats
        s_font = 'Courier' if platform in ["linux", "linux2"] else 'Monaco'
        self.saved_textures = [] # saved from windows/linux garbage collection/memory re-allocation
        helpmenu = tkinter.Menu(menubar,tearoff=0)
        fm_dummy = tkinter.Menu(helpmenu,tearoff=0,font=(s_font, 12))
        for x in self.game.hotKeyInfo.split("\n") :
            fm_dummy.add_command(label=x)
        helpmenu.add_cascade(label="Hot Key Info", menu=fm_dummy)
        menubar.add_cascade(label="Help", menu=helpmenu)
        
        fm_dummy = tkinter.Menu(helpmenu,tearoff=0,font=(s_font, 10))
        for x in self.game.antUnitStatsInfo.split("\n"):
            xl = x.lower()
            rgx_ants = { "queen" : r"queen",
                         "worker": r"worker",
                         "rsoldier": r"r.*soldier",
                         "soldier": r"soldier",
                         "drone": r"drone" }
            ant = None
            for k in sorted(list(rgx_ants.keys())):
                if re.match(rgx_ants[k], xl):
                    ant = k+"Blue"
                    break
            if ant is None:
                fm_dummy.add_command(label=x)
                continue
            ant_img = tkinter.Menu(fm_dummy,tearoff=0)
            self.saved_textures.append(tkinter.PhotoImage(file="Textures/"+ant+".gif"))
            ant_img.add_command(image=self.saved_textures[-1])
            fm_dummy.add_cascade(label=x, menu=ant_img)
        # king
        # if format of UNIT_STATS is changed this will also have to change to keep correct spacing.
        # If needed, look at "lens" in infoScraper.GetAntStats(), this is a modified copy of what that produces
        x = "{:<11}{:<11}{:<9}{:<9}{:<8}{:<7}{:<16}".format("King", 11, 11, 11, 11, 11, "True")
        ant_img = tkinter.Menu(fm_dummy,tearoff=0)
        self.saved_textures.append(tkinter.PhotoImage(file="Textures/king.gif"))
        ant_img.add_command(image=self.saved_textures[-1])
        fm_dummy.add_cascade(label=x, menu=ant_img)
        # populate the help menu
        helpmenu.add_cascade(label="Ant Unit Stats", menu=fm_dummy)

        # helpmenu = tkinter.Menu(menubar, tearoff=0)
        # helpmenu.add_command(label="About", command=self.menuPressed)
        # menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

        # hot keys
        self.root.bind("<Return>", self.gameHandler.endTurnPressed)#end turn
        self.root.bind("<space>", self.stepPressed)#step
        self.root.bind("<p>", self.pausePressed)#pause
        self.root.bind("<u>", self.hotKeyUndo)#undo
        self.root.bind("<Shift-N>", self.secretPressed)
        self.root.bind("<r>", self.regGPressed)#regular graphics
        self.root.bind("<Shift-C>", self.secret2Pressed)
        self.root.bind("<s>", self.setSeasonalGraphics)

        # we want the game to start on the settings screen, so show it first
        self.settingsFrame.pack(fill="both")

        # pack main GUI
        self.baseFrame.pack(fill="both")

        self.count = 0
        #self.setSeasonalGraphics()
        self.setup = True

    # def menuPressed(self):
    #     print("Omg a menu button was pressed!")

    def reloadAgentPressed(self):
        if self.currentFrame == 0:
            self.game.loadAIs()
            self.game.UI.settingsHandler.changePlayers([ai[0].author for ai in self.game.players])
            self.game.UI.settingsHandler.addGameChanged("QuickStart")
            self.game.UI.settingsHandler.addGameType.set("QuickStart")

    def regGPressed(self, event = None):
        resets = ["queenRed", "queenBlue", "food", "grass", "carrying", "terrain"]
        for r in resets:
            self.gameHandler.textures[r] = tkinter.PhotoImage(file="Textures/"+r+".gif")
        self.gameHandler.textures["hat"] = None
        self.reDrawBoard()

    def loadSecret(self, secret):
        with open("Textures/FrameHelper.py", "rb") as f:
            info = pickle.load(f)[secret - 1]
            for key in info.keys():
                self.gameHandler.textures[key] = tkinter.PhotoImage(data=info[key])

        self.reDrawBoard()

    def secretPressed(self, event = None):
        self.loadSecret(1)

    def secret2Pressed(self, event = None):
        self.loadSecret(2)

    def setSeasonalGraphics(self, event = None):
        now = datetime.datetime.now()
        if now.month == 3:
            self.loadSecret(3)
        elif now.month == 10:
            self.loadSecret(4)
        elif now.month == 12:
            self.loadSecret(5)
        elif now.month == 2:
            self.loadSecret(6)


    def hotKeyUndo(self, event=None):
        self.gameHandler.undoPressed()

        

            
    ##
    # is called when the program is closed
    # to clean up
    #
    def onClose(self):
        self.game.endClient()
        self.root.after(100, self.continueClose)
        #self.continueClose()

    def continueClose(self):
        if self.game.gameThread.is_alive():
            self.root.after(50, self.continueClose)
            return
        self.game.gameThread.join()
        self.root.destroy()

    ##
    # reDrawBoard
    #
    # Calls the reDraw() method on all the tiles on the board
    #
    ##
    def reDrawBoard(self):
        for x in range(10):
            for y in range(10):
                self.gameHandler.boardIcons[x][y].reDraw()


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
                if self.waitingForHuman and self.phase in [SETUP_PHASE_1, SETUP_PHASE_2]:
                    self.gameHandler.showSetupConstructions(self.phase)

    ##
    # showState
    #
    # updates the current gameState of the GUI and updates the
    # GUI itself if appropriate to do so
    #
    def showState(self, state):
        self.currentState = state

        if self.currentFrame == 2 and self.currentState is not None:
            self.gameHandler.setToGameState(state)

    ##
    # setPlayers
    #
    # sets the name of the current players
    #
    def setPlayers(self, p1, p2):
        self.gameHandler.p1Name.set(p1)
        self.gameHandler.p2Name.set(p2)

        self.enableAllButtons()
        if p1 == "Human" or p2 == "Human":
            self.disableHumanButtons()
        else:
            self.gameHandler.undoButton.disable()

    def enableAllButtons(self):
        self.gameHandler.UIbutton.enable()
        self.gameHandler.stepButton.enable()

        self.gameHandler.killButton.enable()
        self.gameHandler.restartButton.enable()
        self.gameHandler.settingsButton.enable()

        self.statsHandler.killButton.enable()
        self.statsHandler.restartButton.enable()
        self.statsHandler.settingsButton.enable()

    def disableHumanButtons(self):
        self.gameHandler.UIbutton.disable()
        self.gameHandler.stepButton.disable()

    ##
    # getHumanMove
    #
    # sets up GUI to receive a game move from a human player
    #
    def getHumanMove(self, phase):
        if phase not in [SETUP_PHASE_1, SETUP_PHASE_2, PLAY_PHASE]:
            print("Game in wrong phase for human move")
            return

        # disable undo button at beginning of setup moves
        if phase == SETUP_PHASE_1:
            self.gameHandler.undoButton.disable()
            self.gameHandler.setInstructionText("Select where to build your anthill.")
        elif phase == SETUP_PHASE_2:
            self.gameHandler.undoButton.disable()
            self.gameHandler.setInstructionText("Select where to place your enemy's food. 2 remaining.")
        else:
            # enable undo if there are states to undo to
            if len(self.game.undoStates) > 0:
                self.gameHandler.undoButton.enable()
            else:
                self.gameHandler.undoButton.disable()
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
        # disable undo during attacks
        self.gameHandler.undoButton.disable()
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
        self.gameHandler.undoButton.disable()
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
    def pausePressed(self, event=None):
        if self.paused:
            self.paused = False
            self.pauseVar.set("Pause")
            self.gameHandler.pauseButton.config(bg = self.blue)
            self.statsHandler.pauseButton.config(bg = self.blue)
            self.statsHandler.startCurLogItem()
            self.statsHandler.timeLabel.Start()
            # should only wake if the game is "paused" on an AI turn
            if self.game.waitingOnAI:
                self.game.generalWake()
        else:
            self.paused = True
            self.pauseVar.set("Play")
            self.gameHandler.pauseButton.config(bg = 'green')
            self.statsHandler.pauseButton.config(bg = 'green')
            self.statsHandler.stopCurLogItem()
            self.statsHandler.timeLabel.Stop()

    def stepPressed(self, event=None):
        # should only wake if the game is "paused" on an AI turn
        if self.game.waitingOnAI:
            self.game.generalWake()

    def statsPressed(self):
        if self.stats:
            self.stats = False
            self.statsText.set("Print Stats On")
            self.game.verbose = True
        else:
            self.stats = True
            self.statsText.set("Print Stats Off")
            self.game.verbose = False

    def killPressed(self):
        # only kill if there's something to kill and game is not already killed
        if not self.game.running or self.game.killed:
            return

        # pause the game during the resolution of the kill button
        pause = False
        if not self.paused:
            self.pausePressed()
            pause = True

        res = RedoneWidgets.askQuestion("Kill Game", "Do you want to kill the game immediately?\n"
                                                     "Note that ending running games may damage AIs.", self.root)

        if res == "yes":
            self.gameHandler.setupsPlaced = None
            self.gameHandler.setupLocations = None
            self.gameHandler.killButton.disable()
            self.statsHandler.killButton.disable()

            self.game.kill()
            self.gameHandler.setInstructionText("Game Killed")
            if self.paused:
                self.pausePressed()

        # unpause the game if we paused it
        if self.paused and pause:
            self.pausePressed()

    def restartPressed(self):
        if self.game.restarted:
            return

        # pause the game during the resolution of the restart button
        pause = False
        if not self.paused and self.game.running:
            self.pausePressed()
            pause = True

        if self.game.running:
            self.game.restart()
            self.killPressed()
        else:
            self.game.restartFromEnd()

        self.gameHandler.restartButton.disable()
        self.statsHandler.restartButton.disable()

        # unpause the game if we paused it
        if pause and self.paused:
            self.pausePressed()

    def settingsPressed(self):
        self.game.gamesToPlay = []
        self.game.goToSettings = True
        self.killPressed()

        if not self.game.gameThread.is_alive():
            self.game.gameThread = threading.Thread(target=self.game.start, daemon=True)
            self.game.gameThread.start()
            self.showFrame(0)

        self.gameHandler.settingsButton.disable()
        self.statsHandler.settingsButton.disable()

        # needs to be reset so that it does not restart when cleared
        self.game.autorestart = False 

        # only wake the game thread if it's not running games ATM
        if not self.game.running:
            self.game.generalWake()
