from Constants import *

#Unit stats array [ant type][stat]
#(movement, health, attack, range, cost)
UNIT_STATS = []
UNIT_STATS.append((2, 8, 2, 1, None)) #Queen
UNIT_STATS.append((2, 1, 1, 1, 1)) #Worker
UNIT_STATS.append((3, 2, 1, 1, 2)) #Drone 
UNIT_STATS.append((2, 4, 2, 1, 3)) #Soldier
UNIT_STATS.append((1, 1, 2, 3, 2)) #Ranged soldier

##
#Ant
#Description: This class represents an ant on the board. All information
#   pertaining to Ants that may be required by the game is stored in this
#   class.
#
# Variables:
#   coords - An int[] of length 2, representing the Ant's position on the
#       board.  Positions start at (0, 0) in the upper left and increase down
#       and to the right.
#   type - Ants come in all shapes and sizes. Type is an int that indexes into
#       an array of stats for various ant types.
#   alive - A boolean representing if the Ant's alive or not.
#   hasMoved - A boolean representing if the ant has moved yet this turn
#   carrying - A boolean representing if the Ant's carrying food or not.
#   player - The id of the player that owns the Ant
##
class Ant(object):
    
    ##
    #__init__
    #Description: Creates a new Ant
    #
    #Parameters:
    #   inputCoords - The position on the board to place the Ant at (int,int)
    #   inputType - The type of ant to create (int)
    #   inputPlayer - The id of the player that owns the Ant (int)
    ##
    def __init__(self, inputCoords, inputType, inputPlayer):
        self.coords = inputCoords
        self.type = inputType
        self.hasMoved = False
        self.carrying = False
        self.player = inputPlayer
        self.health = UNIT_STATS[self.type][HEALTH]

    def clone(self):
        rtnAnt = Ant(self.coords, self.type, self.player)
        rtnAnt.hasMoved = self.hasMoved
        rtnAnt.carrying = self.carrying
        rtnAnt.health = self.health
        return rtnAnt
