"""Short-term mean-reversion strategies (intraday or daily bars)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from lolos.features import rsi
from lolos.strategies.base import Strategy


class RsiReversion(Strategy):
    """Buy oversold dips: enter long when RSI < `entry`, exit when RSI > `exit`."""

    name = "rsi"

    def __init__(self, window: int = 14, entry: float = 30, exit: float = 55):
        if entry >= exit:
            raise ValueError("entry threshold must be below exit threshold")
        self.window = window
        self.entry = entry
        self.exit = exit

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        r = rsi(df["close"], self.window)
        state = pd.Series(np.nan, index=df.index)
        state[r < self.entry] = 1.0
        state[r > self.exit] = 0.0
        return state.ffill().fillna(0.0)
