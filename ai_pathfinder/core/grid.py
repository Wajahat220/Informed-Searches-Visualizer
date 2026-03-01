
"""
* Create / resize the grid.
* Provide neighbour lookup (4-directional).
* Random obstacle generation.
* Reset helpers (clear path vs full reset).
"""

from __future__ import annotations
import random
from core.node import Node


class Grid:
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]   # up/down/left/right

    def __init__(self, rows: int, cols: int):
        self.rows  = rows
        self.cols  = cols
        self.cells: list[list[Node]] = []
        self.start: Node | None = None
        self.goal:  Node | None = None
        self._build()

    
    def _build(self):
        self.cells = [[Node(r, c) for c in range(self.cols)]
                      for r in range(self.rows)]
        self.start = None
        self.goal  = None

    def resize(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._build()

    
    def node(self, row: int, col: int) -> Node:
        return self.cells[row][col]

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def neighbours(self, node: Node) -> list[Node]:
        result = []
        for dr, dc in self.DIRECTIONS:
            r, c = node.row + dr, node.col + dc
            if self.in_bounds(r, c):
                nb = self.cells[r][c]
                if nb.state != Node.WALL:
                    result.append(nb)
        return result

    
    def set_start(self, row: int, col: int):
        if self.start:
            self.start.state = Node.EMPTY
        n = self.cells[row][col]
        if n.state not in (Node.WALL, Node.GOAL):
            n.state    = Node.START
            self.start = n

    def set_goal(self, row: int, col: int):
        if self.goal:
            self.goal.state = Node.EMPTY
        n = self.cells[row][col]
        if n.state not in (Node.WALL, Node.START):
            n.state   = Node.GOAL
            self.goal = n

    def toggle_wall(self, row: int, col: int):
        n = self.cells[row][col]
        if n.state == Node.EMPTY:
            n.state = Node.WALL
        elif n.state == Node.WALL:
            n.state = Node.EMPTY

    def add_wall(self, row: int, col: int):
        n = self.cells[row][col]
        if n.state == Node.EMPTY:
            n.state = Node.WALL

    
    def generate_random(self, density: float):
        """
        Fill grid randomly.  density is 0.0–1.0 fraction of cells to wall.
        Always places start top-left area, goal bottom-right area.
        """
        self._build()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.cells[r][c].state = Node.WALL

    
        sr, sc = 0, 0
        gr, gc = self.rows - 1, self.cols - 1
        self.cells[sr][sc].state = Node.EMPTY
        self.cells[gr][gc].state = Node.EMPTY
        self.set_start(sr, sc)
        self.set_goal(gr, gc)

    
    def clear_search(self):
        """Remove frontier/visited/path colouring; keep walls, start, goal."""
        for r in range(self.rows):
            for c in range(self.cols):
                n = self.cells[r][c]
                n.reset_search()
    
        if self.start:
            self.start.state = Node.START
        if self.goal:
            self.goal.state  = Node.GOAL

    def full_reset(self):
        """Wipe everything."""
        self._build()

    
    def spawn_obstacle(self, exclude: set[tuple[int, int]]) -> tuple[int, int] | None:
        """
        Place a wall on a random EMPTY cell not in *exclude*.
        Returns (row,col) of new wall or None if no space available.
        """
        empty_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.cells[r][c].state == Node.EMPTY
            and (r, c) not in exclude
        ]
        if not empty_cells:
            return None
        r, c = random.choice(empty_cells)
        self.cells[r][c].state = Node.WALL
        return (r, c)
