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

##
# Haven't Figured out how to run this stress test from a file.
# Currently working on making an Error Handling Stress Test
# in an Agent.
#
#
#
##