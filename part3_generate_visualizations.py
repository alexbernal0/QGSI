#!/usr/bin/env python3.11
"""
Part III - Generate All Visualizations
Creates charts and graphs for strategy comparison and stock analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PART III - GENERATING VISUALIZATIONS")
print("="*80)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

# ============================================================================
# SECTION A VISUALIZATIONS
# ============================================================================
print("\n[Section A: Strategy Comparison Visualizations]")

# A.2: Combined Portfolio Equity Curves
print("  → Combined portfolio equity curves...")
long_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
short_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Equity.parquet')
combined_equity = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_equity_curve.csv')

fig, ax = plt.subplots(figsize=(14, 7))
long_equity['Date'] = pd.to_datetime(long_equity['Timestamp']).dt.date
short_equity['Date'] = pd.to_datetime(short_equity['Timestamp']).dt.date
combined_equity['Date'] = pd.to_datetime(combined_equity['Timestamp']).dt.date

long_daily = long_equity.groupby('Date')['Equity'].last()
short_daily = short_equity.groupby('Date')['Equity'].last()
combined_daily = combined_equity.groupby('Date')['Equity'].last()

ax.plot(long_daily.index, long_daily.values, label='LONG Strategy', linewidth=2, color='#2E86AB')
ax.plot(short_daily.index, short_daily.values, label='SHORT Strategy', linewidth=2, color='#A23B72')
ax.plot(combined_daily.index, combined_daily.values, label='Combined Portfolio', linewidth=2.5, color='#F18F01', linestyle='--')
ax.axhline(y=1000000, color='gray', linestyle=':', alpha=0.5, label='Starting Capital')
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Equity ($)', fontsize=12, fontweight='bold')
ax.set_title('Combined Portfolio Performance: LONG + SHORT Strategies', fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_combined_equity_curves.png', dpi=300, bbox_inches='tight')
plt.close()

# A.3: Correlation Scatter Plot
print("  → Correlation scatter plot...")
corr_data = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a3_daily_returns_correlation.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot
ax1.scatter(corr_data['Long_Returns']*100, corr_data['Short_Returns']*100, alpha=0.5, s=30)
ax1.set_xlabel('LONG Daily Returns (%)', fontsize=11, fontweight='bold')
ax1.set_ylabel('SHORT Daily Returns (%)', fontsize=11, fontweight='bold')
ax1.set_title('Daily Returns Correlation', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

# Rolling correlation
ax2.plot(corr_data['Date'], corr_data['Rolling_Corr'], linewidth=2, color='#2E86AB')
ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
ax2.set_ylabel('30-Day Rolling Correlation', fontsize=11, fontweight='bold')
ax2.set_title('Rolling Correlation Over Time', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_correlation_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# A.4: Trade Distribution Heatmap
print("  → Trade distribution heatmap...")
trades_by_hour = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a4_trades_by_hour.csv', index_col=0)

fig, ax = plt.subplots(figsize=(12, 6))
trades_by_hour.plot(kind='bar', ax=ax, color=['#2E86AB', '#A23B72'])
ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Trades', fontsize=12, fontweight='bold')
ax.set_title('Trade Distribution by Hour of Day', fontsize=14, fontweight='bold')
ax.legend(['LONG', 'SHORT'], fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_trades_by_hour.png', dpi=300, bbox_inches='tight')
plt.close()

# A.5: Symbol Overlap Venn Diagram (using bar chart)
print("  → Symbol overlap visualization...")
symbol_summary = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a5_symbol_summary.csv')

fig, ax = plt.subplots(figsize=(10, 6))
categories = ['LONG Only', 'SHORT Only', 'Both Strategies']
values = [symbol_summary['LONG Only'].iloc[0], symbol_summary['SHORT Only'].iloc[0], symbol_summary['Both Strategies'].iloc[0]]
colors = ['#2E86AB', '#A23B72', '#F18F01']
bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Number of Symbols', fontsize=12, fontweight='bold')
ax.set_title('Symbol Overlap Between Strategies', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_symbol_overlap.png', dpi=300, bbox_inches='tight')
plt.close()

# A.6: Risk Contribution Pie Chart
print("  → Risk contribution pie chart...")
risk_contrib = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a6_risk_contribution.csv')

fig, ax = plt.subplots(figsize=(10, 7))
sizes = [risk_contrib['LONG Risk Contribution (%)'].iloc[0], risk_contrib['SHORT Risk Contribution (%)'].iloc[0]]
labels = [f"LONG\n{sizes[0]:.1f}%", f"SHORT\n{sizes[1]:.1f}%"]
colors = ['#2E86AB', '#A23B72']
explode = (0.05, 0.05)
ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='',
       shadow=True, startangle=90, textprops={'fontsize': 14, 'fontweight': 'bold'})
ax.set_title('Risk Contribution to 50/50 Portfolio', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_risk_contribution.png', dpi=300, bbox_inches='tight')
plt.close()

# A.7: Optimal Allocation Efficient Frontier
print("  → Optimal allocation efficient frontier...")
allocation_df = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a7_optimal_allocation.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Efficient frontier
ax1.plot(allocation_df['Volatility (%)'], allocation_df['Expected Return (%)'], 
         marker='o', linewidth=2, markersize=6, color='#2E86AB')
max_sharpe_idx = allocation_df['Sharpe Ratio'].idxmax()
ax1.scatter(allocation_df.loc[max_sharpe_idx, 'Volatility (%)'], 
           allocation_df.loc[max_sharpe_idx, 'Expected Return (%)'],
           color='red', s=200, marker='*', label='Max Sharpe', zorder=5)
ax1.set_xlabel('Volatility (%)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Expected Return (%)', fontsize=11, fontweight='bold')
ax1.set_title('Efficient Frontier', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Sharpe ratio by allocation
ax2.plot(allocation_df['LONG Weight (%)'], allocation_df['Sharpe Ratio'], 
         linewidth=2.5, color='#F18F01')
ax2.scatter(allocation_df.loc[max_sharpe_idx, 'LONG Weight (%)'], 
           allocation_df.loc[max_sharpe_idx, 'Sharpe Ratio'],
           color='red', s=200, marker='*', zorder=5)
ax2.set_xlabel('LONG Allocation (%)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Sharpe Ratio', fontsize=11, fontweight='bold')
ax2.set_title('Sharpe Ratio by Allocation', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_optimal_allocation.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# SECTION B VISUALIZATIONS
# ============================================================================
print("\n[Section B: Stock Characteristics Visualizations]")

# B.3: Performance by Market Cap
print("  → Performance by market cap...")
long_by_mcap = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b3_long_performance_by_mcap.csv')
short_by_mcap = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b3_short_performance_by_mcap.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Total PnL
x = np.arange(len(long_by_mcap))
width = 0.35
ax1.bar(x - width/2, long_by_mcap['Total_PnL'], width, label='LONG', color='#2E86AB')
ax1.bar(x + width/2, short_by_mcap['Total_PnL'], width, label='SHORT', color='#A23B72')
ax1.set_xlabel('Market Cap Tier', fontsize=11, fontweight='bold')
ax1.set_ylabel('Total PnL ($)', fontsize=11, fontweight='bold')
ax1.set_title('Total PnL by Market Cap', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(long_by_mcap['Market_Cap_Tier'], rotation=45, ha='right')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# Win Rate
ax2.bar(x - width/2, long_by_mcap['Win_Rate'], width, label='LONG', color='#2E86AB')
ax2.bar(x + width/2, short_by_mcap['Win_Rate'], width, label='SHORT', color='#A23B72')
ax2.set_xlabel('Market Cap Tier', fontsize=11, fontweight='bold')
ax2.set_ylabel('Win Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Win Rate by Market Cap', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(short_by_mcap['Market_Cap_Tier'], rotation=45, ha='right')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_performance_by_mcap.png', dpi=300, bbox_inches='tight')
plt.close()

# B.4: Performance by Liquidity Tier
print("  → Performance by liquidity tier...")
long_by_liq = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b4_long_performance_by_liquidity.csv')
short_by_liq = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b4_short_performance_by_liquidity.csv')

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(long_by_liq))
width = 0.35
ax.bar(x - width/2, long_by_liq['Total_PnL'], width, label='LONG', color='#2E86AB')
ax.bar(x + width/2, short_by_liq['Total_PnL'], width, label='SHORT', color='#A23B72')
ax.set_xlabel('Liquidity Tier', fontsize=12, fontweight='bold')
ax.set_ylabel('Total PnL ($)', fontsize=12, fontweight='bold')
ax.set_title('Performance by Liquidity Tier', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(long_by_liq['Liquidity_Tier'], rotation=45, ha='right')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_performance_by_liquidity.png', dpi=300, bbox_inches='tight')
plt.close()

# B.5: Performance by Volatility Quintile
print("  → Performance by volatility quintile...")
long_by_vol = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b5_long_performance_by_volatility.csv')
short_by_vol = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b5_short_performance_by_volatility.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Win Rate
ax1.plot(long_by_vol['Volatility_Quintile'], long_by_vol['Win_Rate'], marker='o', linewidth=2, markersize=8, label='LONG', color='#2E86AB')
ax1.plot(short_by_vol['Volatility_Quintile'], short_by_vol['Win_Rate'], marker='s', linewidth=2, markersize=8, label='SHORT', color='#A23B72')
ax1.set_xlabel('Volatility Quintile (0=Low, 4=High)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Win Rate (%)', fontsize=11, fontweight='bold')
ax1.set_title('Win Rate by Volatility', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Avg PnL per Trade
ax2.plot(long_by_vol['Volatility_Quintile'], long_by_vol['Avg_PnL_Per_Trade'], marker='o', linewidth=2, markersize=8, label='LONG', color='#2E86AB')
ax2.plot(short_by_vol['Volatility_Quintile'], short_by_vol['Avg_PnL_Per_Trade'], marker='s', linewidth=2, markersize=8, label='SHORT', color='#A23B72')
ax2.set_xlabel('Volatility Quintile (0=Low, 4=High)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Avg PnL per Trade ($)', fontsize=11, fontweight='bold')
ax2.set_title('Avg Profit by Volatility', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_performance_by_volatility.png', dpi=300, bbox_inches='tight')
plt.close()

# B.7: Capital Deployment Capacity
print("  → Capital deployment capacity...")
capacity_summary = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b7_capacity_summary.csv')

fig, ax = plt.subplots(figsize=(10, 6))
strategies = capacity_summary['Strategy']
capacity = capacity_summary['Total_Capacity']
current = capacity_summary['Current_Capital']

x = np.arange(len(strategies))
width = 0.35
bars1 = ax.bar(x - width/2, current, width, label='Current Capital', color='#F18F01')
bars2 = ax.bar(x + width/2, capacity, width, label='Max Capacity', color='#2E86AB')

ax.set_ylabel('Capital ($)', fontsize=12, fontweight='bold')
ax.set_title('Capital Deployment Capacity Analysis', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(strategies)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height/1e6:.1f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_capital_capacity.png', dpi=300, bbox_inches='tight')
plt.close()

# B.6: Top vs Bottom Performers Comparison
print("  → Top vs bottom performers comparison...")
long_comparison = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b6_long_top_vs_bottom_comparison.csv')
short_comparison = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b6_short_top_vs_bottom_comparison.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# LONG
x = np.arange(len(long_comparison))
width = 0.35
ax1.bar(x - width/2, long_comparison['Top 20'], width, label='Top 20', color='#2E86AB')
ax1.bar(x + width/2, long_comparison['Bottom 20'], width, label='Bottom 20', color='#A23B72')
ax1.set_ylabel('Value', fontsize=11, fontweight='bold')
ax1.set_title('LONG: Top 20 vs Bottom 20 Characteristics', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(long_comparison['Metric'], rotation=45, ha='right')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# SHORT
x = np.arange(len(short_comparison))
ax2.bar(x - width/2, short_comparison['Top 20'], width, label='Top 20', color='#2E86AB')
ax2.bar(x + width/2, short_comparison['Bottom 20'], width, label='Bottom 20', color='#A23B72')
ax2.set_ylabel('Value', fontsize=11, fontweight='bold')
ax2.set_title('SHORT: Top 20 vs Bottom 20 Characteristics', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(short_comparison['Metric'], rotation=45, ha='right')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/stage4_optimization/part3_viz_top_vs_bottom_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*80)
print("ALL VISUALIZATIONS GENERATED")
print("="*80)
print("\nFiles created:")
print("  Section A (Strategy Comparison):")
print("    - part3_viz_combined_equity_curves.png")
print("    - part3_viz_correlation_analysis.png")
print("    - part3_viz_trades_by_hour.png")
print("    - part3_viz_symbol_overlap.png")
print("    - part3_viz_risk_contribution.png")
print("    - part3_viz_optimal_allocation.png")
print("\n  Section B (Stock Characteristics):")
print("    - part3_viz_performance_by_mcap.png")
print("    - part3_viz_performance_by_liquidity.png")
print("    - part3_viz_performance_by_volatility.png")
print("    - part3_viz_capital_capacity.png")
print("    - part3_viz_top_vs_bottom_comparison.png")
print("="*80)
