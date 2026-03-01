# ─── core/node.py ────────────────────────────────────────────────────────────
"""
A single cell in the search space.

Attributes
----------
row, col  : grid coordinates
g         : cost from start  (used by A*)
h         : heuristic to goal
f         : g + h  (priority key)
parent    : previous Node on the best path found so far
"""

from __future__ import annotations


class Node:
    # Cell state constants – stored on the node so the grid can colour it
    EMPTY    = "empty"
    WALL     = "wall"
    START    = "start"
    GOAL     = "goal"
    FRONTIER = "frontier"
    VISITED  = "visited"
    PATH     = "path"
    AGENT    = "agent"

    def __init__(self, row: int, col: int):
        self.row    = row
        self.col    = col
        self.state  = Node.EMPTY
        self.g      = float("inf")   # unknown cost at creation
        self.h      = 0.0
        self.f      = float("inf")
        self.parent: Node | None = None

    # ── comparison operators needed by heapq ─────────────────────────────
    def __lt__(self, other: "Node") -> bool:
        return self.f < other.f

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))

    def __repr__(self) -> str:
        return f"Node({self.row},{self.col},g={self.g:.1f},h={self.h:.1f})"

    # ── helpers ───────────────────────────────────────────────────────────
    def reset_search(self):
        """Clear search state but keep wall/start/goal."""
        self.g      = float("inf")
        self.h      = 0.0
        self.f      = float("inf")
        self.parent = None
        if self.state in (Node.FRONTIER, Node.VISITED, Node.PATH, Node.AGENT):
            self.state = Node.EMPTY

    @property
    def pos(self) -> tuple[int, int]:
        return (self.row, self.col)
