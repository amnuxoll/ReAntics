##
#Constants
#Description: This file contains all the named numeric "constants"
#for use in the aNTiCS project.
#
##

#Player IDs
PLAYER_ONE = 0
PLAYER_TWO = 1
NEUTRAL    = 2

#Length of the board (it's square)
BOARD_LENGTH = 10

#Game Phases
MENU_PHASE = 0
SETUP_PHASE_1 = 1
SETUP_PHASE_2 = 2
PLAY_PHASE = 3

#Game Modes
TOURNAMENT_MODE = 0
HUMAN_MODE = 1
AI_MODE = 2

#Amount of food require to win
FOOD_GOAL = 11

#Types of ants
QUEEN = 0
WORKER = 1
DRONE = 2
SOLDIER = 3
R_SOLDIER = 4

#Types of contructions
ANTHILL = -4
TUNNEL = -3
GRASS = -2
FOOD = -1

#Types of moves
MOVE_ANT = 0
BUILD = 1
END = 2
UNDO = 3

#Indices into unit stats
MOVEMENT = 0
HEALTH = 1
ATTACK = 2
RANGE = 3
COST = 4
IGNORES_GRASS = 5

#Indices into construction stats
MOVE_COST = 0
CAP_HEALTH = 1
BUILD_COST = 2

#Activity of AI players
INACTIVE = 0
ACTIVE = 1

#Error codes used by game
INVALID_PLACEMENT = 0
INVALID_MOVE = 1
INVALID_ATTACK = 2

#Max time (seconds) an AI is allowed to make a move
AI_MOVE_TIMEOUT = 30

#Player ID values
COPY = -2
HUMAN = -1

##
# moveTypeToStr
#
# returns a string the corresponds to a given move type
#
def moveTypeToStr(type):
    if (type == MOVE_ANT):
        return "MOVE_ANT"
    elif (type == BUILD):
        return "BUILD"
    elif (type == END):
        return "END"
    else:
        return "???"
    
##
# antTypeToStr
#
# returns a string the corresponds to a given ant type
#
def antTypeToStr(type):
    if (type == QUEEN):
        return "QUEEN"
    elif (type == WORKER):
        return "WORKER"
    elif (type == DRONE):
        return "DRONE"
    elif (type == SOLDIER):
        return "SOLDIER"
    elif (type == R_SOLDIER):
        return "RANGED"
    else:
        return "???"
    
##
# buildTypeToStr
#
# returns a string the corresponds to a given build type
#
def buildTypeToStr(type):
    if (type == TUNNEL):
        return "TUNNEL"
    else:
        return antTypeToStr(type)
    
    


    
