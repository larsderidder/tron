'''
Survival algorithms for the survival phase, that is after the enemy can't be
reached anymore. Try to fill the space as efficiently as possible.
'''
import tron, time

from heapq import heappush, heappop
	
class OptimizeSpaceAlgorithm:

    def __init__(self):
		self.cachedPaths = []
		
    def prepareCachedPaths(self, dest):
        '''
        Prepare cache for next decision round. Only those paths computed that
        start with the actual choice made (dest node) are kept as they are of 
        course they are the only relevant ones.
        '''
        newAllPaths = [path for path in self.cachedPaths if path.visited and path.visited[0] == dest]
        for path in newAllPaths:
            path.visited = path.visited[1:]
            path.diffSequence = path.diffSequence[1:]
        return newAllPaths

    def execute(self, board, spaceCount):
        timer = time.clock()

        # Find longest path
        path = self.longestPathFloodfill(board, spaceCount)
        tron.log("Longestpath: " + str(len(path)))
        dest = path[0]

        # Find which direction is relevant for the computed destination
        choice = [dir for dir in board.moves() if board.rel(dir) == dest][0]

        # Prepare cached paths for next decision round
        self.cachedPaths = self.prepareCachedPaths(dest)

        tron.log("Survival algorithm took: " + str(time.clock() - timer))
        return choice

    def longestPathFloodfill(self, board, spaceCount):
        '''
        Compute the longest path possible using the floodfill algorithm.
        '''
        # start off with cached paths (if there are any)
        queue = self.cachedPaths
        origin = board.me()

        originScore = tron.floodfill.floodfillScore(board, origin, [])
        startnodes = set([path.visited[0] for path in queue if path.visited])
        directions = [dir for dir in board.moves(origin) if board.rel(dir, origin) not in startnodes]
        for dir in directions:
            path = OptimizeSpaceAlgorithm.Path(board, board.rel(dir, origin), [], originScore, [], spaceCount[dir])
            heappush(queue, path)

        newAllPaths = []
        while queue and time.clock() - board.startTime < 0.82:
            path = heappop(queue)
            destinations = board.moveableDestinations(path.node, path.visited)
            if not destinations:
                heappush(newAllPaths, path)
                continue
            for dest in destinations:
                newScore = tron.floodfill.floodfillScore(board, dest, path.visited)
                newPath = OptimizeSpaceAlgorithm.Path(board, dest, list(path.visited), path.score, list(path.diffSequence), newScore)
                heappush(queue, newPath)

		for path in queue:
			heappush(newAllPaths, path)
		self.cachedPaths = newAllPaths
		
		maxPath = newAllPaths[0]
		for path in newAllPaths:
			if len(path.visited) > len(maxPath.visited):
				maxPath = path
		tron.log(maxPath.visited)
		tron.log(maxPath.score)
		return maxPath.visited
		
    class Path:
        '''
        Path entity, containing the current node, the visited nodes, and a
        score, amongst other things. Can be compared to other paths, which
        compares the scores of each path.

        The Path also contains a diffSequence. This is a sequence of diffs
        between scores, so that for every point on the path the score can be
        calculated.
        '''

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
            selfScore = 0
            for i in xrange(0, len(self.diffSequence)):
                selfScore += self.diffSequence[i] * (len(self.diffSequence) - i)
			#selfscore = sum([(self.diffSequence[i] * (len(self.diffSequence) - i)) for i in range(0, len(self.diffSequence))])
            return selfScore - len(self.board.adjacentImpassableOrVisited(self.node, self.visited))
