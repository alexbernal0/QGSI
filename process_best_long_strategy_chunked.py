"""
Process ALL LONG signals with BEST strategy (ATR Trailing Stop) - CHUNKED VERSION
Process symbols in small batches, save incrementally to avoid memory issues

Best Parameters: ATR(30), Multiplier 5.0×
Expected Performance: +$1,281K, PF 1.087, Win 50.6%
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime
import os

# Import strategy function
sys.path.append('/home/ubuntu/stage4_optimization')
from BEST_LONG_STRATEGY_ATR_Trailing_Stop import backtest_long_trailing

def process_symbol_batch(symbols_batch, df_full):
    """Process a batch of symbols and return trades."""
    batch_trades = []
    
    for symbol in symbols_batch:
        # Get symbol data
        symbol_df = df_full[df_full['Symbol'] == symbol].sort_values('Date').reset_index(drop=True)
        
        # Run backtest
        trades = backtest_long_trailing(
            df=symbol_df,
            symbol=symbol,
            atr_period=30,
            multiplier=5.0,
            max_bars=20,
            position_size=100000.0
        )
        
        if len(trades) > 0:
            batch_trades.append(trades)
    
    if batch_trades:
        return pd.concat(batch_trades, ignore_index=True)
    return pd.DataFrame()

def process_all_long_trades_chunked():
    """
    Process all LONG signals in chunks, saving incrementally.
    """
    print("=" * 80)
    print("PROCESSING BEST LONG STRATEGY: ATR Trailing Stop (CHUNKED)")
    print("Parameters: ATR(30), Multiplier 5.0×")
    print("=" * 80)
    
    # Load data
    print("\n[1/4] Loading dataset...")
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    df = pd.read_parquet(data_path)
    print(f"✓ Loaded {len(df):,} rows, {len(df['Symbol'].unique())} symbols")
    
    # Get unique symbols
    symbols = sorted(df['Symbol'].unique())
    print(f"✓ Processing {len(symbols)} symbols")
    
    # Process in small batches
    BATCH_SIZE = 5  # Smaller batches to conserve memory
    total_trades = 0
    chunk_files = []
    
    print(f"\n[2/4] Processing symbols in batches of {BATCH_SIZE}...")
    
    for batch_num in range(0, len(symbols), BATCH_SIZE):
        batch_symbols = symbols[batch_num:batch_num + BATCH_SIZE]
        
        # Process batch
        batch_trades = process_symbol_batch(batch_symbols, df)
        
        if len(batch_trades) > 0:
            # Save chunk immediately
            chunk_num = batch_num // BATCH_SIZE + 1
            chunk_path = f'/home/ubuntu/stage4_optimization/Best_Long_Chunk_{chunk_num:03d}.parquet'
            batch_trades.to_parquet(chunk_path, index=False)
            chunk_files.append(chunk_path)
            total_trades += len(batch_trades)
            
            # Progress update
            progress = min(batch_num + BATCH_SIZE, len(symbols))
            print(f"  Chunk {chunk_num}/{(len(symbols)-1)//BATCH_SIZE + 1}: "
                  f"Processed {progress}/{len(symbols)} symbols, "
                  f"{total_trades:,} trades so far, saved to chunk file")
            
            # Clear memory
            del batch_trades
    
    # Combine all chunks
    print(f"\n[3/4] Combining {len(chunk_files)} chunk files...")
    all_chunks = []
    for chunk_file in chunk_files:
        chunk_df = pd.read_parquet(chunk_file)
        all_chunks.append(chunk_df)
        print(f"  Loaded {chunk_file}: {len(chunk_df):,} trades")
    
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
    trades = process_all_long_trades_chunked()
