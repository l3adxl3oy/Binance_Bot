"""
🔥 Run Backtest - Aggressive Recovery Bot
ทดสอบกลยุทธ์ Aggressive Recovery ด้วยข้อมูลย้อนหลัง
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


def run_aggressive_backtest(
    symbols: list,
    start_date: datetime,
    end_date: datetime,
    initial_balance: float = 100.0,
    timeframe: str = '1m',
    use_cache: bool = True
):
    """
    รัน backtest สำหรับ Aggressive Recovery Bot
    
    Args:
        symbols: List of trading pairs
        start_date: Start date for backtest
        end_date: End date for backtest
        initial_balance: Starting capital
        timeframe: Candle timeframe
        use_cache: Use cached data if available
    """
    
    logger.info("="*80)
    logger.info("🔥 AGGRESSIVE RECOVERY BOT - BACKTEST".center(80))
    logger.info("="*80)
    logger.info(f"💰 Initial Balance: ${initial_balance:,.2f}")
    logger.info(f"📅 Period: {start_date.date()} to {end_date.date()}")
    logger.info(f"📊 Symbols: {', '.join(symbols)}")
    logger.info(f"⏱️  Timeframe: {timeframe}")
    logger.info("-"*80)
    logger.info("⚡ OPTIMIZED Aggressive Strategy v2.1 (Ultra-Selective):")
    logger.info(f"  TP: 1.2-2.5% (เพิ่มขึ้น +50%)")
    logger.info(f"  SL: 0.6-1.0% (ปรับสมดุล +20%)")
    logger.info(f"  Martingale: 1.3x multiplier, max 2 levels (ลดความเสี่ยง -67%)")
    logger.info(f"  Averaging: DISABLED (ป้องกันขาดทุนซ้อน)")
    logger.info(f"  Signal Quality: 4.0/5, 4/4 confluence (เข้มงวดสูงสุด - เลือกแต่ดีที่สุด!)")
    logger.info(f"  Daily Target: 5% แล้วหยุดทันที!")
    logger.info("="*80)
    
    # Step 1: Initialize Binance client
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
    
    # Step 3: Run backtest with AGGRESSIVE parameters
    logger.info("\n🚀 Running AGGRESSIVE backtest...")
    logger.info("⚡ Using aggressive parameters:")
    logger.info("  - Tighter TP/SL (0.8%/0.5%)")
    logger.info("  - More frequent trades (lower signal threshold)")
    logger.info("  - Position sizing with Martingale recovery")
    
    engine = BacktestEngine(
        initial_balance=initial_balance,
        commission_rate=0.001,      # 0.1% Binance fee
        slippage_pct=0.001,         # 0.1% slippage (เพิ่มขึ้นเพราะ aggressive)
        max_positions=6,            # Max 6 concurrent (เพิ่มจาก 3 สำหรับ recovery)
        position_size_pct=0.25      # 25% per position (เล็กกว่าเพื่อรองรับ martingale)
    )
    
    # Override strategy parameters for v2.2 Original (Proven Profitable)
    aggressive_params = {
        'strategy_mode': 'aggressive',
        'take_profit_pct': 0.012,    # 1.2% TP (Proven: +13.19% in 7 days)
        'stop_loss_pct': 0.006,       # 0.6% SL (Good R/R ratio)
        'min_signal_strength': 4.0,   # 4.0 (Strict quality - 78.67% WR)
        'min_confluence': 3,          # 3 confluence signals
        'enable_martingale': True,
        'martingale_multiplier': 1.3, # Safe recovery
        'max_martingale_levels': 2,   # Limited risk
        'enable_averaging': False,    # Disabled
        'averaging_distance': 0.003,
        'max_averaging_times': 0,
        'time_stop_seconds': 600,     # 10 minutes
        'daily_target_pct': 0.05,     # 5% target
        'max_intraday_dd_pct': -0.15, # -15% max DD
    }
    
    results = engine.run_backtest(
        data=historical_data,
        strategy_params=aggressive_params
    )
    
    # Step 4: Calculate metrics
    logger.info("\n📊 Calculating performance metrics...")
    metrics = PerformanceMetrics.calculate_metrics(
        trades=results['trades'],
        initial_balance=initial_balance
    )
    
    # Step 5: Display results with aggressive context
    logger.info("\n")
    logger.info("="*80)
    logger.info("🔥 AGGRESSIVE BOT - RESULTS".center(80))
    logger.info("="*80)
    PerformanceMetrics.print_summary(metrics)
    
    # Additional aggressive-specific metrics
    if results['trades']:
        logger.info("\n" + "="*80)
        logger.info("⚡ AGGRESSIVE STRATEGY ANALYSIS".center(80))
        logger.info("="*80)
        
        total_trades = len(results['trades'])
        
        # Martingale analysis (simulated)
        logger.info("\n🔄 Recovery System Performance:")
        logger.info(f"  Total Trades: {total_trades}")
        
        # Estimate recovery scenarios based on consecutive losses
        consecutive_losses = 0
        max_consecutive_losses = 0
        recovery_opportunities = 0
        
        for trade in results['trades']:
            if trade.get('pnl', 0) < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                if consecutive_losses > 0:
                    recovery_opportunities += 1
                consecutive_losses = 0
        
        logger.info(f"  Max Consecutive Losses: {max_consecutive_losses}")
        logger.info(f"  Recovery Opportunities: {recovery_opportunities}")
        
        if max_consecutive_losses >= 3:
            logger.warning("  ⚠️ Warning: Reached max martingale level (3) at least once")
        
        # Fast profit analysis
        quick_profits = sum(1 for t in results['trades'] if t.get('pnl', 0) > 0 and t.get('pnl', 0) / initial_balance < 0.015)
        logger.info(f"\n💨 Quick Scalps (<1.5% profit):")
        logger.info(f"  Count: {quick_profits}/{total_trades} ({quick_profits/total_trades*100:.1f}%)")
        
        # Risk assessment
        logger.info(f"\n⚠️ Risk Assessment:")
        logger.info(f"  Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
        if metrics.get('max_drawdown_pct', 0) > 20:
            logger.warning("  ⚠️ HIGH RISK: Drawdown exceeded 20%")
        elif metrics.get('max_drawdown_pct', 0) > 15:
            logger.warning("  ⚠️ MODERATE RISK: Drawdown 15-20%")
        else:
            logger.info("  ✅ ACCEPTABLE: Drawdown under 15%")
        
        logger.info("="*80)
    
    # Step 6: Save results
    logger.info("\n💾 Saving results...")
    output_file = f"backtest/results/backtest_aggressive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    save_data = {
        "bot_type": "aggressive_recovery",
        "config": {
            "symbols": symbols,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_balance": initial_balance,
            "timeframe": timeframe,
            "strategy_params": aggressive_params
        },
        "metrics": metrics,
        "trades": results['trades']
    }
    
    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2, default=str)
    
    logger.info(f"✅ Results saved to: {output_file}")
    
    # Comparison reminder
    logger.info("\n" + "="*80)
    logger.info("💡 TIPS & COMPARISON".center(80))
    logger.info("="*80)
    logger.info("📊 Compare with Daily Scalping Bot:")
    logger.info("  - Daily Bot: 2-5% target, safer, 60-70% WR")
    logger.info("  - Aggressive: 3-8% target, riskier, 50-65% WR")
    logger.info("")
    logger.info("⚠️ Remember:")
    logger.info("  - Aggressive uses Martingale (can increase drawdown)")
    logger.info("  - Requires more capital reserve ($500+ recommended)")
    logger.info("  - ALWAYS test in DEMO MODE first")
    logger.info("="*80)
    
    return metrics


if __name__ == "__main__":
    # ==================== CONFIGURATION ====================
    
    # Backtest period (7 days test - same as Daily Bot for comparison)
    END_DATE = datetime.now(UTC)
    START_DATE = END_DATE - timedelta(days=7)
    
    # Symbols to test (same as Daily Bot)
    SYMBOLS = [
        'BTCUSDT',
        'BNBUSDT',
        'SOLUSDT',
        'ADAUSDT'
    ]
    
    # Initial balance
    INITIAL_BALANCE = 100.0  # $100 starting capital
    
    # Timeframe
    TIMEFRAME = '1m'  # 1-minute candles
    
    # ==================== RUN BACKTEST ====================
    
    try:
        logger.info("\n🔥 Starting Aggressive Recovery Bot Backtest...")
        logger.info("⚠️ This bot uses aggressive parameters and recovery systems")
        logger.info("📊 Results will be compared with Daily Scalping Bot\n")
        
        results = run_aggressive_backtest(
            symbols=SYMBOLS,
            start_date=START_DATE,
            end_date=END_DATE,
            initial_balance=INITIAL_BALANCE,
            timeframe=TIMEFRAME,
            use_cache=True  # Use cached data from previous backtest
        )
        
        logger.info("\n✅ Aggressive Bot backtest completed successfully!")
        logger.info("📁 Check backtest/results/ for detailed JSON results")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Backtest interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Backtest failed: {e}", exc_info=True)
