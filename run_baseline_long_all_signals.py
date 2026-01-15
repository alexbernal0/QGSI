"""
Run Best LONG Strategy on ALL Signals
Generates complete trade log for production simulation
"""

import pandas as pd
import numpy as np

print("="*80)
print("BASELINE BACKTEST - BEST LONG STRATEGY")
print("Strategy: ATR Trailing Stop, ATR(30), Multiplier 5.0")
print("="*80)

# Load data
print("\n[1/4] Loading data...")
data = pd.read_parquet('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
print(f"✓ Loaded {len(data):,} rows")
print(f"  Symbols: {data['Symbol'].nunique()}")
print(f"  Date range: {data['BarDate'].min()} to {data['BarDate'].max()}")

# Filter LONG signals
long_signals = data[data['Signal'] == 1].copy()
print(f"✓ Found {len(long_signals):,} LONG signals")

# Calculate ATR
print("\n[2/4] Calculating ATR...")

def calculate_atr(df, period=30):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

all_data_with_atr = []
for symbol in data['Symbol'].unique():
    symbol_data = data[data['Symbol'] == symbol].copy().sort_values('BarDate')
    symbol_data['ATR'] = calculate_atr(symbol_data, 30)
    all_data_with_atr.append(symbol_data)

data = pd.concat(all_data_with_atr, ignore_index=True)
print(f"✓ ATR calculated for all symbols")

# Run strategy on each signal
print("\n[3/4] Processing signals...")

ATR_MULT = 5.0
MAX_BARS = 20

trade_log = []

for idx, signal_row in long_signals.iterrows():
    symbol = signal_row['Symbol']
    entry_date = signal_row['BarDate']
    
    # Get symbol data from entry date forward
    symbol_data = data[(data['Symbol'] == symbol) & (data['BarDate'] >= entry_date)].copy()
    
    if len(symbol_data) == 0:
        continue
    
    # Entry
    entry_row = symbol_data.iloc[0]
    entry_price = entry_row['Close']
    initial_stop = entry_price - (entry_row['ATR'] * ATR_MULT)
    
    # Track position
    current_stop = initial_stop
    bars_held = 0
    
    # Check each subsequent bar for exit
    for i in range(len(symbol_data)):
        bar = symbol_data.iloc[i]
        bars_held = i
        
        # Update trailing stop
        new_stop = bar['Low'] - (bar['ATR'] * ATR_MULT)
        if new_stop > current_stop:
            current_stop = new_stop
        
        # Check exit conditions
        exit_reason = None
        exit_price = None
        
        if bar['Low'] <= current_stop:
            exit_reason = 'STOP'
            exit_price = current_stop
        elif bars_held >= MAX_BARS:
            exit_reason = 'TIME'
            exit_price = bar['Close']
        
        if exit_reason:
            # Calculate P&L (using $100K position)
            shares = int(100000 / entry_price)
            net_profit = (exit_price - entry_price) * shares
            
            trade_log.append({
                'Symbol': symbol,
                'EntryDate': entry_date,
                'EntryPrice': entry_price,
                'ExitDate': bar['BarDate'],
                'ExitPrice': exit_price,
                'Shares': shares,
                'NetProfit': net_profit,
                'PctProfit': ((exit_price - entry_price) / entry_price) * 100,
                'BarsInTrade': bars_held,
                'ExitReason': exit_reason,
                'InitialStop': initial_stop,
                'FinalStop': current_stop
            })
            break

print(f"✓ Processed {len(trade_log):,} trades")

# Save trade log
print("\n[4/4] Saving trade log...")
trades_df = pd.DataFrame(trade_log)

trades_df.to_parquet('/home/ubuntu/stage4_optimization/Baseline_Long_All_Trades.parquet', index=False)
trades_df.to_csv('/home/ubuntu/stage4_optimization/Baseline_Long_All_Trades.csv', index=False)

# Summary
winning = trades_df[trades_df['NetProfit'] > 0]
losing = trades_df[trades_df['NetProfit'] < 0]

print(f"\n✓ Trade log saved")
print(f"\n" + "="*80)
print("BASELINE PERFORMANCE")
print("="*80)
print(f"Total Trades:        {len(trades_df):,}")
print(f"Winning Trades:      {len(winning):,} ({len(winning)/len(trades_df)*100:.1f}%)")
print(f"Losing Trades:       {len(losing):,} ({len(losing)/len(trades_df)*100:.1f}%)")
print(f"Net Profit:          ${trades_df['NetProfit'].sum():,.2f}")
print(f"Gross Profit:        ${winning['NetProfit'].sum():,.2f}")
print(f"Gross Loss:          ${abs(losing['NetProfit'].sum()):,.2f}")
print(f"Profit Factor:       {winning['NetProfit'].sum()/abs(losing['NetProfit'].sum()):.3f}")
print(f"Avg Bars Held:       {trades_df['BarsInTrade'].mean():.1f}")
print("="*80)
