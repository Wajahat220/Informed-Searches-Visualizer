# ─── config.py ───────────────────────────────────────────────────────────────
# Central place for every "magic number" in the project.
# Change values here and the whole app adapts.

# ── Grid defaults ──────────────────────────────────────────────────────────
DEFAULT_ROWS = 20
DEFAULT_COLS = 30
CELL_SIZE    = 28          # pixels per cell

# ── Animation delays (ms) ─────────────────────────────────────────────────
SEARCH_DELAY = 30          # delay between each search step
MOVE_DELAY   = 150         # delay between agent movement steps

# ── Dynamic mode ──────────────────────────────────────────────────────────
SPAWN_PROBABILITY = 0.12   # chance per step of spawning a new obstacle

# ── Colors ────────────────────────────────────────────────────────────────
COLOR_BG       = "#1e1e2e"
COLOR_CELL     = "#313244"
COLOR_GRID_LINE= "#45475a"
COLOR_START    = "#40b556"   # dark green
COLOR_GOAL     = "#89b4fa"   # blue
COLOR_WALL     = "#11111b"   # near-black
COLOR_FRONTIER = "#f9e2af"   # yellow
COLOR_VISITED  = "#f38ba8"   # red
COLOR_PATH     = "#a6e3a1"   # bright green
COLOR_AGENT    = "#fab387"   # orange
COLOR_TEXT     = "#cdd6f4"
COLOR_SIDEBAR  = "#181825"
COLOR_BUTTON   = "#313244"
COLOR_BTN_ACT  = "#45475a"
COLOR_ACCENT   = "#cba6f7"
