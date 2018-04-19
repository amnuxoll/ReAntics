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
from Game import Game
from SettingsPane import SETTINGS_FILE
from GamePane import GamePane
import json

# save original settings
with open(SETTINGS_FILE, 'r') as f:
    old = json.load(f)

# write stress test to board file
with open("Stress Tests/board.json", 'r') as board:
    new = json.load(board)

with open(SETTINGS_FILE, 'w') as board:
    json.dump(new, board)
g = Game()

with open(SETTINGS_FILE, 'w') as board:
    json.dump(old, board)
