import os
import sys
import importlib
import shutil


def makeDistrib():
    cwd = os.getcwd()

    # get paths for needed folders
    distribPath = os.path.join(cwd, "ReAnticsDistributable")
    distribTexturesPath = os.path.join(distribPath, "Textures")
    distribAIPath = os.path.join(distribPath, "AI")
    texturesPath = os.path.join(cwd, "Textures")
    aiPath = os.path.join(cwd, "AI")
    hiddenAIPath = os.path.join(aiPath, "__pycache__")

    # remove old distrib if present to prevent conflicts
    if os.path.isdir(distribPath):
        shutil.rmtree(distribPath)

    os.mkdir(distribPath)

    ignored = ["MakeDistributable.py", "make-distrib-windows.bat"]

    # copy game files and bat scripts
    files = os.listdir(cwd)
    for file in files:
        if (file[-3:] == ".py" or file[-4:] == ".bat" or file[-3:] == ".sh") and file not in ignored:
            shutil.copyfile(os.path.join(cwd, file), os.path.join(distribPath, file))

    # copy texture files
    os.mkdir(distribTexturesPath)
    files = os.listdir(texturesPath)
    for file in files:
        shutil.copyfile(os.path.join(texturesPath, file), os.path.join(distribTexturesPath, file))

    # AIs that should be copied in obfuscated form
    hiddenAIs = ["anthillAttackAI.py", "Complex Food Gatherer.py", "DefensiveV1.py", "Nibble.py", "shapeShifter.py",
                 "Starve.py", "Soldier.py", "Very Complex Food Gatherer.py"]
    ignored = hiddenAIs + ["BoogerTestTimeout.py", "ErrorHandlingStressTest.py", "Learning.py", "LearningV2.py",
                           "rangedSoldierTestAI.py"]

    os.mkdir(distribAIPath)
    files = os.listdir(aiPath)
    # copy "open" AIs
    for file in files:
        if file[-3:] == ".py" and file not in ignored:
            shutil.copyfile(os.path.join(aiPath, file), os.path.join(distribAIPath, file))

    files = os.listdir(hiddenAIPath)
    # copy "hidden" AIs
    for file in files:
        # note these are .pyc files, the .py inclusion is to prevent the copy of the unobfuscated files
        cleaned = file.split(".")[0] + ".py"
        if cleaned in hiddenAIs:
            shutil.copyfile(os.path.join(hiddenAIPath, file), os.path.join(distribAIPath, cleaned + "c"))


# causes python to compile all of the AIs to make sure the compiled code is up to date with any changes
# essentially the LoadAI() from Game.py with the actual saving of AI's removed
def compileAIs():
    # Attempt to load AIs. Exit gracefully if user trying to load weird stuff.
    filesInAIFolder = os.listdir("AI")
    # Change directory to AI subfolder so modules can be loaded (they won't load as filenames).
    os.chdir('AI')

    # Add current directory in python's import search order.
    sys.path.insert(0, os.getcwd())
    # Make player instances from all AIs in folder.
    for file in filesInAIFolder:
        if file[-3:] == ".py" or file[-4:] == ".pyc":
            moduleName, ext = os.path.splitext(file)
            # Check to see if the file is already loaded.
            temp = importlib.import_module(moduleName)
    # Remove current directory from python's import search order.
    sys.path.pop(0)
    # Revert working directory to parent.
    os.chdir('..')



if __name__ == "__main__":
    compileAIs()
    makeDistrib()
