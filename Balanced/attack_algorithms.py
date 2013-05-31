
import tron, time

from heapq import heappush, heappop, heapify

class AStar:

	def execute(self, board):
		start = time.clock()
		goal = board.them()
		
		closedSet = []
		openSet = dict()
		startPath = AStar.Path(board.me(), [], 0, board.distance(board.me(), goal))
		openSet[board.me()] = startPath
		queue = [startPath]
		tron.log("goal: " + str(goal))
		shortestPath = []
		while len(queue) > 0 and time.clock() - start < 0.4:
			path = heappop(queue)
			shortestPath = path.visited
			if path.node == goal:
				break
			closedSet.append(path.node)
			destinations = [dest for dest in board.adjacent(path.node) if board.passable(dest) or dest == goal]
			for dest in destinations:
				if dest in closedSet:
					continue
				newScore = path.score + 1
				if dest not in openSet.keys() or openSet[dest] not in queue:
					newPath = AStar.Path(dest, list(path.visited), newScore, board.distance(dest, goal))
					openSet[dest] = newPath
					heappush(queue, newPath)
				elif newScore < openSet[dest].score and openSet[dest] in queue:
					openSet[dest].node = dest
					openSet[dest].score = newScore
					newVisited = list(path.visited)
					newVisited.append(dest)
					openSet[dest].visited = newVisited
					openSet[dest].estimate = board.distance(dest, goal)
		tron.log("Shortest path took: " + str(float(time.clock() - start)))
		return shortestPath[1:]
		
	class Path:
		
		def __init__(self, node, visited, score, estimate):
			self.node = node
			self.visited = visited
			self.visited.append(node)
			self.score = score
			self.estimate = estimate
			
		def __eq__(self, other):
			return self.visited == other.visited
			
		def __cmp__(self, other):
			return cmp(self.score + self.estimate, other.score + other.estimate)
			
class Minimax:

	def __init__(self):
		self.cachedLevels = []
		
	def prepareCache(self, board, spaceCount, enemySpaceCount):
		if len(self.cachedLevels) <= 3:
			root = Minimax.TreeNode(None, board.me(), board.them(), [board.me(), board.them()], True, 0)
			levels = [Minimax.Level([root], True)]
			for dir in board.moves():
				move = board.rel(dir)
				visited = list(root.visited)
				visited.append(move)
				root.addChild(root, move, root.them, visited, spaceCount[dir] - enemySpaceCount[dir])
			self.cachedLevels = levels
			return
		myMove = None
		for node in self.cachedLevels[1].nodes:
			if node.me == board.me():
				myMove = node
				break
		theirMove = None
		for node in myMove.children:
			if node.them == board.them():
				theirMove = node
				break
		theirMove.score = 0
		self.cachedLevels = self.cachedLevels[2:]
		self.cachedLevels[0] = Minimax.Level([theirMove], True)

	def execute(self, board, spaceCount, enemySpaceCount):
		#self.prepareCache(board, spaceCount, enemySpaceCount)
		levels = self.minimax(board, spaceCount, enemySpaceCount)
		#self.cachedLevels = levels
		root = levels[0].nodes[0]
		
		tron.log("Minimax level: " + str(len(levels)-1))
		
		minimaxSpaceCount = dict()
		for node in root.children:
			for dir in spaceCount.keys():
				if board.rel(dir) == node.me:
					minimaxSpaceCount[dir] = node.score
		return minimaxSpaceCount
		
	def minimax(self, board, spaceCount, enemySpaceCount):
		#'''
		root = Minimax.TreeNode(None, board.me(), board.them(), [board.me(), board.them()], True, 0)
		levels = [Minimax.Level([root], True)]
		for dir in spaceCount.keys():
			move = board.rel(dir, root.me)
			visited = list(root.visited)
			visited.append(move)
			root.addChild(root, move, root.them, visited, spaceCount[dir] - enemySpaceCount[dir])
		#'''
		#levels = list(self.cachedLevels)
		#levels.append(Minimax.Level(list(root.children)))
		
		outOfTime = False
		while time.clock() - board.startTime < 0.85 and len(levels[len(levels)-1].nodes) > 0:
			currLevel = levels[len(levels)-1]
			#for node in level.nodes:
			#	node.refineScore()
			#tron.log("level " + str(len(levels)))
			#tron.log("nodes" + str(level.nodes))
			for parent in currLevel.nodes:
				if time.clock() - board.startTime > 0.85:
					outOfTime = True
					break
				nodeChildren = [child for child in parent.children if child.me != child.them and len(board.adjacentImpassableOrVisited(child.me, child.visited)) < 4 and len(board.adjacentImpassableOrVisited(child.them, child.visited)) < 4]
				heapify(nodeChildren)
				while len(nodeChildren) > 0:
					node = heappop(nodeChildren)
				
					if node.myMove:
						movedFrom = node.me
						other = node.them
					else:
						movedFrom = node.them
						other = node.me
					unvisitedMoves = [move for move in board.moveableDestinations(movedFrom) if move not in node.visited or move == other]
					newScore = None
					for move in unvisitedMoves:
						moveVisited = list(node.visited)
						moveVisited.append(move)
						if move == other:
							score = 0
						elif len(board.adjacentImpassableOrVisited(move, moveVisited)) == 4:
							boardSize = (board.width - 2) * (board.height - 2)
							if node.myMove:
								score = -boardSize
							else:
								score = boardSize
						else:
							#floodfilled = tron.floodfill.execute(board, move, moveVisited)
							#deadCorners = [ffNode for ffNode in floodfilled if len(board.adjacentImpassable(ffNode)) == 3]
							#moveScore = len(floodfilled) - len(deadCorners) + min(len(deadCorners), 1)
							#if other in floodfilled:
							#	score = 0
							#else:
							moveScore = tron.floodfill.floodfillScore(board, move, moveVisited)
							otherScore = tron.floodfill.floodfillScore(board, other, moveVisited)
							if node.myMove:
								score = moveScore - otherScore
							else:
								score = otherScore - moveScore
					
						if node.myMove:
							child = node.addChild(node, move, other, moveVisited, score)
							if newScore is None or score > newScore:
								newScore = score
						else:
							child = node.addChild(node, other, move, moveVisited, score)
							if newScore is None or score < newScore:
								newScore = score
					node.score = newScore
					#newLevel.nodes.append(node)
					#childlevel
				#parentlevel
				parent.refineScore()
			if outOfTime:
				break
			#tron.log(levels)
			enemyMoveLevels = [level for level in levels if not level.myMove]
			for level in enemyMoveLevels:
				for parent in level.nodes:
					parent.children = [child for child in parent.children if child.score == parent.score]
			newLevel = Minimax.Level([], not currLevel.myMove)
			for parent in currLevel.nodes:
				newLevel.nodes.extend(parent.children)
				#tron.log("parentscore: " + str(parent.score) + " " + str(parent.me) + str(parent.them))
				#if parent.myMove:
				#	tron.log("mine: " + str([(node.me, node.score) for node in parent.children]))
				#else:
				#	tron.log("them: " + str([(node.them, node.score) for node in parent.children]))
			levels.append(newLevel)
		index = 0
		'''
		for index in range(len(levels)):
			printLevel = levels[index]
			tron.log("level " + str(index) + ", nodes " + str(len(printLevel.nodes)))
			for node in printLevel.nodes:
				tron.log(str(node.me) + "," + str(node.them) + " " + str(node.score))
				#tron.log(node.visited)
			index += 1
		'''
		return levels
	
	class Level:
		def __init__(self, nodes, myMove):
			self.nodes = nodes
			self.myMove = myMove
	
	class TreeNode:
		def __init__(self, parent, me, them, visited, myMove, score):
			self.parent = parent
			self.me = me
			self.them = them
			self.visited = visited
			self.myMove = myMove
			self.score = score
			self.children = []
			
		def addChild(self, node, me, them, moveVisited, score):
			child = Minimax.TreeNode(self, me, them, moveVisited, not self.myMove, score)
			heappush(self.children, child)
			return child
			
		def __cmp__(self, other):
			return cmp(other.score, self.score)
		
		def refineScore(self):
			if len(self.children) > 0:
				if self.myMove:
					maxScore = -100
					for child in self.children:
						if child.score > maxScore:
							maxScore = child.score
					self.score = maxScore
				else:
					minScore = 100
					for child in self.children:
						if child.score < minScore:
							minScore = child.score
					self.score = minScore
			if self.parent is not None:
				self.parent.refineScore()
				
		'''
		def addChild(self, board, dest, score=None):
			#tron.log(score)
			newVisited = list(self.visited)
			if score == None:
				if dest == self.them or dest == self.me:
					score = 0
				else:
					if self.myMove:
						other = self.them
						newVisited.append(self.me)
						#child = Minimax.TreeNode(self, node, self.them, newVisited, False, score)
					else:
						other = self.me
						newVisited.append(self.them)
						#child = Minimax.TreeNode(self, self.me, node, newVisited, True, score)
					destScore = tron.floodfill.floodfillScore(board, dest, self.visited)
					otherScore = tron.floodfill.floodfillScore(board, other, newVisited)
					score = destScore - otherScore
			if self.myMove:
				child = Minimax.TreeNode(self, dest, self.them, newVisited, not self.myMove, score)
			else:
				child = Minimax.TreeNode(self, self.me, dest, newVisited, not self.myMove, score)
			self.children.append(child)
			return child
		'''
		
