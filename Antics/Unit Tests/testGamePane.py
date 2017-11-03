import sys
sys.path.append(".\\")
import os
os.chdir("..")
import unittest
import Game
from GUIHandler import GUIHandler
from GameState import GameState
from Construction import Construction
from Constants import *


class testGamePane(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game.Game(True)

    def testBoardHighlighting(self):
        handler = GUIHandler(None)
        handler.gameHandler.createFrames()
        handler.showFrame(2)
        state = GameState.getBlankState()
        handler.showState(state)

        handler.gameHandler.highlightValidMoves((2, 2), 1)
        locs = [        (2, 1),
                (1, 2), (2, 2), (3, 2),
                        (2, 3)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the no-grass test."
                                     % (x, y))
                else:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the no-grass test."
                                     % (x, y))

        handler.gameHandler.clearHighlights()
        for y in range(10):
            for x in range(10):
                self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, False,
                                 "%d , %d: was highlighted when it shouldn't have been after a clear."
                                 % (x, y))

        grass = Construction((2, 2), GRASS)
        state.inventories[2].constrs.append(grass)
        state.board[2][2].constr = grass
        handler.showState(state)

        # grass on start point shouldn't affect anything
        handler.gameHandler.highlightValidMoves((2, 2), 1)
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the on-grass test."
                                     % (x, y))
                else:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the on-grass test."
                                     % (x, y))

        handler.gameHandler.clearHighlights()

        handler.gameHandler.highlightValidMoves((2, 3), 1)
        locs = [(1, 3), (2, 3), (3, 3),
                        (2, 4)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the under grass 1 test."
                                     % (x, y))
                else:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the under grass 1 test."
                                     % (x, y))
        handler.gameHandler.clearHighlights()

        handler.gameHandler.highlightValidMoves((2, 3), 2)
        locs = [        (1, 2), (2, 2), (3, 2),
                (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
                        (1, 4), (2, 4), (3, 4),
                                (2, 5)]
        for y in range(10):
            for x in range(10):
                if (x, y) in locs:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, True,
                                     "%d, %d: was not highlighted when it should have been in the under grass 2 test."
                                     % (x, y))
                else:
                    self.assertEqual(handler.gameHandler.boardIcons[y][x].highlight, False,
                                     "%d, %d: was highlighted when it shouldn't have been in the under grass 2 test."
                                     % (x, y))





if __name__ == '__main__':
    unittest.main()
