from Construction import *
from Constants import *
##
#Building
#Description: Represents any static object that can be placed on the board
#   aside from food.
#
#Variables:
#   type - int identifying the type of Building, which allows the game to
#       decide what to do with it.
#   player - int equal to the playerId of the player that owns this Building.
#   captureHealth - int representing the amount of damage this Building can
#       take before being captured.
##
class Building(Construction):

    ##
    #__init__
    #Description: Creates a new Building
    #
    #Parameters:
    #   inputCoords - The location to place the new Building (int[])
    #   inputPlayer - The playerId of the Player that owns the Building (int)
    ##
    def __init__(self,inputCoords, inputType, inputPlayer):
        super(Building,self).__init__(inputCoords, inputType)
        self.player = inputPlayer
        self.captureHealth = CONSTR_STATS[inputType][CAP_HEALTH]
    
    def clone(self):
        return Building(self.coords, self.type, self.player)
