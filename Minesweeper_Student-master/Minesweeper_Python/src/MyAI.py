# ====================
#
#
# \
#
#==========CS-199==================================
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
import itertools
import random


class Tile():
    def __init__(self, m=False, c=True, f=False, xCoord=-1, yCoord=-1, number=-1, l='. '):
        self.mine = m
        self.covered = c
        self.flag = f
        self.number = number
        self.x = xCoord
        self.y = yCoord
        self.label = l

    def __repr__(self):
        return 'Tile at ({x},{y}):n={n},c={c},f={f},m={m},l={l}'.format(x=self.x, y=self.y, n=self.number,
                                                                  c=self.covered, f=self.flag, m=self.mine,
                                                                        l=self.label)

    def __str__(self):
        if self.label == '. ':
            lab = ''
        else:
            lab = ': ' + self.label
        return 'Tile({x}, {y}{l})'.format(x=self.x, y=self.y, l=lab)

    def __eq__(self, other):
        if self.mine == other.mine and \
                self.covered == other.covered and \
                self.flag == other.flag and \
                self.number == other.number and \
                self.x == other.x and \
                self.y == other.y:
            return True
        return False

    def __hash__(self):
        return hash((self.x, self.y))

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
        self.__covered = dict()  # We could keep a dict of covered tiles keyed to their chance of being a bomb
        self.__totalTiles = rowDimension * colDimension
        self.__totalMines = totalMines
        self.__totalUncovered = 0
        self.__flagsLeft = totalMines
        self.__temp_guess = dict()

        for x in range(0, self.__colDimension):
            for y in range(0, self.__rowDimension):
                self.__covered[(x,y)] = self.__totalTiles / self.__totalMines

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
            print(self.__board[c][r].label, end=" ")

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
        debugging = False


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
            # print('--' + repr(t))
            self.__frontier[t.number].remove(t)
            if t.number > -1:
                t.number -= 1
            self.__frontier[t.number].append(t)
            self.__board[t.x][t.y].number = t.number

        def countFlags(tileList: list) -> int:
            """Returns the num of flags in list"""
            return len([answer for answer in tileList if answer.flag])

        def countUncovered(tileList: list) -> int:
            '''Returns the num of uncovered tiles in a list'''
            return len([answer for answer in tileList if not answer.covered])

        def countCovered(tileList: list) -> int:
            '''Returns the num of covered tiles in a list, excluding flags'''
            return len([answer for answer in tileList if answer.covered and not answer.flag])

        def getCovered(tileList: list) -> list:
            '''Returns a list of all the covered tiles in a tile list, excluding flags'''
            return [answer for answer in tileList if answer.covered and not answer.flag]

        def getUncovered(tileList: list) -> list:
            '''Returns a list of all the uncovered tiles in a tile list, excluding 0s'''
            return [answer for answer in tileList if not answer.covered and answer.number != 0]

        def updateLabels(tileList: list) -> None:
            """Go through the given list and update labels"""
            for tile in tileList:
                # print('Updating label: ' + repr(tile))
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
                        answer.append(self.__board[t.x + x][t.y + y])
            return answer

        def cleanFrontier() -> None:
            # Look at the new zeroes and clear them
            for t in self.__frontier[0]:
                clearSurrounding(t)
                self.__frontier[0].remove(t)

        def modelChecking() -> None:
            '''Performs model checking and adds to the move list'''
            frontier = {}
            temp_guess = dict();
            guess_bool = False;
            for num, lst in self.__frontier.items():
                if num == -1:
                    continue
                for tile in lst:
                    c = countCovered(getSurroundings(tile))
                    if c == 0:
                        continue
                    frontier[(tile.x, tile.y)] = c

            for coord in frontier.keys():
                pick = self.__board[coord[0]][coord[1]]
                scope = getCovered(getSurroundings(pick))

                surroundingScope = set()
                for s in scope:
                    new = set(getUncovered(getSurroundings(s)))
                    surroundingScope.update(new)

                kb = surroundingScope

                if debugging:
                    print('Picked: ' + str(pick))
                    print('SCOPE: ' + str(scope))
                    print('Knowl:' + str(kb))



                # Add labels to board
                abc = 'abcdefghijklmnopqrstuvwxyz'
                count = 0
                for t in scope:
                    t.label = abc[count] + ' '
                    count += 1

                if debugging: self.__printWorld()

                possible = []
                bombs = pick.number
                for i in range(len(scope)):
                    if bombs > 0:
                        possible.append(1)
                        bombs -= 1
                    else:
                        possible.append(0)
                perms = set(itertools.permutations(possible))

                if debugging:
                    print({p for p in perms})

                worlds = {}
                cpy = list(perms)
                # This loop removes the impossible worlds
                for p in cpy:
                    if debugging: print('Permutation: ' + str(p))
                    labels = []
                    i = 0
                    for t in p:
                        worlds[abc[i]] = t
                        labels.append(abc[i])
                        i += 1
                    for tile in kb:
                        b = tile.number;
                        surroundings = getCovered(getSurroundings(tile))
                        for s in surroundings:
                            try:
                                b -= worlds[s.label.strip(' ')]
                            except:
                                continue
                        if b < 0:
                            if debugging:
                                print('IMPOSSIBLE')
                                print(perms)
                            perms.remove(p)
                            break
                if debugging: print("SCOPE---",scope)
                if debugging: print("LEGAL PERMS----",perms)
                for p in perms:
                    count = 0
                    for k in scope:
                        if (k.x,k.y) in self.__temp_guess:
                            #print("COUNT IN GUESS-----",count)
                            #print("value of COUNT ------", p[count])
                            self.__temp_guess[(k.x,k.y)] += p[count]
                            #print("VALUE OF DICT--------", temp_guess[(k.x,k.y)])
                            count+=1
                        else:
                            #print("COUNT IN GUESS-----", count)
                            #print("value of COUNT ------", p[count])
                            self.__temp_guess[(k.x, k.y)] =0;
                            self.__temp_guess[(k.x,k.y)] += p[count]
                            #print("VALUE OF DICT--------", temp_guess[(k.x, k.y)])
                            count+=1

                if len(perms) == 1:
                    if debugging: print('Only one world is possible, flag it!')
                    flagWorld(pick, perms.pop())
                else:
                    pass
                    #if debugging: print("Multiple Options")
                    #guess()
                    #do smart guessing


                for t in scope:
                    t.label = '. '



        def flagWorld(t : Tile, p: tuple) -> None:
            '''Given a target tile and a possible world, flag the board with that world'''
            surroundings = getCovered(getSurroundings(t))
            if debugging:
                print(t)
                print(p)
                print(surroundings)
            for i in range(len(p)):
                if p[i] == 1:
                    flagMe = surroundings[i]
                    if self.__board[flagMe.x][flagMe.y] not in [move[1] for move in self.__moveList]:
                        self.__moveList.append(tuple([Action(AI.Action.FLAG, flagMe.x, flagMe.y),
                                                  self.__board[flagMe.x][flagMe.y]]))


        def guess() -> None:
            """Make a guess here. Note: must append at least one move to movelist before function terminates"""
            #print("TEMP GUESS ---- ", self.__temp_guess)
            if debugging:
                print("TEMP GUESS ---- ", self.__temp_guess)
                print("GUESS TOO BE PICKED MIN OF DICT------", min(self.__temp_guess, key=self.__temp_guess.get))

            try:
                main_guess = min(self.__temp_guess, key=self.__temp_guess.get)
                if debugging: print("X------", main_guess[0])
                self.__moveList.append(tuple([Action(AI.Action.UNCOVER, main_guess[0], main_guess[1]),
                                          self.__board[main_guess[0]][main_guess[1]]]))
                self.__temp_guess.clear()
            except ValueError:
                pass

        def updateCovered() -> None:
            """Iterate through covered and update their probabilities"""
            for tile, chance in list(self.__covered.items()):
                if tile in self.__uncovered.keys():
                    del self.__covered[tile]
                else:
                    self.__covered[tile] = (self.__flagsLeft) / (self.__totalTiles - self.__totalUncovered -
                                            self.__totalMines + self.__flagsLeft)

                surroundings = getSurroundings(self.__board[tile[0]][tile[1]])
                uncovered = countUncovered(surroundings)
                if uncovered == 0:
                    del self.__covered[tile]




        #################################################Main Logic#############################################################
        self.__lastTile = self.__board[self.__lastX][self.__lastY]
        # Updates Uncovered dict, which is (coord)->number form. Always has original number
        self.__uncovered[(self.__lastX, self.__lastY)] = number

        # Update our knowledge of the board
        if number == -1:  # Last move was a flag
            self.__flagsLeft -= 1
            self.__board[self.__lastX][self.__lastY].flag = True
            updateLabels(getSurroundings(self.__lastTile))
        else:
            self.__lastTile.number = number
            self.__lastTile.covered = False
            self.__totalUncovered += 1


        if debugging: print('Total Tiles: {t}, Uncovered: {u}, Mines: {m}'.format(t=self.__totalTiles, u=self.__totalUncovered, m=self.__totalMines))
        if self.__totalTiles - self.__totalUncovered == self.__totalMines:  # if we've uncovered everything
            if debugging: print('WINNER')                                   #
            return Action(AI.Action.LEAVE)                                  #
        elif self.__flagsLeft == 0:                                         # or if we flagged all of the mines
            for x in range(self.__colDimension):
                for y in range(self.__rowDimension):
                    if(x, y) not in self.__uncovered.keys() and self.__board[x][y] not in [move[1] for move in self.__moveList]:
                        self.__moveList.append(tuple([Action(AI.Action.UNCOVER, x, y), self.__board[x][y]]))
            if debugging: print('COVERED:'); print(self.__covered)

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
            if debugging: print('MOVELIST EMPTY')
            flagObvious()
            cleanFrontier()


        ###########################################################
        if debugging:
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
            print('Total tiles: {t} | Uncovered: {u} | Total Mines:{m}'.format(t=self.__totalTiles,
                                                                               u=self.__totalUncovered,
                                                                               m=self.__totalMines))
            print(str(self.__totalTiles - self.__totalUncovered) + '->' + str(self.__totalMines))
            ##print('UNCOVERED:' + str(self.__uncovered))
        ################################################################


        try:
            currentAction = self.__moveList.pop(0)
        except:
            modelChecking()
            try:
                currentAction = self.__moveList.pop(0)
            except IndexError:
                # Replace this with guess
                guess() # We HAVE to add something to move list here
                currentAction = self.__moveList.pop(0)

        self.__lastX = currentAction[1].x
        self.__lastY = currentAction[1].y
        return currentAction[0]
    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################
