#!/bin/bash
# Master script to complete all report improvements

echo "=== Phase 4: Regenerating visualizations with stock counts ==="
python3.11 << 'EOFPYTHON'
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data with updated liquidity tiers
long_chars = pd.read_csv('part3_b2_long_stock_characteristics_updated.csv')
short_chars = pd.read_csv('part3_b2_short_stock_characteristics_updated.csv')
long_by_liq = pd.read_csv('part3_b4_long_by_liquidity_7tier.csv')
short_by_liq = pd.read_csv('part3_b4_short_by_liquidity_7tier.csv')
long_by_mcap = pd.read_csv('part3_b3_long_performance_by_mcap.csv')
short_by_mcap = pd.read_csv('part3_b3_short_performance_by_mcap.csv')
long_by_vol = pd.read_csv('part3_b5_long_performance_by_volatility.csv')
short_by_vol = pd.read_csv('part3_b5_short_performance_by_volatility.csv')

print("Regenerating visualizations with stock counts...")

# 1. Performance by Liquidity (7 tiers)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

tier_order = ['Very High', 'High', 'Medium-High', 'Medium', 'Medium-Low', 'Low', 'Very Low']
long_by_liq['Tier_Order'] = long_by_liq['Liquidity_Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)
short_by_liq['Tier_Order'] = short_by_liq['Liquidity_Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)
long_by_liq = long_by_liq.sort_values('Tier_Order')
short_by_liq = short_by_liq.sort_values('Tier_Order')

# LONG
bars1 = ax1.bar(range(len(long_by_liq)), long_by_liq['Total_PnL'], color='steelblue', alpha=0.7)
ax1.set_xticks(range(len(long_by_liq)))
ax1.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(long_by_liq['Liquidity_Tier'], long_by_liq['Stock_Count'])], 
                     rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Total PnL ($)', fontweight='bold')
ax1.set_title('LONG Strategy: Performance by Liquidity Tier', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

# SHORT
bars2 = ax2.bar(range(len(short_by_liq)), short_by_liq['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_liq)))
ax2.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(short_by_liq['Liquidity_Tier'], short_by_liq['Stock_Count'])], 
                     rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Total PnL ($)', fontweight='bold')
ax2.set_title('SHORT Strategy: Performance by Liquidity Tier', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

plt.tight_layout()
plt.savefig('part3_viz_performance_by_liquidity.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Liquidity tier visualization updated")

# 2. Performance by Market Cap
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# LONG
bars1 = ax1.bar(range(len(long_by_mcap)), long_by_mcap['Total_PnL'], color='steelblue', alpha=0.7)
ax1.set_xticks(range(len(long_by_mcap)))
ax1.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(long_by_mcap['Market_Cap_Category'], long_by_mcap['Stock_Count'])], 
                     rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Total PnL ($)', fontweight='bold')
ax1.set_title('LONG Strategy: Performance by Market Cap', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')

# SHORT
bars2 = ax2.bar(range(len(short_by_mcap)), short_by_mcap['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_mcap)))
ax2.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(short_by_mcap['Market_Cap_Category'], short_by_mcap['Stock_Count'])], 
                     rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Total PnL ($)', fontweight='bold')
ax2.set_title('SHORT Strategy: Performance by Market Cap', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('part3_viz_performance_by_mcap.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Market cap visualization updated")

# 3. Performance by Volatility
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# LONG
bars1 = ax1.bar(range(len(long_by_vol)), long_by_vol['Total_PnL'], color='steelblue', alpha=0.7)
ax1.set_xticks(range(len(long_by_vol)))
ax1.set_xticklabels([f"Q{int(q)}\n(n={int(c)})" for q, c in zip(long_by_vol['Volatility_Quintile'], long_by_vol['Stock_Count'])], 
                     fontsize=10)
ax1.set_ylabel('Total PnL ($)', fontweight='bold')
ax1.set_title('LONG Strategy: Performance by Volatility Quintile', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')

# SHORT
bars2 = ax2.bar(range(len(short_by_vol)), short_by_vol['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_vol)))
ax2.set_xticklabels([f"Q{int(q)}\n(n={int(c)})" for q, c in zip(short_by_vol['Volatility_Quintile'], short_by_vol['Stock_Count'])], 
                     fontsize=10)
ax2.set_ylabel('Total PnL ($)', fontweight='bold')
ax2.set_title('SHORT Strategy: Performance by Volatility Quintile', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('part3_viz_performance_by_volatility.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Volatility quintile visualization updated")

print("\n✓ All visualizations regenerated with stock counts")
EOFPYTHON

echo ""
echo "=== Phase 5: Creating analysis summaries ==="
cat > analysis_summaries.txt << 'EOFTEXT'
ANALYSIS SUMMARIES FOR REPORT

Section A1 - Performance Comparison:
The combined portfolio (LONG + SHORT) delivers 104.62% return, significantly outperforming either strategy alone (LONG: 46.74%, SHORT: 36.28%). This 2.2x improvement demonstrates strong diversification benefits from the low correlation (0.0516) between strategies.

Section A2 - Combined Portfolio Simulation:
Running both strategies with shared $1M capital and 10-position limit yields exceptional risk-adjusted returns (Sharpe 9.87) with minimal drawdown (-0.89%). The portfolio maintains near-full position utilization, suggesting efficient capital deployment across complementary signal types.

Section A3 - Correlation Analysis:
Daily returns correlation of 0.0516 indicates the strategies respond to different market conditions. LONG captures momentum trends while SHORT exploits mean reversion, providing natural hedging without explicit correlation management.

Section A4 - Trade Distribution:
LONG signals distribute relatively evenly throughout trading hours with slight concentration during mid-day (10am-2pm EST). SHORT signals show higher temporal clustering, explaining the lower signal utilization rate (2.4% vs 52.6% for LONG).

Section A5 - Symbol Analysis:
Of 400 total symbols, 208 (52%) appear in both strategies, indicating moderate overlap. The remaining 192 LONG-only symbols contribute to portfolio diversification and explain why LONG dominates the combined portfolio allocation.

Section B3 - Performance by Market Cap:
Medium-tier market cap stocks ($20B-$50B range) generate highest absolute PnL for LONG strategy. SHORT strategy shows more uniform performance across market cap tiers, suggesting the mean-reversion approach is less sensitive to company size.

Section B4 - Performance by Liquidity Tier:
Medium liquidity tier (T4) delivers strongest performance for both strategies. Very High liquidity stocks underperform despite lower execution risk, possibly due to increased efficiency and reduced mispric ing opportunities in heavily-traded names.

Section B5 - Performance by Volatility:
LONG strategy performs best in moderate volatility quintiles (Q2-Q3), consistent with momentum strategies that benefit from trending moves without excessive noise. SHORT strategy shows resilience across all volatility levels, with strongest performance in medium volatility (Q3).

Section B6 - Top vs Bottom Performers:
Top 20 performers average $11,641 PnL (LONG) and $35,858 (SHORT), while bottom 20 average -$3,421 (LONG) and -$1,847 (SHORT). Top performers exhibit higher liquidity scores and more moderate volatility, suggesting these characteristics enable better strategy execution.

Section B7 - Capital Deployment Capacity:
Combined maximum capacity of $133.5M (67x current deployment) indicates massive scaling potential. Current 0.75% utilization suggests the strategy can accommodate institutional capital without significant market impact, assuming execution quality is maintained.

Section B8 - Stock Exclusion Recommendations:
Excluding 127 LONG symbols (negative risk-adjusted returns) reduces trade count by 27% while improving win rate and Sharpe ratio. For SHORT, excluding 12 symbols has minimal impact but reduces tail risk. Exclusions prioritize risk management over absolute PnL maximization.
EOFTEXT

echo "✓ Analysis summaries created"

echo ""
echo "=== All improvements completed ===" 
echo "Ready for final report generation"
