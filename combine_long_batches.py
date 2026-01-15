"""
Combine all batch parquet files into final result
"""

import pandas as pd
import numpy as np
from datetime import datetime
import glob
import os

print("=" * 80)
print("COMBINING ALL LONG STRATEGY BATCH RESULTS")
print("=" * 80)

# Find all batch files
batch_files = sorted(glob.glob('/home/ubuntu/stage4_optimization/Best_Long_Subset_*.parquet'))
print(f"\n[1/3] Found {len(batch_files)} batch files")

if len(batch_files) == 0:
    print("✗ No batch files found!")
    exit(1)

# Load and combine
print(f"\n[2/3] Loading and combining batches...")
all_trades = []

for i, batch_file in enumerate(batch_files, 1):
    df = pd.read_parquet(batch_file)
    all_trades.append(df)
    if i % 10 == 0:
        print(f"  Loaded {i}/{len(batch_files)} batches...")

final_trades = pd.concat(all_trades, ignore_index=True)
print(f"✓ Combined {len(final_trades):,} total trades")

# Calculate summary statistics
print(f"\n[3/3] Calculating summary statistics...")
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

# Clean up batch files
print(f"\n✓ Cleaning up {len(batch_files)} batch files...")
for batch_file in batch_files:
    if os.path.exists(batch_file):
        os.remove(batch_file)
print(f"✓ Batch files removed")

print(f"\n{'='*80}")
print(f"✓ ALL PROCESSING COMPLETE!")
print(f"{'='*80}\n")
