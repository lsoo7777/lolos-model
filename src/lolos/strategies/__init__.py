from lolos.strategies.base import Strategy
from lolos.strategies.mean_reversion import RsiReversion
from lolos.strategies.trend import BuyAndHold, Momentum, SmaCrossover

REGISTRY: dict[str, type[Strategy]] = {
    cls.name: cls for cls in (BuyAndHold, SmaCrossover, Momentum, RsiReversion)
}

__all__ = ["REGISTRY", "BuyAndHold", "Momentum", "RsiReversion", "SmaCrossover", "Strategy"]
