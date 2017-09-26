from Constants import *

##
#Move
#Description: This class represents any valid move that can be made during Antics gameplay
#
#Variables:
#   moveType - This represents the type of move the player has made(moveAnt,build and endTurn)
#   coordList - The list of coordinates representing the path to take, does not include fromCoord
#   buildType - This identifies the type of a unit(only relevant to Moves of type build)
##
class Move(object):

    ##
    #__init__
    #Description: Creates a new Move
    #
    #Parameters:
    #   inputMoveType - The type of move the Player is making (int)
    #   inputCoordList - A list of coordinates representing the path to take (List<(int,int)>)
    #   inputBuildType - The type of unit being built (int)
    ##
    def __init__(self, inputMoveType, inputCoordList, inputBuildType):
        self.moveType = inputMoveType
        self.coordList = inputCoordList
        self.buildType = inputBuildType
    

    ##
    # try to print this object out in an easier-to-read manner
    def __str__(self):
        moveName = str(moveTypeToStr(self.moveType))
        buildName = str(buildTypeToStr(self.buildType))
        if (self.moveType != BUILD):
            buildName = ""
        coordStr = str(self.coordList)
        if (self.coordList == None):
            coordStr = ""
        
        return "<Move: " + moveName + " " + buildName + " " +  coordStr + ">"
