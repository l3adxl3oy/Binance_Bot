# 🧪 Backtest System Documentation

ระบบทดสอบกลยุทธ์การเทรดด้วยข้อมูลย้อนหลัง (Backtesting System)

## 📋 สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [โครงสร้างไฟล์](#โครงสร้างไฟล์)
3. [การติดตั้ง](#การติดตั้ง)
4. [การใช้งาน](#การใช้งาน)
5. [ฟีเจอร์หลัก](#ฟีเจอร์หลัก)
6. [ตัวอย่างผลลัพธ์](#ตัวอย่างผลลัพธ์)
7. [การปรับแต่ง](#การปรับแต่ง)

---

## 🎯 ภาพรวม

Backtest System ออกแบบมาเพื่อทดสอบกลยุทธ์การเทรดของบอทด้วยข้อมูลราคาย้อนหลัง ช่วยให้คุณ:

- ✅ ทดสอบกลยุทธ์ก่อนใช้เงินจริง
- ✅ วิเคราะห์ผลกำไร/ขาดทุน
- ✅ คำนวณ metrics สำคัญ (Win Rate, Sharpe Ratio, Max Drawdown, etc.)
- ✅ เปรียบเทียบกลยุทธ์หลายๆ แบบ
- ✅ สร้างกราฟและรายงานอัตโนมัติ

---

## 📁 โครงสร้างไฟล์

```
backtest/
│
├── __init__.py                  # Module initialization
├── data_loader.py               # โหลดข้อมูลราคาจาก Binance หรือ CSV
├── backtest_engine.py           # Engine หลักสำหรับจำลองการเทรด
├── performance_metrics.py       # คำนวณและวิเคราะห์ metrics
├── visualizer.py               # สร้างกราฟและ charts
├── comparator.py               # เปรียบเทียบผล backtests หลายรอบ
├── requirements.txt            # Dependencies สำหรับ backtest
│
├── data/                       # Cache ข้อมูลราคาที่ดาวน์โหลด
├── results/                    # ผลการ backtest (JSON)
└── reports/                    # กราฟและรายงาน (PNG)

run_backtest.py                 # Script หลักสำหรับรัน backtest
```

---

## 🔧 การติดตั้ง

### 1. ติดตั้ง Dependencies

```powershell
# ติดตั้ง packages พื้นฐาน (ถ้ายังไม่มี)
pip install pandas numpy

# ติดตั้ง packages สำหรับ visualization (optional)
pip install matplotlib seaborn
```

หรือติดตั้งจาก requirements ในโฟลเดอร์ backtest:

```powershell
pip install -r backtest/requirements.txt
```

### 2. ตรวจสอบ API Keys

ตรวจสอบว่าไฟล์ `config/config.py` มี API keys ของ Binance:

```python
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
```

**หมายเหตุ:** Backtest จะใช้ API เพื่อดาวน์โหลดข้อมูลราคาเท่านั้น ไม่มีการเทรดจริง

---

## 🚀 การใช้งาน

### 🔹 วิธีที่ 1: รัน Backtest แบบพื้นฐาน

```powershell
python run_backtest.py
```

Script จะรัน backtest ด้วยการตั้งค่าเริ่มต้น:
- ช่วงเวลา: 7 วันย้อนหลัง
- Symbols: BTC, ETH, BNB, SOL, ADA
- ทุนเริ่มต้น: $100
- Timeframe: 1 นาที

### 🔹 วิธีที่ 2: ปรับแต่งพารามิเตอร์

แก้ไขไฟล์ `run_backtest.py`:

```python
# ตั้งค่าช่วงเวลา
START_DATE = datetime(2025, 1, 1, tzinfo=UTC)
END_DATE = datetime(2025, 1, 31, tzinfo=UTC)

# เลือก Symbols
SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    # เพิ่มเติมได้ตามต้องการ
]

# ทุนเริ่มต้น
INITIAL_BALANCE = 100.0

# Timeframe
TIMEFRAME = '1m'  # 1m, 5m, 15m, 1h, etc.
```

### 🔹 วิธีที่ 3: รัน Backtest แบบ Custom

สร้าง script ของคุณเอง:

```python
from datetime import datetime, timedelta, UTC
from run_backtest import run_backtest

# กำหนดพารามิเตอร์
symbols = ['BTCUSDT', 'ETHUSDT']
start = datetime.now(UTC) - timedelta(days=30)
end = datetime.now(UTC)

# รัน backtest
results = run_backtest(
    symbols=symbols,
    start_date=start,
    end_date=end,
    initial_balance=500.0,  # $500
    timeframe='5m',         # 5-minute candles
    use_cache=True
)
```

---

## 🎨 ฟีเจอร์หลัก

### 1️⃣ **Historical Data Loader**

ดาวน์โหลดและจัดการข้อมูลราคา:

```python
from backtest.data_loader import HistoricalDataLoader
from binance.spot import Spot

client = Spot(api_key="...", api_secret="...")
loader = HistoricalDataLoader(client=client)

# ดาวน์โหลดข้อมูล
data = loader.download_historical_data(
    symbol='BTCUSDT',
    interval='1m',
    start_date=start_date,
    end_date=end_date,
    use_cache=True  # ใช้ cache ถ้ามี
)
```

**Features:**
- ✅ ดาวน์โหลดจาก Binance อัตโนมัติ
- ✅ Cache ข้อมูลเพื่อประหยัดเวลา
- ✅ รองรับหลาย symbols
- ✅ โหลดจาก CSV ได้

### 2️⃣ **Backtest Engine**

จำลองการเทรดที่สมจริง:

```python
from backtest.backtest_engine import BacktestEngine

engine = BacktestEngine(
    initial_balance=100.0,
    commission_rate=0.001,    # 0.1% fee
    slippage_pct=0.0005,      # 0.05% slippage
    max_positions=3,          # Max 3 trades พร้อมกัน
    position_size_pct=0.33    # 33% per trade
)

results = engine.run_backtest(data=historical_data)
```

**Features:**
- ✅ จำลอง slippage และ commission
- ✅ Position management
- ✅ Stop Loss / Take Profit
- ✅ Time-based exits
- ✅ ใช้ indicators เดียวกับบอทจริง

### 3️⃣ **Performance Metrics**

คำนวณ metrics มากกว่า 20 ตัว:

```python
from backtest.performance_metrics import PerformanceMetrics

metrics = PerformanceMetrics.calculate_metrics(
    trades=results['trades'],
    initial_balance=100.0
)

# แสดงผล
PerformanceMetrics.print_summary(metrics)
```

**Metrics ที่คำนวณ:**

| Category | Metrics |
|----------|---------|
| **Basic** | Total Trades, Win Rate, P&L |
| **Risk** | Max Drawdown, Sharpe Ratio, Risk/Reward |
| **Trade** | Avg Win, Avg Loss, Best/Worst Trade |
| **Advanced** | Profit Factor, Expectancy, Symbol Stats |

### 4️⃣ **Visualizer**

สร้างกราฟและ charts:

```python
from backtest.visualizer import BacktestVisualizer

viz = BacktestVisualizer(results_file="backtest/results/backtest_xxx.json")

# สร้างกราฟแต่ละอัน
viz.plot_equity_curve()
viz.plot_drawdown()
viz.plot_trade_distribution()
viz.plot_symbol_performance()

# หรือสร้างทั้งหมดพร้อมกัน
viz.create_full_report(output_dir="backtest/reports")
```

**Charts ที่สร้าง:**
- 📈 Equity Curve
- 📉 Drawdown Chart
- 📊 Trade Distribution (Histogram)
- 🎯 Symbol Performance

### 5️⃣ **Comparator**

เปรียบเทียบผล backtests หลายรอบ:

```python
from backtest.comparator import BacktestComparator
import glob

# โหลดผลทั้งหมด
files = glob.glob("backtest/results/*.json")
comp = BacktestComparator(files)

# แสดงตารางเปรียบเทียบ
comp.print_comparison()

# หา backtest ที่ดีที่สุด
best = comp.find_best_result('sharpe_ratio')

# Export เป็น CSV
comp.export_comparison_csv()
```

---

## 📊 ตัวอย่างผลลัพธ์

### Console Output

```
================================================================================
                            📊 BACKTEST RESULTS                                
================================================================================
💰 Initial Balance: $100.00
💰 Final Balance:   $105.50
📈 Total P&L:       $5.50 (+5.50%)
--------------------------------------------------------------------------------
📊 Total Trades:    45
✅ Winning Trades:  28 (62.22%)
❌ Losing Trades:   17
🎯 Profit Factor:   1.85
💡 Expectancy:      $0.12
--------------------------------------------------------------------------------
📊 Avg Trade:       $0.12
✅ Avg Win:         $0.35
❌ Avg Loss:        -$0.18
⚖️  Risk/Reward:     1.94
--------------------------------------------------------------------------------
🎉 Best Trade:      $1.25 (+2.50%)
😢 Worst Trade:     -$0.75 (-1.50%)
--------------------------------------------------------------------------------
📉 Max Drawdown:    -$2.30 (-2.30%)
📊 Sharpe Ratio:    1.45
⏱️  Avg Duration:    12.5 minutes
================================================================================
```

### JSON Output

ผลลัพธ์ทั้งหมดถูกบันทึกใน `backtest/results/backtest_YYYYMMDD_HHMMSS.json`:

```json
{
  "config": {
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "start_date": "2025-01-01T00:00:00+00:00",
    "end_date": "2025-01-31T23:59:59+00:00",
    "initial_balance": 100.0,
    "timeframe": "1m"
  },
  "metrics": {
    "total_trades": 45,
    "win_rate": 62.22,
    "total_return_pct": 5.50,
    "sharpe_ratio": 1.45,
    ...
  },
  "trades": [...]
}
```

---

## ⚙️ การปรับแต่ง

### 🔧 ปรับพารามิเตอร์ Engine

แก้ไขใน `run_backtest.py` หรือ script ของคุณ:

```python
engine = BacktestEngine(
    initial_balance=500.0,        # เปลี่ยนทุนเริ่มต้น
    commission_rate=0.0005,       # ลด fee (VIP level)
    slippage_pct=0.001,           # เพิ่ม slippage (realistic)
    max_positions=5,              # เทรดพร้อมกันได้ 5 คู่
    position_size_pct=0.2         # ใช้ 20% per trade
)
```

### 🎯 ปรับกลยุทธ์

แก้ไข `backtest_engine.py` ในส่วน signal generation:

```python
def _should_enter_long(self, signals: Dict) -> bool:
    """ปรับเงื่อนไขเข้า LONG"""
    confluence = 0
    
    # เพิ่ม/ลด/แก้ไขเงื่อนไข
    if signals['rsi'] < 30:  # เปลี่ยนจาก 30 เป็นค่าอื่น
        confluence += 1
    
    # เพิ่มเงื่อนไขใหม่
    if signals['volume_ratio'] > 2.0:
        confluence += 2  # ให้น้ำหนักมากขึ้น
    
    return confluence >= 3  # เปลี่ยนขีดตัดสิน
```

### 📈 เพิ่ม Indicators ใหม่

แก้ไข `_calculate_signals()` ใน `backtest_engine.py`:

```python
def _calculate_signals(self, df: pd.DataFrame) -> Dict:
    # ... existing code ...
    
    # เพิ่ม indicator ใหม่
    sma_20 = np.mean(close[-20:])
    sma_50 = np.mean(close[-50:])
    
    return {
        # ... existing signals ...
        'sma_20': sma_20,
        'sma_50': sma_50,
        'sma_cross': 'golden' if sma_20 > sma_50 else 'death'
    }
```

---

## 🎓 Best Practices

### 1. **ใช้ข้อมูลเพียงพอ**
- อย่างน้อย 1 เดือนสำหรับ 1m timeframe
- อย่างน้อย 3-6 เดือนสำหรับ 5m-15m

### 2. **ทดสอบหลายช่วงเวลา**
```python
# ทดสอบหลายช่วง
periods = [
    (datetime(2025, 1, 1), datetime(2025, 1, 31)),
    (datetime(2025, 2, 1), datetime(2025, 2, 28)),
    (datetime(2025, 3, 1), datetime(2025, 3, 31)),
]

for start, end in periods:
    run_backtest(symbols, start, end, ...)
```

### 3. **เปรียบเทียบผล**
```python
# ใช้ Comparator หาค่าเฉลี่ย
comparator = BacktestComparator(all_result_files)
summary = comparator.get_summary_statistics()
```

### 4. **พิจารณา Market Conditions**
- Bull market vs Bear market
- High volatility vs Low volatility
- ทดสอบในทุกสภาวะตลาด

### 5. **ระวัง Overfitting**
- อย่าปรับพารามิเตอร์ให้เหมาะกับข้อมูลเดียว
- ทดสอบ out-of-sample data
- ใช้ walk-forward analysis

---

## 🐛 Troubleshooting

### ❌ API Error
```
Error: 429 Too Many Requests
```
**แก้ไข:** ลดความเร็วในการดาวน์โหลด หรือรอสักครู่

### ❌ No Data
```
Error: No data downloaded for XXXUSDT
```
**แก้ไข:** 
- ตรวจสอบชื่อ symbol ว่าถูกต้อง
- ตรวจสอบช่วงเวลา (อาจเป็นวันหยุด)

### ❌ Visualization Error
```
Error: matplotlib not available
```
**แก้ไข:**
```powershell
pip install matplotlib seaborn
```

### ❌ Memory Error
```
MemoryError: Unable to allocate array
```
**แก้ไข:**
- ลดจำนวน symbols
- ลดช่วงเวลา
- ใช้ timeframe ที่ใหญ่ขึ้น (5m แทน 1m)

---

## 📚 เอกสารเพิ่มเติม

- [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)

---

## 🤝 การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ:

1. ตรวจสอบ logs ใน console
2. ตรวจสอบไฟล์ผลลัพธ์ใน `backtest/results/`
3. เปิด issue หรือติดต่อผู้พัฒนา

---

## 📝 License

ใช้ภายใต้ license เดียวกับ main bot

---

**Happy Backtesting! 🚀📈**
