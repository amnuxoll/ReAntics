import os
os.chdir("..")
import unittest
import Game
from Constants import *
from Player import Player
import re
import StatsPane as sp

class testStatsPane(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game.Game(True)



if __name__ == '  main  ':
    unittest.main()