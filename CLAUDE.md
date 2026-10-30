# CLAUDE.md

Python package `lolos` (src layout) for backtesting stock strategies.

## Commands
- Install: `pip install -e ".[dev]"`
- Lint: `ruff check .`
- Test: `pytest -q`

## Rules
- **No lookahead.** A signal at bar t may use data through bar t's close only;
  `run_backtest` shifts signals one bar to execute them. Never use `shift(-n)`
  or centered windows in features or strategies.
- Strategies return a float Series of target positions in [-1, 1], indexed like the input.
- Tests must run offline: use the synthetic fixtures in `tests/conftest.py`, never the network.
- Always compare new strategies against `BuyAndHold` and include transaction costs.
- Do not add live order placement without an explicit request; paper trading first.
