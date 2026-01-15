"""
Process SUBSET of LONG signals with BEST strategy (ATR Trailing Stop)
Run this script multiple times with different START_IDX to process all 400 symbols

Usage: python3.11 process_best_long_subset.py <start_idx> <end_idx>
Example: python3.11 process_best_long_subset.py 0 50  (processes symbols 0-49)

Best Parameters: ATR(30), Multiplier 5.0×
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime
import os
import gc
import pyarrow.parquet as pq

# Import strategy function
sys.path.append('/home/ubuntu/stage4_optimization')
from BEST_LONG_STRATEGY_ATR_Trailing_Stop import backtest_long_trailing

def get_all_symbols():
    """Get complete list of symbols."""
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    table = pq.read_table(data_path, columns=['Symbol'])
    df_symbols = table.to_pandas()
    symbols = sorted(df_symbols['Symbol'].unique())
    del df_symbols, table
    gc.collect()
    return symbols

def process_symbol_subset(start_idx, end_idx):
    """Process a subset of symbols."""
    
    print("=" * 80)
    print(f"PROCESSING BEST LONG STRATEGY: Symbols {start_idx} to {end_idx-1}")
    print("=" * 80)
    
    # Get all symbols
    print("\n[1/3] Getting symbol list...")
    all_symbols = get_all_symbols()
    print(f"✓ Total symbols available: {len(all_symbols)}")
    
    # Get subset
    subset_symbols = all_symbols[start_idx:end_idx]
    print(f"✓ Processing {len(subset_symbols)} symbols (index {start_idx} to {end_idx-1})")
    
    if len(subset_symbols) == 0:
        print("⚠ No symbols in this range!")
        return None
    
    # Load data (only once for this subset)
    print(f"\n[2/3] Loading data for subset...")
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    df_full = pd.read_parquet(data_path)
    df_subset = df_full[df_full['Symbol'].isin(subset_symbols)].copy()
    del df_full
    gc.collect()
    print(f"✓ Loaded {len(df_subset):,} rows for {len(subset_symbols)} symbols")
    
    # Process each symbol
    print(f"\n[3/3] Processing symbols...")
    all_trades = []
    
    for idx, symbol in enumerate(subset_symbols, 1):
        symbol_df = df_subset[df_subset['Symbol'] == symbol].sort_values('Date').reset_index(drop=True)
        
        trades = backtest_long_trailing(
            df=symbol_df,
            symbol=symbol,
            atr_period=30,
            multiplier=5.0,
            max_bars=20,
            position_size=100000.0
        )
        
        if len(trades) > 0:
            all_trades.append(trades)
        
        if idx % 10 == 0 or idx == len(subset_symbols):
            print(f"  Processed {idx}/{len(subset_symbols)} symbols...")
    
    # Combine trades
    if all_trades:
        final_trades = pd.concat(all_trades, ignore_index=True)
    else:
        final_trades = pd.DataFrame()
    
    print(f"\n✓ Total trades from this subset: {len(final_trades):,}")
    
    # Save subset result
    output_path = f'/home/ubuntu/stage4_optimization/Best_Long_Subset_{start_idx:03d}_{end_idx:03d}.parquet'
    final_trades.to_parquet(output_path, index=False)
    print(f"✓ Saved to: {output_path}")
    
    # Summary
    if len(final_trades) > 0:
        winning = len(final_trades[final_trades['NetProfit'] > 0])
        total_profit = final_trades['NetProfit'].sum()
        print(f"\nSubset Summary:")
        print(f"  Trades: {len(final_trades):,}")
        print(f"  Winners: {winning:,} ({winning/len(final_trades)*100:.1f}%)")
        print(f"  Net Profit: ${total_profit:,.2f}")
    
    print(f"\n{'='*80}\n")
    
    return final_trades

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3.11 process_best_long_subset.py <start_idx> <end_idx>")
        print("Example: python3.11 process_best_long_subset.py 0 50")
        sys.exit(1)
    
    start_idx = int(sys.argv[1])
    end_idx = int(sys.argv[2])
    
    process_symbol_subset(start_idx, end_idx)
