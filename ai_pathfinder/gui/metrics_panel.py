# ─── gui/metrics_panel.py ────────────────────────────────────────────────────
"""Bottom metrics bar showing live search statistics."""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import config as C


class MetricsPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C.COLOR_SIDEBAR, **kwargs)

        label_cfg = dict(bg=C.COLOR_SIDEBAR, fg=C.COLOR_TEXT,
                         font=("Consolas", 10))
        val_cfg   = dict(bg=C.COLOR_SIDEBAR, fg=C.COLOR_ACCENT,
                         font=("Consolas", 11, "bold"))

        def _pair(label_text):
            f  = tk.Frame(self, bg=C.COLOR_SIDEBAR, padx=18, pady=4)
            lbl = tk.Label(f, text=label_text, **label_cfg)
            lbl.pack(side=tk.LEFT)
            val = tk.Label(f, text="—", width=10, anchor="w", **val_cfg)
            val.pack(side=tk.LEFT)
            f.pack(side=tk.LEFT)
            return val

        tk.Label(self, text=" METRICS ", bg=C.COLOR_ACCENT,
                 fg=C.COLOR_SIDEBAR, font=("Consolas", 10, "bold"),
                 padx=8, pady=4).pack(side=tk.LEFT, padx=(0, 8))

        self._nodes  = _pair("Nodes Visited:")
        self._cost   = _pair("Path Cost:")
        self._time   = _pair("Time (ms):")
        self._replan = _pair("Re-plans:")
        self._status = _pair("Status:")

    def update(self, *, nodes=None, cost=None, time_ms=None,
               replan=None, status=None):
        if nodes   is not None: self._nodes ["text"]  = str(nodes)
        if cost    is not None: self._cost  ["text"]  = str(cost)
        if time_ms is not None: self._time  ["text"]  = f"{time_ms:.1f}"
        if replan  is not None: self._replan["text"]  = str(replan)
        if status  is not None: self._status["text"]  = status

    def reset(self):
        for w in (self._nodes, self._cost, self._time, self._replan):
            w.config(text="—")
        self._status.config(text="Ready")

    # Allow dict-style access used in update() shorthand above
    def __getitem__(self, key):
        return self.__dict__.get(f"_{key}")
