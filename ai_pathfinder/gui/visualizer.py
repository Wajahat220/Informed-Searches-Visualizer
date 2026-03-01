from __future__ import annotations
import tkinter as tk
from core.grid import Grid
from core.node import Node
from gui.colors import color_for
import config as C

class Visualizer:
    # Initializes canvas, default states, and binds input/resize events
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg=C.COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.grid: Grid | None = None
        self._rects: list[list[int]] = []
        self._cell_size = C.CELL_SIZE
        self._draw_mode: str = "wall"
        self._drag_drawing = False
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Configure>", self._on_resize)
        self.on_manual_wall = None # Add this callback placeholder  

    # Re-draws the grid whenever the window size changes
    def _on_resize(self, event):
        if self.grid:
            self.attach_grid(self.grid)

    # Calculates optimal cell size to fit window and creates centered grid rectangles
    def attach_grid(self, grid: Grid):
        self.grid = grid
        self._rects = []
        self.canvas.delete("all")
        rows, cols = grid.rows, grid.cols
        canv_w, canv_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if canv_w < 10: canv_w = cols * C.CELL_SIZE
        if canv_h < 10: canv_h = rows * C.CELL_SIZE
        self._cell_size = min(canv_w // cols, canv_h // rows)
        cs = self._cell_size
        offset_x = (canv_w - (cols * cs)) // 2
        offset_y = (canv_h - (rows * cs)) // 2
        for r in range(rows):
            row_ids = []
            for c in range(cols):
                x1, y1 = offset_x + (c * cs), offset_y + (r * cs)
                x2, y2 = x1 + cs, y1 + cs
                iid = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color_for(grid.node(r, c).state),
                    outline=C.COLOR_GRID_LINE,
                    width=1 if cs > 5 else 0,
                )
                row_ids.append(iid)
            self._rects.append(row_ids)

    # Iterates through all nodes to update their colors on screen
    def refresh_all(self):
        if self.grid is None: return
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                self._paint(r, c)

    # Updates the visual state of a single specific node object
    def paint_node(self, node: Node):
        self._paint(node.row, node.col)

    # Updates the visual state for a list or set of node objects
    def paint_nodes(self, nodes):
        for n in nodes:
            self._paint(n.row, n.col)

    # Modifies the fill color of an existing canvas item using O(1) lookup
    def _paint(self, r: int, c: int):
        if self.grid is None: return
        try:
            iid = self._rects[r][c]
            state = self.grid.node(r, c).state
            self.canvas.itemconfig(iid, fill=color_for(state))
        except IndexError:
            pass

    # Updates the internal state for which node type to place on click
    def set_draw_mode(self, mode: str):
        self._draw_mode = mode

    # Calculates grid coordinates from pixel coordinates considering offsets and scaling
    def _cell_at(self, x: int, y: int) -> tuple[int, int] | None:
        if self.grid is None: return None
        cs = self._cell_size
        off_x = (self.canvas.winfo_width() - (self.grid.cols * cs)) // 2
        off_y = (self.canvas.winfo_height() - (self.grid.rows * cs)) // 2
        r, c = (y - off_y) // cs, (x - off_x) // cs
        if self.grid.in_bounds(r, c):
            return int(r), int(c)
        return None

    # Activates drawing state and applies changes at click location
    def _on_click(self, event):
        self._drag_drawing = True
        self._apply(event.x, event.y)

    # Applies changes continuously as the mouse moves across the canvas
    def _on_drag(self, event):
        if self._drag_drawing:
            self._apply(event.x, event.y)

    # Deactivates the continuous drawing state
    def _on_release(self, _event):
        self._drag_drawing = False

    # Updates node states in the grid model based on current drawing mode
    # Modifies the grid model and triggers external callbacks for manual changes
    def _apply(self, x: int, y: int):
        if self.grid is None: return
        cell = self._cell_at(x, y)
        if cell is None: return
        r, c = cell
        mode = self._draw_mode

        if mode == "start":
            self.grid.set_start(r, c)
        elif mode == "goal":
            self.grid.set_goal(r, c)
        elif mode == "wall":
            # Add the wall to the grid data
            self.grid.add_wall(r, c)
            # Trigger the callback to notify window.py (and the replanner)
            if hasattr(self, 'on_manual_wall') and self.on_manual_wall:
                self.on_manual_wall(r, c)
        elif mode == "erase":
            n = self.grid.node(r, c)
            if n.state not in (Node.START, Node.GOAL):
                n.state = Node.EMPTY
        
        self.refresh_all()