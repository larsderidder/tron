'''
Algorithms for the attack phase, that is before the enemy is unreachable. The
goal is to get into a position that we have more positions on the board
available than they have in the floodfill phase. This is often done by getting
near to them as soon as possible, to maximize the space we could claim.
'''
import tron, time, sys

class AStar:
    '''
    Implementation of the A* shortest path algorithm.
    '''

    def execute(self, board):
		start = time.clock()
		goal = board.them()
		
		closedSet = []
		openSet = [board.me()]
		came_from = {}
		travelledScore = {board.me(): 0}
		finalScore = {board.me(): board.distance(board.me(), goal)}
		finalNode = None
		while openSet:
			node = openSet[0]
			minScore = finalScore[node]
			for n in openSet:
				if finalScore[n] < minScore:
					minScore = finalScore[n]
					node = n
			finalNode = node
			if node == goal or time.clock() - board.startTime > 0.9:
				tron.log("Shortest path took: " + str(float(time.clock() - start)))
				return self.reconstructPath(finalNode, came_from)
			openSet.remove(node)
			closedSet.append(node)
			neighbours = [dest for dest in board.adjacent(node) if board.passable(dest) and dest not in closedSet or dest == goal]
			newTravelledScore = travelledScore[node] + 1
			for neighbour in neighbours:				
				if neighbour not in openSet:
					openSet.append(neighbour)
					tentative = True
				elif newTravelledScore < travelledScore[neighbour]:
					tentative = True
				else:
					tentative = False
				if tentative:
					came_from[neighbour] = node
					travelledScore[neighbour] = newTravelledScore
					finalScore[neighbour] = newTravelledScore + board.distance(neighbour, goal)
		tron.log("Shortest path took: " + str(float(time.clock() - start)))
		tron.log("Shortest path failed.")
		return None
		
    def reconstructPath(self, node, came_from):
        '''
        Reconstruct the path back to the node from the path given in came_from.
        came_from is an array with nodes.
        '''
        if node in came_from:
            path = self.reconstructPath(came_from[node], came_from)
            path.append(node)
            return path
        else:
            return [node]
			
class Minimax:
    '''
    Implementation of the minimax algorithm, to minimize loss. Loss is defined
    as the difference between the spaces we can still travel to and the spaces
    they can still travel to. In other words, it aims to maximize our_nodes -
    their_nodes.
    '''

    def execute(self, board):
		levels = self.minimax(board)
		root = levels[0].nodes[0]
		
		tron.log("Minimax level: " + str(len(levels)-1))
		
		minimaxSpaceCount = dict()
		for node in root.children:
			for dir in board.moves(board.me()):
				if board.rel(dir) == node.me:
					minimaxSpaceCount[dir] = node.score
		return minimaxSpaceCount
		
    def minimax(self, board):
		boardSize = (board.width - 2) * (board.height - 2)
		root = Minimax.TreeNode(None, board.me(), board.them(), [board.me(), board.them()], 0, True)
		levels = [Minimax.Level([root])]
		#tron.log(levels)
		root = levels[0].nodes[0]
		
		#outOfTime = False
		while levels[-1].nodes and time.clock() - board.startTime < 0.82:
			currLevel = levels[-1]
			newLevel = Minimax.Level([])
							
			currLevel.nodes.sort()
			minScore = currLevel.nodes[0].score
			
			for node in currLevel.nodes:
				if time.clock() - board.startTime > 0.82:
                    # Break out if we notice we have not enough time left.
					break
				if node.score > minScore:
					continue
				myNeighbours = board.moveableDestinations(node.me, node.visited)
				
				for myNeighbour in myNeighbours:
					newVisited = list(node.visited)
					newVisited.append(myNeighbour)
					score = tron.dijkstra.meThemDifference(board, myNeighbour, node.them, newVisited)
					node.addChild(myNeighbour, node.them, newVisited, score)
				
				if time.clock() - board.startTime > 0.85:
                    # Break out if we notice we have not enough time left.
					break
					
				for child in node.children:
					theirNeighbours = board.moveableDestinations(child.them, node.visited)
					for theirNeighbour in theirNeighbours:
						newVisited = list(child.visited)
						newVisited.append(theirNeighbour)
						if theirNeighbour == child.me:
							score = 0
						elif len(board.adjacentImpassableOrVisited(child.me, newVisited)) == 4:
							score = -boardSize
						elif len(board.adjacentImpassableOrVisited(theirNeighbour, newVisited)) == 4:
							score = boardSize
						else: 
							score = tron.dijkstra.meThemDifference(board, child.me, theirNeighbour, newVisited)
						child.addChild(child.me, theirNeighbour, newVisited, score)
					newLevel.nodes.extend(child.children)
				#nodelevel
			#if outOfTime:
			#	break
			levels.append(newLevel)
		root.refineScore()
		
		return levels
		
    class TreeNode:
        def __init__(self, parent, me, them, visited, score, myMove):
            self.parent = parent
            self.me = me
            self.them = them
            self.visited = visited
            self.score = score
            self.myMove = myMove
            self.children = []

        def addChild(self, me, them, moveVisited, score):
            self.children.append(Minimax.TreeNode(self, me, them, moveVisited, score, not self.myMove))

        def refineScore(self):
			if self.children:
				if self.myMove:
					maxMyScore = -sys.maxint
					for child in self.children:
						child.refineScore()
						if child.score > maxMyScore:
							maxMyScore = child.score
					self.score = maxMyScore
				else:
					minTheirScore = sys.maxint
					for child in self.children:
						child.refineScore()
						if child.score < minTheirScore:
							minTheirScore = child.score
					self.score = minTheirScore
		
        def descendantOf(self, ancestor):
            if self.parent is ancestor:
                return True
            if self.parent is None:
                return False
            return self.parent.descendantOf(ancestor)
					
        def __cmp__(self, other):
            return cmp(self.score, other.score)

    class Level:
        def __init__(self, nodes):
            self.nodes = nodes
