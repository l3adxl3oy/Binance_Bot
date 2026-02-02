"""
📊 Historical Data Loader
โหลดข้อมูลราคาย้อนหลังจาก Binance หรือไฟล์ CSV
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional
import os
import json
from binance.spot import Spot
import time

logger = logging.getLogger(__name__)


class HistoricalDataLoader:
    """โหลดและจัดการข้อมูลราคาย้อนหลัง"""
    
    def __init__(self, client: Optional[Spot] = None, cache_dir: str = "backtest/data"):
        """
        Initialize data loader
        
        Args:
            client: Binance Spot client (optional)
            cache_dir: Directory to cache downloaded data
        """
        self.client = client
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def download_historical_data(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        ดาวน์โหลดข้อมูลราคาย้อนหลังจาก Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1m', '5m', '15m', etc.)
            start_date: Start date
            end_date: End date
            use_cache: Use cached data if available
            
        Returns:
            DataFrame with OHLCV data
        """
        # Check cache first
        cache_file = self._get_cache_filename(symbol, interval, start_date, end_date)
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📂 Loading cached data for {symbol} from {cache_file}")
            return pd.read_csv(cache_file, parse_dates=['timestamp'])
        
        if not self.client:
            logger.error("❌ No Binance client provided")
            return None
        
        logger.info(f"⬇️ Downloading {symbol} data from {start_date} to {end_date}")
        
        all_klines = []
        current_start = start_date
        
        # Download in chunks (Binance limit is 1000 candles per request)
        while current_start < end_date:
            try:
                start_ms = int(current_start.timestamp() * 1000)
                
                klines = self.client.klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=start_ms,
                    limit=1000
                )
                
                if not klines:
                    break
                
                all_klines.extend(klines)
                
                # Update start time for next batch
                last_time = datetime.fromtimestamp(klines[-1][0] / 1000, tz=UTC)
                current_start = last_time + timedelta(minutes=1)
                
                # Rate limiting
                time.sleep(0.1)
                
                if len(all_klines) % 10000 == 0:
                    logger.info(f"  Downloaded {len(all_klines)} candles...")
                
            except Exception as e:
                logger.error(f"❌ Error downloading data: {e}")
                break
        
        if not all_klines:
            logger.error(f"❌ No data downloaded for {symbol}")
            return None
        
        # Convert to DataFrame
        df = self._klines_to_dataframe(all_klines)
        
        # Filter by date range (convert start/end to tz-naive for comparison)
        start_naive = start_date.replace(tzinfo=None)
        end_naive = end_date.replace(tzinfo=None)
        df = df[(df['timestamp'] >= start_naive) & (df['timestamp'] <= end_naive)]
        
        # Save to cache
        df.to_csv(cache_file, index=False)
        logger.info(f"✅ Downloaded {len(df)} candles for {symbol} and saved to cache")
        
        return df
    
    def load_from_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        โหลดข้อมูลจากไฟล์ CSV
        
        Expected columns: timestamp, open, high, low, close, volume
        """
        try:
            df = pd.read_csv(filepath, parse_dates=['timestamp'])
            logger.info(f"✅ Loaded {len(df)} candles from {filepath}")
            return df
        except Exception as e:
            logger.error(f"❌ Error loading CSV: {e}")
            return None
    
    def prepare_multiple_symbols(
        self,
        symbols: List[str],
        interval: str,
        start_date: datetime,
        end_date: datetime,
        use_cache: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        เตรียมข้อมูลหลายคู่เทรดพร้อมกัน
        
        Returns:
            Dict mapping symbol to DataFrame
        """
        data = {}
        
        for symbol in symbols:
            logger.info(f"📊 Processing {symbol}...")
            df = self.download_historical_data(
                symbol=symbol,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                use_cache=use_cache
            )
            
            if df is not None and len(df) > 0:
                data[symbol] = df
            else:
                logger.warning(f"⚠️ Skipping {symbol} - no data available")
        
        logger.info(f"✅ Prepared data for {len(data)}/{len(symbols)} symbols")
        return data
    
    def _klines_to_dataframe(self, klines: List) -> pd.DataFrame:
        """แปลง Binance klines เป็น DataFrame"""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # Keep only essential columns
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        return df
    
    def _get_cache_filename(
        self,
        symbol: str,
        interval: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """สร้างชื่อไฟล์สำหรับ cache"""
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        return os.path.join(
            self.cache_dir,
            f"{symbol}_{interval}_{start_str}_{end_str}.csv"
        )
    
    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """รับข้อมูลสรุปของ DataFrame"""
        if df is None or len(df) == 0:
            return {}
        
        return {
            "total_candles": len(df),
            "start_date": df['timestamp'].iloc[0],
            "end_date": df['timestamp'].iloc[-1],
            "duration_days": (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).days,
            "price_range": {
                "min": float(df['low'].min()),
                "max": float(df['high'].max()),
                "mean": float(df['close'].mean())
            },
            "volume_stats": {
                "total": float(df['volume'].sum()),
                "mean": float(df['volume'].mean()),
                "max": float(df['volume'].max())
            }
        }
