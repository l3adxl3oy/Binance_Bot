"""
🧪 Run Backtest - ทดสอบกลยุทธ์ด้วยข้อมูลย้อนหลัง
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta, UTC
import json

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from binance.spot import Spot
from backtest.data_loader import HistoricalDataLoader
from backtest.backtest_engine import BacktestEngine
from backtest.performance_metrics import PerformanceMetrics
from config.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def run_backtest(
    symbols: list,
    start_date: datetime,
    end_date: datetime,
    initial_balance: float = 100.0,
    timeframe: str = '1m',
    use_cache: bool = True
):
    """
    รัน backtest หลัก
    
    Args:
        symbols: List of trading pairs
        start_date: Start date for backtest
        end_date: End date for backtest
        initial_balance: Starting capital
        timeframe: Candle timeframe
        use_cache: Use cached data if available
    """
    
    logger.info("="*80)
    logger.info("🧪 BACKTEST SYSTEM".center(80))
    logger.info("="*80)
    logger.info(f"💰 Initial Balance: ${initial_balance:,.2f}")
    logger.info(f"📅 Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"📊 Symbols: {', '.join(symbols)}")
    logger.info(f"⏱️  Timeframe: {timeframe}")
    logger.info("="*80)
    
    # Step 1: Initialize Binance client (for downloading data)
    logger.info("\n📡 Connecting to Binance...")
    client = Spot(
        api_key=Config.API_KEY,
        api_secret=Config.API_SECRET,
        base_url=Config.BASE_URL
    )
    
    # Step 2: Load historical data
    logger.info("\n📥 Loading historical data...")
    data_loader = HistoricalDataLoader(client=client)
    
    historical_data = data_loader.prepare_multiple_symbols(
        symbols=symbols,
        interval=timeframe,
        start_date=start_date,
        end_date=end_date,
        use_cache=use_cache
    )
    
    if not historical_data:
        logger.error("❌ No data loaded. Exiting.")
        return
    
    # Print data info
    logger.info(f"\n✅ Loaded data for {len(historical_data)} symbols:")
    for symbol, df in historical_data.items():
        info = data_loader.get_data_info(df)
        logger.info(f"  {symbol}: {info['total_candles']} candles, "
                   f"${info['price_range']['min']:.2f} - ${info['price_range']['max']:.2f}")
    
    # Step 3: Run backtest
    logger.info("\n🚀 Running backtest...")
    engine = BacktestEngine(
        initial_balance=initial_balance,
        commission_rate=0.001,      # 0.1% Binance fee
        slippage_pct=0.0005,        # 0.05% slippage
        max_positions=3,            # Max 3 concurrent positions
        position_size_pct=0.33      # 33% per position
    )
    
    results = engine.run_backtest(
        data=historical_data,
        strategy_params=None
    )
    
    # Step 4: Calculate metrics
    logger.info("\n📊 Calculating performance metrics...")
    metrics = PerformanceMetrics.calculate_metrics(
        trades=results['trades'],
        initial_balance=initial_balance
    )
    
    # Step 5: Display results
    logger.info("\n")
    PerformanceMetrics.print_summary(metrics)
    
    # Step 6: Save results to file
    logger.info("\n💾 Saving results...")
    output_file = f"backtest/results/backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    save_data = {
        "config": {
            "symbols": symbols,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_balance": initial_balance,
            "timeframe": timeframe
        },
        "metrics": metrics,
        "trades": results['trades']
    }
    
    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2, default=str)
    
    logger.info(f"✅ Results saved to: {output_file}")
    
    return metrics


if __name__ == "__main__":
    # ==================== CONFIGURATION ====================
    
    # Backtest period (past 30 days for comprehensive test)
    END_DATE = datetime.now(UTC)
    START_DATE = END_DATE - timedelta(days=30)  # ขยายจาก 7 → 30 วัน
    
    # You can also specify exact dates:
    # START_DATE = datetime(2025, 1, 1, tzinfo=UTC)
    # END_DATE = datetime(2025, 1, 31, tzinfo=UTC)
    
    # Symbols to test (Optimized - removed ETHUSDT due to poor performance)
    SYMBOLS = [
        'BTCUSDT',   # Best: 68.75% WR
        # 'ETHUSDT', # ❌ REMOVED: -$18.65 total PnL
        'BNBUSDT',   # Explosive: +$10.25
        'SOLUSDT',   # Good: 63.16% WR
        'ADAUSDT'    # Stable: 68.42% WR
    ]
    
    # Initial balance
    INITIAL_BALANCE = 100.0  # $100 starting capital
    
    # Timeframe
    TIMEFRAME = '1m'  # 1-minute candles (same as bot)
    
    # ==================== RUN BACKTEST ====================
    
    try:
        results = run_backtest(
            symbols=SYMBOLS,
            start_date=START_DATE,
            end_date=END_DATE,
            initial_balance=INITIAL_BALANCE,
            timeframe=TIMEFRAME,
            use_cache=True  # Set False to force re-download
        )
        
        logger.info("\n✅ Backtest completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Backtest interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Backtest failed: {e}", exc_info=True)
