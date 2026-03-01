# ─── utils/timer.py ──────────────────────────────────────────────────────────
import time


class Timer:
    """Simple wall-clock timer."""
    def __init__(self):
        self._start = 0.0

    def start(self):
        self._start = time.time()

    def elapsed_ms(self) -> float:
        return (time.time() - self._start) * 1000
