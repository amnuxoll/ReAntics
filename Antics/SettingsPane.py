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
import json
from os.path import exists

PLAYERS = []
for i in range(10):
    PLAYERS.append ( "AI #" + str(i) ) # to be changed later
PLAYER_COLS = 1 

GAME_TYPES = [ "QuickStart", "Two Player", "Play Self", "Round Robin", "Play All" ]
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
# Papyrus, Harrington, Herculanum, Desdemona, Wingdings :)

# button font
BUTTON1_FONT = ( "Copperplate", 20, "bold")
BUTTON2_FONT = ( "Copperplate", 15, "bold")

ERROR_CODE = -1

SETTINGS_FILE = "my-settings.json"

########################################################################
# GameSettingsFrame
#
# tkinter frame for the settings menu
# includes the quickstart menu, a game queue, and pause conditions list
########################################################################
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

        self.the_game = None
        
    ###
    # to be called once the AIs are loaded in Game.py
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
        self.gameQFrame.grid ( row = 1, column = 0, rowspan = 8, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.gameQLabel = tk.Label ( self.gameQFrame, text = "Game Queue", \
                                     fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.gameQLabel.pack ( side=tk.TOP, fill=tk.X )
        self.gameQClearButton = wgt.ColoredButton ( self.gameQFrame, "Clear All Games", wgt.RED, "black", self.clearGameList, True )
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
        self.pauseConditionsFrame.grid ( row = 10, column = 0, rowspan = 8, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.pauseConditionsLabel = tk.Label ( self.pauseConditionsFrame, text = "Pause Conditions", \
                                               fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.pauseConditionsLabel.pack ( side=tk.TOP, fill=tk.X )
        self.pauseConditionsClearButton = wgt.ColoredButton ( self.pauseConditionsFrame, "Clear All Pause Conditions",\
                                                              wgt.RED, "black", self.clearPCList, True )
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
        self.startButtonFrame.grid ( row = 18, column = 0, rowspan = 1, columnspan = 1, sticky = tk.E+tk.W )

        self.startButton = wgt.ColoredButton ( self.startButtonFrame, "START", wgt.GREEN, "black", self.changeFrameStart, True  )
        self.startButton.config ( font = BUTTON1_FONT )
        self.startButton.pack ( fill = tk.X )

        ##########################
        # right side -- add game, additional settings, add pause conditions
        
        # add a game
        self.addGameFrame = tk.Frame(self.parent, bg = "black", padx = FRAME_BDR, pady=FRAME_BDR )
        self.addGameFrame.grid(row = 1, column = 1, rowspan = 6, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.addGameType = tk.StringVar ( self.addGameFrame )
        self.addGameType.set(GAME_TYPES[0])
        self.addGameOptionMenu = tk.OptionMenu(self.addGameFrame, self.addGameType, *GAME_TYPES, command = self.addGameChanged )
        self.addGameOptionMenu.config ( font=FL_FONT )
        self.addGameOptionMenu.pack ( fill=tk.X, side=tk.TOP )

        self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
        self.addGameOptionsWindow.startButton.command = self.changeFrameQS
        
        # additional settings
        self.additionalSettingsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR ) 
        self.additionalSettingsFrame.grid(row = 7, column = 1, rowspan = 5, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.additionalSettingsLabel = tk.Label(self.additionalSettingsFrame, text = "Additional Settings", \
                                                fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.additionalSettingsLabel.pack ( fill=tk.X )

        self.additionalOptionsFrame = AdditionalSettingsOptionsFrame ( self.additionalSettingsFrame )
        self.additionalOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        # add pause condition
        self.addPauseConditionsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR )
        self.addPauseConditionsFrame.grid(row = 13, column = 1, rowspan = 6, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S)

        self.pcLabelFrame = tk.Frame(self.addPauseConditionsFrame)
        self.pcLabelFrame.pack(fill=tk.X)

        self.addPauseConditionPlus = wgt.ColoredButton ( self.pcLabelFrame, " "*1 + "+" + " "*1, "black", "white", flash=True )
        self.addPauseConditionPlus.config ( font = BUTTON1_FONT )
        self.addPauseConditionPlus.pack ( side=tk.LEFT )
        self.addPauseConditionPlus.command = self.pauseConditionAdded

        self.addPauseConditionsLabel = tk.Label(self.pcLabelFrame, text = "Add Pause Conditions", \
                                                fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.addPauseConditionsLabel.pack ( fill=tk.X )

        self.addPauseOptionsFrame = AddPauseOptionsFrame ( self.addPauseConditionsFrame )
        self.addPauseOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        self.dummyPCLabel = None
        self.dummyGameLabel = None

        # saved settings?
        self.loadSavedSettings()
        
        

    #####
    # addGameChanged
    # changes the add game options, to be used when the dropdown is changed
    #
    # Parameters:
    #   option -- the selected game option
    #####
    def addGameChanged ( self, option ) :
        self.addGameOptionsWindow.destroy()

        if option == "QuickStart" :
            self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
            self.addGameOptionsWindow.startButton.command = self.changeFrameQS
        elif option == "Play Self" :
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

    ###
    # connected to the start button
    # saves all of the current settings to the settings file
    # and passes them to the game
    def changeFrameStart ( self ) :
        if self.the_game is None: return
        
        games = [ g.copy() for g in self.my_games ]
        more_settings = copy.deepcopy ( self.additionalOptionsFrame.public_selected )
        more_settings [ "timeout_limit" ] = self.additionalOptionsFrame.public_timeout
        if more_settings [ "timeout" ] :
            # convert n to integer
            rgx_float = re.compile ( "^[0-9]+(\.[0-9]+)?$" )
            if not rgx_float.match(more_settings [ "timeout_limit" ]) :
                title = "Error: Additional Settings"
                message = "Games could not be started.\nError: Invalid timeout"
                wgt.ShowError( title, message, self.handler.root )
                return
            more_settings [ "timeout_limit" ] = float(more_settings [ "timeout_limit" ])
        more_settings [ "layout_chosen" ] = self.additionalOptionsFrame.public_layout

        if more_settings [ "timeout" ] and more_settings [ "timeout_limit" ] <= 0 :
            title = "Error: Additional Settings"
            message = "Games could not be started.\nError: Invalid timeout"
            wgt.ShowError( title, message, self.handler.root )
            return
        if len(games) <= 0 :
            title = "Error: Games"
            message = "Games could not be started.\nError: No Games in queue"
            wgt.ShowError( title, message, self.handler.root )
            return

        pcs = [ pc.copyDict() for pc in self.my_pause_conditions ]

        self.saveSettings()
        self.the_game.process_settings ( games, more_settings, pcs )
        self.the_game.gameStartRequested ()
        self.handler.showFrame ( 2 )

    ###
    # connected to the quickstart button
    # saves all of the current settings to the settings file
    # and passes them to the game
    def changeFrameQS ( self ) :
        if self.the_game is None: return
        
        orig_len = len ( self.my_games )
        self.gameAdded()
        # make sure that game was added, if so, start
        new_len =  len ( self.my_games ) 
        if orig_len + 1 == new_len :
            g = self.my_games.pop ( new_len - 1 )
            more_settings = copy.deepcopy ( self.additionalOptionsFrame.public_selected )
            more_settings [ "timeout_limit" ] = self.additionalOptionsFrame.public_timeout
            if more_settings [ "timeout" ] :
                # convert n to integer
                rgx_float = re.compile ( "^[0-9]+(\.[0-9]+)?$" )
                if not rgx_float.match(more_settings [ "timeout_limit" ]) :
                    title = "Error: Additional Settings"
                    message = "Games could not be started.\nError: Invalid timeout"
                    wgt.ShowError( title, message, self.handler.root )
                    return
                more_settings [ "timeout_limit" ] = float(more_settings [ "timeout_limit" ])
            more_settings [ "layout_chosen" ] = self.additionalOptionsFrame.public_layout

            if more_settings [ "timeout" ] and more_settings [ "timeout_limit" ] <= 0 :
                title = "Error: Additional Settings"
                message = "Games could not be started.\nError: Invalid timeout"
                wgt.ShowError( title, message, self.handler.root )
                return

            pcs = [ pc.copyDict() for pc in self.my_pause_conditions ]
            self.saveSettings()
            self.the_game.process_settings ( [ g ], more_settings, pcs )
            self.the_game.gameStartRequested ()
            self.handler.showFrame(2)

    ###
    # gameAdded
    # verify that a game is valid
    # add a game to the game queue
    #
    # Parameters:
    #   t -- game type
    #   n -- number of games
    #   p -- player list
    #   box_needed -- whether or not a blue box needs to be added to the game queue
    #                 false when quickstart is used
    def gameAdded ( self, t = None, n = None, p = None, box_needed = True ) :

        if t is None and n is None and p is None:
            t = self.addGameType.get() 
            n = self.addGameOptionsWindow.get_num_games ()
            p = self.addGameOptionsWindow.get_players ()
            box_needed = self.addGameOptionsWindow.is_box_needed ()
        elif t is None or n is None or p is None:
            return
        else :
            # check the players
            for i in p:
                if i not in PLAYERS and \
                    not (t == "Two Player" and i == "Human" and i == p[0] ):
                    print("bad game excluded:", t,n,p)
                    return

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
            title = "Error: Game Addition"
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

        # limit human games to 1
        if "human" in [l.lower() for l in p] and n != 1 :
            title = "Error: Game Addtion"
            message = "No game added.\nError: Human Games limited to 1, add separately for more."
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

        if self.dummyGameLabel is not None:
            self.dummyGameLabel.destroy()
        self.dummyGameLabel = tk.Label(self.gamesScrollFrame.interior, bg = "white", text = "\n\n")
        self.dummyGameLabel.grid(sticky=tk.W)

        self.gamesScrollFrame.set_scrollregion(vertical_buff=300)
        self.my_games.append ( new_game )
        self.parent.update_idletasks()

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

        self.my_pause_conditions = []

    def deletePC ( self, pauseConditionGUIDataObj ) :
        pauseConditionGUIDataObj.gui_box.destroy()
        self.my_pause_conditions.remove ( pauseConditionGUIDataObj )

    def pauseConditionAdded ( self, c = None, p = None ) :
        if c is None and p is None:
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
        elif c is None or p is None:
            return
        else:
            # check the players
            for i in p:
                if i not in PLAYERS and i != "Any AI":
                    print("bad pause condition excluded:", p, c)
                    print("uhoh", i)
                    return
            # check the pause conditions
            valid_keys = self.addPauseOptionsFrame.public_selected.keys()
            for i in list(c.keys()):
                if i not in valid_keys:
                    print("bad pause condition excluded:", p, c)
                    return
                # check for invalid selection
            
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
        
        new_pc = PauseConditionGUIData ( c, p, b )
        new_pc.gui_box.delButton.command = partial ( self.deletePC, new_pc )

        b.grid (sticky=tk.W)
        if self.dummyPCLabel is not None:
            self.dummyPCLabel.destroy()
        self.dummyPCLabel = tk.Label(self.pcScrollFrame.interior, bg = "white", text = "\n\n")
        self.dummyPCLabel.grid(sticky=tk.W)

        self.pcScrollFrame.set_scrollregion(vertical_buff=300)
        self.my_pause_conditions.append (new_pc)
        self.parent.update_idletasks()

    ###
    # saving game settings
    def saveSettings ( self ):
        data = {}
        # games
        data['games'] = []
        for g in self.my_games:
            game_data = {'type': g.game_type, 'num_games': g.num_games, 'players': copy.deepcopy(g.players)}
            data['games'].append(game_data)    

        # additional
        more_settings = copy.deepcopy ( self.additionalOptionsFrame.public_selected )
        more_settings [ "timeout_limit" ] = self.additionalOptionsFrame.public_timeout 
        more_settings [ "layout_chosen" ] = self.additionalOptionsFrame.public_layout
        data['additional_settings'] = more_settings

        # pause conditions
        data['pause_conditions'] = []
        for pc in self.my_pause_conditions:
            pc_data = {'players': pc.players, 'conditions': copy.deepcopy(pc.conditions)}
            data['pause_conditions'].append(pc_data)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)

    ###
    # laod the settings
    def loadSavedSettings ( self ) :
        data = None

        if not exists(SETTINGS_FILE):
            return

        self.startButton.disable()
        self.addGameOptionsWindow.startButton.disable()

        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)

        msg = "bad settings file"
        if data is None:
            print (msg)
            self.resetSettings()

        # chack that all of the keys are present
        try:
            if data.keys() != {'games','additional_settings','pause_conditions'}:
                print ( msg )
                self.resetSettings()
        except:
            print ( msg )
            self.resetSettings()

        # check that the games are in the correct format
        for g in data['games'] :
            t = g['type'] 
            if t not in GAME_TYPES or t == "QuickStart":
                print("bad game type", t)
                self.resetSettings()
                return
            n = str(g['num_games'])
            p = g['players']
            self.gameAdded ( t, n, p )
            
        # check that all of the additional settings are present
        # timeChanged, layoutChanged, clicked
        more = data['additional_settings']

        opts = { o['opt'] for o in self.additionalOptionsFrame.options }
        
        try:
            # checkboxes | fancy option inputs
            optsPlus = opts | {'layout_chosen', 'timeout_limit'}
            if more.keys() != optsPlus :
                print ( msg )
                self.resetSettings()
        except:
            print ( msg )
            self.resetSettings()

        for k in list(more.keys()) :
            if more[k] and k in opts :
                self.additionalOptionsFrame.selected[k].set(1)
                self.additionalOptionsFrame.clicked(k)
            elif more['timeout'] and k == 'timeout_limit' :
                self.additionalOptionsFrame.sv.set(more[k])
                self.additionalOptionsFrame.timeChanged(self.additionalOptionsFrame.sv)
                pass
            elif k == 'layout_chosen' :
                self.additionalOptionsFrame.layoutType.set(more[k])
                self.additionalOptionsFrame.layoutChanged(more[k])
                pass
        
        # check that the pause conditions are in the correct format???
        for pc in data['pause_conditions']:
            c = pc['conditions']
            p = pc['players']
            self.pauseConditionAdded ( c, p )


        self.startButton.enable()
        self.addGameOptionsWindow.startButton.enable()

    def resetSettings ( self ):
        data = {}
        # games
        data['games'] = []   

        # additional
        more_settings = copy.deepcopy ( self.additionalOptionsFrame.public_selected )
        for m in list(more_settings.keys()):
            more_settings[m] = False
        more_settings [ "timeout_limit" ] = "0" 
        more_settings [ "layout_chosen" ] = "Player Invoked"
        data['additional_settings'] = more_settings

        # pause conditions
        data['pause_conditions'] = []

        self.clearGameList()
        self.clearPCList()
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)

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
            maxlen = 30
            tempP0 = "P0: " + self.players[0]
            if len(tempP0) > maxlen:
                tempP0 = tempP0[:maxlen-3] + "..."
            tempP1 = "P1: " + self.players[1]
            if len(tempP1) > maxlen:
                tempP1 = tempP1[:maxlen-3] + "..."
            box.setTopText ( tempP0 + ",\n" + tempP1 )
            box.setTextLines ( self.getPCStr() )
        self.gui_box = box

    def getPCStr ( self ) :
        s = []
        for k in list ( self.conditions.keys() ) :
            s.append ( k + ": " + str(self.conditions[k]) )
        return s

    def copyDict ( self ) :
        return { 'conditions':copy.deepcopy(self.conditions), 'players':copy.deepcopy(self.players) }
        
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
        
        self.delButton = wgt.ColoredButton ( self, "x", wgt.LIGHT_BLUE, wgt.RED, flash = True )
        self.delButton.config ( font = BUTTON1_FONT, relief="flat", borderwidth=2 )
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

        self.canvas.config(height=120)

        self.selected = {}

        # accessible by other classes
        self.public_selected = {}
        self.public_layout = LAYOUT_OPTIONS[0]
        self.public_timeout = str(ERROR_CODE)

        # additional option keys and their descriptions to be printed on the menu
        # { 'opt' : "", 'descrip' : "" }
        self.options = [
                         { 'opt' : "swap"            , 'descrip' : "alternate player start" },
                         { 'opt' : "verbose"         , 'descrip' : "verbose (print W/L)" },
                         { 'opt' : "timeout"         , 'descrip' : "move timeout" },
                         { 'opt' : "autorestart"     , 'descrip' : "auto-restart" },
                         { 'opt' : "pause"           , 'descrip' : "pause on start" },
                         { 'opt' : "pauseIllegal"    , 'descrip' : "pause on illegal move" }
                       ]

        for i in range(len(self.options)) :
            o = self.options[i]
            self.addCheckOption ( o['opt'], o['descrip'], i )  

        r = [ o['opt'] for o in self.options ].index("timeout")
        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.timeChanged(sv))
        self.o_timeoutText = tk.Entry ( self.interior, textvar = sv )
        self.o_timeoutText.grid ( row = r, column = 1, sticky=tk.W )
        self.sv = sv

        r = len(self.options)
        self.layoutText = tk.Label ( self.interior, text = "Layout Option: " , bg="white")
        self.layoutText.grid ( row = r, sticky=tk.W )
        self.layoutType = tk.StringVar ( self.interior )
        self.layoutType.set(LAYOUT_OPTIONS[0])
        self.o_layout = tk.OptionMenu(self.interior, self.layoutType, *LAYOUT_OPTIONS, command = self.layoutChanged )
        self.o_layout.grid ( row = r, column = 1, sticky=tk.W )
            
    def clicked ( self, opt ) :
        self.public_selected[opt] = not self.public_selected[opt]

    def timeChanged ( self, sv  ) :
        self.public_timeout = sv.get()

    def layoutChanged ( self, option ) :
        self.public_layout = option

    def addCheckOption ( self, name, text, row ) :
        cb = tk.Checkbutton ( self.interior, text = text, command = partial(self.clicked, opt = name), bg = "white" )
        cb.grid ( row = row, sticky=tk.W )
        self.selected[name] = tk.BooleanVar()
        cb.config ( variable = self.selected[name] )
        self.public_selected[name] = False

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
                                     command = partial ( self.newSelection, value = "dummy", idx = item_name ), bg = "white" )
                b.grid ( row = loc, sticky=tk.W )

                var = tk.StringVar ( self.interior )
                self.values[item_name] = ttk.Combobox ( self.interior, values = list(range(self.tracking[o])), \
                                                        textvariable = var, state = "readonly" )
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
        #print("changed selection: %s, %s" %(str(value), str(idx)))
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
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p], bg = "white" )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )
            if p == "Select All" :
                b.config ( command = self.selectAllPlayers )

        self.gameStartFrame = tk.Frame ( self )
        
        self.numGamesFrame = tk.Frame ( self.gameStartFrame )
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill="both")#tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.startButton = wgt.ColoredButton ( self.gameStartFrame, "QuickStart", wgt.LIGHT_GREEN, "black", flash=True )
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
                self.update_idletasks()

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
        self.player2Type.set(PLAYERS[0])
        self.o_player2 = tk.OptionMenu(self.playersFrame, self.player2Type, *PLAYERS )
        self.o_player2.grid ( row = 1, column = 1, rowspan = 1, columnspan = 10, sticky = tk.W )

        self.filler = tk.Label ( self.playersFrame, text="\n"*10 )
        self.filler.grid ( row = 2, column = 0, rowspan = 1, columnspan = 1 )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white", flash=True )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill="both")#tk.X )
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

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white", flash=True  )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill="both")#tk.X )
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
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p], bg = "white" )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )
            if p == "Select All" :
                b.config ( command = self.selectAllPlayers )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "black", "white", flash=True )
        self.plusButton.config ( font=BUTTON1_FONT )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill="both")
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
                self.update_idletasks()
                
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

       


