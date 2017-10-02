# ReAntics Hello World program
# Author: Brendan Thomas
# Date: 16 September 2017
#
# This program is just to start out the ReAntics repository and show off a demo of Tkinter code.

import tkinter as tk


class HelloUI(tk.Frame):

    def __init__(self, parent = None):
        # initialize UI object
        tk.Frame.__init__(self, parent)

        # store event handler to close later
        self.parent = parent

        self.hellos = 0

        # create UI elements in the standard way
        # the first argument is the parent element, which determines where it will be placed
        # in this case I use "self" because this object is the main UI frame
        self.helloLabel = tk.Label(self, text = "Hello World! I'm Tkinter.")

        # use stringvars to create changing text in the UI
        self.countText = tk.StringVar()
        self.countText.set("You've greeted me %d times" % self.hellos)
        self.countLabel = tk.Label(self, textvar = self.countText)

        # to attach commands to buttons or other widgets, pass in their reference like this
        self.helloButton = tk.Button(self, text = "Hello Tkinter!", command = self.helloPressed)
        self.quitButton = tk.Button(self, text = "Goodbye Tkinter.", command = self.goodbyePressed)

        # likely using grid structures for nearly everything
        self.helloLabel.grid(column = 0, columnspan = 2, row = 0)
        self.countLabel.grid(column = 0, columnspan = 2, row = 1)
        self.helloButton.grid(column = 0, row = 2)
        self.quitButton.grid(column = 1, row = 2)

        # pack is for when you don't care about layout or only have one element, such as the main frame
        self.pack()

        # editing the parent's attributes edits the base level window
        self.parent.title("ReAntics Hello World")

        # start event handling loop
        tk.mainloop()

    def helloPressed(self):
        self.hellos += 1
        self.countText.set("You've greeted me %d times" % self.hellos)

    def goodbyePressed(self):
        # close the UI like this
        self.parent.destroy()


# main code

# setup GUI object and initialize GUI library
app = HelloUI(tk.Tk())
