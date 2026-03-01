
"""
A* Search — step-by-step generator version.

KEY CONCEPTS
------------
f(n) = g(n) + h(n)

g(n)  : actual cost from START to n  (increases as we move away from start)
h(n)  : estimated cost from n to GOAL (heuristic)
f(n)  : total estimated cost of cheapest solution through n

The algorithm always expands the node with the LOWEST f value first.
This guarantees the OPTIMAL path when the heuristic is admissible
(never overestimates the true cost).

GENERATOR DESIGN
----------------
Instead of a blocking while-loop we yield after every expansion.
The GUI calls next(gen) on a timer so the canvas can redraw between steps.
"""

from __future__ import annotations
import heapq
from core.node   import Node
from core.grid   import Grid


def astar(grid: Grid, heuristic) -> tuple[list[Node], int]:
    """
    Run A* to completion (used for dynamic re-planning where we need
    the full path instantly).

    Returns
    -------
    path         : list of Nodes from start to goal (empty if no path)
    nodes_visited: count of nodes expanded
    """
    start = grid.start
    goal  = grid.goal
    if start is None or goal is None:
        return [], 0




    start.g = 0
    start.h = heuristic(start, goal)
    start.f = start.g + start.h

    open_heap: list[Node] = []
    heapq.heappush(open_heap, start)

    open_set:   set[Node] = {start}
    closed_set: set[Node] = set()
    nodes_visited = 0

    while open_heap:
        current = heapq.heappop(open_heap)
        open_set.discard(current)

        if current in closed_set:
            continue

        closed_set.add(current)
        nodes_visited += 1

        if current == goal:
            return _reconstruct(goal), nodes_visited

        for nb in grid.neighbours(current):
            if nb in closed_set:
                continue
            tentative_g = current.g + 1   # cost = 1 per step
            if tentative_g < nb.g:
                nb.g      = tentative_g
                nb.h      = heuristic(nb, goal)
                nb.f      = nb.g + nb.h
                nb.parent = current
                if nb not in open_set:
                    heapq.heappush(open_heap, nb)
                    open_set.add(nb)

    return [], nodes_visited   # no path found


# ── Generator version (for animated search) ──────────────────────────────────

def astar_generator(grid: Grid, heuristic):
    """
    Yields after EVERY node expansion so the GUI can animate each step.

    Yields
    ------
    ("step",   current_node, open_set_snapshot)   – during search
    ("path",   path_list,    nodes_visited)        – when goal found
    ("no_path",[], nodes_visited)                  – when exhausted
    """
    start = grid.start
    goal  = grid.goal
    if start is None or goal is None:
        yield ("no_path", [], 0)
        return
        


    start.g = 0
    start.h = heuristic(start, goal)
    start.f = start.g + start.h

    open_heap: list[Node] = []
    heapq.heappush(open_heap, start)
    open_set:   set[Node] = {start}
    closed_set: set[Node] = set()
    nodes_visited = 0

    while open_heap:
        current = heapq.heappop(open_heap)
        open_set.discard(current)

        if current in closed_set:
            continue
        closed_set.add(current)
        nodes_visited += 1

        yield ("step", current, set(open_set))   # ← GUI animates here

        if current == goal:
            yield ("path", _reconstruct(goal), nodes_visited)
            return

        for nb in grid.neighbours(current):
            if nb in closed_set:
                continue
            tentative_g = current.g + 1
            if tentative_g < nb.g:
                nb.g      = tentative_g
                nb.h      = heuristic(nb, goal)
                nb.f      = nb.g + nb.h
                nb.parent = current
                if nb not in open_set:
                    heapq.heappush(open_heap, nb)
                    open_set.add(nb)

    yield ("no_path", [], nodes_visited)


# ── helper ────────────────────────────────────────────────────────────────────

def _reconstruct(goal: Node) -> list[Node]:
    path = []
    cur  = goal
    while cur is not None:
        path.append(cur)
        cur = cur.parent
    path.reverse()
    return path
