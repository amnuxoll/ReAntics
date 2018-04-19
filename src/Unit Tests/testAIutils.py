import sys
# this needs to be here for module importing with directory change
# windows
sys.path.append(".\\")
# unix
sys.path.append("./")
import os
# some code assumes the CWD, so we have to do a work around for unit tests
# to keep unit tests in a separate folder
os.chdir("..")
import unittest
from GameState import GameState
from Construction import Construction
from Ant import Ant
from Constants import *
from AIPlayerUtils import *


class testGetPathTowards(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasic(self):
        state = GameState.getBlankState()
        name = "basic"

        path = createPathToward(state, (3, 2), (2, 1), 2)
        correct = [(3, 2), (2, 2), (2, 1)]
        self.assertEqual(path, correct, "Failure in %s test. Path was %s and should have been %s."
                         % (name, path, correct))

    def testGrassLeft(self):
        grass = Construction((2, 2), GRASS)
        state = GameState.getBlankState()
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass
        name = "grass left"

        path = createPathToward(state, (3, 2), (2, 1), 2)
        correct = [(3, 2), (3, 1), (2, 1)]
        self.assertEqual(path, correct, "Failure in %s test. Path was %s and should have been %s."
                         % (name, path, correct))

    def testGrassUp(self):
        grass = Construction((3, 1), GRASS)
        state = GameState.getBlankState()
        state.inventories[2].constrs.append(grass)
        state.board[3][1].constr = grass
        name = "grass up"

        path = createPathToward(state, (3, 2), (2, 1), 2)
        correct = [(3, 2), (2, 2), (2, 1)]
        self.assertEqual(path, correct, "Failure in %s test. Path was %s and should have been %s."
                         % (name, path, correct))

    def testIgnoreGrass(self):
        state = GameState.getBlankState()

        # add grass
        grass = Construction((2, 2), GRASS)
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass

        # add ant that ignores grass
        ant = Ant((3, 2), DRONE, 0)
        state.inventories[0].ants.append(ant)
        state.board[2][3].ant = ant
        name = "ignores grass"

        path = createPathToward(state, (3, 2), (1, 2), 2)
        correct = [(3, 2), (2, 2), (1, 2)]
        self.assertEqual(path, correct, "Failure in %s test. Path was %s and should have been %s."
                         % (name, path, correct))

##
# Tests for this method should already exist in previous antics repository
# they should be copied here. Tests written here will only be for newly
# added/changed functionality.
#
#
class testGetNextState(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # note this test current passes because getNextState does no error checking on moves,
    # not because this case is specifically handled
    def testIgnoreGrass(self):
        state = GameState.getBasicState()

        # add grass
        grass = Construction((2, 2), GRASS)
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass

        # add ant that ignores grass
        ant = Ant((1, 2), DRONE, 0)
        state.inventories[0].ants.append(ant)
        state.board[1][2].ant = ant

        name = "ignores grass"
        path = createPathToward(state, (1, 2), (4, 2), 3)
        newState = getNextState(state, Move(MOVE_ANT, path, None))
        ant = getAntAt(newState, (4, 2))
        self.assertIsNotNone(ant, "Failure in %s test. Ant at %s was none." % (name, (4, 2)))

    def testRangeAttack(self):
        state = GameState.getBasicState()

        # add ant
        ant = Ant((4, 2), R_SOLDIER, 0)
        state.inventories[0].ants.append(ant)
        state.board[2][4].ant = ant

        # add ant to attack
        ant = Ant((1, 2), DRONE, 1)
        state.inventories[1].ants.append(ant)
        state.board[2][1].ant = ant

        # adjust unit stats
        old = UNIT_STATS[R_SOLDIER][ATTACK]
        UNIT_STATS[R_SOLDIER][ATTACK] = UNIT_STATS[DRONE][HEALTH]

        move = Move(MOVE_ANT, [(4, 2)], None)
        newState = getNextState(state, move)
        ant = getAntAt(newState, (1, 2))

        # adjust back
        UNIT_STATS[R_SOLDIER][ATTACK] = old

        name = "ranged attack"
        self.assertIsNone(ant, "Failure in %s test. Ant at %s was still alive" % (name, (1, 2)))

    def testWorkerAttack(self):
        state = GameState.getBasicState()

        # add ant
        ant = Ant((4, 2), WORKER, 0)
        state.inventories[0].ants.append(ant)
        state.board[2][4].ant = ant

        # add ant to attack
        ant = Ant((3, 2), WORKER, 1)
        state.inventories[1].ants.append(ant)
        state.board[2][3].ant = ant

        move = Move(MOVE_ANT, [(4, 2)], None)
        newState = getNextState(state, move)
        ant = getAntAt(newState, (3, 2))

        name = "worker attack"
        self.assertIsNotNone(ant, "Failure in %s test. Ant at %s was dead" % (name, (1, 2)))



class testListAttackable(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasic(self):
        name = "attackable basic"
        coords = listAttackable((4, 4))
        correct = [         (4, 3),
                    (3, 4),         (5, 4),
                            (4, 5)]

        # should be true up to order
        self.assertEqual(set(coords), set(correct), "Failure in %s test. Attackable was %s and should have been %s."
                         % (name, coords, correct))

    def testNearWall(self):
        name = "attackable near wall"
        coords = listAttackable((0, 4))
        correct = [(0, 3),
                           (1, 4),
                   (0, 5)]

        # should be true up to order
        self.assertEqual(set(coords), set(correct), "Failure in %s test. Attackable was %s and should have been %s."
                         % (name, coords, correct))

    def testRanged(self):
        name = "attackable ranged"
        # only using range 2 for simplicity
        coords = listAttackable((4, 4), 2)
        correct = [                (4, 2),
                           (3, 3), (4, 3), (5, 3),
                   (2, 4), (3, 4),         (5, 4), (6, 4),
                           (3, 5), (4, 5), (5, 5),
                                   (4, 6)]

        # should be true up to order
        self.assertEqual(set(coords), set(correct), "Failure in %s test. Attackable was %s and should have been %s."
                         % (name, coords, correct))


##
# Tests for this method should already exist in previous antics repository
# they should be copied here. Tests written here will only be for newly
# added/changed functionality.
#
#
class testAllLegalMoves(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIgnoreGrass(self):
        state = GameState.getBasicState()

        # build state to test
        # make default ant not move
        getAntAt(state, (0, 0)).hasMoved = True
        ant = Ant((3, 0), DRONE, 0)
        state.board[0][3].ant = ant
        state.inventories[0].ants.append(ant)

        # add grass
        grass = Construction((3, 2), GRASS)
        state.inventories[2].constrs.append(grass)
        state.board[2][3].constr = grass

        name = "Legal moves ignore grass"
        move = None
        moves = listAllMovementMoves(state)
        for m in moves:
            if m.coordList[0] == (3, 0) and m.coordList[-1] == (3, 3):
                move = m

        self.assertIsNotNone(move, "Failure in %s test. Found no move to (3, 3)." % name)

    def testTunnelBuilding(self):
        state = GameState.getBasicState()
        state.inventories[0].foodCount = 9

        # add worker to *not* build tunnel
        ant = Ant((3, 3), WORKER, 0)
        state.inventories[0].ants.append(ant)
        state.board[3][3].ant = ant

        # move queen off anthill to catch possible errors building ants
        queen = getAntAt(state, (0, 0))
        queen.coords = (0, 1)
        state.board[0][0].ant = None
        state.board[1][0].ant = queen


        move = None
        moves = listAllBuildMoves(state)
        for m in moves:
            if m.buildType == TUNNEL:
                move = m
                break

        name = "Legal moves build no tunnels"
        self.assertIsNone(move, "Faliure in %s test. A build tunnel move was found." % name)


if __name__ == '__main__':
    unittest.main()
