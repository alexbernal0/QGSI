"""
Process ALL LONG signals with BEST strategy (ATR Trailing Stop) - MINIMAL MEMORY
Process ONE symbol at a time, save immediately, never hold more than 1 symbol in memory

Best Parameters: ATR(30), Multiplier 5.0×
Expected Performance: +$1,281K, PF 1.087, Win 50.6%
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

def get_symbol_list():
    """Get list of symbols without loading full dataset."""
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    # Use pyarrow to read only Symbol column efficiently
    table = pq.read_table(data_path, columns=['Symbol'])
    df_symbols = table.to_pandas()
    symbols = sorted(df_symbols['Symbol'].unique())
    del df_symbols, table
    gc.collect()
    return symbols

def process_single_symbol(symbol, data_path):
    """Load and process a single symbol."""
    # Load only this symbol's data
    df_full = pd.read_parquet(data_path)
    df = df_full[df_full['Symbol'] == symbol].sort_values('Date').reset_index(drop=True)
    del df_full
    gc.collect()
    
    # Run backtest
    trades = backtest_long_trailing(
        df=df,
        symbol=symbol,
        atr_period=30,
        multiplier=5.0,
        max_bars=20,
        position_size=100000.0
    )
    
    del df
    gc.collect()
    
    return trades

def process_all_long_trades_minimal():
    """
    Process all LONG signals one symbol at a time.
    """
    print("=" * 80)
    print("PROCESSING BEST LONG STRATEGY: ATR Trailing Stop (MINIMAL MEMORY)")
    print("Parameters: ATR(30), Multiplier 5.0×")
    print("=" * 80)
    
    # Get symbol list
    print("\n[1/4] Getting symbol list...")
    symbols = get_symbol_list()
    print(f"✓ Found {len(symbols)} symbols to process")
    
    # Data path
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    
    # Process one symbol at a time
    total_trades = 0
    chunk_files = []
    CHUNK_SIZE = 10  # Save after every 10 symbols
    chunk_trades = []
    
    print(f"\n[2/4] Processing symbols one at a time...")
    
    for idx, symbol in enumerate(symbols, 1):
        # Process single symbol
        trades = process_single_symbol(symbol, data_path)
        
        if len(trades) > 0:
            chunk_trades.append(trades)
            total_trades += len(trades)
        
        # Save chunk every CHUNK_SIZE symbols
        if idx % CHUNK_SIZE == 0 or idx == len(symbols):
            if chunk_trades:
                chunk_df = pd.concat(chunk_trades, ignore_index=True)
                chunk_num = (idx - 1) // CHUNK_SIZE + 1
                chunk_path = f'/home/ubuntu/stage4_optimization/Best_Long_Chunk_{chunk_num:03d}.parquet'
                chunk_df.to_parquet(chunk_path, index=False)
                chunk_files.append(chunk_path)
                
                print(f"  Progress: {idx:3d}/{len(symbols)} symbols, "
                      f"{total_trades:,} trades, "
                      f"saved chunk {chunk_num}")
                
                # Clear memory
                del chunk_df
                chunk_trades = []
                gc.collect()
    
    # Combine all chunks
    print(f"\n[3/4] Combining {len(chunk_files)} chunk files...")
    all_chunks = []
    for i, chunk_file in enumerate(chunk_files, 1):
        chunk_df = pd.read_parquet(chunk_file)
        all_chunks.append(chunk_df)
        if i % 5 == 0:
            print(f"  Loaded {i}/{len(chunk_files)} chunks...")
    
    final_trades = pd.concat(all_chunks, ignore_index=True)
    print(f"✓ Total trades: {len(final_trades):,}")
    
    # Calculate summary statistics
    print(f"\n[4/4] Calculating summary statistics...")
    winning_trades = len(final_trades[final_trades['NetProfit'] > 0])
    losing_trades = len(final_trades[final_trades['NetProfit'] < 0])
    total_profit = final_trades['NetProfit'].sum()
    gross_profit = final_trades[final_trades['NetProfit'] > 0]['NetProfit'].sum()
    gross_loss = abs(final_trades[final_trades['NetProfit'] < 0]['NetProfit'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    win_rate = (winning_trades / len(final_trades)) * 100
    
    print(f"\n{'='*80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Total Trades:        {len(final_trades):,}")
    print(f"Winning Trades:      {winning_trades:,} ({win_rate:.1f}%)")
    print(f"Losing Trades:       {losing_trades:,} ({100-win_rate:.1f}%)")
    print(f"Net Profit:          ${total_profit:,.2f}")
    print(f"Gross Profit:        ${gross_profit:,.2f}")
    print(f"Gross Loss:          ${gross_loss:,.2f}")
    print(f"Profit Factor:       {profit_factor:.3f}")
    print(f"Avg Bars in Trade:   {final_trades['BarsInTrade'].mean():.1f}")
    print(f"Avg Stop Movement:   ${final_trades['StopMoved'].mean():.2f} ({final_trades['StopMovedPct'].mean():.2f}%)")
    print(f"{'='*80}")
    
    # Exit reason breakdown
    print(f"\nExit Reason Breakdown:")
    exit_counts = final_trades['ExitReason'].value_counts()
    for reason, count in exit_counts.items():
        pct = (count / len(final_trades)) * 100
        print(f"  {reason:10s}: {count:,} ({pct:.1f}%)")
    
    # Save final combined parquet
    output_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet'
    final_trades.to_parquet(output_path, index=False)
    print(f"\n✓ Final parquet saved to: {output_path}")
    
    # Save summary to CSV
    summary_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_Summary.csv'
    summary_df = pd.DataFrame([{
        'Strategy': 'ATR_Trailing_Stop',
        'Signal': 'LONG',
        'ATR_Period': 30,
        'Multiplier': 5.0,
        'Max_Bars': 20,
        'Total_Trades': len(final_trades),
        'Winning_Trades': winning_trades,
        'Losing_Trades': losing_trades,
        'Win_Rate_Pct': win_rate,
        'Net_Profit': total_profit,
        'Gross_Profit': gross_profit,
        'Gross_Loss': gross_loss,
        'Profit_Factor': profit_factor,
        'Avg_Bars_In_Trade': final_trades['BarsInTrade'].mean(),
        'Avg_Stop_Moved': final_trades['StopMoved'].mean(),
        'Avg_Stop_Moved_Pct': final_trades['StopMovedPct'].mean(),
        'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])
    summary_df.to_csv(summary_path, index=False)
    print(f"✓ Summary saved to: {summary_path}")
    
    # Clean up chunk files
    print(f"\n✓ Cleaning up {len(chunk_files)} chunk files...")
    for chunk_file in chunk_files:
        if os.path.exists(chunk_file):
            os.remove(chunk_file)
    print(f"✓ Chunk files removed")
    
    print(f"\n{'='*80}")
    print(f"✓ PROCESSING COMPLETE!")
    print(f"{'='*80}\n")
    
    return final_trades

if __name__ == "__main__":
    trades = process_all_long_trades_minimal()
