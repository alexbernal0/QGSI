"""
OBQ Production Portfolio Simulator - LONG Strategy (Memory Efficient)
Processes data chunk-by-chunk to minimize memory usage
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

print("="*80)
print("OBQ PRODUCTION PORTFOLIO SIMULATOR - LONG STRATEGY")
print("="*80)

# Configuration
STARTING_CAPITAL = 1_000_000
MAX_POSITIONS = 10
POSITION_SIZE_PCT = 0.10
ATR_PERIOD = 30
MULTIPLIER = 5.0
MAX_BARS = 20

# First pass: Get all unique dates and signals
print("\n[1/7] Scanning for signals and dates...")
chunk_files = sorted([f for f in os.listdir('/home/ubuntu/stage4_optimization/data_chunks') 
                      if f.startswith('chunk_') and f.endswith('.parquet')])

all_dates = set()
signal_queue = []  # List of (date, symbol, atr) for LONG signals

for i, chunk_file in enumerate(chunk_files):
    chunk_path = f'/home/ubuntu/stage4_optimization/data_chunks/{chunk_file}'
    df = pd.read_parquet(chunk_path)
    
    # Calculate ATR for each symbol in chunk
    for symbol in df['Symbol'].unique():
        symbol_data = df[df['Symbol'] == symbol].copy().sort_values('BarDate')
        
        # Calculate ATR
        high_low = symbol_data['High'] - symbol_data['Low']
        high_close = np.abs(symbol_data['High'] - symbol_data['Close'].shift())
        low_close = np.abs(symbol_data['Low'] - symbol_data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        symbol_data['ATR'] = tr.ewm(alpha=1/ATR_PERIOD, adjust=False).mean()
        
        # Find LONG signals
        long_signals = symbol_data[symbol_data['Signal'] == 1].copy()
        
        for _, row in long_signals.iterrows():
            signal_queue.append({
                'Date': row['BarDate'],
                'Symbol': symbol,
                'Close': row['Close'],
                'ATR': row['ATR']
            })
        
        # Collect all dates
        all_dates.update(symbol_data['BarDate'].tolist())
    
    print(f"  Processed chunk {i+1}/{len(chunk_files)}: {len(signal_queue):,} signals found")

all_dates = sorted(list(all_dates))
signal_queue = sorted(signal_queue, key=lambda x: (x['Date'], -x['ATR']))  # Sort by date, then ATR desc

print(f"✓ Found {len(signal_queue):,} LONG signals across {len(all_dates):,} trading days")

# Initialize portfolio
print("\n[2/7] Initializing portfolio...")
current_equity = STARTING_CAPITAL
active_positions = {}
trade_log = []
equity_curve = []
signal_index = 0

print(f"✓ Starting capital: ${STARTING_CAPITAL:,.0f}")
print(f"✓ Max positions: {MAX_POSITIONS}")
print(f"✓ Position size: {POSITION_SIZE_PCT*100:.0f}% of equity")

# Main simulation loop
print("\n[3/7] Running simulation...")
total_days = len(all_dates)

for day_num, current_date in enumerate(all_dates):
    if day_num % 500 == 0:
        print(f"  Processing day {day_num}/{total_days} ({current_date})...")
    
    # Load only today's price data (from relevant chunks)
    today_prices = {}
    for chunk_file in chunk_files:
        chunk_path = f'/home/ubuntu/stage4_optimization/data_chunks/{chunk_file}'
        df = pd.read_parquet(chunk_path)
        today_data = df[df['BarDate'] == current_date]
        
        if len(today_data) > 0:
            for _, row in today_data.iterrows():
                # Calculate ATR on the fly
                symbol_data = df[df['Symbol'] == row['Symbol']].sort_values('BarDate')
                symbol_data = symbol_data[symbol_data['BarDate'] <= current_date]
                
                high_low = symbol_data['High'] - symbol_data['Low']
                high_close = np.abs(symbol_data['High'] - symbol_data['Close'].shift())
                low_close = np.abs(symbol_data['Low'] - symbol_data['Close'].shift())
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = tr.ewm(alpha=1/ATR_PERIOD, adjust=False).mean().iloc[-1]
                
                today_prices[row['Symbol']] = {
                    'Open': row['Open'],
                    'High': row['High'],
                    'Low': row['Low'],
                    'Close': row['Close'],
                    'ATR': atr
                }
    
    # Process exits
    symbols_to_exit = []
    for symbol, pos in active_positions.items():
        if symbol not in today_prices:
            continue
        
        prices = today_prices[symbol]
        pos['bars_held'] += 1
        
        # Update trailing stop
        new_stop = prices['Low'] - (prices['ATR'] * MULTIPLIER)
        if new_stop > pos['stop']:
            pos['stop'] = new_stop
        
        # Check exit conditions
        exit_reason = None
        exit_price = None
        
        if prices['Low'] <= pos['stop']:
            exit_reason = 'STOP'
            exit_price = pos['stop']
        elif pos['bars_held'] >= MAX_BARS:
            exit_reason = 'TIME'
            exit_price = prices['Close']
        
        if exit_reason:
            exit_value = exit_price * pos['shares']
            net_profit = exit_value - pos['entry_value']
            
            current_equity += net_profit
            
            trade_log.append({
                'Symbol': symbol,
                'EntryDate': pos['entry_date'],
                'EntryPrice': pos['entry_price'],
                'ExitDate': current_date,
                'ExitPrice': exit_price,
                'Shares': pos['shares'],
                'NetProfit': net_profit,
                'PctProfit': (net_profit / pos['entry_value']) * 100,
                'BarsHeld': pos['bars_held'],
                'ExitReason': exit_reason
            })
            
            symbols_to_exit.append(symbol)
    
    for symbol in symbols_to_exit:
        del active_positions[symbol]
    
    # Process new entries
    while signal_index < len(signal_queue) and signal_queue[signal_index]['Date'] == current_date:
        signal = signal_queue[signal_index]
        signal_index += 1
        
        symbol = signal['Symbol']
        
        if len(active_positions) >= MAX_POSITIONS:
            break
        
        if symbol in active_positions:
            continue
        
        if symbol not in today_prices:
            continue
        
        prices = today_prices[symbol]
        position_value = current_equity * POSITION_SIZE_PCT
        entry_price = prices['Close']
        shares = int(position_value / entry_price)
        
        if shares == 0:
            continue
        
        actual_value = shares * entry_price
        initial_stop = entry_price - (prices['ATR'] * MULTIPLIER)
        
        active_positions[symbol] = {
            'entry_date': current_date,
            'entry_price': entry_price,
            'stop': initial_stop,
            'shares': shares,
            'entry_value': actual_value,
            'bars_held': 0
        }
        
        current_equity -= actual_value
    
    # Record equity
    open_value = sum([
        today_prices[sym]['Close'] * pos['shares']
        for sym, pos in active_positions.items()
        if sym in today_prices
    ])
    
    total_equity = current_equity + open_value
    
    equity_curve.append({
        'Date': current_date,
        'Equity': total_equity,
        'NumPositions': len(active_positions)
    })

print(f"✓ Simulation complete: {len(trade_log):,} trades executed")

# Save results
print("\n[4/7] Saving results...")
trades_df = pd.DataFrame(trade_log)
equity_df = pd.DataFrame(equity_curve)

trades_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.parquet', index=False)
equity_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.parquet', index=False)

print(f"✓ Files saved")
print(f"  Final equity: ${total_equity:,.2f}")
print(f"  Total return: {((total_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100):.2f}%")
