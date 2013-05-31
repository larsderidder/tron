#!/usr/bin/python

"""Template for your tron bot"""

import tron, random, time, attack_algorithms
			
def which_move(board):
	start = time.clock()
	
	if len(board.moves()) == 0:
		return tron.SOUTH

	enemyMoves = [board.rel(dir, board.them()) for dir in board.moves(board.them())]

	enemyReachable = False
	spaceCount = dict()
	for dir in board.moves():
		dest = board.rel(dir)
		floodfilled = tron.floodfill.execute(board, dest)
		enemyReachable = enemyReachable or dest in enemyMoves or len(filter(lambda node : node in enemyMoves, floodfilled)) > 0
		deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
		spaceCount[dir] = len(floodfilled) - len(deadCorners) + 1

	tron.debug("Spacecount: " + str(spaceCount) + "\n")
	tron.debug("EnemyReachable: " + str(enemyReachable) + "\n")
	#enemyReachable = False
	if not enemyReachable:
		return survivalMode(board, spaceCount)

	enemySpaceCount = dict()
	for dir in board.moves():
		enemySpaceCount[dir] = tron.floodfill.floodfillScore(board, board.them(), [board.rel(dir)])
	
	#tron.log("EnemySpaceCount: " + str(enemySpaceCount))
		
	shortestPath = attack_algorithms.AStar().execute(board)
	minimaxSpaceCount = tron.minimax.execute(board, spaceCount, enemySpaceCount)
	tron.log("minimaxspacecount: " + str(minimaxSpaceCount))
	#tron.log(len(shortestPath))
	#tron.log("Shortest path: " + str(shortestPath))
	if len(shortestPath) >= 6:
		return farAwayMode(board, shortestPath, minimaxSpaceCount)
	
	return closeCombatMode(board, minimaxSpaceCount, shortestPath)
	
	'''
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
	tron.log("Choice: " + str(choice))
	tron.log("Turn took: " + str(float(time.clock() - start)) + "\n")
	return choice
	'''
	
def closeCombatMode(board, minimaxSpaceCount, shortestPath):
	maxScore = max([score for score in minimaxSpaceCount.values()])
	bestDirs = [dir for dir in board.moves() if minimaxSpaceCount[dir] == maxScore]
	choice = None
	if len(bestDirs) == 1:
		choice = bestDirs[0]
	
	if choice is None:
		for dir in bestDirs:
			if board.rel(dir) == shortestPath[0]:
				choice = dir
				break

	if choice is None:
		shortestDist = None
		for dir in bestDirs:
			distance = board.distance(board.rel(dir), board.them())
			if shortestDist == None or distance < shortestDist:
				choice = dir
				shortestDist = distance
	
	tron.log("Choice: " + str(choice))
	return choice
	
def farAwayMode(board, shortestPath, minimaxSpaceCount):
	choice = None
	bestChoices = []
	maxScore = max([score for score in minimaxSpaceCount.values()])
	minScore = min([score for score in minimaxSpaceCount.values()])
	for dir in board.moves():
		if board.rel(dir) == shortestPath[0]:
			choice = dir
		if ((minScore <= -5 and maxScore > minScore) or maxScore >= 10) and minimaxSpaceCount[dir] == maxScore:
			bestChoices.append(dir)
	
	if len(bestChoices) > 0 and choice not in bestChoices:
		choice = None
		if len(bestChoices) == 1:
			choice = bestChoices[0]
		if choice == None:
			shortestDist = None
			for dir in bestChoices:
				distance = board.distance(board.rel(dir), board.them())
				if shortestDist == None or distance < shortestDist:
					choice = dir
					shortestDist = distance
	tron.log("Choice: " + str(choice))
	return choice
	
def survivalMode(board, spaceCount):
	choice = tron.optimizeSpaceAlgorithm.execute(board, spaceCount)
	tron.log("Choice: " + str(choice))
	return choice
	
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
    tron.log("Turn took: " + str(float(time.clock() - board.startTime)))
