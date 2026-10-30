# lolos-model

Research and backtesting toolkit for stock trading strategies, covering both
**long-term** (daily/weekly trend and momentum) and **day trading** (intraday
mean reversion, flat by the close).

> Research only. Nothing here places real orders or is financial advice.
> Backtests overstate real-world results: expect slippage, fills, and regime change.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
# Long-term: 50/200-day SMA crossover vs buy-and-hold
lolos backtest SPY --strategy sma

# Tune parameters
lolos backtest QQQ --strategy sma --param fast=20 --param slow=100 --start 2015-01-01

# 12-1 time-series momentum
lolos backtest AAPL --strategy momentum

# Day trading: RSI mean reversion on 15-minute bars, flattened every evening
lolos backtest SPY --strategy rsi --interval 15m --param entry=25 --param exit=50

# Use your own data instead of Yahoo Finance
lolos backtest SPY --csv path/to/bars.csv --strategy rsi
```

Data comes from Yahoo Finance via `yfinance` and is cached in `data/cache/`.
Yahoo only serves ~60 days of sub-hourly bars (~7 days of 1-minute bars).

## Layout

```
src/lolos/
  data.py            # price loading (yfinance + CSV) and cache
  features.py        # indicators: SMA, EMA, RSI, ATR, volatility
  strategies/        # Strategy base class + implementations, REGISTRY for the CLI
    trend.py         #   long-term: BuyAndHold, SmaCrossover, Momentum
    mean_reversion.py#   short-term: RsiReversion
  backtest.py        # vectorized backtester (next-bar execution, costs, flat-EOD)
  metrics.py         # CAGR, Sharpe, Sortino, max drawdown, exposure, trades
  cli.py             # `lolos` command
tests/               # offline tests on synthetic data
```

## Adding a strategy

Subclass `Strategy`, return a target position in `[-1, 1]` per bar using only
data up to that bar's close, and register it in `strategies/__init__.py`.

## Roadmap

- [ ] Walk-forward / out-of-sample parameter testing
- [ ] Multi-asset portfolio backtests and position sizing (vol targeting, ATR stops)
- [ ] ML signal model (features → next-period return classifier)
- [ ] Paper trading via a broker API (e.g. Alpaca)
