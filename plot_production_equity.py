#!/usr/bin/env python3.11
"""
Generate equity curve visualizations for production portfolio
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Load equity curve
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
equity_df['Timestamp'] = pd.to_datetime(equity_df['Timestamp'])

# Create figure with subplots
fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig.suptitle('Production Portfolio Performance - LONG Strategy\nMax 10 Positions | 10% Position Sizing | $1M Starting Capital', 
             fontsize=14, fontweight='bold')

# Plot 1: Equity Curve
ax1 = axes[0]
ax1.plot(equity_df['Timestamp'], equity_df['Equity'], linewidth=2, color='#2E86AB', label='Total Equity')
ax1.axhline(y=1_000_000, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Starting Capital')
ax1.set_ylabel('Equity ($)', fontsize=11, fontweight='bold')
ax1.set_title('Portfolio Equity Curve', fontsize=12, fontweight='bold', pad=10)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper left')
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.2f}M'))

# Add final equity annotation
final_equity = equity_df['Equity'].iloc[-1]
final_date = equity_df['Timestamp'].iloc[-1]
ax1.annotate(f'Final: ${final_equity:,.0f}',
             xy=(final_date, final_equity),
             xytext=(10, 10), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
             fontsize=10, fontweight='bold')

# Plot 2: Number of Positions
ax2 = axes[1]
ax2.fill_between(equity_df['Timestamp'], equity_df['NumPositions'], 
                  alpha=0.5, color='#A23B72', label='Active Positions')
ax2.axhline(y=10, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Max Positions (10)')
ax2.set_ylabel('Number of Positions', fontsize=11, fontweight='bold')
ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
ax2.set_title('Portfolio Position Count', fontsize=12, fontweight='bold', pad=10)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper left')
ax2.set_ylim(0, 12)

# Format x-axis
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax2.xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/Production_Long_Equity_Curve.png', dpi=300, bbox_inches='tight')
print("✓ Equity curve saved: Production_Long_Equity_Curve.png")

# Create monthly returns chart
equity_df['Date'] = equity_df['Timestamp'].dt.date
daily_equity = equity_df.groupby('Date')['Equity'].last().reset_index()
daily_equity['Date'] = pd.to_datetime(daily_equity['Date'])
daily_equity['Month'] = daily_equity['Date'].dt.to_period('M')

monthly_returns = []
for month in daily_equity['Month'].unique():
    month_data = daily_equity[daily_equity['Month'] == month]
    if len(month_data) > 0:
        start_equity = month_data['Equity'].iloc[0]
        end_equity = month_data['Equity'].iloc[-1]
        monthly_return = ((end_equity - start_equity) / start_equity) * 100
        monthly_returns.append({
            'Month': str(month),
            'Return': monthly_return
        })

monthly_df = pd.DataFrame(monthly_returns)

# Plot monthly returns
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['green' if x >= 0 else 'red' for x in monthly_df['Return']]
bars = ax.bar(monthly_df['Month'], monthly_df['Return'], color=colors, alpha=0.7, edgecolor='black')

ax.axhline(y=0, color='black', linewidth=1)
ax.set_ylabel('Return (%)', fontsize=11, fontweight='bold')
ax.set_xlabel('Month', fontsize=11, fontweight='bold')
ax.set_title('Monthly Returns - Production Portfolio (LONG Strategy)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%',
            ha='center', va='bottom' if height >= 0 else 'top',
            fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Returns.png', dpi=300, bbox_inches='tight')
print("✓ Monthly returns saved: Production_Long_Monthly_Returns.png")

print("\nVisualization complete!")
