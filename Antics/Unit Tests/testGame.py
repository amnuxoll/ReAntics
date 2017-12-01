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


class testGame(unittest.TestCase):

    def setUp(self):
        self.gameTest = Game(True)
        pass

    def testStartHumanVsAI(self):
        self.gameTest.startHumanVsAI("Random")

        self.assertEqual(len(self.gameTest.gamesToPlay), 1)

        self.assertEqual(self.gameTest.gamesToPlay[0].n, 1)
        self.assertEqual(self.gameTest.gamesToPlay[0].p1.author, "Human")
        self.assertEqual(self.gameTest.gamesToPlay[0].p2.author, "Random")

    def testStartAIvsAI(self):
        self.gameTest.startAIvsAI(10, "Random", "Booger")

        self.assertEqual(len(self.gameTest.gamesToPlay), 1)

        self.assertEqual(self.gameTest.gamesToPlay[0].n, 10)
        self.assertEqual(self.gameTest.gamesToPlay[0].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[0].p2.author, "Random")

    def testStartRR(self):
        self.gameTest.startRR(20, ["Random", "Booger", "Simple Food Gatherer"])

        self.assertEqual(len(self.gameTest.gamesToPlay), 3)

        self.assertEqual(self.gameTest.gamesToPlay[0].n, 20)
        self.assertEqual(self.gameTest.gamesToPlay[0].p1.author, "Random")
        self.assertEqual(self.gameTest.gamesToPlay[0].p2.author, "Booger")

        self.assertEqual(self.gameTest.gamesToPlay[1].n, 20)
        self.assertEqual(self.gameTest.gamesToPlay[1].p1.author, "Random")
        self.assertEqual(self.gameTest.gamesToPlay[1].p2.author, "Simple Food Gatherer")

        self.assertEqual(self.gameTest.gamesToPlay[2].n, 20)
        self.assertEqual(self.gameTest.gamesToPlay[2].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[2].p2.author, "Simple Food Gatherer")

    def testStartRRall(self):
        self.gameTest.startRRall(15)

        self.assertEqual(len(self.gameTest.gamesToPlay), 10)

        self.assertEqual(self.gameTest.gamesToPlay[0].n, 15)
        self.assertEqual(self.gameTest.gamesToPlay[0].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[0].p2.author, "Booger Test Timeout")

        self.assertEqual(self.gameTest.gamesToPlay[1].n, 15)
        self.assertEqual(self.gameTest.gamesToPlay[1].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[1].p2.author, "Complex Food Gatherer")

        self.assertEqual(self.gameTest.gamesToPlay[2].n, 15)
        self.assertEqual(self.gameTest.gamesToPlay[2].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[2].p2.author, "Simple Food Gatherer")

        self.assertEqual(self.gameTest.gamesToPlay[3].n, 15)
        self.assertEqual(self.gameTest.gamesToPlay[3].p1.author, "Booger")
        self.assertEqual(self.gameTest.gamesToPlay[3].p2.author, "Random")

        self.assertEqual(self.gameTest.gamesToPlay[4].n, 15)
        self.assertEqual(self.gameTest.gamesToPlay[4].p1.author, "Booger Test Timeout")
        self.assertEqual(self.gameTest.gamesToPlay[4].p2.author, "Complex Food Gatherer")

    def testStartSelf(self):
        self.gameTest.startSelf(27, "Random")

        self.assertEqual(len(self.gameTest.gamesToPlay), 1)

        self.assertEqual(self.gameTest.gamesToPlay[0].n, 27)
        self.assertEqual(self.gameTest.gamesToPlay[0].p1.author, "Random")
        self.assertEqual(self.gameTest.gamesToPlay[0].p2.author, "Random@@")

if __name__ == '__main__':
    unittest.main()
