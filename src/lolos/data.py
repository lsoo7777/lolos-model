"""Market data loading with a local CSV cache."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_CACHE_DIR = Path("data/cache")

# Bars per year for each yfinance interval, assuming a 6.5h US trading session.
PERIODS_PER_YEAR = {
    "1m": 252 * 390,
    "2m": 252 * 195,
    "5m": 252 * 78,
    "15m": 252 * 26,
    "30m": 252 * 13,
    "60m": 252 * 7,
    "1h": 252 * 7,
    "1d": 252,
    "1wk": 52,
    "1mo": 12,
}

INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "1h"}

COLUMNS = ["open", "high", "low", "close", "volume"]


def periods_per_year(interval: str) -> int:
    try:
        return PERIODS_PER_YEAR[interval]
    except KeyError:
        raise ValueError(f"Unsupported interval {interval!r}") from None


def load_prices(
    symbol: str,
    start: str | None = None,
    end: str | None = None,
    interval: str = "1d",
    cache_dir: Path | None = DEFAULT_CACHE_DIR,
    refresh: bool = False,
) -> pd.DataFrame:
    """Return split/dividend-adjusted OHLCV bars with lowercase columns.

    Yahoo only serves limited intraday history (1m: ~7 days, <1h: ~60 days),
    so `start` is ignored by yfinance for very old intraday requests.
    """
    cache_file = None
    if cache_dir is not None:
        cache_file = Path(cache_dir) / f"{symbol}_{interval}_{start}_{end}.csv"
        if cache_file.exists() and not refresh:
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)

    import yfinance as yf

    raw = yf.download(
        symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    if raw.empty:
        raise ValueError(
            f"No data returned for {symbol} ({interval}, {start}..{end}). Check the symbol, "
            "the intraday history limits, and that query1/query2.finance.yahoo.com are reachable."
        )

    df = normalize_ohlcv(raw)
    if cache_file is not None:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file)
    return df


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load OHLCV bars from a CSV whose first column is the timestamp."""
    return normalize_ohlcv(pd.read_csv(path, index_col=0, parse_dates=True))


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    """Flatten yfinance's (field, ticker) columns and keep standard OHLCV fields."""
    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    df = df[COLUMNS].dropna(subset=["close"])
    df.index.name = "timestamp"
    return df.sort_index()
