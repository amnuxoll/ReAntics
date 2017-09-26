from Constants import *
from Player import *
from Move import *

##
#HumanPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state.
#
#Variables:
#   playerId - The id of the player.
#   moveType - the type of move that the player is currently wanting to make
#   buildType - the type of building that the player is currently wanting to make
#   coordList - the list of coordinates that correspond to a valid move
##
class HumanPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(HumanPlayer,self).__init__(inputPlayerId, "")
        self.moveType = None
        self.buildType = None
        self.coordList = []
        
    ##
    #getPlacement
    #Description: called during setup phase for each Construction that must be placed by the player.
    #   These items are: 1 Anthill on the player's side; 9 grass on the player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        if len(self.coordList) == 0:
            return []
        target = self.coordList[0]
        self.coordList = []
        return [target]
        
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
        coords = self.coordList
        chosenMove = None
        
        #check if no move has been submitted first
        if self.moveType == None:
            return None
        
        #callbacks have made sure coord list 
        #wasn't empty if we got to this point
        
        #create the appropriate move
        if self.moveType == MOVE_ANT:
            chosenMove = Move(MOVE_ANT, coords, None)
        elif self.moveType == BUILD:
            if self.buildType == None: 
                return None
            #callbacks have checked to make sure coord list is length 1
            loc = currentState.board[coords[0][0]][coords[0][1]]
           
            #we also know from callback that loc contains ant OR hill, not both
            chosenMove = Move(BUILD, coords, self.buildType)
            
        elif self.moveType == END:
            chosenMove = Move(END, None, None)
        else:
            #bad move type
            pass
        
        #clear out move type and coord list
        self.moveType = None
        self.buildType = None
        self.coordList = []
        
        return chosenMove
    
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
        if self.coordList == []:
            return None
        else:
            return self.coordList[0]
        