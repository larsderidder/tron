#!/usr/bin/python

"""Template for your tron bot"""

import tron, time
			
def which_move(board):
	if not board.moves():
		return tron.SOUTH
		
	if board.width >= 40 and board.height >= 40:
		return wallhugMode(board)
	if board.width >= 20 and board.height >= 20:
		return floodfillMode(board)

	enemyMoves = [board.rel(dir, board.them()) for dir in board.moves(board.them())]
	shortestPath = tron.aStar.execute(board)
	
	tron.log("ShortestPath: " + str(shortestPath))
	enemyReachable = shortestPath is not None
	tron.log("EnemyReachable: " + str(enemyReachable))
	#enemyReachable = False
	if not enemyReachable:
		return survivalMode(board)
	
	shortestPath = shortestPath[1:]
	#if shortestPath[-1] != board.them() or time.clock() - board.startTime > 0.2:
	#	return shortestPathMode(board, shortestPath)

	#enemySpaceCount = dict()
	#for dir in board.moves():
	#	enemySpaceCount[dir] = tron.floodfill.floodfillScore(board, board.them(), [board.rel(dir)])
	
	#tron.log("EnemySpaceCount: " + str(enemySpaceCount))
	
	minimaxSpaceCount = tron.minimax.execute(board)
	tron.log("minimaxspacecount: " + str(minimaxSpaceCount))
	#if not minimaxSpaceCount:
	#	return shortestPathMode(board, shortestPath)
	#if len(shortestPath) >= 6:
	#	return farAwayMode(board, shortestPath, minimaxSpaceCount)
	
	return minimaxMode(board, minimaxSpaceCount, shortestPath)
	
def wallhugMode(board):
	order = (tron.WEST, tron.EAST, tron.NORTH, tron.SOUTH)
	decision = board.moves()[0]

	for dir in order:
		dest = board.rel(dir)
		if not board.passable(dest):
			continue
		adj = board.adjacent(dest)
		if any(board[pos] == tron.WALL for pos in adj):
			decision = dir
			break
	return decision
	
def minimaxMode(board, minimaxSpaceCount, shortestPath):
	maxScore = max(minimaxSpaceCount.values())
	bestDirs = [dir for dir in board.moves() if minimaxSpaceCount[dir] == maxScore]
	if len(bestDirs) == 1:
		tron.log("Minimax Choice: " + str(bestDirs[0]))
		return bestDirs[0]
	
	for dir in bestDirs:
		if board.rel(dir) == shortestPath[0]:
			tron.log("Minimax/Shortestpath Choice: " + str(dir))
			return dir

	newBestDirs = []
	minHeuristic = None
	for dir in bestDirs:
		heuristic = board.distance(board.rel(dir), board.them()) - len(board.adjacentImpassable(board.rel(dir))) * 2
		if minHeuristic is None or heuristic < minHeuristic:
			newBestDirs = [dir]
			minHeuristic = heuristic
		elif heuristic == minHeuristic:
			newBestDirs.append(dir)
	
	'''
	if len(newBestDirs) == 1:
		tron.log("Minimax/Heuristic 1 choice: " + str(newBestDirs[0]))
		return newBestDirs[0]
		
	for dir in newBestDirs:
		if board.rel(dir) == shortestPath[0]:
			tron.log("Minimax/Heuristic/Shortestpath Choice: " + str(dir))
			return dir
	'''
			
	choice = newBestDirs[0]
	tron.log("Minimax/Heuristic 2 choice: " + str(choice))
	return choice
	
'''
def shortestPathMode(board, shortestPath):
	choice = tron.SOUTH
	for dir in board.moves():
		if board.rel(dir) == shortestPath[0]:
			choice = dir
	tron.log("Choice: " + str(choice))
	return choice
'''
'''
def farAwayMode(board, shortestPath, minimaxSpaceCount):
	choice = None
	bestChoices = []
	maxScore = max(minimaxSpaceCount.values())
	minScore = min(minimaxSpaceCount.values())
	for dir in board.moves():
		if board.rel(dir) == shortestPath[0]:
			choice = dir
		if ((minScore <= -20 and maxScore >= -8) or (minScore <= -10 and maxScore >= 0) or maxScore >= 8) and minimaxSpaceCount[dir] == maxScore:
			bestChoices.append(dir)

	if bestChoices and choice not in bestChoices:
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
'''
	
def floodfillMode(board):
	spaceCount = dict()
	for dir in board.moves():
		dest = board.rel(dir)
		floodfilled = tron.floodfill.execute(board, dest)
		#enemyReachable = enemyReachable or dest in enemyMoves or len(filter(lambda node : node in enemyMoves, floodfilled)) > 0
		deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
		spaceCount[dir] = len(floodfilled) - len(deadCorners) + 1
	tron.log("Spacecount: " + str(spaceCount))
		
	enemySpaceCount = dict()
	for dir in board.moves():
		myPos = board.rel(dir)
		floodfilled = tron.floodfill.execute(board, board.them(), [myPos])
		deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
		enemySpaceCount[dir] = len(floodfilled) - len(deadCorners) + 1
	tron.log("EnemySpacecount: " + str(enemySpaceCount))
	
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
	tron.log("Bestchoices: " + str(bestchoices))
	
	choice = bestchoices[0]
	tron.log("Choice: " + str(choice))
	return choice
	
def survivalMode(board):
	spaceCount = dict()
	for dir in board.moves():
		dest = board.rel(dir)
		floodfilled = tron.floodfill.execute(board, dest)
		#enemyReachable = enemyReachable or dest in enemyMoves or len(filter(lambda node : node in enemyMoves, floodfilled)) > 0
		deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
		spaceCount[dir] = len(floodfilled) - len(deadCorners) + 1

	tron.log("Spacecount: " + str(spaceCount))
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
