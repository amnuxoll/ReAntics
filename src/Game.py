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
from Player import Player
import traceback
from GUIHandler import *
import threading
import time
import importlib
import argparse
from threading import Thread
import functools

from functools import partial
import copy
import InfoScraper as Is


class GameData:
    def __init__(self, p1: Player, p2: Player, numGames=1):
        self.p1 = p1
        self.p2 = p2
        self.n = numGames


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
        self.last_time = time.time()
        self.waitCond = threading.Condition()

        # Initialize the game variables
        self.players = []
        self.state = None
        self.move = None
        self.undoStates = []
        self.currentPlayers = []
        self.currentPlayerScores = []
        self.gamesToPlay = []
        self.gamesToPlayLock = threading.Lock()

        self.hasHumanPlayer = False
        self.ended = False
        self.errored = False
        self.submittedMove = None
        self.submittedAttack = None
        self.submittedSetup = None
        self.gameOver = False
        self.winner = None
        self.loser = None
        self.running = True
        self.flipped = False
        self.goToSettings = False
        self.waitingOnAI = False
        self.commandLineFinished = False
        self.killed = False
        self.safeKilled = False
        self.restarted = False
        self.restartGameList = None
        self.parser_args = {}

        # Initializes tournament mode variables
        self.playerScores = []  # [[author,wins,losses], ...]
        # debug mode allows initial setup in human vs. AI to be automated
        self.randomSetup     = False  # overrides human setup only
        self.verbose         = False
        # additional settings
        self.timeoutOn       = False
        self.playerSwap      = False  # additonal settings
        self.playersReversed = False  # whether the players are currently swapped
        self.timeoutOn       = False
        self.timeout_limit   = 1
        self.autorestart     = False
        self.pauseOnStart    = False
        self.pauseConditions = []
        self.pauseOnIllegalMove = False

        # other
        self.ee_seasonal = False
        self.hotKeyInfo = Is.getHotKeyInfo()
        self.antUnitStatsInfo = Is.getAntStats()
        self.loadAIs()
        self.playerNamesCheckList = [ai[0].author for ai in self.players]
        self.processCommandLine()
        # setup GUI
        # this has to be done in the main thread because Tkinter is dumb
        if testing:
            return

        # Initializes the UI variables
        self.UI = GUIHandler(self)

        # wait for GUI to set up
        self.UI.showFrame(0)

        # fixing the players on the settings menu
        self.UI.settingsHandler.changePlayers([ai[0].author for ai in self.players])
        self.UI.settingsHandler.createFrames()
        self.UI.settingsHandler.giveGame(self)
        self.UI.gameHandler.createFrames()
        self.UI.gameHandler.giveGame(self)

        self.gameThread = threading.Thread(target=self.start, daemon=True)
        self.gameThread.start()
        self.delayWait = 0

        self.postProcessCommandLine()
        self.post_process_settings()
        self.UI.root.mainloop()

    def gameStartRequested(self):
        while len(self.game_calls) > 0:
            g = self.game_calls.pop(0)
            self.UI.statsHandler.timeLabel.Reset()
            g()

    def submitHumanMove(self, move):
        if not self.waitCond.acquire(blocking=False):
            # we should be able to get the lock here
            # if not, something broke
            print("Error getting lock for human move")
            return
        self.submittedMove = move
        self.waitCond.notify()
        self.waitCond.release()

    def submitHumanAttack(self, attack):
        if not self.waitCond.acquire(blocking=False):
            # we should be able to get the lock here
            # if not, something broke
            print("Error getting lock for human move")
            return
        self.submittedAttack = attack
        self.waitCond.notify()
        self.waitCond.release()

    def submitHumanSetup(self, locations):
        if not self.waitCond.acquire(blocking=False):
            # we should be able to get the lock here
            # if not, something broke
            print("Error getting lock for human move")
            return
        self.submittedSetup = locations
        self.waitCond.notify()
        self.waitCond.release()

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
        # find the given, non-human, agent in the player list and get its index
        index = -1
        for player in self.players:
            if givenPlayer == player[0].author:
                index = self.players.index(player)
                break
        if (index < 0):
            print("ERROR:  AI '" + givenPlayer + "' not found.")
            print("Please specify one of the following:")
            for player in self.players[1:]:
                print('    "' + player[0].author + '"')
            # Assume if we got here it was a command line argument because the gui
            # is populated from the AI list
            self.UI.onClose()
            # sys.exit(0)

        self.gamesToPlayLock.acquire()
        self.gamesToPlay.append(GameData(HumanPlayer.HumanPlayer(HUMAN), self.players[index][0]))
        self.gamesToPlayLock.release()
        self.generalWake()

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
        # AI names should be specified as next command line args
        # need exactly two AI names
        p1, p2 = None, None
        for player in self.players:
            if player1 == player[0].author:
                # append the name of the indices for the tournament
                p1 = player[0]

            if player2 == player[0].author:
                p2 = player[0]

        if p1 is None or p2 is None:
            if p1 is None and p2 is None:
                print("ERROR:  AI '" + player1 + "' AND AI '" + player2 + "' not found.")
            elif p1 is None:
                print("ERROR:  AI '" + player1 + "' not found.")
            else:
                print("ERROR:  AI '" + player2 + "' not found.")
            print("Please specify one of the following:")
            for player in self.players:
                print('    "' + player[0].author + '"')
            # Assume if we got here it was a command line argument because the gui
            # is populated from the AI list
            self.UI.onClose()
            # sys.exit(0)

        self.gamesToPlayLock.acquire()
        self.gamesToPlay.append(GameData(p1, p2, numGames))
        self.gamesToPlayLock.release()
        self.generalWake()

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
        # AI names should be specified as next command line args
        ais = []

        for givenPlayer in givenPlayers:
            index = -1
            for player in self.players:
                if givenPlayer == player[0].author:
                    # append the name of the indices for the tournament
                    ais.append(player[0])
                    index = 1
            if index == -1:
                print("ERROR:  AI '" + givenPlayer + "' not found.")
                print("Please specify one of the following:")
                for thisPlayer in self.players:
                    print('    "' + thisPlayer[0].author + '"')
                # Assume if we got here it was a command line argument because the gui
                # is populated from the AI list
                self.UI.onClose()
                # sys.exit(0)

        # now that we have the AI's make all pairs
        self.gamesToPlayLock.acquire()
        for i in range(len(ais)):
            for j in range(i + 1, len(ais)):
                # don't make ais play themselves
                if i == j:
                    continue
                self.gamesToPlay.append(GameData(ais[i], ais[j], numGames))
        self.gamesToPlayLock.release()
        self.generalWake()

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
        # pair up every loaded AI
        self.gamesToPlayLock.acquire()
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                # don't make ais play themselves
                if i == j:
                    continue
                self.gamesToPlay.append(GameData(self.players[i][0], self.players[j][0], numGames))
        self.gamesToPlayLock.release()
        self.generalWake()

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
        if playerOne not in self.playerNamesCheckList:
            print("ERROR:  AI '" + playerOne + "' not found.")
            print("Please specify one of the following:")
            for thisPlayer in self.players:
                print('    "' + thisPlayer[0].author + '"')
            # Assume if we got here it was a command line argument because the gui
            # is populated from the AI list
            self.UI.onClose()
            # sys.exit(0)

        # get named AI
        ai = None
        for player in self.players:
            if player[0].author == playerOne:
                ai = player[0]
                break

        self.gamesToPlayLock.acquire()
        for player in self.players:
            if player[0] == ai:
                continue
            self.gamesToPlay.append(GameData(ai, player[0], numGames))
        self.gamesToPlayLock.release()
        self.generalWake()

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

        if playerOne not in self.playerNamesCheckList:
            print("ERROR:  AI '" + playerOne + "' not found.")
            print("Please specify one of the following:")
            for thisPlayer in self.players:
                print('    "' + thisPlayer[0].author + '"')
            # Assume if we got here it was a command line argument because the gui
            # is populated from the AI list
            self.UI.onClose()
            # sys.exit(0)

        # get original agent
        p1 = None
        for player in self.players:
            if player[0].author == playerOne:
                p1 = player[0]
                break

        # create a copy of the Agent you want to play itself
        p2 = self.createAICopy(playerOne)

        self.gamesToPlayLock.acquire()
        self.gamesToPlay.append(GameData(p1, p2, numGames))
        self.gamesToPlayLock.release()
        self.generalWake()

    def postProcessCommandLine(self):
        # graphics
        if self.ee_seasonal:
            self.UI.setSeasonalGraphics()
        # games
        if self.parser_args["twoP"]:
            if "human" == self.parser_args["players"][0].lower():
                self.startHumanVsAI(self.parser_args["players"][1])
            elif "human" == self.parser_args["players"][1].lower():
                self.startHumanVsAI(self.parser_args["players"][0])
            else:
                self.startAIvsAI(self.parser_args["numgames"], self.parser_args["players"][0],
                                 self.parser_args["players"][1])
        elif self.parser_args["RR"]:
            self.startRR(self.parser_args["numgames"], self.parser_args["players"])
        elif self.parser_args["RRall"]:
            self.startRRall(self.parser_args["numgames"])
        elif self.parser_args["all"]:
            self.startAllOther(self.parser_args["numgames"], self.parser_args["players"][0])
        elif self.parser_args["self"]:
            self.startSelf(self.parser_args["numgames"], self.parser_args["players"][0])
        if self.parser_args["RR"] or self.parser_args["RRall"] or self.parser_args["self"] or self.parser_args["all"] or \
                self.parser_args["twoP"]:
            self.UI.showFrame(2)
            self.UI.statsHandler.timeLabel.Reset()
            self.UI.statsHandler.timeLabel.Start()

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
        parser = argparse.ArgumentParser(description='Lets play Antics!', add_help=True, allow_abbrev=False)
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
        parser.add_argument('-s', '--seasonal', action='store_true', dest='seasonal_graphics', default=False,
                            help='February, March, October, December')
        parser.add_argument('-r', '--rules', action='store_true', dest='rules_request', default=False,
                            help='print the rules for the game (includes unit stats, hot keys...)')

        args = parser.parse_args()
        self.parser_args["numgames"] = args.numgames
        self.parser_args["players"] = args.players
        self.parser_args["RR"] = args.RR
        self.parser_args["RRall"] = args.RRall
        self.parser_args["all"] = args.all
        self.parser_args["twoP"] = args.twoP
        self.parser_args["self"] = args.self

        # check for rules request
        if args.rules_request:
            print("="*80+"\nUNIT STATS\n"+"-"*80)
            print(self.antUnitStatsInfo)
            print("="*80+"\nHOT KEYS\n"+"-"*80)
            print(self.hotKeyInfo)
            exit(0)
        
        numCheck = re.compile("[0-9]*[1-9][0-9]*")
        # Error and bounds checking for command line parameters
        if not numCheck.match(str(args.numgames)):
            parser.error('NumGames must be a positive number')
        if args.verbose:
            self.verbose = True
        if args.seasonal_graphics:
            self.ee_seasonal = True
        if (args.RR or args.RRall or args.self or args.all or args.twoP) and args.numgames is None:
            parser.error('Flags not valid without number of games (-n)')
        if args.twoP:
            if len(args.players) != 2:
                parser.error('Only two agents allowed')
            if "human" == args.players[0].lower() and "human" == args.players[1].lower():
                parser.error('Only one player may be human')
            if "human" == args.players[0].lower():
                if args.numgames != 1:
                    parser.error('Human Vs Player can only have 1 game. (-n 1)')
                if args.randomLayout:
                    self.randomSetup = True
            elif "human" == args.players[1].lower():
                if args.numgames != 1:
                    parser.error('Human Vs Player can only have 1 game. (-n 1)')
                if args.randomLayout:
                    self.randomSetup = True
        elif args.RR:
            if 'human' in args.players:
                parser.error('Human not allowed in round robin')
            if len(args.players) <= 2:
                parser.error('3 or more players needed for round robin')
        elif args.RRall:
            if args.players is not None:
                parser.error('Do not specify players with (-p), (--RRall) is for all players')
        elif args.all:
            if 'human' in args.players:
                parser.error('Human not allowed in play all others')
            if len(args.players) != 1:
                parser.error('Only specify the Player you want to play all others')
        elif args.self:
            if 'human' in args.players:
                parser.error('Human not allowed in play all others')
            if len(args.players) != 1:
                parser.error('Only specify the Player you want to play its self')
                # if args.RR or args.RRall or args.self or args.all or args.twoP:
                #     self.UI.showFrame(2)
                #     self.UI.statsHandler.timeLabel.Reset()
                #     self.UI.statsHandler.timeLabel.Start()

                # self.commandLineFinished = True

    ##
    # post_process_settings
    #
    # Description: UI variables that need to be changed according to settings after UI initialization
    #
    ##
    def post_process_settings(self):
        if self.verbose:
            self.UI.statsText.set("Print Stats On")
            self.UI.stats = False
        else:
            self.UI.statsText.set("Print Stats Off")
            self.UI.stats = True

    ##
    # process_settings
    #
    # Description: process the current settings and assign values within the game class accordingly
    #              set the game_calls queue
    #
    # Parameters: games - GameGUIData Objects list
    #             additional - dictionary of additional settings
    #             pauseConditions - list of dicts of players and conditions
    #
    ##
    def process_settings(self, games, additional, pauseConditions, testing = False):
        # set the additional settings
        self.restartGameList = None
        self.verbose = additional['verbose']
        self.playerSwap = additional['swap']
        self.playersReversed = False
        self.randomSetup = additional['layout_chosen'] == "Random Override"
        self.timeoutOn = additional['timeout']
        self.autorestart = additional['autorestart']
        self.pauseOnStart = additional['pause']
        self.pauseOnIllegalMove = additional['pauseIllegal']
        
        if self.timeoutOn:
            self.timeout_limit = float(additional['timeout_limit'])

        self.pauseConditions = pauseConditions

        # set the game queue
        self.game_calls = []
        for g in games:
            t = g.game_type
            fx = None
            if t == "Two Player":
                lower_p = [p.lower() for p in g.players]
                human_loc = lower_p.index("human") if "human" in lower_p else -1
                if human_loc != -1:
                    self.game_calls.append(partial(self.startHumanVsAI, g.players[1 - human_loc]))
                else:
                    fx = self.startAIvsAI
                    self.game_calls.append(partial(fx, g.num_games, g.players[0], g.players[1]))
            elif t == "Play Self":
                fx = self.startSelf
                self.game_calls.append(partial(fx, g.num_games, g.players[0]))
            elif t == "Round Robin":
                fx = self.startRR
                self.game_calls.append(partial(fx, g.num_games, g.players))
            elif t == "Play All":
                fx = self.startAllOther
                for player in self.players:
                    if player[0].author != g.players[0]:
                        self.game_calls.append(partial(self.startAIvsAI, g.num_games, g.players[0], player[0].author))
        if not testing: self.UI.statsHandler.clearLog()

    ##
    # start
    # Description: Runs the main game loop, requesting turns for each player.
    #       This loop runs until the user exits the game.
    #
    ##
    def start(self):
        self.UI.statsHandler.timeLabel.Start()

        while not self.ended:
            # if we have nothing to do, wait
            while len(self.gamesToPlay) == 0 and not self.ended:
                self.running = False
                if self.goToSettings:
                    self.goToSettings = False
                    self.UI.showFrame(0)
                self.UI.statsHandler.timeLabel.Stop()
                self.UI.statsHandler.timeLabel.PermanentlyStop()
                # rough fix for mac race condition - that caused it not to start
                if self.delayWait == 4:
                    self.condWait()
                else:
                    self.delayWait = (self.delayWait + 1) % 5
            if self.ended:
                break

            if self.restartGameList is None:
                # why this has to be here, I do not know, but it does or else auto-restart breaks :(
                time.sleep(.01)
                self.restartGameList = list(self.gamesToPlay)

            self.UI.statsHandler.timeLabel.Start()
            self.UI.statsHandler.addLogItem()
            if self.UI.paused:
                self.UI.pausePressed()
            self.running = True

            self.gamesToPlayLock.acquire()
            game = self.gamesToPlay.pop(0)
            self.gamesToPlayLock.release()

            self.hasHumanPlayer = game.p1.author == "Human" or game.p2.author == "Human"

            # pause on start -- only for the first game
            # don't pause if a human is playing because that feels awkward
            if self.pauseOnStart and not self.hasHumanPlayer:
                self.UI.pausePressed()
                self.pauseOnStart = False

            self.currentPlayerScores = []
            self.currentPlayerScores.append([self.truncateName(game.p1.author, 24), 0, 0])
            self.currentPlayerScores.append([self.truncateName(game.p2.author, 24), 0, 0])

            for j in range(game.n):
                self.UI.statsHandler.updateCurLogItem(self.tournamentStr(True))
                self.UI.statsHandler.setScoreRecord(self.tournamentStr(False))
                if self.verbose: print(self.tournamentStr(True), "\n")
                self.setup(game, j)
                self.UI.setPlayers(self.truncateName(self.currentPlayers[0].author),
                                   self.truncateName(self.currentPlayers[1].author))
                self.runGame()

                if self.goToSettings or self.ended:
                    self.killed = False
                    break

                if self.killed:
                    self.killed = False
                    continue
                self.resolveEndGame()

            self.UI.statsHandler.updateCurLogItem(self.tournamentStr(True))
            self.UI.statsHandler.setScoreRecord(self.tournamentStr(False))
            if self.verbose: print(self.tournamentStr(True), "\n")

            self.UI.statsHandler.stopCurLogItem(True)

            if len(self.gamesToPlay) == 0 and self.autorestart:
                # self.UI.restartPressed()
                self.restarted = True
                
            if self.restarted:
                self.restarted = False
                self.gamesToPlay = self.restartGameList
                self.restartGameList = None
                self.UI.statsHandler.clearLog()
                self.UI.statsHandler.timeLabel.Reset()
        self.UI.statsHandler.stopCurLogItem()
        self.UI.statsHandler.timeLabel.Stop()

            

    def setup(self, game, count):
        self.state = GameState.getBlankState()
        self.state.phase = SETUP_PHASE_1

        # load current players
        self.currentPlayers = []
        self.currentPlayers.append(game.p1)
        self.currentPlayers.append(game.p2)
        self.flipped = False

        # switch the order of the players if we should
        if self.playerSwap and count % 2 == 1:
            self.currentPlayers = self.currentPlayers[::-1]
            self.flipped = True

        self.gameOver = False
        self.winner = None
        self.loser = None

    ##
    # kill
    #
    # take whatever actions are necessary to kill the currently running game
    def kill(self):
        self.killed = True
        self.safeKilled = False
        self.generalWake()

    def endClient(self):
        self.ended = True
        self.kill()

    ##
    # restart
    #
    # restart the currently running game.
    def restart(self):
        self.restarted = True

    ##
    # restartFromEnd
    #
    # restarts the game set
    def restartFromEnd(self):
        self.gamesToPlay = self.restartGameList
        self.restartGameList = None
        self.UI.statsHandler.clearLog()
        self.UI.statsHandler.timeLabel.Reset()
        self.generalWake()

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
            if self.killed:
                return
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
                # clear targets list as anything on list been processed on last loop
                targets = []

                # do auto-random setup for human player if required
                if self.randomSetup and isinstance(currentPlayer, HumanPlayer.HumanPlayer):
                    if constrsToPlace[0].type != FOOD:
                        coord = (random.randint(0, 9), random.randint(0, 3))
                        if self.state.board[coord[0]][coord[1]].constr is None:
                            targets.append(coord)
                    elif constrsToPlace[0].type == FOOD:
                        coord = (random.randint(0, 9), random.randint(6, 9))
                        if self.state.board[coord[0]][coord[1]].constr is None:
                            targets.append(coord)

                # hide the 1st player's set anthill and grass placement from the 2nd player
                if theState.whoseTurn == PLAYER_TWO and self.state.phase == SETUP_PHASE_1:
                    theState.clearConstrs()

                # get the placement from the player
                if isinstance(currentPlayer, HumanPlayer.HumanPlayer) and not self.randomSetup:
                    self.UI.getHumanMove(theState.phase)
                    self.condWait()
                    if self.killed:
                        return
                    targets += self.submittedSetup
                    self.submittedSetup = None
                else:
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
                    self.pauseGame()

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
                                self.state.phase = PLAY_PHASE

                        # change player turn in state
                        self.state.whoseTurn = (self.state.whoseTurn + 1) % 2

                else:
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        # cause current player to lose game because AIs aren't allowed to make mistakes.
                        code = self.error(INVALID_PLACEMENT, targets, currentPlayer)
                        self.setWinner(1 - self.state.whoseTurn)
                        self.UI.gameHandler.setInstructionText(code)
                        # pause for the illegal move
                        if self.pauseOnIllegalMove and not self.UI.paused:
                            self.UI.pausePressed()

            elif self.state.phase == PLAY_PHASE:
                currentPlayer = self.currentPlayers[self.state.whoseTurn]

                if isinstance(currentPlayer, HumanPlayer.HumanPlayer):
                    # alert the UI that we need a move, then wait until it gives one to us
                    self.UI.getHumanMove(theState.phase)
                    self.condWait()
                    if self.killed:
                        return
                    self.move = self.submittedMove
                    self.submittedMove = None
                else:
                    if self.timeoutOn:
                        t = Thread(target=self.get_move, args=(currentPlayer, theState))
                        t.daemon = True
                        try:
                            t.start()
                            t.join(self.timeout_limit)
                            if t.isAlive():
                                raise Exception('function [get_move] timeout [%s seconds] exceeded!' % self.timeout_limit)
                        except Exception as je:
                            traceback.print_exc(limit=0)
                            self.setWinner(1 - self.state.whoseTurn)
                            return
                    else:
                        self.get_move(currentPlayer, theState)

                if self.move != None and self.move.coordList != None:
                    for i in range(0, len(self.move.coordList)):
                        # translate coords of move to match player
                        self.move.coordList[i] = self.state.coordLookup(self.move.coordList[i], self.state.whoseTurn)

                # make sure it's a valid move
                validMove = self.isValidMove(self.move)

                # complete the move if valid
                if validMove:
                    # check move type
                    if self.move.moveType == MOVE_ANT:
                        # record state in undo before applying move
                        if self.hasHumanPlayer:
                            self.undoStates.append(self.state.clone())
                        startCoord = self.move.coordList[0]
                        endCoord = self.move.coordList[-1]

                        # take ant from start coord
                        antToMove = self.state.board[startCoord[0]][startCoord[1]].ant

                        # change ant's coords and hasMoved status
                        antToMove.coords = (endCoord[0], endCoord[1])
                        antToMove.hasMoved = True

                        # remove ant from location
                        self.state.board[startCoord[0]][startCoord[1]].ant = None

                        # put ant at last loc in coordList
                        self.state.board[endCoord[0]][endCoord[1]].ant = antToMove

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseGame()

                        # check and take action for attack (workers can not attack)
                        if antToMove.type != WORKER:
                            self.resolveAttack(antToMove, currentPlayer)

                    elif self.move.moveType == BUILD:
                        # record state in undo before applying move
                        if self.hasHumanPlayer:
                            self.undoStates.append(self.state.clone())
                        coord = self.move.coordList[0]
                        currentPlayerInv = self.state.inventories[self.state.whoseTurn]

                        # subtract the cost of the item from the player's food count
                        if self.move.buildType == TUNNEL:
                            currentPlayerInv.foodCount -= CONSTR_STATS[self.move.buildType][BUILD_COST]

                            tunnel = Building(coord, TUNNEL, self.state.whoseTurn)
                            self.state.board[coord[0]][coord[1]].constr = tunnel
                        else:
                            currentPlayerInv.foodCount -= UNIT_STATS[self.move.buildType][COST]

                            ant = Ant(coord, self.move.buildType, self.state.whoseTurn)
                            ant.hasMoved = True
                            self.state.board[coord[0]][coord[1]].ant = ant
                            self.state.inventories[self.state.whoseTurn].ants.append(ant)

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseGame()


                            # clear all highlights after build
                            # self.ui.coordList = []

                    elif self.move.moveType == END:
                        # reset undo moves on each turn change
                        self.undoStates = []

                        # take care of end of turn business for ants and constructions
                        for ant in self.state.inventories[self.state.whoseTurn].ants:
                            constrUnderAnt = self.state.board[ant.coords[0]][ant.coords[1]].constr
                            if constrUnderAnt != None:
                                # if constr is enemy's and ant hasnt moved, affect capture health of buildings
                                if type(
                                        constrUnderAnt) is Building and not constrUnderAnt.player == self.state.whoseTurn:
                                    constrUnderAnt.captureHealth -= 1
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
                        nextPlayerName = self.currentPlayers[self.state.whoseTurn].author
                        self.UI.gameHandler.setInstructionText(nextPlayerName + "'s turn.")

                        # if AI mode, pause to observe move until next or continue is clicked
                        self.pauseGame()
                    elif self.move.moveType == UNDO and len(self.undoStates) > 0:
                        self.state = self.undoStates.pop()
                else:
                    # human can give None move, AI can't
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        code = self.error(INVALID_MOVE, self.move, currentPlayer)
                        self.setWinner(1 - self.state.whoseTurn)
                        self.UI.gameHandler.setInstructionText(code)
                        # pause for the illegal move
                        if self.pauseOnIllegalMove and not self.UI.paused:
                            self.UI.pausePressed()
                    elif validMove != None:
                        # if validMove is False and not None, clear move
                        currentPlayer.coordList = []
                        # self.ui.coordList = []
                        
                # check for pause condition
                if self.pauseConditionReached() and not self.UI.paused:
                    self.UI.pausePressed()
                
            # determine if if someone is a winner.
            if self.hasWon(PLAYER_ONE):
                self.setWinner(PLAYER_ONE)

            elif self.hasWon(PLAYER_TWO):
                self.setWinner(PLAYER_TWO)

    def get_move(self, currentPlayer, theState):
        self.move = currentPlayer.getMove(theState)

    def resolveEndGame(self):
        if self.UI is not None:
            self.UI.showState(self.state)
            # notify the user of the winner
            winnerName = "Copy"
            if self.winner > -1:
                winnerName = self.players[self.winner][0].author

            # special handling for human currently
            if self.winner == -1:
                winnerName = "Human"

            if self.errored:
                self.errored = False
            else:
                self.UI.gameHandler.setInstructionText("%s has won!" % winnerName)

        # adjust the wins and losses of players
        # because of how human and copies are handled currently, problems

        if self.winner >= 0:
            try:
                self.playerScores[self.winner][1] += 1
            except:
                pass
        if self.loser >= 0:
            try:
                self.playerScores[self.loser][2] += 1
            except:
                pass

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

        # make sure scores go to the right place
        if self.flipped:
            id = 1 - id

        self.currentPlayerScores[id][1] += 1
        self.currentPlayerScores[1 - id][2] += 1

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
        for ant in self.state.inventories[opponentId].ants:
            if self.isValidAttack(attackingAnt, ant.coords):
                # keep track of valid attack coords (flipped for player two)
                validAttackCoords.append(self.state.coordLookup(ant.coords, self.state.whoseTurn))
        if validAttackCoords != []:
            theState = self.state.clone()

            if self.UI is not None:
                self.UI.showState(theState)

            if theState.whoseTurn == PLAYER_TWO:
                theState.flipBoard()

            if isinstance(currentPlayer, HumanPlayer.HumanPlayer):
                # have to swap ant back for the GUI if its player 2
                self.UI.getHumanAttack(self.state.coordLookup(attackingAnt.coords, theState.whoseTurn))
                self.condWait()
                if self.killed:
                    return

                attackCoord = self.submittedAttack
                self.submittedAttack = None
            else:
                attackCoord = self.state.coordLookup(
                    currentPlayer.getAttack(theState, attackingAnt.clone(), validAttackCoords), theState.whoseTurn)

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
            self.pauseGame()

    ##
    # loadAIs
    # Description: Loads the AIPlayers from the AI subdirectory into the game.
    #
    # Parameters:
    #   humanMode - a boolean value, if true then the IDs of he AI players are
    #           offset by 1 to account for the human player as player one.
    ##
    def loadAIs(self):
        # Reset the player list in case some have been loaded already
        self.players = []
        self.playerScores = []

        # self.addPlayer(HumanPlayer.HumanPlayer(0))

        # Attempt to load AIs. Exit gracefully if user trying to load weird stuff.
        filesInAIFolder = os.listdir("AI")
        # Change directory to AI subfolder so modules can be loaded (they won't load as filenames).
        os.chdir('AI')

        # Add current directory in python's import search order.
        sys.path.insert(0, os.getcwd())
        # Make player instances from all AIs in folder.
        i = 0
        for file in filesInAIFolder:
            if re.match(".*\.py$", file) or re.match(".*\.pyc$", file):
                moduleName, ext = os.path.splitext(file)
                # Check to see if the file is already loaded.
                # temp = __import__(moduleName, globals(), locals(), [], -1)
                temp = importlib.import_module(moduleName)
                self.addPlayer(temp.AIPlayer(i))
                i += 1
        # Remove current directory from python's import search order.
        sys.path.pop(0)
        # Revert working directory to parent.
        os.chdir('..')

    def createAICopy(self, player):
        filesInAIFolder = os.listdir("AI")
        os.chdir('AI')
        sys.path.insert(0, os.getcwd())
        for file in filesInAIFolder:
            if re.match(".*\.py$", file) or re.match(".*\.pyc$", file):
                moduleName, ext = os.path.splitext(file)
                temp = importlib.import_module(moduleName)
                copy = temp.AIPlayer(COPY)
                if copy.author == player:
                    copy.author += "@@"
                    break
        sys.path.pop(0)
        os.chdir('..')
        return copy

    def addPlayer(self, p: Player):
        self.players.append([p, ACTIVE])
        self.playerScores.append([self.truncateName(p.author, 30), 0, 0])

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
        # for END or UNDO type moves, lots we don't need to check
        if move.moveType == END or move.moveType == UNDO:
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
                    if constrAtLoc == None or UNIT_STATS[antToMove.type][IGNORES_GRASS]:
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
                # we're building either an ant or constr for sure ->
                # -> no longer able to build tunnels, so can only build ants.

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
                        return False


                # Below is the code that allows a player to build more tunnels during the course of a game,
                # in case it is ever desired to be a part of the game again.

                # else:
                #     # we know we're building a construction
                #     adjacentCoords = []
                #     adjacentCoords.append(addCoords(buildCoord, (0, -1)))
                #     adjacentCoords.append(addCoords(buildCoord, (0, 1)))
                #     adjacentCoords.append(addCoords(buildCoord, (-1, 0)))
                #     adjacentCoords.append(addCoords(buildCoord, (1, 0)))
                #
                #     # check that there's no food in adjacent locations
                #     for aCoord in adjacentCoords:
                #         if aCoord[0] >= 0 and aCoord[0] < 10 and aCoord[1] >= 0 and aCoord[1] < 10:
                #             if (self.state.board[aCoord[0]][aCoord[1]].constr != None and
                #                         self.state.board[aCoord[0]][aCoord[1]].constr.type == FOOD):
                #                 self.errorReport("ERROR: Invalid Move: " + str(move))
                #                 self.errorReport("       Cannot tunnel build next to food.")
                #                 return False
                #
                #     buildCost = CONSTR_STATS[TUNNEL][BUILD_COST]
                #     if self.state.inventories[self.state.whoseTurn].foodCount >= buildCost:
                #         # self.ui.notify("")
                #         return True
                #     else:
                #         self.errorReport("ERROR: Invalid Move: " + str(move))
                #         self.errorReport("       Must have at least " + str(buildCost) + " food to build a tunnel.")
                #         return False


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
            if self.state.board[aTarget[0]][aTarget[1]].constr:
                return False
            # This item should be placed and this location becomes occupied
            self.state.board[aTarget[0]][aTarget[1]].constr = items[i]

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
        if range >= diffX + diffY:
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
    # pauseGame
    # Description: Will pause the game if set to AI mode until user clicks next or continue
    #
    ##
    def pauseGame(self):
        # nothing to pause for if there's no UI
        if self.UI is None:
            return

        if not self.UI.paused:
            return

        # pause using this wait condition
        # The GUI thread will wake
        self.waitingOnAI = True
        self.condWait()
        self.waitingOnAI = False

    def condWait(self):
        # python conditions require a lock hold to notify() for some reason
        # this is annoying in our case, where we lock to save CPU time
        # so we have each thread hold the lock for as little as possible
        self.waitCond.acquire()
        self.waitCond.wait()
        self.waitCond.release()

    ##
    # generalWake
    #
    # wake the game thread from waiting without doing any other action
    # could cause errors if used in the wrong place
    #
    def generalWake(self):
        if not self.waitCond.acquire(blocking=False):
            print("Could not get lock to wake thread.")
            return
        self.waitCond.notify()
        self.waitCond.release()

    ##
    # printTournament
    # Description: prints the status of the tournament
    #
    ##
    def printTournament(self):
        print(self.tournamentStr(False))
        print('')

    ##
    # truncateName
    #
    # returns a shortened version of a player name if needed
    def truncateName(self, name, size = 11):
        return name[0:size-5] + '..' + name[-3:] if len(name) > size else name

    ##
    # tournamentStr
    # Description: prints the status of the tournament
    #
    ##
    def tournamentStr(self, current=True):
        if current:
            scores = self.currentPlayerScores
        else:
            scores = self.playerScores

        transposedList = list(map(list, zip(*scores)))
        strTransList = [[str(n) for n in i] for i in transposedList]

        scoreAndTitle = [['Player', 'Wins', 'Losses']] + [['-------', '-------', '-------']] + scores
        scoreAndTitles = [[str(n) for n in i] for i in scoreAndTitle]

        transposedList = list(map(list, zip(*scoreAndTitles)))
        strTransList = [[str(n) for n in i] for i in transposedList]

        longest_len_0 = len(max(strTransList[0], key=len))
        longest_len_1 = len(max(strTransList[1], key=len)) + 2
        longest_len_2 = len(max(strTransList[2], key=len)) + 2

        s = []
        for row in scoreAndTitles:
            s.append(row[0].rjust(longest_len_0) + row[1].rjust(longest_len_1) + row[2].rjust(longest_len_2))
        s = "\n".join(s)
        return s

    ##
    # error
    # Description: Called when an AI player makes an error. Gives a description
    #    of what went wrong and exits the program.
    #
    # Parameters:
    #   errorCode - A code indicating the type of error
    #        info - the offending object that caused the error
    ##
    def error(self, errorCode, info, player = None):
        self.errored = True
        errorMsg = "AI ERROR: "
        if player is not None:
            errorMsg += player.author + ": "

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
        return errorMsg


    ###
    # pauseConditionReached
    # returns True if a pause condition has been reached
    def pauseConditionReached(self):
        # gather state data
        data = {}

        # food
        data["P0 Food"] = self.state.inventories[0].foodCount
        data["P1 Food"] = self.state.inventories[1].foodCount

        # anthill health
        try:
            data["P0 Anthill Health"] = self.state.inventories[0].getAnthill().captureHealth
            data["P1 Anthill Health"] = self.state.inventories[1].getAnthill().captureHealth
        except:
            return False

        # ant counts/queen health
        for i in range(2):
            i = str(i)
            ants = self.state.inventories[int(i)].ants
            
            data["P"+i+" Queen Health"] = 0
            data["P"+i+" Num Ants"] = len(ants)
            data["P"+i+" Num Workers"] = 0
            data["P"+i+" Num Drones"] = 0
            data["P"+i+" Num Soldiers"] = 0
            data["P"+i+" Num Ranged Soldiers"] = 0

            for a in ants:
                if a.type == QUEEN:
                    data["P"+i+" Queen Health"] = a.health
                elif a.type == WORKER:
                    data["P"+i+" Num Workers"] += 1
                elif a.type == DRONE:
                    data["P"+i+" Num Drones"] += 1
                elif a.type == SOLDIER:
                    data["P"+i+" Num Soldiers"] += 1
                elif a.type == R_SOLDIER:
                    data["P"+i+" Num Ranged Soldiers"] += 1

        # check the pause conditions
        for pc in self.pauseConditions:
            if not self.relevantPlayers(pc['players']):
                continue
            pause = True
            for k in list(pc['conditions'].keys()):
                pause = pause and pc['conditions'][k] == data[k]
                break
            if pause : return True
        return False

    ###
    # relevantPlayers
    # returns True if the current players match the given players
    # "Any AI" is reserved
    def relevantPlayers(self, players):
        curPlayerNames = [ai.author for ai in self.currentPlayers]
        if "Any AI" in players:
            i = 1 - players.index("Any AI")
            if players[i] == curPlayerNames[i]:
                return True
            return False
        return curPlayerNames == players


if __name__ == '__main__':
    # Create the game
    a = Game()
    # a.start()
