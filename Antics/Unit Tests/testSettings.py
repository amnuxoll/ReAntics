import os
os.chdir("..")
import unittest
import Game
from Constants import *
from Player import Player
import re
import SettingsPane as sp


class testSettings(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game.Game(True)
        self.gameTest.loadAIs(False)
        pass

    def testInt(self):
        rgx = re.compile("^[0-9]+$")
        strs = {"29": True, "hello": False, "-18": False, "0.25": False}

        for s in list(strs.keys()):
            self.assertEqual(rgx.match(s) is not None, strs[s])

    def testProcessSettings(self):
        games = [sp.GameGUIData("Two Player", 2, ["Random", "Booger"]),
                 sp.GameGUIData("Play All", 1, ["Random"])]
        additional = {"verbose": True, "swap": False, "layout_chosen": "Random Override",
                      "timeout": False, 'timeout_limit': 0.3}
        self.gameTest.process_settings(games, additional)
        self.assertEqual(len(self.gameTest.game_calls), 1 + 1 * 2) # This is Broken
        self.assertEqual(self.gameTest.verbose, additional['verbose'])
        self.assertEqual(self.gameTest.playerSwap, additional['swap'])
        self.assertEqual(self.gameTest.randomSetup, True)
        self.assertEqual(self.gameTest.timeoutOn, additional['timeout'])


if __name__ == '__main__':
    unittest.main()
