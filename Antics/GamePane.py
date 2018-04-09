import tkinter
import RedoneWidgets as wgt
from Constants import *
from GameState import *
from Building import  *
from Move import *
from Ant import *
from GUIHandler import *
from AIPlayerUtils import *
from functools import partial
import random
import os

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
        # bookkeeping
        self.movesHighlighted = False
        self.attacksHighlighted = False
        self.baseLocation = None
        self.setupsPlaced = None
        self.setupLocations = None
        self.hillCoords = None
        
        # create image assets
        self.textures = {}
        for f in os.listdir("Textures/"):
            s1, s2 = f.split('.')
            if s2 == "gif":
                self.textures[s1] = tkinter.PhotoImage(file = "Textures/" + f)
        # don't worry about this
        self.textures["hat"] = None


    def giveGame(self, the_game):
        self.the_game = the_game

    def createFrames(self):

        # make game board
        self.boardFrame = tkinter.Frame(self.parent)
        self.boardFrame.config(bd = 1, bg = 'black')
        self.boardIcons = []

        
        # game board is based on a 10*10 grid of tiles
        # access by self.boardIcons[y][x]
        # custom order to make things render nice
        for y in range(10):
            tmp = []
            for x in range(10):
                button = BoardButton(self.boardFrame, self, x, y)
                tmp.append(button)
            self.boardIcons.append(tmp)
        self.boardFrame.grid(column = 1, row = 0)

        # test board drawing
        # self.randomBoard()

        # make player displays
        self.playerInfoFrame = tkinter.Frame(self.parent, relief = tkinter.GROOVE, borderwidth = 2)
        # set up spacing for player names
        for i in (0, 4):
            self.playerInfoFrame.rowconfigure(i, weight = 1)
        for i in (1, 2, 3):
            self.playerInfoFrame.rowconfigure(i, weight = 0)

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
        font = ("Times New Roman", 16)
        self.p1Label = tkinter.Label(self.playerInfoFrame)
        self.p1Label.config(textvar = self.p1Name, wraplength = 1, font = font, fg = 'BLUE')
        self.p1Label.config(height = 11)
        self.p1Label.grid(column = 0, row = 0, sticky = tkinter.N + tkinter.S)
        self.foodLabel = tkinter.Label(self.playerInfoFrame)
        self.foodLabel.config(text = "Food", fg = "BLACK", font = font)
        self.foodLabel.grid(column = 0, row = 1)
        self.p1FoodLabel = tkinter.Label(self.playerInfoFrame)
        self.p1FoodLabel.config(textvar = self.p1Food, font = font, fg = 'BLUE', width = 2)
        self.p1FoodLabel.grid(column = 0, row = 2)
        self.p2FoodLabel = tkinter.Label(self.playerInfoFrame)
        self.p2FoodLabel.config(textvar = self.p2Food, font = font, fg = 'RED', width = 2)
        self.p2FoodLabel.grid(column = 0, row = 3)
        self.p2Label = tkinter.Label(self.playerInfoFrame)
        self.p2Label.config(textvar = self.p2Name, wraplength = 1, font = font, fg = 'RED')
        self.p2Label.config(height = 12)
        self.p2Label.grid(column = 0, row = 4, sticky = tkinter.N + tkinter.S)

        # set weights so player labels are centered properly
        self.playerInfoFrame.rowconfigure(0, weight = 1)
        self.playerInfoFrame.rowconfigure(3, weight = 1)

        self.playerInfoFrame.grid(column = 0, row = 0, sticky = tkinter.N + tkinter.S)
        self.parent.rowconfigure(0, weight = 1)

        # Make message pane
        font = ("Times New Roman", 16)
        self.messageFrame = tkinter.Frame(self.parent, bg = "white", relief = tkinter.RIDGE, bd = 2)
        self.messageText = tkinter.StringVar()
        self.messageText.set("Please Win")
        self.messageLabel = tkinter.Label(self.messageFrame, textvar = self.messageText, bg = "white", font = font)
        self.messageLabel.grid()
        self.messageFrame.grid(column = 1, row = 1, sticky = tkinter.E + tkinter.W)
        self.messageFrame.columnconfigure(0, weight = 1)

        # Make control buttons
        font = ("Times New Roman", 24)
        
        self.buttonFrame = tkinter.Frame(self.parent)
        self.buttonFrame.grid(column = 2, row = 0, rowspan = 2, sticky = tkinter.N + tkinter.S)

        self.UIbutton = wgt.ColoredButton(self.buttonFrame, text = "Hide Board", command = self.UIbuttonPressed, backgroundcolor = self.handler.blue)
        self.UIbutton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.UIbutton.grid()

        self.endTurnButton = wgt.ColoredButton(self.buttonFrame, text = "End Turn", command = self.endTurnPressed)
        self.endTurnButton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.endTurnButton.grid(row = 1)

        self.pauseButton = wgt.ColoredButton(self.buttonFrame, command = self.handler.pausePressed, backgroundcolor = self.handler.blue)
        self.pauseButton.config(textvar = self.handler.pauseVar)
        self.pauseButton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.pauseButton.grid(row = 2)
        self.paused = True

        self.stepButton = wgt.ColoredButton(self.buttonFrame, text = "Step", command = self.handler.stepPressed, backgroundcolor = self.handler.blue)
        self.stepButton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.stepButton.grid(row = 3)

        self.statsButton = wgt.ColoredButton(self.buttonFrame, command = self.handler.statsPressed)
        self.statsButton.config(textvar = self.handler.statsText)
        self.statsButton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.statsButton.grid(row = 4)
        self.stats = False

        self.killButton = wgt.ColoredButton(self.buttonFrame, text = "Kill Game", command = self.handler.killPressed, backgroundcolor = 'red')
        self.killButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.killButton.grid(row = 5)

        self.restartButton = wgt.ColoredButton(self.buttonFrame, text = "Restart All", command = self.handler.restartPressed, backgroundcolor = 'red')
        self.restartButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.restartButton.grid(row = 6)

        self.settingsButton = wgt.ColoredButton(self.buttonFrame, text = "Settings", command = self.handler.settingsPressed, backgroundcolor = 'red')
        self.settingsButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.settingsButton.grid(row =7)

        self.undoButton = wgt.ColoredButton(self.buttonFrame, text = "Undo", command = self.undoPressed, backgroundcolor = self.handler.blue)
        self.undoButton.config(bg = self.handler.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.undoButton.grid(row =8)

        # make buttons space out a bit
        for i in range(9):
            self.buttonFrame.rowconfigure(i, weight = 1)

    ##
    # randomBoard
    #
    # makes the board a completely random layout for testing purposes
    #
    # hey look its a unit test
    #
    def randomBoard(self):
        for y in range(10):
            for x in range(10):
                r = random.randint(1, 10)
                if r <= 4:
                    cons = -r
                else:
                    cons = -9

                r = random.randint(0, 19)
                if r <= 4:
                    ant = r
                else:
                    ant = -9

                r = random.randint(0, 1)
                if r == 0:
                    team = PLAYER_ONE
                else:
                    team = PLAYER_TWO

                r = random.randint(1, 10)
                if r == 1:
                    moved = True
                    highlight = False
                elif r == 2:
                    moved = False
                    highlight = True
                else:
                    moved = False
                    highlight = False

                r = random.randint(1,5)
                if r == 1:
                    carrying = True
                else:
                    carrying = False

                r = random.randint(1, 8)
                r2 = random.randint(1, r)
                health = (r, r2)

                r = random.randint(1, 8)
                r2 = random.randint(1, r)
                healthConst = (r, r2)

                self.boardIcons[y][x].setImage(construct = cons, ant = ant, antTeam = team, moved = moved,
                                               highlight = highlight, carrying = carrying, health = health, healthConst = healthConst)

    ##
    # setToGameState
    #
    # sets the board elements to reflect a given game state
    #
    def setToGameState(self, state: GameState):
        self.p1Food.set(state.inventories[PLAYER_ONE].foodCount)
        self.p2Food.set(state.inventories[PLAYER_TWO].foodCount)
        for col in range(BOARD_LENGTH):
            for row in range(BOARD_LENGTH):
                loc: Location = state.board[col][row]
                ant = loc.ant
                construction = loc.constr
                antTeam = PLAYER_ONE
                constTeam = PLAYER_ONE

                if construction is not None:
                    cType = construction.type
                    if isinstance(construction, Building):
                        constTeam = construction.player

                    if type(construction) is Building and cType == ANTHILL:
                        cCurHP = construction.captureHealth
                        cMaxHP = CONSTR_STATS[cType][1]
                        healthConst = (cMaxHP, cCurHP)
                    else:
                        healthConst = None
                else:
                    cType = None
                    healthConst = None

                if ant is not None:
                    curHP = ant.health
                    maxHP = UNIT_STATS[ant.type][1]
                    health = (maxHP, curHP)
                    moved = ant.hasMoved
                    carrying = ant.carrying
                    aType = ant.type
                    antTeam = ant.player
                else:
                    health = None
                    moved = False
                    carrying = False
                    aType = None

                # sets highlights to false
                self.boardIcons[row][col].setImage(cType, aType, antTeam, constTeam, moved, health, False, False, carrying, healthConst)

    ##
    # showSetupConstructions
    #
    # this method re-shows the constructions if the board is swapped during a human's setup phase
    def showSetupConstructions(self, phase):
        # do nothing if the player hasn't placed anything
        if self.setupsPlaced is None:
            return

        if phase == SETUP_PHASE_1:
            for i in range(self.setupsPlaced):
                loc = self.setupLocations[i]
                if i == 0:
                    self.boardIcons[loc[1]][loc[0]].setImage(construct=ANTHILL)
                elif i == 1:
                    self.boardIcons[loc[1]][loc[0]].setImage(construct=TUNNEL)
                else:
                    self.boardIcons[loc[1]][loc[0]].setImage(construct=GRASS)
        elif phase == SETUP_PHASE_2:
            for i in range(self.setupsPlaced):
                loc = self.setupLocations[i]
                self.boardIcons[loc[1]][loc[0]].setImage(construct=FOOD)


    ##
    # highlightValidMoves
    #
    # recursive method to highlight all moves
    # an ant can make from a certain location
    #
    # location - a 2 tuple of integers representing a board coordinate
    #
    def highlightValidMoves(self, location, moveLeft, queen = False, ignoresGrass = False):
        self.boardIcons[location[1]][location[0]].setImage(highlight=True)

        # if we're out of movement, then we're done
        if moveLeft <= 0:
            return

        relatives = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        # highlight the neighbors if we can move there
        for i in range(4):
            to = (location[0] + relatives[i][0], location[1] + relatives[i][1])
            # make sure the next coordinate is legal
            if 0 <= to[0] <= 9 and 0 <= to[1] <= 9:
                # queens can't move outside their home area
                if queen:
                    if self.handler.currentState.whoseTurn == PLAYER_ONE:
                        if to[1] > 3:
                            continue
                    elif to[1] < 6:
                        continue

                # if there's an ant at that location, we can't move there
                loc = self.handler.currentState.board[to[0]][to[1]]
                if loc.ant is not None:
                    continue

                # if we don't have enough movement, we can't move there
                if ignoresGrass:
                    remainder = moveLeft - 1
                else:
                    remainder = moveLeft - loc.getMoveCost()
                if remainder < 0:
                    continue

                # if there's no ant and we can move there, highlight it
                self.highlightValidMoves(to, remainder, queen, ignoresGrass)

    ##
    # clearHighlights
    #
    # clears the highlights off of all tiles
    #
    def clearHighlights(self):
        for y in range(10):
            for x in range(10):
                self.boardIcons[y][x].setImage(highlight=False, attackHighlight=False)

    ##
    # highlightValidAttacks
    #
    # highlights all ants able to be attacked by the given ant
    #
    def highlightValidAttacks(self, ant: Ant):
        # this shouldn't happen
        if ant is None:
            print("Something went wrong sending an attacking ant")
            return

        antR = UNIT_STATS[ant.type][3]
        locations = []
        attacks = listAttackable(ant.coords, antR)
        # generate list of possible ants to attack
        # these will exist in a subset of the square with radius ant attack range
        for loc in attacks:
            # we have to have an enemy ant to attack
            target = getAntAt(self.handler.currentState, loc)
            if target is None:
                continue

            if target.player == ant.player:
                continue

            # if we got here, this coordinate has a valid ant to attack
            locations.append(loc)

        # this shouldn't happen
        if len(locations) == 0:
            print("Somehow got 0 ants to attack")
            return

        for loc in locations:
            self.boardIcons[loc[1]][loc[0]].setImage(attackHighlight=True)

    ##
    # setInstructionText
    #
    # sets the text below the game board to a given string
    #
    def setInstructionText(self, text: str):
        self.messageText.set(text)

    #########################################################################
    # button handling functions
    #

    def undoPressed(self):
        # this should not happen if undo button is disabled properly
        # but we protect here nonetheless
        if not self.handler.waitingForHuman:
            return
        # if it's currently setup phase, we handle this internally to the UI
        if self.handler.phase == SETUP_PHASE_1 or self.handler.phase == SETUP_PHASE_2:
            if self.setupsPlaced is not None and self.setupsPlaced > 0:
                # clear the most recent setup from board and memory
                loc = self.setupLocations.pop()
                self.boardIcons[loc[1]][loc[0]].setImage(construct=None)
                self.setupsPlaced -= 1

                # change instruction text
                if self.handler.phase == SETUP_PHASE_1:
                    if self.setupsPlaced == 0:
                        self.undoButton.disable()
                        self.setInstructionText("Select where to place your anthill.")
                    elif self.setupsPlaced == 1:
                        self.setInstructionText("Select where to place your tunnel.")
                    elif self.setupsPlaced == 2:
                        self.setInstructionText("Select where to place grass on your side. 9 Remaining.")
                    else:
                        self.setInstructionText("Select where to place grass on your side. %d Remaining." %
                                                (11 - self.setupsPlaced))
                else:
                    self.undoButton.disable()
                    self.setInstructionText("Select where to place your enemy's food. 2 remaining.")
        elif self.handler.phase == PLAY_PHASE:
            self.handler.submitHumanMove(Move(UNDO))

    def UIbuttonPressed(self):
        self.handler.showFrame(1)

    def endTurnPressed(self, event=None):
        # ending turn is only allowed as a substitute for normal moves
        if self.handler.waitingForHuman and self.handler.phase == PLAY_PHASE and not self.handler.waitingForAttack:
            self.handler.submitHumanMove(Move(END, None, None))

    def boardButtonPressed(self, x, y):
        # if we don't need a human move, do nothing
        if not self.handler.waitingForHuman:
            return

        # handle move based on state of game
        if self.handler.phase == SETUP_PHASE_1:
            self.handleSetup1Move(x, y)
        elif self.handler.phase == SETUP_PHASE_2:
            self.handleSetup2Move(x, y)
        elif self.handler.phase == PLAY_PHASE:
            if self.handler.waitingForAttack:
                self.handleAttackMove(x, y)
            else:
                self.handleNormalMove(x, y)

    ##
    # handleSetup2Move
    #
    # handle board clicks when the game is in setup phase 2 for human
    # player is placing food for the opponent
    #
    def handleSetup2Move(self, x, y):
        # init trackers
        if self.setupsPlaced is None:
            self.setupsPlaced = 0
            self.setupLocations = []

        # construct legal places for the player to place
        possible = []
        for i in range(10):
            for j in range(4):
                if self.handler.currentState.whoseTurn == PLAYER_ONE:
                    loc = (i, 9 - j)
                else:
                    loc = (i, j)

                # food can only be placed on empty tiles
                constr = getConstrAt(self.handler.currentState, loc)
                if constr is None and loc not in self.setupLocations:
                    possible.append(loc)

        if (x, y) in possible:
            self.setupLocations.append((x, y))
            self.setupsPlaced += 1
            # enable the undo button as we've found a valid move
            self.undoButton.enable()
            self.boardIcons[y][x].setImage(construct=FOOD)
            self.setInstructionText("Select where to place your enemy's food. 1 remaining.")

            if self.setupsPlaced == 2:
                # if we're player one, submit normally
                if self.handler.currentState.whoseTurn == PLAYER_ONE:
                    locs = self.setupLocations
                # if we're player two, re have to rotate the board 180 (because each player sees themselves as P1)
                else:
                    locs = []
                    for point in self.setupLocations:
                        locs.append(self.handler.currentState.coordLookup(point, PLAYER_TWO))
                self.handler.submitHumanSetup(locs)
                self.setupsPlaced = None

    ##
    # handleSetupMove
    #
    # handles board clicks when the game is in setup phase 1 for the human
    # player is placing their own anthill, tunnel, and grass is that order
    #
    def handleSetup1Move(self, x, y):
        # init trackers
        if self.setupsPlaced is None:
            self.setupsPlaced = 0
            self.setupLocations = []

        # construct legal places for the player to place
        possible = []
        for i in range(10):
            for j in range(4):
                if self.handler.currentState.whoseTurn == PLAYER_ONE:
                    possible.append((i, j))
                else:
                    possible.append((i, 9 - j))

        # if the location is on our side and does not have anything in it
        if (x, y) in possible and (x, y) not in self.setupLocations:
            self.setupLocations.append((x, y))
            self.setupsPlaced += 1
            # enable the undo buttons as we've found a valid move
            self.undoButton.enable()

            if self.setupsPlaced == 1:
                self.boardIcons[y][x].setImage(construct=ANTHILL)
                self.setInstructionText("Select where to place your tunnel.")
            elif self.setupsPlaced == 2:
                self.boardIcons[y][x].setImage(construct=TUNNEL)
                self.setInstructionText("Select where to place grass on your side. 9 Remaining.")
            else:
                self.boardIcons[y][x].setImage(construct=GRASS)
                self.setInstructionText("Select where to place grass on your side. %d Remaining." %
                                        (11 - self.setupsPlaced))

            # if we've finished placing
            if self.setupsPlaced == 11:
                # if we're player one, submit normally
                if self.handler.currentState.whoseTurn == PLAYER_ONE:
                    locs = self.setupLocations
                # if we're player two, re have to rotate the board 180 (because each player sees themselves as P1)
                else:
                    locs = []
                    for point in self.setupLocations:
                        locs.append(self.handler.currentState.coordLookup(point, PLAYER_TWO))
                self.handler.submitHumanSetup(locs)
                self.setupsPlaced = None

    ##
    # handleNormalMove
    #
    # handles board clicks when the game is in normal play for a human
    #
    def handleNormalMove(self, x, y):
        # the user is currently looking at ant moves
        # so we should either send a move, or stop looking at this ant's moves
        if self.movesHighlighted:
            # if the user clicked on a highlighted tile, submit the move
            if self.boardIcons[y][x].highlight:
                ant: Ant = getAntAt(self.handler.currentState, self.baseLocation)
                path = createPathToward(self.handler.currentState, ant.coords, (x, y), UNIT_STATS[ant.type][0])

                # flip for player 2
                if self.handler.currentState.whoseTurn == PLAYER_TWO:
                    newPath = []
                    for point in path:
                        newPath.append(self.handler.currentState.coordLookup(point, PLAYER_TWO))
                    path = newPath

                self.handler.submitHumanMove(Move(MOVE_ANT, path, None))

                # clear bookkeeping
                self.clearHighlights()
                self.baseLocation = None
                self.movesHighlighted = False
                return
            # if the user clicked a non-highlighted square, assume they want to do something other
            # than move their selected ant. So un-select it
            else:
                self.clearHighlights()
                self.baseLocation = None
                self.movesHighlighted = False

        # if there is an ant on the tile, the only action that can be taken is with that ant
        ant: Ant = getAntAt(self.handler.currentState, (x, y))
        if ant is not None:
            if ant.hasMoved:
                # no action can be taken on a square with an ant that has already moved
                return

            if ant.player != self.handler.currentState.whoseTurn:
                # players can't move the opponent's ants
                return

            # because queens can't go outside their start area, their movement needs special handling
            isQueen = ant.type == QUEEN
            ignoresGrass = UNIT_STATS[ant.type][IGNORES_GRASS]

            # assume player wants to move this ant
            # highlight all squares the ant can move to
            self.highlightValidMoves(ant.coords, UNIT_STATS[ant.type][0], isQueen, ignoresGrass)
            self.movesHighlighted = True
            self.baseLocation = (x, y)
            return

        # if the player clicks on an anthill without an ant on it, assume they want to build
        const = getConstrAt(self.handler.currentState, (x, y))
        if const is not None:
            if const.type == ANTHILL:
                if const.player == self.handler.currentState.whoseTurn:
                    self.hillCoords = self.handler.currentState.coordLookup(const.coords, const.player)
                    # if the player clicks on their anthill, assume they want to build an ant

                    # the popup window opens really fast and can read the "open menu" click and the "build ant" click
                    # without a delay
                    # TODO: this still happens when the cursor is moving during the click, delay does not fix
                    time.sleep(.1)

                    maxExpense = self.handler.currentState.inventories[self.handler.currentState.whoseTurn].foodCount

                    popup = tkinter.Menu()
                    popup.config(tearoff=0)

                    c_active = "black"
                    c_inactive = "red"
                    fg_color = c_inactive if maxExpense <  UNIT_STATS[WORKER][4] else c_active
                    popup.add_command(label="Worker: %d" % UNIT_STATS[WORKER][4], command=partial(self.buildAnt, ant=WORKER), foreground=fg_color)
                    fg_color = c_inactive if maxExpense <  UNIT_STATS[SOLDIER][4] else c_active
                    popup.add_command(label="Soldier: %d" % UNIT_STATS[SOLDIER][4], command=partial(self.buildAnt, ant=SOLDIER), foreground=fg_color)
                    fg_color = c_inactive if maxExpense <  UNIT_STATS[R_SOLDIER][4] else c_active
                    popup.add_command(label="R Soldier: %d" % UNIT_STATS[R_SOLDIER][4], command=partial(self.buildAnt, ant=R_SOLDIER), foreground=fg_color)
                    fg_color = c_inactive if maxExpense <  UNIT_STATS[DRONE][4] else c_active
                    popup.add_command(label="Drone: %d" % UNIT_STATS[DRONE][4], command=partial(self.buildAnt, ant=DRONE), foreground=fg_color)
                    try:
                        locX = self.boardIcons[y][x].label.winfo_rootx()
                        locY = self.boardIcons[y][x].label.winfo_rooty()
                        popup.tk_popup(locX, locY)
                    finally:
                        popup.grab_release()

    def buildAnt(self, ant):
        food = self.handler.currentState.inventories[self.handler.currentState.whoseTurn].foodCount

        if food >= UNIT_STATS[ant][4]:
            self.handler.submitHumanMove(Move(BUILD, [self.hillCoords], ant))
        else:
            self.setInstructionText("You need %d food to build that ant, try something else." % UNIT_STATS[ant][4])

    ##
    # handleAttackMove
    #
    # handles board clicks when the player needs to attack an ant
    #
    def handleAttackMove(self, x, y):
        # player must submit an attack to continue the game
        if self.boardIcons[y][x].attackHighlight:
            # must flip the coordinate for p2
            self.handler.submitHumanAttack(self.handler.currentState.coordLookup((x, y),
                                                                                 self.handler.currentState.whoseTurn))
            self.clearHighlights()





class BoardButton:

    def __init__(self, parent, handler, x, y):
        self.x = x
        self.y = y
        self.handler = handler
        self.parent = parent

        # borderwidth has to be 0 to make seamless grid
        self.label = tkinter.Canvas(self.parent)
        self.label.config(bd = 0, bg = "black", width = 68, height = 68, closeenough=0, highlightthickness = 0)
        if self.y < 4:
            self.label.config(bg = "blue")
        if self.y > 5:
            self.label.config(bg = "red")

        self.label.grid(column = self.x, row = self.y)

        # create border for queen areas so there's not an awkward mix of borders
        if self.y == 4:
            self.bluBorder = tkinter.Canvas(self.parent)
            self.bluBorder.config(bd = 0, bg = "blue", width = 68, height = 2, closeenough = 0, highlightthickness = 0)
            self.bluBorder.grid(column = self.x, row = self.y, sticky = tkinter.N)
        if self.y == 5:
            self.bluBorder = tkinter.Canvas(self.parent)
            self.bluBorder.config(bd = 0, bg = "red", width = 68, height = 2, closeenough = 0, highlightthickness = 0)
            self.bluBorder.grid(column = self.x, row = self.y, sticky = tkinter.S)

        # bind click listener
        self.label.bind("<Button-1>", self.pressed)

        # set internal variables
        self.construct = None
        self.ant = None
        self.antTeam = PLAYER_ONE
        self.constTeam = PLAYER_ONE
        self.moved = False
        self.health = None
        self.healthConst = None
        self.highlight = False
        self.attackHighlight = False
        self.carrying = False

        # draw initial tile
        self.reDraw()


    def pressed(self, event):
        self.handler.boardButtonPressed(self.x, self.y)

    ##
    # setImage
    #
    # sets any number of display values to new values and redraws the tile
    #
    # construct: one of ANTHILL, TUNNEL, GRASS, or FOOD from constants.py
    # ant: one of QUEEN, WORKER, DRONE, SOLDIER, or R_SOLDIER from constants.py
    # antTeam: one of PLAYER_ONE or PLAYER_TWO from constants.py
    # constTeam: as antTeam
    # moved: either True or False
    # health: a tuple of integers in the form (max_hp, current_hp)
    # highlight: True or False
    # carrying: True or False
    #
    # all parameters may be set to None to remove that element from the draw list or replace it with a default
    #
    def setImage(self, construct = -9, ant = -9, antTeam = -9, constTeam = -9, moved = -9, health = -9, highlight = -9, attackHighlight = -9, carrying = -9, healthConst = -9):
        changed = False

        if construct != -9 and construct != self.construct:
            self.construct = construct
            changed = True
        if ant != -9 and ant != self.ant:
            self.ant = ant
            changed = True
        if antTeam != -9 and antTeam != self.antTeam:
            self.antTeam = antTeam
            changed = True
        if constTeam != -9 and constTeam != self.constTeam:
            self.constTeam = constTeam
            changed = True
        if moved != -9 and moved != self.moved:
            self.moved = moved
            changed = True
        if health != -9 and health != self.health:
            self.health = health
            changed = True
        if highlight != -9 and highlight != self.highlight:
            self.highlight = highlight
            changed = True
        if attackHighlight != -9 and attackHighlight != self.attackHighlight:
            self.attackHighlight = attackHighlight
            changed = True
        if carrying != -9 and carrying != self.carrying:
            self.carrying = carrying
            changed = True
        if healthConst != -9 and healthConst != self.healthConst:
            self.healthConst = healthConst
            changed = True

        if changed:
            self.reDraw()

    ##
    # reDraw
    #
    # re draws this tile based on its internal values
    #
    def reDraw(self):
        # general offset
        loc = (2, 2)

        # clear canvas
        self.label.delete("all")
        
        # important vals/refs
        NW = tkinter.N + tkinter.W
        my_textures = self.handler.textures
        
        # draw base
        if self.highlight:
            self.label.create_image(loc, anchor=NW, image=my_textures["terrain_green"])
        elif self.attackHighlight:
            self.label.create_image(loc, anchor=NW, image=my_textures["terrain_red"])
        elif self.moved:
            self.label.create_image(loc, anchor=NW, image=my_textures["terrain_grey"])
        else:
            self.label.create_image(loc, anchor=NW, image=my_textures["terrain"])

        # team color
        team = "Blue" if self.constTeam == PLAYER_ONE else "Red"

        # draw construct
        if self.construct == GRASS:
            self.label.create_image(loc, anchor=NW, image=my_textures["grass"])
        elif self.construct == FOOD:
            self.label.create_image(loc, anchor=NW, image=my_textures["food"])
        elif self.construct == ANTHILL:
            self.label.create_image(loc, anchor=NW, image=my_textures["anthill" + team])
        elif self.construct == TUNNEL:
            self.label.create_image(loc, anchor=NW, image=my_textures["tunnel" + team])

        # team color
        team = "Blue" if self.antTeam == PLAYER_ONE else "Red"

        # draw ant
        if self.ant == WORKER:
            self.label.create_image(loc, anchor=NW, image=my_textures["worker" + team])
            if my_textures["hat"] is not None:
                self.label.create_image((24, 9), anchor=NW, image=my_textures["hat"])
        elif self.ant == SOLDIER:
            self.label.create_image(loc, anchor=NW, image=my_textures["soldier" + team])
            if my_textures["hat"] is not None:
                self.label.create_image((23, 9), anchor=NW, image=my_textures["hat"])
        elif self.ant == QUEEN:
            self.label.create_image(loc, anchor=NW, image=my_textures["queen" + team])
            if my_textures["hat"] is not None:
                self.label.create_image((25, 7), anchor=NW, image=my_textures["hat"])
        elif self.ant == R_SOLDIER:
            self.label.create_image(loc, anchor=NW, image=my_textures["rsoldier" + team])
            if my_textures["hat"] is not None:
                self.label.create_image((23, 5), anchor=NW, image=my_textures["hat"])
        elif self.ant == DRONE:
            self.label.create_image(loc, anchor=NW, image=my_textures["drone" + team])
            if my_textures["hat"] is not None:
                self.label.create_image((23, 7), anchor=NW, image=my_textures["hat"])

        # carrying mark
        if self.carrying:
            self.label.create_image((loc[0] + 48, loc[1] + 48), anchor=NW, image=my_textures["carrying"])


        # draw health
        if self.health:
            if self.health[0] <= 8 or self.health[1] <= 8:
                blue = 0
                green = self.health[1]
                red = min(self.health[0], 8) - self.health[1]
            else:
                blue = self.health[1] - 8
                green = 8 - blue
                red = 0

            count = 0
            for j in range(blue):
                self.label.create_image((loc[0] + 3, loc[1] + count * 8), 
                                         anchor=NW, image=my_textures["healthDouble"])
                count += 1
            for j in range(green):
                self.label.create_image((loc[0] + 3, loc[1] + count * 8), 
                                         anchor=NW, image=my_textures["healthFull"])
                count += 1
            for j in range(red):
                self.label.create_image((loc[0] + 3, loc[1] + count * 8), 
                                         anchor=NW, image=my_textures["healthEmpty"])
                count += 1

        if self.healthConst:
            for k in range(self.healthConst[0]):
                if k < self.healthConst[1]:
                    self.label.create_image((loc[0] + 55, loc[1] + k * 8), 
                                             anchor=NW, image=my_textures["healthFull"])
                else:
                    self.label.create_image((loc[0] + 55, loc[1] + k * 8), 
                                             anchor=NW, image=my_textures["healthEmpty"])


