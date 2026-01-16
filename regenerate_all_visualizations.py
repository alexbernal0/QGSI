#!/usr/bin/env python3.11
"""
Regenerate all Part III visualizations with stock counts (n=X) added
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("Regenerating all visualizations with stock counts...")

# Load data
long_chars = pd.read_csv('part3_b2_long_stock_characteristics_updated.csv')
short_chars = pd.read_csv('part3_b2_short_stock_characteristics_updated.csv')
long_by_liq = pd.read_csv('part3_b4_long_by_liquidity_7tier.csv')
short_by_liq = pd.read_csv('part3_b4_short_by_liquidity_7tier.csv')
long_by_mcap = pd.read_csv('part3_b3_long_performance_by_mcap.csv')
short_by_mcap = pd.read_csv('part3_b3_short_performance_by_mcap.csv')
long_by_vol = pd.read_csv('part3_b5_long_performance_by_volatility.csv')
short_by_vol = pd.read_csv('part3_b5_short_performance_by_volatility.csv')

# 1. Performance by Liquidity (7 tiers) - UPDATED
print("1. Generating liquidity tier visualization...")
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
ax1.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax1.set_title('LONG Strategy: Performance by Liquidity Tier (7 Tiers)', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
for i, (val, count) in enumerate(zip(long_by_liq['Total_PnL'], long_by_liq['Stock_Count'])):
    ax1.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

# SHORT
bars2 = ax2.bar(range(len(short_by_liq)), short_by_liq['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_liq)))
ax2.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(short_by_liq['Liquidity_Tier'], short_by_liq['Stock_Count'])], 
                     rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax2.set_title('SHORT Strategy: Performance by Liquidity Tier (7 Tiers)', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
for i, (val, count) in enumerate(zip(short_by_liq['Total_PnL'], short_by_liq['Stock_Count'])):
    ax2.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

plt.tight_layout()
plt.savefig('part3_viz_performance_by_liquidity.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Liquidity tier visualization")

# 2. Performance by Market Cap - UPDATED
print("2. Generating market cap visualization...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# LONG
bars1 = ax1.bar(range(len(long_by_mcap)), long_by_mcap['Total_PnL'], color='steelblue', alpha=0.7)
ax1.set_xticks(range(len(long_by_mcap)))
ax1.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(long_by_mcap['Market_Cap_Tier'], long_by_mcap['Num_Symbols'])], 
                     rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax1.set_title('LONG Strategy: Performance by Market Cap Category', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')
for i, val in enumerate(long_by_mcap['Total_PnL']):
    ax1.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

# SHORT
bars2 = ax2.bar(range(len(short_by_mcap)), short_by_mcap['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_mcap)))
ax2.set_xticklabels([f"{t}\n(n={int(c)})" for t, c in zip(short_by_mcap['Market_Cap_Tier'], short_by_mcap['Num_Symbols'])], 
                     rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax2.set_title('SHORT Strategy: Performance by Market Cap Category', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')
for i, val in enumerate(short_by_mcap['Total_PnL']):
    ax2.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

plt.tight_layout()
plt.savefig('part3_viz_performance_by_mcap.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Market cap visualization")

# 3. Performance by Volatility - UPDATED
print("3. Generating volatility quintile visualization...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# LONG
bars1 = ax1.bar(range(len(long_by_vol)), long_by_vol['Total_PnL'], color='steelblue', alpha=0.7)
ax1.set_xticks(range(len(long_by_vol)))
ax1.set_xticklabels([f"Q{int(q)}\n(n={int(c)})" for q, c in zip(long_by_vol['Volatility_Quintile'], long_by_vol['Num_Symbols'])], 
                     fontsize=10)
ax1.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax1.set_title('LONG Strategy: Performance by Volatility Quintile', fontweight='bold', fontsize=12)
ax1.set_xlabel('Quintile (Q1=Low Vol, Q5=High Vol)', fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')
for i, val in enumerate(long_by_vol['Total_PnL']):
    ax1.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

# SHORT
bars2 = ax2.bar(range(len(short_by_vol)), short_by_vol['Total_PnL'], color='coral', alpha=0.7)
ax2.set_xticks(range(len(short_by_vol)))
ax2.set_xticklabels([f"Q{int(q)}\n(n={int(c)})" for q, c in zip(short_by_vol['Volatility_Quintile'], short_by_vol['Num_Symbols'])], 
                     fontsize=10)
ax2.set_ylabel('Total PnL ($)', fontweight='bold', fontsize=11)
ax2.set_title('SHORT Strategy: Performance by Volatility Quintile', fontweight='bold', fontsize=12)
ax2.set_xlabel('Quintile (Q1=Low Vol, Q5=High Vol)', fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')
for i, val in enumerate(short_by_vol['Total_PnL']):
    ax2.text(i, val, f'${val:,.0f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=8)

plt.tight_layout()
plt.savefig('part3_viz_performance_by_volatility.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Volatility quintile visualization")

print("\n✓ All visualizations regenerated with stock counts (n=X)")
print("  - Liquidity: 7 tiers with counts")
print("  - Market Cap: Categories with counts")
print("  - Volatility: Quintiles with counts")
