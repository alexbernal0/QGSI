"""
Streaming baseline backtest using pyarrow
Processes data in small batches to avoid memory issues
"""

import pyarrow.parquet as pq
import pandas as pd
import numpy as np

print("="*80)
print("BASELINE BACKTEST - STREAMING MODE")
print("Strategy: ATR Trailing Stop, ATR(30), Multiplier 5.0")
print("="*80)

# Configuration
ATR_PERIOD = 30
ATR_MULT = 5.0
MAX_BARS = 20
POSITION_SIZE = 100000

# Read parquet file metadata
print("\n[1/5] Reading file metadata...")
parquet_file = pq.ParquetFile('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
print(f"✓ File has {parquet_file.metadata.num_rows:,} rows")
print(f"✓ File has {parquet_file.num_row_groups} row groups")

# Process symbol by symbol
print("\n[2/5] Processing symbols...")

trade_log = []
processed_symbols = 0

# Read in batches
for batch in parquet_file.iter_batches(batch_size=50000):
    batch_df = batch.to_pandas()
    
    # Process each symbol in this batch
    for symbol in batch_df['Symbol'].unique():
        symbol_data = batch_df[batch_df['Symbol'] == symbol].sort_values('BarDate').copy()
        
        # Calculate ATR
        high_low = symbol_data['High'] - symbol_data['Low']
        high_close = np.abs(symbol_data['High'] - symbol_data['Close'].shift())
        low_close = np.abs(symbol_data['Low'] - symbol_data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        symbol_data['ATR'] = tr.ewm(alpha=1/ATR_PERIOD, adjust=False).mean()
        
        # Find LONG signals
        long_signals = symbol_data[symbol_data['Signal'] == 1]
        
        for _, signal_row in long_signals.iterrows():
            entry_date = signal_row['BarDate']
            
            # Get data from entry forward
            future_data = symbol_data[symbol_data['BarDate'] >= entry_date].copy()
            
            if len(future_data) == 0:
                continue
            
            # Entry
            entry_row = future_data.iloc[0]
            entry_price = entry_row['Close']
            initial_stop = entry_price - (entry_row['ATR'] * ATR_MULT)
            current_stop = initial_stop
            
            # Track position
            for i, (_, bar) in enumerate(future_data.iterrows()):
                # Update trailing stop
                new_stop = bar['Low'] - (bar['ATR'] * ATR_MULT)
                if new_stop > current_stop:
                    current_stop = new_stop
                
                # Check exit
                exit_reason = None
                exit_price = None
                
                if bar['Low'] <= current_stop:
                    exit_reason = 'STOP'
                    exit_price = current_stop
                elif i >= MAX_BARS:
                    exit_reason = 'TIME'
                    exit_price = bar['Close']
                
                if exit_reason:
                    shares = int(POSITION_SIZE / entry_price)
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
                        'BarsInTrade': i,
                        'ExitReason': exit_reason
                    })
                    break
        
        processed_symbols += 1
        if processed_symbols % 50 == 0:
            print(f"  Processed {processed_symbols} symbols, {len(trade_log):,} trades...")

print(f"✓ Processed {processed_symbols} symbols")
print(f"✓ Generated {len(trade_log):,} trades")

# Save results
print("\n[3/5] Saving trade log...")
trades_df = pd.DataFrame(trade_log)
trades_df.to_parquet('/home/ubuntu/stage4_optimization/Baseline_Long_All_Trades.parquet', index=False)
trades_df.to_csv('/home/ubuntu/stage4_optimization/Baseline_Long_All_Trades.csv', index=False)
print(f"✓ Trade log saved")

# Calculate performance
print("\n[4/5] Calculating performance...")
winning = trades_df[trades_df['NetProfit'] > 0]
losing = trades_df[trades_df['NetProfit'] < 0]

print(f"\n" + "="*80)
print("BASELINE PERFORMANCE")
print("="*80)
print(f"Total Trades:        {len(trades_df):,}")
print(f"Winning Trades:      {len(winning):,} ({len(winning)/len(trades_df)*100:.1f}%)")
print(f"Losing Trades:       {len(losing):,} ({len(losing)/len(trades_df)*100:.1f}%)")
print(f"Net Profit:          ${trades_df['NetProfit'].sum():,.2f}")
print(f"Gross Profit:        ${winning['NetProfit'].sum():,.2f}")
print(f"Gross Loss:          ${abs(losing['NetProfit'].sum()):,.2f}")
if len(losing) > 0:
    print(f"Profit Factor:       {winning['NetProfit'].sum()/abs(losing['NetProfit'].sum()):.3f}")
print(f"Avg Bars Held:       {trades_df['BarsInTrade'].mean():.1f}")
print("="*80)

print("\n✓ BASELINE BACKTEST COMPLETE")
