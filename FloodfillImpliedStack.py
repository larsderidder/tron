#!/usr/bin/python

"""Template for your tron bot"""

import tron

import random

def which_move(board):
	file = open('debug.log', "a")

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
	
	file.write("spacecount: " + str(spaceCount) + "\n")
	
	if not spaceCount:
		# We lost :(
		return tron.NORTH
	
	currentEnemySpace = floodfill(board, board.them(), [])
	file.write("currentEnemySpace: " + str(currentEnemySpace) + "\n")

	enemySpaceCount = {}
	for dir in board.moves():
		myPos = board.rel(dir)
		enemySpaceCount[dir] = floodfill(board, board.them(), [myPos])
	
	file.write("enemySpaceCount: " + str(enemySpaceCount) + "\n")
	
	bestchoices = []
	maxscore = -1
	for dir in spaceCount.keys():
		changeEnemySpace = currentEnemySpace - enemySpaceCount[dir]
		mySpace = spaceCount[dir]
		
		pathlength = 0
		origin = board.me()
		while board.passable(board.rel(dir, origin)) and pathlength <= 5:
			pathlength = pathlength + 1
			origin = board.rel(dir, origin)
		
		score = mySpace + changeEnemySpace + pathlength
		if score == maxscore:
			bestchoices.append(dir)
		elif score > maxscore:
			maxscore = score
			bestchoices = [dir]
	
	file.write("bestchoices: " + str(bestchoices) + "\n")
	"""
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
	"""
	choice = random.choice(bestchoices)
	file.write("choice: " + str(choice) + "\n\n")
	return choice

def floodfill(board, origin, visited):
	visited.append(origin)
	count = 1
	for dir in board.unvisitedMoves(origin, visited):
		count = count + floodfill(board, board.rel(dir, origin), visited)
	return count

# you do not need to modify this part
for board in tron.Board.generate():
    tron.move(which_move(board))
