from Constants import *

##
#Inventory
#Description: This class keeps track of the resources at a player's disposal
#
#Variables
#   player - The id of the player that this inventory belongs to
#   ants - The ants belonging to the player
#    queen - The Player's queen Ant
#    anthill - The player's anthill
#    constrs - An array of all the Player's Constructions
#   foodCount - The amount of food that the player has to use
##
class Inventory(object):

    ##
    #__init__
    #Description: Creates a new Inventory
    #Parameters:
    #   playerId - The id of the player that owns the Inventory (int)
    #   antArray - An array containing the Player's Ants (Ant[])
    #   inputFood - The amount of food in the Inventory (int)
    #   inputConstructions - An array containing all of the Player's Constructions (Construction[])
    ##
    def __init__(self, playerId, antArray, inputConstructions, inputFood):
        self.player = playerId
        self.ants = antArray
        self.constrs = inputConstructions      
        self.foodCount = inputFood
        
    ##
    # return the queen in this inventory
    def getQueen(self):
        if self.ants == None:
            return None
        for checkAnt in self.ants:
            if checkAnt.type == QUEEN: return checkAnt
            
        return None

    ##
    # return the anthill in this inventory
    def getAnthill(self):
        if self.constrs == None:
            return None
        
        for checkConstruction in self.constrs:
            if checkConstruction.type == ANTHILL: return checkConstruction
        
        return None

    ## 
    # construct a list of all the tunnels in this inventory
    def getTunnels(self):
        if self.constrs == None:
            return []

        result = []
        for checkConstruction in self.constrs:
            if checkConstruction.type == TUNNEL:
                result.append(checkConstruction)
        
        return result
        

    ##
    # duplicate this inventory
    def clone(self):
        return Inventory(self.player,self.ants,self.constrs,self.foodCount)
