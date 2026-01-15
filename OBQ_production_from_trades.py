"""
OBQ Production Portfolio Simulator
Simulates portfolio constraints on existing trade logs
"""

import pandas as pd
import numpy as np

print("="*80)
print("OBQ PRODUCTION PORTFOLIO SIMULATOR - LONG STRATEGY")
print("="*80)

# Configuration
STARTING_CAPITAL = 1_000_000
MAX_POSITIONS = 10
POSITION_SIZE_PCT = 0.10

# Load existing trade logs
print("\n[1/4] Loading baseline trade logs...")
trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet')
print(f"✓ Loaded {len(trades):,} baseline trades")
print(f"  Date range: {trades['EntryDate'].min()} to {trades['ExitDate'].max()}")
print(f"  Symbols: {trades['Symbol'].nunique()}")

# Sort trades by entry date
trades = trades.sort_values('EntryDate').reset_index(drop=True)

# Simulate portfolio with constraints
print("\n[2/4] Simulating portfolio with constraints...")
print(f"  Starting capital: ${STARTING_CAPITAL:,.0f}")
print(f"  Max positions: {MAX_POSITIONS}")
print(f"  Position size: {POSITION_SIZE_PCT*100:.0f}% of equity")

current_equity = STARTING_CAPITAL
active_positions = {}  # {symbol: {trade_data}}
portfolio_trades = []
equity_curve = []

# Get all unique dates (both entry and exit)
all_dates = sorted(set(trades['EntryDate'].tolist() + trades['ExitDate'].tolist()))

for current_date in all_dates:
    # Process exits first
    symbols_to_exit = []
    for symbol, pos in list(active_positions.items()):
        if pos['ExitDate'] == current_date:
            # Calculate actual P&L based on position size taken
            actual_shares = pos['shares']
            actual_entry_value = pos['entry_value']
            actual_exit_value = pos['ExitPrice'] * actual_shares
            actual_net_profit = actual_exit_value - actual_entry_value
            
            # Return capital
            current_equity += actual_net_profit
            
            # Log portfolio trade
            portfolio_trades.append({
                'Symbol': symbol,
                'EntryDate': pos['EntryDate'],
                'EntryPrice': pos['EntryPrice'],
                'ExitDate': pos['ExitDate'],
                'ExitPrice': pos['ExitPrice'],
                'Shares': actual_shares,
                'EntryValue': actual_entry_value,
                'ExitValue': actual_exit_value,
                'NetProfit': actual_net_profit,
                'PctProfit': (actual_net_profit / actual_entry_value) * 100,
                'BarsHeld': pos['BarsHeld'],
                'ExitReason': pos['ExitReason']
            })
            
            symbols_to_exit.append(symbol)
    
    for symbol in symbols_to_exit:
        del active_positions[symbol]
    
    # Process new entries
    today_entries = trades[trades['EntryDate'] == current_date]
    
    for _, trade in today_entries.iterrows():
        symbol = trade['Symbol']
        
        # Check constraints
        if len(active_positions) >= MAX_POSITIONS:
            break  # Portfolio full
        
        if symbol in active_positions:
            continue  # Already have position
        
        # Calculate position size (10% of current equity)
        position_value = current_equity * POSITION_SIZE_PCT
        entry_price = trade['EntryPrice']
        shares = int(position_value / entry_price)
        
        if shares == 0:
            continue  # Not enough capital
        
        actual_entry_value = shares * entry_price
        
        # Enter position
        active_positions[symbol] = {
            'EntryDate': trade['EntryDate'],
            'EntryPrice': entry_price,
            'ExitDate': trade['ExitDate'],
            'ExitPrice': trade['ExitPrice'],
            'shares': shares,
            'entry_value': actual_entry_value,
            'BarsHeld': trade['BarsInTrade'],
            'ExitReason': trade['ExitReason']
        }
        
        # Deploy capital
        current_equity -= actual_entry_value
    
    # Record equity (cash + open position value)
    # For open positions, mark-to-market using current "price"
    # (We'll use entry price as proxy since we don't have intraday data)
    open_value = sum([pos['entry_value'] for pos in active_positions.values()])
    total_equity = current_equity + open_value
    
    equity_curve.append({
        'Date': current_date,
        'Equity': total_equity,
        'Cash': current_equity,
        'PositionValue': open_value,
        'NumPositions': len(active_positions)
    })

print(f"✓ Simulation complete")
print(f"  Portfolio trades executed: {len(portfolio_trades):,}")
print(f"  Trades skipped: {len(trades) - len(portfolio_trades):,}")

# Create DataFrames
print("\n[3/4] Calculating performance metrics...")
portfolio_df = pd.DataFrame(portfolio_trades)
equity_df = pd.DataFrame(equity_curve)

# Performance metrics
winning = portfolio_df[portfolio_df['NetProfit'] > 0]
losing = portfolio_df[portfolio_df['NetProfit'] < 0]
final_equity = equity_df['Equity'].iloc[-1]
total_return = ((final_equity - STARTING_CAPITAL) / STARTING_CAPITAL) * 100

print(f"\n" + "="*80)
print("PERFORMANCE SUMMARY")
print("="*80)
print(f"Starting Capital:    ${STARTING_CAPITAL:,.0f}")
print(f"Final Equity:        ${final_equity:,.2f}")
print(f"Net Profit:          ${final_equity - STARTING_CAPITAL:,.2f}")
print(f"Total Return:        {total_return:.2f}%")
print(f"\nTotal Trades:        {len(portfolio_df):,}")
print(f"Winning Trades:      {len(winning):,} ({len(winning)/len(portfolio_df)*100:.1f}%)")
print(f"Losing Trades:       {len(losing):,} ({len(losing)/len(portfolio_df)*100:.1f}%)")
print(f"\nGross Profit:        ${winning['NetProfit'].sum():,.2f}")
print(f"Gross Loss:          ${abs(losing['NetProfit'].sum()):,.2f}")
print(f"Profit Factor:       {winning['NetProfit'].sum()/abs(losing['NetProfit'].sum()):.3f}")
print(f"\nAvg Win:             ${winning['NetProfit'].mean():,.2f}")
print(f"Avg Loss:            ${abs(losing['NetProfit'].mean()):,.2f}")
print(f"Largest Win:         ${portfolio_df['NetProfit'].max():,.2f}")
print(f"Largest Loss:        ${portfolio_df['NetProfit'].min():,.2f}")
print(f"\nAvg Bars Held:       {portfolio_df['BarsHeld'].mean():.1f}")
print("="*80)

# Save results
print("\n[4/4] Saving results...")
portfolio_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.parquet', index=False)
portfolio_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.csv', index=False)
equity_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.parquet', index=False)
equity_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.csv', index=False)

print(f"✓ Files saved:")
print(f"  • OBQ_Production_Long_Trades.parquet ({len(portfolio_df):,} trades)")
print(f"  • OBQ_Production_Long_Equity.parquet ({len(equity_df):,} equity points)")

print("\n" + "="*80)
print("✓ SIMULATION COMPLETE")
print("="*80)
