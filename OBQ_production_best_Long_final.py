"""
OBQ Production Portfolio Simulator - LONG Strategy (Final)
Uses pre-built price index for efficient processing
"""

import pandas as pd
import numpy as np
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

# Load price index
print("\n[1/5] Loading price index...")
price_data = pd.read_parquet('/home/ubuntu/stage4_optimization/price_index.parquet')
print(f"✓ Loaded {len(price_data):,} rows")

# Get LONG signals
print("\n[2/5] Extracting LONG signals...")
long_signals = price_data[price_data['Signal'] == 1].copy()
long_signals = long_signals.sort_values(['BarDate', 'ATR'], ascending=[True, False])
print(f"✓ Found {len(long_signals):,} LONG signals")

# Get all unique dates
all_dates = sorted(price_data['BarDate'].unique())
print(f"✓ Date range: {all_dates[0]} to {all_dates[-1]} ({len(all_dates):,} days)")

# Initialize portfolio
print("\n[3/5] Running simulation...")
current_equity = STARTING_CAPITAL
active_positions = {}
trade_log = []
equity_curve = []

for day_num, current_date in enumerate(all_dates):
    if day_num % 500 == 0:
        print(f"  Day {day_num}/{len(all_dates)} ({current_date})...")
    
    # Get today's prices (drop duplicates, keep first)
    today_data = price_data[price_data['BarDate'] == current_date].drop_duplicates(subset='Symbol', keep='first').set_index('Symbol')
    
    # Process exits
    symbols_to_exit = []
    for symbol, pos in list(active_positions.items()):
        if symbol not in today_data.index:
            continue
        
        row = today_data.loc[symbol]
        pos['bars_held'] += 1
        
        # Update trailing stop
        new_stop = row['Low'] - (row['ATR'] * MULTIPLIER)
        if new_stop > pos['stop']:
            pos['stop'] = new_stop
        
        # Check exits
        exit_reason = None
        exit_price = None
        
        if row['Low'] <= pos['stop']:
            exit_reason = 'STOP'
            exit_price = pos['stop']
        elif pos['bars_held'] >= MAX_BARS:
            exit_reason = 'TIME'
            exit_price = row['Close']
        
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
    today_signals = long_signals[long_signals['BarDate'] == current_date]
    
    for _, signal in today_signals.iterrows():
        if len(active_positions) >= MAX_POSITIONS:
            break
        
        symbol = signal['Symbol']
        
        if symbol in active_positions:
            continue
        
        if symbol not in today_data.index:
            continue
        
        row = today_data.loc[symbol]
        position_value = current_equity * POSITION_SIZE_PCT
        entry_price = float(row['Close'])
        shares = int(position_value / entry_price)
        
        if shares == 0:
            continue
        
        actual_value = shares * entry_price
        initial_stop = entry_price - (row['ATR'] * MULTIPLIER)
        
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
        today_data.loc[sym]['Close'] * pos['shares']
        for sym, pos in active_positions.items()
        if sym in today_data.index
    ])
    
    total_equity = current_equity + open_value
    
    equity_curve.append({
        'Date': current_date,
        'Equity': total_equity,
        'NumPositions': len(active_positions)
    })

print(f"✓ Simulation complete: {len(trade_log):,} trades")

# Save results
print("\n[4/5] Saving results...")
trades_df = pd.DataFrame(trade_log)
equity_df = pd.DataFrame(equity_curve)

trades_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.parquet', index=False)
trades_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.csv', index=False)
equity_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.parquet', index=False)
equity_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.csv', index=False)

# Calculate metrics
winning = trades_df[trades_df['NetProfit'] > 0]
losing = trades_df[trades_df['NetProfit'] < 0]
final_equity = equity_df['Equity'].iloc[-1]

print(f"\n✓ Results saved")
print(f"\n" + "="*80)
print("PERFORMANCE SUMMARY")
print("="*80)
print(f"Starting Capital:    ${STARTING_CAPITAL:,.0f}")
print(f"Final Equity:        ${final_equity:,.2f}")
print(f"Net Profit:          ${final_equity - STARTING_CAPITAL:,.2f}")
print(f"Total Return:        {((final_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100):.2f}%")
print(f"\nTotal Trades:        {len(trades_df):,}")
print(f"Winning Trades:      {len(winning):,} ({len(winning)/len(trades_df)*100:.1f}%)")
print(f"Losing Trades:       {len(losing):,} ({len(losing)/len(trades_df)*100:.1f}%)")
print(f"\nGross Profit:        ${winning['NetProfit'].sum():,.2f}")
print(f"Gross Loss:          ${abs(losing['NetProfit'].sum()):,.2f}")
print(f"Profit Factor:       {winning['NetProfit'].sum()/abs(losing['NetProfit'].sum()):.3f}")
print(f"\nAvg Win:             ${winning['NetProfit'].mean():,.2f}")
print(f"Avg Loss:            ${abs(losing['NetProfit'].mean()):,.2f}")
print(f"Largest Win:         ${trades_df['NetProfit'].max():,.2f}")
print(f"Largest Loss:        ${trades_df['NetProfit'].min():,.2f}")
print(f"\nAvg Bars Held:       {trades_df['BarsHeld'].mean():.1f}")
print("="*80)
