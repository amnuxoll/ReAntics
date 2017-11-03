import os
os.chdir("..")
import unittest
import Game
from Constants import *
from Player import Player


class testGame(unittest.TestCase):

    def setUp(self):
        self.gameTest = Game.Game(True)
        pass

    def testStartHumanVsAI(self):
        self.gameTest.startHumanVsAI("Random")
        self.assertEqual(self.gameTest.numGames, 1)
        self.assertEqual(len(self.gameTest.players), 2)
        self.assertEqual(len(self.gameTest.currentPlayers), 2)
        self.assertEqual(self.gameTest.mode, HUMAN_MODE)
        self.assertEqual(self.gameTest.state.phase, SETUP_PHASE_1)


if __name__ == '__main__':
    unittest.main()
