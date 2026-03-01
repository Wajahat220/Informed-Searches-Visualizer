# ─── main.py ─────────────────────────────────────────────────────────────────
"""
Entry point for AI Pathfinder.

Run with:
    python main.py
"""

import tkinter as tk
from gui.window import AppWindow


def main():
    root = tk.Tk()
    root.minsize(900, 550)
    app  = AppWindow(root)   # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
