import tkinter as tk
from tkinter.font import Font
from functools import partial
from tkinter import ttk
import time
import RedoneWidgets as wgt
import re
from tkinter import messagebox
import threading
import copy
import Constants as cnst
import Ant as AntMod
import Construction as ConstrMod

PLAYERS = []
for i in range(10):
    PLAYERS.append ( "AI #" + str(i) )
PLAYER_COLS = 1 

GAME_TYPES = [ "QuickStart", "Two Player", "Single Player", "Round Robin", "Play All" ]
ANT_NAMES = [ "Workers", "Drones", "Soldiers", "Ranged Soldiers" ]

PLAYER_COLORS = [ "red", "blue" ] 
PLAYER_COLORS_LIGHT = [ wgt.LIGHT_RED, wgt.LIGHT_BLUE ]

FRAME_BDR = 5

LAYOUT_OPTIONS = [ "Player Invoked", "Random Override" ]

# frame label settings
FL_COLOR = "black"
FL_TEXT_COLOR = "white"
FL_BD = 5
FL_STYLE = "ridge"
FL_FONT = ( "Harrington", 18, "bold")
# Papyrus, Harrington, Herculanum, Desdemona, Wingdings

# button font
BUTTON1_FONT = ( "Copperplate", 20, "bold")
BUTTON2_FONT = ( "Copperplate", 15, "bold")

ERROR_CODE = -1

class GameSettingsFrame ( ) :
    
    def __init__(self, handler, parent = None):
        # initialize UI object

        # store event handler to close later
        self.parent = parent
        self.handler = handler

        #### IMPORTANT - DATA STORAGE ####
        self.my_games = [] # store all of the GameGUIData objects here
        self.my_pause_conditions = []
        ##################################
        
        

    def changePlayers ( self, plyrs ) :
        global PLAYERS
        PLAYERS = plyrs

    def giveGame ( self, the_game ) :
        self.the_game = the_game

    def createFrames ( self ) :
        ####
        # GUI
        # configure rows and columns of the main frame
        for r in range(23):
            self.parent.rowconfigure(r, weight=1)

        for c in range(2): 
            if c > 0 : 
                self.parent.columnconfigure(c, weight=1)
            else :
                self.parent.columnconfigure(c, weight=0)

        ##########################
        # left side -- queues and start

        # game queue
        self.gameQFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" )
        self.gameQFrame.grid ( row = 1, column = 0, rowspan = 10, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.gameQLabel = tk.Label ( self.gameQFrame, text = "Game Queue", \
                                     fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.gameQLabel.pack ( side=tk.TOP, fill=tk.X )
        self.gameQClearButton = wgt.ColoredButton ( self.gameQFrame, "Clear All Games", wgt.RED, "black", self.clearGameList )
        self.gameQClearButton.config ( font = BUTTON2_FONT )
        self.gameQClearButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )
        
        self.myGamesFrame = tk.Frame ( self.gameQFrame, bg="white",bd=5 )
        self.gamesScrollFrame = wgt.ScrollableFrame ( self.myGamesFrame )
        self.gamesScrollFrame.config( padx = 2, pady=2 )
        self.gamesScrollFrame.canvas.config(height=300)

        self.myGamesFrame.pack ( fill="both" )
        self.gamesScrollFrame.pack ( fill="both" )

        # pause condition log
        self.pauseConditionsFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" ) 
        self.pauseConditionsFrame.grid ( row = 12, column = 0, rowspan = 9, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.pauseConditionsLabel = tk.Label ( self.pauseConditionsFrame, text = "Pause Conditions", \
                                               fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.pauseConditionsLabel.pack ( side=tk.TOP, fill=tk.X )
        self.pauseConditionsClearButton = wgt.ColoredButton ( self.pauseConditionsFrame, "Clear All Pause Conditions",\
                                                              wgt.RED, "black", self.clearPCList )
        self.pauseConditionsClearButton.config ( font = BUTTON2_FONT )
        self.pauseConditionsClearButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )

        self.myPCFrame = tk.Frame ( self.pauseConditionsFrame, bg="white",bd=5 )
        self.pcScrollFrame = wgt.ScrollableFrame ( self.myPCFrame )
        self.pcScrollFrame.config( padx = 2, pady=2 )
        self.pcScrollFrame.canvas.config(height=200)

        self.myPCFrame.pack ( fill="both" )
        self.pcScrollFrame.pack ( fill="both" )

        # start button
        self.startButtonFrame = tk.Frame ( self.parent, bg="white" )
        self.startButtonFrame.grid ( row = 21, column = 0, rowspan = 1, columnspan = 1, sticky = tk.E+tk.W )

        self.startButton = wgt.ColoredButton ( self.startButtonFrame, "START", wgt.GREEN, "black", self.changeFrameStart  )
        self.startButton.config ( font = BUTTON1_FONT )
        self.startButton.pack ( fill = tk.X )

        ##########################
        # right side -- add game, additional settings, add pause conditions
        
        # add a game
        self.addGameFrame = tk.Frame(self.parent, bg = "black", padx = FRAME_BDR, pady=FRAME_BDR )
        self.addGameFrame.grid(row = 1, column = 1, rowspan = 7, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.addGameType = tk.StringVar ( self.addGameFrame )
        self.addGameType.set(GAME_TYPES[0])
        self.addGameOptionMenu = tk.OptionMenu(self.addGameFrame, self.addGameType, *GAME_TYPES, command = self.addGameChanged )
        self.addGameOptionMenu.config ( font=FL_FONT )
        self.addGameOptionMenu.pack ( fill=tk.X, side=tk.TOP )

        self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
        self.addGameOptionsWindow.startButton.command = self.changeFrameQS
        
        # additional settings
        self.additionalSettingsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR ) 
        self.additionalSettingsFrame.grid(row = 9, column = 1, rowspan = 6, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.additionalSettingsLabel = tk.Label(self.additionalSettingsFrame, text = "Additional Settings", \
                                                fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.additionalSettingsLabel.pack ( fill=tk.X )

        self.additionalOptionsFrame = AdditionalSettingsOptionsFrame ( self.additionalSettingsFrame )
        self.additionalOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        # add pause condition
        self.addPauseConditionsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR )
        self.addPauseConditionsFrame.grid(row = 16, column = 1, rowspan = 6, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.addPauseConditionsLabel = tk.Label(self.addPauseConditionsFrame, text = "Add Pause Conditions", \
                                                fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.addPauseConditionsLabel.pack ( fill=tk.X )

        self.addPauseOptionsFrame = AddPauseOptionsFrame ( self.addPauseConditionsFrame )
        self.addPauseOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        self.addPauseConditionPlus = wgt.ColoredButton ( self.addPauseConditionsFrame, " "*2 + "+" + " "*2, "black", "white" )
        self.addPauseConditionPlus.config ( font = BUTTON1_FONT )
        self.addPauseConditionPlus.pack ( side=tk.LEFT )
        self.addPauseConditionPlus.command = self.pauseConditionAdded

        #o_swap,o_gameBoard,o_verbose,o_timeout,o_timeoutText,o_layout
        

    #####
    # addGameChanged
    #
    # changes the add game options, to be used when the dropdown is changed
    #####
    def addGameChanged ( self, option ) :
        self.addGameOptionsWindow.destroy()

        if option == "QuickStart" :
            self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
            self.addGameOptionsWindow.startButton.command = self.changeFrameQS
        elif option == "Single Player" :
            self.addGameOptionsWindow = SinglePlayerFrame ( self.addGameFrame )
        elif option == "Two Player" :
            self.addGameOptionsWindow = TwoPlayerFrame ( self.addGameFrame )
        elif option == "Round Robin" :
            self.addGameOptionsWindow = RoundRobinFrame ( self.addGameFrame )
        elif option == "Play All" :
            self.addGameOptionsWindow = SinglePlayerFrame ( self.addGameFrame, "All Others" )

        if option != "QuickStart" :
            self.addGameOptionsWindow.plusButton.command = self.gameAdded
        self.addGameOptionsWindow.pack ( fill="both", side=tk.BOTTOM )

    def changeFrameStart ( self ) :
        print("start pressed")
        self.the_game.process_settings ( [ g.copy() for g in self.my_games ] )
        self.the_game.gameStartRequested ()
        self.handler.showFrame(2)

    def changeFrameQS ( self ) :
        print("quickstart pressed")
        orig_len = len ( self.my_games )
        self.gameAdded()
        # make sure that game was added, if so, start
        new_len =  len ( self.my_games ) 
        if orig_len + 1 == new_len :
            g = self.my_games.pop ( new_len - 1 )
            self.the_game.process_settings ( [ g ] )
            self.the_game.gameStartRequested ()
            self.handler.showFrame(2)
        
    def gameAdded ( self ) :
        t = self.addGameType.get() 
        n = self.addGameOptionsWindow.get_num_games ()
        p = self.addGameOptionsWindow.get_players ()
        box_needed = self.addGameOptionsWindow.is_box_needed ()

        # adjust the game type for quickstart
        if t == "QuickStart" :
            num_p = len ( p )
            if num_p == 0 :   # error
                wgt.ShowError( "Error: QuickStart", "Error: No players selected.", self.handler.root )
                return
            elif num_p == 1 : # human versus agent
                p.append ( "human" )
                t = "Two Player"
            else :            # num_p can be classified as round robin
                t = "Round Robin"
        
        # convert n to integer
        rgx_int = re.compile ( "^[0-9]+$" )
        if not rgx_int.match(n) :
            title = "Error: Game Addtion"
            message = "No game added.\nError: Invalid number of games: {}".format(n)
            wgt.ShowError( title, message, self.handler.root )
            return
        n = int ( n )

        # verify valid number of games
        if n < 1 :
            title = "Error: Game Addtion"
            message = "No game added.\nError: Invalid number of games: {}".format(n)
            wgt.ShowError( title, message, self.handler.root )
            return

        # verify valid players
        if p is None or p == [] :
            title = "Error: Game Addtion"
            message = "No game added.\nError: Not enough players."
            wgt.ShowError( title, message, self.handler.root )
            return

        # ensure that two player games have two different players
        if t == "Two Player" and p[0] == p[1] :
            title = "Error: Game Addtion"
            message = "No game added.\nError: Use 'Play Self' instead of 'Two Player' for an agent to play itself."
            wgt.ShowError( title, message, self.handler.root )
            return

        # make the new game
        b = None
        if box_needed :
            b = BlueBox ( self.gamesScrollFrame.interior )
            b.grid (sticky=tk.W)
            self.gamesScrollFrame.set_scrollregion() # update the scroll bar
        new_game = GameGUIData ( t, n, p, b )
        if box_needed :
            new_game.gui_box.delButton.command = partial ( self.deleteSingleGame, new_game )
        self.my_games.append ( new_game )
        self.parent.update()

        return

    def clearGameList ( self ) :
        for g in self.my_games :
            g.gui_box.destroy()

        self.my_games = []

    def deleteSingleGame ( self, gameGUIDataObj ) :
        gameGUIDataObj.gui_box.destroy()
        self.my_games.remove ( gameGUIDataObj )

    def clearPCList ( self ) :
        for g in self.my_pause_conditions :
            g.gui_box.destroy()

        self.my_games = []

    def deletePC ( self, pauseConditionGUIDataObj ) :
        pauseConditionGUIDataObj.gui_box.destroy()
        self.my_pause_conditions.remove ( pauseConditionGUIDataObj )

    def pauseConditionAdded ( self,  ) :
        c = {}
        p = []
        
        keys = sorted ( list (self.addPauseOptionsFrame.public_selected.keys()) )
        for k in keys :
            if self.addPauseOptionsFrame.public_selected[k] :
                if "Player" not in k :
                    c[k] = int (self.addPauseOptionsFrame.public_values[k])
                else :
                    p.append ( self.addPauseOptionsFrame.public_values[k] )
            else:
                continue

        c_keys = list(c.keys()) 
        if len( c_keys ) < 1 :
            title = "Error: Pause Condition Addtion"
            message = "No pause condition added.\nError: No conditions have been selected (checked)".format(k)
            wgt.ShowError( title, message, self.handler.root )
            return

        for k in c_keys :
            if c[k] == ERROR_CODE :
                title = "Error: Pause Condition Addtion"
                message = "No pause condition added.\nError: Pause Condition missing value for: {}".format(k)
                wgt.ShowError( title, message, self.handler.root )
                return
        
        b = BlueBox ( self.pcScrollFrame.interior )
        b.grid (sticky=tk.W)
        self.pcScrollFrame.set_scrollregion()
        new_pc = PauseConditionGUIData ( c, p, b )
        new_pc.gui_box.delButton.command = partial ( self.deletePC, new_pc )
        self.my_pause_conditions.append (new_pc)
        self.parent.update()

######################################################################################
# DATA/SETTINGS COLLECTION OBJECTS
# game and pause conditions objects
# contain blue box widget and data on the pause condition or game
######################################################################################
class GameGUIData () :
    def __init__ ( self, game_type = "", num_games = 0, players = [], box = None ) :
        self.game_type = game_type
        self.num_games = num_games
        self.players = players

        if box is not None :
            box.setTopText ( " ".join( [ str(game_type) +",", "Games :", str(num_games)] ) )
            box.setTextLines ( [ ", ".join ( players ) ] )
        self.gui_box = box

    def copy ( self ) :
        return GameGUIData ( self.game_type, self.num_games, [ p for p in self.players ] )

class PauseConditionGUIData () :
    def __init__ ( self, conditions = {}, players = [], box = None ) :
        self.conditions = conditions
        self.players = players
        if box is not None :
            box.setTopText ( "P0: " + self.players[0] + ", P1: " + self.players[1])
            box.setTextLines ( self.getPCStr() )
        self.gui_box = box

    def getPCStr ( self ) :
        s = []
        for k in list ( self.conditions.keys() ) :
            s.append ( k + ": " + str(self.conditions[k]) )
        return s
        
######################################################################################
# SPECIAL SETTINGS WIDGETS
# delete-able boxes
######################################################################################
#####
# BlueBox
#
# used for the game queue and pause conditions log
#####
class BlueBox ( tk.Frame ) :
    def __init__ ( self, parent = None) :
        tk.Frame.__init__(self, parent)
        self.parent = parent

        bc = wgt.LIGHT_BLUE
        fnt = ( "Courier", 12 )
        self.maxl = 34

        self.config ( bg = bc, padx = 2, pady = 2, width = 500 )
        self.config ( highlightbackground="white", highlightcolor="white", highlightthickness=2, bd= 0 )

        self.myTopText = tk.StringVar()
        self.setTopText ( "game type num games",  )
        self.topLabel = tk.Label ( self, textvar = self.myTopText, anchor=tk.W, justify=tk.LEFT, bg = bc, font = fnt )
        self.topLabel.grid ( row = 0, column = 0, columnspan = 8, sticky = tk.W )
        
        self.delButton = wgt.ColoredButton ( self, "x", "white", wgt.RED )
        self.delButton.config ( font = BUTTON1_FONT )
        self.delButton.grid ( row = 0, column = 8 )

        self.textLines = []
        self.myText = tk.StringVar()
        self.setTextLines ( [ "player,"*50 ] )
        
        self.myTextFrame = tk.Frame ( self, bg = bc, padx = 2, pady = 2 )
        self.myTextLabel = tk.Label ( self.myTextFrame, textvar = self.myText, anchor=tk.W, justify=tk.LEFT, bg = bc, font = fnt )
        self.myTextLabel.pack()
        self.myTextFrame.grid ( row = 1, column = 0, columnspan = 8 )

    #####
    # setTextLines
    # set the lower text level
    #####
    def setTextLines ( self, textArray ) :
        padded = []
        for l in textArray :
            for i in range ( 0, len(l), self.maxl ) :
                cur = l [i: i+self.maxl ]
                cur = cur + " " * ( self.maxl - len (cur) )
                padded.append ( cur )

        self.myText.set ( "\n".join ( padded ) )

    #####
    # setTopText
    # set the top text level ( same line as the delete button )
    #####
    def setTopText ( self, txt ) :
        self.myTopText.set ( txt + " " * ( self.maxl - len (txt) ) )
 

######################################################################################
# INTERIOR FRAMES USED FOR QUEUES, ADDITIONAL SETTINGS, PAUSE CONDITIONS
# generally use a scrollable frame in some form
######################################################################################
class AdditionalSettingsOptionsFrame ( wgt.ScrollableFrame ) :
    def __init__ ( self, parent = None) :
        wgt.ScrollableFrame.__init__(self, parent)
        self.parent = parent

        self.canvas.config(height=100)

        self.selected = {}

        # accessible by other classes
        self.public_selected = {}
        self.public_layout = LAYOUT_OPTIONS[0]
        self.public_timeout = ERROR_CODE

        k = "swap"
        self.o_swap = tk.Checkbutton ( self.interior, text = "alternate player start", command = partial(self.clicked, opt = k) )
        self.o_swap.grid ( row = 0, sticky=tk.W )
        self.selected[k] = tk.BooleanVar()
        self.o_swap.config ( variable = self.selected[k] )
        self.public_selected[k] = False

        k = "game_board"
        self.o_gameBoard = tk.Checkbutton ( self.interior, text = "display game board", command = partial(self.clicked, opt = k) )
        self.o_gameBoard.grid ( row = 1, sticky=tk.W )
        self.selected[k] = tk.BooleanVar()
        self.o_gameBoard.config ( variable = self.selected[k] )
        self.public_selected[k] = False

        k = "verbose"
        self.o_verbose = tk.Checkbutton ( self.interior, text = "verbose (print W/L)", command = partial(self.clicked, opt = k) )
        self.o_verbose.grid ( row = 2, sticky=tk.W )
        self.selected[k] = tk.BooleanVar()
        self.o_verbose.config ( variable = self.selected[k] )
        self.public_selected[k] = False

        k = "timeout"
        self.o_timeout = tk.Checkbutton ( self.interior, text = "move timeout", command = partial(self.clicked, opt = k) )
        self.o_timeout.grid ( row = 3, sticky=tk.W )
        self.selected[k] = tk.BooleanVar()
        self.o_timeout.config ( variable = self.selected[k] )
        self.public_selected[k] = False

        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.timeChanged(sv))
        self.o_timeoutText = tk.Entry ( self.interior, textvar = sv )
        self.o_timeoutText.grid ( row = 3, column = 1, sticky=tk.W )
        
        self.layoutText = tk.Label ( self.interior, text = "Layout Option: " )
        self.layoutText.grid ( row = 4, sticky=tk.W )
        self.layoutType = tk.StringVar ( self.interior )
        self.layoutType.set(LAYOUT_OPTIONS[0])
        self.o_layout = tk.OptionMenu(self.interior, self.layoutType, *LAYOUT_OPTIONS, command = self.layoutChanged )
        self.o_layout.grid ( row = 4, column = 1, sticky=tk.W )
            
    def clicked ( self, opt ) :
        print(opt)
        self.public_selected[opt] = not self.public_selected[opt]

    def timeChanged ( self, sv  ) :
        self.public_timeout = sv.get()
        print ( "timeout: ", sv.get() )

    def layoutChanged ( self, option ) :
        self.public_layout = option

class AddPauseOptionsFrame ( wgt.ScrollableFrame ) :
    def __init__ ( self, parent = None) :
        wgt.ScrollableFrame.__init__(self, parent)
        self.parent = parent

        self.tracking = { 
            "Food" : cnst.FOOD_GOAL + 1,
            "Queen Health" : AntMod.UNIT_STATS [ cnst.QUEEN ] [ cnst.HEALTH ] + 1,
            "Anthill Health" : ConstrMod.CONSTR_STATS [ 0 ] [ cnst.CAP_HEALTH ] + 1, 
            "Num Ants" : 100
            }
        for a in ANT_NAMES :
            self.tracking ["Num " + a] = 100
            
        self.selected = {}
        self.values = {}
        self.public_selected = {}
        self.public_values = {}

        self.track_options = list ( self.tracking.keys() )
        num_trackables = len(self.track_options)

        for i in range ( 2 ) :
            c = PLAYER_COLORS[i]
            c_light = PLAYER_COLORS_LIGHT[i]
            offset = i*(num_trackables+1)
            item_name = "Player " + str(i) 
            f = tk.Frame ( self.interior, bg = c_light, padx = 2, pady = 2 )
            pLabel = tk.Label ( f, text = item_name + ":" + " "*12, fg=c )
            pLabel.config ( font = BUTTON1_FONT )
            pLabel.grid ( row = offset, sticky=tk.W)
            
            # PLAYERS
            var = tk.StringVar ( self.interior )
            self.values[item_name] = ttk.Combobox ( f, values = ["Any Player"] + PLAYERS, textvariable = var, state = "readonly" )
            self.selected[item_name] = tk.BooleanVar().set ( True )
            bText = self.values[item_name]
            bText.grid ( row = offset, column = 1, sticky=tk.W )
            f.grid ( row = offset, column = 0, columnspan = 2, sticky=tk.W+tk.E )
            bText.bind("<<ComboboxSelected>>", partial ( self.newSelection, idx = item_name ) )
            bText.current(0)
            
            self.public_selected[item_name] = True
            self.public_values[item_name] = "Any AI"
            

            for j in range ( num_trackables ) :
                o = self.track_options[j]
                item_name = "P" + str(i) + " " + o # P<1/2> item
                self.selected[item_name] = tk.BooleanVar()
                loc = j + offset + i + 1
                b = tk.Checkbutton ( self.interior, text = item_name, variable = self.selected[item_name], \
                                     command = partial ( self.newSelection, value = "dummy", idx = item_name ) )
                b.grid ( row = loc, sticky=tk.W )

                var = tk.StringVar ( self.interior )
                self.values[item_name] = ttk.Combobox ( self.interior, values = list(range(self.tracking[o])), \
                                                        textvariable = var, state = "readonly" ) #, bg = c, fg = "white" )
                bText = self.values[item_name]
                bText.grid ( row = loc, column = 1, sticky=tk.W )
                bText.bind("<<ComboboxSelected>>", partial ( self.newSelection, idx = item_name ) )

                bText.current(0)

                self.public_selected[item_name] = False
                self.public_values[item_name] = ERROR_CODE


    #####
    # newSelection
    # adapt the public variables when a change has been made
    # other frames can't access the others
    #####
    def newSelection ( self, value, idx ) :
##        if "Player" not in idx:
##            print ( idx, self.values[idx].get(), self.selected[idx].get() )
##        else :
##            print ( idx, self.values[idx].get(), self.public_selected[idx] )
        
        self.public_selected[idx] = self.selected[idx].get() if "Player" not in idx else True
        
        v = self.values[idx].get()
        self.public_values[idx] = v
        if v == "" or v is None :
            self.public_values[idx] = ERROR_CODE if "Player" not in idx else "Any AI"
                

######################################################################################
# FRAMES USED TO ADD A GAME
######################################################################################
class QuickStartFrame ( tk.Frame ) :
    def __init__(self, parent = None):
        # initialize UI object
        tk.Frame.__init__(self, parent)
        # store event handler to close later
        self.parent = parent
        self.config ( padx = 2, pady=2 )
        self.pack ( fill="both", side=tk.BOTTOM )

        self.playersFrame = wgt.ScrollableFrame(self)
        self.playersFrame.config( padx = 2, pady=2 )
        self.playersFrame.canvas.config(height=200)

        self.players = PLAYERS + ["Select All"]
        playerCheckButtons = []

        self.selected = {}

        cols = PLAYER_COLS

        for i in range ( len(self.players) ) :
            p = self.players[i]
            self.selected[p] = tk.BooleanVar()
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p] )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )
            if p == "Select All" :
                b.config ( command = self.selectAllPlayers )

        self.gameStartFrame = tk.Frame ( self )
        
        self.numGamesFrame = tk.Frame ( self.gameStartFrame )
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.startButton = wgt.ColoredButton ( self.gameStartFrame, "QuickStart", wgt.LIGHT_GREEN, "black" )
        self.startButton.pack ( fill=tk.X, side=tk.BOTTOM )
        self.startButton.config ( font = BUTTON2_FONT )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )

        self.gameStartFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )

    def selectAllPlayers ( self ) :
        v = 0
        if self.selected["Select All"].get() :
            v = 1
        for x in self.players :
            if x != "Select All"  :
                self.selected[x].set(v)
                self.update()

    #####
    # !!!! TO DO !!!!!
    #####
    def get_players ( self ) :
        p = []
        for x in self.players :
            if x != "Select All" and self.selected[x].get() :
                p.append ( x )
            
        return p

    def get_num_games ( self ) :
        return self.numGamesEntry.get()

    def is_box_needed ( self ) :
        return False


class TwoPlayerFrame ( tk.Frame ) :
    def __init__(self, parent = None):
        # initialize UI object
        tk.Frame.__init__(self, parent)
        # store event handler to close later
        self.parent = parent
        self.config ( padx = 2, pady=2 )
        self.pack ( side=tk.BOTTOM )

        self.playersFrame = tk.Frame ( self )

        self.players = PLAYERS + ["Human"]
        self.player1Text = tk.Label ( self.playersFrame, text = "Player 1:" )
        self.player1Text.grid ( row = 0, column = 0, rowspan = 1, columnspan = 1, sticky = tk.W )
        self.player1Type = tk.StringVar ( self )
        self.player1Type.set(self.players[0])
        self.o_player1 = tk.OptionMenu(self.playersFrame, self.player1Type, *self.players )
        self.o_player1.grid ( row = 0, column = 1, rowspan = 1, columnspan = 10, sticky = tk.W )

        self.player2Text = tk.Label ( self.playersFrame, text = "Player 2:" )
        self.player2Text.grid ( row = 1, column = 0, rowspan = 1, columnspan = 1, sticky = tk.W )
        self.player2Type = tk.StringVar ( self )
        self.player2Type.set(self.players[0])
        self.o_player2 = tk.OptionMenu(self.playersFrame, self.player2Type, *self.players )
        self.o_player2.grid ( row = 1, column = 1, rowspan = 1, columnspan = 10, sticky = tk.W )

        self.filler = tk.Label ( self.playersFrame, text="\n"*10 )
        self.filler.grid ( row = 2, column = 0, rowspan = 1, columnspan = 1 )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white"  )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )
        
    def get_players ( self ) :
        return [ self.player1Type.get(), self.player2Type.get() ]

    def get_num_games ( self ) :
        return self.numGamesEntry.get()

    def is_box_needed ( self ) :
        return True
    
# can be used for single player - playing self or playing all
class SinglePlayerFrame ( tk.Frame ) :
    def __init__(self, parent = None, p2Note = "Self"):
        # initialize UI object
        tk.Frame.__init__(self, parent)
        # store event handler to close later
        self.parent = parent
        self.config ( padx = 2, pady=2 )
        self.pack ( side=tk.BOTTOM )

        self.playersFrame = tk.Frame ( self )

        self.playerText = tk.Label ( self.playersFrame, text = "Player 1:" )
        self.playerText.grid ( row = 0, column = 0, rowspan = 1, columnspan = 1, sticky = tk.W )
        self.playerType = tk.StringVar ( self )
        self.playerType.set(PLAYERS[0])
        self.o_player = tk.OptionMenu(self.playersFrame, self.playerType, *PLAYERS )
        self.o_player.grid ( row = 0, column = 1, rowspan = 1, columnspan = 10, sticky = tk.W )

        self.player2Text = tk.Label ( self.playersFrame, text = "Player 2:" )
        self.player2Text.grid ( row = 11, column = 0, rowspan = 1, columnspan = 1, sticky = tk.W )
        self.player2AutoText = tk.Label ( self.playersFrame, text = " " + p2Note )
        self.player2AutoText.grid ( row = 11, column = 1, rowspan = 1, columnspan = 10, sticky = tk.W )

        self.filler = tk.Label ( self.playersFrame, text="\n"*10 )
        self.filler.grid ( row = 12, column = 0, rowspan = 1, columnspan = 1 )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white"  )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )
        
    def get_players ( self ) :
        return [ self.playerType.get() ]

    def get_num_games ( self ) :
        return self.numGamesEntry.get()

    def is_box_needed ( self ) :
        return True
    
class RoundRobinFrame ( tk.Frame ) :
    def __init__(self, parent = None):
        # initialize UI object
        tk.Frame.__init__(self, parent)
        # store event handler to close later
        self.parent = parent
        self.config ( padx = 2, pady=2 )
        self.pack ( fill="both", side=tk.BOTTOM )

        self.playersFrame = wgt.ScrollableFrame(self)
        self.playersFrame.canvas.config(height=225)
        self.playersFrame.config( padx = 2, pady=2 )

        self.players = PLAYERS + ["Select All"]
        playerCheckButtons = []

        self.selected = {}

        cols = PLAYER_COLS

        for i in range ( len(self.players) ) :
            p = self.players[i]
            self.selected[p] = tk.BooleanVar()
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p] )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )
            if p == "Select All" :
                b.config ( command = self.selectAllPlayers )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white"  )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )

        self.playersFrame.pack ( fill="both" )

    def selectAllPlayers ( self ) :
        v = 0
        if self.selected["Select All"].get() :
            v = 1
        for x in self.players :
            if x != "Select All"  :
                self.selected[x].set(v)
                self.update()
                
    def get_players ( self ) :
        p = []
        for x in self.players :
            if x != "Select All" and self.selected[x].get() :
                p.append ( x )
            
        return p

    def get_num_games ( self ) :
        return self.numGamesEntry.get()

    def is_box_needed ( self ) :
        return True

       


