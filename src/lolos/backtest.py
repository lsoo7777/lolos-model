"""Vectorized single-asset backtester.

Timing convention: a strategy's signal at bar t is computed from data up to
and including bar t's close, and is held over bar t+1. This avoids lookahead.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from lolos.metrics import summarize


@dataclass
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    positions: pd.Series
    metrics: dict[str, float | int]


def flatten_end_of_day(signals: pd.Series) -> pd.Series:
    """Force the signal flat on the last bar of each session (no overnight risk)."""
    dates = signals.index.normalize()
    last_bar = dates != pd.Series(dates, index=signals.index).shift(-1)
    return signals.where(~last_bar, 0.0)


def run_backtest(
    prices: pd.DataFrame,
    signals: pd.Series,
    periods_per_year: int = 252,
    cost_bps: float = 1.0,
    initial_capital: float = 10_000.0,
    flat_eod: bool = False,
) -> BacktestResult:
    """Simulate holding `signals` (target position in [-1, 1]) on `prices['close']`.

    `cost_bps` is charged on traded notional, i.e. per unit change in position.
    """
    signals = signals.reindex(prices.index).fillna(0.0).clip(-1, 1)
    if flat_eod:
        signals = flatten_end_of_day(signals)

    positions = signals.shift(1).fillna(0.0)
    asset_returns = prices["close"].pct_change().fillna(0.0)
    turnover = positions.diff().abs().fillna(positions.abs())
    returns = positions * asset_returns - turnover * cost_bps / 10_000

    equity = initial_capital * (1 + returns).cumprod()
    metrics = summarize(returns, positions, periods_per_year)
    return BacktestResult(equity=equity, returns=returns, positions=positions, metrics=metrics)
