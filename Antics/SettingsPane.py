import tkinter as tk
from tkinter.font import Font
from functools import partial
from tkinter import ttk
import time
import RedoneWidgets as wgt

PLAYERS = []
for i in range(10):
    PLAYERS.append ( "AI #" + str(i) )
PLAYER_COLS = 1 #2

GAME_TYPES = [ "QuickStart", "Two Player", "Single Player", "Round Robin", "Play All" ]
ANT_NAMES = [ "Workers", "Drones", "Soldiers", "Ranged Soldiers" ]

PLAYER_COLORS = [ "red", "blue" ] #"#ba8a97", "#5993c0" ] #

FRAME_BDR = 5

LAYOUT_OPTIONS = [ "Player Invoked", "Random Override" ]

# frame label settings
FL_COLOR = "black"
FL_TEXT_COLOR = "white"
FL_BD = 5
FL_STYLE = "ridge"
FL_FONT = ( "Herculanum", 15, "bold")
# Papyrus, Harrington, Herculanum, Desdemona, Wingdings

class GameSettingsFrame ( tk.Frame ) :
    
    def __init__(self, parent = None):
        # initialize UI object
        tk.Frame.__init__(self, parent)

        # store event handler to close later
        self.parent = parent

        # configure rows and columns of the main frame
        for r in range(23):
            self.parent.rowconfigure(r, weight=1)

        for c in range(23):
            self.parent.columnconfigure(c, weight=1)

        ##########################
        # left side -- queues and start

        # game queue
        self.gameQFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" ) #, bg = "#adadad" )
        self.gameQFrame.grid ( row = 1, column = 1, rowspan = 10, columnspan = 10, sticky = tk.W+tk.E+tk.N+tk.S )
        self.gameQLabel = tk.Label ( self.gameQFrame, text = "Game Queue", fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.gameQLabel.pack ( side=tk.TOP, fill=tk.X )
        self.gameQClearButton = wgt.ColoredButton ( self.gameQFrame, "Clear All Games", "red", "black" )
        self.gameQClearButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )
        
        self.myGamesFrame = tk.Frame ( self.gameQFrame, bg="white",bd=5 )
        self.gamesScrollFrame = ScrollableFrame ( self.myGamesFrame )
        self.gamesScrollFrame.config( padx = 2, pady=2 )
        self.gamesScrollFrame.canvas.config(height=300)

        self.myGamesFrame.pack ( fill="both" )
        self.gamesScrollFrame.pack ( fill="both" )

        self.temp = BlueBox ( self.gamesScrollFrame.interior )
        self.temp.config ( width = 500 )
        self.temp.grid ( row = 0 ) #grid ( row = 0, sticky = tk.E + tk.W )
        self.temp2 = BlueBox ( self.gamesScrollFrame.interior )
        self.temp2.config ( width = 500 )
        self.temp2.grid ( row = 1 ) #grid ( row = 0, sticky = tk.E + tk.W )

        # pause condition log
        self.pauseConditionsFrame = tk.Frame ( self.parent, highlightthickness = FRAME_BDR, highlightbackground="black" ) #, bg = "#adadad" )
        self.pauseConditionsFrame.grid ( row = 12, column = 1, rowspan = 9, columnspan = 10, sticky = tk.W+tk.E+tk.N+tk.S )
        self.pauseConditionsLabel = tk.Label ( self.pauseConditionsFrame, text = "Pause Conditions", fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.pauseConditionsLabel.pack ( side=tk.TOP, fill=tk.X )
        self.pauseConditionsButton = wgt.ColoredButton ( self.pauseConditionsFrame, "Clear All Pause Conditions", "red", "black" )
        self.pauseConditionsButton.pack ( side=tk.BOTTOM, fill=tk.X, padx=2,pady=2 )

        self.myPCFrame = tk.Frame ( self.pauseConditionsFrame, bg="white",bd=5 )
        self.pcScrollFrame = ScrollableFrame ( self.myPCFrame )
        self.pcScrollFrame.config( padx = 2, pady=2 )
        self.pcScrollFrame.canvas.config(height=200)

        self.myPCFrame.pack ( fill="both" )
        self.pcScrollFrame.pack ( fill="both" )

        # start button
        self.startButtonFrame = tk.Frame ( self.parent, bg="white" )
        self.startButtonFrame.grid ( row = 21, column = 1, rowspan = 1, columnspan = 10, sticky = tk.E+tk.W )

        self.startButton = wgt.ColoredButton ( self.startButtonFrame, "START", "green", "black"  )
        self.startButton.pack ( fill = tk.X )

        ##########################
        # right side -- add game, additional settings, add pause conditions
        
        # add a game
        self.addGameFrame = tk.Frame(self.parent, bg = "black", padx = FRAME_BDR, pady=FRAME_BDR )
        self.addGameFrame.grid(row = 1, column = 12, rowspan = 7, columnspan = 10, sticky = tk.W+tk.E+tk.N+tk.S)

        self.addGameType = tk.StringVar ( self.addGameFrame )
        self.addGameType.set(GAME_TYPES[0])
        self.addGameOptionMenu = tk.OptionMenu(self.addGameFrame, self.addGameType, *GAME_TYPES, command = self.addGameChanged )
        self.addGameOptionMenu.pack ( fill=tk.X, side=tk.TOP )

        self.addGameOptionsWindow = QuickStartFrame ( self.addGameFrame )
        
        # additional settings
        self.additionalSettingsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR ) 
        self.additionalSettingsFrame.grid(row = 9, column = 12, rowspan = 6, columnspan = 10, sticky = tk.W+tk.E+tk.N+tk.S)

        self.additionalSettingsLabel = tk.Label(self.additionalSettingsFrame, text = "Additional Settings", fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.additionalSettingsLabel.pack ( fill=tk.X )

        self.additionalOptionsFrame = AdditionalSettingsOptionsFrame ( self.additionalSettingsFrame )
        self.additionalOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        # add pause condition
        self.addPauseConditionsFrame = tk.Frame(self.parent, padx = FRAME_BDR, pady=FRAME_BDR )
        self.addPauseConditionsFrame.grid(row = 16, column = 12, rowspan = 6, columnspan = 10, sticky = tk.W+tk.E+tk.N+tk.S)

        self.addPauseConditionsLabel = tk.Label(self.addPauseConditionsFrame, text = "Add Pause Conditions", fg = FL_TEXT_COLOR, bg=FL_COLOR, borderwidth=FL_BD, relief=FL_STYLE, font=FL_FONT )
        self.addPauseConditionsLabel.pack ( fill=tk.X )

        self.addPauseOptionsFrame = AddPauseOptionsFrame ( self.addPauseConditionsFrame )
        self.addPauseOptionsFrame.pack (side=tk.BOTTOM, fill="both")

        self.addPauseConditionPlus = tk.Button ( self.addPauseConditionsFrame, text = "+" )
        self.addPauseConditionPlus.pack ( side=tk.LEFT)

        # editing the parent's attributes edits the base level window
        self.parent.title("Settings Frame")

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
        elif option == "Single Player" :
            self.addGameOptionsWindow = SinglePlayerFrame ( self.addGameFrame )
        elif option == "Two Player" :
            self.addGameOptionsWindow = TwoPlayerFrame ( self.addGameFrame )
        elif option == "Round Robin" :
            self.addGameOptionsWindow = RoundRobinFrame ( self.addGameFrame )
        elif option == "Play All" :
            self.addGameOptionsWindow = SinglePlayerFrame ( self.addGameFrame, "All Others" )
        self.addGameOptionsWindow.pack ( fill="both", side=tk.BOTTOM )


class BlueBox ( tk.Frame ) :
    def __init__ ( self, parent = None) :
        tk.Frame.__init__(self, parent)
        self.parent = parent

        bc = "cyan"

        self.config ( bg = "cyan", padx = 2, pady = 2 )
        self.config ( highlightbackground="white", highlightcolor="white", highlightthickness=2, bd= 0 )
        self.delButton = wgt.ColoredButton ( self, "x", "white", "red" )
        self.delButton.grid ( row = 0, column = 9 )

        self.textLines = []
        self.myText = tk.StringVar()
        self.setTextLines ( [ "game type", "num games", "player,"*50 ] )
        
        self.myTextFrame = tk.Frame ( self, bg = bc, padx = 2, pady = 2 )
        self.myTextLabel = tk.Label ( self.myTextFrame, textvar = self.myText, anchor=tk.W, justify=tk.LEFT, bg = bc )
        self.myTextLabel.pack()
        self.myTextFrame.grid ( row = 1, column = 0, columnspan = 8 )
        

    def setTextLines ( self, textArray ) :
        maxl = 40
        padded = []
        for l in textArray :
            for i in range ( 0, len(l), maxl ) :
                cur = l [i: i+maxl ]
                cur = cur + " " * ( maxl - len (cur) )
                padded.append ( cur )

        self.myText.set ( "\n".join ( padded ) )
        print ( "hi" )
        print ( self.myText.get() )
        print ( "hi" )
            

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
##                                height=100,
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
            offset = i*(num_trackables+1)
            pLabel = tk.Label ( self.interior, text = "Player " + str(i) + ": ", fg=c )
            pLabel.grid ( row = offset, sticky=tk.W)
            

            for j in range ( num_trackables ) :
                o = self.track_options[j]
                item_name = "P" + str(i) + " " + o # P<1/2> item
                self.selected[item_name] = tk.BooleanVar()
                loc = j + offset + i + 1
                b = tk.Checkbutton ( self.interior, text = item_name, variable = self.selected[item_name] )
                b.grid ( row = loc, sticky=tk.W )

                var = tk.StringVar ( self.interior )
                self.values[item_name] = ttk.Combobox ( self.interior, values = list(range(self.tracking[o])), textvariable = var, state = "readonly" ) #, bg = c, fg = "white" )
                bText = self.values[item_name]
                #bText = tk.Entry ( self.interior, bg = c, fg = "white" )
                bText.grid ( row = loc, column = 1, sticky=tk.W )
                bText.bind("<<ComboboxSelected>>", partial ( self.newSelection, idx = item_name ) )

                bText.current(0)

    def newSelection ( self, value, idx ) :
        print ( idx, self.values[idx].get(), self.selected[idx].get() )

##        o_max = self.tracking[idx]
##        try :
##            v = int ( self.values[idx].get() )
##            if v >= 0 and v < o_max:
##                return True
##            else:
##                return False
##        except : 
##            return False



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
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p], command = partial ( self.playerChecked, i ) )
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

        self.startButton = wgt.ColoredButton ( self.gameStartFrame, "QuickStart", "green", "black", self.qs  )
        self.startButton.pack ( fill=tk.X, side=tk.BOTTOM )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )

        self.gameStartFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )

    def playerChecked ( self, idx ) :
        print ( idx )

    def qs ( self ) :
        print ( "quickstart pressed" )

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

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "white", "black"  )
        self.plusButton.config ( font=("Courier", 18, "bold") )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )

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

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "white", "black"  )
        self.plusButton.config ( font=("Courier", 18, "bold") )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )
        self.playersFrame.pack ( fill="both" )

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
            b = tk.Checkbutton ( self.playersFrame.interior, text = p, variable = self.selected[p], command = partial ( self.playerChecked, i ) )
            playerCheckButtons.append ( b )
            b.grid ( row = int (i/cols), column = i%cols, sticky=tk.W )
        
        self.numGamesFrame = tk.Frame ( self ) 
        self.numGamesLabel = tk.Label ( self.numGamesFrame, text = "Games:    " )
        self.numGamesLabel.pack ( side=tk.LEFT ) 

        self.plusButton = wgt.ColoredButton ( self.numGamesFrame, "  +  ", "white", "black"  )
        self.plusButton.config ( font=("Courier", 18, "bold") )
        self.plusButton.pack ( side=tk.RIGHT )
        
        self.numGamesEntry = tk.Entry ( self.numGamesFrame, text="1" )
        self.numGamesEntry.pack ( fill=tk.X )
        self.numGamesEntry.delete ( 0,tk.END )
        self.numGamesEntry.insert ( 0, "1" )

        self.numGamesFrame.pack ( fill=tk.X,side=tk.BOTTOM )

        self.playersFrame.pack ( fill="both" )

    def playerChecked ( self, idx ) :
        print ( idx )


# main code

# setup GUI object and initialize GUI library
app = GameSettingsFrame(tk.Tk())
app.mainloop()
       


