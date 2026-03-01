
"""
ObstacleSpawner — randomly adds walls during agent movement.

Design decision: spawner only SUGGESTS a cell; the DynamicController
decides whether to place it (checks it won't land on agent/start/goal).
"""

from __future__ import annotations
import random
from core.grid import Grid
from core.node import Node
from config    import SPAWN_PROBABILITY


class ObstacleSpawner:
    def __init__(self, grid: Grid, probability: float = SPAWN_PROBABILITY):
        self.grid        = grid
        self.probability = probability

    def maybe_spawn(self, protected: set[tuple[int, int]]) -> tuple[int, int] | None:
        """
        With self.probability, add a wall to a random empty cell.
        *protected* is a set of (row,col) that must not be walled.

        Returns the (row,col) of the new wall, or None.
        """
        if random.random() > self.probability:
            return None
        return self.grid.spawn_obstacle(protected)
