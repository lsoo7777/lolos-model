import numpy as np
import pandas as pd

from lolos.features import atr, rsi, sma


def test_sma_uses_only_past_data():
    s = pd.Series(np.arange(10, dtype=float))
    out = sma(s, 3)
    assert out.iloc[:2].isna().all()
    assert out.iloc[2] == 1.0
    assert out.iloc[-1] == 8.0


def test_rsi_bounds(daily_prices):
    r = rsi(daily_prices["close"]).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_rsi_monotonic_up_is_100():
    s = pd.Series(np.arange(1, 50, dtype=float))
    assert rsi(s).dropna().eq(100).all()


def test_atr_positive(daily_prices):
    assert (atr(daily_prices).dropna() > 0).all()
