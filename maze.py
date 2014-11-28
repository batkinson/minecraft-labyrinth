
from random import choice

NORTH, SOUTH, EAST, WEST = 'N', 'S', 'E', 'W'
DIRECTIONS = [NORTH, SOUTH, EAST, WEST]
OPPOSING_DIRECTIONS = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}


class Maze(object):
    """A randomly generated, abstract maze."""
    def __init__(self, width=5, height=10):
        self.width, self.height = width, height
        self.cells = [[Cell(row, col, self) for col in xrange(width)] for row in xrange(height)]
        for col in xrange(width):
            for row in xrange(height):
                self[col, row].init_adjacents()

    def __getitem__(self, colrow):
        """Takes a tuple in the form of (row,col) and returns the given cell, or None"""
        col, row = colrow
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return None
        else:
            return self.cells[row][col]

    def generate(self, init_cell=(0, 0)):
        """Randomly generates a maze from start to cell"""
        start = self[init_cell]
        in_maze = set([start])
        adj_cells = set()
        adj_cells.update(start.adjacent_cells())

        while adj_cells.difference(in_maze):
            pick = choice(tuple(adj_cells.difference(in_maze)))
            in_maze.add(pick)
            pick_adjs = pick.adjacent_cells()
            connecting_cell = choice(tuple(pick_adjs.intersection(in_maze)))
            pick.remove_wall(pick.adjacent_direction(connecting_cell))
            adj_cells.remove(pick)
            adj_cells.update(pick_adjs)
        return self

    def __str__(self):
        """Converts the maze into a string."""
        result = ''
        for row in xrange(self.height):
            for col in xrange(self.width):
                result += str(self.cells[row][col])
            result += "\n"
        return result

    def __repr__(self):
        return self.__str__()


class Cell(object):
    """A single node in a maze graph."""
    def __init__(self, row, col, maze):
        self.row, self.col = row, col
        self.maze = maze
        self.walls = dict([(d, True) for d in DIRECTIONS])
        self.offsets = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}
        self._adjacent_cells = set()
        self.adjacent_directions = dict()

    def init_adjacents(self):
        """Initialize the adjacent data. Only call after initializing the Maze with Cells."""
        for d in DIRECTIONS:
            if not self[d] is None:
                self._adjacent_cells.add(self[d])
                self.adjacent_directions[self[d]] = d

    def disconnect(self):
        """Disconnects this cell from its adjacent cells."""
        for cell in self.adjacent_cells():
            cell.adjacent_cells().remove(self)

    def remove_wall(self, direction):
        """Removes the wall in the specified direction from cells on both sides."""
        self.walls[direction] = False
        if not self[direction] is None:
            self[direction].walls[OPPOSING_DIRECTIONS[direction]] = False

    def can_traverse(self, direction):
        """Returns whether it is possible to go in a direction."""
        return not self.walls[direction] and not self[direction] is None

    def adjacent_cells(self):
        """Returns the set of adjacent cells."""
        return self._adjacent_cells

    def adjacent_direction(self, cell):
        """Returns the direction of the adjacent cell or None"""
        return self.adjacent_directions[cell]

    def __getitem__(self, direction):
        """Takes a direction and returns the cell in that direction or None."""
        x_off, y_off = self.offsets[direction]
        return self.maze[self.col + x_off, self.row + y_off]

    def __str__(self):
        result = '['
        for d in DIRECTIONS:
            if not self.walls[d]:
                result += d
            else:
                result += ' '
        return result + ']'

    def __repr__(self):
        return self.__str__()
