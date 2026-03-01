
"""


STATE MACHINE

IDLE     → not started
MOVING   → agent walking along current path
DONE     → agent reached goal (or no path found)

Per-step logic (called by GUI timer):
1.  Move agent one cell forward on current path.
2.  Maybe spawn new obstacle (ObstacleSpawner).
3.  If obstacle is ON remaining path → re-plan from current position.
4.  Repeat until goal reached or path exhausted.
"""

from __future__ import annotations
from core.grid              import Grid
from core.node              import Node
from core.planner           import Planner
from dynamic.obstacle_spawner import ObstacleSpawner


class DynamicController:
    IDLE    = "idle"
    MOVING  = "moving"
    DONE    = "done"

    def __init__(self, grid: Grid, planner: Planner):
        self.grid       = grid
        self.planner    = planner
        self.spawner    = ObstacleSpawner(grid)
        self.state      = self.IDLE

        self.agent_node:   Node | None = None
        self.path_remaining: list[Node] = []
        self.replan_count  = 0

        # Callbacks → set by GUI
        self.on_move:    callable | None = None   # (agent_node)
        self.on_replan:  callable | None = None   # (new_path)
        self.on_done:    callable | None = None   # (reached_goal: bool)
        self.on_wall:    callable | None = None   # (row, col)

    
    def start(self, initial_path: list[Node]):
        """Begin dynamic movement along *initial_path*."""
        if len(initial_path) < 2:
            if self.on_done:
                self.on_done(False)
            return
        self.path_remaining = list(initial_path)
        self.agent_node     = self.path_remaining[0]
        self.replan_count   = 0
        self.state          = self.MOVING

    def force_check_collision(self, row: int, col: int):
        """Called by the GUI when a user manually places a wall."""
        if self.state != self.MOVING:
            return

        # Check if the manual wall was placed on the path we planned to take
        remaining_positions = {n.pos for n in self.path_remaining}
        if (row, col) in remaining_positions:
            print(f"Manual Wall detected at {row, col}! Replanning...")
            self._do_replan()

    def step(self) -> bool:
        """
        Advance agent one step.
        Returns True if still moving, False when finished.
        """
        if self.state != self.MOVING:
            return False

        
        if len(self.path_remaining) < 2:
            # Reached (or stuck at) last node
            self._finish(self.agent_node == self.grid.goal)
            return False

        # Remove the cell we just left from path
        self.path_remaining.pop(0)
        next_node = self.path_remaining[0]

        # Safety: next node might have become a wall since planning
        if next_node.state == Node.WALL:
            if not self._do_replan():
                return False
            return True

        # Move
        if self.agent_node and self.agent_node != self.grid.start:
            # mark old position as empty so visualiser can recolour
            if self.agent_node.state == Node.AGENT:
                self.agent_node.state = Node.EMPTY

        self.agent_node       = next_node
        self.agent_node.state = Node.AGENT

        if self.on_move:
            self.on_move(self.agent_node)

        # ── 2. Maybe spawn obstacle ───────────────────────────────────────
        protected = {
            self.agent_node.pos,
            self.grid.start.pos if self.grid.start else (-1, -1),
            self.grid.goal.pos  if self.grid.goal  else (-1, -2),
        }
        new_wall = self.spawner.maybe_spawn(protected)

        if new_wall:
            if self.on_wall:
                self.on_wall(*new_wall)

            # ── 3. Check if new wall blocks remaining path ────────────────
            remaining_positions = {n.pos for n in self.path_remaining}
            if new_wall in remaining_positions:
                if not self._do_replan():
                    return False

        # Check if agent arrived at goal
        if self.agent_node == self.grid.goal:
            self._finish(True)
            return False

        return True

    # ── private ──────────────────────────────────────────────────────────
    def _do_replan(self) -> bool:
        """
        Re-plan from current agent position to original goal.
        Returns False if no path found.
        """
        # Temporarily set grid.start to agent's current position
        original_start = self.grid.start
        self.grid.start = self.agent_node
        self.agent_node.state = Node.START   # required by neighbour() check

        # Reset search state on all nodes (keep walls/goal)
        self.grid.clear_search()
        self.agent_node.state = Node.START
        self.grid.start       = self.agent_node

        new_path = self.planner.instant_plan()
        self.replan_count += 1

        # Restore real start for display purposes (but keep agent as effective start)
        self.grid.start = original_start
        if original_start:
            original_start.state = Node.START

        if not new_path:
            self._finish(False)
            return False

        self.path_remaining = new_path
        if self.on_replan:
            self.on_replan(new_path)
        return True

    def _finish(self, success: bool):
        self.state = self.DONE
        if self.on_done:
            self.on_done(success)
