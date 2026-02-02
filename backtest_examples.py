"""
🎯 Advanced Backtest Examples
ตัวอย่างการใช้งาน Backtest System แบบขั้นสูง
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from datetime import datetime, timedelta, UTC
from binance.spot import Spot

from backtest.data_loader import HistoricalDataLoader
from backtest.backtest_engine import BacktestEngine
from backtest.performance_metrics import PerformanceMetrics
from backtest.visualizer import BacktestVisualizer
from backtest.comparator import BacktestComparator
from config.config import Config

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


def example_1_basic_backtest():
    """
    Example 1: Backtest พื้นฐาน
    ทดสอบ 1 symbol ในช่วง 7 วันย้อนหลัง
    """
    logger.info("\n" + "="*80)
    logger.info("Example 1: Basic Backtest (1 Symbol, 7 Days)")
    logger.info("="*80)
    
    # Setup
    client = Spot(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
    loader = HistoricalDataLoader(client=client)
    
    # Date range
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=7)
    
    # Load data
    data = loader.download_historical_data(
        symbol='BTCUSDT',
        interval='1m',
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    if data is None:
        logger.error("Failed to load data")
        return
    
    # Run backtest
    engine = BacktestEngine(
        initial_balance=100.0,
        commission_rate=0.001,
        slippage_pct=0.0005
    )
    
    results = engine.run_backtest(data={'BTCUSDT': data})
    
    # Show results
    metrics = PerformanceMetrics.calculate_metrics(results['trades'], 100.0)
    PerformanceMetrics.print_summary(metrics)


def example_2_multiple_symbols():
    """
    Example 2: Backtest หลาย Symbols
    ทดสอบ 5 symbols พร้อมกัน
    """
    logger.info("\n" + "="*80)
    logger.info("Example 2: Multiple Symbols Backtest")
    logger.info("="*80)
    
    client = Spot(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
    loader = HistoricalDataLoader(client=client)
    
    # Symbols to test
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']
    
    # Load data for all symbols
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=14)
    
    historical_data = loader.prepare_multiple_symbols(
        symbols=symbols,
        interval='1m',
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    # Run backtest
    engine = BacktestEngine(
        initial_balance=200.0,
        max_positions=3,  # Trade 3 symbols at a time
        position_size_pct=0.33
    )
    
    results = engine.run_backtest(data=historical_data)
    
    # Show results
    metrics = PerformanceMetrics.calculate_metrics(results['trades'], 200.0)
    PerformanceMetrics.print_summary(metrics)
    
    # Show per-symbol performance
    if metrics.get('symbol_stats'):
        logger.info("\n📊 Per-Symbol Performance:")
        for symbol, stats in metrics['symbol_stats'].items():
            logger.info(f"  {symbol}: {stats['trades']} trades, "
                       f"{stats['win_rate']:.1f}% win rate, "
                       f"${stats['total_pnl']:.2f} P&L")


def example_3_parameter_optimization():
    """
    Example 3: Parameter Optimization
    ทดสอบหลาย configurations เพื่อหาค่าที่ดีที่สุด
    """
    logger.info("\n" + "="*80)
    logger.info("Example 3: Parameter Optimization")
    logger.info("="*80)
    
    # Load data once
    client = Spot(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
    loader = HistoricalDataLoader(client=client)
    
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=30)
    
    historical_data = loader.prepare_multiple_symbols(
        symbols=['BTCUSDT', 'ETHUSDT'],
        interval='5m',  # Use 5m for faster testing
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    # Test different configurations
    configs = [
        {'max_positions': 1, 'position_size_pct': 1.0, 'name': 'Conservative'},
        {'max_positions': 2, 'position_size_pct': 0.5, 'name': 'Balanced'},
        {'max_positions': 3, 'position_size_pct': 0.33, 'name': 'Aggressive'},
    ]
    
    results_summary = []
    
    for config in configs:
        logger.info(f"\n🧪 Testing: {config['name']}")
        
        engine = BacktestEngine(
            initial_balance=100.0,
            max_positions=config['max_positions'],
            position_size_pct=config['position_size_pct']
        )
        
        results = engine.run_backtest(data=historical_data)
        metrics = PerformanceMetrics.calculate_metrics(results['trades'], 100.0)
        
        results_summary.append({
            'name': config['name'],
            'total_trades': metrics.get('total_trades', 0),
            'win_rate': metrics.get('win_rate', 0),
            'total_return': metrics.get('total_return_pct', 0),
            'sharpe_ratio': metrics.get('sharpe_ratio', 0),
            'max_drawdown': metrics.get('max_drawdown_pct', 0)
        })
    
    # Compare results
    logger.info("\n" + "="*80)
    logger.info("📊 OPTIMIZATION RESULTS")
    logger.info("="*80)
    
    for result in results_summary:
        logger.info(f"\n{result['name']}:")
        logger.info(f"  Total Trades: {result['total_trades']}")
        logger.info(f"  Win Rate: {result['win_rate']:.2f}%")
        logger.info(f"  Return: {result['total_return']:.2f}%")
        logger.info(f"  Sharpe: {result['sharpe_ratio']:.2f}")
        logger.info(f"  Max DD: {result['max_drawdown']:.2f}%")
    
    # Find best by Sharpe Ratio
    best = max(results_summary, key=lambda x: x['sharpe_ratio'])
    logger.info(f"\n🏆 Best Configuration: {best['name']} (Sharpe: {best['sharpe_ratio']:.2f})")


def example_4_visualization():
    """
    Example 4: สร้าง Visualization
    รัน backtest และสร้างกราฟ
    """
    logger.info("\n" + "="*80)
    logger.info("Example 4: Visualization")
    logger.info("="*80)
    
    # Run a simple backtest
    client = Spot(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
    loader = HistoricalDataLoader(client=client)
    
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=7)
    
    data = loader.download_historical_data(
        symbol='BTCUSDT',
        interval='1m',
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    engine = BacktestEngine(initial_balance=100.0)
    results = engine.run_backtest(data={'BTCUSDT': data})
    
    # Create visualizations
    logger.info("\n📊 Creating charts...")
    
    try:
        visualizer = BacktestVisualizer(
            trades=results['trades'],
            equity_curve=results['equity_curve']
        )
        
        visualizer.create_full_report(output_dir="backtest/reports")
        logger.info("✅ Charts created in backtest/reports/")
        
    except Exception as e:
        logger.error(f"❌ Visualization failed: {e}")
        logger.info("💡 Make sure matplotlib is installed: pip install matplotlib")


def example_5_walk_forward():
    """
    Example 5: Walk-Forward Analysis
    ทดสอบแบบเดินหน้า (ช่วงเวลาต่อเนื่อง)
    """
    logger.info("\n" + "="*80)
    logger.info("Example 5: Walk-Forward Analysis")
    logger.info("="*80)
    
    client = Spot(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
    loader = HistoricalDataLoader(client=client)
    
    # Define periods
    periods = [
        ('Week 1', timedelta(days=7)),
        ('Week 2', timedelta(days=7)),
        ('Week 3', timedelta(days=7)),
        ('Week 4', timedelta(days=7)),
    ]
    
    all_results = []
    
    end_date = datetime.now(UTC)
    
    for name, duration in reversed(periods):
        start_date = end_date - duration
        
        logger.info(f"\n📅 Testing {name}: {start_date.date()} to {end_date.date()}")
        
        # Load data
        data = loader.download_historical_data(
            symbol='BTCUSDT',
            interval='5m',
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        
        if data is None:
            continue
        
        # Run backtest
        engine = BacktestEngine(initial_balance=100.0)
        results = engine.run_backtest(data={'BTCUSDT': data})
        metrics = PerformanceMetrics.calculate_metrics(results['trades'], 100.0)
        
        all_results.append({
            'period': name,
            'trades': metrics.get('total_trades', 0),
            'win_rate': metrics.get('win_rate', 0),
            'return': metrics.get('total_return_pct', 0)
        })
        
        # Move to previous period
        end_date = start_date
    
    # Show summary
    logger.info("\n" + "="*80)
    logger.info("📊 WALK-FORWARD RESULTS")
    logger.info("="*80)
    
    for result in reversed(all_results):
        logger.info(f"{result['period']}: {result['trades']} trades, "
                   f"{result['win_rate']:.1f}% WR, "
                   f"{result['return']:+.2f}% return")
    
    # Calculate average
    if all_results:
        avg_win_rate = sum(r['win_rate'] for r in all_results) / len(all_results)
        avg_return = sum(r['return'] for r in all_results) / len(all_results)
        
        logger.info(f"\n📊 Average across all periods:")
        logger.info(f"  Win Rate: {avg_win_rate:.2f}%")
        logger.info(f"  Return: {avg_return:+.2f}%")


# ==================== MAIN ====================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║         🧪 Advanced Backtest Examples                         ║
╚════════════════════════════════════════════════════════════════╝

เลือกตัวอย่างที่ต้องการรัน:

1. Basic Backtest (1 Symbol, 7 Days)
2. Multiple Symbols Backtest
3. Parameter Optimization
4. Visualization
5. Walk-Forward Analysis
0. Run All Examples

""")
    
    try:
        choice = input("Enter choice (1-5, or 0 for all): ").strip()
        
        if choice == '1':
            example_1_basic_backtest()
        elif choice == '2':
            example_2_multiple_symbols()
        elif choice == '3':
            example_3_parameter_optimization()
        elif choice == '4':
            example_4_visualization()
        elif choice == '5':
            example_5_walk_forward()
        elif choice == '0':
            example_1_basic_backtest()
            example_2_multiple_symbols()
            example_3_parameter_optimization()
            example_4_visualization()
            example_5_walk_forward()
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
