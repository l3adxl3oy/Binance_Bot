# Data Cache Directory

This directory stores downloaded historical data from Binance.

Files are automatically created when running backtests with `use_cache=True`.

Format: `{symbol}_{interval}_{start_date}_{end_date}.csv`

Example: `BTCUSDT_1m_20250101_20250131.csv`
