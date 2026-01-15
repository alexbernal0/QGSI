#!/usr/bin/env python3.11
"""
Prepare SHORT Baseline Trades for Production Portfolio Simulator
Convert existing SHORT trades to format compatible with FIFO processing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*80)
print("PREPARING SHORT BASELINE TRADES FOR PRODUCTION SIMULATOR")
print("="*80)

# Load existing SHORT trades
print("\n[1/4] Loading SHORT baseline trades...")
df = pd.read_parquet('/home/ubuntu/stage4_optimization/Best_Short_Strategy_ATR_Trailing_Trades.parquet')
print(f"✓ Loaded {len(df):,} trades")
print(f"  Columns: {list(df.columns)}")

# Check if we need to add timestamps
if 'EntryTime' not in df.columns:
    print("\n[2/4] Adding timestamps...")
    # Convert dates to timestamps
    # For intraday simulation, we'll use market open (9:30 AM) for entries
    # and various times throughout the day for exits based on bars in trade
    
    df['EntryTime'] = pd.to_datetime(df['EntryDate']) + pd.Timedelta(hours=9, minutes=30)
    
    # Exit time based on bars in trade (assuming 5-minute bars)
    # Each bar = 5 minutes
    df['ExitTime'] = df.apply(
        lambda row: pd.to_datetime(row['ExitDate']) + pd.Timedelta(hours=9, minutes=30) + pd.Timedelta(minutes=5*row['BarsInTrade']),
        axis=1
    )
    
    print(f"✓ Added EntryTime and ExitTime columns")
else:
    print("\n[2/4] Timestamps already exist")

# Verify required columns
print("\n[3/4] Verifying required columns...")
required_cols = ['Symbol', 'EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 
                 'InitialStop', 'ATR', 'BarsInTrade', 'NetProfit', 'Signal']

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"✗ Missing columns: {missing_cols}")
    raise ValueError(f"Missing required columns: {missing_cols}")
else:
    print(f"✓ All required columns present")

# Add MaxBars column if not present
if 'MaxBars' not in df.columns:
    df['MaxBars'] = 20  # From the strategy parameters

# Sort by entry time
df = df.sort_values('EntryTime').reset_index(drop=True)

# Save prepared baseline
print("\n[4/4] Saving prepared baseline...")
output_file = '/home/ubuntu/stage4_optimization/Baseline_Short_Trades.parquet'
df.to_parquet(output_file, index=False)
print(f"✓ Saved to: {output_file}")

# Print summary
print("\n" + "="*80)
print("BASELINE SHORT TRADES SUMMARY")
print("="*80)
print(f"Total Trades:          {len(df):,}")
print(f"Date Range:            {df['EntryTime'].min()} to {df['ExitTime'].max()}")
print(f"Total Net Profit:      ${df['NetProfit'].sum():,.2f}")
print(f"Win Rate:              {(df['NetProfit'] > 0).mean()*100:.2f}%")
print(f"Avg Bars in Trade:     {df['BarsInTrade'].mean():.1f}")
print(f"Strategy:              ATR Trailing Stop")
print(f"Signal:                SHORT")
print(f"Parameters:            Period=30, Multiplier=1.5, MaxBars=20")
print("="*80)

# Sample of first few trades
print("\nFirst 5 trades:")
print(df[['Symbol', 'EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'NetProfit']].head())

print("\n✓ SHORT baseline preparation complete!")
