import os, re, sys, math, multiprocessing, time, random
import HumanPlayer
from UserInterface import *
from Construction import *
from Constants import *
from GameState import *
from Inventory import *
from Building import *
from Location import *
from Ant import *
from Move import *

##
#Game
#Description: Keeps track of game logic and manages the play loop.
##
class Game(object):


    ##
    #__init__
    #Description: Initializes the game's attributes and UI.
    #
    ##
    def __init__(self):
        #Initialize the game variables
        self.players = []
        self.initGame()
        #Initializes the UI variables
        self.ui = UserInterface((865,695))
        self.initUI()
        #Initializes tournament mode variables
        self.playerScores = [] # [[author,wins,losses], ...]
        self.gamesToPlay = [] #((p1.id, p2.id), numGames)
        self.numGames = None
        #debug mode allows initial setup in human vs. AI to be automated
        self.debugMode = False
        self.randomSetup = False
        
    ##
    #processCommandLine
    #
    # parses the command line arguments and configures the game
    # appropriately.
    # "debug" arguments are supported. In this format:
    #           python Game.py debug [<myAIName>] [random]
    # "-t" or tournament arguments are suported in this format:
    #           python Game.py -t <AIName1> <AIName2> [-n <number of games>]
    #       The number of games defaults to 10 if no -n argument is specified.
    ##
    def processCommandLine(self):
        #process command line arguments
        if (len(sys.argv) > 1):
            #player wants to go straight to AI vs. Human for a
            #specific AI
            if sys.argv[1] == "debug":
                self.debugMode = True
                self.humanPathCallback()   #press the "Human vs. AI" button
                #AI name should be specified as second command line arg
                index = -1
                if (len(sys.argv) > 2):
                    ainame = sys.argv[2]
                    for player in self.players:
                        if ainame == player[0].author:
                            index = self.players.index(player)
                            break
                    if (index < 0):
                        print "ERROR:  AI '" + ainame + "' not found."
                        print "Please specify one of the following:"
                        for player in self.players[1:]:
                            print '    "' + player[0].author + '"'
                        return
                    #select the specified AI and click "Submit"
                    self.checkBoxClickedCallback(index)
                    self.submitClickedCallback()
                    self.startGameCallback()
                #User may specify "random" as third argument to get a
                #random layout.  
                if (len(sys.argv) > 3) and (sys.argv[3] == "random"):
                    self.randomSetup = True

            # Check Tournament
            if sys.argv[1].lower() == "-t":
                # press the "Tournament Mode" button
                self.tourneyPathCallback()

                numGames = 10

                # AI names should be specified as next command line args
                # need exactly two AI names
                aiNameIndices = []
                index = -1
                if (len(sys.argv) > 3):
                    ainame1 = sys.argv[2]
                    ainame2 = sys.argv[3]
                    for player in self.players:
                        if ainame1 == player[0].author or ainame2 == player[0].author:
                            # append the name of the indices for the tournament
                            aiNameIndices.append(self.players.index(player))

                    if (len(aiNameIndices) < 2):
                        print "ERROR:  AI '" + ainame1 + "' OR AI '" + ainame2 + "' not found."
                        print "Please specify one of the following:"
                        for player in self.players[1:]:
                            print '    "' + player[0].author + '"'
                        return

                # get the number of games for the tournament if specified
                if (len(sys.argv) > 5):
                    if sys.argv[4].lower() == "-n":
                        try:
                            numGames = int(sys.argv[5])
                        except ValueError:
                            print "ERROR: Please enter a number after -n "
                            return
                    else:
                        print "ERROR: Please specify -n to give a specific number of games to run."
                        print "     FORMAT: -n 1000"
                        return

                # now that we have the AI's check the check boxes
                for index in aiNameIndices:
                    self.checkBoxClickedCallback(index)

                self.ui.textBoxContent = str(numGames)

                self.submitClickedCallback()
                self.startGameCallback()
                pass
        


        
    ##
    #start
    #Description: Runs the main game loop, requesting turns for each player. 
    #       This loop runs until the user exits the game.
    #
    ##
    def start(self):
        self.processCommandLine()

        while True:
            #Determine current chosen game mode. Enter different execution paths
            #based on the mode, which must be chosen by clicking a button.
            self.ui.drawBoard(self.state, self.mode)
            
            if not self.errorNotify:
                if self.mode == None:
                    self.ui.notify("Please select a game mode.")
                elif not self.ui.choosingAIs and self.state.phase == MENU_PHASE:
                    self.ui.notify("Please start the game.")
                
            #player has clicked start game so enter game loop
            if self.state.phase != MENU_PHASE:
                #clear notifications
                self.ui.notify("")
                 
                self.runGame()   
                self.resolveEndGame()

    ##
    # runGame
    #
    # Description: the main game loop
    #
    # ToDo:  This method is way too large and needs to be broken up
    #
    ##
    def runGame(self):
        #build a list of things to place for player 1 in setup phase 1
        #1 anthill/queen, 1 tunnel/worker, 9 obstacles
        constrsToPlace = []
        constrsToPlace += [Building(None, ANTHILL, PLAYER_ONE)]
        constrsToPlace += [Building(None, TUNNEL, PLAYER_ONE)]
        constrsToPlace += [Construction(None, GRASS) for i in xrange(0,9)]
    
        while not self.gameOver:
            if self.state.phase == MENU_PHASE:
                #if we are in menu phase at this point, a reset was requested so break
                break
            else:
                #create a copy of the state to share with the player
                theState = self.state.clone()
                #if the player is player two, flip the board
                if theState.whoseTurn == PLAYER_TWO:
                    theState.flipBoard()

            if self.state.phase == SETUP_PHASE_1 or self.state.phase == SETUP_PHASE_2:
                currentPlayer = self.currentPlayers[self.state.whoseTurn]
                if type(currentPlayer) is HumanPlayer.HumanPlayer:
                    if constrsToPlace[0].type == ANTHILL:
                        self.ui.notify("Place anthill on your side.")
                    elif constrsToPlace[0].type == TUNNEL:
                        self.ui.notify("Place tunnel on your side.")
                    elif constrsToPlace[0].type == GRASS:
                        self.ui.notify("Place grass on your side.")
                    elif constrsToPlace[0].type == FOOD:
                        self.ui.notify("Place food on enemy's side.")
                #clear targets list as anything on list been processed on last loop
                targets = []
                
                #do auto-random setup for human player if required
                if (self.randomSetup) and (type(currentPlayer) is HumanPlayer.HumanPlayer):
                    if (constrsToPlace[0].type != FOOD):
                        coord = (random.randint(0,9), random.randint(0,3))
                        if (self.state.board[coord[0]][coord[1]].constr == None):
                            targets.append(coord)
                    elif (constrsToPlace[0].type == FOOD):
                        coord = (random.randint(0,9), random.randint(6,9))
                        if (self.state.board[coord[0]][coord[1]].constr == None):
                            targets.append(coord)

                #hide the 1st player's set anthill and grass placement from the 2nd player
                if theState.whoseTurn == PLAYER_TWO and self.state.phase == SETUP_PHASE_1:
                    theState.clearConstrs()
                    
                #get the placement from the player
                targets += currentPlayer.getPlacement(theState)
                #only want to place as many targets as constructions to place
                if len(targets) > len(constrsToPlace):
                    targets = targets[:len(constrsToPlace)]

                validPlace = self.isValidPlacement(constrsToPlace, targets)
                if validPlace:
                    for target in targets:
                        #translate coords to match player
                        target = self.state.coordLookup(target, self.state.whoseTurn)
                        #get construction to place
                        constr = constrsToPlace.pop(0)
                        #give constr its coords
                        constr.coords = target
                        #put constr on board
                        self.state.board[target[0]][target[1]].constr = constr
                        if constr.type == ANTHILL or constr.type == TUNNEL:
                            #update the inventory
                            self.state.inventories[self.state.whoseTurn].constrs.append(constr)
                        else:  #grass and food
                            self.state.inventories[NEUTRAL].constrs.append(constr)
                    
                    #if AI mode, pause to observe move until next or continue is clicked
                    self.pauseForAIMode()
                    if self.state.phase == MENU_PHASE:
                        #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                        break
                    
                    if not constrsToPlace:
                        constrsToPlace = []
                        if self.state.phase == SETUP_PHASE_1:
                            if self.state.whoseTurn == PLAYER_ONE:
                                constrsToPlace += [Building(None, ANTHILL, PLAYER_TWO)]
                                constrsToPlace += [Building(None, TUNNEL, PLAYER_TWO)]
                                constrsToPlace += [Construction(None, GRASS) for i in xrange(0,9)]
                            elif self.state.whoseTurn == PLAYER_TWO:
                                constrsToPlace += [Construction(None, FOOD) for i in xrange(0,2)]
                                self.state.phase = SETUP_PHASE_2
                        elif self.state.phase == SETUP_PHASE_2:
                            if self.state.whoseTurn == PLAYER_ONE:
                                constrsToPlace += [Construction(None, FOOD) for i in xrange(0,2)]
                            elif self.state.whoseTurn == PLAYER_TWO:
                                #if we're finished placing, add in queens and move to play phase
                                p1inventory = self.state.inventories[PLAYER_ONE]
                                p2inventory = self.state.inventories[PLAYER_TWO]
                                #get anthill coords
                                p1AnthillCoords = p1inventory.constrs[0].coords
                                p2AnthillCoords = p2inventory.constrs[0].coords
                                #get tunnel coords
                                p1TunnelCoords = p1inventory.constrs[1].coords
                                p2TunnelCoords = p2inventory.constrs[1].coords
                                #create queen and worker ants
                                p1Queen = Ant(p1AnthillCoords, QUEEN, PLAYER_ONE)
                                p2Queen = Ant(p2AnthillCoords, QUEEN, PLAYER_TWO)
                                p1Worker = Ant(p1TunnelCoords, WORKER, PLAYER_ONE)
                                p2Worker = Ant(p2TunnelCoords, WORKER, PLAYER_TWO)
                                #put ants on board
                                self.state.board[p1Queen.coords[0]][p1Queen.coords[1]].ant = p1Queen
                                self.state.board[p2Queen.coords[0]][p2Queen.coords[1]].ant = p2Queen
                                self.state.board[p1Worker.coords[0]][p1Worker.coords[1]].ant = p1Worker
                                self.state.board[p2Worker.coords[0]][p2Worker.coords[1]].ant = p2Worker
                                #add the queens to the inventories
                                p1inventory.ants.append(p1Queen)
                                p2inventory.ants.append(p2Queen)
                                p1inventory.ants.append(p1Worker)
                                p2inventory.ants.append(p2Worker)
                                #give the players the initial food
                                p1inventory.foodCount = 1
                                p2inventory.foodCount = 1
                                #change to play phase
                                self.ui.notify("")
                                self.state.phase = PLAY_PHASE
                                
                        #change player turn in state
                        self.state.whoseTurn = (self.state.whoseTurn + 1) % 2
                            
                else:
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        #cause current player to lose game because AIs aren't allowed to make mistakes.
                        self.error(INVALID_PLACEMENT, targets)
                        break
                    elif validPlace != None:
                        self.ui.notify("Invalid placement.")
                        self.errorNotify = True
                
            elif self.state.phase == PLAY_PHASE: 
                currentPlayer = self.currentPlayers[self.state.whoseTurn]
                
                #display instructions for human player
                if type(currentPlayer) is HumanPlayer.HumanPlayer:
                    #An error message is showing
                    if not self.errorNotify:
                        #nothing selected yet
                        if not currentPlayer.coordList:
                            self.ui.notify("Select an ant or building.")
                        #ant selected
                        elif not self.state.board[currentPlayer.coordList[0][0]][currentPlayer.coordList[0][1]].ant == None:
                            self.ui.notify("Select move for ant.")
                        #Anthill selected
                        elif not self.state.board[currentPlayer.coordList[0][0]][currentPlayer.coordList[0][1]].constr == None:
                            self.ui.notify("Select an ant type to build.")
                        else:
                            self.ui.notify("")

                            
                #get the move from the current player in a separate
                #process so that we can time it out
                move = currentPlayer.getMove(theState)
                
                if move != None and move.coordList != None:
                    for i in xrange(0,len(move.coordList)):
                        #translate coords of move to match player
                        move.coordList[i] = self.state.coordLookup(move.coordList[i], self.state.whoseTurn)
                
                #make sure it's a valid move
                validMove = self.isValidMove(move)
                
                #complete the move if valid
                if validMove:
                    #check move type
                    if move.moveType == MOVE_ANT:
                        startCoord = move.coordList[0]
                        endCoord = move.coordList[-1]
                        
                        #take ant from start coord
                        antToMove = self.state.board[startCoord[0]][startCoord[1]].ant
                        #change ant's coords and hasMoved status
                        antToMove.coords = (endCoord[0], endCoord[1])
                        antToMove.hasMoved = True
                        #remove ant from location
                        self.state.board[startCoord[0]][startCoord[1]].ant = None
                        #put ant at last loc in coordList
                        self.state.board[endCoord[0]][endCoord[1]].ant = antToMove
                        
                        #clear all highlights after move happens
                        self.ui.coordList = []
                        
                        #if AI mode, pause to observe move until next or continue is clicked                               
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break
                        
                        #check and take action for attack (workers can not attack)
                        if (antToMove.type != WORKER):
                            self.resolveAttack(antToMove, currentPlayer)

                        #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                        if self.state.phase == MENU_PHASE:
                            break

                        #clear all highlights after attack happens
                        self.ui.coordList = []
                        self.ui.attackList = []
                        
                    elif move.moveType == BUILD:
                        coord = move.coordList[0]
                        currentPlayerInv = self.state.inventories[self.state.whoseTurn]
                                                 
                        #subtract the cost of the item from the player's food count
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
                        
                        #if AI mode, pause to observe move until next or continue is clicked
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break
                        
                        #clear all highlights after build
                        self.ui.coordList = []    
                        
                    elif move.moveType == END:
                        #take care of end of turn business for ants and contructions
                        for ant in self.state.inventories[self.state.whoseTurn].ants:
                            constrUnderAnt = self.state.board[ant.coords[0]][ant.coords[1]].constr
                            if constrUnderAnt != None:
                                #if constr is enemy's and ant hasnt moved, affect capture health of buildings
                                if type(constrUnderAnt) is Building and not ant.hasMoved and not constrUnderAnt.player == self.state.whoseTurn:
                                    constrUnderAnt.captureHealth -= 1
                                    if constrUnderAnt.captureHealth == 0 and constrUnderAnt.type != ANTHILL:
                                        constrUnderAnt.player = self.state.whoseTurn
                                        constrUnderAnt.captureHealth = CONSTR_STATS[constrUnderAnt.type][CAP_HEALTH]
                                #have all worker ants on food sources gather food
                                elif constrUnderAnt.type == FOOD and ant.type == WORKER:
                                    ant.carrying = True
                                #deposit carried food (only workers carry)
                                elif (constrUnderAnt.type == ANTHILL or constrUnderAnt.type == TUNNEL) and ant.carrying == True:
                                    self.state.inventories[self.state.whoseTurn].foodCount += 1
                                    ant.carrying = False
                            
                            #reset hasMoved on all ants of player
                            ant.hasMoved = False   
                            
                        #clear any currently highlighted squares
                        self.ui.coordList = []
                        
                        #switch whose turn it is
                        self.state.whoseTurn = (self.state.whoseTurn + 1) % 2

                        #notify player which AI is acting
                        nextPlayerName = self.players[self.state.whoseTurn][0].author
                        self.ui.notify(nextPlayerName + "'s turn.")
                        
                        #if AI mode, pause to observe move until next or continue is clicked
                        self.pauseForAIMode()
                        if self.state.phase == MENU_PHASE:
                            #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                            break
                else:     
                    #human can give None move, AI can't
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        self.error(INVALID_MOVE, move)
                        break
                    elif validMove != None:
                        #if validMove is False and not None, clear move
                        currentPlayer.coordList = []
                        self.ui.coordList = []
          
            #determine if if someone is a winner.
            if self.hasWon(PLAYER_ONE):
                self.setWinner(PLAYER_ONE)
                
            elif self.hasWon(PLAYER_TWO):
                self.setWinner(PLAYER_TWO)
                
            #redraw the board periodically and check for user input
            self.ui.drawBoard(self.state, self.mode)
            
        #end game loop
    
    def resolveEndGame(self):
        if self.state.phase != MENU_PHASE:
            #check mode for appropriate response to game over
            if self.mode == HUMAN_MODE:
                self.state.phase = MENU_PHASE
                                         
                #notify the user of the winner
                if self.winner == PLAYER_ONE:
                    self.ui.notify("You have won the game!")
                else:
                    self.ui.notify("The AI has won the game!")
                    
                self.errorNotify = True

            if self.mode == AI_MODE:
                self.state.phase = MENU_PHASE
                                         
                #notify the user of the winner
                winnerName = self.players[self.winner][0].author
                self.ui.notify(winnerName + " has won the game!")
                self.errorNotify = True

            elif self.mode == TOURNAMENT_MODE:               
                #adjust the count of games to play for the current pair
                currentPairing = (self.currentPlayers[PLAYER_ONE].playerId, self.currentPlayers[PLAYER_TWO].playerId)
           
                #give the new scores to the UI
                self.ui.tournamentScores = self.playerScores

                #adjust the wins and losses of players
                self.playerScores[self.winner][1] += 1
                self.playerScores[self.loser][2] += 1

                # if CommandLine Mode print the values to the console
                self.printTournament()

                #reset the game
                self.initGame()
               
                for i in range(0, len(self.gamesToPlay)):
                    #if we found the current pairing
                    if self.gamesToPlay[i][0] == currentPairing:
                        #mark off another game for the pairing
                        self.gamesToPlay[i][1] -= 1
                        
                        #if the pairing has no more games, then remove it
                        if self.gamesToPlay[i][1] == 0:
                            self.gamesToPlay.remove(self.gamesToPlay[i])
                        break
                        
                if len(self.gamesToPlay) == 0:
                    #if no more games to play, reset tournament stuff
                    self.numGames = 0                               
                    self.playerScores = []
                    self.mode = TOURNAMENT_MODE
                    self.ui.tournamentInProgress = False
                else:
                    #setup game to run again
                    self.mode = TOURNAMENT_MODE
                    self.state.phase = SETUP_PHASE_1
                
                    #get players from next pairing
                    playerOneId = self.gamesToPlay[0][0][0]
                    playerTwoId = self.gamesToPlay[0][0][1]
                
                    #set up new current players
                    self.currentPlayers.append(self.players[playerOneId][0])
                    self.currentPlayers.append(self.players[playerTwoId][0]) 
    
    ##
    #setWinner
    #Description: Given a current player ID (0 or 1), sets that player to be the winner of the current game.
    #
    #Parameters:
    #   id - the current player ID. (int)
    ##
    def setWinner(self, id):
        self.gameOver = True
        self.winner = self.currentPlayers[id].playerId
        self.loser = self.currentPlayers[(id + 1) % 2].playerId
         
        #tell the players if they won or lost
        self.currentPlayers[id].registerWin(True)
        self.currentPlayers[(id + 1) % 2].registerWin(False)
    
    ##
    #resolveAttack 
    #Description: Checks a player wants to attack and takes appropriate action.
    #
    #Parameters:
    #   attackingAnt - The Ant that has an available attack (Ant)
    #   currentPlayer - The Player whose turn it currently is (Player)
    ##   
    def resolveAttack(self, attackingAnt, currentPlayer):
        #check if player wants to attack
        validAttackCoords = []
        opponentId = (self.state.whoseTurn + 1) % 2
        range = UNIT_STATS[attackingAnt.type][RANGE]
        for ant in self.state.inventories[opponentId].ants:
            if self.isValidAttack(attackingAnt, ant.coords):
                #keep track of valid attack coords (flipped for player two)
                validAttackCoords.append(self.state.coordLookup(ant.coords, currentPlayer.playerId))
        if validAttackCoords != []:
            #give instruction to human player
            if type(currentPlayer) is HumanPlayer.HumanPlayer:
                self.ui.notify("Select ant to attack")
            
            #players must attack if possible and we know at least one is valid
            attackCoord = None
            validAttack = False
            
            #if a human player, let it know an attack is expected (to affect location clicked context)
            if type(currentPlayer) is HumanPlayer.HumanPlayer:
                #give the valid attack coords to the ui to highlight                                
                self.ui.attackList = validAttackCoords
                #set expecting attack for location clicked context
                self.expectingAttack = True
            
            #keep requesting coords until valid attack is given
            while attackCoord == None or not validAttack:               
                #Draw the board again (to recognize user input inside loop)
                self.ui.drawBoard(self.state, self.mode)
                
                if self.state.phase == MENU_PHASE:
                    #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                    return
                
                #Create a clone of the state to give to the player
                theState = self.state.clone()
                if theState.whoseTurn == PLAYER_TWO:
                    theState.flipBoard()
                        
                #get the attack from the player (flipped for player two)
                attackCoord = self.state.coordLookup(currentPlayer.getAttack(theState, attackingAnt.clone(), validAttackCoords), currentPlayer.playerId)
                
                #check for the move's validity
                validAttack = self.isValidAttack(attackingAnt, attackCoord)
                if not validAttack:
                    if not type(currentPlayer) is HumanPlayer.HumanPlayer:
                        #if an ai submitted an invalid attack, exit
                        self.error(INVALID_ATTACK, attackCoord)
                        break
                    else:
                        #if a human submitted an invalid attack, reset coordList
                        currentPlayer.coordList = []

            #if we reached this point though loop, we must have a valid attack
            #if a human player, let it know an attack is expected (to affect location clicked context)
            if type(currentPlayer) is HumanPlayer.HumanPlayer:
                self.expectingAttack = False
                currentPlayer.coordList = []
            
            #decrement ants health
            attackedAnt = self.state.board[attackCoord[0]][attackCoord[1]].ant
            attackedAnt.health -= UNIT_STATS[attackingAnt.type][ATTACK]
            
            #check for dead ant
            if attackedAnt.health <= 0:
                #remove dead ant from board
                self.state.board[attackCoord[0]][attackCoord[1]].ant = None
                #remove dead ant from inventory
                self.state.inventories[opponentId].ants.remove(attackedAnt)
                
            #if AI mode, pause to observe attack until next or continue is clicked
            self.pauseForAIMode()
            
    ##
    #initGame
    #Description: resets the game's attributes to their starting state
    #
    ##
    def initGame(self):
        board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
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
        #Human vs AI mode
        self.expectingAttack = False
        #AI vs AI mode: used for stepping through moves
        self.nextClicked = False
        self.continueClicked = False
        #Don't reset Tournament Mode's variables, might need to run more games
        
    ##
    #initUI
    #Description: resets the game's UI attributes to their starting state
    #
    ##
    def initUI(self):
        self.ui.initAssets()
        #UI Callback functions
        self.ui.buttons['Start'][-1] = self.startGameCallback
        self.ui.buttons['Tournament'][-1] = self.tourneyPathCallback
        self.ui.buttons['Human vs AI'][-1] = self.humanPathCallback
        self.ui.buttons['AI vs AI'][-1] = self.aiPathCallback      
        self.ui.humanButtons['Build'][-1] = self.buildClickedCallback
        self.ui.humanButtons['End'][-1] = self.endClickedCallback
        self.ui.aiButtons['Next'][-1] = self.nextClickedCallback
        self.ui.aiButtons['Continue'][-1] = self.continueClickedCallback
        self.ui.antButtons['Worker'][-1] = self.buildWorkerCallback
        self.ui.antButtons['Drone'][-1] = self.buildDroneCallback
        self.ui.antButtons['Soldier'][-1] = self.buildDSoldierCallback
        self.ui.antButtons['Ranged Soldier'][-1] = self.buildISoldierCallback
        self.ui.antButtons['None'][-1] = self.buildNothingCallback       
        self.ui.submitSelected['Submit AIs'][-1] = self.submitClickedCallback
        self.ui.locationClicked = self.locationClickedCallback      
        self.ui.checkBoxClicked = self.checkBoxClickedCallback
        self.ui.allAIs = self.players
            
    ##
    #loadAIs
    #Description: Loads the AIPlayers from the AI subdirectory into the game.
    #
    #Parameters:
    #   humanMode - a boolean value, if true then the IDs of he AI players are
    #           offset by 1 to account for the human player as player one.
    ##
    def loadAIs(self, humanMode):
        #Reset the player list in case some have been loaded already
        self.players = []
        self.ui.allAIs = self.players
        #Attempt to load AIs. Exit gracefully if user trying to load weird stuff.
        filesInAIFolder = os.listdir("AI")
        #Change directory to AI subfolder so modules can be loaded (they won't load as filenames).
        os.chdir('AI')
      
        #Add current directory in python's import search order.
        sys.path.insert(0, os.getcwd())
        #Make player instances from all AIs in folder.
        for file in filesInAIFolder:
            if re.match(".*\.py$", file):
                moduleName = file[:-3]
                #Check to see if the file is already loaded.
                temp = __import__(moduleName, globals(), locals(), [], -1)
                #If the module has already been imported into this python instance, reload it.
                if temp == None:
                    temp = reload(globals()[moduleName])
                #Create an instance of Player from temp
                self.players.append([temp.AIPlayer(-1), INACTIVE])
        #Remove current directory from python's import search order.
        sys.path.pop(0)
        #Revert working directory to parent.
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
        print msg
        
    ##
    #isValidMove(Move)
    #Description: Checks to see if the move is valid for the current player.
    # 
    #Parameters:
    #   move - The Move to check (Move)
    #
    #Returns: None if no move is given, true if the given move is valid, or false if the given move is invalid
    ##
    def isValidMove(self, move):
        #check for no move
        if move == None:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            return None
        
        #check that the move is well-formed typewise (tuples, ints, etc)
        if type(move) != Move:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            self.errorReport("ERROR:  player did not supply an object of type 'Move'")
            return False
        if type(move.moveType) != int:
            self.errorReport("ERROR: Invalid Move: " + str(move))
            self.errorReport("       Move type must be an integer.")
            return False
        #for END type moves, lots we don't need to check
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
                self.errorReport("       Coordinate at index " + str(index) + " has " + str(len(coord)) + "entries instead of 2.")
                return False
            if (type(coord[0]) != int) or (type(coord[1]) != int):
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       Coordinate at index " + str(index) + " contains a value that is not an int.")
                return False
            index += 1
        if type(move.buildType) != type(None) and type(move.buildType) != int:
            return False

        #for MOVE_ANT and BUILD type moves
        if move.moveType == MOVE_ANT:
            firstCoord = move.coordList[0]
            #check valid start location (good coords and ant ownership)
            if self.checkMoveStart(firstCoord):
                #get ant to move
                antToMove = self.state.board[firstCoord[0]][firstCoord[1]].ant
                movePoints = UNIT_STATS[antToMove.type][MOVEMENT]             
                previousCoord = None

                index = 0
                for coord in move.coordList:
                    #if first runthough, need to set up previous coord
                    if previousCoord == None:
                        previousCoord = coord
                        continue  
                    #if any to-coords are invalid, return invalid move
                    if not self.checkMovePath(previousCoord, coord):
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Illegal movement path at index" + str(index))
                        return False
                        
                    #subtract cost of loc from movement points
                    constrAtLoc = self.state.board[coord[0]][coord[1]].constr
                    if constrAtLoc == None or antToMove.type == DRONE:
                        movePoints -= 1
                    else:
                        movePoints -= CONSTR_STATS[constrAtLoc.type][MOVE_COST]
                        
                    previousCoord = coord
                    index += 1
                    
                #Check for Queen ant trying to leave her territory
                if (antToMove.type == QUEEN):
                    for coord in move.coordList:
                        if (coord[1] == BOARD_LENGTH / 2 - 1) \
                        or (coord[1] == BOARD_LENGTH / 2):
                            self.errorReport("ERROR: Invalid Move: " + str(move))
                            self.errorReport("       Queen ant may not leave her own territory")
                            return False
                            
                #within movement range and hasn't moved yet?
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
            #coord list must contain one point for build
            if len(move.coordList) != 1:
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       for a BUILD move, the coordinate list should contain exactly 1 coordinate")
                return False
        
            buildCoord = move.coordList[0]
            #check valid start location
            if self.checkBuildStart(buildCoord):
                #we're building either an ant or constr for sure
               
                if self.state.board[buildCoord[0]][buildCoord[1]].ant == None:
                #we know we're building an ant
                    buildCost = None
                    #check buildType for valid ant
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
                    
                    #check the player has enough food
                    currFood = self.state.inventories[self.state.whoseTurn].foodCount
                    if currFood >= buildCost:
                        self.ui.notify("")
                        return True
                    else:
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Player has " + str(currFood) + " food but needs " + str(buildCost) + " to build this ant")
                        self.ui.notify("Requires " + str(buildCost) + " food.")
                        self.errorNotify = True
                        return False
                else:
                #we know we're building a construction
                    adjacentCoords = []
                    adjacentCoords.append(addCoords(buildCoord, (0, -1)))
                    adjacentCoords.append(addCoords(buildCoord, (0, 1)))
                    adjacentCoords.append(addCoords(buildCoord, (-1, 0)))
                    adjacentCoords.append(addCoords(buildCoord, (1, 0)))
                
                    #check that there's no food in adjacent locations
                    for aCoord in adjacentCoords:
                        if aCoord[0] >= 0 and aCoord[0] < 10 and aCoord[1] >= 0 and aCoord[1] < 10:
                            if (self.state.board[aCoord[0]][aCoord[1]].constr != None and
                                    self.state.board[aCoord[0]][aCoord[1]].constr.type == FOOD):
                                self.errorReport("ERROR: Invalid Move: " + str(move))
                                self.errorReport("       Cannot tunnel build next to food.")
                                self.ui.notify("Cannot tunnel build next to food.")
                                self.errorNotify = True
                                return False
                 
                    buildCost = CONSTR_STATS[TUNNEL][BUILD_COST]
                    if self.state.inventories[self.state.whoseTurn].foodCount >= buildCost:
                        self.ui.notify("")
                        return True
                    else:
                        self.ui.notify("Requires "+ str(buildCost) + " food.")
                        self.errorNotify = True
                        self.errorReport("ERROR: Invalid Move: " + str(move))
                        self.errorReport("       Must have at least " + str(buildCost) + " food to build a tunnel.")
                        return False
            else:  #invalid build start
                self.errorReport("ERROR: Invalid Move: " + str(move))
                self.errorReport("       Build location invalid.  Possible cause:")
                loc = self.state.board[buildCoord[0]][buildCoord[1]]
                if loc.ant == None:  #building ant
                    self.errorReport("         - Anthill does not belong to current player")
                else:
                    if (move.buildType != TUNNEL):
                        self.errorReport("         - Anthill is already occupied")
                    elif (loc.ant.hasMoved):
                        self.errorReport("         - Worker ant has already moved this turn")
                    else:
                        self.errorReport("         - Worker ant does not belong to current player")
        else:
            #invalid numeric move type
            return False
            
    ##
    #isValidPlacement
    #Description: Checks that the given placement of Constructions is valid
    #
    #Paramters:
    #   items - The items to place (Construction[])
    #   targets - A list of the coordinates to place the items at ((int,int)[])
    #
    #Returns None if no target is given, true if it is a valid placement, or false if it is an invalid placement
    ##
    def isValidPlacement(self, items, targets):
        #check for well-formed input of targets (from players)
        if type(targets) == type(None) or type(targets) != list:
            return False
         #If no target, return None (human vs ai caught by caller)
        if len(targets) == 0:
            return None
        for coord in targets:
            if not self.isValidCoord(coord):
                return False

        for i in range(0, len(targets)):
            #Nobody can place in the center two rows of the board or on their opponents side
                 
            #check item type
            if items[i].type == ANTHILL or items[i].type == TUNNEL or items[i].type == GRASS:
                #check targets[i] is within proper boundaries y-wise
                #must be on own side
                if not self.isInHomeTerritory(targets[i]):
                    return False
            #check item type
            elif items[i].type == FOOD:
                #check targets[i] is within proper boundaries y-wise
                #must be on opponent's side
                if not self.isInEnemyTerritory(targets[i]):
                    return False
            else:
                #I don't know what this type is.
                return False
            
            #change target to access appropriate players locations
            aTarget = self.state.coordLookup(targets[i], self.state.whoseTurn)
            #make sure nothing is there yet
            if not self.state.board[aTarget[0]][aTarget[1]].constr == None:
                return False
                    
        return True
      
    ##
    #isValidAttack
    #Description: Determines whether the attack with the given parameters is valid
    #   Attacking ant is assured to exist and belong to the player whose turn it is
    #
    #Parameters:
    #   attackingAnt - The Ant that is attacking (Ant)
    #   attackCoord - The coordinates of the Ant that is being attacked ((int,int))
    #
    #Returns: None if there is no attackCoord, true if valid attack, or false if invalid attack
    ##  
    def isValidAttack(self, attackingAnt, attackCoord):
        if attackCoord == None:
            return None
        
        #check for well-formed input from players
        if not self.isValidCoord(attackCoord):
            return False
    
        attackLoc = self.state.board[attackCoord[0]][attackCoord[1]]
        
        if attackLoc.ant == None or attackLoc.ant.player == attackingAnt.player:
            return False
        
        #we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])
        
        #pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            #return True if within range
            return True
        else:
            return False
   
    ##
    #isValidCoord
    #Description: Retruns whether this coord represents a valid board location. 
    #
    #Parameters:
    #   coord - The coord to be checked trying to be checked ((int, int))
    #
    #Returns: True if the coordinate is between (0,0) and (9,9)
    ##
    def isValidCoord(self, coord):
        #check for well-formed coord
        if type(coord) != tuple or len(coord) != 2 or type(coord[0]) != int or type(coord[1]) != int:
            return False
        
        #check boundaries
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
    #checkMoveStart 
    #Description: Checks if the location is valid to move from.
    #  (bounds and ant ownership)
    #
    #Parameters:
    #   coord - The starting point for the move ((int, int))
    #
    #Returns: True if it is a valid starting point for a move and false if not
    ##
    def checkMoveStart(self, coord):
        #check location is on board
        if self.isValidCoord(coord):
            antToMove = self.state.board[coord[0]][coord[1]].ant
            #check that an ant exists at the loc
            if antToMove != None:
                #check that it's the player's ant and that it hasn't moved
                if antToMove.player == self.state.whoseTurn and not antToMove.hasMoved:
                    return True
                                      
        return False

    ##
    #checkMovePath
    #Description: Checks if the location is valid to move to.
    #  (clear path, adjacent locations) 
    #
    #Parameters:
    #   fromCoord - The Ant's current coordinate ((int, int))
    #   toCoord - The coorinate to move the Ant to ((int, int))
    #
    #Returns: True if it is a valid move and false otherwise
    #
    #Note: fromCoord must always have been checked by the time it's passed
    #  (either in checkMoveStart or previous checkMovePath call)
    ##
    def checkMovePath(self, fromCoord, toCoord):
        #check location is on board
        if self.isValidCoord(toCoord):
            #check that squares are adjacent (difference on only one axis is 1)
            if ((abs(fromCoord[0] - toCoord[0]) == 1 and abs(fromCoord[1] - toCoord[1]) == 0) or
                    (abs(fromCoord[0] - toCoord[0]) == 0 and abs(fromCoord[1] - toCoord[1]) == 1)):
                antAtLoc = self.state.board[toCoord[0]][toCoord[1]].ant
                #check if an ant exists at the loc
                if antAtLoc ==  None:
                    return True
                    
        return False

    ##
    #checkBuildStart 
    #Description: Checks if the location is valid to build from.
    #  (bounds and building ownership)
    #
    #Parameters:
    #   coord - The coordinate trying to be used to build ((int, int))
    #
    #Returns: True if it is a valid build location and false otherwise
    ##    
    def checkBuildStart(self, coord):
        #check location is on board
        if self.isValidCoord(coord):
            loc = self.state.board[coord[0]][coord[1]]
            #check that an empty anthill exists at the loc
            if loc.constr != None and loc.constr.type == ANTHILL and loc.ant == None:
                #check that it's the player's anthill
                if loc.constr.player == self.state.whoseTurn:
                    return True
            #check that an ant exists at an empty location
            elif loc.ant != None and loc.ant.type == WORKER and loc.constr == None:       
                #check that it's the player's ant and it hasn't moved
                if loc.ant.player == self.state.whoseTurn and not loc.ant.hasMoved:
                    return True
                    
        return False
    
    ##
    #highlightValidMoves
    #Description: Highlights valid possible moves for the player when an ant is selected
    #
    #Parameters:
    #   coord - The coordinate of the starting ant ((int, int))
    ##
    def highlightValidMoves(self, antCoord):
        #create a list of 2 element tuples: (coord, path cost)
        adjacentCoords = {antCoord:0}
        ant = self.state.board[antCoord[0]][antCoord[1]].ant
        movement = UNIT_STATS[ant.type][MOVEMENT]
        for i in range(0, movement):
            tempCoords = {}
            for coord in adjacentCoords:
                for inc in [(0, -1), (0, 1), (-1, 0) ,(1, 0)]:
                    newCoord = addCoords(coord, inc)
                    if not self.isValidCoord(newCoord):
                        continue
                    construction = self.state.board[newCoord[0]][newCoord[1]].constr
                    pathCost = adjacentCoords[coord] + (2 if construction and construction.type == GRASS else 1)
                    if newCoord in adjacentCoords and adjacentCoords[newCoord] > pathCost:
                        continue
                    elif newCoord in tempCoords and tempCoords[newCoord] > pathCost:
                        continue
                    elif pathCost > movement:
                        continue
                    else:
                        #If this is either previously unseen, or cheaper than previously seen, add it to adjacentCoords/
                        tempCoords[newCoord] = pathCost
            #Finally, add new coords to adjacentCoords, or update costs of perviously examined coords.
            for coord in tempCoords:
                if coord not in adjacentCoords:
                    adjacentCoords[coord] = tempCoords[coord]
                elif coord in adjacentCoords and adjacentCoords[coord] > tempCoords[coord]:
                    adjacentCoords[coord] = tempCoords[coord]
        for key in adjacentCoords:
            self.ui.validCoordList.append(key)
        self.ui.validCoordList.remove(antCoord)

    
    ##
    #hasWon(int)
    #Description: Determines whether the game has ended in victory for the given player.
    #
    #Parameters:
    #   playerId - The ID of the player being checked for winning (int)
    #   
    #Returns: True if the player with playerId has won the game.
    ##
    def hasWon(self, playerId):
        opponentId = (playerId + 1) % 2
        
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
    #pauseForAIMode
    #Description: Will pause the game if set to AI mode until user clicks next or continue
    #
    ##    
    def pauseForAIMode(self):
        if self.mode == AI_MODE:
            while not self.nextClicked and not self.continueClicked:
                self.ui.drawBoard(self.state, self.mode)
                if self.state.phase == MENU_PHASE:
                    #if we are in menu phase at this point, a reset was requested so we need to break the game loop.
                    return
            #reset nextClicked to catch next move
            self.nextClicked = False

    ##
    # printTournament
    # Description: prints the status of the tournament
    #
    ##
    def printTournament(self):
        columns = ['AI', 'Wins', 'Losses']
        row_format ="{:>15}" * (len(columns))
        print row_format.format(*columns)
        for row in self.playerScores:
            print row_format.format(*row)
    
    ##
    #error
    #Description: Called when an AI player makes an error. Gives a description
    #    of what went wrong and exits the program.
    #
    #Parameters:
    #   errorCode - A code indicating the type of error
    #        info - the offending object that caused the error
    ##
    def error(self, errorCode, info):
        errorMsg = "AI ERROR: "

        if errorCode == INVALID_PLACEMENT:
            #info is a coord list
            errorMsg += "invalid placement\nCoords given: "
            lastCoord = info.pop()
            for coord in info:
                errorMsg += "(" + str(coord[0]) + ", " + str(coord[1]) + "), "
            errorMsg += "(" + str(lastCoord[0]) + ", " + str(lastCoord[1]) + ")"

        elif errorCode == INVALID_MOVE:
            #info is a move
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

        else: #INVALID_ATTACK
            #info is a coord          
            errorMsg += "invalid attack\n"
            errorMsg += "(" + str(info[0]) + ", " + str(info[1]) + ")"
    
        print errorMsg
        self.setWinner((self.state.whoseTurn + 1) % 2)

    ############################################################# 
    #####  #####  #      #      ####   #####  #####  #   #  #####
    #      #   #  #      #      #   #  #   #  #      #  #   #
    #      #####  #      #      ####   #####  #      ###    #####
    #      #   #  #      #      #   #  #   #  #      #  #       #
    #####  #   #  #####  #####  ####   #   #  #####  #   #  #####  
    #############################################################
    
    ##
    #startGameCallback
    #Description: Starts a new game. Called when start game button is clicked.
    #
    ##
    def startGameCallback(self):
        #Notice if the user hits this button in mid-game so we can reset (below)
        reset = False
        if self.state.phase == PLAY_PHASE:
            reset = True
        
        #save the mode
        currMode = self.mode
        #reset the game
        self.initGame()
        #restore the mode
        self.mode = currMode

        #if we are resetting, set the phase to MENU_PHASE with no mode
        if reset:
            self.state.phase = MENU_PHASE
            self.mode = None
        
        if self.mode == None:
            self.ui.notify("Please select a mode.")
            return
        
        if self.ui.choosingAIs:
            self.ui.notify("Please submit AIs to play game.")
            return

        if self.state.phase == MENU_PHASE:     
            #set up stuff for tournament mode
            if self.mode == TOURNAMENT_MODE:
                #reset tournament variables
                self.playerScores = [] # [[author,wins,losses], ...]
                self.gamesToPlay = [] #((p1.id, p2.id), numGames)
                self.numGames = None
                #notify UI tournament has started
                self.ui.tournamentStartTime = time.clock()
                self.ui.tournamentInProgress = True
    
                if self.ui.textBoxContent != '':
                    self.numGames = int(self.ui.textBoxContent)
                else:
                    self.ui.textBoxContent = '0'
                    self.numGames = 0
            
                #if numGames is non-positive, dont set up game
                if self.numGames <= 0:
                    return
                
                self.ui.tournamentScores = []
                
                for i in range(0, len(self.players)):
                    #initialize the player's win/loss scores
                    tempAuth = self.players[i][0].author
                    #If the length of the author's name is longer than 24 characters, truncate it to 24 characters
                    if len(tempAuth) > 20:
                        tempAuth = tempAuth[0:21] + "..."
                    
                    self.playerScores.append([tempAuth, 0, 0])
                    self.ui.tournamentScores.append([tempAuth, 0, 0])
                    
                    for j in range(i, len(self.players)):
                        if self.players[i][0] != self.players[j][0]:
                            self.gamesToPlay.append([(self.players[i][0].playerId, self.players[j][0].playerId), None])
                            
                numPairings = len(self.gamesToPlay)
                for i in range(0, numPairings):
                    #assign equal number of games to each pairing (rounds down)
                    self.gamesToPlay[i][1] = self.numGames

                # print that The tournament has Started
                print "Tournament Starting..."

            #Make a temporary list to append to so that we may check how many AIs we have available.
            tempCurrent = []
             
            #Load the first two active players (idx 0 is human player)
            for index in range(0, len(self.players)):
                tempCurrent.append(self.players[index][0])
                for playerEntry in self.players[index + 1:]:
                    tempCurrent.append(playerEntry[0])
                    break
                break

            self.currentPlayers = tempCurrent
                 
            #change the phase to setup
            self.state.phase = SETUP_PHASE_1
            
    ##
    #tourneyPathCallback
    #Description: Responds to a user clicking on the Tournament button
    #
    ##
    def tourneyPathCallback(self):
        #Reset the game
        self.initGame()
        self.initUI()
        #Reset tournament mode variables
        self.playerScores = []
        self.gamesToPlay = []
        self.numGames = None
        #Attempt to load the AI files
        self.loadAIs(False)
        #Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            self.ui.choosingAIs = True
            self.mode = TOURNAMENT_MODE
            self.ui.notify("Mode set to Tournament. Submit two or more AI players.")
        else:
            self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True
    
    ##
    #humanPathCallback
    #Description: Responds to a user clicking on the Human vs. AI button
    #
    ##
    def humanPathCallback(self):
        #Reset the game and UI
        self.initGame()
        self.initUI()
        #Attempt to load the AI files
        self.loadAIs(True) 
        #Add the human player to the player list
        self.players.insert(PLAYER_ONE, (HumanPlayer.HumanPlayer(PLAYER_ONE), ACTIVE))
        #Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            self.ui.choosingAIs = True
            self.mode = HUMAN_MODE
            self.ui.notify("Mode set to Human vs. AI. Submit one AI.")
        else:
            self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True
    
    ##
    #aiPathCallback
    #Description: Responds to a user clicking on the AI vs. AI button
    #
    ##
    def aiPathCallback(self):
        #Reset the game
        self.initGame()
        self.initUI()
        #Attempt to load the AI files
        self.loadAIs(False)
        #Check right number of players, if successful set the mode.
        if len(self.players) >= 2:
            self.ui.choosingAIs = True
            self.mode = AI_MODE
            self.ui.notify("Mode set to AI vs. AI. Submit two AIs.")    
        else:
            self.ui.notify("Could not load enough AI players for game type.")
            self.errorNotify = True
     
    ##
    #locationClickedCallback
    #Description: Responds to a user clicking on a board location
    #
    #Parameters:
    #   coord - The coordinate clicked ((int, int))
    #
    ##
    def locationClickedCallback(self, coord):
        #Check if its human player's turn during play phase
        if self.state.phase == PLAY_PHASE and type(self.currentPlayers[self.state.whoseTurn]) is HumanPlayer.HumanPlayer:
            currentPlayer = self.currentPlayers[self.state.whoseTurn]
            
            #determine if the coord is on the list
            onList = True if coord in currentPlayer.coordList else False
            index = currentPlayer.coordList.index(coord) if onList else None
         
            if len(currentPlayer.coordList) == 0:
                #clicked when nothing selected yet (select ant or building)
                
                #add location to human player's movelist if appropriate 
                if self.checkMoveStart(coord):
                    currentPlayer.coordList.append(coord)
                    self.highlightValidMoves(coord)
                elif self.checkBuildStart(coord) or self.expectingAttack:
                    currentPlayer.coordList.append(coord)
                self.errorNotify = False
            #clicked most recently added location (unselect building or submit ant move)
            elif coord == currentPlayer.coordList[-1]:
                if not self.ui.buildAntMenu:
                    startCoord = currentPlayer.coordList[0]
                    if self.state.board[startCoord[0]][startCoord[1]].ant == None:
                        currentPlayer.coordList.pop()
                    else:
                        currentPlayer.moveType = MOVE_ANT
                        self.ui.validCoordList = []
                    #clear notifications
                    self.errorNotify = False
            #player clicked off the path    
            else:
                if not onList:            
                    startCoord = currentPlayer.coordList[0]
                    antToMove = self.state.board[startCoord[0]][startCoord[1]].ant
                    if self.ui.validCoordList.count(coord) != 0:
                        #coord is a valid move coord
                        if self.checkMovePath(currentPlayer.coordList[-1], coord): 
                            #add the coord to the move list so we can check if it makes a valid move
                            currentPlayer.coordList.append(coord)
                            
                            #enact the theoretical move
                            move = Move(MOVE_ANT, currentPlayer.coordList, antToMove.type)
                            
                            #if the move wasn't valid, remove added coord from move list              
                            if not self.isValidMove(move):
                                currentPlayer.coordList.pop()
                            else:
                                self.ui.validCoordList.remove(coord)
                                self.errorNotify = False
                    elif not self.ui.buildAntMenu:
                        #coord outside of valid radius
                        self.ui.validCoordList = []
                        currentPlayer.coordList = []
                else:
                    #player clicked a previous location, change move to it
                    numToRemove = len(currentPlayer.coordList) - (index + 1)
                    for i in range(0, numToRemove):
                        self.ui.validCoordList.append(currentPlayer.coordList.pop())
                            
            #give coordList to UI so it can hightlight the player's path
            if not self.expectingAttack:
                self.ui.coordList = currentPlayer.coordList       
                
        #Check if its human player's turn during set up phase
        elif ((self.state.phase == SETUP_PHASE_1 or self.state.phase == SETUP_PHASE_2) 
                and type(self.currentPlayers[self.state.whoseTurn]) is HumanPlayer.HumanPlayer):
            self.currentPlayers[self.state.whoseTurn].coordList.append(coord)
    
    ##
    #buildClickedCallback
    #Description: Responds to a user clicking on the build button
    #
    ##
    def buildClickedCallback(self):
        #Check if its human player's turn during play phase
        if (self.state.phase == PLAY_PHASE and type(self.currentPlayers[self.state.whoseTurn]) is 
                HumanPlayer.HumanPlayer and len(self.currentPlayers[self.state.whoseTurn].coordList) == 1):
            whoseTurn = self.state.whoseTurn
            currentPlayer = self.currentPlayers[whoseTurn]
            
            loc = self.state.board[currentPlayer.coordList[0][0]][currentPlayer.coordList[0][1]]
            #we know loc has to have an ant or constr at this point, so make sure it doesnt have both
            if loc.constr == None or loc.ant == None:
                if loc.constr == None:
                    #a tunnel is to be built
                    currentPlayer.buildType = TUNNEL
                elif loc.ant == None:
                    self.ui.buildAntMenu = True                    
                
                currentPlayer.moveType = BUILD
                self.ui.validCoordList = []

    ##
    #endClickedCallback
    #Description: Responds to a user clicking on the end button
    #
    ##
    def endClickedCallback(self):    
        #Check if its human player's turn during play phase
        if (self.state.phase == PLAY_PHASE and self.expectingAttack == False 
                and type(self.currentPlayers[self.state.whoseTurn]) is HumanPlayer.HumanPlayer):
            self.currentPlayers[self.state.whoseTurn].moveType = END
            self.ui.validCoordList = []
    
    ##
    #buildWorkerClickedCallback
    #Description: Responds to a user clicking on the Build Worker button
    #
    ##
    def buildWorkerCallback(self):
        whoseTurn = self.state.whoseTurn
        currentPlayer = self.currentPlayers[whoseTurn]
        
        self.ui.buildAntMenu = False
        currentPlayer.buildType = WORKER
    
    ##
    #buildDroneClickedCallback
    #Description: Responds to a user clicking on the Drone button
    #
    ##    
    def buildDroneCallback(self):
        whoseTurn = self.state.whoseTurn
        currentPlayer = self.currentPlayers[whoseTurn]
        
        self.ui.buildAntMenu = False
        currentPlayer.buildType = DRONE
    
    ##
    #buildSoldierClickedCallback
    #Description: Responds to a user clicking on the Soldier button
    #
    ##
    def buildDSoldierCallback(self):
        whoseTurn = self.state.whoseTurn
        currentPlayer = self.currentPlayers[whoseTurn]
        
        self.ui.buildAntMenu = False
        currentPlayer.buildType = SOLDIER
    
    ##
    #buildISoldierClickedCallback
    #Description: Responds to a user clicking on the R. Soldier button
    #
    ##
    def buildISoldierCallback(self):
        whoseTurn = self.state.whoseTurn
        currentPlayer = self.currentPlayers[whoseTurn]
        
        self.ui.buildAntMenu = False
        currentPlayer.buildType = R_SOLDIER  
    
    ##
    #buildNothinClickedCallback
    #Description: Responds to a user clicking on the None button
    #
    ##
    def buildNothingCallback(self):
        whoseTurn = self.state.whoseTurn
        currentPlayer = self.currentPlayers[whoseTurn]        
        self.ui.buildAntMenu = False
        currentPlayer.moveType = None      
        self.ui.coordList = []
        currentPlayer.coordList = []
    
    ##
    #nextClickedCallback
    #Description: Responds to a user clicking on the next button in AI vs AI mode
    #
    ##
    def nextClickedCallback(self):
        if self.state.phase != MENU_PHASE:
            self.nextClicked = True
    
    ##
    #continueClickedCallback
    #Description: Responds to a user clicking on the continue button in AI vs AI mode
    #
    ##
    def continueClickedCallback(self):
        if self.state.phase != MENU_PHASE:
            self.continueClicked = True
    
    ##
    #checkBoxClickedCallback
    #Description: Responds to a user clicking on a checkbox to select AIs
    #
    #Parameters:
    #   index - The index of the checkbox clicked on (int)
    ##
    def checkBoxClickedCallback(self, index):
        self.players[index][1] = ACTIVE if self.players[index][1] == INACTIVE else INACTIVE

    ##
    #submitClickedCallback
    #Description: Responds to a user clicking on the submit button when selecting AIs
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
        
        #check to see if we have enough checked players
        if (len(self.players) - len(inactivePlayers)) < 2:
            self.ui.notify("Please select more AIs to play this game type.")
            return
        if (len(self.players) - len(inactivePlayers)) > 23 and self.mode == TOURNAMENT_MODE:
            self.ui.notify("Please select less than 24 AI players to play this game type.")
            return
            
        
        #remove all inactive players
        for player in inactivePlayers:
            self.players.remove(player)
        
        if self.mode == HUMAN_MODE and len(self.players) > 2:
            self.ui.notify("Too many AIs selected. Using first from list.")
        elif self.mode == AI_MODE and len(self.players) > 2:
            self.ui.notify("Too many AIs selected. Using first two from list.")
        else:
            self.ui.notify("")
        self.ui.choosingAIs = False


#Import all the python files in the AI folder so they can be serialized
sys.path.insert(0, "AI")
for module in os.listdir("AI"):
    if module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module

if __name__ == '__main__':
    #Create the game
    a = Game()
    a.start()

    
