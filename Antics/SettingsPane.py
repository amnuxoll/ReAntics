import tkinter as tk
from tkinter.font import Font
from functools import partial
from tkinter import ttk
import time
import RedoneWidgets as wgt
import re

PLAYERS = []
for i in range(10):
    PLAYERS.append ( "AI #" + str(i) )
PLAYER_COLS = 1 #2

GAME_TYPES = [ "QuickStart", "Two Player", "Single Player", "Round Robin", "Play All" ]
ANT_NAMES = [ "Workers", "Drones", "Soldiers", "Ranged Soldiers" ]

PLAYER_COLORS = [ "red", "blue" ] #"#ba8a97", "#5993c0" ] #
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

class GameSettingsFrame ( ) :
    
    def __init__(self, handler, parent = None):
        # initialize UI object

        # store event handler to close later
        self.parent = parent
        self.handler = handler

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
        self.gameQFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" ) #, bg = "#adadad" )
        self.gameQFrame.grid ( row = 1, column = 0, rowspan = 10, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.gameQLabel = tk.Label ( self.gameQFrame, text = "Game Queue", \
                                     fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.gameQLabel.pack ( side=tk.TOP, fill=tk.X )
        self.gameQClearButton = wgt.ColoredButton ( self.gameQFrame, "Clear All Games", wgt.RED, "black" )
        self.gameQClearButton.config ( font = BUTTON2_FONT )
        self.gameQClearButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )
        
        self.myGamesFrame = tk.Frame ( self.gameQFrame, bg="white",bd=5 )
        self.gamesScrollFrame = ScrollableFrame ( self.myGamesFrame )
        self.gamesScrollFrame.config( padx = 2, pady=2 )
        self.gamesScrollFrame.canvas.config(height=300)

        self.myGamesFrame.pack ( fill="both" )
        self.gamesScrollFrame.pack ( fill="both" )

        #### important ####
        self.my_games = [] # store all of the GameGUIData objects here
        ###################

        # pause condition log
        self.pauseConditionsFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" ) 
        self.pauseConditionsFrame.grid ( row = 12, column = 0, rowspan = 9, columnspan = 1, sticky = tk.W+tk.E+tk.N+tk.S )

        self.pauseConditionsLabel = tk.Label ( self.pauseConditionsFrame, text = "Pause Conditions", \
                                               fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.pauseConditionsLabel.pack ( side=tk.TOP, fill=tk.X )
        self.pauseConditionsButton = wgt.ColoredButton ( self.pauseConditionsFrame, "Clear All Pause Conditions", wgt.RED, "black" )
        self.pauseConditionsButton.config ( font = BUTTON2_FONT )
        self.pauseConditionsButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )

        self.myPCFrame = tk.Frame ( self.pauseConditionsFrame, bg="white",bd=5 )
        self.pcScrollFrame = ScrollableFrame ( self.myPCFrame )
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
        self.addGameOptionMenu.config ( font=FL_FONT, bg = "black" )
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

    #####
    # addGameChanged
    #
    # changes the add game options, to be used when the dropdown is changed
    #####
    def addGameChanged ( self, option ) :
        # self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
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
        self.handler.showFrame(2)

    def changeFrameQS ( self ) :
        print("quickstart pressed")
        self.handler.showFrame(2)
        
    def gameAdded ( self ) :
        print ( "a game has been added" )

        t = self.addGameType.get() #addGameOptionsWindow.get_game_type ()

        n = self.addGameOptionsWindow.get_num_games ()
        p = self.addGameOptionsWindow.get_players ()
        box_needed = self.addGameOptionsWindow.is_box_needed ()
        
        print ( t, n, p, box_needed )

        # convert n to integer

        rgx_int = re.compile ( "^[0-9]+$" )
        if not rgx_int.match :
            print ( "invalid game option A", n, p )
            return

        n = int ( n )
        if n < 1 or p is None or p == [] :
            print ( "invalid game option B", n, p )
            return

        b = None
        if box_needed :
            b = BlueBox ( self.gamesScrollFrame.interior )
            b.grid (sticky=tk.W)
            self.gamesScrollFrame.set_scrollregion() # update the scroll bar
        new_game = GameGUIData ( t, n, p, b )
        self.my_games.append ( new_game )
        self.parent.update()

        return



class GameGUIData () :
    def __init__ ( self, game_type = "", num_games = 0, players = [], box = None ) :
        self.game_type = game_type
        self.num_games = num_games
        self.players = players

        if box is not None :
            box.setTopText ( " ".join( [ str(game_type) +",", "Games :", str(num_games)] ) )
            box.setTextLines ( [ ", ".join ( players ) ] )
        self.gui_box = box

        

class BlueBox ( tk.Frame ) :
    def __init__ ( self, parent = None) :
        tk.Frame.__init__(self, parent)
        self.parent = parent

        bc = wgt.LIGHT_BLUE
        fnt = ( "Courier", 12 )

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
        

    def setTextLines ( self, textArray ) :
        maxl = 34
        padded = []
        for l in textArray :
            for i in range ( 0, len(l), maxl ) :
                cur = l [i: i+maxl ]
                cur = cur + " " * ( maxl - len (cur) )
                padded.append ( cur )

        self.myText.set ( "\n".join ( padded ) )

    def setTopText ( self, txt ) :
        self.myTopText.set ( txt )
            

#####
# ScrollableFrame
#
# creates a nested frame and canvas to be used as a scroll area
# add widgets to the frame <ScrollableFrame>.interior
#
# source: https://stackoverflow.com/questions/23483629/dynamically-adding-checkboxes-into-scrollable-frame
#####
class ScrollableFrame ( tk.Frame ) :
    def __init__ ( self, master, **kwargs ) :
        tk.Frame.__init__(self, master, **kwargs )

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar ( self, orient=tk.VERTICAL )
        self.vscrollbar.pack ( side='right', fill="y",  expand="false" )
        self.canvas = tk.Canvas ( self,
                                bg='white', bd=0,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set )
        self.canvas.pack ( side="left", fill="both", expand="true" )
        self.vscrollbar.config ( command=self.canvas.yview )

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame ( self.canvas, **kwargs, bg="white", padx = 2, pady = 2 )
        self.canvas.create_window ( 0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)

    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

######################################################################################
# INTERIOR FRAMES USED FOR QUEUES, ADDITIONAL SETTINGS, PAUSE CONDITIONS
# generally use a scrollable frame in some form
######################################################################################
class AdditionalSettingsOptionsFrame ( ScrollableFrame ) :
    def __init__ ( self, parent = None) :
        ScrollableFrame.__init__(self, parent)
        self.parent = parent

        self.canvas.config(height=100)

        self.selected = {}

        self.o_swap = tk.Checkbutton ( self.interior, text = "alternate player start", command = partial(self.clicked) )
        self.o_swap.grid ( row = 0, sticky=tk.W )
        self.selected["swap"] = tk.BooleanVar()
        self.o_swap.config ( variable = self.selected["swap"] )
        
        self.o_gameBoard = tk.Checkbutton ( self.interior, text = "display game board" )
        self.o_gameBoard.grid ( row = 1, sticky=tk.W )
        self.selected["game_board"] = tk.BooleanVar()
        self.o_gameBoard.config ( variable = self.selected["game_board"] )
        
        self.o_verbose = tk.Checkbutton ( self.interior, text = "verbose (print W/L)" )
        self.o_verbose.grid ( row = 2, sticky=tk.W )
        self.selected["verbose"] = tk.BooleanVar()
        self.o_verbose.config ( variable = self.selected["verbose"] )
        
        self.o_timeout = tk.Checkbutton ( self.interior, text = "move timeout" )
        self.o_timeout.grid ( row = 3, sticky=tk.W )
        self.selected["timeout"] = tk.BooleanVar()
        self.o_timeout.config ( variable = self.selected["timeout"] )

        self.o_timeoutText = tk.Entry ( self.interior )
        self.o_timeoutText.grid ( row = 3, column = 1, sticky=tk.W )

        self.layoutText = tk.Label ( self.interior, text = "Layout Option: " )
        self.layoutText.grid ( row = 4, sticky=tk.W )
        self.layoutType = tk.StringVar ( self.interior )
        self.layoutType.set(LAYOUT_OPTIONS[0])
        self.o_layout = tk.OptionMenu(self.interior, self.layoutType, *LAYOUT_OPTIONS, command = self.layoutChanged )
        self.o_layout.grid ( row = 4, column = 1, sticky=tk.W )

    def clicked ( self ) :
        print("swap")

    def layoutChanged ( self, option ) :
        print ( option )

class AddPauseOptionsFrame ( ScrollableFrame ) :
    def __init__ ( self, parent = None) :
        ScrollableFrame.__init__(self, parent)
        self.parent = parent

        ## !! change to constants later
        self.tracking = { 
            "Food" : 12,
            "Queen Health" : 5,
            "Anthill Health" : 5,
            "Num Ants" : 100
            }
        for a in ANT_NAMES :
            self.tracking ["Num " + a] = 100
            
        self.selected = {}
        self.values = {}

        self.track_options = list ( self.tracking.keys() )
        num_trackables = len(self.track_options)

        for i in range ( 2 ) :
            c = PLAYER_COLORS[i]
            c_light = PLAYER_COLORS_LIGHT[i]
            offset = i*(num_trackables+1)
            f = tk.Frame ( self.interior, bg = c_light, padx = 2, pady = 2 )
            pLabel = tk.Label ( f, text = "Player " + str(i) + ":" + " "*12, fg=c )
            pLabel.config ( font = BUTTON1_FONT )
            pLabel.grid ( row = offset, sticky=tk.W)
            
            # PLAYERS
            var = tk.StringVar ( self.interior )
##            self.values[item_name]
            bText= ttk.Combobox ( f, values = PLAYERS, textvariable = var, state = "readonly" )
##            bText = self.values[item_name]
            bText.grid ( row = offset, column = 1, sticky=tk.W )
            f.grid ( row = offset, column = 0, columnspan = 2, sticky=tk.W+tk.E )
##            bText.bind("<<ComboboxSelected>>", partial ( self.newSelection, idx = item_name ) )
            bText.current(0)
            

            for j in range ( num_trackables ) :
                o = self.track_options[j]
                item_name = "P" + str(i) + " " + o # P<1/2> item
                self.selected[item_name] = tk.BooleanVar()
                loc = j + offset + i + 1
                b = tk.Checkbutton ( self.interior, text = item_name, variable = self.selected[item_name] )
                b.grid ( row = loc, sticky=tk.W )

                var = tk.StringVar ( self.interior )
                self.values[item_name] = ttk.Combobox ( self.interior, values = list(range(self.tracking[o])), \
                                                        textvariable = var, state = "readonly" ) #, bg = c, fg = "white" )
                bText = self.values[item_name]
                bText.grid ( row = loc, column = 1, sticky=tk.W )
                bText.bind("<<ComboboxSelected>>", partial ( self.newSelection, idx = item_name ) )

                bText.current(0)


    def newSelection ( self, value, idx ) :
        print ( idx, self.values[idx].get(), self.selected[idx].get() )

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

        self.playersFrame = ScrollableFrame(self)
        self.playersFrame.config( padx = 2, pady=2 )
        self.playersFrame.canvas.config(height=200)

        self.players = PLAYERS + ["Select All"]
        playerCheckButtons = []

        self.selected = {}

        cols = PLAYER_COLS

        for i in range ( len(self.players) ) :
            p = self.players[i]
            self.selected[p] = tk.BooleanVar()
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p], \
                                 command = partial ( self.playerChecked, i ) )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )

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

    def playerChecked ( self, idx ) :
        print ( idx )

    def get_players ( self ) :
        return [ "Still need to parse QS" ]

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

        self.playersFrame = ScrollableFrame(self)
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
        p = []
        for x in self.players :
            if x != "Select All" and self.selected[x].get() :
                p.append ( x )
            
        return p

    def get_num_games ( self ) :
        return self.numGamesEntry.get()

    def is_box_needed ( self ) :
        return True

       


