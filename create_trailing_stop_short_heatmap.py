"""
Generate heatmap for ATR Trailing Stop SHORT
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')

# Load data
df = pd.read_csv(OUTPUT_DIR / 'ATR_Trailing_Stop_Short_Performance.csv')

# Create simple bar chart (only 8 values, not enough for heatmap)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Bar chart of Net Profit
multipliers = df['Multiplier'].values
net_profits = df['NetProfit'].values
colors = ['green' if x > 0 else 'red' for x in net_profits]

ax1.bar(range(len(multipliers)), net_profits, color=colors, alpha=0.7, edgecolor='black')
ax1.set_xticks(range(len(multipliers)))
ax1.set_xticklabels([f'{m:.1f}×' for m in multipliers], fontsize=11)
ax1.set_xlabel('ATR Multiplier', fontsize=13, fontweight='bold')
ax1.set_ylabel('Net Profit ($)', fontsize=13, fontweight='bold')
ax1.set_title('ATR Trailing Stop SHORT - Net Profit by Multiplier', fontsize=14, fontweight='bold', pad=15)
ax1.grid(axis='y', alpha=0.3)
ax1.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Add value labels
for i, (mult, profit) in enumerate(zip(multipliers, net_profits)):
    ax1.text(i, profit, f'${profit/1000:.0f}K', ha='center', 
             va='bottom' if profit > 0 else 'top', fontsize=10, fontweight='bold')

# Profit Factor chart
pfs = df['ProfitFactor'].values
ax2.plot(range(len(multipliers)), pfs, marker='o', linewidth=2, markersize=8, color='navy')
ax2.set_xticks(range(len(multipliers)))
ax2.set_xticklabels([f'{m:.1f}×' for m in multipliers], fontsize=11)
ax2.set_xlabel('ATR Multiplier', fontsize=13, fontweight='bold')
ax2.set_ylabel('Profit Factor', fontsize=13, fontweight='bold')
ax2.set_title('ATR Trailing Stop SHORT - Profit Factor by Multiplier', fontsize=14, fontweight='bold', pad=15)
ax2.grid(alpha=0.3)
ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Breakeven (PF=1.0)')
ax2.legend(fontsize=10)

# Add value labels
for i, (mult, pf) in enumerate(zip(multipliers, pfs)):
    ax2.text(i, pf, f'{pf:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'ATR_Trailing_Stop_Short_Charts.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Saved: ATR_Trailing_Stop_Short_Charts.png")
