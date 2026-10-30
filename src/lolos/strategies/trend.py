"""Long-term trend-following strategies (daily/weekly bars)."""

from __future__ import annotations

import pandas as pd

from lolos.features import sma
from lolos.strategies.base import Strategy


class BuyAndHold(Strategy):
    name = "buy_hold"

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(1.0, index=df.index)


class SmaCrossover(Strategy):
    """Long while the fast SMA is above the slow SMA, flat otherwise."""

    name = "sma"

    def __init__(self, fast: int = 50, slow: int = 200):
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast = sma(df["close"], self.fast)
        slow = sma(df["close"], self.slow)
        return (fast > slow).astype(float)


class Momentum(Strategy):
    """Time-series momentum: long when the trailing return (skipping the most
    recent `skip` bars, which tend to mean-revert) is positive."""

    name = "momentum"

    def __init__(self, lookback: int = 252, skip: int = 21):
        self.lookback = lookback
        self.skip = skip

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        trailing = close.shift(self.skip) / close.shift(self.lookback) - 1
        return (trailing > 0).astype(float)
