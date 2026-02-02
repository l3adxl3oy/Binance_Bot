"""
🧪 Walk-Forward Test - ทดสอบกลยุทธ์บนหลาย periods
วิเคราะห์ความสม่ำเสมอและ robustness ของ strategy
"""

import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta, UTC
import json
from typing import List, Dict

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


def run_single_period(
    symbols: list,
    start_date: datetime,
    end_date: datetime,
    initial_balance: float = 100.0,
    timeframe: str = '1m'
) -> Dict:
    """รัน backtest สำหรับ 1 period"""
    
    logger.info(f"📅 Testing period: {start_date.date()} to {end_date.date()}")
    
    # Initialize client
    client = Spot(
        api_key=Config.API_KEY,
        api_secret=Config.API_SECRET,
        base_url=Config.BASE_URL
    )
    
    # Load data
    data_loader = HistoricalDataLoader(client=client)
    historical_data = data_loader.prepare_multiple_symbols(
        symbols=symbols,
        interval=timeframe,
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    if not historical_data:
        logger.error("❌ No data loaded")
        return None
    
    # Run backtest
    engine = BacktestEngine(
        initial_balance=initial_balance,
        commission_rate=0.001,
        slippage_pct=0.0005,
        max_positions=3,
        position_size_pct=0.33
    )
    
    results = engine.run_backtest(
        data=historical_data,
        strategy_params=None
    )
    
    # Calculate metrics
    metrics = PerformanceMetrics.calculate_metrics(
        trades=results['trades'],
        initial_balance=initial_balance
    )
    
    return {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'metrics': metrics,
        'trades': results['trades']
    }


def run_walk_forward_test(
    symbols: list,
    period_days: int = 7,
    num_periods: int = 4,
    initial_balance: float = 100.0
):
    """
    รัน Walk-Forward Test หลาย periods
    
    Args:
        symbols: Trading pairs
        period_days: จำนวนวันต่อ period
        num_periods: จำนวน periods ที่จะทดสอบ
        initial_balance: เงินทุนเริ่มต้น
    """
    
    logger.info("="*80)
    logger.info("🧪 WALK-FORWARD TEST".center(80))
    logger.info("="*80)
    logger.info(f"💰 Initial Balance: ${initial_balance:,.2f}")
    logger.info(f"📊 Symbols: {', '.join(symbols)}")
    logger.info(f"📅 Period Length: {period_days} days")
    logger.info(f"🔢 Number of Periods: {num_periods}")
    logger.info("="*80)
    
    end_date = datetime.now(UTC)
    all_results = []
    
    # รันแต่ละ period
    for i in range(num_periods):
        period_end = end_date - timedelta(days=i * period_days)
        period_start = period_end - timedelta(days=period_days)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 Period {i+1}/{num_periods}")
        logger.info(f"{'='*80}")
        
        result = run_single_period(
            symbols=symbols,
            start_date=period_start,
            end_date=period_end,
            initial_balance=initial_balance
        )
        
        if result:
            all_results.append(result)
            
            # แสดงผลสรุป
            metrics = result['metrics']
            logger.info(f"\n📊 Period {i+1} Results:")
            logger.info(f"  Return: {metrics['total_return_pct']:+.2f}%")
            logger.info(f"  Trades: {metrics['total_trades']}")
            logger.info(f"  Win Rate: {metrics['win_rate']:.1f}%")
            logger.info(f"  Profit Factor: {metrics['profit_factor']:.2f}")
            logger.info(f"  Max DD: {metrics['max_drawdown_pct']:.2f}%")
    
    # วิเคราะห์รวม
    logger.info(f"\n{'='*80}")
    logger.info("📊 WALK-FORWARD ANALYSIS".center(80))
    logger.info(f"{'='*80}")
    
    if all_results:
        returns = [r['metrics']['total_return_pct'] for r in all_results]
        win_rates = [r['metrics']['win_rate'] for r in all_results]
        profit_factors = [r['metrics']['profit_factor'] for r in all_results]
        max_dds = [r['metrics']['max_drawdown_pct'] for r in all_results]
        
        logger.info(f"\n📈 Return Statistics:")
        logger.info(f"  Average: {sum(returns)/len(returns):+.2f}%")
        logger.info(f"  Best: {max(returns):+.2f}%")
        logger.info(f"  Worst: {min(returns):+.2f}%")
        logger.info(f"  Std Dev: {(sum((x - sum(returns)/len(returns))**2 for x in returns) / len(returns))**0.5:.2f}%")
        
        logger.info(f"\n🎯 Win Rate Statistics:")
        logger.info(f"  Average: {sum(win_rates)/len(win_rates):.1f}%")
        logger.info(f"  Best: {max(win_rates):.1f}%")
        logger.info(f"  Worst: {min(win_rates):.1f}%")
        
        logger.info(f"\n💪 Profit Factor Statistics:")
        logger.info(f"  Average: {sum(profit_factors)/len(profit_factors):.2f}")
        logger.info(f"  Best: {max(profit_factors):.2f}")
        logger.info(f"  Worst: {min(profit_factors):.2f}")
        
        logger.info(f"\n🛡️ Max Drawdown Statistics:")
        logger.info(f"  Average: {sum(max_dds)/len(max_dds):.2f}%")
        logger.info(f"  Best (smallest): {max(max_dds):.2f}%")
        logger.info(f"  Worst (largest): {min(max_dds):.2f}%")
        
        # Consistency check
        positive_periods = sum(1 for r in returns if r > 0)
        consistency = (positive_periods / len(returns)) * 100
        
        logger.info(f"\n✅ Consistency:")
        logger.info(f"  Profitable Periods: {positive_periods}/{len(returns)} ({consistency:.1f}%)")
        
        if consistency >= 75:
            logger.info(f"  🌟 Excellent consistency!")
        elif consistency >= 60:
            logger.info(f"  ✅ Good consistency")
        elif consistency >= 50:
            logger.info(f"  ⚠️ Moderate consistency")
        else:
            logger.info(f"  ❌ Poor consistency - strategy may not be robust")
    
    # บันทึกผลลัพธ์
    output_file = f"backtest/results/walkforward_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'test_date': datetime.now(UTC).isoformat(),
            'config': {
                'symbols': symbols,
                'period_days': period_days,
                'num_periods': num_periods,
                'initial_balance': initial_balance
            },
            'results': all_results
        }, f, indent=2, default=str)
    
    logger.info(f"\n💾 Results saved to: {output_file}")
    logger.info(f"\n{'='*80}")
    
    return all_results


if __name__ == "__main__":
    # ==================== CONFIGURATION ====================
    
    # Symbols (optimized set)
    SYMBOLS = [
        'BTCUSDT',   # Best performer
        'BNBUSDT',   # High profit potential
        'SOLUSDT',   # Good consistency
        'ADAUSDT'    # Stable
    ]
    
    # Test parameters
    PERIOD_DAYS = 7      # ทดสอบทีละ 7 วัน
    NUM_PERIODS = 4      # ทดสอบ 4 periods (28 วันรวม)
    INITIAL_BALANCE = 100.0
    
    # ==================== RUN TEST ====================
    
    try:
        results = run_walk_forward_test(
            symbols=SYMBOLS,
            period_days=PERIOD_DAYS,
            num_periods=NUM_PERIODS,
            initial_balance=INITIAL_BALANCE
        )
        
        logger.info("\n✅ Walk-Forward Test completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
