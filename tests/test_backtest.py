import numpy as np
import pandas as pd
import pytest

from lolos.backtest import run_backtest
from lolos.strategies import BuyAndHold


def test_buy_and_hold_matches_asset_return(daily_prices):
    # Signal at the first close -> held from bar 1 onward -> earns close[-1] / close[0].
    result = run_backtest(daily_prices, BuyAndHold().generate_signals(daily_prices), cost_bps=0)
    close = daily_prices["close"]
    assert result.metrics["total_return"] == pytest.approx(close.iloc[-1] / close.iloc[0] - 1)


def test_no_lookahead(daily_prices):
    # A "perfect foresight" signal that uses the same bar's return must not be
    # rewarded: it is executed one bar late.
    same_bar_up = (daily_prices["close"].pct_change() > 0).astype(float)
    result = run_backtest(daily_prices, same_bar_up, cost_bps=0)
    assert result.metrics["sharpe"] < 3


def test_future_leak_would_be_profitable(daily_prices):
    # Sanity check of the test above: actually peeking one bar ahead is wildly profitable.
    peek = (daily_prices["close"].pct_change().shift(-1) > 0).astype(float)
    result = run_backtest(daily_prices, peek, cost_bps=0)
    assert result.metrics["sharpe"] > 5


def test_costs_reduce_returns(daily_prices):
    flip = pd.Series(np.tile([1.0, 0.0], len(daily_prices) // 2), index=daily_prices.index)
    free = run_backtest(daily_prices, flip, cost_bps=0)
    costly = run_backtest(daily_prices, flip, cost_bps=10)
    assert costly.equity.iloc[-1] < free.equity.iloc[-1]


def test_flat_eod_never_holds_overnight(intraday_prices):
    result = run_backtest(
        intraday_prices, BuyAndHold().generate_signals(intraday_prices), flat_eod=True
    )
    first_bar_of_day = ~intraday_prices.index.normalize().duplicated()
    assert (result.positions[first_bar_of_day] == 0).all()
    assert result.metrics["trades"] == 5


def test_cli_runs_from_csv(daily_prices, tmp_path, capsys):
    from lolos.cli import main

    path = tmp_path / "bars.csv"
    daily_prices.rename(columns=str.capitalize).to_csv(path)
    main(["backtest", "TEST", "--csv", str(path), "--strategy", "sma", "--param", "fast=10",
          "--param", "slow=50"])
    out = capsys.readouterr().out
    assert "SmaCrossover(fast=10, slow=50)" in out
    assert "sharpe" in out
