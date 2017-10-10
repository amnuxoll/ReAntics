import tkinter

#########################################################
# Class GUIHandler
#
# This class is to be instantiated by the game engine
# whenever the ReAntics GUI is needed. This class will
# handle all interactions with GUI threads and methods
# and needed callbacks to the game engine.
#
# The goal of this class is to keep the UI as separate as
# possible from the game engine so that the game can be
# easily configured to run without a GUI if desired.
#########################################################
class GUIHandler:

    def __init__(self, game):
        self.game = game

        # set up tkinter things
        self.root = tkinter.Tk()
        self.baseFrame = tkinter.Frame(self.root)
        self.settingsFrame = tkinter.Frame(self.baseFrame)
        self.statsFrame = tkinter.Frame(self.baseFrame)
        self.gameFrame = tkinter.Frame(self.baseFrame)

        # TODO implement and attach these handlers
        self.settingsHandler = None
        self.statsHandler = None
        self.gameHandler = None # GamePane(self, self.gameFrame)

        # we want the game to start on the settings screen, so show it first
        self.settingsFrame.pack()

        # pack main GUI
        self.baseFrame.pack()

        # this starts the event handling loop if we want to
        # execute code afterwords, this handler needs to be
        # in a separate thread
        self.root.mainloop()

    ##
    # showFrame
    #
    # The GUI handler never destroys the windows in order to
    # be memory and CPU efficient. This method shows whichever
    # frame needs to be present and hides the others.
    #
    #   @param frameNum - integer representing which frame to show
    #       0: settings frame
    #       1: stats frame
    #       2: game frame
    ##
    def showFrame(self, frameNum):
        self.settingsFrame.pack_forget()
        self.statsFrame.pack_forget()
        self.gameFrame.pack_forget()

        if frameNum == 0:
            self.settingsFrame.pack()
        elif frameNum == 1:
            self.statsFrame.pack()
        else:
            self.gameFrame.pack()

# test code to check GUI without running the game itself

if __name__ == "__main__":
    handler = GUIHandler(None)