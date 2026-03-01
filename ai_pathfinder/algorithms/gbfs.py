
"""
Greedy Best-First Search (GBFS) — step-by-step generator version.

KEY DIFFERENCE FROM A*
-----------------------
f(n) = h(n)   ← ignores g(n) entirely!

This makes GBFS:
  ✔ Faster than A* in many cases (less computation)
  ✘ NOT guaranteed to find the optimal (shortest) path
  ✘ Can be fooled by dead ends and re-explore areas

It is "greedy" because it always moves toward what looks closest to
the goal, without caring how far it has already travelled.

Compare this to A* which balances both g (effort spent) and h (effort ahead).
"""

from __future__ import annotations
import heapq
from core.node import Node
from core.grid import Grid


def gbfs(grid: Grid, heuristic) -> tuple[list[Node], int]:
    """
    Run GBFS to completion (instant, used in re-planning).
    """
    start = grid.start
    goal  = grid.goal
    if start is None or goal is None:
        return [], 0

    start.h = heuristic(start, goal)
    start.f = start.h   # GBFS: f = h only

    open_heap: list[Node] = []
    heapq.heappush(open_heap, start)
    open_set:   set[Node] = {start}
    visited:    set[Node] = set()
    nodes_visited = 0

    while open_heap:
        current = heapq.heappop(open_heap)
        open_set.discard(current)

        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1

        if current == goal:
            return _reconstruct(goal), nodes_visited

        for nb in grid.neighbours(current):
            if nb in visited or nb in open_set:
                continue
            nb.h      = heuristic(nb, goal)
            nb.f      = nb.h
            nb.parent = current
            heapq.heappush(open_heap, nb)
            open_set.add(nb)

    return [], nodes_visited


def gbfs_generator(grid: Grid, heuristic):
    """
    Animated generator version — same yield protocol as astar_generator.
    """
    start = grid.start
    goal  = grid.goal
    if start is None or goal is None:
        yield ("no_path", [], 0)
        return

    start.h = heuristic(start, goal)
    start.f = start.h

    open_heap: list[Node] = []
    heapq.heappush(open_heap, start)
    open_set:   set[Node] = {start}
    visited:    set[Node] = set()
    nodes_visited = 0

    while open_heap:
        current = heapq.heappop(open_heap)
        open_set.discard(current)

        if current in visited:
            continue
        visited.add(current)
        nodes_visited += 1

        yield ("step", current, set(open_set))

        if current == goal:
            yield ("path", _reconstruct(goal), nodes_visited)
            return

        for nb in grid.neighbours(current):
            if nb in visited or nb in open_set:
                continue
            nb.h      = heuristic(nb, goal)
            nb.f      = nb.h
            nb.parent = current
            heapq.heappush(open_heap, nb)
            open_set.add(nb)

    yield ("no_path", [], nodes_visited)


def _reconstruct(goal: Node) -> list[Node]:
    path = []
    cur  = goal
    while cur is not None:
        path.append(cur)
        cur = cur.parent
    path.reverse()
    return path
