import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "ErrorHandlingStressTest")
        self.runsTried = 0
    
    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        if self.runsTried <= 1000:
            if currentState.phase == SETUP_PHASE_1:  # stuff on my side
                numToPlace = 11
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(10, 20)
                        # Choose any y location on your side of the board
                        y = random.randint(4, 7)
                        # Set the move if this space is empty
                        if (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                    moves.append(move)
                self.runsTried += 1
                return moves
            elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
                numToPlace = 2
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(0, 9)
                        # Choose any y location on enemy side of the board
                        y = random.randint(6, 9)
                        # Set the move if this space is empty
                        if currentState.board[x][y].constr == None and (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                            currentState.board[x][y].constr = True
                    moves.append(move)
                self.runsTried += 1
                return moves
            else:
                self.runsTried += 1
                return [(0, 0)]
        elif 1000 < self.runsTried <= 2000:
            if currentState.phase == SETUP_PHASE_1:  # stuff on my side
                numToPlace = 11
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(0, 9)
                        # Choose any y location on your side of the board
                        y = random.randint(0, 3)
                        # Set the move if this space is empty
                        if currentState.board[x][y].constr == None and (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                            currentState.board[x][y].constr = True
                    moves.append(move)
                self.runsTried += 1
                return moves
            elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
                numToPlace = 2
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(10, 20)
                        # Choose any y location on enemy side of the board
                        y = random.randint(10, 14)
                        # Set the move if this space is empty
                        if (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                    moves.append(move)
                self.runsTried += 1
                return moves
            else:
                self.runsTried += 1
                return [(0, 0)]
        else:
            if currentState.phase == SETUP_PHASE_1:  # stuff on my side
                numToPlace = 11
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(0, 9)
                        # Choose any y location on your side of the board
                        y = random.randint(0, 3)
                        # Set the move if this space is empty
                        if currentState.board[x][y].constr == None and (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                            currentState.board[x][y].constr = True
                    moves.append(move)
                self.runsTried += 1
                return moves
            elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
                numToPlace = 2
                moves = []
                for i in range(0, numToPlace):
                    move = None
                    while move == None:
                        # Choose any x location
                        x = random.randint(0, 9)
                        # Choose any y location on enemy side of the board
                        y = random.randint(6, 9)
                        # Set the move if this space is empty
                        if currentState.board[x][y].constr == None and (x, y) not in moves:
                            move = (x, y)
                            # Just need to make the space non-empty. So I threw whatever I felt like in there.
                            currentState.board[x][y].constr = True
                    moves.append(move)
                self.runsTried += 1
                return moves
            else:
                self.runsTried += 1
                return [(0, 0)]

    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
            
        return Move(MOVE_ANT, [(11, 21), (12, 21), (13, 21), (14, 21), (15, 21)], None)
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
