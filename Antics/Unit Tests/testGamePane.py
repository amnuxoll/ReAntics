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
from Game import Game
from GUIHandler import GUIHandler
from GameState import GameState
from Construction import Construction
from Ant import Ant
from Constants import *


class testBoardHighlight(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game(True)
        self.handler: GUIHandler = GUIHandler(None)
        self.handler.gameHandler.createFrames()
        self.handler.showFrame(2)
        state = GameState.getBlankState()
        self.handler.showState(state)

    def tearDown(self):
        self.handler.root.destroy()

    def testBlankBoard(self):
        state = GameState.getBlankState()
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.gameHandler.highlightValidMoves((2, 2), 1)

        locs = [        (2, 1),
                (1, 2), (2, 2), (3, 2),
                        (2, 3)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the no-grass test."
                                     % (x, y))
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the no-grass test."
                                     % (x, y))

    def testClear(self):
        state = GameState.getBlankState()
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.gameHandler.highlightValidMoves((2, 2), 1)
        self.handler.gameHandler.clearHighlights()

        for y in range(10):
            for x in range(10):
                self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                 "%d , %d: was highlighted when it shouldn't have been after a clear."
                                 % (x, y))

    def testOnGrass(self):
        grass = Construction((2, 2), GRASS)
        state = GameState.getBlankState()
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        # grass on start point shouldn't affect anything
        self.handler.gameHandler.highlightValidMoves((2, 2), 1)

        locs = [        (2, 1),
                (1, 2), (2, 2), (3, 2),
                        (2, 3)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the on-grass test."
                                     % (x, y))
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the on-grass test."
                                     % (x, y))

    def testNearGrass(self):
        grass = Construction((2, 2), GRASS)
        state = GameState.getBlankState()
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.gameHandler.highlightValidMoves((2, 3), 1)

        locs = [(1, 3), (2, 3), (3, 3),
                        (2, 4)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the under grass 1 test."
                                     % (x, y))
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the under grass 1 test."
                                     % (x, y))

    def testBigMoveNearGrass(self):
        grass = Construction((2, 2), GRASS)
        state = GameState.getBlankState()
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.gameHandler.highlightValidMoves((2, 3), 2)

        locs = [        (1, 2), (2, 2), (3, 2),
                (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
                        (1, 4), (2, 4), (3, 4),
                                (2, 5)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the under grass 2 test."
                                     % (x, y))
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the under grass 2 test."
                                     % (x, y))


class testAttackHighlight(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game(True)
        self.handler: GUIHandler = GUIHandler(None)
        self.handler.gameHandler.createFrames()
        self.handler.showFrame(2)
        state = GameState.getBlankState()
        self.handler.showState(state)

    def tearDown(self):
        self.handler.root.destroy()

    def testAdjacentAttack(self):
        name = "adjacent attack"
        # construct test state
        grass = Construction((2, 2), GRASS)
        atkAnt = Ant((1, 1), SOLDIER, PLAYER_ONE)
        defAnt = Ant((1, 2), WORKER, PLAYER_TWO)
        state = GameState.getBlankState()
        state.inventories[0].ants.append(atkAnt)
        state.inventories[1].ants.append(defAnt)

        # apply state and highlight function
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.getHumanAttack(atkAnt.coords)

        locs = [defAnt.coords]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the " % (x, y) + name +
                                     " test.")
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the " % (x, y) + name +
                                     " test.")

    def testMultiAttack(self):
        name = "multi attack"
        # construct test state
        grass = Construction((2, 2), GRASS)
        atkAnt = Ant((1, 1), SOLDIER, PLAYER_ONE)
        defAnt = Ant((1, 2), WORKER, PLAYER_TWO)
        defAnt2 = Ant((2, 1), WORKER, PLAYER_TWO)
        defAnt3 = Ant((0, 1), WORKER, PLAYER_TWO)
        state = GameState.getBlankState()
        state.inventories[0].ants.append(atkAnt)
        state.inventories[1].ants.append(defAnt)
        state.inventories[1].ants.append(defAnt2)
        state.inventories[1].ants.append(defAnt3)

        # apply state and highlight function
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.getHumanAttack(atkAnt.coords)

        locs = [defAnt.coords, defAnt2.coords, defAnt3.coords]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the " % (x, y) + name +
                                     " test.")
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the " % (x, y) + name +
                                     " test.")

    def testRangedAttack(self):
        name = "ranged attack"
        # construct test state
        grass = Construction((2, 2), GRASS)
        atkAnt = Ant((1, 1), R_SOLDIER, PLAYER_ONE)
        defAnt = Ant((1, 4), WORKER, PLAYER_TWO)
        state = GameState.getBlankState()
        state.inventories[0].ants.append(atkAnt)
        state.inventories[1].ants.append(defAnt)

        # apply state and highlight function
        self.handler.showState(state)
        self.handler.gameHandler.clearHighlights()
        self.handler.getHumanAttack(atkAnt.coords)

        locs = [defAnt.coords]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the " % (x, y) + name +
                                     " test.")
                else:
                    self.assertEqual(self.handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the " % (x, y) + name +
                                     " test.")


if __name__ == '__main__':
    unittest.main()
