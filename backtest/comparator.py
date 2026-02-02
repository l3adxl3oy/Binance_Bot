"""
⚖️ Backtest Comparison Tool
เปรียบเทียบผลของ backtest หลายๆ รอบ
"""

import logging
import json
import pandas as pd
from typing import List, Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class BacktestComparator:
    """เปรียบเทียบผลการ backtest หลายๆ รอบ"""
    
    def __init__(self, result_files: List[str] = None):
        """
        Initialize comparator
        
        Args:
            result_files: List of paths to backtest result JSON files
        """
        self.result_files = result_files or []
        self.results = []
        
        if result_files:
            self.load_results(result_files)
    
    def load_results(self, files: List[str]):
        """โหลดผล backtest จากหลายไฟล์"""
        self.results = []
        
        for filepath in files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Add filename for reference
                data['filename'] = Path(filepath).name
                self.results.append(data)
                
                logger.info(f"✅ Loaded: {filepath}")
            except Exception as e:
                logger.error(f"❌ Error loading {filepath}: {e}")
        
        logger.info(f"📊 Loaded {len(self.results)} backtest results")
    
    def compare_metrics(self) -> pd.DataFrame:
        """
        เปรียบเทียบ metrics หลัก
        
        Returns:
            DataFrame with comparison
        """
        if not self.results:
            logger.warning("⚠️ No results to compare")
            return pd.DataFrame()
        
        comparison_data = []
        
        for result in self.results:
            metrics = result.get('metrics', {})
            config = result.get('config', {})
            
            comparison_data.append({
                'File': result.get('filename', 'Unknown'),
                'Symbols': ', '.join(config.get('symbols', [])),
                'Period': f"{config.get('start_date', '')} to {config.get('end_date', '')}",
                'Total Trades': metrics.get('total_trades', 0),
                'Win Rate (%)': f"{metrics.get('win_rate', 0):.2f}",
                'Total Return (%)': f"{metrics.get('total_return_pct', 0):.2f}",
                'Final Balance ($)': f"{metrics.get('final_balance', 0):.2f}",
                'Profit Factor': f"{metrics.get('profit_factor', 0):.2f}",
                'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
                'Max Drawdown (%)': f"{metrics.get('max_drawdown_pct', 0):.2f}",
                'Avg Trade ($)': f"{metrics.get('avg_trade', 0):.2f}",
            })
        
        df = pd.DataFrame(comparison_data)
        return df
    
    def print_comparison(self):
        """พิมพ์ตารางเปรียบเทียบ"""
        df = self.compare_metrics()
        
        if df.empty:
            logger.warning("⚠️ No data to display")
            return
        
        logger.info("\n" + "="*120)
        logger.info("📊 BACKTEST COMPARISON".center(120))
        logger.info("="*120)
        
        # Print as table
        print(df.to_string(index=False))
        
        logger.info("="*120)
    
    def find_best_result(self, metric: str = 'total_return_pct') -> Dict:
        """
        หา backtest ที่ดีที่สุดตาม metric ที่กำหนด
        
        Args:
            metric: Metric to optimize ('total_return_pct', 'sharpe_ratio', 'profit_factor', etc.)
            
        Returns:
            Best result data
        """
        if not self.results:
            return {}
        
        best_result = max(
            self.results,
            key=lambda x: x.get('metrics', {}).get(metric, 0)
        )
        
        logger.info(f"\n🏆 Best result by {metric}:")
        logger.info(f"   File: {best_result.get('filename', 'Unknown')}")
        logger.info(f"   {metric}: {best_result.get('metrics', {}).get(metric, 0):.2f}")
        
        return best_result
    
    def export_comparison_csv(self, output_file: str = "backtest/comparison.csv"):
        """
        ส่งออกตารางเปรียบเทียบเป็น CSV
        
        Args:
            output_file: Path to save CSV
        """
        df = self.compare_metrics()
        
        if df.empty:
            logger.warning("⚠️ No data to export")
            return
        
        # Create directory if needed
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_file, index=False)
        logger.info(f"💾 Comparison exported to: {output_file}")
    
    def get_summary_statistics(self) -> Dict:
        """
        สรุปสถิติรวมจาก backtests ทั้งหมด
        
        Returns:
            Dict with summary stats
        """
        if not self.results:
            return {}
        
        all_metrics = [r.get('metrics', {}) for r in self.results]
        
        summary = {
            'total_backtests': len(self.results),
            'avg_win_rate': sum(m.get('win_rate', 0) for m in all_metrics) / len(all_metrics),
            'avg_return_pct': sum(m.get('total_return_pct', 0) for m in all_metrics) / len(all_metrics),
            'best_return_pct': max(m.get('total_return_pct', 0) for m in all_metrics),
            'worst_return_pct': min(m.get('total_return_pct', 0) for m in all_metrics),
            'avg_sharpe_ratio': sum(m.get('sharpe_ratio', 0) for m in all_metrics) / len(all_metrics),
            'avg_profit_factor': sum(m.get('profit_factor', 0) for m in all_metrics) / len(all_metrics),
        }
        
        return summary
    
    def print_summary(self):
        """พิมพ์สรุปสถิติ"""
        summary = self.get_summary_statistics()
        
        if not summary:
            logger.warning("⚠️ No summary available")
            return
        
        logger.info("\n" + "="*80)
        logger.info("📊 SUMMARY STATISTICS".center(80))
        logger.info("="*80)
        logger.info(f"Total Backtests: {summary['total_backtests']}")
        logger.info(f"Average Win Rate: {summary['avg_win_rate']:.2f}%")
        logger.info(f"Average Return: {summary['avg_return_pct']:.2f}%")
        logger.info(f"Best Return: {summary['best_return_pct']:.2f}%")
        logger.info(f"Worst Return: {summary['worst_return_pct']:.2f}%")
        logger.info(f"Average Sharpe Ratio: {summary['avg_sharpe_ratio']:.2f}")
        logger.info(f"Average Profit Factor: {summary['avg_profit_factor']:.2f}")
        logger.info("="*80)


# Example usage
if __name__ == "__main__":
    import glob
    
    # Find all backtest result files
    result_files = glob.glob("backtest/results/*.json")
    
    if not result_files:
        print("❌ No backtest results found. Run backtest first.")
    else:
        print(f"📊 Found {len(result_files)} backtest results")
        
        comparator = BacktestComparator(result_files)
        comparator.print_comparison()
        comparator.print_summary()
        
        # Find best by different metrics
        comparator.find_best_result('total_return_pct')
        comparator.find_best_result('sharpe_ratio')
        comparator.find_best_result('profit_factor')
        
        # Export to CSV
        comparator.export_comparison_csv()
