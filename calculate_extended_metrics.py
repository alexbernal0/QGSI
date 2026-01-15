#!/usr/bin/env python3.11
"""
Calculate Extended Metrics for Production Portfolio
"""

import pandas as pd
import numpy as np
from extended_metrics import calculate_all_metrics, get_drawdowns, get_monthly_table

print("="*80)
print("CALCULATING EXTENDED PERFORMANCE METRICS")
print("="*80)

# Load equity curve
print("\n[1/3] Loading equity curve...")
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
equity_df['Timestamp'] = pd.to_datetime(equity_df['Timestamp'])
equity_df = equity_df.set_index('Timestamp').sort_index()

print(f"✓ Loaded {len(equity_df):,} equity points")
print(f"  Date range: {equity_df.index[0]} to {equity_df.index[-1]}")

# Calculate daily returns
print("\n[2/3] Calculating daily returns...")
# Resample to daily (take last equity value of each day)
daily_equity = equity_df['Equity'].resample('D').last().dropna()
daily_returns = daily_equity.pct_change().dropna()

print(f"✓ Calculated {len(daily_returns):,} daily returns")
print(f"  Mean daily return: {daily_returns.mean()*100:.4f}%")
print(f"  Std daily return: {daily_returns.std()*100:.4f}%")

# Calculate all metrics
print("\n[3/3] Calculating extended metrics...")
rf = 0.0  # Risk-free rate (can adjust if needed)
metrics = calculate_all_metrics(daily_returns, rf=rf)

print(f"✓ Calculated {len(metrics)} metrics")

# Get additional tables
drawdowns = get_drawdowns(daily_returns)
monthly_table = get_monthly_table(daily_returns)

# Save metrics to CSV
print("\nSaving results...")
metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Value'])
metrics_df.to_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv')
print(f"✓ Saved metrics: Production_Long_Extended_Metrics.csv")

# Save drawdowns
if len(drawdowns) > 0:
    drawdowns.to_csv('/home/ubuntu/stage4_optimization/Production_Long_Drawdowns.csv', index=False)
    print(f"✓ Saved drawdowns: Production_Long_Drawdowns.csv ({len(drawdowns)} periods)")

# Save monthly table
if len(monthly_table) > 0:
    monthly_table.to_csv('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Table.csv')
    print(f"✓ Saved monthly table: Production_Long_Monthly_Table.csv")

# Print summary
print("\n" + "="*80)
print("KEY METRICS SUMMARY")
print("="*80)

# Select key metrics to display
key_metrics = [
    'Cumulative Return',
    'CAGR',
    'Sharpe',
    'Sortino',
    'Calmar',
    'Max Drawdown',
    'Volatility (ann.)',
    'Profit Factor',
    'Payoff Ratio',
    'Kelly Criterion',
    'Win Days %',
    'Win Month %',
    'Best Month',
    'Worst Month',
    'Ulcer Index',
    'Recovery Factor'
]

for metric in key_metrics:
    if metric in metrics:
        value = metrics[metric]
        if isinstance(value, float):
            if abs(value) > 100:
                print(f"{metric:.<40} {value:>15,.2f}")
            else:
                print(f"{metric:.<40} {value:>15.4f}")
        else:
            print(f"{metric:.<40} {value:>15}")

print("="*80)
print("\n✓ Extended metrics calculation complete!")
