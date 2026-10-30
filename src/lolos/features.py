"""Technical indicators. All functions use only past and current bars."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder's Relative Strength Index, in [0, 100]."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss
    out = 100 - 100 / (1 + rs)
    # No losses in the window means maximum strength.
    return out.where(avg_loss != 0, 100.0).where(avg_gain.notna())


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range."""
    prev_close = df["close"].shift(1)
    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()


def log_returns(close: pd.Series) -> pd.Series:
    return np.log(close).diff()


def rolling_volatility(close: pd.Series, window: int = 20) -> pd.Series:
    """Per-bar standard deviation of log returns (not annualized)."""
    return log_returns(close).rolling(window, min_periods=window).std()
