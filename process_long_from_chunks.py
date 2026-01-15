"""
Process LONG signals from pre-split chunk files
Each chunk is small (~20-30MB) so no memory issues
"""

import pandas as pd
import numpy as np
import sys
import os
import glob
from datetime import datetime

# Import strategy function
sys.path.append('/home/ubuntu/stage4_optimization')
from BEST_LONG_STRATEGY_ATR_Trailing_Stop import backtest_long_trailing

def process_all_chunks():
    """Process all chunk files."""
    
    print("=" * 80)
    print("PROCESSING BEST LONG STRATEGY FROM CHUNKS")
    print("Parameters: ATR(30), Multiplier 5.0×")
    print("=" * 80)
    
    # Find all chunk files
    chunks_dir = '/home/ubuntu/stage4_optimization/data_chunks'
    chunk_files = sorted(glob.glob(f'{chunks_dir}/chunk_*.parquet'))
    
    print(f"\n[1/3] Found {len(chunk_files)} chunk files")
    
    if len(chunk_files) == 0:
        print("✗ No chunk files found!")
        return None
    
    # Process each chunk
    print(f"\n[2/3] Processing chunks...")
    all_trades = []
    total_trades = 0
    
    for chunk_num, chunk_file in enumerate(chunk_files, 1):
        # Load chunk
        df_chunk = pd.read_parquet(chunk_file)
        symbols_in_chunk = df_chunk['Symbol'].unique()
        
        # Process each symbol in chunk
        chunk_trades = []
        for symbol in symbols_in_chunk:
            symbol_df = df_chunk[df_chunk['Symbol'] == symbol].sort_values('BarDate').reset_index(drop=True)
            
            trades = backtest_long_trailing(
                df=symbol_df,
                symbol=symbol,
                atr_period=30,
                multiplier=5.0,
                max_bars=20,
                position_size=100000.0
            )
            
            if len(trades) > 0:
                chunk_trades.append(trades)
        
        # Combine chunk trades
        if chunk_trades:
            chunk_df = pd.concat(chunk_trades, ignore_index=True)
            all_trades.append(chunk_df)
            total_trades += len(chunk_df)
        
        # Progress
        print(f"  Chunk {chunk_num:2d}/{len(chunk_files)}: "
              f"{len(symbols_in_chunk)} symbols, "
              f"{total_trades:,} trades so far")
    
    # Combine all trades
    print(f"\n[3/3] Combining all results...")
    final_trades = pd.concat(all_trades, ignore_index=True)
    print(f"✓ Total trades: {len(final_trades):,}")
    
    # Calculate summary statistics
    print(f"\nCalculating summary statistics...")
    winning_trades = len(final_trades[final_trades['NetProfit'] > 0])
    losing_trades = len(final_trades[final_trades['NetProfit'] < 0])
    total_profit = final_trades['NetProfit'].sum()
    gross_profit = final_trades[final_trades['NetProfit'] > 0]['NetProfit'].sum()
    gross_loss = abs(final_trades[final_trades['NetProfit'] < 0]['NetProfit'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    win_rate = (winning_trades / len(final_trades)) * 100
    
    print(f"\n{'='*80}")
    print(f"FINAL SUMMARY STATISTICS")
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
    
    # Save final parquet
    output_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet'
    final_trades.to_parquet(output_path, index=False)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✓ Final parquet saved to: {output_path} ({file_size_mb:.1f} MB)")
    
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
    
    print(f"\n{'='*80}")
    print(f"✓ PROCESSING COMPLETE!")
    print(f"{'='*80}\n")
    
    return final_trades

if __name__ == "__main__":
    trades = process_all_chunks()
