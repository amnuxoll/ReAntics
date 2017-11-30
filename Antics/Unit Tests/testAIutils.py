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
        name = "grass left"

        path = createPathToward(state, (3, 2), (1, 2), 2)
        correct = [(3, 2), (2, 2), (1, 2)]
        self.assertEqual(path, correct, "Failure in %s test. Path was %s and should have been %s."
                         % (name, path, correct))

if __name__ == '__main__':
    unittest.main()
