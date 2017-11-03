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

    def testStartAIvsAI(self):
        self.gameTest.startAIvsAI(10, "Random", "Booger")

        self.assertEqual(self.gameTest.numGames, 10)
        self.assertEqual(len(self.gameTest.players), 2)
        self.assertEqual(len(self.gameTest.currentPlayers), 2)
        self.assertEqual(self.gameTest.playerScores, [['Booger', 0, 0], ['Random', 0, 0]])
        self.assertEqual(self.gameTest.mode, TOURNAMENT_MODE)
        self.assertEqual(self.gameTest.state.phase, SETUP_PHASE_1)

    def testStartRR(self):
        self.gameTest.startRR(20, ["Random", "Booger", "Simple Food Gatherer"])

        self.assertEqual(self.gameTest.numGames, 20)
        self.assertEqual(len(self.gameTest.players), 3)
        self.assertEqual(len(self.gameTest.currentPlayers), 2)
        self.assertEqual(self.gameTest.playerScores, [['Booger', 0, 0], ['Simple Food Gatherer', 0, 0], ['Random', 0, 0]])
        self.assertEqual(self.gameTest.mode, TOURNAMENT_MODE)
        self.assertEqual(self.gameTest.state.phase, SETUP_PHASE_1)

    def testStartRRall(self):
        self.gameTest.startRRall(15)

        self.assertEqual(self.gameTest.numGames, 15)
        self.assertEqual(len(self.gameTest.players), 3)
        self.assertEqual(len(self.gameTest.currentPlayers), 2)
        self.assertEqual(self.gameTest.playerScores, [['Booger', 0, 0], ['Simple Food Gatherer', 0, 0], ['Random', 0, 0]])
        self.assertEqual(self.gameTest.mode, TOURNAMENT_MODE)
        self.assertEqual(self.gameTest.state.phase, SETUP_PHASE_1)

    def testStartSelf(self):
        self.gameTest.startSelf(27, "Random")

        self.assertEqual(self.gameTest.numGames, 27)
        self.assertEqual(len(self.gameTest.players), 2)
        self.assertEqual(len(self.gameTest.currentPlayers), 2)
        self.assertEqual(self.gameTest.playerScores, [['Random', 0, 0], ['Random@@', 0, 0]])
        self.assertEqual(self.gameTest.mode, TOURNAMENT_MODE)
        self.assertEqual(self.gameTest.state.phase, SETUP_PHASE_1)

if __name__ == '__main__':
    unittest.main()
