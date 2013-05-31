#!/usr/bin/python

"""Template for your tron bot"""

import tron, sys, random, time

from collections import deque
			
def which_move(board):
	start = time.clock()
	
	if len(board.moves()) == 0:
		return tron.SOUTH
		
	#if len(board.moves()) == 1:
	#	tron.debug("Quickchoice: " + str(board.moves()[0]) + "\n\n")
	#	return board.moves()[0]

	enemyMoves = []
	for dir in board.moves(board.them()):
		enemyMoves.append(board.rel(dir, board.them()))

	deadCorners = []
	enemyReachable = False
	spaceCount = {}
	for dir in board.moves():
		dest = board.rel(dir)
		if dest in enemyMoves:
			#spaceCount[dir] = 1
			enemyReachable = True
		visited = floodfill(board, dest)
		enemyReachable = enemyReachable or len(filter(lambda node : node in enemyMoves, visited)) != 0
		deadCorners.extend([node for node in visited if len(board.adjacentImpassable(node)) == 3 and node not in deadCorners])
		spaceCount[dir] = len(visited)

	tron.debug("Spacecount: " + str(spaceCount) + "\n")
	tron.debug("EnemyReachable: " + str(enemyReachable) + "\n")
	#enemyReachable = False
	if not enemyReachable:
		choice = tron.optimizeSpaceAlgorithm.execute(board, spaceCount, deadCorners)
		tron.debug("Choice: " + str(choice) + "\n")
		tron.debug("Turn took: " + str(time.clock() - start) + "\n\n")
		return choice

	enemySpaceCount = {}
	for dir in board.moves():
		myPos = board.rel(dir)
		enemySpaceCount[dir] = len(floodfill(board, board.them(), [myPos]))
	
	tron.debug("EnemySpaceCount: " + str(enemySpaceCount) + "\n")
	
	bestchoices = []
	maxscore = None
	for dir in spaceCount.keys():		
		score = spaceCount[dir] - enemySpaceCount[dir]
		if score == maxscore:
			bestchoices.append(dir)
		elif maxscore == None or score > maxscore:
			maxscore = score
			bestchoices = [dir]
	
	bestchoices = findLongestPathDirections(board.me(), bestchoices)
	tron.debug("Bestchoices: " + str(bestchoices) + "\n")
	
	choice = random.choice(bestchoices)
	tron.debug("Choice: " + str(choice) + "\n")
	tron.debug("Turn took: " + str(time.clock() - start) + "\n\n")
	return choice

def floodfill(board, origin, exclude=[]):
	start = time.clock()
	visited=[]
	queue = deque()
	queue.append(origin)
	
	while len(queue) > 0:
		node = queue.popleft()
		if node in visited:
			continue
			
		west = continuouslyMoveDirection(board, node, tron.WEST, exclude)
		east = continuouslyMoveDirection(board, node, tron.EAST, exclude)
		
		westToEast = west
		northInterrupted = True
		southInterrupted = True
		while westToEast != board.rel(tron.EAST, east):
			north = board.rel(tron.NORTH, westToEast)
			if not northInterrupted and (not board.passable(north) or north in exclude or north in visited):
				northInterrupted = True
			elif northInterrupted and board.passable(north) and north not in exclude and north not in visited:
				queue.append(north)
				northInterrupted = False
				
			south = board.rel(tron.SOUTH, westToEast)
			if not southInterrupted and (not board.passable(south) or south in exclude or south in visited):
				southInterrupted = True
			elif southInterrupted and board.passable(south) and south not in exclude and south not in visited:
				queue.append(south)
				southInterrupted = False
				
			visited.append(westToEast)
			westToEast = board.rel(tron.EAST, westToEast)
	tron.debug("FLOODFILL TOOK: " + str(time.clock() - start) + "\n")
	return visited
	
def continuouslyMoveDirection(board, start, dir, exclude=[]):
	'''
	Continuously move in direction dir until not passable or in excludelist.
	'''
	loc = start
	newLoc = board.rel(dir, loc)
	while board.passable(newLoc) and newLoc not in exclude:
		loc = newLoc
		newLoc = board.rel(dir, loc)
	return loc
	
def findLongestPathDirections(start, directions):
	longestDirections = directions
	if len(directions) > 1:
		maxpathlength = -1
		longestDirections = []
		for dir in directions:
			pathlength = 0
			node = start
			while board.passable(board.rel(dir, node)):
				pathlength += 1
				node = board.rel(dir, node)
			if pathlength == maxpathlength:
				longestDirections.append(dir)
			elif pathlength > maxpathlength:
				maxpathlength = pathlength
				longestDirections = [dir]
	return longestDirections

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
