# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

import random
from AI import AI
from Action import Action
from collections import defaultdict
import random


class Tile():
    def __init__(self, m=False, c=True, f=False, xCoord=-1, yCoord=-1, number=-1):
        self.mine = m
        self.covered = c
        self.flag = f
        self.number = number
        self.x = xCoord
        self.y = yCoord

    def __repr__(self):
        return 'Tile at ({x},{y}):n={n},c={c},f={f},m={m}'.format(x=self.x, y=self.y, n=self.number,
                                                                  c=self.covered, f=self.flag, m=self.mine)

    def __str__(self):
        return 'Tile({x}, {y})'.format(x=self.x, y=self.y)

    def __eq__(self, other):
        if self.mine == other.mine and \
                self.covered == other.covered and \
                self.flag == other.flag and \
                self.number == other.number and \
                self.x == other.x and \
                self.y == other.y:
            return True
        return False


class MyAI(AI):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################

        self.__rowDimension = rowDimension
        self.__colDimension = colDimension
        self.__moveCount = 0
        self.__startX = startX
        self.__startY = startY
        self.__lastX = startX
        self.__lastY = startY
        self.__lastTile = Tile()
        self.__moveList = []
        self.__frontier = defaultdict(list)
        self.__uncovered = {}
        self.__totalTiles = rowDimension * colDimension
        self.__totalMines = totalMines
        self.__totalUncovered = 0

        # Creates an empty board that we will update
        self.__board = [[Tile(xCoord=j, yCoord=i) for i in range(self.__rowDimension)] for j in
                        range(self.__colDimension)]

    #############################################
    #			 BOARD REPRESENTATION			#
    #############################################
    def __printWorld(self) -> None:
        """ Prints to console information about Minesweeper World """
        self.__printBoardInfo()

    def __printBoardInfo(self) -> None:
        """ Print board for debugging """
        print("\nThis is what we think the board looks like:")

        board_as_string = ""
        print("", end=" ")
        for r in range(self.__rowDimension - 1, -1, -1):
            print(str(r).ljust(2) + '|', end=" ")
            for c in range(self.__colDimension):
                self.__printTileInfo(c, r)
            if (r != 0):
                print('\n', end=" ")

        column_label = "     "
        column_border = "   "
        for c in range(0, self.__colDimension):
            column_border += "---"
            column_label += str(c).ljust(3)
        print(board_as_string)
        print(column_border)
        print(column_label)

    def __printTileInfo(self, c: int, r: int) -> None:
        """ Checks tile attributes and prints accordingly """
        if not self.__board[c][r].covered and self.__board[c][r].mine:
            print('B ', end=" ")
        elif self.__board[c][r].flag:
            print('? ', end=" ")
        elif not self.__board[c][r].covered:
            print(str(self.__board[c][r].number) + ' ', end=" ")
        elif self.__board[c][r].covered:
            print('. ', end=" ")

    def __isInBounds(self, c: int, r: int) -> bool:
        """ Returns true if given coordinates are within the boundaries of the game board """
        if c < self.__colDimension and c >= 0 and r < self.__rowDimension and r >= 0:
            return True
        return False

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################

    def getAction(self, number: int) -> "Action Object":
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################
        def clearSurrounding(t: Tile) -> None:
            """We know that the given coord is a 0, so uncover the surroundings"""
            s = getSurroundings(t)
            for tile in s:
                if tile.covered and not tile.flag and \
                        (tile.x, tile.y) not in self.__uncovered.keys() and \
                        tile not in [move[1] for move in self.__moveList]:
                    self.__moveList.append(tuple([Action(AI.Action.UNCOVER, tile.x, tile.y), tile]))

        def flagObvious() -> None:
            """Adds flag moves to the move list"""
            #  Go through frontier, find all the flags, and add them to the front of the queue
            for n in sorted(self.__frontier.keys()):
                if n < 1: continue
                tiles = self.__frontier[n]
                for center in tiles:
                    flags = scanSurroundings(center)
                    if flags:
                        for flag in flags:
                            if self.__board[flag[0]][flag[1]] not in [move[1] for move in self.__moveList]:
                                # print(' FLAG ' + str(self.__board[flag[0]][flag[1]]))
                                self.__moveList.append(tuple([Action(AI.Action.FLAG, flag[0], flag[1]),
                                                              self.__board[flag[0]][flag[1]]]))

        def scanSurroundings(c: Tile) -> []:  # or false
            """Helper func that returns false if surroundings shouldn't be flagged
            Otherwise returns a list of coords to flag"""
            answer = []
            num = self.__uncovered[(c.x, c.y)]
            s = getSurroundings(c)
            unknownTiles = len(s)
            for adj in s:
                if adj.covered:
                    if adj.flag:
                        unknownTiles -= 1
                        num -= 1
                    else:
                        answer.append((adj.x, adj.y))
                else:
                    unknownTiles -= 1
            if unknownTiles == num:
                return answer
            return answer.clear()

        def subtractOne(t: Tile) -> None:
            #print('--' + repr(t))
            self.__frontier[t.number].remove(t)
            if t.number > -1:
                t.number -= 1
            self.__frontier[t.number].append(t)
            self.__board[t.x][t.y].number = t.number

        def countFlags(tileList: list) -> int:
            """Returns the num of flags in list"""
            return len([answer for answer in tileList if answer.flag])

        def updateLabels(tileList: list) -> None:
            """Go through the given list and update labels"""
            for tile in tileList:
                #print('Updating label: ' + repr(tile))
                if not tile.covered:
                    subtractOne(tile)
                    if tile.number == 0:
                        clearSurrounding(tile)

        def getSurroundings(t: Tile) -> [Tile]:
            """Returns the surrounding tiles"""
            answer = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0: continue
                    if self.__isInBounds(t.x + x, t.y + y):
                        answer.append(self.__board[t.x+x][t.y+y])
            return answer

        def cleanFrontier() -> None:
            # Look at the new zeroes and clear them
            for t in self.__frontier[0]:
                clearSurrounding(t)
                self.__frontier[0].remove(t)

        def guess() -> None:
            frontierList = []
            for n in sorted(self.__frontier.keys()):
                if n < 1: continue
                for tile in self.__frontier[n]:
                    s = getSurroundings(tile)
                    for move in s:
                        if not move.flag and move.covered:
                            frontierList.append(move)
            r = random.randint(0, len(frontierList))
            chosen = frontierList.pop(r)
            self.__moveList.append(tuple([Action(AI.Action.UNCOVER, chosen.x, chosen.y), chosen]))
            print('GUESSING: {c}'.format(c=chosen))



#################################################Main Logic#############################################################
        self.__lastTile = self.__board[self.__lastX][self.__lastY]
        # Updates Uncovered dict, which is Tile->number form. Always has original number
        self.__uncovered[(self.__lastX, self.__lastY)] = number

        # Update our knowledge of the board
        if number == -1: # Last move was a flag
            self.__board[self.__lastX][self.__lastY].flag = True
            updateLabels(getSurroundings(self.__lastTile))
        else:
            self.__lastTile.number = number
            self.__lastTile.covered = False
            self.__totalUncovered += 1

        # Check if we win
        if self.__totalTiles - self.__totalUncovered == self.__totalMines:
            #print('WINNER')
            return Action(AI.Action.LEAVE)

        if number == 0:
            clearSurrounding(self.__lastTile)
        else:
            if self.__lastTile not in self.__frontier[number]:
                self.__frontier[number].append(self.__lastTile)
                numFlags = countFlags(getSurroundings(self.__lastTile))
                for x in range(numFlags):
                    subtractOne(self.__lastTile)

        cleanFrontier()
        # Makes the next move in the moveList
        if not self.__moveList:
            #print('MOVELIST EMPTY')
            flagObvious()
            cleanFrontier()

        if False:  # debugs
            def PrettyList(l: iter) -> str:
                answer = ''
                for item in l:
                    if item[0].getMove() == AI.Action.UNCOVER:
                        move = 'UNCOVER'
                    elif item[0].getMove() == AI.Action.FLAG:
                        move = 'FLAG'
                    answer += '\t' + move + '\t' + str(item[1]) + '\n'
                return answer

            print('FRONTIER:')
            for num in sorted(self.__frontier.keys()):
                print('*' * 10 + str(num) + '*' * 10)
                for tile in self.__frontier[num]:
                    print(' ' + str(tile))
            print('MOVE LIST:')
            print(PrettyList([move for move in self.__moveList]))
            self.__printWorld()
            print('Total tiles: {t} | Uncovered: {u} | Total Mines:{m}'.format(t=self.__totalTiles, u=self.__totalUncovered, m = self.__totalMines))
            print(str(self.__totalTiles-self.__totalUncovered) + '->' + str(self.__totalMines))

            ##print('UNCOVERED:' + str(self.__uncovered))
        try:
            currentAction = self.__moveList.pop(0)
        except:
            #guess()
            #currentAction = self.__moveList.pop(0)
            return Action(AI.Action.LEAVE)

        self.__lastX = currentAction[1].x
        self.__lastY = currentAction[1].y
        return currentAction[0]
    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################
