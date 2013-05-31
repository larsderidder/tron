
import tron, time

from collections import deque

class Floodfill:

	def __init__(self):
		self.cache = dict()
		#self.avgTime = []

	def execute(self, board, origin, exclude=[]):
		start = time.clock()
		
		impassableNodes = board.impassableNodes()
		impassableNodes.extend(exclude)
		impassableNodes = frozenset(impassableNodes).difference([origin])
		if impassableNodes in self.cache.keys():
			result = self.cache[impassableNodes]
			if origin in result:
				#tron.log("CACHE CONSULTED")
				#self.avgTime.append(time.clock() - start)
				return result
		'''
		newExclude = list(exclude)
		newExclude.append(origin)
		newExclude.sort()
		excludeStr = str(newExclude)
		#tron.log(self.cache.keys())
		#tron.log(excludeStr)
		#tron.log()
		if excludeStr in self.cache.keys():
			#tron.log("CACHE CONSULTED")
			#tron.log("FLOODFILL TOOK: " + str(time.clock() - start))
			self.avgTime.append(time.clock() - start)
			return self.cache[excludeStr]
		'''
		visited=[]
		queue = deque()
		queue.append(origin)
		
		while len(queue) > 0:
			node = queue.popleft()
			if node in visited:
				continue
			
			west = self.findFurthestNodeInDirection(board, node, tron.WEST, exclude)
			east = self.findFurthestNodeInDirection(board, node, tron.EAST, exclude)
		
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
		#tron.log("FLOODFILL TOOK: " + str(time.clock() - start))
		self.cache[impassableNodes] = list(visited)
		#self.avgTime.append(time.clock() - start)
		return visited
	
	def floodfillScore(self, board, origin, exclude=[]):
		floodfilled = self.execute(board, origin, exclude)
		deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
#		articulationPoints = []
#		for node in floodfilled:
#			if len(board.adjacentImpassable) == 2 and node not in articulationPoints:
#				articulationPoints.append(node)
#		articulationPoints = [node for node in floodfilled if len(board.adjacentImpassable) == 2]
		
#		nrOfAreas = len(articulationPoints) + 1
#		if origin in articulationPoints:
#			nrOfAreas -= 1
		return len(floodfilled) - len(deadCorners) + min(len(deadCorners), 1)
        
	def findFurthestNodeInDirection(self, board, start, dir, exclude=[]):
		loc = start
		newLoc = board.rel(dir, loc)
		while board.passable(newLoc) and newLoc not in exclude:
			loc = newLoc
			newLoc = board.rel(dir, loc)
		return loc
