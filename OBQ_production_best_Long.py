"""
OBQ Production Portfolio Simulator - LONG Strategy
Simulates real-world portfolio constraints with max 10 concurrent positions
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
POSITION_SIZE_PCT = 0.10  # 10% of current equity per position
ATR_PERIOD = 30
MULTIPLIER = 5.0
MAX_BARS = 20

# Load data from chunks
print("\n[1/6] Loading data from chunks...")
chunk_files = sorted([f for f in os.listdir('/home/ubuntu/stage4_optimization/data_chunks') 
                      if f.startswith('chunk_') and f.endswith('.parquet')])

all_data = []
for chunk_file in chunk_files:
    chunk_path = f'/home/ubuntu/stage4_optimization/data_chunks/{chunk_file}'
    df = pd.read_parquet(chunk_path)
    all_data.append(df)

data = pd.concat(all_data, ignore_index=True)
data = data.sort_values(['BarDate', 'Symbol']).reset_index(drop=True)

print(f"✓ Loaded {len(data):,} rows across {data['Symbol'].nunique()} symbols")
print(f"  Date range: {data['BarDate'].min()} to {data['BarDate'].max()}")

# Filter for LONG signals only
long_signals = data[data['Signal'] == 1].copy()
print(f"✓ Found {len(long_signals):,} LONG signals")

# Calculate ATR for all data
print("\n[2/6] Calculating ATR...")
def calculate_atr(df, period=14):
    """Calculate ATR using Wilder's method"""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    
    return atr

# Calculate ATR for each symbol
data_with_atr = []
for symbol in data['Symbol'].unique():
    symbol_data = data[data['Symbol'] == symbol].copy()
    symbol_data['ATR'] = calculate_atr(symbol_data, ATR_PERIOD)
    data_with_atr.append(symbol_data)

data = pd.concat(data_with_atr, ignore_index=True)
data = data.sort_values(['BarDate', 'Symbol']).reset_index(drop=True)

print(f"✓ ATR calculated for all symbols")

# Merge ATR into signals
long_signals = long_signals.merge(
    data[['Symbol', 'BarDate', 'ATR']], 
    on=['Symbol', 'BarDate'], 
    how='left'
)

# Sort signals by date, then by ATR (for tiebreaker)
long_signals = long_signals.sort_values(['BarDate', 'ATR'], ascending=[True, False]).reset_index(drop=True)

print(f"✓ Signals sorted by timestamp (ATR tiebreaker)")

# Portfolio simulation
print("\n[3/6] Running portfolio simulation...")

# Initialize portfolio state
current_equity = STARTING_CAPITAL
active_positions = {}  # {symbol: {entry_date, entry_price, stop, shares, bars_held}}
trade_log = []
equity_curve = []

# Get all unique dates
all_dates = sorted(data['BarDate'].unique())

for current_date in all_dates:
    # Get today's price data
    today_data = data[data['BarDate'] == current_date].set_index('Symbol')
    
    # Check exits first (process all active positions)
    symbols_to_exit = []
    for symbol, position in active_positions.items():
        if symbol not in today_data.index:
            continue
            
        row = today_data.loc[symbol]
        position['bars_held'] += 1
        
        # Check for exit conditions
        exit_reason = None
        exit_price = None
        
        # Update trailing stop
        new_stop = row['Low'] - (row['ATR'] * MULTIPLIER)
        if new_stop > position['stop']:
            position['stop'] = new_stop
        
        # Check if stopped out
        if row['Low'] <= position['stop']:
            exit_reason = 'STOP'
            exit_price = position['stop']
        
        # Check time limit
        elif position['bars_held'] >= MAX_BARS:
            exit_reason = 'TIME'
            exit_price = row['Close']
        
        # Process exit
        if exit_reason:
            exit_value = exit_price * position['shares']
            net_profit = exit_value - position['entry_value']
            pct_profit = (net_profit / position['entry_value']) * 100
            
            # Update equity
            current_equity += net_profit
            
            # Log trade
            trade_log.append({
                'Symbol': symbol,
                'EntryDate': position['entry_date'],
                'EntryPrice': position['entry_price'],
                'ExitDate': current_date,
                'ExitPrice': exit_price,
                'Shares': position['shares'],
                'EntryValue': position['entry_value'],
                'ExitValue': exit_value,
                'NetProfit': net_profit,
                'PctProfit': pct_profit,
                'BarsHeld': position['bars_held'],
                'ExitReason': exit_reason,
                'InitialStop': position['initial_stop'],
                'FinalStop': position['stop'],
                'StopMoved': position['stop'] - position['initial_stop']
            })
            
            symbols_to_exit.append(symbol)
    
    # Remove exited positions
    for symbol in symbols_to_exit:
        del active_positions[symbol]
    
    # Check for new entries (only if we have capacity)
    if len(active_positions) < MAX_POSITIONS:
        # Get today's signals
        today_signals = long_signals[long_signals['BarDate'] == current_date]
        
        for _, signal in today_signals.iterrows():
            symbol = signal['Symbol']
            
            # Check if we can enter
            if len(active_positions) >= MAX_POSITIONS:
                break  # Portfolio full
            
            if symbol in active_positions:
                continue  # Already have position in this symbol
            
            if symbol not in today_data.index:
                continue  # No price data
            
            row = today_data.loc[symbol]
            
            # Calculate position size (10% of current equity)
            position_value = current_equity * POSITION_SIZE_PCT
            entry_price = row['Close']
            shares = int(position_value / entry_price)
            
            if shares == 0:
                continue  # Not enough capital
            
            actual_position_value = shares * entry_price
            
            # Calculate initial stop
            initial_stop = entry_price - (row['ATR'] * MULTIPLIER)
            
            # Enter position
            active_positions[symbol] = {
                'entry_date': current_date,
                'entry_price': entry_price,
                'stop': initial_stop,
                'initial_stop': initial_stop,
                'shares': shares,
                'entry_value': actual_position_value,
                'bars_held': 0
            }
            
            # Deduct from equity (capital deployed)
            current_equity -= actual_position_value
    
    # Record equity curve
    # Current equity = cash + value of open positions
    open_position_value = sum([
        today_data.loc[symbol]['Close'] * pos['shares'] 
        for symbol, pos in active_positions.items()
        if symbol in today_data.index
    ])
    
    total_equity = current_equity + open_position_value
    
    equity_curve.append({
        'Date': current_date,
        'Equity': total_equity,
        'Cash': current_equity,
        'PositionValue': open_position_value,
        'NumPositions': len(active_positions)
    })

print(f"✓ Simulation complete")
print(f"  Total trades executed: {len(trade_log):,}")
print(f"  Final equity: ${total_equity:,.2f}")

# Convert to DataFrames
print("\n[4/6] Creating output files...")
trades_df = pd.DataFrame(trade_log)
equity_df = pd.DataFrame(equity_curve)

# Calculate performance metrics
if len(trades_df) > 0:
    winning_trades = trades_df[trades_df['NetProfit'] > 0]
    losing_trades = trades_df[trades_df['NetProfit'] < 0]
    
    total_net_profit = trades_df['NetProfit'].sum()
    gross_profit = winning_trades['NetProfit'].sum() if len(winning_trades) > 0 else 0
    gross_loss = abs(losing_trades['NetProfit'].sum()) if len(losing_trades) > 0 else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    
    print(f"\n✓ Performance Summary:")
    print(f"  Total Trades: {len(trades_df):,}")
    print(f"  Winning Trades: {len(winning_trades):,} ({len(winning_trades)/len(trades_df)*100:.1f}%)")
    print(f"  Losing Trades: {len(losing_trades):,} ({len(losing_trades)/len(trades_df)*100:.1f}%)")
    print(f"  Net Profit: ${total_net_profit:,.2f}")
    print(f"  Profit Factor: {profit_factor:.3f}")
    print(f"  Total Return: {((total_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100):.2f}%")

# Save outputs
print("\n[5/6] Saving files...")

# Trade log
trades_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.parquet', index=False)
trades_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Trades.csv', index=False)
print(f"✓ Trade log saved ({len(trades_df):,} trades)")

# Equity curve
equity_df.to_parquet('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.parquet', index=False)
equity_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Equity.csv', index=False)
print(f"✓ Equity curve saved ({len(equity_df):,} points)")

# Summary statistics
summary = {
    'StartingCapital': STARTING_CAPITAL,
    'FinalEquity': total_equity,
    'TotalReturn': ((total_equity - STARTING_CAPITAL) / STARTING_CAPITAL * 100),
    'TotalTrades': len(trades_df),
    'WinningTrades': len(winning_trades),
    'LosingTrades': len(losing_trades),
    'WinRate': (len(winning_trades) / len(trades_df) * 100) if len(trades_df) > 0 else 0,
    'NetProfit': total_net_profit,
    'GrossProfit': gross_profit,
    'GrossLoss': gross_loss,
    'ProfitFactor': profit_factor,
    'AvgWin': winning_trades['NetProfit'].mean() if len(winning_trades) > 0 else 0,
    'AvgLoss': losing_trades['NetProfit'].mean() if len(losing_trades) > 0 else 0,
    'LargestWin': trades_df['NetProfit'].max() if len(trades_df) > 0 else 0,
    'LargestLoss': trades_df['NetProfit'].min() if len(trades_df) > 0 else 0,
    'AvgBarsHeld': trades_df['BarsHeld'].mean() if len(trades_df) > 0 else 0,
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('/home/ubuntu/stage4_optimization/OBQ_Production_Long_Summary.csv', index=False)
print(f"✓ Summary statistics saved")

print("\n" + "="*80)
print("✓ SIMULATION COMPLETE")
print("="*80)
print(f"\nFiles created:")
print(f"  • OBQ_Production_Long_Trades.parquet")
print(f"  • OBQ_Production_Long_Trades.csv")
print(f"  • OBQ_Production_Long_Equity.parquet")
print(f"  • OBQ_Production_Long_Equity.csv")
print(f"  • OBQ_Production_Long_Summary.csv")
