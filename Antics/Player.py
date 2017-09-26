##
#Player
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class is abstract and
#should not be instantiated.
#
#Variables:
#   playerId - The id of the player.
##
class Player(object):

    ##
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId, inputAuthor):
        self.playerId = inputPlayerId
        self.author = inputAuthor
    
    ##
    #getPlacement
    #Description: called during setup phase for each Construction that must be placed by the player.
    #   These items are: 1 Anthill on the player's side; 9 grass on the player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        #method template, not implemented
        pass
    
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
        #method template, not implemented
        pass
    
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
        #method template, not implemented
        pass
        
    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
