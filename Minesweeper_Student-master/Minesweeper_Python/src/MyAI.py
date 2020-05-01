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


class MyAI( AI ):

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
		self.__moveList = []
		self.__uncovered = {}
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


	def getAction(self, number: int) -> "Action Object":
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		# Adds valid surrounding coords to moveList
		def clearSurrounding(coordX: int, coordY: int) -> None:
			for x in range(-1, 2):
				for y in range(-1, 2):
					if x == 0 and y == 0: continue

					# If the surroundings are out of bounds, we've already been there,
					# or if it is already queued, do not add it to the moveList
					targetX = coordX + x
					targetY = coordY + y
					if (targetX, targetY) in self.__uncovered or \
						(targetX, targetY) in self.__moveList or \
						targetX == self.__colDimension or targetX < 0 or \
						targetY == self.__rowDimension or targetY < 0:
						continue
					self.__moveList.append((coordX + x, coordY + y))


		self.__uncovered[(self.__lastX, self.__lastY)] = number;

		if( False ):
			print('MOVE LIST:' + str(self.__moveList))
			print('UNCOVERED:' + str(self.__uncovered))

		if number == 0:
			clearSurrounding(self.__lastX, self.__lastY)
		try:
			currentAction = self.__moveList.pop(0)
		except IndexError:
			return Action(AI.Action.LEAVE)

		self.__lastX = currentAction[0]
		self.__lastY = currentAction[1]
		return Action(AI.Action.UNCOVER, currentAction[0], currentAction[1])
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################


