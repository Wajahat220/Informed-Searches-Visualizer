
"""
All heuristic functions live here.

Each function signature:
    h(node, goal) -> float

Adding a new heuristic:
1.  Write the function below.
2.  Add it to HEURISTICS dict at the bottom.
3.  It automatically appears in the GUI dropdown.
"""

from __future__ import annotations
import math
from core.node import Node


def manhattan(node: Node, goal: Node) -> float:
    """
    Manhattan distance — sum of absolute differences in row and column.
    Admissible for 4-directional movement with cost = 1.
    h = |r1-r2| + |c1-c2|
    """
    return abs(node.row - goal.row) + abs(node.col - goal.col)


def euclidean(node: Node, goal: Node) -> float:
    """
    Euclidean distance — straight-line distance.
    h = sqrt((r1-r2)^2 + (c1-c2)^2)
    Not perfectly admissible for 4-directional but still useful.
    """
    return math.sqrt((node.row - goal.row) ** 2 +
                     (node.col  - goal.col) ** 2)



HEURISTICS: dict[str, callable] = {
    "Manhattan": manhattan,
    "Euclidean": euclidean,
}
