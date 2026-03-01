

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import config as C
from algorithms.heuristics import HEURISTICS
from core.planner           import Planner


class Sidebar(tk.Frame):
    def __init__(self, parent, callbacks: dict, **kwargs):
        super().__init__(parent, bg=C.COLOR_SIDEBAR,
                         width=220, **kwargs)
        self.pack_propagate(False)
        self._cb  = callbacks
        self._build()

    
    def _build(self):
        self._section("GRID SETTINGS")
        self._grid_controls()
        self._section("MAP TOOLS")
        self._map_tools()
        self._section("ALGORITHM SETTINGS")
        self._algo_settings()
        self._section("ACTIONS")
        self._action_buttons()

    
    def _section(self, text):
        tk.Label(self, text=text, bg=C.COLOR_ACCENT, fg=C.COLOR_SIDEBAR,
                 font=("Verdana", 10, "bold"), anchor="w",
                 padx=8, pady=3).pack(fill=tk.X, pady=(8, 2))

    def _lbl(self, text):
        tk.Label(self, text=text, bg=C.COLOR_SIDEBAR, fg=C.COLOR_TEXT,
                 font=("Verdana", 9,"bold"), anchor="w").pack(
                     fill=tk.X, padx=10, pady=(4, 0))

    def _btn(self, text, cmd, color=None):
        b = tk.Button(
            self, text=text, command=cmd,
            bg=color or C.COLOR_BUTTON, fg=C.COLOR_TEXT,
            font=("Verdana", 10,"bold"), relief=tk.FLAT,
            activebackground=C.COLOR_BTN_ACT,
            activeforeground=C.COLOR_TEXT,
            cursor="hand2", pady=5,
        )
        b.pack(fill=tk.X, padx=10, pady=2)
        return b

    
    def _grid_controls(self):
        row_frame = tk.Frame(self, bg=C.COLOR_SIDEBAR)
        row_frame.pack(fill=tk.X, padx=10, pady=2)

        tk.Label(row_frame, text="Rows:", bg=C.COLOR_SIDEBAR,
                 fg=C.COLOR_TEXT, font=("Verdana", 9,"bold"), width=6).pack(side=tk.LEFT)
        self.rows_var = tk.StringVar(value=str(C.DEFAULT_ROWS))
        tk.Entry(row_frame, textvariable=self.rows_var, width=5,
                 bg=C.COLOR_BUTTON, fg=C.COLOR_TEXT,
                 insertbackground=C.COLOR_TEXT,
                 font=("Verdana", 9,"bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        col_frame = tk.Frame(self, bg=C.COLOR_SIDEBAR)
        col_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(col_frame, text="Cols:", bg=C.COLOR_SIDEBAR,
                 fg=C.COLOR_TEXT, font=("Verdana", 9,"bold"), width=6).pack(side=tk.LEFT)
        self.cols_var = tk.StringVar(value=str(C.DEFAULT_COLS))
        tk.Entry(col_frame, textvariable=self.cols_var, width=5,
                 bg=C.COLOR_BUTTON, fg=C.COLOR_TEXT,
                 insertbackground=C.COLOR_TEXT,
                 font=("Verdana", 9,"bold"), relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        self._btn("Create Grid", self._cb.get("create_grid"), "#00694B")

    
    def _map_tools(self):
        self._btn("Set Start",  lambda: self._cb["set_mode"]("start"))
        self._btn("Set Goal",   lambda: self._cb["set_mode"]("goal"))
        self._btn("Draw Walls", lambda: self._cb["set_mode"]("wall"))
        self._btn("Erase",      lambda: self._cb["set_mode"]("erase"))

        self._lbl("Obstacle Density:")
        self.density_var = tk.DoubleVar(value=0.25)
        tk.Scale(self, variable=self.density_var,
                 from_=0.0, to=0.60, resolution=0.01,
                 orient=tk.HORIZONTAL, bg=C.COLOR_SIDEBAR,
                 fg=C.COLOR_TEXT, troughcolor=C.COLOR_BUTTON,
                 highlightthickness=0, sliderrelief=tk.FLAT,
                 font=("Consolas", 8)
                 ).pack(fill=tk.X, padx=10)

        self._btn("Generate Random Map", self._cb.get("random_map"))

    
    def _algo_settings(self):
        self._lbl("Algorithm:")
        self.algo_var = tk.StringVar(value="A*")
        ttk.Combobox(
            self, textvariable=self.algo_var,
            values=list(Planner.ALGORITHMS.keys()),
            state="readonly", font=("Verdana", 9,"bold"),
        ).pack(fill=tk.X, padx=10, pady=2)

        self._lbl("Heuristic:")
        self.heuristic_var = tk.StringVar(value="Manhattan")
        ttk.Combobox(
            self, textvariable=self.heuristic_var,
            values=list(HEURISTICS.keys()),
            state="readonly", font=("Verdana", 9,"bold"),
        ).pack(fill=tk.X, padx=10, pady=2)

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Dynamic Mode",
            variable=self.dynamic_var,
            bg=C.COLOR_SIDEBAR, fg=C.COLOR_TEXT,
            selectcolor=C.COLOR_BUTTON,
            activebackground=C.COLOR_SIDEBAR,
            font=("Verdana", 9,"bold"),
        ).pack(anchor="w", padx=10, pady=4)

    
    def _action_buttons(self):
        self._btn("▶  Start Search",  self._cb.get("start"),      "#064700")
        self._btn("⟳  Clear Path",    self._cb.get("clear_path"), "#BDBD00")
        self._btn("✕  Reset Grid",    self._cb.get("reset_grid"), "#540018")

    @property
    def rows(self) -> int:
        try:
            val = int(self.rows_var.get())
            if val > 50:
                tk.messagebox.showwarning("Limit Exceeded", "Maximum 50 rows allowed for performance.")
                self.rows_var.set("50")
                return 50
            return max(3, val)
        except:
            return C.DEFAULT_ROWS

    @property
    def cols(self) -> int:
        try:
            val = int(self.cols_var.get())
            if val > 50:
                tk.messagebox.showwarning("Limit Exceeded", "Maximum 50 columns allowed for performance.")
                self.cols_var.set("50")
                return 50
            return max(3, val)
        except:
            return C.DEFAULT_COLS

    @property
    def density(self) -> float:
        return self.density_var.get()

    @property
    def algorithm(self) -> str:
        return self.algo_var.get()

    @property
    def heuristic_name(self) -> str:
        return self.heuristic_var.get()

    @property
    def dynamic_mode(self) -> bool:
        return self.dynamic_var.get()
