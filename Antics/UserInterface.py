##
#UserInterface
#Description: This class renders the game board through pygame library method calls,
#   and handles user input events.
#
##
import pygame, os, sys, time
from pygame.locals import *
from Building import Building
from Ant import UNIT_STATS
from Constants import *
from GameState import addCoords, subtractCoords

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OFF_BLACK = (255, 0, 204)
GREY = (195, 195, 195)
DARK_RED = (150, 0, 0)
LIGHT_RED = (255, 0, 0)
DARK_GREEN = (0, 150, 0)
LIGHT_GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 150)
LIGHT_BLUE = (0, 0, 255)
ROBIN_EGG_BLUE = (0, 204, 204)
GOLDENROD = (238, 173, 14)
CELL_SIZE = Rect(0,0,10,10)
BOARD_SIZE = Rect(0,0,10,10)
CELL_SPACING = 5
FIELD_SPACING = 10

##
#UserInterface
#Description: class that handles all drawing and key presses, and translates everything to something that can more easily be understood by a programmer.
#
#Variables:
#   inputSize - An (x,y) tuple expressing the size of the aNTiCS window in pixels.((int,int))
##
class UserInterface(object):
    ##
    #__init__
    #Description: Creates a new UserInterface
    #
    #Parameters:
    #   inputSize - the size of the window to be created, in pixels.(int)
    ##
    def __init__(self, inputSize):
        self.screen = pygame.display.set_mode(inputSize)
        pygame.display.set_caption("aNTiCS")
        icon = pygame.image.load(os.path.join("Textures", "icon.bmp"))
        pygame.display.set_icon(icon)
    
    ##
    #submitBuild
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitBuild(self):
        print "Clicked SUBMIT BUILD"
    
    ##
    #submitEndTurn
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitEndTurn(self):
        print "Clicked SUBMIT END TURN"
    
    ##
    #gameModeTournament
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def gameModeTournament(self):
        print "Clicked GAME MODE TOURNAMENT"
    
    ##
    #gameModeHumanAI
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def gameModeHumanAI(self):
        print "Clicked GAME MODE HUMAN AI"
    
    ##
    #gameModeAIAI
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def gameModeAIAI(self):
        print "Clicked GAME MODE AI AI"
    
    ##
    #startGame
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def startGame(self):
        print "Clicked START GAME"
    
    ##
    #submitNext
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitNext(self):
        print "Clicked NEXT"
    
    ##
    #submitContinue
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitContinue(self):
        print "Clicked CONTINUE"
    
    ##
    #submitWorker
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitWorker(self):
        print "Clicked WORKER"
    
    ##
    #submitDrone
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitDrone(self):
        print "Clicked DRONE"
    
    ##
    #submitDSoldier
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitDSoldier(self):
        print "Clicked DIRECT SOLDIER"
    
    ##
    #submitISoldier
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitISoldier(self):
        print "Clicked INDIRECT SOLDIER"
    
    ##
    #submitNoBuild
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitNoBuild(self):
        print "Clicked BUILD NOTHING"
    
    ##
    #submitStartTournament
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitStartTournament(self):
        print "Clicked START TOURNAMENT"
    
    ##
    #submitStopTournament
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitStopTournament(self):
        print "Clicked STOP TOURNAMENT"
    
    ##
    #locationClicked
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    #
    #Parameters:
    #   coords - the cell on the board that was clicked.((int,int))
    ##
    def locationClicked(self, coords):
        print "Clicked LOCATION " + str(coords)
    
    ##
    #checkBoxClicked
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    #
    #Parameters:
    #   index - the index into the array self.allAIs.(int)
    ##
    def checkBoxClicked(self, index):
        print "CLICKED CHECKBOX NUMBER " + str(index)
    
    ##
    #submitSelectedAIs
    #Description: Dummy method used as a placeholder for the event handling methods that will be passed in from Game.py.
    ##
    def submitSelectedAIs(self):
        print "CLICKED SUBMIT SELECTED AIS"
    
    ##
    #notify
    #Description: changes the message displayed in the notification box.
    #
    #Parameters:
    #   message - The message to be relayed to the user.(string)
    ##
    def notify(self, message):
        self.lastNotification = message
    
    ##
    #getCaptureValues
    #Description: determines whether any anthills are being captured.
    #
    #Parameters:
    #   state - the current gameState.(GameState)
    #
    #Returns: a tuple representing the anthills of each player. If a player's
    #   anthill is being captured, their space in the tuple will contain the
    #   health of their anthill. Otherwise that space will be set to -1.
    ##
    def getCaptureValues(self, state):
        #Find the health of player 1's anthill, and whether it's being captured.
        player1Val = -1
        player1Hill = state.inventories[PLAYER_ONE].getAnthill()
        if player1Hill != None:
            hCoords = player1Hill.coords
            boardAnt = state.board[hCoords[0]][hCoords[1]].ant
            if boardAnt != None and boardAnt.player != player1Hill.player:
                player1Val = player1Hill.captureHealth
        #Find the health of player 2's anthill, and whether it's being captured.
        player2Val = -1
        player2Hill = state.inventories[PLAYER_TWO].getAnthill()
        if player2Hill != None:
            hCoords = player2Hill.coords
            boardAnt = state.board[hCoords[0]][hCoords[1]].ant
            if boardAnt != None and boardAnt.player != player2Hill.player:
                player2Val = player2Hill.captureHealth
        #Return the values acquired from the above calculations.
        return player1Val, player2Val
    
    ##
    #getCaptureValue
    #Description: determines whether the given location is being captured.
    #
    #Parameters:
    #   loc - a location containing an ant tunnel, which may or may not be getting captured.(Location)
    #
    #Returns: an integer containing the ant tunnel's health if it is being captured,
    #   or -1 otherwise.
    ##
    def getCaptureValue(self, loc):
        if loc.constr == None or loc.constr.type != TUNNEL:
            return -1
        elif loc.ant == None or loc.ant.player == loc.constr.player:
            return -1
        else:
            return loc.constr.captureHealth
    
    ##
    #drawNotification
    #Description: draws the notification currently being relayed to the user.
    #   Breaks the notification into multiple lines if necessary.
    ##
    def drawNotification(self):
        #Draw a black box to encapsulate the notification
        outerNoteBox = Rect(0, 0, self.buttonRect.width + 2 * CELL_SPACING, self.buttonRect.height + 2 * CELL_SPACING)
        pygame.draw.rect(self.screen, BLACK, outerNoteBox.move(self.messageLocation).move(-CELL_SPACING, -CELL_SPACING))
        #Draw a white box to make the black box appear empty
        noteBox = Rect(0, 0, self.buttonRect.width + CELL_SPACING + 1, self.buttonRect.height + CELL_SPACING + 1)
        pygame.draw.rect(self.screen, WHITE, noteBox.move(self.messageLocation).move(-CELL_SPACING / 2, -CELL_SPACING / 2))
        #Chop up text by moving to a new line every time you get close to the edge of the notification area.
        breakupIndex = 0
        lineNum = 0
        while self.notifyFont.size(self.lastNotification[breakupIndex:])[0] > self.buttonRect.width:
            pctToNewline = float(self.buttonRect.width) / float(self.notifyFont.size(self.lastNotification[breakupIndex:])[0])
            indexOfNewline = int(float(len(self.lastNotification[breakupIndex:])) * pctToNewline) - 1
            while self.lastNotification[breakupIndex+indexOfNewline] != " " or indexOfNewline == breakupIndex:
               indexOfNewline -= 1
            if indexOfNewline == breakupIndex:
                indexOfNewline = int(float(len(self.lastNotification)) * pctToNewline) - 1
            messageSurface = self.notifyFont.render(self.lastNotification[breakupIndex:breakupIndex+indexOfNewline].lstrip(), True, DARK_RED)
            self.screen.blit(messageSurface, (self.messageLocation[0], self.messageLocation[1] + lineNum * self.notifyFont.get_height()))
            breakupIndex += indexOfNewline
            lineNum += 1
        
        messageSurface = self.notifyFont.render(self.lastNotification[breakupIndex:].lstrip(), True, DARK_RED)
        self.screen.blit(messageSurface, (self.messageLocation[0], self.messageLocation[1] + lineNum * self.notifyFont.get_height()))
    
    ##
    #drawConstruction
    #Description: Draws a non-moving structure of the specified type to the specified location on the game board.
    #
    #Parameters:
    #   item - an object subclassed from Construction.(Construction or Building)
    #   position - a tuple that indicates a cell on the board. This will be converted to a pixel location.((int,int))
    ##
    def drawConstruction(self, item, position):
        Xpixel = CELL_SPACING * (position[0] + 1) + CELL_SIZE.width * position[0]
        Ypixel = CELL_SPACING * (position[1] + 1) + CELL_SIZE.height * position[1]
        constrTex = self.constructionTexs[item.type].copy()
        background = pygame.Surface(CELL_SIZE.size)
        if type(item) is Building:
            background.fill(LIGHT_RED if item.player == PLAYER_ONE else LIGHT_BLUE)
            constrTex.set_colorkey(self.playerAlpha)
        else:
            background.fill(WHITE)
        background.blit(constrTex, (0, 0))
        background.set_colorkey(WHITE)
        self.screen.blit(background, (Xpixel, Ypixel))
    
    ##
    #drawAnt
    #Description: Draws an Ant of the specified type to the specified location on the game board.
    #
    #Parameters:
    #   ant - an Ant object.(Ant)
    #   position - a tuple that indicates a cell on the board. This will be converted to a pixel location.((int,int))
    ##
    def drawAnt(self, ant, position):
        Xpixel = CELL_SPACING * (position[0] + 1) + CELL_SIZE.width * position[0]
        Ypixel = CELL_SPACING * (position[1] + 1) + CELL_SIZE.height * position[1]
        #Start by drawing the ant itself onto a solid player color background.
        #The player color should only show in areas of the playerAlpha color.
        background = pygame.Surface(CELL_SIZE.size)
        background.fill(LIGHT_RED if ant.player == PLAYER_ONE else LIGHT_BLUE)
        background.blit(self.antTexs[ant.type], (0, 0))
        background.set_colorkey(WHITE)
        #Then draw the ant itself.
        self.screen.blit(background, (Xpixel, Ypixel))
        #Draw current health across the top from the left as a series of boxes
        boxWidth = 7;
        boxHeight = 6;
        healthBox = Rect(0,0,boxWidth-2,boxHeight-2)
        healthPerimiter = Rect(0,0,boxWidth,boxHeight)
        for x in xrange(0, UNIT_STATS[ant.type][HEALTH]):
            pygame.draw.rect(self.screen, DARK_GREEN, healthPerimiter.move(Xpixel + CELL_SIZE.width - boxWidth * (x + 1) - 1, Ypixel + 1))
        for x in xrange(0, ant.health):
            pygame.draw.rect(self.screen, LIGHT_GREEN, healthBox.move(Xpixel + CELL_SIZE.width - boxWidth * (x + 1), Ypixel + 2))
        for x in xrange(ant.health, UNIT_STATS[ant.type][HEALTH]):
            pygame.draw.rect(self.screen, DARK_RED, healthBox.move(Xpixel + CELL_SIZE.width - boxWidth * (x + 1), Ypixel + 2))
        #Draw isCarrying marker in lower right
        if ant.carrying:
            XoffsetCarry = CELL_SIZE.width - self.isCarryingTex.get_width()
            YoffsetCarry = CELL_SIZE.height - self.isCarryingTex.get_height()
            self.screen.blit(self.isCarryingTex, (Xpixel + XoffsetCarry, Ypixel + YoffsetCarry))
        #Draw hasMoved marker as a shade across the image
        if ant.hasMoved:
            self.shaderTex.fill(BLACK)
            self.screen.blit(self.shaderTex, (Xpixel, Ypixel))
    
    ##
    #drawCaptureHealths
    #Description: draw the health of the anthill that's about to die.
    #
    #Parameters:
    #   health - the amount of health to draw.(int, int)
    ##
    def drawCaptureHealths(self, health):
        label1 = self.monsterFont.render(str(health[0]), True, DARK_BLUE, WHITE)
        label2 = self.monsterFont.render(str(health[1]), True, DARK_RED, WHITE)
        #Find out where to put the text onscreen.
        label1Size = label1.get_size()
        label2Size = label2.get_size()
        label1Center = (label1Size[0] / 2, label1Size[1] / 2)
        label2Center = (label2Size[0] / 2, label2Size[1] / 2)
        boardCenter = ((self.screen.get_width() - self.buttonArea.width) / 2, self.screen.get_height() / 2)
        #Initialize destinations for the sake of scope.
        destination1 = 0
        destination2 = 0
        #Change the settings of the text surface to look the way it should.
        label1.set_colorkey(WHITE)
        label2.set_colorkey(WHITE)
        label1.set_alpha(50)
        label2.set_alpha(50)
        #Find out which case occured. Both players have anthills getting captured, or just one.
        if health[0] != -1 and health[1] != -1:
            #Make destinations offset for both units.
            destination1 = subtractCoords(boardCenter, (label1Size[0], label1Center[1]))
            destination2 = subtractCoords(boardCenter, (0, label2Center[1]))
            #Draw the text surface.
            self.screen.blit(label1, destination1)
            self.screen.blit(label2, destination2)
        elif health[0] != -1:
            destination1 = subtractCoords(boardCenter, label1Center)
            destination2 = 0
            #Draw the text surface.
            self.screen.blit(label1, destination1)
        elif health[1] != -1:
            destination1 = 0
            destination2 = subtractCoords(boardCenter, label2Center)
            #Draw the text surface.
            self.screen.blit(label2, destination2)
        else:
            print "Oh my gawd my code broke in UserInterface.drawCaptureHealth"
    
    ##
    #drawCaptureHealth
    #Description: draw the health of the ant tunnel that's about to die.
    #
    #Parameters:
    #   health - the amount of health to draw.(int)
    #   coords - the board coordinates to draw at.((int,int))
    #   player - the playerID of the player being drawn for.(int)
    ##
    def drawCaptureHealth(self, health, coords, player):
        #Create and add settings to the text we want to draw. Background needs to be set so we don't have per pixel alpha.
        label = self.captureFont.render(str(health), True, LIGHT_RED if player == PLAYER_ONE else LIGHT_BLUE, WHITE)
        label.set_colorkey(WHITE)
        label.set_alpha(100)
        #Find where to place the text.
        sizeDiff = subtractCoords(CELL_SIZE.size, subtractCoords(label.get_size(), (0, 10)))
        halfDiff = (sizeDiff[0] / 2, sizeDiff[1] / 2)
        #Draw the text.
        self.screen.blit(label, addCoords(coords, halfDiff))
    
    ##
    #drawButton
    #Description: Draws a button to the board. All necessary information is contained in self.buttons under the given key.
    #
    #Parameters:
    #   key - a key in the self.buttons hash table, known in Python as a Dictionary.(string)
    ##
    def drawButton(self, key, buttons):
        label = self.gameFont.render(key, True, BLACK)
        offset = subtractCoords(self.buttonRect.center, label.get_rect().center)
        self.screen.blit(self.buttonTextures[buttons[key][1]], buttons[key][0])
        self.screen.blit(label, addCoords(buttons[key][0], offset))
    
    ##
    #drawScoreBoard
    #Description: Draws the scores of both players as given.
    #
    #Parameters:
    #   player1Score - the integer value of player 1's food stock.(int)
    #   player2Score - the integer value of player 2's food stock.(int)
    ##
    def drawScoreBoard(self, player1Score, player2Score):
        label1 = self.gameFont.render("Player 1: " + str(player1Score) + " food", True, BLACK)
        label2 = self.gameFont.render("Player 2: " + str(player2Score) + " food", True, BLACK)
        self.screen.blit(label1, self.scoreLocation)
        self.screen.blit(label2, addCoords(self.scoreLocation, (0, label2.get_rect().height)))
    
    ##
    #drawTextBox
    #Description: Draws a box that holds text to the buttonArea.
    ##
    def drawTextBox(self):
        #Start by drawing the text box in the appropriate color.
        pygame.draw.rect(self.screen, DARK_RED if self.textBoxContent == '' else LIGHT_GREEN, self.buttonRect.move(self.textPosition))
        #Then draw the number in the text box.
        label = self.gameFont.render(self.textBoxContent + ('|' if self.boxSelected else ''), True, BLACK)
        offset = subtractCoords(self.buttonRect.center, label.get_rect().center)
        self.screen.blit(label, addCoords(self.textPosition, offset))
        #Finally, draw the text box title.
        boxLabel = self.gameFont.render("Games to play:", True, BLACK)
        boxLabelOffset = (0, - boxLabel.get_height() - FIELD_SPACING)
        self.screen.blit(boxLabel, addCoords(self.textPosition, boxLabelOffset))
    
    ##
    #drawTable
    #Description: Draws the tournament score table from a list of (author string, wins int, losses int, ties int) tuples.
    ##
    def drawTable(self):
        XStartPixel = 50
        YStartPixel = self.screen.get_height() / 2 - len(self.tournamentScores) * (self.tournFont.get_height() + FIELD_SPACING) / 2 - CELL_SPACING
        if YStartPixel < 0:
            YStartPixel = 0
        #Prepend the column headers to the tournamentScores list, so that we can draw the entire table without special cases.
        scores = [('Author', 'Wins', 'Losses')] + self.tournamentScores
        #Find the longest string for each column
        lengths = [0 for i in range(0, len(scores[0]) + 1)]
        for score in scores:
            for index in range(0, len(score)):
                if self.tournFont.size(str(score[index]))[0] > lengths[index+1]:
                    lengths[index + 1] = self.tournFont.size(str(score[index]))[0]
        #add some padding for readability
        lengths = [x + 10 for x in lengths]
                    
        #Draw the table itself
        for index in range(0, len(scores)):
            for innerDex in range(0, len(scores[index])):
                Xoffset = 0 if innerDex == 0 else reduce(lambda x,y: x+y, lengths[:innerDex+1])
                tempX = XStartPixel + Xoffset + FIELD_SPACING * innerDex
                tempY = YStartPixel + index * (self.tournFont.get_height() + FIELD_SPACING)
                label = self.tournFont.render(str(scores[index][innerDex]), True, BLACK)
                self.screen.blit(label, (tempX, tempY))

        #Add some underlines under the table headers
        Yoffset = YStartPixel + self.tournFont.get_height()
        for index in range(1, len(lengths)):
            Xoffset = 0 if index == 0 else reduce(lambda x,y: x+y, lengths[:index])
            Xspacing = -1 * FIELD_SPACING if index == 1 else FIELD_SPACING * (index - 1)
            startX = XStartPixel + Xoffset + Xspacing
            endX = startX + lengths[index]
            pygame.draw.line(self.screen, BLACK, (startX, Yoffset), (endX, Yoffset))

        #Draw the elapsed time
        Yoffset = YStartPixel + len(scores) * (self.tournFont.get_height() + FIELD_SPACING)
        if (self.tournamentInProgress):
            self.tournamentElapsed = time.clock() - self.tournamentStartTime
        elapsedMessage = "Elapsed time: "
        elapsedColor = DARK_RED
        if (not self.tournamentInProgress):
            elapsedMessage = "Final time: "
            elapsedColor = DARK_GREEN
        elapsedMessage += str(int(self.tournamentElapsed) / 60) + "m "
        elapsedMessage += str(int(self.tournamentElapsed) % 60) + "s"
        label = self.tournFont.render(elapsedMessage, True, elapsedColor)
        self.screen.blit(label, (XStartPixel, Yoffset))
        
    
    ##
    #drawAICheckList
    #Description: draws a checklist of all AIs that are available to select.
    #
    #Parameters:
    #   mode - The current game mode.(int)
    ##
    def drawAIChecklist(self, mode):
        #Replace the AIList with a shorter one if in human mode because I don't want to draw the human player in the checklist.
        safeList = self.allAIs[1:] if mode == HUMAN_MODE else self.allAIs
        #Find out how many AIs can be put in a column.
        maxRows = (self.screen.get_height() - 100) / (self.checkBoxRect.height + FIELD_SPACING)
        secondColumnOffset = (self.screen.get_width() - self.buttonArea.width) / 2
        #Prevent the list from overflowing on the screen.
        safeList = safeList[:2 * maxRows] if len(safeList) > maxRows * 2 else safeList
        #Decide on where the checkList should start on screen.
        XStartPixel = 50
        YStartPixel = self.screen.get_height() / 2 - min(len(safeList), maxRows) * (self.checkBoxRect.height + FIELD_SPACING) / 2
        if YStartPixel < 0:
            YStartPixel = 0
        #Draw the checkList.
        for index in range(0, len(safeList)):
            tempX = XStartPixel + (secondColumnOffset if index >= maxRows else 0)
            tempY = YStartPixel + index % maxRows * (self.checkBoxRect.height + FIELD_SPACING)
            self.screen.blit(self.checkBoxTextures[safeList[index][1]], (tempX, tempY))
            label = self.notifyFont.render(str(safeList[index][0].author), True, BLACK)
            self.screen.blit(label, (tempX + self.checkBoxRect.width + FIELD_SPACING, tempY + (self.checkBoxRect.height - self.notifyFont.get_height()) / 2))
        #Find out where the button should go.
        buttonIndex = maxRows if maxRows < len(safeList) else len(safeList)
        buttonY = YStartPixel + buttonIndex * (self.checkBoxRect.height + FIELD_SPACING)
        #Reset the location of the button.
        key = self.submitSelected.keys()[0]
        self.submitSelected[key][0] = (XStartPixel, buttonY)
        #And last but not least, draw the "Submit Selected" button below the end of the first column.
        self.drawButton(key, self.submitSelected)
    
    ##
    #drawCell
    #Description: Draws a cell. The basic component of the board.
    #
    #Parameters:
    #   currentLoc - The Location to be drawn in this cell. Locations can have
    #       ants and buildings attached, so those will be drawn if present.(Location)
    ##
    def drawCell(self, currentLoc):
        col = currentLoc.coords[0]
        row = currentLoc.coords[1]
        #Find the x y coordinates that this column and row map to.
        Xpixel = CELL_SPACING * (col + 1) + CELL_SIZE.width * col
        Ypixel = CELL_SPACING * (row + 1) + CELL_SIZE.height * row
        #Create a Rect that shows up if the square is selected.
        shadeWidth = CELL_SPACING / 2 * 2 + CELL_SIZE.width
        shadeHeight = CELL_SPACING  / 2 * 2 + CELL_SIZE.height
        shadeRect = Rect(0, 0, shadeWidth, shadeHeight)
        #Find the X and Y coordinates to draw the shade at.
        shadeXpixel = Xpixel - CELL_SPACING / 2
        shadeYpixel = Ypixel - CELL_SPACING / 2
        #Create a True/False list indicating which shaders should be drawn
        drawList = []
        colorList = [DARK_GREEN, LIGHT_GREEN, GOLDENROD, LIGHT_RED]
        if self.coordList != []:
            #Draw the shadeRect if currentLoc is in coordList
            drawList.append(True if currentLoc.coords in self.coordList[:-1] else False)
            #Draw brighter if the currentLoc is the last move selected
            drawList.append(True if currentLoc.coords == self.coordList[-1] else False)
        else:
            drawList += [False, False]
        #Also shade potential moves.
        drawList.append(True if currentLoc.coords in self.validCoordList else False)
        #Draw the shade for a cell highlighted for attacks if currentLoc is in attackList
        drawList.append(True if currentLoc.coords in self.attackList else False)
        #Draw the background shades
        for index in xrange(0, len(drawList)):
            if drawList[index]:
                pygame.draw.rect(self.screen, colorList[index], shadeRect.move(shadeXpixel, shadeYpixel))
        #Draw the cell itself.
        self.screen.blit(self.terrainTex, CELL_SIZE.move(Xpixel, Ypixel))
        #Draw what's in this cell
        if currentLoc.constr != None:
            self.drawConstruction(currentLoc.constr, (col, row))
        if currentLoc.ant != None:
            self.drawAnt(currentLoc.ant, (col, row))
        #Draw the translucent foreground shades.
        for index in xrange(0, len(drawList)):
            if drawList[index]:
                self.shaderTex.fill(colorList[index])
                self.screen.blit(self.shaderTex, CELL_SIZE.move(Xpixel, Ypixel))
        #Draw the captureHealth of any ant tunnel being captured.
        captureVal = self.getCaptureValue(currentLoc)
        if captureVal != -1:
            self.drawCaptureHealth(captureVal, (Xpixel, Ypixel), currentLoc.constr.player)

    ##
    #drawBoard
    #Description: This is the bread and butter of the UserInterface class. Everything
    #   starts drawing from here.
    #
    #Parameters:
    #   currentState - The state of the board to draw as a GameState.(GameState)
    #   mode - The current game mode.(int)
    ##
    def drawBoard(self, currentState, mode):
        self.handleEvents(mode)
        if self.choosingAIs:
            self.screen.fill(WHITE)
            self.drawAIChecklist(mode)
            self.drawNotification()
        elif mode == TOURNAMENT_MODE:
            self.screen.fill(WHITE)
            #Draw the box into which the user can enter the number of games they want to play.
            self.drawTextBox()
            #Draw the table with columns author/win/loss/tie
            self.drawTable()
        else:
            self.screen.fill(BLACK)
            #Draw the menu area.
            pygame.draw.rect(self.screen, WHITE, self.buttonArea)
            #Draw the player color indicator boxes.
            pygame.draw.rect(self.screen, LIGHT_RED, self.outerRect)
            pygame.draw.rect(self.screen, BLACK, self.innerRect.move((CELL_SPACING, CELL_SPACING)))
            pygame.draw.rect(self.screen, LIGHT_BLUE, self.outerRect.move((0, self.p2RectYOffset)))
            pygame.draw.rect(self.screen, BLACK, self.innerRect.move((CELL_SPACING, CELL_SPACING + self.p2RectYOffset)))
            #Draw the cells themselves.
            for col in xrange(0, len(currentState.board)):
                for row in xrange(0, len(currentState.board[col])):
                    self.drawCell(currentState.board[col][row])
            #Draw the captureHealth of any anthill being captured.
            captureVals = self.getCaptureValues(currentState)
            if captureVals[0] != -1 or captureVals[1] != -1:
                self.drawCaptureHealths(captureVals)
            #Make sure we draw the right buttons
            relButtons = {} if mode == None else self.humanButtons if mode == HUMAN_MODE else self.aiButtons
            if self.buildAntMenu == True:
                relButtons = self.antButtons
            #Draw the context buttons
            for key in relButtons:
                self.drawButton(key, relButtons)
            #I can't put this draw method outside of drawBoard, but it shouldn't work this way.
            self.drawScoreBoard(currentState.inventories[0].foodCount, currentState.inventories[1].foodCount)
            #Draw notifications just above menu buttons.
            self.drawNotification()
        #Draw the basic buttons
        for key in self.buttons:
            self.drawButton(key, self.buttons)
        #Show everything I've drawn by posting self.screen to the monitor.
        pygame.display.flip()
    
    ##
    #handleButton
    #Description: Handles the finer details of what happens when a user is clicking on buttons.
    #   The button will only be counted as clicked if the user both presses and releases a mouse
    #   button while hovering over the game button. If clicked, a callback function will be used
    #   to notify Game.py.
    #
    #Parameters:
    #   key - a key in the self.buttons hash table, known in Python as a Dictionary.(string)
    #   released - an integer/boolean that represents the state of the button: 1 if the button
    #       is released, or 0 if the button is depressed.(int)
    ##
    def handleButton(self, key, released, buttons):
        if buttons[key][1] != released and released == 1:
            buttons[key][2]()
        
        buttons[key][1] = released
    
    ##
    #handleAICheckList
    #Description: handles any MOUSE_BUTTON_DOWN events pertaining to the AI
    #   check list.
    #
    #Parameters:
    #   event - All information about the event. We already know its type due
    #       to the fact we are in this method, but position of the click is
    #       also important.(pygame.Event)
    #   mode - The current game mode.(int)
    ##
    def handleAICheckList(self, event, mode):
        #Replace the AIList with a shorter one if in human mode because find the human player in the checklist.
        safeList = self.allAIs[1:] if mode == HUMAN_MODE else self.allAIs
        #Find out how many AIs can be in a column.
        maxRows = (self.screen.get_height() - 100) / (self.checkBoxRect.height + FIELD_SPACING)
        secondColumnOffset = (self.screen.get_width() - self.buttonArea.width) / 2
        #The list can't overflow on the screen.
        safeList = safeList[:2 * maxRows] if len(safeList) > maxRows * 2 else safeList
        #Check if a column was clicked (x position of mouse may result in a checkbox being clicked)
        columnClicked = -1
        if event.pos[0] - 50 > 0 and event.pos[0] - 50 < self.checkBoxRect.width:
            columnClicked = 0
        elif event.pos[0] - 50 - secondColumnOffset > 0 and event.pos[0] - 50 - secondColumnOffset < self.checkBoxRect.width:
            columnClicked = 1
        #If a column was clicked, check if a row was clicked.
        if columnClicked > -1:
            yStart = self.screen.get_height() / 2 - min(len(safeList), maxRows) * (self.checkBoxRect.height + FIELD_SPACING) / 2
            if (event.pos[1] - yStart + FIELD_SPACING) % (self.checkBoxRect.height + FIELD_SPACING) > FIELD_SPACING:
                checkIndex = (event.pos[1] - yStart) / (self.checkBoxRect.height + FIELD_SPACING)
                #If the checkbox clicked was in a column other than the first, add the implicit rows skipped.
                checkIndex += columnClicked * maxRows
                #If the checkindex falls within the list, go ahead and call the callback.
                if checkIndex < len(safeList) and checkIndex >= 0:
                    #If the mode is human mode, there is an invisible player (the human) that I don't want clicked.
                    checkIndex += 1 if mode == HUMAN_MODE else 0
                    self.checkBoxClicked(checkIndex)
    
    ##
    #handleHotkey
    #Description: Handles any key presses in place of using the mouse to press
    #   buttons. All hotkeys are hard coded in here.
    #
    #Parameters:
    #   mode - The current game mode.(int)
    #   char - The key that was pressed. Actually passed as a string, but since
    #       each keyboard event is spawned by one key, the string length is
    #       always 1.(string)
    ##
    def handleHotkey(self, mode, char):
        if char == '\r':
            self.buttons['Start'][-1]()
        elif mode == HUMAN_MODE:
            if not self.buildAntMenu:
                if char == ' ':
                    self.humanButtons['End'][-1]()
                elif char == 'b':
                    self.humanButtons['Build'][-1]()
            else:
                if char == 'w':
                    self.antButtons['Worker'][-1]()
                elif char == 'd':
                    self.antButtons['Drone'][-1]()
                elif char == 's':
                    self.antButtons['Soldier'][-1]()
                elif char == 'r':
                    self.antButtons['Ranged Soldier'][-1]()
                elif char == 'n':
                    self.antButtons['None'][-1]()
        elif mode == AI_MODE:
            if char == 'n':
                self.aiButtons['Next'][-1]()
            elif char == 'c':
                self.aiButtons['Continue'][-1]()
    
    ##
    #handleEvents
    #Description: Handles the more generic mouse movements. Finds out what has been
    #   clicked, and either calls handleButton on the activated button, or uses a
    #   callback to tell the HumanPlayer what the human clicked.
    #
    #Pararmeters:
    #   mode - The current game mode.(int)
    ##
    def handleEvents(self, mode):
        #Make sure we check the right buttons
        relButtons = {} if self.choosingAIs else self.humanButtons if mode == HUMAN_MODE else self.aiButtons if mode == AI_MODE else {}
        #It should be impossible for self.buildAntMenu to be True unless mode is HUMAN_MODE and AIs have already been chosen.
        if mode == HUMAN_MODE and self.buildAntMenu:
            relButtons = self.antButtons
        #Check what to do for each event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and time.clock() - self.lastClicked > self.clickCooldown:
                self.lastClicked = time.clock()
                #Start by checking the basic buttons that always get drawn
                for key in self.buttons:
                    if self.buttonRect.move(self.buttons[key][0]).collidepoint(event.pos):
                        self.handleButton(key, 0, self.buttons)
                #Then check the buttons that congregate at the top of the screen, and change based on context
                for key in relButtons:
                    if self.buttonRect.move(relButtons[key][0]).collidepoint(event.pos):
                        self.handleButton(key, 0, relButtons)
                #Check to see if text box should be selected or deselected
                if mode == TOURNAMENT_MODE and self.buttonRect.move(self.textPosition).collidepoint(pygame.mouse.get_pos()):
                    self.boxSelected = True
                else:
                    self.boxSelected = False
                #Additionally, check if a cell on the board has been clicked.
                if mode != TOURNAMENT_MODE and not self.choosingAIs:
                    if event.pos[0] % (CELL_SPACING + CELL_SIZE.width) > CELL_SPACING and event.pos[1] % (CELL_SPACING + CELL_SIZE.height) > CELL_SPACING:
                        x = event.pos[0] / (CELL_SPACING + CELL_SIZE.width)
                        y = event.pos[1] / (CELL_SPACING + CELL_SIZE.height)
                        if x < BOARD_SIZE.width and y < BOARD_SIZE.height:
                            self.locationClicked((x, y))
                elif self.choosingAIs:
                    self.handleAICheckList(event, mode)
                    #Handle the AI selecting button.
                    AIKey = self.submitSelected.keys()[0]
                    if self.buttonRect.move(self.submitSelected[AIKey][0]).collidepoint(event.pos):
                        self.handleButton(AIKey, 0, self.submitSelected)
            elif event.type == pygame.MOUSEBUTTONUP:
                #Start by checking the basic buttons that always get drawn
                for key in self.buttons:
                    if self.buttonRect.move(self.buttons[key][0]).collidepoint(event.pos):
                        self.handleButton(key, 1, self.buttons)
                #Then check the buttons that congregate at the top of the screen, and change based on context
                for key in relButtons:
                    if self.buttonRect.move(relButtons[key][0]).collidepoint(event.pos):
                        self.handleButton(key, 1, relButtons)
                #Handle the AI selecting button.
                if self.choosingAIs:
                    AIKey = self.submitSelected.keys()[0]
                    if self.buttonRect.move(self.submitSelected[AIKey][0]).collidepoint(event.pos):
                        self.handleButton(AIKey, 1, self.submitSelected)
                #Check to see if text box should be selected or deselected
                if mode == TOURNAMENT_MODE and self.buttonRect.move(self.textPosition).collidepoint(pygame.mouse.get_pos()):
                    boxSelected = True
                else:
                    boxSelected = False
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                #Start by checking the basic buttons that always get drawn
                for key in self.buttons:
                    if self.buttonRect.move(self.buttons[key][0]).collidepoint(addCoords(event.pos, event.rel)):
                        self.buttons[key][1] = 0
                    else:
                        self.buttons[key][1] = 1
                #Then check the buttons that congregate at the top of the screen, and change based on context
                for key in relButtons:
                    if self.buttonRect.move(relButtons[key][0]).collidepoint(addCoords(event.pos, event.rel)):
                        relButtons[key][1] = 0
                    else:
                        relButtons[key][1] = 1
                #Handle the AI selecting button.
                if self.choosingAIs:
                    AIKey = self.submitSelected.keys()[0]
                    if self.buttonRect.move(self.submitSelected[AIKey][0]).collidepoint(event.pos):
                        self.submitSelected[AIKey][1] = 0
                    else:
                        self.submitSelected[AIKey][1] = 1
            elif self.boxSelected and event.type == KEYDOWN:
                if str(event.unicode) in [str(i) for i in range(0, 10)]:
                    self.textBoxContent += str(event.unicode)
                elif event.key == 8 and self.textBoxContent != '':
                    self.textBoxContent = self.textBoxContent[:-1]
            elif event.type == KEYDOWN:
                self.handleHotkey(mode, str(event.unicode))
    
    ##
    #findButtonCoords
    #Description: Finds the coordinates that button should be placed at based on its index from the top or bottom of the screen.
    #
    #Parameters:
    #   index - There are reserved spaces for buttons, allowing for a certain buffer zone between each button.
    #       This is the index from the top or bottom of the screen that this button should be placed at.(int)
    #   isTop - True if the index be counted from the top of the screen. False otherwise.(boolean)
    #
    #Returns: The coordinates of the button.
    ##
    def findButtonCoords(self, index, isTop):
        buttonSpacing = 2 * CELL_SPACING
        buttonX = self.screen.get_width() - self.buttonRect.width - buttonSpacing
        if isTop:
            buttonY = (index + 1) * buttonSpacing + index * self.buttonRect.height
            return buttonX, buttonY
        else:
            buttonY = self.screen.get_height() - (index + 1) * (buttonSpacing + self.buttonRect.height)
            return buttonX, buttonY
    
    ##
    #initAssets
    #Description: initializes everything the UserInterface needs to render a game state properly.
    ##
    def initAssets(self):
        global CELL_SIZE
        #Declare the name of the folder that all textures are in.
        texFolder = "Textures"
        #Load textures as Surfaces. Should convert these surfaces later for optimal speed.
        self.constructionTexs = []
        self.constructionTexs.append(pygame.image.load(os.path.join(texFolder, "anthill.bmp")))
        self.constructionTexs.append(pygame.image.load(os.path.join(texFolder, "antTunnel.bmp")))
        self.constructionTexs.append(pygame.image.load(os.path.join(texFolder, "grass.bmp")))
        self.constructionTexs.append(pygame.image.load(os.path.join(texFolder, "food.bmp")))
        self.antTexs = []
        self.antTexs.append(pygame.image.load(os.path.join(texFolder, "queen.bmp")))
        self.antTexs.append(pygame.image.load(os.path.join(texFolder, "worker.bmp")))
        self.antTexs.append(pygame.image.load(os.path.join(texFolder, "drone.bmp")))
        self.antTexs.append(pygame.image.load(os.path.join(texFolder, "direct.bmp")))
        self.antTexs.append(pygame.image.load(os.path.join(texFolder, "indirect.bmp")))
        #Load isCarrying and texture, which will allow players to see the conditions of their ants.
        self.isCarryingTex = pygame.image.load(os.path.join(texFolder, "isCarrying.bmp"))
        #Load the texture used for terrain (ground).
        self.terrainTex = pygame.image.load(os.path.join(texFolder, "terrain.bmp"))
        #CheckBox textures
        self.checkBoxTextures = []
        self.checkBoxTextures.append(pygame.image.load(os.path.join(texFolder, "unchecked.bmp")))
        self.checkBoxTextures.append(pygame.image.load(os.path.join(texFolder, "checked.bmp")))
        #CheckBox rectangle
        self.checkBoxRect = self.checkBoxTextures[0].get_rect()
        #Button textures
        self.buttonTextures = []
        self.buttonTextures.append(pygame.image.load(os.path.join(texFolder, "buttonDown.bmp")))
        self.buttonTextures.append(pygame.image.load(os.path.join(texFolder, "buttonUp.bmp")))
        #Button rectangle
        self.buttonRect = self.buttonTextures[0].get_rect()
        #Make CELL_SIZE equal to the size of an ant image.
        CELL_SIZE = self.constructionTexs[0].get_rect()
        #Create shaderTex, which will be used to translucently shade ants.
        self.shaderTex = pygame.Surface((CELL_SIZE.width, CELL_SIZE.height))
        #Set the color that will be used as an alpha transparency to let player colors shine through.
        self.playerAlpha = OFF_BLACK
        #Make White transparent (alpha 0) for most textures (well, buttons don't actually need it).
        for construction in self.constructionTexs:
            construction.set_colorkey(WHITE)
        #Ants don't get posted directly to the board. They go to an intermediate
        #texture of their player color, so they don't need a WHITE alpha.
        for ant in self.antTexs:
            ant.set_colorkey(self.playerAlpha)
        self.isCarryingTex.set_colorkey(WHITE)
        self.shaderTex.set_alpha(50)
        #Set up fonts.
        pygame.font.init()
        self.statFont = pygame.font.Font(None, 15)
        self.notifyFont = pygame.font.Font(None, 16)
        self.gameFont = pygame.font.Font(None, 25)
        self.tournFont = pygame.font.Font(None, 25)
        self.captureFont = pygame.font.Font(None, 130)
        self.monsterFont = pygame.font.Font(None, 300)
        #Where should scores be drawn?
        self.scoreLocation = self.findButtonCoords(0, True)
        #Where should notifications be drawn?
        self.messageLocation = self.findButtonCoords(5, False)
        #Where should non-board stuff be placed (an area for buttons, notifications, and scores)?
        buttonAreaWidth = self.buttonRect.width + 4 * CELL_SPACING
        self.buttonArea = Rect(self.screen.get_width() - buttonAreaWidth, 0, buttonAreaWidth, self.screen.get_height())
        #Button statistics for basic buttons in order: x, y, buttonState(pressed/released)
        self.buttons = {
        'Start':[self.findButtonCoords(3.5, False), 1, self.startGame],
        'Tournament':[self.findButtonCoords(2, False), 1, self.gameModeTournament],
        'Human vs AI':[self.findButtonCoords(1, False), 1, self.gameModeHumanAI],
        'AI vs AI':[self.findButtonCoords(0, False), 1, self.gameModeAIAI]
        }
        #Initial values for buttons in human vs AI mode.
        self.humanButtons = {
        'Build':[self.findButtonCoords(1, True), 1, self.submitBuild],
        'End':[self.findButtonCoords(2, True), 1, self.submitEndTurn]
        }
        #Initial values for buttons in human vs AI mode.
        self.aiButtons = {
        'Next':[self.findButtonCoords(1, True), 1, self.submitNext],
        'Continue':[self.findButtonCoords(2, True), 1, self.submitContinue]
        }
        #Initial values for build ant buttons.
        self.antButtons = {
        'Worker':[self.findButtonCoords(1, True), 1, self.submitWorker],
        'Drone':[self.findButtonCoords(2, True), 1, self.submitDrone],
        'Soldier':[self.findButtonCoords(3, True), 1, self.submitDSoldier],
        'Ranged Soldier':[self.findButtonCoords(4, True), 1, self.submitISoldier],
        'None':[self.findButtonCoords(5, True), 1, self.submitNoBuild]
        }
        #Initial value for submit button for AI checklist.
        self.submitSelected = {
        'Submit AIs':[(0,0), 1, self.submitSelectedAIs]
        }
        #Define the player color indicator boxes.
        bw = BOARD_SIZE.width
        bh = BOARD_SIZE.height
        cw = CELL_SIZE.width
        ch = CELL_SIZE.height
        cs = CELL_SPACING
        self.outerRect = Rect(0, 0, bw * (cw + cs) + cs, (bh / 2 - 1) * (ch + cs) + cs)
        self.innerRect = Rect(0, 0, bw * (cw + cs) - cs, (bh / 2 - 1) * (ch + cs) - cs)
        self.p2RectYOffset = (bh / 2 + 1) * (cw + cs)
        #Properties of our single text box
        self.textPosition = self.findButtonCoords(2, True)
        self.textBoxContent = ''
        self.boxSelected = False
        #Initial vaue for callback function that will be used to get cell clicks in game
        self.locationCallback = self.locationClicked
        #Draw the ant build menu?
        self.buildAntMenu = False
        #Initial user notification is empty, since we assume the user hasn't made a mistake in opening the program. Not that the program could detect that anyway.
        self.lastNotification = ''
        #Initial coordList so I know what to shade
        self.coordList = []
        #Initial "Where can the ant go" list, for the same reason as above.
        self.validCoordList = []
        #Cells that should be highlighted for attacks
        self.attackList = []
        #Initializing tournament scores
        self.tournamentScores = []
        #Variables used to track elapsed time during tournaments
        self.tournamentStartTime = time.clock()
        self.tournamentElapsed = 0.0
        self.tournamentInProgress = False
        #Find out if user is choosing AIs
        self.choosingAIs = False
        #Set an initial value for the list of AIs that the game uses.
        self.allAIs = []
        #Set a minimmum time between accepted clicks.
        self.clickCooldown = 0.15
        self.lastClicked = time.clock()
