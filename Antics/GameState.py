import copy
from Constants import *
from Inventory import Inventory
from Building import Building
from Location import *

def addCoords(tuple1, tuple2):
    if len(tuple1) != len(tuple2):
        return None
    else:
        return tuple([tuple1[i] + tuple2[i] for i in range(0, len(tuple1))])

def subtractCoords(tuple1, tuple2):
    if len(tuple1) != len(tuple2):
        return None
    else:
        return tuple([tuple1[i] - tuple2[i] for i in range(0, len(tuple1))])

##
#GameState
#
#Description: The current state of the game.
#
#Variables:
#   board - The game Board being used.
#   inventories - A tuple containing the Inventory for each player.
#   phase - The current phase of the game.
#    whoseTurn - The ID of the Player who's turn it currently is.
##
class GameState(object):

    ##
    #__init__
    #Description: Creates a new GameState
    #
    #Parameters:
    #   inputBoard - The Board to be used by the GameState (Board)
    #   inputInventories - A tuple containing the Inventory for each player as
    #    well as a third inventory for grass and food: (Inventory, Inventory, Inventory)
    #   inputPhase - The phase of the game (int)
    #   inputTurn - The ID of the Player who's turn it is (int)
    ##
    def __init__(self, inputBoard, inputInventories, inputPhase, inputTurn):
        self.board = inputBoard
        self.inventories = inputInventories
        self.phase = inputPhase
        self.whoseTurn = inputTurn

    ##
    #coordLookup
    #Description: Returns the appropriate coordinates for the given
    #   player to allow both players to play from top of the board.
    #
    #Return: Correct coordinate location for player
    ##
    def coordLookup(self, coords, playerId):
        if coords == None or playerId == None:
            return None
    
        if playerId == PLAYER_ONE:
            return coords
        else:
            return (BOARD_LENGTH - 1 - coords[0], BOARD_LENGTH - 1 - coords[1])
    
    ##
    #flipBoard
    #Description: Flips the board (so Player Two sees self on top side)
    #
    ##
    def flipBoard(self):
        for col in self.board:
            col.reverse()
            
        self.board.reverse()
        
        for inv in self.inventories:
            for ant in inv.ants:
                ant.coords = self.coordLookup(ant.coords, PLAYER_TWO)
            for constr in inv.constrs:
                constr.coords = self.coordLookup(constr.coords, PLAYER_TWO)
      
    ##
    #clearConstrs
    #Description: Clears the board of all constructions (so Player Two doesn't see Player One's setup)
    #
    ##
    def clearConstrs(self):
        for col in self.board:
            for loc in col:
                loc.constr = None

    ##
    #clone
    #Description: Returns a deep copy of itself
    #
    #Return: The GameState identical to the original
    ##
    def clone(self):
        newBoard = []
        ants1 = []
        ants2 = []
        cons1 = []
        cons2 = []
        cons3 = []
        food1 = self.inventories[PLAYER_ONE].foodCount
        food2 = self.inventories[PLAYER_TWO].foodCount
        for col in xrange(0,len(self.board)):
            newBoard.append([])
            for row in xrange(0,len(self.board)):
                newLoc = self.board[col][row].clone()
                newBoard[col].append(newLoc)
                #Organize constructions into inventories
                if newLoc.constr != None and type(newLoc.constr) is Building and newLoc.constr.player == PLAYER_ONE:
                    cons1.append(newLoc.constr)
                elif newLoc.constr != None and type(newLoc.constr) is Building and newLoc.constr.player == PLAYER_TWO:
                    cons2.append(newLoc.constr)
                #Organize ants into inventories
                if newLoc.ant != None and newLoc.ant.player == PLAYER_ONE:
                    ants1.append(newLoc.ant)
                elif newLoc.ant != None and newLoc.ant.player == PLAYER_TWO:
                    ants2.append(newLoc.ant)
        for constr in self.inventories[NEUTRAL].constrs:
            cons3.append(constr.clone())
        newInventories = [Inventory(PLAYER_ONE, ants1, cons1, food1),
                          Inventory(PLAYER_TWO, ants2, cons2, food2),
                          Inventory(NEUTRAL, [], cons3, 0) ]
        return GameState(newBoard, newInventories, self.phase, self.whoseTurn)


    ##
    #fastclone
    #
    #Description: Returns a deep copy of itself *without* a board (which is set
    # to None).  Omitting the board makes the clone run much faster and, if
    # necessary, the board can be reconstructed from the inventories.
    #
    #Return: a GameState object _almost_ identical to the original
    ##
    def fastclone(self):
        newBoard = None
        #For speed, preallocate the lists at their eventual size 
        ants1 = [ None ] * len(self.inventories[PLAYER_ONE].ants)
        ants2 = [ None ] * len(self.inventories[PLAYER_TWO].ants)
        cons1 = [ None ] * len(self.inventories[PLAYER_ONE].constrs)
        cons2 = [ None ] * len(self.inventories[PLAYER_TWO].constrs)
        cons3 = [ None ] * len(self.inventories[NEUTRAL].constrs)
        antIndex1 = 0
        antIndex2 = 0
        conIndex1 = 0
        conIndex2 = 0
        conIndex3 = 0

        #clone all the entries in the inventories
        for ant in self.inventories[PLAYER_ONE].ants:
            ants1[antIndex1] = ant.clone()
            antIndex1 += 1
        for ant in self.inventories[PLAYER_TWO].ants:
            ants2[antIndex2] = ant.clone()
            antIndex2 += 1
        for constr in self.inventories[PLAYER_ONE].constrs:
            cons1[conIndex1] = constr.clone()
            conIndex1 += 1
        for constr in self.inventories[PLAYER_TWO].constrs:
            cons2[conIndex2] = constr.clone()
            conIndex2 += 1
        for constr in self.inventories[NEUTRAL].constrs:
            cons3[conIndex3] = constr.clone()
            conIndex3 += 1

        #clone the list of inventory objects
        food1 = self.inventories[PLAYER_ONE].foodCount
        food2 = self.inventories[PLAYER_TWO].foodCount
        newInventories = [ Inventory(PLAYER_ONE, ants1, cons1, food1),
                           Inventory(PLAYER_TWO, ants2, cons2, food2),
                           Inventory(NEUTRAL, [], cons3, 0) ]
        
        return GameState(newBoard, newInventories, self.phase, self.whoseTurn)
