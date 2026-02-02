# Backtest Results Directory

This directory stores backtest results in JSON format.

Files are automatically created when running backtests.

Format: `backtest_YYYYMMDD_HHMMSS.json`

Each file contains:
- Configuration (symbols, dates, balance)
- Metrics (all performance statistics)
- Trades (list of all executed trades)
- Equity curve data
