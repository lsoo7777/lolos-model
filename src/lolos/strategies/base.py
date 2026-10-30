from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """A strategy maps OHLCV bars to a target position per bar.

    Positions are in [-1, 1] (fraction of capital, negative = short). The value
    at bar t may only use information available at bar t's close.
    """

    name: str = "strategy"

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series: ...

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{type(self).__name__}({params})"
