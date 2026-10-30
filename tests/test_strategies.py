import numpy as np
import pandas as pd
import pytest

from lolos.strategies import REGISTRY, RsiReversion, SmaCrossover


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_signals_are_valid_positions(name, daily_prices):
    signals = REGISTRY[name]().generate_signals(daily_prices)
    assert signals.index.equals(daily_prices.index)
    assert signals.notna().all()
    assert signals.between(-1, 1).all()


def test_sma_crossover_follows_trend():
    index = pd.bdate_range("2020-01-01", periods=300)
    close = pd.Series(np.r_[np.linspace(100, 200, 150), np.linspace(200, 50, 150)], index=index)
    signals = SmaCrossover(fast=10, slow=30).generate_signals(pd.DataFrame({"close": close}))
    assert signals.iloc[100] == 1.0
    assert signals.iloc[-1] == 0.0


def test_rsi_reversion_holds_until_exit():
    index = pd.bdate_range("2020-01-01", periods=80)
    close = pd.Series(np.r_[np.full(20, 100.0), np.linspace(100, 70, 30), np.linspace(70, 110, 30)],
                      index=index)
    signals = RsiReversion().generate_signals(pd.DataFrame({"close": close}))
    assert signals.iloc[45] == 1.0  # oversold during the selloff
    assert signals.iloc[-1] == 0.0  # exited on the rebound


def test_invalid_params_rejected():
    with pytest.raises(ValueError):
        SmaCrossover(fast=200, slow=50)
