#!/usr/bin/env python3.11
"""
Regenerate SHORT equity curve to match LONG format
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

print("Regenerating SHORT equity curve...")

# Load data
equity_df = pd.read_parquet('Production_Short_Equity.parquet')
trades_df = pd.read_parquet('Production_Short_Trades.parquet')

# Convert to datetime
equity_df['Timestamp'] = pd.to_datetime(equity_df['Timestamp'])
equity_df['Date'] = equity_df['Timestamp'].dt.date
trades_df['EntryTime'] = pd.to_datetime(trades_df['EntryTime'])
trades_df['ExitTime'] = pd.to_datetime(trades_df['ExitTime'])

# Get daily equity (end of day)
daily_equity = equity_df.groupby('Date').agg({'Equity': 'last', 'Timestamp': 'last'}).reset_index()
daily_equity['Date'] = pd.to_datetime(daily_equity['Date'])

# Calculate position count over time (daily)
position_counts = []
for date in daily_equity['Date']:
    active = trades_df[
        (trades_df['EntryTime'].dt.date <= date.date()) & 
        (trades_df['ExitTime'].dt.date >= date.date())
    ].shape[0]
    position_counts.append(active)

daily_equity['Position_Count'] = position_counts

# Create figure with 3 subplots matching LONG format
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), 
                                      gridspec_kw={'height_ratios': [3, 1.5, 2]})

# Subplot 1: Equity curve
ax1.plot(daily_equity['Date'], daily_equity['Equity'], color='#d62728', linewidth=1.5, label='Total Equity')
ax1.axhline(y=1000000, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Starting Capital')
ax1.set_ylabel('Equity ($)', fontsize=11, fontweight='bold')
ax1.set_title('Production Portfolio Performance - SHORT Strategy\nMax 10 Positions | 10% Position Sizing | $1M Starting Capital\nPortfolio Equity Curve', 
              fontsize=12, fontweight='bold', pad=15)
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
final_equity = daily_equity['Equity'].iloc[-1]
ax1.text(0.98, 0.95, f'Final: ${final_equity:,.0f}', 
         transform=ax1.transAxes, fontsize=10, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
         verticalalignment='top', horizontalalignment='right')

# Subplot 2: Position count
ax2.fill_between(daily_equity['Date'], 0, daily_equity['Position_Count'], 
                  color='#ff9896', alpha=0.6, label='Active Positions')
ax2.axhline(y=10, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Max Positions (10)')
ax2.set_ylabel('Number of Positions', fontsize=10, fontweight='bold')
ax2.set_title('Portfolio Position Count', fontsize=11, fontweight='bold')
ax2.legend(loc='upper right', fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 12)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Subplot 3: Monthly returns
monthly_equity = daily_equity.set_index('Date')['Equity'].resample('M').last()
monthly_returns = monthly_equity.pct_change() * 100
monthly_returns = monthly_returns.dropna()

colors = ['green' if x > 0 else 'red' for x in monthly_returns]
ax3.bar(monthly_returns.index, monthly_returns.values, color=colors, alpha=0.7, width=20)
ax3.set_ylabel('Return (%)', fontsize=10, fontweight='bold')
ax3.set_xlabel('Month', fontsize=10, fontweight='bold')
ax3.set_title('Monthly Returns - Production Portfolio (SHORT Strategy)', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Add value labels on bars
for date, value in zip(monthly_returns.index, monthly_returns.values):
    ax3.text(date, value, f'{value:.1f}%', ha='center', 
             va='bottom' if value > 0 else 'top', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('Production_Short_Equity_Curve.png', dpi=300, bbox_inches='tight')
print("✓ SHORT equity curve regenerated successfully")
print(f"  Final equity: ${final_equity:,.0f}")
print(f"  Monthly returns: {len(monthly_returns)} months")
print(f"  Avg position count: {daily_equity['Position_Count'].mean():.1f}")
plt.close()
