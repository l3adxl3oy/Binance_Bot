"""
📈 Backtest Visualization
สร้าง charts และกราฟแสดงผลการ backtest
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import matplotlib, but make it optional
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("⚠️ matplotlib not installed. Visualization features disabled.")
    logger.warning("   Install with: pip install matplotlib")


class BacktestVisualizer:
    """สร้างกราฟและ charts จากผล backtest"""
    
    def __init__(self, results_file: str = None, trades: List[Dict] = None, equity_curve: List[Dict] = None):
        """
        Initialize visualizer
        
        Args:
            results_file: Path to saved backtest results JSON
            trades: List of trades (alternative to loading from file)
            equity_curve: Equity curve data
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("❌ Cannot initialize visualizer: matplotlib not available")
            return
        
        if results_file:
            self._load_from_file(results_file)
        else:
            self.trades = trades or []
            self.equity_curve = equity_curve or []
    
    def _load_from_file(self, filepath: str):
        """โหลดผล backtest จากไฟล์"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.trades = data.get('trades', [])
            self.equity_curve = data.get('equity_curve', [])
            self.metrics = data.get('metrics', {})
            
            logger.info(f"✅ Loaded backtest results from {filepath}")
        except Exception as e:
            logger.error(f"❌ Error loading file: {e}")
            self.trades = []
            self.equity_curve = []
    
    def plot_equity_curve(self, save_path: str = None):
        """
        วาดกราฟ Equity Curve
        
        Args:
            save_path: Path to save figure (optional)
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("❌ matplotlib not available")
            return
        
        if not self.equity_curve:
            logger.warning("⚠️ No equity curve data available")
            return
        
        df = pd.DataFrame(self.equity_curve)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(df['timestamp'], df['equity'], linewidth=2, color='#2196F3', label='Equity')
        ax.fill_between(df['timestamp'], df['equity'], alpha=0.3, color='#2196F3')
        
        # Add horizontal line at starting balance
        if len(df) > 0:
            start_balance = df['equity'].iloc[0]
            ax.axhline(y=start_balance, color='gray', linestyle='--', alpha=0.5, label='Starting Balance')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"💾 Equity curve saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_drawdown(self, save_path: str = None):
        """
        วาดกราฟ Drawdown
        
        Args:
            save_path: Path to save figure
        """
        if not MATPLOTLIB_AVAILABLE or not self.equity_curve:
            return
        
        df = pd.DataFrame(self.equity_curve)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate drawdown
        running_max = df['equity'].expanding().max()
        drawdown = df['equity'] - running_max
        drawdown_pct = (drawdown / running_max * 100)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.fill_between(df['timestamp'], 0, drawdown_pct, color='red', alpha=0.3, label='Drawdown')
        ax.plot(df['timestamp'], drawdown_pct, color='red', linewidth=1)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"💾 Drawdown chart saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_trade_distribution(self, save_path: str = None):
        """
        วาดกราฟกระจายของ P&L
        
        Args:
            save_path: Path to save figure
        """
        if not MATPLOTLIB_AVAILABLE or not self.trades:
            return
        
        df = pd.DataFrame(self.trades)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # P&L distribution
        wins = df[df['pnl'] > 0]['pnl']
        losses = df[df['pnl'] < 0]['pnl']
        
        ax1.hist(wins, bins=20, color='green', alpha=0.7, label=f'Wins ({len(wins)})')
        ax1.hist(losses, bins=20, color='red', alpha=0.7, label=f'Losses ({len(losses)})')
        ax1.set_xlabel('P&L ($)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('P&L Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # P&L percentage distribution
        wins_pct = df[df['pnl_pct'] > 0]['pnl_pct']
        losses_pct = df[df['pnl_pct'] < 0]['pnl_pct']
        
        ax2.hist(wins_pct, bins=20, color='green', alpha=0.7, label='Wins')
        ax2.hist(losses_pct, bins=20, color='red', alpha=0.7, label='Losses')
        ax2.set_xlabel('P&L (%)', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.set_title('P&L % Distribution', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"💾 Trade distribution saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_symbol_performance(self, save_path: str = None):
        """
        วาดกราฟผลตาม symbol
        
        Args:
            save_path: Path to save figure
        """
        if not MATPLOTLIB_AVAILABLE or not self.trades:
            return
        
        df = pd.DataFrame(self.trades)
        
        # Group by symbol
        symbol_stats = df.groupby('symbol').agg({
            'pnl': ['sum', 'mean', 'count']
        }).reset_index()
        
        symbol_stats.columns = ['symbol', 'total_pnl', 'avg_pnl', 'trades']
        symbol_stats = symbol_stats.sort_values('total_pnl', ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Total P&L by symbol
        colors = ['green' if x > 0 else 'red' for x in symbol_stats['total_pnl']]
        ax1.barh(symbol_stats['symbol'], symbol_stats['total_pnl'], color=colors, alpha=0.7)
        ax1.set_xlabel('Total P&L ($)', fontsize=12)
        ax1.set_title('Total P&L by Symbol', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Trade count by symbol
        ax2.barh(symbol_stats['symbol'], symbol_stats['trades'], color='#2196F3', alpha=0.7)
        ax2.set_xlabel('Number of Trades', fontsize=12)
        ax2.set_title('Trades by Symbol', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"💾 Symbol performance saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_full_report(self, output_dir: str = "backtest/reports"):
        """
        สร้างรายงานครบถ้วน (ทุกกราฟ)
        
        Args:
            output_dir: Directory to save all charts
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("❌ matplotlib not available")
            return
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"📊 Creating full backtest report in {output_dir}...")
        
        # Create all charts
        self.plot_equity_curve(f"{output_dir}/equity_curve_{timestamp}.png")
        self.plot_drawdown(f"{output_dir}/drawdown_{timestamp}.png")
        self.plot_trade_distribution(f"{output_dir}/trade_distribution_{timestamp}.png")
        self.plot_symbol_performance(f"{output_dir}/symbol_performance_{timestamp}.png")
        
        logger.info(f"✅ Full report created in {output_dir}")


# Example usage
if __name__ == "__main__":
    # Load a backtest result file and visualize
    import sys
    
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Find the most recent results file
        import glob
        files = glob.glob("backtest/results/*.json")
        if files:
            results_file = max(files, key=lambda x: x)
        else:
            print("❌ No backtest results found. Run backtest first.")
            sys.exit(1)
    
    print(f"📊 Visualizing: {results_file}")
    
    visualizer = BacktestVisualizer(results_file=results_file)
    visualizer.create_full_report()
