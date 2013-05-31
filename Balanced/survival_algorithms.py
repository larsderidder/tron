
import tron, time, sys

from collections import deque

from heapq import heappush, heappop
	
class OptimizeSpaceAlgorithm:

	'''
	def __init__(self):
		self.cachedPaths = []
		
	def prepareCachedPaths(self, origin):
		newAllPaths = [path for path in self.cachedPaths if len(path.visited) > 0 and path.visited[0] == origin]
		for path in newAllPaths:
			path.visited = path.visited[1:]
			path.diffSequence = path.diffSequence[1:]
		return newAllPaths
	'''

	def execute(self, board, spaceCount):
		timer = time.clock()
		path = self.longestPathFloodfill(board, spaceCount)
		tron.debug("Longestpath: " + str(len(path)) + "\n")
		dest = path[0]
		choice = [dir for dir in board.moves() if board.rel(dir) == dest][0]
		'''
		tron.log(len(self.cachedPaths))
		self.cachedPaths = self.prepareCachedPaths(dest)
		tron.log(len(self.cachedPaths))
		'''
		tron.log("Survival algorithm took: " + str(time.clock() - timer))
		return choice

	def longestPathFloodfill(self, board, spaceCount):
		#queue = self.cachedPaths
		queue = []
		origin = board.me()
		
		originScore = tron.floodfill.floodfillScore(board, origin, [])
		startnodes = set([path.visited[0] for path in queue if len(path.visited) > 0])
		#destinations = [dest for dest in board.moveableDestinations(origin) if dest not in startnodes]
		directions = [dir for dir in board.moves(origin) if board.rel(dir, origin) not in startnodes]
		tron.log(directions)
		for dir in directions:
			path = OptimizeSpaceAlgorithm.Path(board, board.rel(dir, origin), [], originScore, [], spaceCount[dir])
			heappush(queue, path)

		maxPath = queue[0]
		
		newAllPaths = []
		while len(queue) > 0 and time.clock() - board.startTime < 0.9:
			path = heappop(queue)
			destinations = [dest for dest in board.moveableDestinations(path.node) if dest not in path.visited]
			if len(destinations) == 0:
				heappush(newAllPaths, path)
				continue
			for dest in destinations:
				newScore = tron.floodfill.floodfillScore(board, dest, path.visited)
				newPath = OptimizeSpaceAlgorithm.Path(board, dest, list(path.visited), path.score, list(path.diffSequence), newScore)
				heappush(queue, newPath)
		for path in queue:
			heappush(newAllPaths, path)
		#self.cachedPaths = newAllPaths
		
		for path in newAllPaths:
			if len(path.visited) >= len(maxPath.visited):
				maxPath = path
		tron.log(maxPath.visited)
		tron.log(maxPath.score)
		return maxPath.visited
		
	class Path:
		def __init__(self, board, node, visited, prevScore, diffSequence, score):
			self.board = board
			self.node = node
			self.visited = visited
			self.visited.append(node)
			self.diffSequence = diffSequence
			self.diffSequence.append(prevScore - score - 1)
			self.score = score
		
		def __str__(self):
			return "Score: " + str(self.score) + ", Path: " + str(self.visited)
		
		def __cmp__(self, other):
			return cmp(self.calcCmpScore(), other.calcCmpScore())
			
		def calcCmpScore(self):
			selfscore = sum([(self.diffSequence[i] * (len(self.diffSequence) - i)) for i in range(0, len(self.diffSequence))])
			return selfscore - len(self.board.adjacentImpassableOrVisited(self.node, self.visited))

'''
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
		while len(currLevel) > 0 and time.clock() - board.startTime < 0.9:
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
		return maxPath.visited
    	
   	def longestPathBFS(self, board, start, upperBound, visited=[]):
   		queue = deque()
   		
		while len(queue) > 0:
			if time.clock() - board.startTime > 0.8:
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
    	
	def longestPathDFS(self, board, start, upperBound, visited=[]):
		maxVisited = visited
		destinations = board.moveableDestinations(start)
		destinations.sort(key = lambda x : len(board.adjacentImpassable(x)), reverse=True)
	
		for dest in destinations:
			if time.clock() - board.startTime > 0.8:
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
'''
