# yfinance API Documentation

## Overview
yfinance is a free, open-source Python library that downloads historical market data from Yahoo Finance. No API key required.

**Installation:**
```bash
pip install yfinance
```

**Official Docs:** https://github.com/ranaroussi/yfinance

---

## Basic Usage

### Download Stock Data
```python
import yfinance as yf

# Download data for a single ticker
df = yf.download('AAPL', period='1y')

# Download multiple tickers
df = yf.download(['AAPL', 'MSFT', 'GOOGL'], period='1y')
```

### Ticker Object
```python
# Create a Ticker object for detailed data
ticker = yf.Ticker('AAPL')

# Get historical data
hist = ticker.history(period='1y')

# Get company info
info = ticker.info  # Dict with company metadata

# Get financials
financials = ticker.financials
balance_sheet = ticker.balance_sheet
cashflow = ticker.cashflow
```

---

## Parameters

### `period` - Predefined Time Ranges
Valid periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

```python
# Last 1 year of data
df = yf.download('AAPL', period='1y')

# Year to date
df = yf.download('AAPL', period='ytd')

# All available historical data
df = yf.download('AAPL', period='max')
```

### `start` and `end` - Custom Date Ranges
```python
# Specific date range
df = yf.download('AAPL', start='2023-01-01', end='2024-01-01')
```

### `interval` - Data Granularity
Valid intervals: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

```python
# Daily data (default)
df = yf.download('AAPL', period='1y', interval='1d')

# Weekly data
df = yf.download('AAPL', period='1y', interval='1wk')

# Hourly data (max 730 days)
df = yf.download('AAPL', period='1mo', interval='1h')
```

### Other Parameters
```python
df = yf.download(
    'AAPL',
    period='1y',
    auto_adjust=True,      # Adjust OHLC automatically? (default: True)
    prepost=False,         # Include pre/post market data? (default: False)
    threads=True,          # Use threads for mass downloading? (default: True)
    proxy=None             # Proxy server URL (optional)
)
```

---

## DataFrame Structure

### Columns
The returned DataFrame includes:
- **Date** - Index (datetime)
- **Open** - Opening price
- **High** - Highest price of the day
- **Low** - Lowest price of the day
- **Close** - Closing price (adjusted for splits)
- **Volume** - Number of shares traded
- **Dividends** - Dividend amount (if any)
- **Stock Splits** - Stock split ratio (if any)

### Multi-Ticker DataFrames
When downloading multiple tickers, columns have a MultiIndex:

```python
df = yf.download(['AAPL', 'MSFT'], period='1y')

# Access specific ticker's Close price
aapl_close = df['Close']['AAPL']

# Access all tickers' Close price
all_close = df['Close']
```

### Single-Ticker DataFrames
For a single ticker, yfinance may return a MultiIndex with the ticker name:

```python
df = yf.download('AAPL', period='1y')

# May need to access as:
close_price = df['Close']  # This works
# or
close_price = df[('Close', 'AAPL')]  # If MultiIndex
```

**Tip:** Always use `df['Close']` (simple column access) for single tickers.

---

## Common Operations

### Calculate Moving Averages
```python
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()
```

### Calculate Returns
```python
# Daily returns
df['Daily_Return'] = df['Close'].pct_change()

# Cumulative returns
df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
```

### Find Min/Max Prices
```python
# Find minimum closing price
min_price = df['Close'].min()
min_idx = df['Close'].idxmin()

# Find maximum closing price
max_price = df['Close'].max()
max_idx = df['Close'].idxmax()

# Access value at specific index
value_at_min = df.loc[min_idx, 'Close']
```

### Handle MultiIndex Issues
If you encounter MultiIndex issues (e.g., when using `.loc`):

```python
# Safe way to get scalar values
min_price = float(df['Close'].min())
max_price = float(df['Close'].max())

# Or use .values[0]
value = df.loc[min_idx, 'Close'].values[0]
```

---

## Error Handling

### No Data Available
```python
df = yf.download('INVALID_TICKER', period='1y')
# Returns empty DataFrame if ticker not found
```

### Network Issues
```python
import yfinance as yf

try:
    df = yf.download('AAPL', period='1y')
    if df.empty:
        print("No data returned")
except Exception as e:
    print(f"Error: {e}")
```

---

## Example: Complete Stock Analysis Workflow

```python
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Download data
df = yf.download('AAPL', period='1y')

# 2. Calculate indicators
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

# 3. Find extremes
min_price = float(df['Close'].min())
max_price = float(df['Close'].max())
min_idx = df['Close'].idxmin()
max_idx = df['Close'].idxmax()

# 4. Visualize
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df.index, df['Close'], label='Close Price', linewidth=2)
ax.plot(df.index, df['MA20'], label='20-Day MA', linestyle='--')
ax.scatter([min_idx], [min_price], color='red', s=100, zorder=5)
ax.scatter([max_idx], [max_price], color='green', s=100, zorder=5)

ax.set_title('AAPL Stock Price - 1 Year', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Price (USD)', fontsize=12)
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig('stock_chart.png', dpi=300)
plt.close()
```

---

## Tips for LLM Code Generation

1. **Always wrap scalars in float()** when using df values in f-strings:
   ```python
   # Good
   min_price = float(df['Close'].min())
   title = f"Min: ${min_price:.2f}"

   # Bad (may cause TypeError)
   title = f"Min: ${df['Close'].min():.2f}"
   ```

2. **Use simple column access for single tickers:**
   ```python
   # Good
   close = df['Close']

   # Avoid
   close = df[('Close', 'AAPL')]
   ```

3. **Handle index access carefully:**
   ```python
   # Good
   value = df.loc[idx, 'Close'].values[0]
   # or
   value = float(df['Close'].min())

   # Bad (may return DataFrame/Series)
   value = df.loc[idx, 'Close']
   ```

4. **Date formatting:**
   ```python
   # Good
   start = df.index.min().strftime('%Y-%m-%d')
   end = df.index.max().strftime('%Y-%m-%d')
   ```

---

## Common Tickers

- **Tech:** AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), META (Meta)
- **Finance:** JPM (JPMorgan), BAC (Bank of America), GS (Goldman Sachs)
- **Indices:** ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)
- **Crypto:** BTC-USD (Bitcoin), ETH-USD (Ethereum)

---

## Limitations

- **Intraday data:** Limited to last 60-730 days depending on interval
- **No API key:** Free but rate-limited (avoid excessive requests)
- **Data quality:** Yahoo Finance data, quality varies
- **Real-time:** 15-20 minute delay for free data
