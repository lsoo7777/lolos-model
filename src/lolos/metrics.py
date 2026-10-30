"""Performance statistics for a series of per-bar strategy returns."""

from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough decline, as a negative fraction."""
    peak = equity.cummax()
    return float((equity / peak - 1).min())


def summarize(
    returns: pd.Series,
    positions: pd.Series,
    periods_per_year: int,
) -> dict[str, float | int]:
    equity = (1 + returns).cumprod()
    n = len(returns)
    years = n / periods_per_year if n else 0.0
    total_return = float(equity.iloc[-1] - 1) if n else 0.0
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 and total_return > -1 else np.nan

    std = returns.std()
    sharpe = returns.mean() / std * np.sqrt(periods_per_year) if std > 0 else np.nan
    downside = returns[returns < 0].std()
    sortino = returns.mean() / downside * np.sqrt(periods_per_year) if downside > 0 else np.nan

    in_market = positions != 0
    entries = in_market & ~in_market.shift(1, fill_value=False)

    return {
        "total_return": total_return,
        "cagr": float(cagr),
        "annual_vol": float(std * np.sqrt(periods_per_year)),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": max_drawdown(equity) if n else 0.0,
        "exposure": float(in_market.mean()) if n else 0.0,
        "trades": int(entries.sum()),
    }
