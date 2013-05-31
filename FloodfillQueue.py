#!/usr/bin/python

"""Template for your tron bot"""

import tron
import sys
import random

from collections import deque

def which_move(board):
	#file = open('debug.log', "a")
	#sys.stderr = file
	
	if len(board.moves()) == 0:
		return tron.SOUTH
		
	if len(board.moves()) == 1:
		#sys.stderr.write("quickchoice: " + str(board.moves()[0]) + "\n\n")
		return board.moves()[0]

	enemyReachable = []
	for dir in board.moves(board.them()):
		enemyReachable.append(board.rel(dir, board.them()))

	spaceCount = {}
	for dir in board.moves():
		dest = board.rel(dir)
		if dest in enemyReachable:
			spaceCount[dir] = 1
		else:
			spaceCount[dir] = floodfill(board, dest, [])
	
	#sys.stderr.write("spacecount: " + str(spaceCount) + "\n")

	enemySpaceCount = {}
	for dir in board.moves():
		myPos = board.rel(dir)
		enemySpaceCount[dir] = floodfill(board, board.them(), [myPos])
	
	#sys.stderr.write("enemySpaceCount: " + str(enemySpaceCount) + "\n")
	
	bestchoices = []
	maxscore = None
	for dir in spaceCount.keys():		
		score = spaceCount[dir] - enemySpaceCount[dir]
		if score == maxscore:
			bestchoices.append(dir)
		elif maxscore == None or score > maxscore:
			maxscore = score
			bestchoices = [dir]
	
	#sys.stderr.write("bestchoices: " + str(bestchoices) + "\n")
	'''
	if len(bestchoices) == 1:
		return bestchoices[0]
	
	bestchoice = bestchoices[0]
	maxcount = 0
	for dir in bestchoices:
		count = 0
		origin = board.me()
		while board.passable(board.rel(dir, origin)):
			count = count + 1
			origin = board.rel(dir, origin)
		if count > maxcount:
			maxcount = count
			bestchoice = dir
	return bestchoice
	'''
	if len(bestchoices) > 1:		
		maxpathlength = -1
		oldbestchoices = bestchoices
		bestchoices = []
		for dir in oldbestchoices:
			pathlength = 0
			node = board.me()
			while board.passable(board.rel(dir, node)):
				pathlength = pathlength + 1
				node = board.rel(dir, node)
			if pathlength == maxpathlength:
				bestchoices.append(dir)
			elif pathlength > maxpathlength:
				maxpathlength = pathlength
				bestchoices = [dir]
		
		forward = findForward(board)
		if forward != None and forward in bestchoices:
			choice = forward
			#sys.stderr.write("choice: " + str(choice) + "\n\n")
			return choice
	choice = random.choice(bestchoices)
	#sys.stderr.write("choice: " + str(choice) + "\n\n")
	return choice

def floodfill(board, origin, visited):
	queue = deque()
	queue.append(origin)
	count = -1
	'''
	while len(queue) > 0:
		node = queue.popleft()
		count += 1
		visited.append(node)
		for dir in board.unvisitedMoves(node, visited):
			other = board.rel(dir, node)
			if other not in queue:
				queue.append(board.rel(dir, node))
	'''
	while len(queue) > 0:
		node = queue.popleft()
		if node in visited:
			continue
		west = node
		while board.passable(board.rel(tron.WEST, west)) and west not in visited:
			west = board.rel(tron.WEST, west)
		east = node
		while board.passable(board.rel(tron.EAST, east)) and east not in visited:
			east = board.rel(tron.EAST, east)
		
		westToEast = west
		while westToEast != board.rel(tron.EAST, east):
			north = board.rel(tron.NORTH, westToEast)
			if board.passable(north) and north not in visited:
				queue.append(north)
			south = board.rel(tron.SOUTH, westToEast)
			if board.passable(south) and south not in visited:
				queue.append(south)
			count += 1
			visited.append(westToEast)
			westToEast = board.rel(tron.EAST, westToEast)
	return count

def findForward(board):
	forward = None
	if len(board.moves()) == 3:
		originDir = (set(tron.DIRECTIONS) - set(board.moves())).pop()
		forward = None
		if originDir == tron.NORTH:
			forward = tron.SOUTH
		elif originDir == tron.SOUTH:
			forward = tron.NORTH
		elif originDir == tron.EAST:
			forward = tron.WEST
		elif originDir == tron.WEST:
			forward = tron.EAST
	return forward

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
