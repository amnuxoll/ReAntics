  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

## Author : Sara Perkins, Brendan Thomas
## Version: 1/23/2018

##
# a path is a support data structure that hold arrangements of ants, food pickup,
# and food dropoff locations
class AntPathCycle():

    def __init__(self, foodCoords, depositCoords):
        self.antList = []
        self.food = foodCoords
        self.deposit = depositCoords
        self.state = None

    ## adds a new ant to the list this path interacts with
    def addAnt(self, newCoords):
        self.antList.append(newCoords)

    ## searches through the ants in this path and returns an applicable action for that path
    ## if there is no applicable action returns None
    def updateNextAnt(self):
        for ant in self.antList:
            currentAnt = getAntAt(self.state, ant)
            if currentAnt is not None:
                if not currentAnt.hasMoved:
                    if currentAnt.carrying:
                        path = createPathToward(self.state, ant, self.deposit, UNIT_STATS[WORKER][MOVEMENT])
                        self.antList.append(path[len(path) - 1])
                        return Move(MOVE_ANT, path, None)
                    else:
                        path = createPathToward(self.state, ant, self.food, UNIT_STATS[WORKER][MOVEMENT])
                        self.antList.append(path[len(path) - 1])
                        return Move(MOVE_ANT, path, None)
        return None

    ## gets a new gamestate and clears out ants that are no longer present (killed or moved)
    def updateState(self, newState):
        self.state = newState

        toRemove = []
        for ant in self.antList:
            boardAnt = getAntAt(self.state, ant)
            if boardAnt is None or boardAnt.player != self.state.whoseTurn or boardAnt.type != WORKER:
                toRemove.append(ant)

        for ant in toRemove:
            self.antList.remove(ant)


##
#AIPlayer
#Description: The responsibility of this class is to interact with the game by
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
        super(AIPlayer, self).__init__(inputPlayerId, "Ralph")
        self.foods = None
        self.distances = [0 for i in range(2)]
        self.hill = None
        self.tunnel = None
        self.paths = None

        self.o_foods   = [] # coords of the opponent's food
        
    
    ##
    #getPlacement
    #
    #Description: The getPlacement method corresponds to the 
    #action taken on setup phase 1 and setup phase 2 of the game. 
    #In setup phase 1, the AI player will be passed a copy of the 
    #state as currentState which contains the board, accessed via 
    #currentState.board. The player will then return a list of 11 tuple 
    #coordinates (from their side of the board) that represent Locations 
    #to place the anthill and 9 grass pieces. In setup phase 2, the player 
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent's side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to 
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of eleven 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            ##reset instance variables (for tournaments)
            self.foods = None
            self.distances = [0 for i in range(2)]
            self.hill = None
            self.tunnel = None
            self.paths = None

            ## place hill, tunnel, and grass in a predefined set
            return [(2, 1), (7, 2),
                    (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (6, 3), (7, 3), (8, 3), (9, 3)]
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            self.o_food = []
            ## find enemy tunnel and hill
            enemy = 1 - currentState.whoseTurn
            enemyHill = getConstrList(currentState, enemy, (ANTHILL,))[0]
            enemyTunnel = getConstrList(currentState, enemy, (TUNNEL,))[0]

            ## find two places for food as far from opponent deposit spots as possible
            for i in range(0, numToPlace):
                move = None
                maxDist = 0
                for j in range(10):
                    for k in range(6, 10):
                        if getConstrAt(currentState, (j, k)) is None:
                            dist1 = stepsToReach(currentState, (j, k), enemyHill.coords)
                            dist2 = stepsToReach(currentState, (j, k), enemyTunnel.coords)

                            if min(dist1, dist2) > maxDist and i == 0:
                                    maxDist = min(dist1, dist2)
                                    move = (j, k)

                            if min(dist1, dist2) > maxDist and i == 1:
                                if not self.o_food[0] == (j, k):
                                    maxDist = min(dist1, dist2)
                                    move = (j, k)
                self.o_food.append(move)

            return self.o_food
        else:
            return None  #should never happen
    
    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game 
    #and requests from the player a Move object. All types are symbolic 
    #constants which can be referred to in Constants.py. The move object has a 
    #field for type (moveType) as well as field for relevant coordinate 
    #information (coordList). If for instance the player wishes to move an ant, 
    #they simply return a Move object where the type field is the MOVE_ANT constant 
    #and the coordList contains a listing of valid locations starting with an Ant 
    #and containing only unoccupied spaces thereafter. A build is similar to a move 
    #except the type is set as BUILD, a buildType is given, and a single coordinate 
    #is in the list representing the build location. For an end turn, no coordinates 
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a move from the player.(GameState)   
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        ##helpful Pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        ##setup instance variables if necessary
        if self.hill is None:
            self.hill = getConstrList(currentState, me, (ANTHILL,))[0]
        if self.tunnel is None:
            self.tunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if self.paths is None:
            #find shortest paths from tunnel to fruit and anthill to fruit
            self.paths = [0 for i in range(2)]

            temp_foods = getConstrList(currentState, None, (FOOD,))
            foods = []
            for f in temp_foods:
                if isPathOkForQueen ( [f.coords] ) :
                    foods.append(f)
            self.foods = foods
            dist = 999
            bestForTunnel = None
            for food in foods:
                testDist = stepsToReach(currentState, self.tunnel.coords, food.coords)
                if testDist < dist:
                    dist = testDist
                    bestForTunnel = food.coords

            dist = 999
            bestForHill = None
            for food in foods:
                testDist = stepsToReach(currentState, self.hill.coords, food.coords)
                if testDist < dist:
                    dist = testDist
                    bestForHill = food.coords

            if bestForTunnel == bestForHill:
                dist = 999
                for food in foods:
                    testDist = stepsToReach(currentState, self.hill.coords, food.coords)
                    if testDist < dist:
                        if food.coords != bestForTunnel:
                            dist = testDist
                            bestForHill = food.coords



            self.paths[0] = AntPathCycle(bestForHill, self.hill.coords)
            self.paths[1] = AntPathCycle(bestForTunnel, self.tunnel.coords)

            self.paths[1].addAnt(self.tunnel.coords)

        ## give every path a new gamestate to work with
        for path in self.paths:
            path.updateState(currentState)

        #move queen to basic defensive position
        myQueen = myInv.getQueen()
        if not myQueen.hasMoved:
            enemyAnts = getAntList(currentState, 1-me, (DRONE, SOLDIER, R_SOLDIER))
            enemy_locs = [ a.coords for a  in enemyAnts ]

            if len(enemy_locs) < 1 or len(getAntList(currentState, me, (WORKER,))) == 0:
                q_dst = [(4,3), (5,3)][random.randint(0,1)]
                path = createPathToward(currentState, myQueen.coords,
                                    q_dst, UNIT_STATS[QUEEN][MOVEMENT])
                return Move(MOVE_ANT, path, None)
            
            moves_temp = listAllMovementPaths(currentState, myQueen.coords, UNIT_STATS[QUEEN][MOVEMENT], ignoresGrass = False)
            moves = [ ]
            for m in moves_temp:
                if isPathOkForQueen(m) and m[-1] not in [x.coords for x in self.foods]:
                    moves.append(m)

            dests = [ m[-1] for m in moves ]
            
            dest_scores = [ ]

            for d in range(len(dests)):
                dest_scores.append([])
                for src in enemy_locs:
                    dest_scores[d].append(stepsToReach(currentState, src, dests[d]) )
            dest_scores = [ min(d) for d in dest_scores ]
            
            path = moves[ dest_scores.index( max(dest_scores) ) ] if 1 not in dest_scores else moves[ dest_scores.index( 1 ) ] 
            return Move(MOVE_ANT, path, None)


        O_ANT = SOLDIER
        O_ANT_COST = UNIT_STATS[O_ANT][COST]
        ##generate ranged soldiers
        if myInv.foodCount >= O_ANT_COST :
            if getAntAt(currentState, self.hill.coords) is None:
                ##check if we need one
                enemy = 1 - me
                enemyAnts = getAntList(currentState, enemy, (WORKER, DRONE, SOLDIER, R_SOLDIER))
                numAttacking = 0
                hill_in_range = False 
                for ant in enemyAnts:
                    if ant.coords[1] < 6:
                        numAttacking += 1
                    if stepsToReach(currentState, ant.coords, self.hill.coords) <=  UNIT_STATS[ant.type][RANGE] +  UNIT_STATS[ant.type][MOVEMENT] + 1:
                        hill_in_range = True
                        break
                myAnts = getAntList(currentState, me, (O_ANT,))
                myAnts_coords = [ a.coords for a in myAnts ]
                if len(myAnts) < 2 and not hill_in_range: 
                    return Move(BUILD, [self.hill.coords], O_ANT)

        ##update drone
        ##simply send the drone on a mission towards nearest enemy ant
        soldiers = getAntList(currentState, me, (O_ANT,))
        for soldier in soldiers:
            if not soldier.hasMoved:
                enemy = 1 - me
                enemyAnts = getAntList(currentState, enemy, (WORKER, DRONE, SOLDIER, R_SOLDIER))
                dist = 999
                target = None
                enemy_atHome = None
                for ant in enemyAnts:
                    newDist = stepsToReach(currentState, ant.coords, soldier.coords)
                    if newDist < dist:
                        dist = newDist
                        target = ant
                    if ant.type != WORKER and \
                       stepsToReach(currentState, (ant.coords[0], self.hill.coords[1]), ant.coords) <= 2:
                        enemy_atHome = ant.coords
                enemy_workers = getAntList(currentState, enemy, (WORKER,))
                enemy_queen  = getAntList(currentState, enemy, (QUEEN,))[0].coords
                x = stepsToReach(currentState, soldier.coords, enemy_queen)
##                # hey look the queen is here 
##                if x <= UNIT_STATS[O_ANT][RANGE] + 1: ### umm why
##                    target = soldier.coords
                # kill the last worker -- head up first, at least into no man's land
                if len(enemy_workers) == 1 and not isPathOkForQueen([soldier.coords]):
                    target = enemy_workers[0].coords
                # kill the queen
                elif len(enemy_workers) == 0 or \
                     len(getAntList(currentState, me, (WORKER,))) == 0 and myInv.foodCount < 1 :
                    target = enemy_queen                
                # defend at home
                elif enemy_atHome :
                    target = enemy_atHome
                else :
                    target = enemy_queen
                if target is not None:
                    path = createPathToward(currentState, soldier.coords, target, UNIT_STATS[O_ANT][MOVEMENT])

                    y = stepsToReach(currentState, path[-1], enemy_queen)
                    if y <= UNIT_STATS[QUEEN][RANGE]:
                        temp = list(path)
                        if len(temp) > 1:
                            temp = temp[:len(temp)-1]
                        path = temp
                    #self.occupants[i] = path[-1]
                    return Move(MOVE_ANT, path, None)

        ##make a worker if there aren't enough and anthill is empty
        if myInv.foodCount > 0:
            enemy = 1 - me
            enemyAnts = getAntList(currentState, enemy, (WORKER, DRONE, SOLDIER, R_SOLDIER))
            hill_in_range = False 
            for ant in enemyAnts:
                if stepsToReach(currentState, ant.coords, self.hill.coords) <=  UNIT_STATS[ant.type][RANGE] +  UNIT_STATS[ant.type][MOVEMENT] + 1:
                    hill_in_range = True
                    break
            if not hill_in_range and getAntAt(currentState, self.hill.coords) is None:
                for path in self.paths:
                    if len(path.antList) == 0:
                        path.addAnt(self.hill.coords)
                        return Move(BUILD, [self.hill.coords], WORKER)

        ##update worker ants
        for path in self.paths:
            result = path.updateNextAnt()
            if result is not None:
                return result

        return Move(END, None, None)


    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes 
    #a move and has a valid attack. It is assumed that an attack will always be made 
    #because there is no strategic advantage from withholding an attack. The AIPlayer 
    #is passed a copy of the state which again contains the board and also a clone of 
    #the attacking ant. The player is also passed a list of coordinate tuples which 
    #represent valid locations for attack. Hint: a random AI can simply return one of 
    #these coordinates for a valid attack. 
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting 
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e. 
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]
        
    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply 
    #indicates to the AI whether it has won or lost the game. This is to help with 
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
