#!/usr/bin/env python3.11
"""
Production Portfolio Simulator - LONG Strategy
Simulates real-world portfolio constraints with max concurrent positions
Uses baseline trade log and applies portfolio-level constraints
"""

import pandas as pd
import numpy as np
from pathlib import Path
import gc

print("="*80)
print("PRODUCTION PORTFOLIO SIMULATOR - LONG STRATEGY")
print("="*80)

# Configuration
STARTING_CAPITAL = 1_000_000
MAX_POSITIONS = 10
POSITION_SIZE_PCT = 0.10  # 10% of current equity per position

# Load baseline trade log
print("\n[1/5] Loading baseline trade log...")
trades_file = "/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet"
baseline_trades = pd.read_parquet(trades_file)

print(f"✓ Loaded {len(baseline_trades):,} baseline trades")
print(f"  Unique symbols: {baseline_trades['Symbol'].nunique()}")
print(f"  Date range: {baseline_trades['EntryTime'].min()} to {baseline_trades['ExitTime'].max()}")

# Sort by entry time (first-come-first-served), then by ATR (tiebreaker)
baseline_trades = baseline_trades.sort_values(['EntryTime', 'EntryATR'], ascending=[True, False]).reset_index(drop=True)

print("\n[2/5] Running portfolio simulation...")
print(f"  Max positions: {MAX_POSITIONS}")
print(f"  Position size: {POSITION_SIZE_PCT*100:.0f}% of current equity")
print(f"  Starting capital: ${STARTING_CAPITAL:,.0f}")

# Portfolio state
current_equity = STARTING_CAPITAL
active_positions = {}  # {symbol: {entry_time, exit_time, entry_price, exit_price, shares, entry_value}}
portfolio_trades = []
equity_curve = []
skipped_signals = []

# Track equity at each timestamp
last_timestamp = None

for idx, trade in baseline_trades.iterrows():
    symbol = trade['Symbol']
    entry_time = trade['EntryTime']
    exit_time = trade['ExitTime']
    entry_price = trade['EntryPrice']
    exit_price = trade['ExitPrice']
    
    # Update equity curve at new timestamp
    if last_timestamp != entry_time:
        # Calculate total equity (cash + open positions marked to market)
        # For simplicity, we'll track equity at entry/exit points
        total_equity = current_equity + sum([pos['entry_value'] for pos in active_positions.values()])
        
        equity_curve.append({
            'Timestamp': entry_time,
            'Equity': total_equity,
            'Cash': current_equity,
            'NumPositions': len(active_positions)
        })
        
        last_timestamp = entry_time
    
    # Check for exits at this timestamp
    symbols_to_exit = []
    for sym, pos in active_positions.items():
        if pos['exit_time'] <= entry_time:
            symbols_to_exit.append(sym)
    
    # Process exits
    for sym in symbols_to_exit:
        pos = active_positions[sym]
        
        # Calculate P&L
        exit_value = pos['exit_price'] * pos['shares']
        net_profit = exit_value - pos['entry_value']
        pct_profit = (net_profit / pos['entry_value']) * 100
        
        # Return capital to equity
        current_equity += exit_value
        
        # Log trade
        portfolio_trades.append({
            'Symbol': sym,
            'EntryTime': pos['entry_time'],
            'ExitTime': pos['exit_time'],
            'EntryPrice': pos['entry_price'],
            'ExitPrice': pos['exit_price'],
            'Shares': pos['shares'],
            'EntryValue': pos['entry_value'],
            'ExitValue': exit_value,
            'NetProfit': net_profit,
            'PctProfit': pct_profit,
            'Direction': 'LONG'
        })
        
        del active_positions[sym]
    
    # Check if we can enter this trade
    can_enter = True
    skip_reason = None
    
    # Check 1: Portfolio at max capacity?
    if len(active_positions) >= MAX_POSITIONS:
        can_enter = False
        skip_reason = 'MaxPositions'
    
    # Check 2: Already have position in this symbol?
    elif symbol in active_positions:
        can_enter = False
        skip_reason = 'DuplicateSymbol'
    
    # Check 3: Enough capital?
    elif current_equity <= 0:
        can_enter = False
        skip_reason = 'NoCapital'
    
    # Enter trade if possible
    if can_enter:
        # Calculate position size (10% of current equity)
        position_value = current_equity * POSITION_SIZE_PCT
        shares = int(position_value / entry_price)
        
        if shares == 0:
            skip_reason = 'InsufficientCapital'
            skipped_signals.append({
                'Symbol': symbol,
                'EntryTime': entry_time,
                'Reason': skip_reason
            })
        else:
            actual_position_value = shares * entry_price
            
            # Enter position
            active_positions[symbol] = {
                'entry_time': entry_time,
                'exit_time': exit_time,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': shares,
                'entry_value': actual_position_value
            }
            
            # Deduct from equity
            current_equity -= actual_position_value
    else:
        skipped_signals.append({
            'Symbol': symbol,
            'EntryTime': entry_time,
            'Reason': skip_reason
        })
    
    # Progress update
    if idx % 5000 == 0:
        print(f"  Processed {idx:,}/{len(baseline_trades):,} signals... ({len(portfolio_trades)} trades taken)")

# Close any remaining positions at final timestamp
for sym, pos in active_positions.items():
    exit_value = pos['exit_price'] * pos['shares']
    net_profit = exit_value - pos['entry_value']
    pct_profit = (net_profit / pos['entry_value']) * 100
    
    current_equity += exit_value
    
    portfolio_trades.append({
        'Symbol': sym,
        'EntryTime': pos['entry_time'],
        'ExitTime': pos['exit_time'],
        'EntryPrice': pos['entry_price'],
        'ExitPrice': pos['exit_price'],
        'Shares': pos['shares'],
        'EntryValue': pos['entry_value'],
        'ExitValue': exit_value,
        'NetProfit': net_profit,
        'PctProfit': pct_profit,
        'Direction': 'LONG'
    })

print(f"\n✓ Simulation complete")
print(f"  Baseline signals: {len(baseline_trades):,}")
print(f"  Trades taken: {len(portfolio_trades):,}")
print(f"  Signals skipped: {len(skipped_signals):,}")

# Convert to DataFrames
print("\n[3/5] Calculating performance metrics...")
trades_df = pd.DataFrame(portfolio_trades)
equity_df = pd.DataFrame(equity_curve)
skipped_df = pd.DataFrame(skipped_signals)

# Calculate final equity
final_equity = current_equity

if len(trades_df) > 0:
    winning_trades = trades_df[trades_df['NetProfit'] > 0]
    losing_trades = trades_df[trades_df['NetProfit'] < 0]
    
    total_net_profit = trades_df['NetProfit'].sum()
    gross_profit = winning_trades['NetProfit'].sum() if len(winning_trades) > 0 else 0
    gross_loss = abs(losing_trades['NetProfit'].sum()) if len(losing_trades) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    print(f"Starting Capital:    ${STARTING_CAPITAL:>15,.2f}")
    print(f"Final Equity:        ${final_equity:>15,.2f}")
    print(f"Net Profit:          ${total_net_profit:>15,.2f}")
    print(f"Total Return:        {((final_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100):>15.2f}%")
    print(f"\nTotal Trades:        {len(trades_df):>15,}")
    print(f"Winning Trades:      {len(winning_trades):>15,} ({len(winning_trades)/len(trades_df)*100:.1f}%)")
    print(f"Losing Trades:       {len(losing_trades):>15,} ({len(losing_trades)/len(trades_df)*100:.1f}%)")
    print(f"\nGross Profit:        ${gross_profit:>15,.2f}")
    print(f"Gross Loss:          ${gross_loss:>15,.2f}")
    print(f"Profit Factor:       {profit_factor:>15.3f}")
    print(f"\nAvg Win:             ${winning_trades['NetProfit'].mean():>15,.2f}" if len(winning_trades) > 0 else "Avg Win:             $            0.00")
    print(f"Avg Loss:            ${losing_trades['NetProfit'].mean():>15,.2f}" if len(losing_trades) > 0 else "Avg Loss:            $            0.00")
    print(f"Largest Win:         ${trades_df['NetProfit'].max():>15,.2f}")
    print(f"Largest Loss:        ${trades_df['NetProfit'].min():>15,.2f}")
    print(f"\nSignals Skipped:     {len(skipped_signals):>15,}")
    print(f"  Max Positions:     {skipped_df[skipped_df['Reason']=='MaxPositions'].shape[0]:>15,}")
    print(f"  Duplicate Symbol:  {skipped_df[skipped_df['Reason']=='DuplicateSymbol'].shape[0]:>15,}")
    print(f"  Insufficient Cap:  {skipped_df[skipped_df['Reason']=='InsufficientCapital'].shape[0]:>15,}")
    print(f"{'='*80}")

# Save outputs
print("\n[4/5] Saving files...")

# Trade log
output_dir = Path("/home/ubuntu/stage4_optimization")
trades_df.to_parquet(output_dir / "Production_Long_Trades.parquet", index=False)
trades_df.to_csv(output_dir / "Production_Long_Trades.csv", index=False)
print(f"✓ Trade log saved ({len(trades_df):,} trades)")

# Equity curve
equity_df.to_parquet(output_dir / "Production_Long_Equity.parquet", index=False)
equity_df.to_csv(output_dir / "Production_Long_Equity.csv", index=False)
print(f"✓ Equity curve saved ({len(equity_df):,} points)")

# Skipped signals
skipped_df.to_parquet(output_dir / "Production_Long_Skipped.parquet", index=False)
skipped_df.to_csv(output_dir / "Production_Long_Skipped.csv", index=False)
print(f"✓ Skipped signals saved ({len(skipped_df):,} signals)")

# Summary statistics
if len(trades_df) > 0:
    summary = {
        'StartingCapital': STARTING_CAPITAL,
        'FinalEquity': final_equity,
        'NetProfit': total_net_profit,
        'TotalReturn': ((final_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100),
        'TotalTrades': len(trades_df),
        'WinningTrades': len(winning_trades),
        'LosingTrades': len(losing_trades),
        'WinRate': (len(winning_trades) / len(trades_df) * 100),
        'GrossProfit': gross_profit,
        'GrossLoss': gross_loss,
        'ProfitFactor': profit_factor,
        'AvgWin': winning_trades['NetProfit'].mean() if len(winning_trades) > 0 else 0,
        'AvgLoss': losing_trades['NetProfit'].mean() if len(losing_trades) > 0 else 0,
        'LargestWin': trades_df['NetProfit'].max(),
        'LargestLoss': trades_df['NetProfit'].min(),
        'BaselineSignals': len(baseline_trades),
        'SignalsSkipped': len(skipped_signals),
        'MaxPositions': MAX_POSITIONS,
        'PositionSizePct': POSITION_SIZE_PCT * 100
    }
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(output_dir / "Production_Long_Summary.csv", index=False)
    print(f"✓ Summary statistics saved")

print("\n[5/5] Complete!")
print(f"\n{'='*80}")
print("OUTPUT FILES")
print(f"{'='*80}")
print("  • Production_Long_Trades.parquet")
print("  • Production_Long_Trades.csv")
print("  • Production_Long_Equity.parquet")
print("  • Production_Long_Equity.csv")
print("  • Production_Long_Skipped.parquet")
print("  • Production_Long_Skipped.csv")
print("  • Production_Long_Summary.csv")
print(f"{'='*80}")
