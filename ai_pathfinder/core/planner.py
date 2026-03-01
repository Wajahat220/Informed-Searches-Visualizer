
"""
Planner — bridges the algorithms and the GUI.

Responsibilities
----------------
* Own the search generator.
* Track metrics (nodes visited, path cost, time).
* Expose step() which the GUI calls via root.after().
* Provide instant_plan() for dynamic re-planning.
"""

from __future__ import annotations
import time
from core.node       import Node
from core.grid       import Grid
from algorithms.astar import astar, astar_generator
from algorithms.gbfs  import gbfs, gbfs_generator


class Planner:
    ALGORITHMS = {
        "A*":   (astar,  astar_generator),
        "GBFS": (gbfs,   gbfs_generator),
    }

    def __init__(self, grid: Grid):
        self.grid         = grid
        self._gen         = None        
        self._heuristic   = None
        self._algo_name   = "A*"

        
        self.nodes_visited = 0
        self.path_cost     = 0
        self.exec_time_ms  = 0.0
        self.path: list[Node] = []

        
        self.on_step:     callable | None = None   
        self.on_path:     callable | None = None   
        self.on_no_path:  callable | None = None   

        self._start_time: float = 0.0

   
    def configure(self, algo_name: str, heuristic):
        self._algo_name = algo_name
        self._heuristic = heuristic

    
    def start_search(self):
        """Initialise the generator.  GUI calls step() on a timer."""
        if self._heuristic is None:
            return
        self.nodes_visited = 0
        self.path_cost     = 0
        self.exec_time_ms  = 0.0
        self.path          = []
        self._start_time   = time.time()

        _, gen_fn  = self.ALGORITHMS[self._algo_name]
        self._gen  = gen_fn(self.grid, self._heuristic)

    def step(self) -> bool:
        """
        Advance search by one node expansion.
        Returns True if search is still running, False when done.
        """
        if self._gen is None:
            return False
        try:
            event, *data = next(self._gen)
        except StopIteration:
            return False

        if event == "step":
            current, open_set = data
            self.nodes_visited += 1
            if self.on_step:
                self.on_step(current, open_set)
            return True

        elif event == "path":
            path, visited = data
            self.path          = path
            self.nodes_visited = visited
            self.path_cost     = len(path) - 1 if path else 0
            self.exec_time_ms  = (time.time() - self._start_time) * 1000
            self._gen          = None
            if self.on_path:
                self.on_path(path)
            return False

        elif event == "no_path":
            _, visited = data
            self.nodes_visited = visited
            self.exec_time_ms  = (time.time() - self._start_time) * 1000
            self._gen          = None
            if self.on_no_path:
                self.on_no_path()
            return False

        return False

    
    def instant_plan(self) -> list[Node]:
        """
        Run the selected algorithm instantly (no animation).
        Used during dynamic re-planning.
        Updates metrics cumulatively (adds to existing counts).
        """
        if self._heuristic is None:
            return []
        t0           = time.time()
        instant_fn, _ = self.ALGORITHMS[self._algo_name]
        path, visited = instant_fn(self.grid, self._heuristic)

        self.nodes_visited  += visited
        self.path_cost       = len(path) - 1 if path else 0
        self.exec_time_ms   += (time.time() - t0) * 1000
        self.path            = path
        return path
