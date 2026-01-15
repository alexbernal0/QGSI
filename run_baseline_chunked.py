#!/usr/bin/env python3.11
"""
Baseline Backtest - Chunked Processing
Process symbols in chunks, save after each chunk to avoid memory issues
"""

import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from pathlib import Path
import gc
import time

# Strategy parameters
ATR_PERIOD = 30
ATR_MULTIPLIER = 5.0
MAX_BARS = 20

# File paths
DATA_FILE = "/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet"
OUTPUT_DIR = Path("/home/ubuntu/stage4_optimization/chunks")
OUTPUT_DIR.mkdir(exist_ok=True)

def calculate_atr(df, period=14):
    """Calculate ATR"""
    high = df['High'].values
    low = df['Low'].values
    close = df['Close'].values
    
    tr = np.maximum(
        high - low,
        np.maximum(
            np.abs(high - np.roll(close, 1)),
            np.abs(low - np.roll(close, 1))
        )
    )
    tr[0] = high[0] - low[0]
    
    atr = pd.Series(tr).rolling(window=period, min_periods=1).mean().values
    return atr

def process_long_signals(df, atr_period=14, atr_mult=2.0, max_bars=20):
    """Process LONG signals with ATR Trailing Stop"""
    df = df.sort_values('BarDateTime').reset_index(drop=True)
    df['ATR'] = calculate_atr(df, atr_period)
    
    trades = []
    in_trade = False
    entry_idx = None
    entry_price = None
    highest_since_entry = None
    trailing_stop = None
    entry_atr = None
    
    for i in range(len(df)):
        if not in_trade:
            if df.loc[i, 'Signal'] == 1:  # Signal=1 for LONG
                in_trade = True
                entry_idx = i
                entry_price = df.loc[i, 'Close']
                entry_atr = df.loc[i, 'ATR']
                highest_since_entry = entry_price
                trailing_stop = entry_price - (atr_mult * entry_atr)
        else:
            bars_in_trade = i - entry_idx
            current_price = df.loc[i, 'Close']
            
            # Update highest price
            if current_price > highest_since_entry:
                highest_since_entry = current_price
                trailing_stop = highest_since_entry - (atr_mult * entry_atr)
            
            # Check exit conditions
            exit_triggered = False
            exit_reason = None
            exit_price = current_price
            
            # Max bars exit
            if bars_in_trade >= max_bars:
                exit_triggered = True
                exit_reason = 'MaxBars'
            # Trailing stop exit
            elif current_price <= trailing_stop:
                exit_triggered = True
                exit_reason = 'TrailingStop'
                exit_price = trailing_stop
            
            if exit_triggered:
                pnl = exit_price - entry_price
                pnl_pct = (pnl / entry_price) * 100
                
                trades.append({
                    'Symbol': df.loc[entry_idx, 'Symbol'],
                    'EntryTime': df.loc[entry_idx, 'BarDateTime'],
                    'ExitTime': df.loc[i, 'BarDateTime'],
                    'EntryPrice': entry_price,
                    'ExitPrice': exit_price,
                    'PnL': pnl,
                    'PnL_Pct': pnl_pct,
                    'BarsInTrade': bars_in_trade,
                    'ExitReason': exit_reason,
                    'EntryATR': entry_atr,
                    'Direction': 'LONG'
                })
                
                in_trade = False
                entry_idx = None
    
    return pd.DataFrame(trades)

def get_all_symbols():
    """Get list of all symbols from the parquet file"""
    pf = pq.ParquetFile(DATA_FILE)
    
    # Read just the Symbol column from first row group to get unique symbols
    symbols = set()
    for i in range(pf.num_row_groups):
        table = pf.read_row_group(i, columns=['Symbol'])
        symbols.update(table['Symbol'].to_pylist())
    
    return sorted(list(symbols))

def process_chunk(symbols_chunk, chunk_num, total_chunks):
    """Process a chunk of symbols"""
    print(f"\n{'='*80}")
    print(f"CHUNK {chunk_num}/{total_chunks}: Processing {len(symbols_chunk)} symbols")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    # Read data for these symbols only
    pf = pq.ParquetFile(DATA_FILE)
    
    all_trades = []
    processed = 0
    
    for rg_idx in range(pf.num_row_groups):
        table = pf.read_row_group(rg_idx)
        df_rg = table.to_pandas()
        
        # Filter to symbols in this chunk
        df_chunk = df_rg[df_rg['Symbol'].isin(symbols_chunk)]
        
        if len(df_chunk) == 0:
            continue
        
        # Process each symbol
        for symbol in df_chunk['Symbol'].unique():
            df_sym = df_chunk[df_chunk['Symbol'] == symbol].copy()
            
            if len(df_sym) > 0 and (df_sym['Signal'] == 1).sum() > 0:
                trades = process_long_signals(df_sym, ATR_PERIOD, ATR_MULTIPLIER, MAX_BARS)
                if len(trades) > 0:
                    all_trades.append(trades)
            
            processed += 1
            if processed % 10 == 0:
                print(f"  Processed {processed}/{len(symbols_chunk)} symbols in chunk...")
        
        del df_rg, df_chunk
        gc.collect()
    
    # Combine all trades
    if all_trades:
        df_trades = pd.concat(all_trades, ignore_index=True)
    else:
        df_trades = pd.DataFrame()
    
    # Save chunk
    chunk_file = OUTPUT_DIR / f"chunk_{chunk_num:03d}_trades.parquet"
    df_trades.to_parquet(chunk_file, index=False)
    
    elapsed = time.time() - start_time
    print(f"✓ Chunk {chunk_num} complete: {len(df_trades)} trades in {elapsed:.1f}s")
    print(f"  Saved to: {chunk_file}")
    
    return len(df_trades)

def main():
    print("="*80)
    print("BASELINE BACKTEST - CHUNKED PROCESSING")
    print(f"Strategy: ATR Trailing Stop, ATR({ATR_PERIOD}), Multiplier {ATR_MULTIPLIER}")
    print("="*80)
    
    # Get all symbols
    print("\n[1/4] Reading symbols...")
    all_symbols = get_all_symbols()
    print(f"✓ Found {len(all_symbols)} unique symbols")
    
    # Split into chunks
    CHUNK_SIZE = 40  # Process 40 symbols at a time
    chunks = [all_symbols[i:i+CHUNK_SIZE] for i in range(0, len(all_symbols), CHUNK_SIZE)]
    print(f"✓ Split into {len(chunks)} chunks of ~{CHUNK_SIZE} symbols each")
    
    # Process each chunk
    print("\n[2/4] Processing chunks...")
    total_trades = 0
    for i, chunk in enumerate(chunks, 1):
        trades_count = process_chunk(chunk, i, len(chunks))
        total_trades += trades_count
        gc.collect()
    
    print(f"\n✓ All chunks processed: {total_trades} total trades")
    
    # Combine all chunks
    print("\n[3/4] Combining chunks...")
    chunk_files = sorted(OUTPUT_DIR.glob("chunk_*_trades.parquet"))
    print(f"  Found {len(chunk_files)} chunk files")
    
    all_trades = []
    for cf in chunk_files:
        df = pd.read_parquet(cf)
        all_trades.append(df)
        print(f"  Loaded {cf.name}: {len(df)} trades")
    
    df_final = pd.concat(all_trades, ignore_index=True)
    df_final = df_final.sort_values('EntryTime').reset_index(drop=True)
    
    # Save final result
    print("\n[4/4] Saving final result...")
    output_file = "/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet"
    df_final.to_parquet(output_file, index=False)
    print(f"✓ Saved {len(df_final)} trades to: {output_file}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Trades: {len(df_final):,}")
    print(f"Total PnL: ${df_final['PnL'].sum():,.2f}")
    print(f"Win Rate: {(df_final['PnL'] > 0).mean() * 100:.1f}%")
    print(f"Avg PnL per Trade: ${df_final['PnL'].mean():,.2f}")
    print(f"Unique Symbols: {df_final['Symbol'].nunique()}")
    print("="*80)

if __name__ == "__main__":
    main()
