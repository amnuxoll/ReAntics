import random
from Constants import *
from Ant import *
from Construction import *
from Move import *

#
# AIPlayerUtils.py
#
# a set of methods that are likely to be handy for all kinds of AI
# players.
#
# Important Note:  All the methods in this file that take a GameState object
# will not attempt to access the 'board' member of the at object.  This makes
# these routines safe for a GameState that has been generated via the
# GameState.fastclone method.
#

##
# legalCoord
#
# determines whether a given coordinate is legal or not
#
#Parameters:
#   coord        - an x,y coordinate
#
# Return: true (legal) or false (illegal)
def legalCoord(coord):

    #make sure we have a tuple or list with two elements in it
    try:
        if len(coord) != 2:
            return False
    except TypeError:
        print("ERROR:  parameter to legalCoord was not a tuple or list")
        return False

    x = coord[0]
    y = coord[1]
    return ( (x >= 0) and (x <= 9) and (y >= 0) and (y <= 9))


##
# getAntList()
#
# builds a list of all ants that meet a given specification
#
# Parameters:
#     currentState - a GameState or Node
#     pid   - all ants must belong to this player id.  Pass None to
#             indicate any player
#     types - a tuple of all the ant types wanted (see Constants.py)
#
def getAntList(currentState,
               pid = None,
               types = (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)):

    #start with a list of all ants that belong to the indicated player(s)
    allAnts = []
    for inv in currentState.inventories:
        if (pid == None) or (pid == inv.player):
            allAnts += inv.ants

    #fill the result with ants that are of the right type
    result = []
    for ant in allAnts:
        if ant.type in types:
            result.append(ant)

    return result


##
# getConstrList()
#
# builds a list of all constructs that meet a given specification.
#
# Caveat:  if you pass a GameState for the first parameter, food and grass will
# not be returned.
#
# Parameters:
#     currentState - a GameState or Node
#     pid   - all ants must belong to this player id.  Pass None to
#             indicate any player including unowned constructs like grass/food
#     types - a tuple of all the constr types wanted (see Constants.py)
#
def getConstrList(currentState,
                  pid = None,
                  types = (ANTHILL, TUNNEL, GRASS, FOOD)):

    #start with a list of all constrs that belong to the indicated player(s)
    allConstrs = []
    for inv in currentState.inventories:
        if (pid == None) or (pid == inv.player):
            allConstrs += inv.constrs

    #fill the result with constrs that are of the right type
    result = []
    for constr in allConstrs:
        if constr.type in types:
            result.append(constr)

    return result


##
# getConstrAt
#
# determines which construct is at a given coordinate
#
# Parameters:
#    state  - a valid GameState object
#    coords - a valid coordinate (code does not check for invalid!)
#
# Return:  the construct at the coordinate or None if there is none
def getConstrAt(state, coords):
    #get a list of all constructs
    allConstrs = getConstrList(state)

    #search for one at the given coord
    for constr in allConstrs:
        if constr.coords == coords:
            return constr

    return None  #not found


##
# getAntAt
#
# determines which ant is at a given coordinate
#
# Parameters:
#    state  - a valid GameState object
#    coords - a valid coordinate (code does not check for invalid!)
#
# Return:  the ant at the coordinate or None if there is none
def getAntAt(state, coords) -> Ant:
    #get a list of all constructs
    allAnts = getAntList(state)

    #search for one at the given coord
    for ant in allAnts:
        if ant.coords == coords:
            return ant

    return None  #not found


##
# getWinner
#
# Parameters:
#       currentState: a gameState of the current state of the game
#
# Return:
#       1  - (int) the player of the current turn has won
#       0  - (int) the opponent of the player of the current turn has won
#    None  - (null) no player has won
#
def getWinner(currentState):
    myId = currentState.whoseTurn
    enemyId = 1 - myId

    myInv = currentState.inventories[myId]
    enemyInv = currentState.inventories[enemyId]

    myQueen = myInv.getQueen()
    myAntHill = myInv.getAnthill()
    myFoodCount = myInv.foodCount

    enemyQueen = enemyInv.getQueen()
    enemyAntHill = enemyInv.getAnthill()
    enemyFoodCount = enemyInv.foodCount

    if enemyAntHill.captureHealth <= 0 or myFoodCount >= FOOD_GOAL or enemyQueen is None or (enemyFoodCount == 0 and len(enemyInv.ants) == 1):
        return 1

    if myAntHill.captureHealth <= 0 or enemyFoodCount >= FOOD_GOAL or myQueen is None or (myFoodCount == 0 and len(myInv.ants) == 1):
        return 0

    return None


##
# listAdjacent
#
# Parameters:
#     coord    - a tuple containing a valid x,y coordinate
#
# Return: a list of all legal coords that are adjacent to the given space
#
def listAdjacent(coord):
    #catch invalid inputs
    if not legalCoord(coord):
        return []

    #this set of coord deltas represent movement in each cardinal direction
    deltas = [ (-1, 0), (1, 0), (0, -1), (0, 1) ]
    x = coord[0]
    y = coord[1]
    result = []

    #calculate the cost after making each move
    for delta in deltas:
        newX = delta[0] + coord[0]
        newY = delta[1] + coord[1]

        #skip illegal moves
        if legalCoord((newX, newY)):
            result.append((newX, newY))

    return result

##
# listAttackable
#
# lists the attackable coordinates from a start coordinate and attack range
# coordinates from a taxicab square around start
#
# coord - the coordinate of the attacking ant
# dist - the attack range of the attacking ant
def listAttackable(coord, dist = 1):
    res = []

    # goes L-R across board, offset by 1 for range()
    for i in range(-dist, dist + 1):
        # get allowed y variance given x variance
        # offset by 1 for range()
        yLen = dist - abs(i)
        for j in range(-yLen, yLen + 1):
            newCord = (coord[0] + i, coord[1] + j)
            if legalCoord(newCord) and newCord != coord:
                res.append(newCord)

    return res




##
# listReachableAdjacent
#
# calculates all the adjacent cells that can be reached from a given coord.
#
# Parameters:
#    state        - a GameState object
#    coords       - where the ant is
#    movement     - movement points the ant has
#
# Return:  a list of coords (tuples)
def listReachableAdjacent(state, coords, movement, ignoresGrass = False):
    #build a list of all adjacent cells
    oneStep = listAdjacent(coords)

    #winnow the list based upon cell contents and cost to reach
    candMoves = []
    for cell in oneStep:
        ant = getAntAt(state, cell)
        constr = getConstrAt(state, cell)
        moveCost = 1  #default cost
        if constr != None and not ignoresGrass:
            moveCost = CONSTR_STATS[constr.type][MOVE_COST]
        if (ant == None) and (moveCost <= movement):
            candMoves.append(cell)

    return candMoves

##
# listAllMovementPaths              <!-- RECURSIVE -->
#
# calculates all the legal paths for a single ant to move from a given position.
# The ant doesn't actually have to be there for this method to return a valid
# answer.  This method does not take queen ant movement restrictions
# into account.
#
# Parameters:
#    currentState - current game state
#    coords       - where the ant is
#    movement     - movement points ant has remaining
#
# Return: a list of lists of coords (tuples). Each sub-list of tuples is an
# acceptable set of coords for a Move object
# TODO: I think this method could be sped up to improve computation time
def listAllMovementPaths(currentState, coords, movement, ignoresGrass = False):
    #base case: ant can't move any further
    if (movement <= 0): return []

    #construct a list of all valid one-step moves
    adjCells = listReachableAdjacent(currentState, coords, movement, ignoresGrass)
    oneStepMoves = []
    for cell in adjCells:
        oneStepMoves.append([coords, cell])

    #add those as valid moves
    validMoves = list(oneStepMoves)

    #recurse for each adj cell to see if we can take additional steps
    for move in oneStepMoves:
        #figure out what it would cost to get to the current dest
        moveCoords = move[-1]
        constrAtDest = getConstrAt(currentState, moveCoords)
        cost = 1   #default
        if constrAtDest != None and not ignoresGrass:
            cost = CONSTR_STATS[constrAtDest.type][MOVE_COST]

        #get a list of all moves that will extend this one
        extensions = listAllMovementPaths(currentState, moveCoords, movement - cost, ignoresGrass)

        #create new moves by adding each extension to the base move
        for ext in extensions:
            newMove = list(move)      #create a clone
            for cell in ext[1:]:      #start at index '1' to skip overlap
                newMove.append(cell)
            validMoves.append(newMove)

    #Append the zero-step move (used to activate attack on adjacent foe)
    validMoves.append([coords])

    return validMoves


##
# stepsToReach
#
# calculates the shortest distance between two cells taking
# movement costs into account.
#
#Parameters:
#   currentState   - The state of the game (GameState)
#   src            - starting position (an x,y coord)
#   dst            - destination position (an x,y coord)
#
# Return: the costs in steps (an integer) or -1 on invalid input
def stepsToReach(currentState, src, dst):
    #check for invalid input
    if (not legalCoord(src)): return -1
    if (not legalCoord(dst)): return -1

    #a dictionary of already visted cells and the corresponding cost to reach
    visited = { src : 0 }
    #a list of to be processed cells
    queue = [ src ]

    #this loops processes cells in the queue until it is empty
    while(len(queue) > 0):
        cell = queue.pop(0)

        #if this cell is our destination we are done
        if (cell == dst):
            return visited[cell]

        #calc distance to all cells adj to this one assuming we reach them
        #from this one
        nextSteps = listAdjacent(cell)
        for newCell in nextSteps:
            constrAtDest = getConstrAt(currentState, newCell)
            cost = 1  #default
            if constrAtDest != None:
                cost = CONSTR_STATS[constrAtDest.type][MOVE_COST]
            dist = visited[cell] + cost

            #if the new distance is best so far, update the visited dict
            if (newCell in visited):
                if (dist < visited[newCell]):
                    visited[newCell] = dist
            #if we've never seen this cell before also update dict and
            #enqueue this new cell to be processed at a future loop iteration
            else:
                visited[newCell] = dist
                queue.append(newCell)

    #we should never reach this point
    return -1


##
# approxDist
#
# gives an approximate distance between two cells.  This method is much faster
# than stepsToReach but does not take grass and other ants into account
#
#Parameters:
#   sourceCoords - starting position (an x,y coord)
#   targetCoords - destination position (an x,y coord)
#
# Return: the approximate distance (an integer)
def approxDist(sourceCoords, targetCoords):
    return abs(sourceCoords[0]-targetCoords[0]) + abs(sourceCoords[1]-targetCoords[1])


##
# createPathToward
#
# creates a legal path toward a destination.  This method does not verify that
# the path is okay for a queen.
#
# Parameters:
#   currentState - currentState of the game
#   sourceCoords - starting position (an x,y coord)
#   targetCoords - destination position (an x,y coord)
#   movement     - movement points to spend
#
# Return the required path
#
def createPathToward(currentState, sourceCoords, targetCoords, movement):
    ant = getAntAt(currentState, sourceCoords)
    # paths may be requested with no ant for planning purposes
    if ant is None:
        ignoresGrass = False
    else:
        ignoresGrass = UNIT_STATS[ant.type][IGNORES_GRASS]
    return findPathRecursive(currentState, sourceCoords, targetCoords, movement, ignoresGrass)[0]


##
# findPathRecursive
#
# finds the best path from a given source, target, and movement and returns it and the end distance to target
# To save on computation time, this path is not necessarily optimal if there's not enough movement to reach the target.
# In most cases it will still be optimal.
#
# state - the state to find the path in: GameState
# source - the start location of the path: (x: int, y: int)
# target - the target location for the path: (x: int, y:int)
# movement - amount of movement left to spend on path: int
# ignoresGrass - if the path should respect grass movement penalty: bool
#
def findPathRecursive(state, source, target, movement, ignoresGrass):
    dist = approxDist(source, target)
    if dist == 0:
        return ([source], 0)
    if movement == 0:
        return ([source], dist)

    bestPath = ([source], dist)
    for coord in listReachableAdjacent(state, source, movement, ignoresGrass):
        # find movement cost to go here
        cost = 1
        if not ignoresGrass:
            const = getConstrAt(state, coord)
            if const is not None:
                cost = const.movementCost

        # find best path
        path = findPathRecursive(state, coord, target, movement - cost, ignoresGrass)

        # if this path is better than we've found, use it
        if path[1] < bestPath[1]:
            bestPath = ([source] + path[0], path[1])
            # computation time decrease
            if bestPath[1] == 0 or bestPath[1] == dist - movement:
                return bestPath
    return bestPath


##
# listAllBuildMoves
#
# calcualtes all the legal BUILD moves that the current player can
# make
#
# Parameters
#   currentState - currentState of the game
#
# Returns: a list of Move objects
def listAllBuildMoves(currentState):
    result = []

    #if the anthill is unoccupied list a BUILD move for each ant
    #that there is enough food to build
    myInv = getCurrPlayerInventory(currentState)
    hill = myInv.getAnthill()
    if (getAntAt(currentState, hill.coords)  == None):
        for type in range(1, len(UNIT_STATS)):
            cost = UNIT_STATS[type][COST]
            if (cost <= myInv.foodCount):
                result.append(Move(BUILD, [hill.coords], type))

    return result

##
# isPathOkForQueen
#
# determines if a given path would move the ant outside of the home
# territory.  The caller is responsible for providing a legal path.
# This is a helper method for listAllMovementMoves
#
#Parameters:
#   path - the path to check
#
# Return: True if the is okay
#
def isPathOkForQueen(path):
    for coord in path:
        if (coord[1] == BOARD_LENGTH / 2 - 1) \
        or (coord[1] == BOARD_LENGTH / 2):
            return False
    return True

##
# listAllMovementMoves
#
# calculates all valid MOVE_ANT moves for the current player in a
# given GameState
#
# Parameters:
#   currentState - the current state
#
# Returns:  a list of Move objects
def listAllMovementMoves(currentState):
    result = []

    #first get all MOVE_ANT moves for each ant in the inventory
    myInv = getCurrPlayerInventory(currentState)
    for ant in myInv.ants:
        #skip ants that have already moved
        if (ant.hasMoved): continue

        #create a Move object for each valid movement path
        allPaths = listAllMovementPaths(currentState,
                                        ant.coords,
                                        UNIT_STATS[ant.type][MOVEMENT],
                                        UNIT_STATS[ant.type][IGNORES_GRASS])

        #remove moves that take the queen out of her territory
        if (ant.type == QUEEN):
            tmpList = []
            for path in allPaths:
                if (isPathOkForQueen(path)):
                    tmpList.append(path)
            allPaths = tmpList

        #construct the list of moves using the paths
        for path in allPaths:
            result.append(Move(MOVE_ANT, path, None))

    return result


##
# listAllLegalMoves
#
# determines all the legal moves that can be made by the player
# whose turn it currently is.
#
# Parameters:
#   currentState - the current state
#
# Returns:  a list of Move objects
def listAllLegalMoves(currentState):
    result = []
    result.extend(listAllMovementMoves(currentState))
    result.extend(listAllBuildMoves(currentState))
    result.append(Move(END, None, None))
    return result



##
# Return: a reference to the inventory of the player whose turn it is
def getCurrPlayerInventory(currentState):
    #Get my inventory
    resultInv = None
    for inv in currentState.inventories:
        if inv.player == currentState.whoseTurn:
            resultInv = inv
            break

    return resultInv

##
# Return: a reference to the QUEEN of the player whose turn it is
def getCurrPlayerQueen(currentState):
    #find the queen
    queen = None
    for inv in currentState.inventories:
        if inv.player == currentState.whoseTurn:
            queen = inv.getQueen()
            break
    return queen


##
# Return: a list of the food objects on my side of the board
def getCurrPlayerFood(self, currentState):
    food = getConstrList(currentState, 2, (FOOD,))
    myFood = []
    if (currentState.inventories[0].player == currentState.whoseTurn):
        myFood.append(food[2])
        myFood.append(food[3])
    else:
        myFood.append(food[0])
        myFood.append(food[1])
    return myFood



##
# Return: a reference to my enemy's inventory
def getEnemyInv(self, currentState):
    if (currentState.inventories[0].player == currentState.whoseTurn):
        return currentState.inventories[1]
    else:
        return currentState.inventories[0]

##
# getNextState
#
# Author:  Jordan Goldey (Class of 2017)
#
# Description: Creates a copy of the given state and modifies the inventories in
# it to reflect what they would look like after a given move.  For efficiency,
# only the inventories are modified and the board is set to None.  The original
# (given) state is not modified.
#
# CAVEAT: To facilitate longer term analysis without having to take enemy moves
# into consideration, MOVE_ANT commands do not cause the hasMoved property of
# the ant to change to True.  Furthermore the END move type is ignored.
#
# Parameters:
#   currentState - A clone of the current state (GameState)
#   move - The move that the agent would take (Move)
#
# Return: A clone of what the state would look like if the move was made
##
def getNextState(currentState, move):
    # variables I will need
    myGameState = currentState.fastclone()
    myInv = getCurrPlayerInventory(myGameState)
    me = myGameState.whoseTurn
    myAnts = myInv.ants
    myTunnels = myInv.getTunnels()
    myAntHill = myInv.getAnthill()

    # If enemy ant is on my anthill or tunnel update capture health
    ant = getAntAt(myGameState, myAntHill.coords)
    if ant is not None:
        if ant.player != me:
            myAntHill.captureHealth -= 1

    # If an ant is built update list of ants
    antTypes = [WORKER, DRONE, SOLDIER, R_SOLDIER]
    if move.moveType == BUILD:
        if move.buildType in antTypes:
            ant = Ant(myInv.getAnthill().coords, move.buildType, me)
            myInv.ants.append(ant)
            # Update food count depending on ant built
            myInv.foodCount -= UNIT_STATS[move.buildType][COST]
        # ants are no longer allowed to build tunnels, so this is an error
        elif move.buildType == TUNNEL:
            print("Attempted tunnel build in getNextState()")
            return currentState

    # If an ant is moved update their coordinates and has moved
    elif move.moveType == MOVE_ANT:
        newCoord = move.coordList[-1]
        startingCoord = move.coordList[0]
        for ant in myAnts:
            if ant.coords == startingCoord:
                ant.coords = newCoord
                # TODO: should this be set true? Design decision
                ant.hasMoved = False
                # If an ant is carrying food and ends on the anthill or tunnel drop the food
                if ant.carrying and ant.coords == myInv.getAnthill().coords:
                    myInv.foodCount += 1
                    ant.carrying = False
                for tunnels in myTunnels:
                    if ant.carrying and (ant.coords == tunnels.coords):
                        myInv.foodCount += 1
                        ant.carrying = False
                # If an ant doesn't have food and ends on the food grab food
                if not ant.carrying and ant.type == WORKER:
                    foods = getConstrList(myGameState, 2, [FOOD])
                    for food in foods:
                        if food.coords == ant.coords:
                            ant.carrying = True
                # If my ant is close to an enemy ant attack it
                attackable = listAttackable(ant.coords, UNIT_STATS[ant.type][RANGE])
                for coord in attackable:
                    foundAnt = getAntAt(myGameState, coord)
                    if foundAnt is not None:  # If ant is adjacent my ant
                        if foundAnt.player != me:  # if the ant is not me
                            foundAnt.health = foundAnt.health - UNIT_STATS[ant.type][ATTACK]  # attack
                            # If an enemy is attacked and looses all its health remove it from the other players
                            # inventory
                            if foundAnt.health <= 0:
                                myGameState.inventories[1 - me].ants.remove(foundAnt)
                            # If attacked an ant already don't attack any more
                            break
    return myGameState

##
# getNextStateAdversarial
#
# Description: This is the same as getNextState (above) except that it properly
# updates the hasMoved property on ants and the END move is processed correctly.
#
# Parameters:
#   currentState - A clone of the current state (GameState)
#   move - The move that the agent would take (Move)
#
# Return: A clone of what the state would look like if the move was made
##
def getNextStateAdversarial(currentState, move):
    # variables I will need
    nextState = getNextState(currentState, move)
    myInv = getCurrPlayerInventory(nextState)
    myAnts = myInv.ants

    # If an ant is moved update their coordinates and has moved
    if move.moveType == MOVE_ANT:
        startingCoord = move.coordList[-1]
        for ant in myAnts:
            if ant.coords == startingCoord:
                ant.hasMoved = True
    elif move.moveType == END:
        for ant in myAnts:
            ant.hasMoved = False
        nextState.whoseTurn = 1 - currentState.whoseTurn
    return nextState


##
# returns a character representation of a given ant
# (helper for asciiPrintState)
def charRepAnt(ant):
    if (ant == None):
        return " "
    elif (ant.type == QUEEN):
        return "Q"
    elif (ant.type == WORKER):
        return "W"
    elif (ant.type == DRONE):
        return "D"
    elif (ant.type == SOLDIER):
        return "S"
    elif (ant.type == R_SOLDIER):
        return "I"
    else:
        return "?"

##
# returns a character representation of a given construct
# (helper for asciiPrintState)
def charRepConstr(constr):
    if (constr == None):
        return " "
    if (constr.type == ANTHILL):
        return "^"
    elif (constr.type == TUNNEL):
        return "@"
    elif (constr.type == GRASS):
        return ";"
    elif (constr.type == FOOD):
        return "%"
    else:
        return "?"

##
# returns a character representation of a given location
# (helper for asciiPrintState)
def charRepLoc(loc):
    if (loc == None):
        return " "
    elif (loc.ant != None):
        return charRepAnt(loc.ant)
    elif (loc.constr != None):
        return charRepConstr(loc.constr)
    else:
        return "."


##
# asciiPrintState
#
# prints a text representation of a GameState to stdout.  This is useful for
# debugging.
#
# Parameters:
#    state - the state to print
#
def asciiPrintState(state):
    #select coordinate ranges such that board orientation will match the GUI
    #for either player
    coordRange = list(range(0,10))
    colIndexes = " 0123456789"
    if (state.whoseTurn == PLAYER_TWO):
        coordRange = list(range(9,-1,-1))
        colIndexes = " 9876543210"

    #print the board with a border of column/row indexes
    print(colIndexes)
    index = 0              #row index
    for x in coordRange:
        row = str(x)
        for y in coordRange:
            ant = getAntAt(state, (y, x))
            if (ant != None):
                row += charRepAnt(ant)
            else:
                constr = getConstrAt(state, (y, x))
                if (constr != None):
                    row += charRepConstr(constr)
                else:
                    row += "."
        print(row + str(x))
        index += 1
    print(colIndexes)

    #print food totals
    p1Food = state.inventories[0].foodCount
    p2Food = state.inventories[1].foodCount
    print(" food: " + str(p1Food) + "/" + str(p2Food))


class GraphNode:

    def __init__(self, parent=None, coords=None, f=0.0, g=0.0, h=0.0):
        self.parent = parent
        self.coords = coords
        self.f = f
        self.g = g
        self.h = h

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        if self.coords == other.coords:
            return True
        return False

    def __str__(self):
        return str(self.coords)


##
# aStarSearchPath
#
# Create a path towards from start to goal
# CAVEAT: A-STAR SEARCH IS SLOWER THAN createPathToward() BECAUSE THIS IS OPTIMAL
#         AND createPathTowards() IS GREEDY FOR TIME EFFICIENCY
#
#   @param currentState - a gameState
#   @param start - the Ant's Coordinates aka ant.coords
#   @param goal - the target coordinates
#
##
def aStarSearchPath(currentState, start, goal):
    start = GraphNode(coords=start)
    goal = GraphNode(coords=goal)

    ant = getAntAt(currentState, start.coords)

    antMovement = UNIT_STATS[ant.type][MOVEMENT]
    antMovement = antMovement + 1
    ign_grass = UNIT_STATS[ant.type][IGNORES_GRASS]

    if start.coords == goal.coords:
        return []

    start.f = start.g + approxDist(start.coords, goal.coords)
    open_list = [start, ]
    closed_list = list()
    current = start

    while open_list:
        if current == goal:
            return construct_path(current, antMovement)

        current = open_list.pop(open_list.index(min(open_list, key=lambda x: x.f)))

        if current in closed_list:
            continue

        for neighbor in neighbors(currentState, current, goal, ign_grass, antMovement):
            if neighbor == goal:
                return construct_path(current, antMovement)
            if neighbor in open_list:
                other = next((x for x in open_list if x.coords == neighbor.coords), None)
                if next((x for x in open_list if x.coords == neighbor.coords), None) is not None:
                    if other.f < neighbor.f:
                        continue
            if neighbor in closed_list:
                other = next((x for x in open_list if x.coords == neighbor.coords), None)
                if next((x for x in open_list if x.coords == neighbor.coords), None) is not None:
                    if other.f < neighbor.f:
                        continue
                    else:
                        open_list.append(neighbor)
                else:
                    open_list.append(neighbor)
            else:
                open_list.append(neighbor)

        closed_list.append(current)

    return False


def neighbors(currentState, node, goal, ign_grass, antMovement):
    bors = [GraphNode(coords=y) for y in listReachableAdjacent(currentState, node.coords, antMovement, ign_grass)]
    for bor in bors:
        bor.g = node.g + 1
        bor.f = bor.g + approxDist(bor.coords, goal.coords)
        bor.parent = node
    return bors


def construct_path(node, antMovement):
    path = [node, ]
    normalPath = list()
    while node.parent is not None:
        node = node.parent
        path.append(node)

    for x in path:
        normalPath.append(x.coords)

    li = normalPath[::-1]

    return li if len(li) <= antMovement else li[:antMovement]
