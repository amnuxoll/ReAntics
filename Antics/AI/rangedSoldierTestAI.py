import random
import sys
from Player import*
from Constants import*
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


class AIPlayer(Player):


    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "rangedSoldierTestAI")

        self.myFood = None
        self.myTunnel = None

    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None

        if currentState.phase == SETUP_PHASE_1:
            return[(0,0), (5,1),
                   (0,3), (1,2), (2,1), (3,0),
                   (0,2), (1,1), (2,0),
                   (0,1), (1,0)];

        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return None  # should never happen

    def getMove(self, currentState):

        playerInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        # the first time this method is called, the food and tunnel locations
        # need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            # find the food closest to the tunnel
            bestDistSoFar = 1000  # i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist

        # if I don't have a worker, give up.  QQ
        numAnts = len(playerInv.ants)
        if (numAnts == 1):
            return Move(END, None, None)

        # if the worker has already moved, we're done
        workerList = getAntList(currentState, me, (WORKER,))
        if (len(workerList) < 1):
            return Move(END, None, None)
        else:
            myWorker = workerList[0]
            if (myWorker.hasMoved):
                return Move(END, None, None)

        # if the queen is on the anthill move her
        myQueen = playerInv.getQueen()
        if (myQueen.coords == playerInv.getAnthill().coords):
            return Move(MOVE_ANT, [playerInv.getQueen().coords, (1, 0)], None)

        # if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)

        # # if I have the food and the anthill is unoccupied then
        # # make another tunnel
        # if (playerInv.foodCount > 2):
        #     return Move(BUILD, [4,5], TUNNEL)

        # if I have the food and the anthill is unoccupied then
        # make a ranged soldier
        if (playerInv.foodCount > 2):
            if (getAntAt(currentState, playerInv.getAnthill().coords) is None):
                return Move(BUILD, [playerInv.getAnthill().coords], R_SOLDIER)

        # Move all my ranged soldiers towards the enemy
        myRSoldiers = getAntList(currentState, me, (R_SOLDIER,))
        for drone in myRSoldiers:
            if not (drone.hasMoved):
                droneX = drone.coords[0]
                droneY = drone.coords[1]
                if (droneY < 9):
                    droneY += 1;
                else:
                    droneX += 1;
                if (droneX, droneY) in listReachableAdjacent(currentState, drone.coords, 3):
                    return Move(MOVE_ANT, [drone.coords, (droneX, droneY)], None)
                else:
                    return Move(MOVE_ANT, [drone.coords], None)

        # if the worker has food, move toward tunnel
        if (myWorker.carrying):
            path = createPathToward(currentState, myWorker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        # if the worker has no food, move toward food
        else:
            path = createPathToward(currentState, myWorker.coords,
                                    self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)


    ##

    # getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  # don't care

    ##
    # registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass

