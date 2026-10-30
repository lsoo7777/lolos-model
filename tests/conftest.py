import numpy as np
import pandas as pd
import pytest


def make_ohlcv(close: np.ndarray, index: pd.DatetimeIndex) -> pd.DataFrame:
    close = pd.Series(close, index=index)
    return pd.DataFrame(
        {
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": 1_000_000,
        }
    )


@pytest.fixture
def daily_prices() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    index = pd.bdate_range("2020-01-01", periods=600)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(index))))
    return make_ohlcv(close, index)


@pytest.fixture
def intraday_prices() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    days = pd.bdate_range("2024-01-02", periods=5)
    index = pd.DatetimeIndex(
        [d + pd.Timedelta(hours=9, minutes=30) + pd.Timedelta(minutes=15 * i)
         for d in days for i in range(26)]
    )
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, len(index))))
    return make_ohlcv(close, index)
