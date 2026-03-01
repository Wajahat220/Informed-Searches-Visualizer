# ─── gui/visualizer.py ───────────────────────────────────────────────────────
"""
Visualizer — owns the tkinter Canvas and draws the grid.

Drawing strategy
----------------
* On grid creation: draw every cell rectangle once, store canvas item IDs.
* On updates: only change the fill colour of affected cells (O(1) per cell).
  This is MUCH faster than redrawing the whole canvas every frame.
"""

from __future__ import annotations
import tkinter as tk
from core.grid  import Grid
from core.node  import Node
from gui.colors import color_for
import config as C


class Visualizer:
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.canvas = tk.Canvas(
            parent,
            bg=C.COLOR_BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.grid: Grid | None = None
        self._rects: list[list[int]] = []   # canvas item IDs [row][col]

        # Mouse interaction state
        self._draw_mode: str = "wall"        # "start" | "goal" | "wall" | "erase"
        self._drag_drawing = False

        self.canvas.bind("<Button-1>",        self._on_click)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    # ── grid setup ────────────────────────────────────────────────────────
    def attach_grid(self, grid: Grid):
        self.grid   = grid
        self._rects = []
        self.canvas.delete("all")

        rows, cols = grid.rows, grid.cols
        cs = C.CELL_SIZE

        # Resize canvas
        width  = cols * cs
        height = rows * cs
        self.canvas.config(width=width, height=height)

        # Draw cells
        for r in range(rows):
            row_ids = []
            for c in range(cols):
                x1, y1 = c * cs,     r * cs
                x2, y2 = x1 + cs,    y1 + cs
                iid = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color_for(grid.node(r, c).state),
                    outline=C.COLOR_GRID_LINE,
                    width=1,
                )
                row_ids.append(iid)
            self._rects.append(row_ids)

    def refresh_all(self):
        """Repaint every cell (called after full reset or random generation)."""
        if self.grid is None:
            return
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                self._paint(r, c)

    def paint_node(self, node: Node):
        self._paint(node.row, node.col)

    def paint_nodes(self, nodes):
        for n in nodes:
            self._paint(n.row, n.col)

    def _paint(self, r: int, c: int):
        if self.grid is None:
            return
        try:
            iid   = self._rects[r][c]
            state = self.grid.node(r, c).state
            self.canvas.itemconfig(iid, fill=color_for(state))
        except IndexError:
            pass

    # ── mouse interaction ─────────────────────────────────────────────────
    def set_draw_mode(self, mode: str):
        """mode: 'start' | 'goal' | 'wall' | 'erase'"""
        self._draw_mode = mode

    def _cell_at(self, x: int, y: int) -> tuple[int, int] | None:
        if self.grid is None:
            return None
        cs  = C.CELL_SIZE
        r, c = y // cs, x // cs
        if self.grid.in_bounds(r, c):
            return r, c
        return None

    def _on_click(self, event):
        self._drag_drawing = True
        self._apply(event.x, event.y)

    def _on_drag(self, event):
        if self._drag_drawing:
            self._apply(event.x, event.y)

    def _on_release(self, _event):
        self._drag_drawing = False

    def _apply(self, x: int, y: int):
        if self.grid is None:
            return
        cell = self._cell_at(x, y)
        if cell is None:
            return
        r, c = cell
        mode = self._draw_mode
        if mode == "start":
            self.grid.set_start(r, c)
        elif mode == "goal":
            self.grid.set_goal(r, c)
        elif mode == "wall":
            self.grid.add_wall(r, c)
        elif mode == "erase":
            n = self.grid.node(r, c)
            if n.state not in (Node.START, Node.GOAL):
                n.state = Node.EMPTY
        self.refresh_all()
