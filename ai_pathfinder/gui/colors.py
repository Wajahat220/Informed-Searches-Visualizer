# ─── gui/colors.py ───────────────────────────────────────────────────────────
"""Map Node states → canvas fill colours."""
from core.node import Node
import config as C

STATE_COLORS: dict[str, str] = {
    Node.EMPTY:    C.COLOR_CELL,
    Node.WALL:     C.COLOR_WALL,
    Node.START:    C.COLOR_START,
    Node.GOAL:     C.COLOR_GOAL,
    Node.FRONTIER: C.COLOR_FRONTIER,
    Node.VISITED:  C.COLOR_VISITED,
    Node.PATH:     C.COLOR_PATH,
    Node.AGENT:    C.COLOR_AGENT,
}


def color_for(state: str) -> str:
    return STATE_COLORS.get(state, C.COLOR_CELL)
