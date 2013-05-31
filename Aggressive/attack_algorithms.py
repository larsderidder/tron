
import tron, time

from heapq import heappush, heappop

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
		while len(queue) > 0 and time.clock() - start < 0.9:
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
		return shortestPath
		
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

	def execute(self, board, spaceCount, enemySpaceCount):
		root = Minimax.TreeNode(board.me(), board.them(), [], True, 0)
		for dir in spaceCount.keys():
			root.addChild(board.rel(dir, root.me), spaceCount[dir] - enemySpaceCount[dir])
		queue = root.children
		while len(queue) > 0 and time.clock() - board.startTime < 0.92:
			node = queue.pop()
			if node.myMove:
				for dest in board.moveableDestinations(node.me):
					if dest not in node.visited:
						myScore = tron.floodfill.floodfillScore(board, dest, node.visited)
						theirScore = tron.floodfill.floodfillScore(board, node.them, node.visited)
						child = node.addChild(dest, myScore - theirScore)
						queue.append(child)
			else:
				for dest in board.moveableDestinations(node.them):
					if dest not in node.visited:
						theirScore = tron.floodfill.floodfillScore(board, dest, node.visited)
						myScore = tron.floodfill.floodfillScore(board, node.me, node.visited)
						child = node.addChild(dest, myScore - theirScore)
						queue.append(child)
					
	class TreeNode:
		def __init__(self, me, them, visited, myMove, score):
			self.me = me
			self.them = them
			self.visited = visited
			self.myMove = myMove
			self.score = score
			self.children = []
			
		def addChild(self, node, score):
			if self.myMove:
				newVisited = list(self.visited)
				newVisited.append(self.me)
				child = Minimax.TreeNode(node, self.them, newVisited, False, score)
			else:
				newVisited = list(self.visited)
				newVisited.append(self.them)
				child = Minimax.TreeNode(self.me, node, newVisited, True, score)
			self.children.append(child)
			return child
		
