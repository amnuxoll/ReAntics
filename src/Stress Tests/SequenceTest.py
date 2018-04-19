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
import json

# save original settings
with open(SETTINGS_FILE, 'r') as f:
    old_data = json.load(f)

# write stress test to settings file
with open("Stress Tests/sequence.json", 'r') as f:
    data = json.load(f)
with open(SETTINGS_FILE, 'w') as f:
    json.dump(data, f)
# TODO: Run game automatically
G = Game()

# replace old settings after test done
with open(SETTINGS_FILE, 'w') as f:
    json.dump(old_data, f)
