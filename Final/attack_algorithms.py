'''
Algorithms for the attack phase, that is before the enemy is unreachable. The
goal is to get into a position that we have more positions on the board
available than they have in the survival phase. This is often done by getting
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
    Implementation of the minimax algorithm, to maximize win. Win is defined
    as the difference between the spaces we can still travel to and the spaces
    they can still travel to. In other words, it aims to maximize our_nodes -
    their_nodes.
    '''
	
    def execute(self, board):
        levels = self.minimax(board)
        root = levels[0].nodes[0]

        tron.log("Minimax level: " + str(len(levels)-1))

        # Compute the minimax score for each direction we can take.
        minimaxSpaceCount = dict()
        for node in root.children:
            for dir in board.moves(board.me()):
                if board.rel(dir) == node.me:
                    minimaxSpaceCount[dir] = node.score
		return minimaxSpaceCount
		
    def minimax(self, board):
        '''
        Run the minimax algorithm. It keeps doing this until it has made a
        definitive choice or until it detects we're running out of time for our
        decision turn, after which it will break out of the computation.

        This algorithm basically simulates the game as long as it can, and build
        a decision tree out of it. It has a concept of levels, which is the
        depth of the decision tree, and a TreeNode which is a situation in the
        game, resulting from a number of moves.
        '''
        boardSize = (board.width - 2) * (board.height - 2)
        root = Minimax.TreeNode(None, board.me(), board.them(), [board.me(), board.them()], 0, True)
        levels = [Minimax.Level([root])]
        #tron.log(levels)
        root = levels[0].nodes[0]
		
		#outOfTime = False
        # Keep going until the next level has no nodes to visit
        while levels[-1].nodes and time.clock() - board.startTime < 0.82:
            currLevel = levels[-1]
            newLevel = Minimax.Level([])

            # Sort nodes based on score
            currLevel.nodes.sort()
            minScore = currLevel.nodes[0].score

            for node in currLevel.nodes:
                # Break if out of time
                if time.clock() - board.startTime > 0.82:
                    break
                if node.score > minScore:
                    continue
                myNeighbours = board.moveableDestinations(node.me, node.visited)
				
                for myNeighbour in myNeighbours:
                    newVisited = list(node.visited)
                    newVisited.append(myNeighbour)
                    score = tron.dijkstra.meThemDifference(board, myNeighbour, node.them, newVisited)
                    node.addChild(myNeighbour, node.them, newVisited, score)

                # Break if out of time
                if time.clock() - board.startTime > 0.85:
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
        '''
        A node is a given situation in the game. It has a parent (the previous
        situation), it has locations for me and for them, it has a list of
        visited nodes, a score and whether the situation is a result of a move
        of myself or of the enemy.
        '''
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
            '''
            Determine own score based on children.
            '''
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
        '''
        A level is a collection of nodes that can be visited.
        '''
        def __init__(self, nodes):
            self.nodes = nodes
