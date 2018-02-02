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
import Game
from Constants import *
from Player import Player
import re
import SettingsPane as sp


class testSettings(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game.Game(True)
        self.gameTest.loadAIs()
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
                      "timeout": False, 'timeout_limit': 0.3, 'pause': False, 'autorestart': False}
        pauseConditions = [{"players":["Random", "Booger"], "conditions":{"P0 Food":3}}]
        self.gameTest.process_settings(games, additional, pauseConditions, True)
        self.assertEqual(len(self.gameTest.game_calls), 1 + 1 * (len(self.gameTest.players)-1))
        self.assertEqual(self.gameTest.verbose, additional['verbose'])
        self.assertEqual(self.gameTest.playerSwap, additional['swap'])
        self.assertEqual(self.gameTest.randomSetup, True)
        self.assertEqual(self.gameTest.timeoutOn, additional['timeout'])
        self.assertEqual(len(self.gameTest.pauseConditions), 1)


if __name__ == '__main__':
    unittest.main()
