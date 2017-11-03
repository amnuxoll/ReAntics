import os, re, sys, math, multiprocessing, time, random
import HumanPlayer
from Construction import *
from Constants import *
from GameState import *
from Inventory import *
from Building import *
from Location import *
from Ant import *
from Move import *
from GUIHandler import *
import threading
import time
import importlib
import argparse

from functools import partial
import copy


##
# Game
# Description: Keeps track of game logic and manages the play loop.
##
class Game(object):
    ##
    # __init__
    # Description: Initializes the game's attributes and UI.
    #
    ##
    def __init__(self, testing=False):
        ### new game queue, this is a queue of function calls ( does not sub for the tournament vars )
        self.last_time = time.time()
        self.game_calls  = []
        
        # Initialize the game variables
        self.players = []
        self.initGame()
        # Initializes tournament mode variables
        self.playerScores = []  # [[author,wins,losses], ...]
        self.gamesToPlay = []  # ((p1.id, p2.id), numGames)
        self.numGames = None
        # debug mode allows initial setup in human vs. AI to be automated
        self.randomSetup = False  # overrides human setup only
        self.verbose = False
        # additional settings
        self.playerSwap      = False   # additonal settings
        self.playersReversed = False   # whether the players are currently swapped
        self.timeoutOn    = False # !!! TODO - not presently implemented
        self.timeoutLimit = -1    # !!! TODO - not presently implemented
        # !!! TODO - decide on game board or stats pane displaying first, fix that additional setting accordingly

        # setup GUI
        # this has to be done in the main thread because Tkinter is dumb
        if testing:
            return

        # Initializes the UI variables
        self.UI = GUIHandler(self)
        self.gameThread = None

        # TODO: figure out how to make this work properly
        # wait for GUI to set up
        self.loadAIs(False)
        done = False
        while not done:
            time.sleep(.1)
            if self.UI is not None:
                done = self.UI.setup
        self.UI.showFrame(0)

        # fixing the players on the settings menu
        self.UI.settingsHandler.changePlayers ( [ ai[0].author for ai in self.players ] )
        self.UI.settingsHandler.createFrames ( )
        self.UI.settingsHandler.giveGame ( self )
        self.UI.gameHandler.createFrames()
        self.UI.gameHandler.giveGame(self)

        print("Starting")
        self.gameThread = threading.Thread(target=self.start, daemon=True)
        self.gameThread.start()
        print("game thread started")

        self.UI.root.mainloop()

    def tick(self,fps):
        interval = 60 / fps
        current_time = time.time()

        delta = current_time - self.last_time

        if delta < interval :
            time.sleep(interval - delta)
        self.last_time = time.time()

    def gameStartRequested ( self ) :
        if len ( self.game_calls ) > 0 :
            g = self.game_calls.pop(0)
            g ()
            print("started game")

    def closeGUI(self):
        # Tried to make it close nicely, failed
        # instead we brute force
        # TODO: make this work better

        # if self.UI is not None:
        #     self.UI.closed = True
        #     self.UI.root.after(50, self.UI.root.destroy())
        #
        # if self.GUIthread is not None:
        #     self.GUIthread.join()

        # theoretically sys.exit() should work here. I'm not sure why it doesn't.
        os._exit(0)


    ##
    # startHumanVsAI
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for a human player and an AI
    #
    # Parameters: givenPlayer - A string that specifies the non-human Agent name
    #
    ##
    def startHumanVsAI(self, givenPlayer):
        # set the number of games to be played
        self.numGames = 1
        # setup instance variable necessary for human gameplay, e.g. pre-setup
        self.humanPathCallback()
        # find the given, non-human, agent in the player list and get its index
        aiName = givenPlayer
        index = -1
        for player in self.players:
            if aiName == player[0].author:
                index = self.players.index(player)
                break
        if (index < 0):
            print("ERROR:  AI '" + aiName + "' not found.")
            print("Please specify one of the following:")
            for player in self.players[1:]:
                print('    "' + player[0].author + '"')
            return

        # select the specified AI and click "Submit"
        self.checkBoxClickedCallback(index)
        self.submitClickedCallback()
        self.startGameCallback()

    ##
    # startAIvsAI
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for an AI vs an AI
    #
    # Parameters: numGames - An int which specifies the number of games for the two given players to play
    #             player1 - A string that specifies a non-human Agent name
    #             player2 - Another string that specifies a non-human Agent name
    #
    ##
    def startAIvsAI(self, numGames, player1, player2):
        # initiate variables as to a tournament setup -- pre-setup
        self.tourneyPathCallback()
        # set the number of games to be played as an instance variable
        self.numGames = numGames

        # AI names should be specified as next command line args
        # need exactly two AI names
        aiNameIndices = []
        index = -1
        for player in self.players:
            if player1 == player[0].author or player2 == player[0].author:
                # append the name of the indices for the tournament
                aiNameIndices.append(self.players.index(player))

        if (len(aiNameIndices) < 2):
            print("ERROR:  AI '" + player1 + "' OR AI '" + player2 + "' not found.")
            print("Please specify one of the following:")
            for player in self.players:
                print('    "' + player[0].author + '"')
            return

        # now that we have the AI's check the check boxes
        for index in aiNameIndices:
            self.checkBoxClickedCallback(index)

        # post-setup AI choice instance variables that need to be set
        self.submitClickedCallback()
        self.startGameCallback()
        pass

    ##
    # startRR
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for Round Robin
    #
    # Parameters: numGames - An int which specifies the number of games for the each player pair to play
    #             givenPlayers - A list of strings defining the Agents that should be in round robin game play
    #
    ##
    def startRR(self, numGames, givenPlayers):
        # initiate variables as to a tournament setup -- pre-setup
        self.tourneyPathCallback()
        # set the number of games to be played as an instance variable
        self.numGames = numGames

        # AI names should be specified as next command line args
        # need exactly two AI names
        aiNameIndices = []

        for givenPlayer in givenPlayers:
            index = -1
            for player in self.players:
                if givenPlayer == player[0].author:
                    # append the name of the indices for the tournament
                    aiNameIndices.append(self.players.index(player))
                    index = 1
            if index == -1:
                print("ERROR:  AI '" + givenPlayer + "' not found.")
                print("Please specify one of the following:")
                for thisPlayer in self.players[1:]:
                    print('    "' + thisPlayer[0].author + '"')
                return

        # now that we have the AI's check the check boxes
        for index in aiNameIndices:
            self.checkBoxClickedCallback(index)

        # post-setup AI choice instance variables that need to be set
        self.submitClickedCallback()
        self.startGameCallback()
        pass

    ##
    # startRRall
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for Round Robin with all possible Agents
    #
    # Parameters: numGames - An int which specifies the number of games for the each player pair to play
    #
    ##
    def startRRall(self, numGames):
        # initiate variables as to a tournament setup -- pre-setup
        self.tourneyPathCallback()
        # set the number of games to be played as an instance variable
        self.numGames = numGames

        # AI names should be specified as next command line args
        # need exactly two AI names
        aiNameIndices = []
        for player in self.players:
            aiNameIndices.append(self.players.index(player))

        # now that we have the AI's check the check boxes
        for index in aiNameIndices:
            self.checkBoxClickedCallback(index)

        # post-setup AI choice instance variables that need to be set
        self.submitClickedCallback()
        self.startGameCallback()
        pass

    ##
    # startAllOther
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for a Specific Agent to play all other Agents
    #
    # Parameters: numGames - An int which specifies the number of games for the each player pair to play
    #             playerOne - A string that specifies the non-human Agent name
    #
    ##
    def startAllOther(self, numGames, playerOne):
        # Attempt to load the AI files
        self.loadAIs(False)

        # create a game queue of AI vs AI games and block the queue until the current game has finished
        self.game_calls  = []
        for player in self.players:
            if player[0].author != playerOne:
                self.game_calls.append ( partial ( self.startAIvsAI, numGames, playerOne, player[0].author ) )
        if len (self.game_calls) > 0 :
            fx_start = self.game_calls.pop(0)
            fx_start()
        pass

    ##
    # startSelf
    #
    # Description: Set up the Game object instance variables so that a game can
    #              be started with the specific information for an Agent to play itself
    #
    # Parameters: numGames - An int which specifies the number of games for the each player pair to play
    #             playerOne - A string that specifies the non-human Agent name
    #
    ##
    def startSelf(self, numGames, playerOne):
        # initiate variables as to a tournament setup -- pre-setup
        self.tourneyPathCallback()
        # create a copy of the Agent you want to play itself
        self.createAICopy(playerOne)
        # set the number of games to be played as an instance variable
        self.numGames = numGames
        # set playerTwo to the predetermined copy name
        playerTwo = playerOne + "@@"

        # AI names should be specified as next command line args
        # need exactly two AI names
        aiNameIndices = []
        for player in self.players:
            if playerOne == player[0].author or playerTwo == player[0].author:
                # append the name of the indices for the tournament
                aiNameIndices.append(self.players.index(player))

        if (len(aiNameIndices) < 2):
            print("ERROR:  AI '" + playerOne + "' not found.")
            print("Please specify one of the following:")
            for player in self.players:
                print('    "' + player[0].author + '"')
            return

        # now that we have the AI's check the check boxes
        for index in aiNameIndices:
            self.checkBoxClickedCallback(index)

        # post-setup AI choice instance variables that need to be set
        self.submitClickedCallback()
        self.startGameCallback()
        pass

    ##
    # processCommandLine
    #
    # Description: Parses the command line arguments and configures the game appropriately.
    #
    # Formats:
    #           Mutually Exclusive Game Types:
    #           --RR    >> Round robin of given Agents
    #           --RRall >> Round robin between all Agents
    #           --self  >> Allow the Agent to play itself
    #           --all   >> Play all other AI's
    #           --2p    >> Two player game
    #
    #           Meta-Variables:
    #           -n >> Number of Games
    #           -p >> List of Agents (can be "human" if it applies)
    #
    #           Useful Command Flags:
    #           -v >> Verbose print out game records to console
    #           -h >> Print the command option help page
    #
    #           Example:
    #           python Game.py --2P -p <AIName1> <AIName2> -n <number of games>
    #
    ##
    def processCommandLine(self):
        parser = argparse.ArgumentParser(description='Lets play Antics!', add_help=True)
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-RR', '--RR', action='store_true', dest='RR', default=False,
                           help='Round robin of given AI\'s(minimum of 3 AI’s required)')
        group.add_argument('-RRall', '--RRall', action='store_true', dest='RRall', default=False,
                           help='Round robin between all AI\'s')
        group.add_argument('-self', '--self', action='store_true', dest='self', default=False,
                           help='Allow the AI to play itself')
        group.add_argument('-all', '--all', action='store_true', dest='all', default=False,
                           help='Play all other AI\'s total games = NUMGAMES * (total number of AI\'s)')
        group.add_argument('-2p', '--2p', action='store_true', dest='twoP', default=False,
                           help='Two player game')
        parser.add_argument('-randomLayout', action='store_true', dest='randomLayout', default=False,
                            help='Override layout calls to human/agent with a random layout')
        parser.add_argument('-v', action='store_true', default=False, dest='verbose',
                            help='Verbose - print out game records to console'
                                 '(Prints the current game record at the end of each game to the console)')
        parser.add_argument('-n', '--NumGames', metavar='NUMGAMES', type=int, dest='numgames', default=1,
                            help='number of games ( per agent pair for round robin )')
        parser.add_argument('-p', '--Players', metavar='PLAYER', type=str, nargs='*', dest='players',
                            help='player, can either be the name of an agent or "human"'
                                 'which will be reserved for human')

        args = parser.parse_args()
        numCheck = re.compile("[0-9]*[1-9][0-9]*")

        # Error and bounds checking for command line parameters
        if not numCheck.match(str(args.numgames)):
            parser.error('NumGames must be a positive number')
        if args.verbose:
            self.verbose = True
        if (args.RR or args.RRall or args.self or args.all or args.twoP) and args.numgames is None:
            parser.error('Flags not valid without number of games (-n)')
        if args.twoP:
            if len(args.players) != 2:
                parser.error('Only two agents allowed')
            # TODO: This is to change with stretch goals
            if "human" == args.players[0].lower() and "human" == args.players[1].lower():
                parser.error('Only one player may be human')
            if "human" == args.players[0].lower():
                if args.numgames != 1:
                    parser.error('Human Vs Player can only have 1 game. (-n 1)')
                self.startHumanVsAI(args.players[1])
                if args.randomLayout:
                    self.randomSetup = True
            elif "human" == args.players[1].lower():
                if args.numgames != 1:
                    parser.error('Human Vs Player can only have 1 game. (-n 1)')
                self.startHumanVsAI(args.players[0])
                if args.randomLayout:
                    self.randomSetup = True
            else:
                self.startAIvsAI(args.numgames, args.players[0], args.players[1])
        elif args.RR:
            if 'human' in args.players:
                parser.error('Human not allowed in round robin')
            if len(args.players) <= 2:
                parser.error('3 or more players needed for round robin')
            self.startRR(args.numgames, args.players)
        elif args.RRall:
            if args.players is not None:
                parser.error('Do not specify players with (-p), (--RRall) is for all players')
            self.startRRall(args.numgames)
        elif args.all:
            if 'human' in args.players:
                parser.error('Human not allowed in play all others')
            if len(args.players) != 1:
                parser.error('Only specify the Player you want to play all others')
            self.startAllOther(args.numgames, args.players[0])
        elif args.self:
            if 'human' in args.players:
                parser.error('Human not allowed in play all others')
            if len(args.players) != 1:
                parser.error('Only specify the Player you want to play its self')
            self.startSelf(args.numgames, args.players[0])

    ##
    # process_settings
    #
    # Description: process the current settings and assign values within the game class accordingly
    #              set the game_calls queue
    #
    # Parameters: games - GameGUIData Objects list
    #             additional - dictionary of additional settings
    #
    ##
    def process_settings ( self, games, additional ) :
        # set the additional settings
        self.verbose = additional [ 'verbose' ]
        self.playerSwap = additional [ 'swap' ]
        self.playersReversed = False
        self.randomSetup = additional [ 'layout_chosen' ] == "Random Override"
        self.timeoutOn = additional [ 'timeout' ]
        if self.timeoutOn :
            self.timeoutLimit = additional [ 'timeout_limit' ]
        
        # set the game queue
        self.game_calls = []
        for g in games :
            t = g.game_type
            fx = None
            if t == "Two Player":
                fx = self.startAIvsAI
                self.game_calls.append( partial ( fx, g.num_games, g.players[0], g.players[1] ) )
            elif t == "Single Player":
                fx = self.startSelf
                self.game_calls.append( partial ( fx, g.num_games, g.players[0] ) )
            elif t == "Round Robin":
                fx = self.startRR
                self.game_calls.append( partial ( fx, g.num_games, g.players ) )
            elif t == "Play All":
                fx = self.startAllOther
                for player in self.players:
                    if player[0].author != g.players[0]:
                        self.game_calls.append ( partial ( self.startAIvsAI, g.num_games, g.players[0], player[0].author ) )
                        
    ##
    # start
    # Description: Runs the main game loop, requesting turns for each player.
    #       This loop runs until the user exits the game.
    #
    ##
    def start(self):
        self.processCommandLine()
        #self.state.phase = MENU_PHASE
        
        while True:
            self.tick(80)
            # Determine current chosen game mode. Enter different execution paths
            # based on the mode, which must be chosen by clicking a button.

            # player has clicked start game so enter game loop
            #if self.state.phase != MENU_PHASE:
            # clear notifications
            # self.ui.notify("")

            self.runGame()
            self.resolveEndGame()
            #else:
                #self.process_settings()

    ##
    # runGame
    #
    # Description: the main game loop
    #
    # ToDo:  This method is way too large and needs to be broken up
    #
    ##
    def runGame(self):
        # build a list of things to place for player 1 in setup phase 1
        # 1 anthill/queen, 1 tunnel/worker, 9 obstacles
        constrsToPlace = []
        constrsToPlace += [Building(None, ANTHILL, PLAYER_ONE)]
        constrsToPlace += [Building(None, TUNNEL, PLAYER_ONE)]
        constrsToPlace += [Construction(None, GRASS) for i in range(0, 9)]

        while not self.gameOver:
            if self.state.phase == MENU_PHASE:
                # if we are in menu phase at this point, a reset was requested so break
                break
            else:
                # create a copy of the state to share with the player
                theState = self.state.clone()

                # I think this is where it should go
                if self.UI is not None:
                    self.UI.showState(theState)

                # if the player is player two, flip the board
                if theState.whoseTurn == PLAYER_TWO:
                    theState.flipBoard()

            if self.state.phase == SETUP_PHASE_1 or self.state.phase == SETUP_PHASE_2:
                currentPlayer = self.currentPlayers[self.state.whoseTurn]
                # if type(currentPlayer) is HumanPlayer.HumanPlayer:
                #     if constrsToPlace[0].type == ANTHILL:
                #         self.ui.notify("Place anthill on your side.")
                #     elif constrsToPlace[0].type == TUNNEL:
                #         self.ui.notify("Place tunnel on your side.")
                #     elif constrsToPlace[0].type == GRASS:
                #         self.ui.notify("Place grass on your side.")
                #     elif constrsToPlace[0].type == FOOD:
                #         self.ui.notify("Place food on enemy's side.")
                # clear targets list as anything on list been processed on last loop
                targets = []

                # do auto-random setup for human player if required
                if (self.randomSetup) and (type(currentPlayer) is HumanPlayer.HumanPlayer):
                    if (constrsToPlace[0].type != FOOD):
                        coord = (random.randint(0, 9), random.randint(0, 3))
                        if (self.state.board[coord[0]][coord[1]].constr == None):
                            targets.append(coord)
                    elif (constrsToPlace[0].type == FOOD):
                        coord = (random.randint(0, 9), random.randint(6, 9))
                        if (self.state.board[coord[0]][coord[1]].constr == None):
                            targets.append(coord)

                # hide the 1st player's set anthill and grass placement from the 2nd player
                if theState.whoseTurn == PLAYER_TWO and self.state.phase == SETUP_PHASE_1:
                    theState.clearConstrs()

                # get the placement from the player
                targets += currentPlayer.getPlacement(theState)
                # only want to place as many targets as constructions to place
                if len(targets) > len(constrsToPlace):
                    targets = targets[:len(constrsToPlace)]

                validPlace = self.isValidPlacement(constrsToPlace, targets)
                if validPlace:
                    for target in targets:
                        # translate coords to match player
                        target = self.state.coordLookup(target, self.state.whoseTurn)
                        # get construction to place
                        constr = constrsToPlace.pop(0)
                        # give constr its coords
                        constr.coords = target
                        # put constr on board
                        self.state.board[target[0]][target[1]].constr = constr
                        if constr.type == ANTHILL or constr.type == TUNNEL:
                            # update the inventory
                            self.state.inventories[self.state.whoseTurn].constrs.append(constr)
                        else:  # grass and food
                            self.state.inventories[NEUTRAL].constrs.append(constr)

                    # if AI mode, pause to observe move until next or continue is clicked
                    self.pauseForAIMode()
                    if self.state.phase == MENU_PHASE:
                        # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                        break

                    if not constrsToPlace:
                        constrsToPlace = []
                        if self.state.phase == SETUP_PHASE_1:
                            if self.state.whoseTurn == PLAYER_ONE:
                                constrsToPlace += [Building(None, ANTHILL, PLAYER_TWO)]
                                constrsToPlace += [Building(None, TUNNEL, PLAYER_TWO)]
                                constrsToPlace += [Construction(None, GRASS) for i in range(0, 9)]
                            elif self.state.whoseTurn == PLAYER_TWO:
                                constrsToPlace += [Construction(None, FOOD) for i in range(0, 2)]
                                self.state.phase = SETUP_PHASE_2
                        elif self.state.phase == SETUP_PHASE_2:
                            if self.state.whoseTurn == PLAYER_ONE:
                                constrsToPlace += [Construction(None, FOOD) for i in range(0, 2)]
                            elif self.state.whoseTurn == PLAYER_TWO:
                                # if we're finished placing, add in queens and move to play phase
                                p1inventory = self.state.inventories[PLAYER_ONE]
                                p2inventory = self.state.inventories[PLAYER_TWO]
                                # get anthill coords
                                p1AnthillCoords = p1inventory.constrs[0].coords
                                p2AnthillCoords = p2inventory.constrs[0].coords
                                # get tunnel coords
                                p1TunnelCoords = p1inventory.constrs[1].coords
                                p2TunnelCoords = p2inventory.constrs[1].coords
                                # create queen and worker ants
                                p1Queen = Ant(p1AnthillCoords, QUEEN, PLAYER_ONE)
                                p2Queen = Ant(p2AnthillCoords, QUEEN, PLAYER_TWO)
                                p1Worker = Ant(p1TunnelCoords, WORKER, PLAYER_ONE)
                                p2Worker = Ant(p2TunnelCoords, WORKER, PLAYER_TWO)
                                # put ants on board
                                self.state.board[p1Queen.coords[0]][p1Queen.coords[1]].ant = p1Queen
                                self.state.board[p2Queen.coords[0]][p2Queen.coords[1]].ant = p2Queen
                                self.state.board[p1Worker.coords[0]][p1Worker.coords[1]].ant = p1Worker
                                self.state.board[p2Worker.coords[0]][p2Worker.coords[1]].ant = p2Worker
                                # add the queens to the inventories
                                p1inventory.ants.append(p1Queen)
                                p2inventory.ants.append(p2Queen)
                                p1inventory.ants.append(p1Worker)
                                p2inventory.ants.append(p2Worker)
                                # give the players the initial food
                                p1inventory.foodCount = 1
                                p2inventory.foodCount = 1
                                # change to play phase
                                # self.ui.notify("")
                                self.state.phase = PLAY_PHASE

                        # change player turn in state
                        self.state.whoseTurn = (self.state.whoseTurn + 1) % 2

                else:
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        # cause current player to lose game because AIs aren't allowed to make mistakes.
                        self.error(INVALID_PLACEMENT, targets)
                        break
                    elif validPlace != None:
                        # self.ui.notify("Invalid placement.")
                        self.errorNotify = True

            elif self.state.phase == PLAY_PHASE:
                currentPlayer = self.currentPlayers[self.state.whoseTurn]

                # display instructions for human player
                if type(currentPlayer) is HumanPlayer.HumanPlayer:
                    # An error message is showing

                    pass
                    # if not self.errorNotify:
                    #     #nothing selected yet
                    #     if not currentPlayer.coordList:
                    #         self.ui.notify("Select an ant or building.")
                    #     #ant selected
                    #     elif not self.state.board[currentPlayer.coordList[0][0]][currentPlayer.coordList[0][1]].ant == None:
                    #         self.ui.notify("Select move for ant.")
                    #     #Anthill selected
                    #     elif not self.state.board[currentPlayer.coordList[0][0]][currentPlayer.coordList[0][1]].constr == None:
                    #         self.ui.notify("Select an ant type to build.")
                    #     else:
                    #         self.ui.notify("")

                # get the move from the current player in a separate
                # process so that we can time it out
                move = currentPlayer.getMove(theState)

                if move != None and move.coordList != None:
                    for i in range(0, len(move.coordList)):
                        # translate coords of move to match player
                        move.coordList[i] = self.state.coordLookup(move.coordList[i], self.state.whoseTurn)

                # make sure it's a valid move
                validMove = self.isValidMove(move)

                # complete the move if valid
                if validMove:
                    # check move type
                    if move.moveType == MOVE_ANT:
                        startCoord = move.coordList[0]
                        endCoord = move.coordList[-1]

                        # take ant from start coord
                        antToMove = self.state.board[startCoord[0]][startCoord[1]].ant
                        # change ant's coords and hasMoved status
                        antToMove.coords = (endCoord[0], endCoord[1])
                        antToMove.hasMoved = True
                        # remove ant from location
                        self.state.board[startCoord[0]][startCoord[1]].ant = None
                        # put ant at last loc in coordList
                        self.state.board[endCoord[0]][endCoord[1]].ant = antToMove

                        # clear all highlights after move happens
                        # self.ui.coordList = []

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break

                        # check and take action for attack (workers can not attack)
                        if (antToMove.type != WORKER):
                            self.resolveAttack(antToMove, currentPlayer)

                        # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                        if self.state.phase == MENU_PHASE:
                            break

                            # clear all highlights after attack happens
                            # self.ui.coordList = []
                            # self.ui.attackList = []

                    elif move.moveType == BUILD:
                        coord = move.coordList[0]
                        currentPlayerInv = self.state.inventories[self.state.whoseTurn]

                        # subtract the cost of the item from the player's food count
                        if move.buildType == TUNNEL:
                            currentPlayerInv.foodCount -= CONSTR_STATS[move.buildType][BUILD_COST]

                            tunnel = Building(coord, TUNNEL, self.state.whoseTurn)
                            self.state.board[coord[0]][coord[1]].constr = tunnel
                        else:
                            currentPlayerInv.foodCount -= UNIT_STATS[move.buildType][COST]

                            ant = Ant(coord, move.buildType, self.state.whoseTurn)
                            ant.hasMoved = True
                            self.state.board[coord[0]][coord[1]].ant = ant
                            self.state.inventories[self.state.whoseTurn].ants.append(ant)

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break

                            # clear all highlights after build
                            # self.ui.coordList = []

                    elif move.moveType == END:
                        # take care of end of turn business for ants and contructions
                        for ant in self.state.inventories[self.state.whoseTurn].ants:
                            constrUnderAnt = self.state.board[ant.coords[0]][ant.coords[1]].constr
                            if constrUnderAnt != None:
                                # if constr is enemy's and ant hasnt moved, affect capture health of buildings
                                if type(
                                        constrUnderAnt) is Building and not ant.hasMoved and not constrUnderAnt.player == self.state.whoseTurn:
                                    constrUnderAnt.captureHealth -= 1
                                    if constrUnderAnt.captureHealth == 0 and constrUnderAnt.type != ANTHILL:
                                        constrUnderAnt.player = self.state.whoseTurn
                                        constrUnderAnt.captureHealth = CONSTR_STATS[constrUnderAnt.type][CAP_HEALTH]
                                # have all worker ants on food sources gather food
                                elif constrUnderAnt.type == FOOD and ant.type == WORKER:
                                    ant.carrying = True
                                # deposit carried food (only workers carry)
                                elif (
                                        constrUnderAnt.type == ANTHILL or constrUnderAnt.type == TUNNEL) and ant.carrying == True:
                                    self.state.inventories[self.state.whoseTurn].foodCount += 1
                                    ant.carrying = False

                            # reset hasMoved on all ants of player
                            ant.hasMoved = False

                        # clear any currently highlighted squares
                        # self.ui.coordList = []

                        # switch whose turn it is
                        self.state.whoseTurn = (self.state.whoseTurn + 1) % 2

                        # notify player which AI is acting
                        nextPlayerName = self.players[self.state.whoseTurn][0].author
                        # self.ui.notify(nextPlayerName + "'s turn.")

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break
                else:
                    # human can give None move, AI can't
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        self.error(INVALID_MOVE, move)
                        break
                    elif validMove != None:
                        # if validMove is False and not None, clear move
                        currentPlayer.coordList = []
                        # self.ui.coordList = []

            # determine if if someone is a winner.
            if self.hasWon(PLAYER_ONE):
                self.setWinner(PLAYER_ONE)

            elif self.hasWon(PLAYER_TWO):
                self.setWinner(PLAYER_TWO)

                # redraw the board periodically and check for user input
                # self.ui.drawBoard(self.state, self.mode)

                # end game loop

    def resolveEndGame(self):
        if self.state.phase != MENU_PHASE:
            # check mode for appropriate response to game over
            if self.UI is not None:
                self.UI.showState(self.state)

            if self.mode == HUMAN_MODE:
                self.state.phase = MENU_PHASE

                # notify the user of the winner
                # if self.winner == PLAYER_ONE:
                #     self.ui.notify("You have won the game!")
                # else:
                #     self.ui.notify("The AI has won the game!")

                self.errorNotify = True

            if self.mode == AI_MODE:
                self.state.phase = MENU_PHASE

                # notify the user of the winner
                winnerName = self.players[self.winner][0].author
                # self.ui.notify(winnerName + " has won the game!")
                self.errorNotify = True

            elif self.mode == TOURNAMENT_MODE:
                # adjust the count of games to play for the current pair
                currentPairing = (self.currentPlayers[PLAYER_ONE].playerId, self.currentPlayers[PLAYER_TWO].playerId)

                # give the new scores to the UI
                # self.ui.tournamentScores = self.playerScores

                # adjust the wins and losses of players
                self.playerScores[self.winner][1] += 1
                self.playerScores[self.loser][2] += 1

                # if CommandLine Mode print the values to the console
                if self.verbose:
                    self.printTournament()

                # reset the game
                self.initGame()

                for i in range(0, len(self.gamesToPlay)):
                    # if we found the current pairing
                    if self.gamesToPlay[i][0] == currentPairing:
                        # mark off another game for the pairing
                        self.gamesToPlay[i][1] -= 1

                        # if the pairing has no more games, then remove it
                        if self.gamesToPlay[i][1] == 0:
                            self.gamesToPlay.remove(self.gamesToPlay[i])
                        break

                if len(self.gamesToPlay) == 0:
                    # if no more games to play, reset tournament stuff
                    if not self.verbose:
                        self.printTournament()
                    self.numGames = 0
                    self.playerScores = []
                    self.mode = TOURNAMENT_MODE

                    ### pop the next game off the gameQ
                    if len (self.game_calls) > 0 :
                        fx_start = self.game_calls.pop(0)
                        fx_start()

                    # seems out of place, did I add this?
                    # TODO: implement this nicely
                    # self.closeGUI()
                    # sys.exit(0)
                else:
                    # setup game to run again
                    self.mode = TOURNAMENT_MODE
                    self.state.phase = SETUP_PHASE_1

                    # get players from next pairing
                    if self.playerSwap and self.playersReversed:
                        playerTwoId = self.gamesToPlay[0][0][0]
                        playerOneId = self.gamesToPlay[0][0][1]
                    else:
                        playerOneId = self.gamesToPlay[0][0][0]
                        playerTwoId = self.gamesToPlay[0][0][1]
                    self.playersReversed = not self.playersReversed

                    # set up new current players
                    self.currentPlayers.append(self.players[playerOneId][0])
                    self.currentPlayers.append(self.players[playerTwoId][0])

    ##
    # setWinner
    # Description: Given a current player ID (0 or 1), sets that player to be the winner of the current game.
    #
    # Parameters:
    #   id - the current player ID. (int)
    ##
    def setWinner(self, id):
        self.gameOver = True
        self.winner = self.currentPlayers[id].playerId
        self.loser = self.currentPlayers[1 - id].playerId

        # tell the players if they won or lost
        self.currentPlayers[id].registerWin(True)
        self.currentPlayers[1 - id].registerWin(False)

    ##
    # resolveAttack
    # Description: Checks a player wants to attack and takes appropriate action.
    #
    # Parameters:
    #   attackingAnt - The Ant that has an available attack (Ant)
    #   currentPlayer - The Player whose turn it currently is (Player)
    ##
    def resolveAttack(self, attackingAnt, currentPlayer):
        # check if player wants to attack
        validAttackCoords = []
        opponentId = (self.state.whoseTurn + 1) % 2
        range = UNIT_STATS[attackingAnt.type][RANGE]
        for ant in self.state.inventories[opponentId].ants:
            if self.isValidAttack(attackingAnt, ant.coords):
                # keep track of valid attack coords (flipped for player two)
                validAttackCoords.append(self.state.coordLookup(ant.coords, currentPlayer.playerId))
        if validAttackCoords != []:
            # give instruction to human player
            # if type(currentPlayer) is HumanPlayer.HumanPlayer:
            #     self.ui.notify("Select ant to attack")

            # players must attack if possible and we know at least one is valid
            attackCoord = None
            validAttack = False

            # if a human player, let it know an attack is expected (to affect location clicked context)
            if type(currentPlayer) is HumanPlayer.HumanPlayer:
                # give the valid attack coords to the ui to highlight
                # self.ui.attackList = validAttackCoords
                # set expecting attack for location clicked context
                self.expectingAttack = True

            # keep requesting coords until valid attack is given
            while attackCoord == None or not validAttack:
                # Draw the board again (to recognize user input inside loop)
                # self.ui.drawBoard(self.state, self.mode)

                if self.state.phase == MENU_PHASE:
                    # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                    return

                # Create a clone of the state to give to the player
                theState = self.state.clone()
                if theState.whoseTurn == PLAYER_TWO:
                    theState.flipBoard()

                # get the attack from the player (flipped for player two)
                attackCoord = self.state.coordLookup(
                    currentPlayer.getAttack(theState, attackingAnt.clone(), validAttackCoords), currentPlayer.playerId)

                # check for the move's validity
                validAttack = self.isValidAttack(attackingAnt, attackCoord)
                if not validAttack:
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        # if an ai submitted an invalid attack, exit
                        self.error(INVALID_ATTACK, attackCoord)
                        break
                    else:
                        # if a human submitted an invalid attack, reset coordList
                        currentPlayer.coordList = []

            # if we reached this point though loop, we must have a valid attack
            # if a human player, let it know an attack is expected (to affect location clicked context)
            if type(currentPlayer) is HumanPlayer.HumanPlayer:
                self.expectingAttack = False
                currentPlayer.coordList = []

            # decrement ants health
            attackedAnt = self.state.board[attackCoord[0]][attackCoord[1]].ant
            attackedAnt.health -= UNIT_STATS[attackingAnt.type][ATTACK]

            # check for dead ant
            if attackedAnt.health <= 0:
                # remove dead ant from board
                self.state.board[attackCoord[0]][attackCoord[1]].ant = None
                # remove dead ant from inventory
                self.state.inventories[opponentId].ants.remove(attackedAnt)

            # if AI mode, pause to observe attack until next or continue is clicked
            self.pauseForAIMode()

    ##
    # initGame
    # Description: resets the game's attributes to their starting state
    #
    ##
    def initGame(self):
        board = [[Location((col, row)) for row in range(0, BOARD_LENGTH)] for col in range(0, BOARD_LENGTH)]
        p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
        p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
        neutralInventory = Inventory(NEUTRAL, [], [], 0)
        self.state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)
        self.currentPlayers = []
        self.mode = None
        self.errorNotify = False
        self.gameOver = False
        self.winner = None
        self.loser = None
        # Human vs AI mode
        self.expectingAttack = False
        # AI vs AI mode: used for stepping through moves
        self.nextClicked = False
        self.continueClicked = False
        # Don't reset Tournament Mode's variables, might need to run more games

    ##
    # loadAIs
    # Description: Loads the AIPlayers from the AI subdirectory into the game.
    #
    # Parameters:
    #   humanMode - a boolean value, if true then the IDs of he AI players are
    #           offset by 1 to account for the human player as player one.
    ##
    def loadAIs(self, humanMode):
        # Reset the player list in case some have been loaded already
        self.players = []
        # self.ui.allAIs = self.players
        # Attempt to load AIs. Exit gracefully if user trying to load weird stuff.
        filesInAIFolder = os.listdir("AI")
        # Change directory to AI subfolder so modules can be loaded (they won't load as filenames).
        os.chdir('AI')

        # Add current directory in python's import search order.
        sys.path.insert(0, os.getcwd())
        # Make player instances from all AIs in folder.
        for file in filesInAIFolder:
            if re.match(".*\.py$", file):
                moduleName = file[:-3]
                # Check to see if the file is already loaded.
                # temp = __import__(moduleName, globals(), locals(), [], -1)
                temp = importlib.import_module(moduleName)
                self.players.append([temp.AIPlayer(-1), INACTIVE])
        # Remove current directory from python's import search order.
        sys.path.pop(0)
        # Revert working directory to parent.
        os.chdir('..')

    def createAICopy(self, player):
        filesInAIFolder = os.listdir("AI")
        os.chdir('AI')
        sys.path.insert(0, os.getcwd())
        for file in filesInAIFolder:
            if re.match(".*\.py$", file):
                moduleName = file[:-3]
                temp = importlib.import_module(moduleName)
                if temp.AIPlayer(-1).author == player:
                    lst = [temp.AIPlayer(-1)]
                    lst[0].author += "@@"
                    self.players.append([lst[0], INACTIVE])
                    break
        sys.path.pop(0)
        os.chdir('..')

    #########################################
    #   # ##### #     ##### ##### ####  #####
    #   # #     #     #   # #     #   # #
    ##### ###   #     ##### ###   ####  #####
    #   # #     #     #     #     #  #      #
    #   # ##### ##### #     ##### #   # #####
    #########################################

    ##
    # errorReport
    #
    # Description:  Notifies the user of an invalid move.  For AI
    # players, this takes the form of a message on the console.
    #
    # Parameters:
    #   msg - the message to send
    #
    def errorReport(self, msg):
        currentPlayer = self.currentPlayers[self.state.whoseTurn]
        if type(currentPlayer) is HumanPlayer.HumanPlayer:
            return
        print(msg)

    ##
    # isValidMove(Move)
    # Description: Checks to see if the move is valid for the current player.
    #
    # Parameters:
    #   move - The Move to check (Move)
    #
    # Returns: None if no move is given, true if the given move is valid, or false if the given move is invalid
    ##
    def isValidMove(self, move):
        # check for no move
        if move == None:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            return None

        # check that the move is well-formed typewise (tuples, ints, etc)
        if type(move) != Move:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            self.errorReport("ERROR:  player did not supply an object of type 'Move'")
            return False
        if type(move.moveType) != int:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            self.errorReport("       Move type must be an integer.")
            return False
        # for END type moves, lots we don't need to check
        if move.moveType == END:
            return True
        if move.coordList == None or type(move.coordList) != list or len(move.coordList) == 0:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            self.errorReport("       The coordinate list is empty!")
            return False
        index = 0
        for coord in move.coordList:
            if (type(coord) != tuple):
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       Coordinate at index " + str(index) + " is not a tuple.")
                return False
            if (len(coord) != 2):
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport(
                    "       Coordinate at index " + str(index) + " has " + str(len(coord)) + "entries instead of 2.")
                return False
            if (type(coord[0]) != int) or (type(coord[1]) != int):
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       Coordinate at index " + str(index) + " contains a value that is not an int.")
                return False
            index += 1
        if type(move.buildType) != type(None) and type(move.buildType) != int:
            return False

        # for MOVE_ANT and BUILD type moves
        if move.moveType == MOVE_ANT:
            firstCoord = move.coordList[0]
            # check valid start location (good coords and ant ownership)
            if self.checkMoveStart(firstCoord):
                # get ant to move
                antToMove = self.state.board[firstCoord[0]][firstCoord[1]].ant
                movePoints = UNIT_STATS[antToMove.type][MOVEMENT]
                previousCoord = None

                index = 0
                for coord in move.coordList:
                    # if first runthough, need to set up previous coord
                    if previousCoord == None:
                        previousCoord = coord
                        continue
                    # if any to-coords are invalid, return invalid move
                    if not self.checkMovePath(previousCoord, coord):
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Illegal movement path at index" + str(index))
                        return False

                    # subtract cost of loc from movement points
                    constrAtLoc = self.state.board[coord[0]][coord[1]].constr
                    if constrAtLoc == None or antToMove.type == DRONE:
                        movePoints -= 1
                    else:
                        movePoints -= CONSTR_STATS[constrAtLoc.type][MOVE_COST]

                    previousCoord = coord
                    index += 1

                # Check for Queen ant trying to leave her territory
                if (antToMove.type == QUEEN):
                    for coord in move.coordList:
                        if (coord[1] == BOARD_LENGTH / 2 - 1) \
                                or (coord[1] == BOARD_LENGTH / 2):
                            self.errorReport("ERROR: Invalid Move: " + str(move))
                            self.errorReport("       Queen ant may not leave her own territory")
                            return False

                # within movement range and hasn't moved yet?
                if (movePoints < 0):
                    self.errorReport("ERROR: Invalid Move: " + str(move))
                    self.errorReport("       Ant has insufficient movement points for this move")
                    return False
                if antToMove.hasMoved:
                    self.errorReport("ERROR: Invalid Move: " + str(move))
                    self.errorReport("       Ant has already made a move this turn")
                    return False
                else:
                    return True

        elif move.moveType == BUILD:
            # coord list must contain one point for build
            if len(move.coordList) != 1:
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       for a BUILD move, the coordinate list should contain exactly 1 coordinate")
                return False

            buildCoord = move.coordList[0]
            # check valid start location
            if self.checkBuildStart(buildCoord):
                # we're building either an ant or constr for sure

                if self.state.board[buildCoord[0]][buildCoord[1]].ant == None:
                    # we know we're building an ant
                    buildCost = None
                    # check buildType for valid ant
                    if move.buildType == WORKER:
                        buildCost = UNIT_STATS[WORKER][COST]
                    elif move.buildType == DRONE:
                        buildCost = UNIT_STATS[DRONE][COST]
                    elif move.buildType == SOLDIER:
                        buildCost = UNIT_STATS[SOLDIER][COST]
                    elif move.buildType == R_SOLDIER:
                        buildCost = UNIT_STATS[R_SOLDIER][COST]
                    else:
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       the buildType must be one of:  WORKER, DRONE, SOLDIER or R_SOLDIER.")
                        return False

                    # check the player has enough food
                    currFood = self.state.inventories[self.state.whoseTurn].foodCount
                    if currFood >= buildCost:
                        # self.ui.notify("")
                        return True
                    else:
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Player has " + str(currFood) + " food but needs " + str(
                            buildCost) + " to build this ant")
                        # self.ui.notify("Requires " + str(buildCost) + " food.")
                        self.errorNotify = True
                        return False
                else:
                    # we know we're building a construction
                    adjacentCoords = []
                    adjacentCoords.append(addCoords(buildCoord, (0, -1)))
                    adjacentCoords.append(addCoords(buildCoord, (0, 1)))
                    adjacentCoords.append(addCoords(buildCoord, (-1, 0)))
                    adjacentCoords.append(addCoords(buildCoord, (1, 0)))

                    # check that there's no food in adjacent locations
                    for aCoord in adjacentCoords:
                        if aCoord[0] >= 0 and aCoord[0] < 10 and aCoord[1] >= 0 and aCoord[1] < 10:
                            if (self.state.board[aCoord[0]][aCoord[1]].constr != None and
                                        self.state.board[aCoord[0]][aCoord[1]].constr.type == FOOD):
                                self.errorReport("ERROR: Invalid Move: " + str(move))
                                self.errorReport("       Cannot tunnel build next to food.")
                                # self.ui.notify("Cannot tunnel build next to food.")
                                self.errorNotify = True
                                return False

                    buildCost = CONSTR_STATS[TUNNEL][BUILD_COST]
                    if self.state.inventories[self.state.whoseTurn].foodCount >= buildCost:
                        # self.ui.notify("")
                        return True
                    else:
                        # self.ui.notify("Requires "+ str(buildCost) + " food.")
                        self.errorNotify = True
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Must have at least " + str(buildCost) + " food to build a tunnel.")
                        return False
            else:  # invalid build start
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       Build location invalid.  Possible cause:")
                loc = self.state.board[buildCoord[0]][buildCoord[1]]
                if loc.ant == None:  # building ant
                    self.errorReport("         - Anthill does not belong to current player")
                else:
                    if (move.buildType != TUNNEL):
                        self.errorReport("         - Anthill is already occupied")
                    elif (loc.ant.hasMoved):
                        self.errorReport("         - Worker ant has already moved this turn")
                    else:
                        self.errorReport("         - Worker ant does not belong to current player")
        else:
            # invalid numeric move type
            return False

    ##
    # isValidPlacement
    # Description: Checks that the given placement of Constructions is valid
    #
    # Paramters:
    #   items - The items to place (Construction[])
    #   targets - A list of the coordinates to place the items at ((int,int)[])
    #
    # Returns None if no target is given, true if it is a valid placement, or false if it is an invalid placement
    ##
    def isValidPlacement(self, items, targets):
        # check for well-formed input of targets (from players)
        if type(targets) == type(None) or type(targets) != list:
            return False
            # If no target, return None (human vs ai caught by caller)
        if len(targets) == 0:
            return None
        for coord in targets:
            if not self.isValidCoord(coord):
                return False

        for i in range(0, len(targets)):
            # Nobody can place in the center two rows of the board or on their opponents side

            # check item type
            if items[i].type == ANTHILL or items[i].type == TUNNEL or items[i].type == GRASS:
                # check targets[i] is within proper boundaries y-wise
                # must be on own side
                if not self.isInHomeTerritory(targets[i]):
                    return False
            # check item type
            elif items[i].type == FOOD:
                # check targets[i] is within proper boundaries y-wise
                # must be on opponent's side
                if not self.isInEnemyTerritory(targets[i]):
                    return False
            else:
                # I don't know what this type is.
                return False

            # change target to access appropriate players locations
            aTarget = self.state.coordLookup(targets[i], self.state.whoseTurn)
            # make sure nothing is there yet
            if not self.state.board[aTarget[0]][aTarget[1]].constr == None:
                return False

        return True

    ##
    # isValidAttack
    # Description: Determines whether the attack with the given parameters is valid
    #   Attacking ant is assured to exist and belong to the player whose turn it is
    #
    # Parameters:
    #   attackingAnt - The Ant that is attacking (Ant)
    #   attackCoord - The coordinates of the Ant that is being attacked ((int,int))
    #
    # Returns: None if there is no attackCoord, true if valid attack, or false if invalid attack
    ##
    def isValidAttack(self, attackingAnt, attackCoord):
        if attackCoord == None:
            return None

        # check for well-formed input from players
        if not self.isValidCoord(attackCoord):
            return False

        attackLoc = self.state.board[attackCoord[0]][attackCoord[1]]

        if attackLoc.ant == None or attackLoc.ant.player == attackingAnt.player:
            return False

        # we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        # pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            # return True if within range
            return True
        else:
            return False

    ##
    # isValidCoord
    # Description: Retruns whether this coord represents a valid board location.
    #
    # Parameters:
    #   coord - The coord to be checked trying to be checked ((int, int))
    #
    # Returns: True if the coordinate is between (0,0) and (9,9)
    ##
    def isValidCoord(self, coord):
        # check for well-formed coord
        if type(coord) != tuple or len(coord) != 2 or type(coord[0]) != int or type(coord[1]) != int:
            return False

        # check boundaries
        if coord[0] < 0 or coord[1] < 0 or coord[0] >= BOARD_LENGTH or coord[1] >= BOARD_LENGTH:
            return False

        return True

    ##
    # isInHomeTerritory
    #
    # Description: determines whether the position is in the player's
    # home territory
    #
    # Parameters:
    #   coord - The coord to be checked trying to be checked ((int, int))
    #
    # Returns: True if it is and False otherwise
    #
    ##
    def isInHomeTerritory(self, coord):
        if not self.isValidCoord(coord):
            return False
        if not (coord[1] >= 0 and coord[1] < BOARD_LENGTH / 2 - 1):
            return False
        return True

    ##
    # isInEnemyTerritory
    #
    # Description: determines whether the position is in the player's
    # enemy's territory
    #
    # Parameters:
    #   coord - The coord to be checked trying to be checked ((int, int))
    #
    # Returns: True if it is and False otherwise
    #
    ##
    def isInEnemyTerritory(self, coord):
        if not self.isValidCoord(coord):
            return False
        if not (coord[1] < BOARD_LENGTH and coord[1] >= BOARD_LENGTH / 2 + 1):
            return False
        return True

    ##
    # checkMoveStart
    # Description: Checks if the location is valid to move from.
    #  (bounds and ant ownership)
    #
    # Parameters:
    #   coord - The starting point for the move ((int, int))
    #
    # Returns: True if it is a valid starting point for a move and false if not
    ##
    def checkMoveStart(self, coord):
        # check location is on board
        if self.isValidCoord(coord):
            antToMove = self.state.board[coord[0]][coord[1]].ant
            # check that an ant exists at the loc
            if antToMove != None:
                # check that it's the player's ant and that it hasn't moved
                if antToMove.player == self.state.whoseTurn and not antToMove.hasMoved:
                    return True

        return False

    ##
    # checkMovePath
    # Description: Checks if the location is valid to move to.
    #  (clear path, adjacent locations)
    #
    # Parameters:
    #   fromCoord - The Ant's current coordinate ((int, int))
    #   toCoord - The coorinate to move the Ant to ((int, int))
    #
    # Returns: True if it is a valid move and false otherwise
    #
    # Note: fromCoord must always have been checked by the time it's passed
    #  (either in checkMoveStart or previous checkMovePath call)
    ##
    def checkMovePath(self, fromCoord, toCoord):
        # check location is on board
        if self.isValidCoord(toCoord):
            # check that squares are adjacent (difference on only one axis is 1)
            if ((abs(fromCoord[0] - toCoord[0]) == 1 and abs(fromCoord[1] - toCoord[1]) == 0) or
                    (abs(fromCoord[0] - toCoord[0]) == 0 and abs(fromCoord[1] - toCoord[1]) == 1)):
                antAtLoc = self.state.board[toCoord[0]][toCoord[1]].ant
                # check if an ant exists at the loc
                if antAtLoc == None:
                    return True

        return False

    ##
    # checkBuildStart
    # Description: Checks if the location is valid to build from.
    #  (bounds and building ownership)
    #
    # Parameters:
    #   coord - The coordinate trying to be used to build ((int, int))
    #
    # Returns: True if it is a valid build location and false otherwise
    ##
    def checkBuildStart(self, coord):
        # check location is on board
        if self.isValidCoord(coord):
            loc = self.state.board[coord[0]][coord[1]]
            # check that an empty anthill exists at the loc
            if loc.constr != None and loc.constr.type == ANTHILL and loc.ant == None:
                # check that it's the player's anthill
                if loc.constr.player == self.state.whoseTurn:
                    return True
            # check that an ant exists at an empty location
            elif loc.ant != None and loc.ant.type == WORKER and loc.constr == None:
                # check that it's the player's ant and it hasn't moved
                if loc.ant.player == self.state.whoseTurn and not loc.ant.hasMoved:
                    return True

        return False

    ##
    # hasWon(int)
    # Description: Determines whether the game has ended in victory for the given player.
    #
    # Parameters:
    #   playerId - The ID of the player being checked for winning (int)
    #
    # Returns: True if the player with playerId has won the game.
    ##
    def hasWon(self, playerId):
        opponentId = 1 - playerId

        if ((self.state.phase == PLAY_PHASE) and
                ((self.state.inventories[opponentId].getQueen() == None) or
                     (self.state.inventories[opponentId].getAnthill().captureHealth <= 0) or
                     (self.state.inventories[playerId].foodCount >= FOOD_GOAL) or
                     (self.state.inventories[opponentId].foodCount == 0 and
                              len(self.state.inventories[opponentId].ants) == 1))):
            return True
        else:
            return False

    ##
    # pauseForAIMode
    # Description: Will pause the game if set to AI mode until user clicks next or continue
    #
    ##
    def pauseForAIMode(self):
        if self.mode == AI_MODE:
            while not self.nextClicked and not self.continueClicked:
                # self.ui.drawBoard(self.state, self.mode)
                if self.state.phase == MENU_PHASE:
                    # if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                    return
            # reset nextClicked to catch next move
            self.nextClicked = False

    ##
    # printTournament
    # Description: prints the status of the tournament
    #
    ##
    def printTournament(self):
        transposedList = list(map(list, zip(*self.playerScores)))
        strTransList = [[str(n) for n in i] for i in transposedList]
        longest_len = len(max(strTransList[0], key=len))

        scoreAndTitle = [['Player', 'Wins', 'Losses']] + [['-------', '-------', '-------']] + self.playerScores
        scoreAndTitles = [[str(n) for n in i] for i in scoreAndTitle]

        for row in scoreAndTitles:
            print("".join(str(word).rjust(longest_len+2) for word in row))
        print('')

    ##
    # error
    # Description: Called when an AI player makes an error. Gives a description
    #    of what went wrong and exits the program.
    #
    # Parameters:
    #   errorCode - A code indicating the type of error
    #        info - the offending object that caused the error
    ##
    def error(self, errorCode, info):
        errorMsg = "AI ERROR: "

        if errorCode == INVALID_PLACEMENT:
            # info is a coord list
            errorMsg += "invalid placement\nCoords given: "
            lastCoord = info.pop()
            for coord in info:
                errorMsg += "(" + str(coord[0]) + ", " + str(coord[1]) + "), "
            errorMsg += "(" + str(lastCoord[0]) + ", " + str(lastCoord[1]) + ")"

        elif errorCode == INVALID_MOVE:
            # info is a move
            errorMsg += "invalid move: " + str(info) + "\n"
            if info == None:
                errorMsg += "Move is non-move type: None"
            elif type(info) != Move:
                errorMsg += "Move is non-move type: " + str(type(info))
            elif info.moveType == None:
                errorMsg += "moveType is non-int type: None"
            elif type(info.moveType) != int:
                errorMsg += "moveType is non-int type: " + str(type(info.moveType))
            elif info.moveType < MOVE_ANT or info.moveType > END:
                errorMsg += "moveType not a recognized value: " + str(info.moveType)
            elif info.moveType == MOVE_ANT:
                pass

        else:  # INVALID_ATTACK
            # info is a coord
            errorMsg += "invalid attack\n"
            errorMsg += "(" + str(info[0]) + ", " + str(info[1]) + ")"

        print(errorMsg)
        self.setWinner((self.state.whoseTurn + 1) % 2)

    #############################################################
    #####  #####  #      #      ####   #####  #####  #   #  #####
    #      #   #  #      #      #   #  #   #  #      #  #   #
    #      #####  #      #      ####   #####  #      ###    #####
    #      #   #  #      #      #   #  #   #  #      #  #       #
    #####  #   #  #####  #####  ####   #   #  #####  #   #  #####
    #############################################################

    ##
    # startGameCallback
    # Description: Starts a new game. Called when start game button is clicked.
    #
    ##
    def startGameCallback(self):
        # Notice if the user hits this button in mid-game so we can reset (below)
        reset = False
        if self.state.phase == PLAY_PHASE:
            reset = True

        # save the mode
        currMode = self.mode
        # reset the game
        self.initGame()
        # restore the mode
        self.mode = currMode

        # if we are resetting, set the phase to MENU_PHASE with no mode
        if reset:
            self.state.phase = MENU_PHASE
            self.mode = None

        if self.mode == None:
            # self.ui.notify("Please select a mode.")
            return

        # if self.ui.choosingAIs:
        #     self.ui.notify("Please submit AIs to play game.")
        #     return

        if self.state.phase == MENU_PHASE:
            # set up stuff for tournament mode
            if self.mode == TOURNAMENT_MODE:
                # reset tournament variables
                self.playerScores = []  # [[author,wins,losses], ...]
                self.gamesToPlay = []  # ((p1.id, p2.id), numGames)
                # TODO: Im not sure what this did but it was messing up round robin
                # self.numGames = None
                # notify UI tournament has started
                # self.ui.tournamentStartTime = time.clock()
                # self.ui.tournamentInProgress = True

                # if self.ui.textBoxContent != '':
                #     self.numGames = int(self.ui.textBoxContent)
                # else:
                #     self.ui.textBoxContent = '0'
                #     self.numGames = 0

                # TODO: Im not sure what this did but it was messing up round robin
                # self.numGames = 10

                # if numGames is non-positive, dont set up game
                if self.numGames <= 0:
                    return

                # self.ui.tournamentScores = []

                for i in range(0, len(self.players)):
                    # initialize the player's win/loss scores
                    tempAuth = self.players[i][0].author
                    # If the length of the author's name is longer than 24 characters, truncate it to 24 characters
                    if len(tempAuth) > 20:
                        tempAuth = tempAuth[0:21] + "..."

                    self.playerScores.append([tempAuth, 0, 0])
                    # self.ui.tournamentScores.append([tempAuth, 0, 0])

                    for j in range(i, len(self.players)):
                        if self.players[i][0] != self.players[j][0]:
                            self.gamesToPlay.append([(self.players[i][0].playerId, self.players[j][0].playerId), None])

                numPairings = len(self.gamesToPlay)
                for i in range(0, numPairings):
                    # assign equal number of games to each pairing (rounds down)
                    self.gamesToPlay[i][1] = self.numGames

                # print that The tournament has Started
                print("Tournament Starting...")

            # Make a temporary list to append to so that we may check how many AIs we have available.
            tempCurrent = []

            # Load the first two active players (idx 0 is human player)
            for index in range(0, len(self.players)):
                tempCurrent.append(self.players[index][0])
                for playerEntry in self.players[index + 1:]:
                    tempCurrent.append(playerEntry[0])
                    break
                break

            self.currentPlayers = tempCurrent

            # change the phase to setup
            self.state.phase = SETUP_PHASE_1

    ##
    # tourneyPathCallback
    # Description: Responds to a user clicking on the Tournament button
    #
    ##
    def tourneyPathCallback(self):
        # Reset the game
        self.initGame()
        # self.initUI()
        # Reset tournament mode variables
        self.playerScores = []
        self.gamesToPlay = []
        self.numGames = None
        # Attempt to load the AI files
        self.loadAIs(False)
        # Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            # self.ui.choosingAIs = True
            self.mode = TOURNAMENT_MODE
            # self.ui.notify("Mode set to Tournament. Submit two or more AI players.")
        else:
            # self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True

    ##
    # humanPathCallback
    # Description: Responds to a user clicking on the Human vs. AI button
    #
    ##
    def humanPathCallback(self):
        # Reset the game and UI
        self.initGame()
        # self.initUI()
        # Attempt to load the AI files
        self.loadAIs(True)
        # Add the human player to the player list
        self.players.insert(PLAYER_ONE, (HumanPlayer.HumanPlayer(PLAYER_ONE), ACTIVE))
        # Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            # self.ui.choosingAIs = True
            self.mode = HUMAN_MODE
            # self.ui.notify("Mode set to Human vs. AI. Submit one AI.")
        else:
            # self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True

    ##
    # aiPathCallback
    # Description: Responds to a user clicking on the AI vs. AI button
    #
    ##
    def aiPathCallback(self):
        # Reset the game
        self.initGame()
        # self.initUI()
        # Attempt to load the AI files
        self.loadAIs(False)
        # Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            # self.ui.choosingAIs = True
            self.mode = AI_MODE
            # self.ui.notify("Mode set to AI vs. AI. Submit two AIs.")
        else:
            # self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True

    ##
    # checkBoxClickedCallback
    # Description: Responds to a user clicking on a checkbox to select AIs
    #
    # Parameters:
    #   index - The index of the checkbox clicked on (int)
    ##
    def checkBoxClickedCallback(self, index):
        self.players[index][1] = ACTIVE if self.players[index][1] == INACTIVE else INACTIVE

    ##
    # submitClickedCallback
    # Description: Responds to a user clicking on the submit button when selecting AIs
    #
    ##
    def submitClickedCallback(self):
        currId = 0
        inactivePlayers = []
        for i in range(0, len(self.players)):
            if self.players[i][1] == ACTIVE:
                self.players[i][0].playerId = currId
                currId += 1
            else:
                inactivePlayers.append(self.players[i])

        # check to see if we have enough checked players
        if (len(self.players) - len(inactivePlayers)) < 2:
            # self.ui.notify("Please select more AIs to play this game type.")
            return
        if (len(self.players) - len(inactivePlayers)) > 23 and self.mode == TOURNAMENT_MODE:
            # self.ui.notify("Please select less than 24 AI players to play this game type.")
            return

        # remove all inactive players
        for player in inactivePlayers:
            self.players.remove(player)


# Import all the python files in the AI folder so they can be serialized
sys.path.insert(0, "AI")
for mod in os.listdir("AI"):
    if mod[-3:] != '.py':
        continue
    __import__(mod[:-3], locals(), globals())
del mod

if __name__ == '__main__':
    # Create the game
    a = Game()
    # a.start()


