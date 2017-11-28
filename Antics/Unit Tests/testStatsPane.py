import os
os.chdir("..")
import unittest
import Game
from GUIHandler import GUIHandler
from Constants import *
from Player import Player
import re
import StatsPane as sp


class testStatsPane(unittest.TestCase):
    def setUp(self):
        self.gameTest = Game.Game()
        self.handler: GUIHandler = GUIHandler(None)
        self.handler.gameHandler.createFrames()
        self.handler.showFrame(1)



    def testButtonCloseUI(self):
       self.gameTest.sp.UIButton.invoke()

    def testButtonPause(self):
        self.gameTest.children['pauseButton'].invoke()

    def testButtonStep(self):
        self.gameTest.children['pauseButton'].invoke()

    def testButtonStatsOnOff(self):
        self.gameTest.children['statsButton'].invoke()

    def testButtonKill(self):
        self.gameTest.children['killButton'].invoke()

    def testButtonrestart(self):
        self.gameTest.children['restartButton'].invoke()

    def testButtonSettings(self):
        self.gameTest.children['settingsButton'].invoke()





if __name__ == '  main  ':
    unittest.main()