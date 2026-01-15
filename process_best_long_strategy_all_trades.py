"""
Process ALL LONG signals with BEST strategy (ATR Trailing Stop)
Generate complete trade logs for all ~80K signals across 400 stocks
Save to parquet and upload to MotherDuck

Best Parameters: ATR(30), Multiplier 5.0×
Expected Performance: +$1,281K, PF 1.087, Win 50.6%
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime

# Import strategy function
sys.path.append('/home/ubuntu/stage4_optimization')
from BEST_LONG_STRATEGY_ATR_Trailing_Stop import backtest_long_trailing

def process_all_long_trades():
    """
    Process all LONG signals with best ATR Trailing Stop strategy.
    Save results to parquet file in batches.
    """
    print("=" * 80)
    print("PROCESSING BEST LONG STRATEGY: ATR Trailing Stop")
    print("Parameters: ATR(30), Multiplier 5.0×")
    print("=" * 80)
    
    # Load data
    print("\n[1/5] Loading dataset...")
    data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
    df = pd.read_parquet(data_path)
    print(f"✓ Loaded {len(df):,} rows, {len(df['Symbol'].unique())} symbols")
    
    # Filter LONG signals only
    long_signals = df[df['Signal'] == 1].copy()
    print(f"✓ Found {len(long_signals):,} LONG signals")
    
    # Get unique symbols
    symbols = sorted(df['Symbol'].unique())
    print(f"✓ Processing {len(symbols)} symbols")
    
    # Process in batches
    BATCH_SIZE = 10
    all_trades = []
    total_trades = 0
    
    print(f"\n[2/5] Processing symbols in batches of {BATCH_SIZE}...")
    
    for batch_num in range(0, len(symbols), BATCH_SIZE):
        batch_symbols = symbols[batch_num:batch_num + BATCH_SIZE]
        batch_trades = []
        
        for symbol in batch_symbols:
            # Get symbol data
            symbol_df = df[df['Symbol'] == symbol].sort_values('Date').reset_index(drop=True)
            
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
        
        # Combine batch trades
        if batch_trades:
            batch_df = pd.concat(batch_trades, ignore_index=True)
            all_trades.append(batch_df)
            total_trades += len(batch_df)
            
            # Progress update
            progress = min(batch_num + BATCH_SIZE, len(symbols))
            print(f"  Batch {batch_num//BATCH_SIZE + 1}/{(len(symbols)-1)//BATCH_SIZE + 1}: "
                  f"Processed {progress}/{len(symbols)} symbols, "
                  f"{total_trades:,} trades so far")
    
    # Combine all trades
    print(f"\n[3/5] Combining all trades...")
    final_trades = pd.concat(all_trades, ignore_index=True)
    print(f"✓ Total trades: {len(final_trades):,}")
    
    # Calculate summary statistics
    print(f"\n[4/5] Calculating summary statistics...")
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
    
    # Save to parquet
    print(f"\n[5/5] Saving results...")
    output_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet'
    final_trades.to_parquet(output_path, index=False)
    file_size_mb = pd.io.common.file_exists(output_path)
    print(f"✓ Saved to: {output_path}")
    
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
    trades = process_all_long_trades()
