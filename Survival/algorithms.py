
import tron, time

from collections import deque

from heapq import heappush, heappop
	
class OptimizeSpaceAlgorithm:

	def __init__(self):
		self.timer = 0
		self.allPaths = []

	def execute(self, board, spaceCount, deadCorners):
		self.timer = time.clock()
		spaceUpperBound = max(spaceCount.values()) - len(deadCorners)
		path = self.longestPathFloodfill(board)
		tron.debug("Longestpath: " + str(len(path)) + "\n")
		dest = path[0]
		choice = None
		for dir in board.moves():
			if board.rel(dir) == dest:
				choice = dir
		tron.log(len(self.allPaths))
		self.allPaths = self.prepareQueue(dest)
		tron.log(len(self.allPaths))
		tron.log("Optimize space algorithm time: " + str(time.clock() - self.timer))
		self.timer = 0
		return choice
		
	def prepareQueue(self, origin):
		if len(self.allPaths) == 0:
			return []
		newAllPaths = [path for path in self.allPaths if len(path.visited) > 0 and path.visited[0] == origin]
		for path in newAllPaths:
			path.visited = path.visited[1:]
			path.diffSequence = path.diffSequence[1:]
		return newAllPaths

	def longestPathFloodIterative(self, board):
		currLevel = []
		nextLevel = []
		origin = board.me()
		
		originScore = len(tron.floodfill.execute(board, origin, []))
		startnodes = set([path.visited[0] for path in currLevel if len(path.visited) > 0])
		destinations = [dest for dest in board.moveableDestinations(origin) if dest not in startnodes]
		for dest in destinations:
			path = OptimizeSpaceAlgorithm.PathIt(dest, [], board)
			heappush(currLevel, path)

		maxPath = currLevel[0]
		newAllPaths = []
		while len(currLevel) > 0 and time.clock() - self.timer < 0.9:
			path = heappop(currLevel)
			destinations = [dest for dest in board.moveableDestinations(path.node) if dest not in path.visited]
			if len(destinations) == 0:
				#newAllPaths.append(path)
				continue
			for dest in destinations:
				newVisited = list(path.visited)
				newPath = OptimizeSpaceAlgorithm.PathIt(dest, newVisited, board)
				heappush(nextLevel, newPath)
			if len(currLevel) == 0:
				for nextPath in nextLevel:
					heappush(currLevel, nextPath)
				nextLevel = []
				tron.log("nextlevel")
		newAllPaths.extend(currLevel)
		newAllPaths.extend(nextLevel)
		for path in newAllPaths:
			if len(path.visited) > len(maxPath.visited):
				maxPath = path
			elif len(path.visited) == len(maxPath.visited) and path.score > maxPath.score:
				maxPath = path
		tron.log(maxPath.visited)
		tron.log(maxPath.score)
		return maxPath.visited

	def longestPathFloodfill(self, board):
		queue = self.allPaths
		#queue = []
		origin = board.me()
		
		originScore = len(tron.floodfill.execute(board, origin, []))
		startnodes = set([path.visited[0] for path in queue if len(path.visited) > 0])
		destinations = [dest for dest in board.moveableDestinations(origin) if dest not in startnodes]
		tron.log(destinations)
		for dest in destinations:
			path = OptimizeSpaceAlgorithm.Path(dest, [], originScore, [], board)
			heappush(queue, path)

		maxPath = queue[0]
		
		newAllPaths = []
		while len(queue) > 0 and time.clock() - self.timer < 0.93:
			path = heappop(queue)
			destinations = [dest for dest in board.moveableDestinations(path.node) if dest not in path.visited]
			if len(destinations) == 0:
				newAllPaths.append(path)
				continue
			for dest in destinations:
				newVisited = list(path.visited)
				newDiffSequence = list(path.diffSequence)
				newPath = OptimizeSpaceAlgorithm.Path(dest, newVisited, path.score, newDiffSequence, board)
				heappush(queue, newPath)
		newAllPaths.extend(queue)
		self.allPaths = newAllPaths
		
		for path in newAllPaths:
			if len(path.visited) >= len(maxPath.visited):
				maxPath = path
		tron.log(maxPath.visited)
		tron.log(maxPath.score)
		return maxPath.visited
    	
   	def longestPathBFS(self, board, start, upperBound, visited=[]):
   		queue = deque()
   		
		while len(queue) > 0:
			if time.clock() - self.timer > 0.8:
				break
			visited = queue.popleft()
			lastNode = visited[len(visited)-1]
			destinations = board.moveableDestinations(lastNode)
			destinations = filter(lambda dest : dest not in visited, destinations)
			destinations.sort(key = lambda x : len(board.adjacentImpassable(x)), reverse=True)
			for dest in destinations:
				if dest not in visited:
					viz = list(visited)
					viz.append(dest)
					queue.append(viz)
					if len(visited) > len(maxpath):
						maxpath = visited
		return maxpath
    	
	def longestPath(self, board, start, upperBound, visited=[]):
		maxVisited = visited
		destinations = board.moveableDestinations(start)
		destinations.sort(key = lambda x : len(board.adjacentImpassable(x)), reverse=True)
	
		for dest in destinations:
			if time.clock() - self.timer > 0.8:
				break
			if dest not in visited:
				newVisited = list(visited)
				newVisited.append(dest)
				newVisited = self.longestPath(board, dest, upperBound, newVisited)
				if len(newVisited) > len(maxVisited):
					maxVisited = newVisited
					if len(maxVisited) == upperBound:
						break
		return maxVisited
    	
	class PathIt:
		def __init__(self, node, visited, board):
			self.node = node
			self.visited = visited
			self.score = len(tron.floodfill.execute(board, node, visited))
			self.visited.append(self.node)
		
		def __str__(self):
			return "Score: " + str(self.score) + ", Path: " + str(self.visited)
		
		def __cmp__(self, other):
			return cmp(self.score, other.score)
    	
	class Path:
		def __init__(self, node, visited, prevScore, diffSequence, board):
			self.node = node
			self.visited = visited
			self.visited.append(node)
			self.board = board
			newScore = len(tron.floodfill.execute(board, self.node, self.visited))
			diffSequence.append(prevScore - newScore - 1)
			self.diffSequence = diffSequence
			self.score = newScore
		
		def __str__(self):
			return "Score: " + str(self.score) + ", Path: " + str(self.visited)
		
		def __cmp__(self, other):
			return cmp(self.calcCmpScore(), other.calcCmpScore())
			
		def calcCmpScore(self):
			selfscore = sum([(self.diffSequence[i] * (len(self.diffSequence) - i)) for i in range(0, len(self.diffSequence))])
			return selfscore - len(self.board.adjacentImpassableOrVisited(self.node, self.visited))

'''
	class Path:
		def __init__(self, node, visited, initScore, board):
			self.node = node
			self.visited = visited
			self.board = board
			self.prevScore = initScore
			
			#self.score = initScore + len(tron.floodfill.execute(board, self.node, self.visited))# + len(self.visited)
		
		def __str__(self):
			return "Score: " + str(self.score) + ", Path: " + str(self.visited)
		
		def __cmp__(self, other):
			#return 0 - cmp(float(self.score) / (len(self.visited) + 1) + len(self.board.adjacentImpassableOrVisited(self.node, self.visited)), float(other.score) / (len(other.visited) + 1) + len(self.board.adjacentImpassableOrVisited(other.node, other.visited)))
			return 0 - cmp(self.score + len(self.board.adjacentImpassableOrVisited(self.node, self.visited)), other.score + len(self.board.adjacentImpassableOrVisited(other.node, other.visited)))
'''
			
class Floodfill:
	def execute(self, board, origin, exclude=[]):
		start = time.clock()
		visited=[]
		queue = deque()
		queue.append(origin)
	
		while len(queue) > 0:
			node = queue.popleft()
			if node in visited:
				continue
			
			west = self.continuouslyMoveDirection(board, node, tron.WEST, exclude)
			east = self.continuouslyMoveDirection(board, node, tron.EAST, exclude)
		
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
		#tron.debug("FLOODFILL TOOK: " + str(time.clock() - start) + "\n")
		return visited
        
	def continuouslyMoveDirection(self, board, start, dir, exclude=[]):
		loc = start
		newLoc = board.rel(dir, loc)
		while board.passable(newLoc) and newLoc not in exclude:
			loc = newLoc
			newLoc = board.rel(dir, loc)
		return loc
