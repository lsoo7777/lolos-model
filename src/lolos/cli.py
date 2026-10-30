"""Command-line entry point: `lolos backtest SPY --strategy sma`."""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from lolos.backtest import run_backtest
from lolos.data import INTRADAY_INTERVALS, load_csv, load_prices, periods_per_year
from lolos.strategies import REGISTRY, BuyAndHold


def _parse_params(pairs: list[str]) -> dict[str, float | int]:
    params: dict[str, float | int] = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        if not value:
            raise SystemExit(f"--param expects key=value, got {pair!r}")
        params[key] = float(value) if "." in value else int(value)
    return params


def _format(metrics: dict[str, float | int]) -> dict[str, str]:
    pct = {"total_return", "cagr", "annual_vol", "max_drawdown", "exposure"}
    return {
        k: f"{v:.2%}" if k in pct else str(v) if isinstance(v, int) else f"{v:.2f}"
        for k, v in metrics.items()
    }


def _default_start(interval: str) -> str:
    # Yahoo serves only ~60 days of sub-daily bars (~7 days for 1m).
    if interval == "1m":
        return str(date.today() - timedelta(days=6))
    if interval in INTRADAY_INTERVALS:
        return str(date.today() - timedelta(days=59))
    return "2010-01-01"


def cmd_backtest(args: argparse.Namespace) -> None:
    if args.csv:
        prices = load_csv(args.csv).loc[args.start : args.end]
    else:
        start = args.start or _default_start(args.interval)
        prices = load_prices(args.symbol, start, args.end, args.interval, refresh=args.refresh)
    ppy = periods_per_year(args.interval)
    flat_eod = args.interval in INTRADAY_INTERVALS and not args.hold_overnight

    strategy = REGISTRY[args.strategy](**_parse_params(args.param))
    results = {
        repr(strategy): run_backtest(
            prices, strategy.generate_signals(prices), ppy, args.cost_bps, flat_eod=flat_eod
        ),
        "BuyAndHold": run_backtest(
            prices, BuyAndHold().generate_signals(prices), ppy, args.cost_bps
        ),
    }

    print(f"{args.symbol} {args.interval}: {prices.index[0]} -> {prices.index[-1]} "
          f"({len(prices)} bars, cost {args.cost_bps} bps, flat_eod={flat_eod})\n")
    rows = {name: _format(r.metrics) for name, r in results.items()}
    keys = list(next(iter(rows.values())))
    width = max(len(n) for n in rows) + 2
    print(" " * 14 + "".join(n.rjust(width) for n in rows))
    for key in keys:
        print(key.ljust(14) + "".join(rows[n][key].rjust(width) for n in rows))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="lolos")
    sub = parser.add_subparsers(dest="command", required=True)

    bt = sub.add_parser("backtest", help="Backtest a strategy against buy-and-hold")
    bt.add_argument("symbol")
    bt.add_argument("--strategy", choices=sorted(REGISTRY), default="sma")
    bt.add_argument("--param", action="append", default=[], help="strategy param, e.g. fast=20")
    bt.add_argument("--start", default=None, help="default: 2010 daily, ~60d intraday")
    bt.add_argument("--end", default=None)
    bt.add_argument("--interval", default="1d", help="1d, 1wk, 1h, 15m, 5m, ...")
    bt.add_argument("--cost-bps", type=float, default=1.0)
    bt.add_argument("--hold-overnight", action="store_true",
                    help="allow intraday strategies to hold positions overnight")
    bt.add_argument("--csv", help="load bars from a local OHLCV CSV instead of Yahoo")
    bt.add_argument("--refresh", action="store_true", help="ignore the local data cache")
    bt.set_defaults(func=cmd_backtest)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
