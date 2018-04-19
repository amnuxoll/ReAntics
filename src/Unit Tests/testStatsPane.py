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