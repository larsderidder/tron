
import tron, time, sys

from collections import deque

class Floodfill:
    """
    Implementation of the floodfill algorithm. It determines all nodes that can
    be reached from a certain point.
    """

    def execute(self, board, origin, exclude=[]):
        '''
        Compute all nodes that can be reached from the provided origin. Returns
        a list of all these nodes.

        The exclude parameter can be used to ignore certain nodes and consider
        them impassable.
        '''
        start = time.clock()
        visited = []
        queue = deque()
        queue.append(origin)

        while queue:
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
        tron.log("FLOODFILL TOOK: " + str(time.clock() - start))
        return visited
	
    def floodfillScore(self, board, origin, exclude=[]):
        '''
        Calculate the floodfillscore of a certain origin. This score is
        determined by looking at all nodes that can be visited, minus all dead
        corners (+1 if there are dead corners, because you have to end in some
        corner after all).
        '''
        floodfilled = self.execute(board, origin, exclude)
        # Dead corner = node from which you can go nowhere.
        deadCorners = [node for node in floodfilled if len(board.adjacentImpassable(node)) == 3]
        return len(floodfilled) - len(deadCorners) + min(len(deadCorners), 1)
        
    def findFurthestNodeInDirection(self, board, start, dir, exclude=[]):
        '''
        Find the node the furtest away that can still be entered (board.passable
        == True) in the direction provided.
        '''
        loc = start
        newLoc = board.rel(dir, loc)
        while board.passable(newLoc) and newLoc not in exclude:
            loc = newLoc
            newLoc = board.rel(dir, loc)
        return loc
		
class Dijkstra:
    '''
    Implementation of Dijkstra's shortest path algorithm for this application.
    '''

    def computeDistances(self, board, origin, exclude=[]):
        '''
        Compute the distances to all points on the board from point origin,
        including the distance to origin itself (always 0).

        Optionally, an exclude parameter can be given to exclude certain points
        on the board.
        '''
        start = time.clock()
        vertices = []
        allVertices = []
        distances = dict()
        for y in xrange(board.height):
            for x in xrange(board.width):
                coords = (y, x)
                if board.passable(coords) and coords not in exclude:
                    distances[coords] = sys.maxint
                    vertices.append(coords)
		distances[origin] = 0
        
		vertices.append(origin)
		while vertices:
			minScore = sys.maxint
			vertex = None
			for v in vertices:
				if distances[v] < minScore:
					minScore = distances[v]
					vertex = v
			if vertex is None:
				break
			vertices.remove(vertex)
			neighbours = [dest for dest in board.moveableDestinations(vertex) if dest in vertices and dest not in exclude]
			newScore = distances[vertex] + 1
			for neighbour in neighbours:
				if newScore < distances[neighbour]:
					distances[neighbour] = newScore
					
		tron.log("Dijkstra took: " + str(float(time.clock() - start)))
		tron.log(distances)
		return distances
		
    def meThemDifference(self, board, me, them, exclude=[]):
        '''
        Computes the difference between the number of nodes I can reach and they
        can reach (positive means me > them). This is used in computing weights
        for moves.
        '''
        meDistances = self.computeDistances(board, me, exclude)
        # Remove ourselves from distance computation
        del meDistances[me]
        themDistances = self.computeDistances(board, them, exclude)
        # Remove them from their distance computation
        del themDistances[them]

        # Compute a list of meNodes (nodes that I can reach first) and a list of
        # themNodes (nodes that they can reach first) and return the difference.
        meNodes = []
        themNodes = []
        for vertex in meDistances:
			if meDistances[vertex] < themDistances[vertex]:
				meNodes.append(vertex)
			elif themDistances[vertex] < meDistances[vertex]:
				themNodes.append(vertex)
        return len(meNodes) - len(themNodes)
		
