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
from SettingsPane import SETTINGS_FILE
import json

data = None

def overWriteSettings ( filename ) :
    with open("Stress Tests/" + filename, 'r') as f:
                data = json.load(f)
                
    with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f)

overWriteSettings ( "Test_GameSet_Settings.json " )           
g = Game()



