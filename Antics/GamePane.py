import tkinter
import RedoneWidgets as wgt
from Constants import *
from GameState import *
from Building import  *
from Ant import *
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

    def giveGame(self, the_game):
        self.the_game = the_game

    def createFrames(self):

        # make game board
        self.boardFrame = tkinter.Frame(self.parent)
        self.boardFrame.config(bd = 1, bg = 'black')
        self.boardIcons = []

        # create image assets
        self.textures = {}
        for f in os.listdir("Textures/"):
            s1, s2 = f.split('.')
            if s2 == "gif":
                self.textures[s1] = tkinter.PhotoImage(file = "Textures/" + f)


        # game board is based on a 10*10 grid of tiles
        for i in range(10):
            tmp = []
            for j in range(10):
                button = BoardButton(self.boardFrame, self, j, i)
                tmp.append(button)
            self.boardIcons.append(tmp)
        self.boardFrame.grid(column = 1, row = 0)

        # test board drawing
        # self.randomBoard()

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
        self.p1Label = tkinter.Label(self.playerInfoFrame)
        self.p1Label.config(textvar = self.p1Name, wraplength = 1, font = textFont, fg = 'BLUE')
        self.p1Label.grid(column = 0, row = 0)
        self.p1FoodLabel = tkinter.Label(self.playerInfoFrame)
        self.p1FoodLabel.config(textvar = self.p1Food, font = textFont, fg = 'BLUE', width = 2)
        self.p1FoodLabel.grid(column = 0, row = 1)
        self.p2FoodLabel = tkinter.Label(self.playerInfoFrame)
        self.p2FoodLabel.config(textvar = self.p2Food, font = textFont, fg = 'RED', width = 2)
        self.p2FoodLabel.grid(column = 0, row = 2)
        self.p2Label = tkinter.Label(self.playerInfoFrame)
        self.p2Label.config(textvar = self.p2Name, wraplength = 1, font = textFont, fg = 'RED')
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

        self.UIbutton = wgt.ColoredButton(self.buttonFrame, text = "Close UI", command = self.UIbuttonPressed)
        self.UIbutton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.UIbutton.grid()

        self.endTurnButton = wgt.ColoredButton(self.buttonFrame, text = "End Turn", command = self.endTurnPressed)
        self.endTurnButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.endTurnButton.grid(row = 1)

        self.pauseVar = tkinter.StringVar()
        self.pauseVar.set("Play")
        self.pauseButton = wgt.ColoredButton(self.buttonFrame, command = self.pausePressed)
        self.pauseButton.config(textvar = self.pauseVar)
        self.pauseButton.config(bg = 'green', fg = 'white', font = font, width = 12, pady = 3)
        self.pauseButton.grid(row = 2)
        self.paused = True

        self.stepButton = wgt.ColoredButton(self.buttonFrame, text = "Step", command = self.stepPressed)
        self.stepButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.stepButton.grid(row = 3)

        self.statsText = tkinter.StringVar()
        self.statsText.set("Print Stats On")
        self.statsButton = wgt.ColoredButton(self.buttonFrame, command = self.statsPressed)
        self.statsButton.config(textvar = self.statsText)
        self.statsButton.config(bg = self.blue, fg = 'white', font = font, width = 12, pady = 3)
        self.statsButton.grid(row = 4)
        self.stats = False

        self.killButton = wgt.ColoredButton(self.buttonFrame, text = "Kill Game", command = self.killPressed)
        self.killButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.killButton.grid(row = 5)

        self.restartButton = wgt.ColoredButton(self.buttonFrame, text = "Restart All", command = self.restartPressed)
        self.restartButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.restartButton.grid(row = 6)

        self.settingsButton = wgt.ColoredButton(self.buttonFrame, text = "Settings", command = self.settingsPressed)
        self.settingsButton.config(bg = 'red', fg = 'white', font = font, width = 12, pady = 3)
        self.settingsButton.grid(row =7)

        # make buttons space out a bit
        for i in range(8):
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

                self.boardIcons[y][x].setImage(construct = cons, ant = ant, antTeam = team, moved = moved,
                                               highlight = highlight, carrying = carrying, health = health)

    ##
    # setToGameState
    #
    # sets the board elements to reflect a given game state
    #
    def setToGameState(self, state: GameState):
        self.p1Name.set(self.the_game.currentPlayers[PLAYER_ONE].author[0:6] + '..' + self.the_game.currentPlayers[PLAYER_ONE].author[-3:] if len(self.the_game.currentPlayers[PLAYER_ONE].author) > 6 else self.the_game.currentPlayers[PLAYER_ONE].author[0:6])
        self.p2Name.set(self.the_game.currentPlayers[PLAYER_TWO].author[0:6] + '..' + self.the_game.currentPlayers[PLAYER_TWO].author[-3:] if len(self.the_game.currentPlayers[PLAYER_TWO].author) > 6 else self.the_game.currentPlayers[PLAYER_TWO].author[0:6])
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
                else:
                    cType = None

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

                self.boardIcons[row][col].setImage(cType, aType, antTeam, constTeam, moved, health, False, carrying)



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
        self.killPressed()
        print("Restart")

    def settingsPressed(self):
        self.killPressed()
        self.handler.showFrame(0)

    def boardButtonPressed(self, x, y):
        print("Board Clicked x: %d, y: %d" % (x, y))


class BoardButton:

    def __init__(self, parent, handler, x, y):
        self.x = x
        self.y = y
        self.handler: GamePane = handler
        self.parent: tkinter.Frame = parent

        # borderwidth has to be 0 to make seamless grid
        self.label = tkinter.Canvas(self.parent)
        self.label.config(bd = 1, bg = "black", width = 66, height = 66, highlightthickness = 0)
        self.label.grid(column = self.x, row = self.y)

        # bind click listener
        self.label.bind("<Button-1>", self.pressed)

        # set internal variables
        self.construct = None
        self.ant = None
        self.antTeam = PLAYER_ONE
        self.constTeam = PLAYER_ONE
        self.moved = False
        self.health = None
        self.highlight = False
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
    def setImage(self, construct = -9, ant = -9, antTeam = -9, constTeam = -9, moved = -9, health = -9, highlight = -9, carrying = -9):
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
        if carrying != -9 and carrying != self.carrying:
            self.carrying = carrying
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
        loc = (1, 1)

        # clear canvas
        self.label.delete("all")
        
        # draw base
        self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["terrain"])

        # team color
        if self.constTeam == PLAYER_ONE:
            team = "Blue"
        else:
            team = "Red"

        # draw construct
        if self.construct == GRASS:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["grass"])
        elif self.construct == FOOD:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["food"])
        elif self.construct == ANTHILL:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["anthill" + team])
        elif self.construct == TUNNEL:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["tunnel" + team])

        # team color
        if self.antTeam == PLAYER_ONE:
            team = "Blue"
        else:
            team = "Red"

        # draw ant
        if self.ant == WORKER:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["worker" + team])
        elif self.ant == SOLDIER:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["soldier" + team])
        elif self.ant == QUEEN:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["queen" + team])
        elif self.ant == R_SOLDIER:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["rsoldier" + team])
        elif self.ant == DRONE:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["drone" + team])

        # carrying mark
        if self.carrying:
            self.label.create_image((loc[0] + 48, loc[1] + 48), anchor=tkinter.N + tkinter.W,
                                    image=self.handler.textures["carrying"])

        # hasMoved marker
        if self.moved:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["moved"])

        # highlighted marker
        elif self.highlight:
            self.label.create_image(loc, anchor=tkinter.N + tkinter.W, image=self.handler.textures["highlighted"])

        # draw health
        if self.health:
            for i in range(self.health[0]):
                if i <= self.health[1]:
                    self.label.create_image((loc[0] + 3, loc[1] + i * 8), anchor=tkinter.N + tkinter.W,
                                            image=self.handler.textures["healthFull"])
                else:
                    self.label.create_image((loc[0] + 3, loc[1] + i * 8), anchor=tkinter.N + tkinter.W,
                                            image=self.handler.textures["healthEmpty"])






