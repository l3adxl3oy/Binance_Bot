"""
📈 Performance Metrics Calculator
วิเคราะห์ผลการเทรดและคำนวณ metrics ต่างๆ
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """คำนวณและวิเคราะห์ผลการเทรดจาก backtest"""
    
    @staticmethod
    def calculate_metrics(trades: List[Dict], initial_balance: float) -> Dict:
        """
        คำนวณ metrics หลักของ backtest
        
        Args:
            trades: List of trade dictionaries
            initial_balance: Starting capital
            
        Returns:
            Dict containing all performance metrics
        """
        if not trades:
            return PerformanceMetrics._empty_metrics()
        
        df = pd.DataFrame(trades)
        
        # Basic Stats
        total_trades = len(trades)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] < 0])
        breakeven_trades = len(df[df['pnl'] == 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L Stats
        total_pnl = df['pnl'].sum()
        total_pnl_pct = (total_pnl / initial_balance * 100)
        
        gross_profit = df[df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum()) if losing_trades > 0 else 0
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        # Average trades
        avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        avg_trade = df['pnl'].mean()
        
        # Best and worst
        best_trade = df['pnl'].max()
        worst_trade = df['pnl'].min()
        largest_win_pct = df['pnl_pct'].max() if 'pnl_pct' in df else 0
        largest_loss_pct = df['pnl_pct'].min() if 'pnl_pct' in df else 0
        
        # Expectancy
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
        
        # Risk/Reward Ratio
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Drawdown
        df_sorted = df.sort_values('exit_time')
        equity_curve = initial_balance + df_sorted['pnl'].cumsum()
        max_drawdown, max_dd_pct = PerformanceMetrics._calculate_drawdown(equity_curve, initial_balance)
        
        # Sharpe Ratio (annualized)
        returns = df['pnl'] / initial_balance
        sharpe_ratio = PerformanceMetrics._calculate_sharpe_ratio(returns)
        
        # Trade Duration
        df['entry_time'] = pd.to_datetime(df['entry_time']).dt.tz_localize(None)
        df['exit_time'] = pd.to_datetime(df['exit_time']).dt.tz_localize(None)
        df['duration'] = df['exit_time'] - df['entry_time']
        avg_duration = df['duration'].mean()
        
        # Per symbol stats
        symbol_stats = PerformanceMetrics._calculate_per_symbol_stats(df)
        
        # Time-based analysis
        time_stats = PerformanceMetrics._calculate_time_based_stats(df)
        
        # Final balance
        final_balance = initial_balance + total_pnl
        
        return {
            # Overview
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "total_pnl": total_pnl,
            "total_return_pct": total_pnl_pct,
            
            # Trade Stats
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "breakeven_trades": breakeven_trades,
            "win_rate": win_rate,
            
            # P&L
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            
            # Average Trades
            "avg_trade": avg_trade,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "risk_reward_ratio": risk_reward_ratio,
            
            # Best/Worst
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "largest_win_pct": largest_win_pct,
            "largest_loss_pct": largest_loss_pct,
            
            # Risk Metrics
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_dd_pct,
            "sharpe_ratio": sharpe_ratio,
            
            # Duration
            "avg_duration_seconds": avg_duration.total_seconds() if avg_duration else 0,
            "avg_duration_minutes": avg_duration.total_seconds() / 60 if avg_duration else 0,
            
            # Detailed Stats
            "symbol_stats": symbol_stats,
            "time_stats": time_stats,
            "equity_curve": equity_curve.tolist()
        }
    
    @staticmethod
    def _calculate_drawdown(equity_curve: pd.Series, initial_balance: float) -> Tuple[float, float]:
        """คำนวณ Maximum Drawdown"""
        running_max = equity_curve.expanding().max()
        drawdown = equity_curve - running_max
        max_dd = drawdown.min()
        max_dd_pct = (max_dd / initial_balance * 100) if initial_balance > 0 else 0
        return max_dd, max_dd_pct
    
    @staticmethod
    def _calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        คำนวณ Sharpe Ratio (annualized)
        สมมติ 365 trading days per year
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate
        sharpe = excess_returns.mean() / returns.std()
        sharpe_annualized = sharpe * np.sqrt(365)  # Annualize
        
        return sharpe_annualized
    
    @staticmethod
    def _calculate_per_symbol_stats(df: pd.DataFrame) -> Dict:
        """คำนวณ stats แยกตามแต่ละ symbol"""
        if 'symbol' not in df:
            return {}
        
        stats = {}
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol]
            
            total = len(symbol_df)
            wins = len(symbol_df[symbol_df['pnl'] > 0])
            win_rate = (wins / total * 100) if total > 0 else 0
            total_pnl = symbol_df['pnl'].sum()
            
            stats[symbol] = {
                "trades": total,
                "wins": wins,
                "losses": total - wins,
                "win_rate": win_rate,
                "total_pnl": total_pnl,
                "avg_pnl": symbol_df['pnl'].mean()
            }
        
        return stats
    
    @staticmethod
    def _calculate_time_based_stats(df: pd.DataFrame) -> Dict:
        """วิเคราะห์ผลตามช่วงเวลา (hour of day, day of week)"""
        if 'entry_time' not in df:
            return {}
        
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['hour'] = df['entry_time'].dt.hour
        df['day_of_week'] = df['entry_time'].dt.day_name()
        
        # By hour
        hourly_stats = {}
        for hour in range(24):
            hour_df = df[df['hour'] == hour]
            if len(hour_df) > 0:
                hourly_stats[hour] = {
                    "trades": len(hour_df),
                    "win_rate": (len(hour_df[hour_df['pnl'] > 0]) / len(hour_df) * 100),
                    "avg_pnl": hour_df['pnl'].mean()
                }
        
        # By day of week
        daily_stats = {}
        for day in df['day_of_week'].unique():
            day_df = df[df['day_of_week'] == day]
            daily_stats[day] = {
                "trades": len(day_df),
                "win_rate": (len(day_df[day_df['pnl'] > 0]) / len(day_df) * 100),
                "avg_pnl": day_df['pnl'].mean()
            }
        
        return {
            "by_hour": hourly_stats,
            "by_day": daily_stats
        }
    
    @staticmethod
    def _empty_metrics() -> Dict:
        """Return empty metrics when no trades"""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "total_return_pct": 0,
            "message": "No trades executed"
        }
    
    @staticmethod
    def print_summary(metrics: Dict):
        """พิมพ์สรุปผลการ backtest แบบสวยงาม"""
        if not metrics or metrics.get("total_trades", 0) == 0:
            logger.info("❌ No trades to display")
            return
        
        logger.info("=" * 80)
        logger.info("📊 BACKTEST RESULTS".center(80))
        logger.info("=" * 80)
        
        # Overview
        logger.info(f"💰 Initial Balance: ${metrics['initial_balance']:,.2f}")
        logger.info(f"💰 Final Balance:   ${metrics['final_balance']:,.2f}")
        logger.info(f"📈 Total P&L:       ${metrics['total_pnl']:,.2f} ({metrics['total_return_pct']:+.2f}%)")
        logger.info("-" * 80)
        
        # Trade Statistics
        logger.info(f"📊 Total Trades:    {metrics['total_trades']}")
        logger.info(f"✅ Winning Trades:  {metrics['winning_trades']} ({metrics['win_rate']:.2f}%)")
        logger.info(f"❌ Losing Trades:   {metrics['losing_trades']}")
        logger.info(f"🎯 Profit Factor:   {metrics['profit_factor']:.2f}")
        logger.info(f"💡 Expectancy:      ${metrics['expectancy']:.2f}")
        logger.info("-" * 80)
        
        # Average Trades
        logger.info(f"📊 Avg Trade:       ${metrics['avg_trade']:,.2f}")
        logger.info(f"✅ Avg Win:         ${metrics['avg_win']:,.2f}")
        logger.info(f"❌ Avg Loss:        ${metrics['avg_loss']:,.2f}")
        logger.info(f"⚖️  Risk/Reward:     {metrics['risk_reward_ratio']:.2f}")
        logger.info("-" * 80)
        
        # Best/Worst
        logger.info(f"🎉 Best Trade:      ${metrics['best_trade']:,.2f} ({metrics['largest_win_pct']:+.2f}%)")
        logger.info(f"😢 Worst Trade:     ${metrics['worst_trade']:,.2f} ({metrics['largest_loss_pct']:+.2f}%)")
        logger.info("-" * 80)
        
        # Risk Metrics
        logger.info(f"📉 Max Drawdown:    ${metrics['max_drawdown']:,.2f} ({metrics['max_drawdown_pct']:.2f}%)")
        logger.info(f"📊 Sharpe Ratio:    {metrics['sharpe_ratio']:.2f}")
        logger.info(f"⏱️  Avg Duration:    {metrics['avg_duration_minutes']:.1f} minutes")
        logger.info("=" * 80)
