#!/usr/bin/env python3.11
"""
Production Portfolio Simulator - SHORT Strategy
FIFO realistic backtesting with portfolio constraints
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("PRODUCTION PORTFOLIO SIMULATOR - SHORT STRATEGY")
print("="*80)

# Configuration
STARTING_CAPITAL = 1_000_000
MAX_POSITIONS = 10
POSITION_SIZE_PCT = 0.10  # 10% of current equity per position

# Load baseline trades
print("\n[1/5] Loading baseline SHORT trades...")
baseline = pd.read_parquet('/home/ubuntu/stage4_optimization/Baseline_Short_Trades.parquet')
baseline = baseline.sort_values(['EntryTime', 'ATR'], ascending=[True, False]).reset_index(drop=True)
print(f"✓ Loaded {len(baseline):,} baseline trades")
print(f"  Date range: {baseline['EntryTime'].min()} to {baseline['ExitTime'].max()}")

# Initialize portfolio state
print("\n[2/5] Initializing portfolio...")
current_equity = STARTING_CAPITAL
open_positions = {}  # symbol -> position dict
equity_curve = []
production_trades = []
skipped_signals = {'MaxPositions': 0, 'DuplicateSymbol': 0, 'InsufficientCapital': 0}

print(f"✓ Starting capital: ${STARTING_CAPITAL:,.2f}")
print(f"✓ Max positions: {MAX_POSITIONS}")
print(f"✓ Position sizing: {POSITION_SIZE_PCT*100:.0f}% of equity")

# Process baseline trades
print("\n[3/5] Processing trades with FIFO constraints...")
total_signals = len(baseline)
processed = 0
last_pct = 0

for idx, signal in baseline.iterrows():
    # Progress indicator
    processed += 1
    pct = int(processed / total_signals * 100)
    if pct >= last_pct + 10:
        print(f"  Progress: {pct}% ({processed:,}/{total_signals:,} signals)")
        last_pct = pct
    
    symbol = signal['Symbol']
    entry_time = signal['EntryTime']
    
    # Check if we can enter this position
    can_enter = True
    skip_reason = None
    
    # Check 1: Max positions
    if len(open_positions) >= MAX_POSITIONS:
        can_enter = False
        skip_reason = 'MaxPositions'
        skipped_signals['MaxPositions'] += 1
    
    # Check 2: Duplicate symbol
    elif symbol in open_positions:
        can_enter = False
        skip_reason = 'DuplicateSymbol'
        skipped_signals['DuplicateSymbol'] += 1
    
    # Check 3: Sufficient capital
    else:
        position_size_dollars = current_equity * POSITION_SIZE_PCT
        shares = int(position_size_dollars / signal['EntryPrice'])
        cost = shares * signal['EntryPrice']
        
        if cost > current_equity:
            can_enter = False
            skip_reason = 'InsufficientCapital'
            skipped_signals['InsufficientCapital'] += 1
    
    if can_enter:
        # Enter position
        position_size_dollars = current_equity * POSITION_SIZE_PCT
        shares = int(position_size_dollars / signal['EntryPrice'])
        cost = shares * signal['EntryPrice']
        
        # Store position
        open_positions[symbol] = {
            'EntryTime': entry_time,
            'EntryPrice': signal['EntryPrice'],
            'Shares': shares,
            'Cost': cost,
            'InitialStop': signal['InitialStop'],
            'ATR': signal['ATR'],
            'MaxBars': signal['MaxBars'],
            'ExitTime': signal['ExitTime'],
            'ExitPrice': signal['ExitPrice'],
            'NetProfit': signal['NetProfit'] * (shares / signal['Shares']) if signal['Shares'] > 0 else signal['NetProfit'],
            'BarsInTrade': signal['BarsInTrade']
        }
        
        # Record equity at entry
        equity_curve.append({
            'Timestamp': entry_time,
            'Equity': current_equity,
            'OpenPositions': len(open_positions),
            'Action': 'Entry'
        })
    
    # Check for exits at this timestamp
    symbols_to_exit = []
    for sym, pos in open_positions.items():
        if pos['ExitTime'] <= entry_time:
            symbols_to_exit.append(sym)
    
    # Process exits
    for sym in symbols_to_exit:
        pos = open_positions[sym]
        pnl = pos['NetProfit']
        current_equity += pnl
        
        # Record trade
        production_trades.append({
            'Symbol': sym,
            'EntryTime': pos['EntryTime'],
            'ExitTime': pos['ExitTime'],
            'EntryPrice': pos['EntryPrice'],
            'ExitPrice': pos['ExitPrice'],
            'Shares': pos['Shares'],
            'Cost': pos['Cost'],
            'NetProfit': pnl,
            'BarsInTrade': pos['BarsInTrade'],
            'InitialStop': pos['InitialStop'],
            'ATR': pos['ATR']
        })
        
        # Record equity at exit
        equity_curve.append({
            'Timestamp': pos['ExitTime'],
            'Equity': current_equity,
            'OpenPositions': len(open_positions) - 1,
            'Action': 'Exit'
        })
        
        # Remove position
        del open_positions[sym]

# Close any remaining open positions at final timestamp
print("\n[4/5] Closing remaining positions...")
final_time = baseline['ExitTime'].max()
for sym, pos in list(open_positions.items()):
    pnl = pos['NetProfit']
    current_equity += pnl
    
    production_trades.append({
        'Symbol': sym,
        'EntryTime': pos['EntryTime'],
        'ExitTime': final_time,
        'EntryPrice': pos['EntryPrice'],
        'ExitPrice': pos['ExitPrice'],
        'Shares': pos['Shares'],
        'Cost': pos['Cost'],
        'NetProfit': pnl,
        'BarsInTrade': pos['BarsInTrade'],
        'InitialStop': pos['InitialStop'],
        'ATR': pos['ATR']
    })
    
    equity_curve.append({
        'Timestamp': final_time,
        'Equity': current_equity,
        'OpenPositions': 0,
        'Action': 'Exit'
    })

print(f"✓ Closed {len(production_trades)} positions")

# Convert to DataFrames
trades_df = pd.DataFrame(production_trades)
equity_df = pd.DataFrame(equity_curve)

# Calculate performance metrics
print("\n[5/5] Calculating performance metrics...")
total_trades = len(trades_df)
winning_trades = (trades_df['NetProfit'] > 0).sum()
losing_trades = (trades_df['NetProfit'] < 0).sum()
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

gross_profit = trades_df[trades_df['NetProfit'] > 0]['NetProfit'].sum()
gross_loss = abs(trades_df[trades_df['NetProfit'] < 0]['NetProfit'].sum())
net_profit = trades_df['NetProfit'].sum()
profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf

avg_win = trades_df[trades_df['NetProfit'] > 0]['NetProfit'].mean() if winning_trades > 0 else 0
avg_loss = trades_df[trades_df['NetProfit'] < 0]['NetProfit'].mean() if losing_trades > 0 else 0
largest_win = trades_df['NetProfit'].max() if total_trades > 0 else 0
largest_loss = trades_df['NetProfit'].min() if total_trades > 0 else 0

final_equity = current_equity
total_return = ((final_equity - STARTING_CAPITAL) / STARTING_CAPITAL) * 100

# Calculate max drawdown
equity_df = equity_df.sort_values('Timestamp')
equity_df['Peak'] = equity_df['Equity'].cummax()
equity_df['Drawdown'] = (equity_df['Equity'] / equity_df['Peak'] - 1) * 100
max_drawdown = equity_df['Drawdown'].min()

# Summary statistics
summary = {
    'Strategy': 'ATR_Trailing_Stop',
    'Signal': 'SHORT',
    'StartingCapital': STARTING_CAPITAL,
    'FinalEquity': final_equity,
    'NetProfit': net_profit,
    'TotalReturn': total_return,
    'MaxPositions': MAX_POSITIONS,
    'PositionSizePct': POSITION_SIZE_PCT * 100,
    'TotalTrades': total_trades,
    'WinningTrades': winning_trades,
    'LosingTrades': losing_trades,
    'WinRate': win_rate,
    'GrossProfit': gross_profit,
    'GrossLoss': gross_loss,
    'ProfitFactor': profit_factor,
    'AvgWin': avg_win,
    'AvgLoss': avg_loss,
    'LargestWin': largest_win,
    'LargestLoss': largest_loss,
    'MaxDrawdown': max_drawdown,
    'AvgBarsInTrade': trades_df['BarsInTrade'].mean() if total_trades > 0 else 0,
    'BaselineSignals': total_signals,
    'SignalsSkipped_MaxPositions': skipped_signals['MaxPositions'],
    'SignalsSkipped_Duplicate': skipped_signals['DuplicateSymbol'],
    'SignalsSkipped_Capital': skipped_signals['InsufficientCapital']
}

# Save results
print("\nSaving results...")
trades_df.to_parquet('/home/ubuntu/stage4_optimization/Production_Short_Trades.parquet', index=False)
print(f"✓ Saved trades: Production_Short_Trades.parquet ({len(trades_df):,} trades)")

equity_df.to_parquet('/home/ubuntu/stage4_optimization/Production_Short_Equity.parquet', index=False)
print(f"✓ Saved equity curve: Production_Short_Equity.parquet ({len(equity_df):,} points)")

summary_df = pd.DataFrame([summary])
summary_df.to_csv('/home/ubuntu/stage4_optimization/Production_Short_Summary.csv', index=False)
print(f"✓ Saved summary: Production_Short_Summary.csv")

# Print results
print("\n" + "="*80)
print("PRODUCTION SHORT PORTFOLIO RESULTS")
print("="*80)
print(f"Starting Capital:          ${STARTING_CAPITAL:,.2f}")
print(f"Final Equity:              ${final_equity:,.2f}")
print(f"Net Profit:                ${net_profit:,.2f}")
print(f"Total Return:              {total_return:.2f}%")
print(f"Max Drawdown:              {max_drawdown:.2f}%")
print()
print(f"Total Trades:              {total_trades:,}")
print(f"Winning Trades:            {winning_trades:,} ({win_rate:.1f}%)")
print(f"Losing Trades:             {losing_trades:,}")
print(f"Profit Factor:             {profit_factor:.3f}")
print()
print(f"Gross Profit:              ${gross_profit:,.2f}")
print(f"Gross Loss:                ${gross_loss:,.2f}")
print(f"Average Win:               ${avg_win:,.2f}")
print(f"Average Loss:              ${avg_loss:,.2f}")
print(f"Largest Win:               ${largest_win:,.2f}")
print(f"Largest Loss:              ${largest_loss:,.2f}")
print()
print(f"Baseline Signals:          {total_signals:,}")
print(f"Signals Taken:             {total_trades:,} ({total_trades/total_signals*100:.1f}%)")
print(f"Skipped (Max Positions):   {skipped_signals['MaxPositions']:,}")
print(f"Skipped (Duplicate):       {skipped_signals['DuplicateSymbol']:,}")
print(f"Skipped (Capital):         {skipped_signals['InsufficientCapital']:,}")
print("="*80)

print("\n✓ Production SHORT portfolio simulation complete!")
