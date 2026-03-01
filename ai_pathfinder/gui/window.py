# ─── gui/window.py ───────────────────────────────────────────────────────────
"""
AppWindow — top-level Tk window.

Wires together:
  Sidebar (controls)  ←→  AppWindow  ←→  Visualizer (canvas)
                                     ←→  MetricsPanel
                                     ←→  Planner / DynamicController
"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

import config as C
from core.grid              import Grid
from core.node              import Node
from core.planner           import Planner
from dynamic.replanner      import DynamicController
from gui.visualizer         import Visualizer
from gui.controls           import Sidebar
from gui.metrics_panel      import MetricsPanel
from algorithms.heuristics  import HEURISTICS


class AppWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("AI Pathfinder — A* & GBFS Visualiser")
        root.configure(bg=C.COLOR_BG)
        root.resizable(True, True)

        # ── Model ─────────────────────────────────────────────────────────
        self.grid    = Grid(C.DEFAULT_ROWS, C.DEFAULT_COLS)
        self.planner = Planner(self.grid)
        self.dyn     = DynamicController(self.grid, self.planner)

        # ── Layout ────────────────────────────────────────────────────────
        self._build_layout()

        # ── Wire planner callbacks ────────────────────────────────────────
        self.planner.on_step    = self._on_search_step
        self.planner.on_path    = self._on_path_found
        self.planner.on_no_path = self._on_no_path

        # ── Wire dynamic callbacks ─────────────────────────────────────────
        self.dyn.on_move   = self._on_agent_move
        self.dyn.on_replan = self._on_replan
        self.dyn.on_done   = self._on_dynamic_done
        self.dyn.on_wall   = self._on_new_wall

        # ── State flags ───────────────────────────────────────────────────
        self._searching   = False
        self._moving      = False
        self._search_path: list[Node] = []

        # Initial grid draw
        self._create_grid()

    # ── layout ────────────────────────────────────────────────────────────
    def _build_layout(self):
        callbacks = {
            "create_grid": self._create_grid,
            "set_mode":    self._set_draw_mode,
            "random_map":  self._random_map,
            "start":       self._start,
            "clear_path":  self._clear_path,
            "reset_grid":  self._reset_grid,
        }

        # Sidebar (left)
        self.sidebar = Sidebar(self.root, callbacks)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Right side: canvas + metrics
        right = tk.Frame(self.root, bg=C.COLOR_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas area (scrollable for large grids)
        canvas_frame = tk.Frame(right, bg=C.COLOR_BG)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.vis = Visualizer(canvas_frame)

        # Metrics bar (bottom)
        self.metrics = MetricsPanel(right)
        self.metrics.pack(fill=tk.X, side=tk.BOTTOM)
        self.metrics.reset()

    # ── grid creation ─────────────────────────────────────────────────────
    def _create_grid(self):
        rows = self.sidebar.rows
        cols = self.sidebar.cols
        self.grid.resize(rows, cols)
        self.planner.grid = self.grid
        self.dyn.grid     = self.grid
        self.vis.attach_grid(self.grid)
        self.metrics.reset()
        self._searching = False
        self._moving    = False

    # ── draw mode ─────────────────────────────────────────────────────────
    def _set_draw_mode(self, mode: str):
        self.vis.set_draw_mode(mode)

    # ── random map ────────────────────────────────────────────────────────
    def _random_map(self):
        self._stop_animations()
        density = self.sidebar.density
        self.grid.generate_random(density)
        self.vis.refresh_all()
        self.metrics.reset()

    # ── start search ──────────────────────────────────────────────────────
    def _start(self):
        if self._searching or self._moving:
            return
        if self.grid.start is None or self.grid.goal is None:
            messagebox.showwarning("Missing",
                "Please set both a Start (green) and a Goal (blue) node.")
            return

        # Clear previous search visuals
        self.grid.clear_search()
        self.vis.refresh_all()
        self.metrics.reset()

        # Configure planner
        algo = self.sidebar.algorithm
        h    = HEURISTICS[self.sidebar.heuristic_name]
        self.planner.configure(algo, h)

        if self.sidebar.dynamic_mode:
            self._start_dynamic()
        else:
            self._start_static()

    # ── STATIC mode ───────────────────────────────────────────────────────
    def _start_static(self):
        self.metrics._status.config(text="Searching…")
        self._searching = True
        self.planner.start_search()
        self._search_tick()

    def _search_tick(self):
        if not self._searching:
            return
        still_going = self.planner.step()
        if still_going:
            self.root.after(C.SEARCH_DELAY, self._search_tick)
        # callbacks handle path/no-path

    def _on_search_step(self, current: Node, open_set: set[Node]):
        """Colour current node as VISITED, open_set as FRONTIER."""
        if current.state not in (Node.START, Node.GOAL):
            current.state = Node.VISITED
        for n in open_set:
            if n.state not in (Node.START, Node.GOAL, Node.VISITED):
                n.state = Node.FRONTIER
        self.vis.paint_node(current)
        self.vis.paint_nodes(open_set)
        self.metrics._nodes.config(text=str(self.planner.nodes_visited))

    def _on_path_found(self, path: list[Node]):
        self._searching = False
        self._search_path = path
        # Paint path
        for n in path:
            if n.state not in (Node.START, Node.GOAL):
                n.state = Node.PATH
        self.vis.refresh_all()
        self.metrics._nodes .config(text=str(self.planner.nodes_visited))
        self.metrics._cost  .config(text=str(self.planner.path_cost))
        self.metrics._time  .config(text=f"{self.planner.exec_time_ms:.1f}")
        self.metrics._status.config(text="Path Found ✓")

    def _on_no_path(self):
        self._searching = False
        self.metrics._nodes .config(text=str(self.planner.nodes_visited))
        self.metrics._time  .config(text=f"{self.planner.exec_time_ms:.1f}")
        self.metrics._status.config(text="No Path ✗")
        messagebox.showinfo("No Path", "No path found between start and goal.")

    # ── DYNAMIC mode ──────────────────────────────────────────────────────
    def _start_dynamic(self):
        """First find initial path instantly, then animate movement."""
        self.metrics._status.config(text="Planning…")
        path = self.planner.instant_plan()
        if not path:
            self.metrics._status.config(text="No Path ✗")
            messagebox.showinfo("No Path", "No initial path found.")
            return

        # Show initial path briefly
        for n in path:
            if n.state not in (Node.START, Node.GOAL):
                n.state = Node.PATH
        self.vis.refresh_all()
        self.metrics._nodes .config(text=str(self.planner.nodes_visited))
        self.metrics._cost  .config(text=str(self.planner.path_cost))
        self.metrics._time  .config(text=f"{self.planner.exec_time_ms:.1f}")
        self.metrics._replan.config(text="0")
        self.metrics._status.config(text="Moving…")

        self.dyn.start(path)
        self._moving = True
        self.root.after(C.MOVE_DELAY, self._move_tick)

    def _move_tick(self):
        if not self._moving:
            return
        still_going = self.dyn.step()
        self.vis.refresh_all()
        self.metrics._replan.config(text=str(self.dyn.replan_count))
        if still_going:
            self.root.after(C.MOVE_DELAY, self._move_tick)

    def _on_agent_move(self, agent: Node):
        pass   # refresh_all handles repainting

    def _on_replan(self, new_path: list[Node]):
        # Colour new planned path
        self.grid.clear_search()
        for n in new_path:
            if n.state not in (Node.START, Node.GOAL, Node.AGENT):
                n.state = Node.PATH
        self.metrics._nodes.config(text=str(self.planner.nodes_visited))
        self.metrics._cost .config(text=str(self.planner.path_cost))
        self.metrics._time .config(text=f"{self.planner.exec_time_ms:.1f}")

    def _on_new_wall(self, row: int, col: int):
        pass   # wall already set on node; refresh_all repaints it

    def _on_dynamic_done(self, success: bool):
        self._moving = False
        self.metrics._status.config(
            text="Goal Reached ✓" if success else "Blocked — No Path ✗"
        )
        if not success:
            messagebox.showinfo("Dynamic Mode",
                "Agent is blocked — no path to goal remains.")

    # ── clear / reset ─────────────────────────────────────────────────────
    def _clear_path(self):
        self._stop_animations()
        self.grid.clear_search()
        self.vis.refresh_all()
        self.metrics.reset()

    def _reset_grid(self):
        self._stop_animations()
        self.grid.full_reset()
        self.vis.refresh_all()
        self.metrics.reset()

    def _stop_animations(self):
        self._searching = False
        self._moving    = False
        self.planner._gen = None
        self.dyn.state    = DynamicController.IDLE
