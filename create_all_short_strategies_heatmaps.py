"""
Generate heatmaps with 3D surface plots for all SHORT strategies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')

# Strategy 1: Fixed ATR Symmetric
print("Generating Fixed ATR Symmetric SHORT heatmap...")
df_sym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Performance.csv')

# Create pivot table
pivot_sym = df_sym.pivot_table(
    values='NetProfit',
    index='ATRPeriod',
    columns='StopMultiplier',
    aggfunc='first'
)

fig = plt.figure(figsize=(20, 10))

# Heatmap
ax1 = fig.add_subplot(121)
im = ax1.imshow(pivot_sym.values, cmap='RdYlGn', aspect='auto', interpolation='nearest')
ax1.set_xticks(range(len(pivot_sym.columns)))
ax1.set_yticks(range(len(pivot_sym.index)))
ax1.set_xticklabels([f'{x:.1f}×' for x in pivot_sym.columns], fontsize=10)
ax1.set_yticklabels([f'ATR({int(y)})' for y in pivot_sym.index], fontsize=10)
ax1.set_xlabel('Stop/Target Multiplier', fontsize=12, fontweight='bold')
ax1.set_ylabel('ATR Period', fontsize=12, fontweight='bold')
ax1.set_title('Fixed ATR Symmetric SHORT - Net Profit Heatmap', fontsize=14, fontweight='bold', pad=20)

for i in range(len(pivot_sym.index)):
    for j in range(len(pivot_sym.columns)):
        value = pivot_sym.values[i, j]
        color = 'white' if value < -100000 or value > 100000 else 'black'
        ax1.text(j, i, f'${value/1000:.0f}K', ha='center', va='center', color=color, fontsize=9)

cbar = plt.colorbar(im, ax=ax1)
cbar.set_label('Net Profit ($)', fontsize=11, fontweight='bold')

# 3D Surface
ax2 = fig.add_subplot(122, projection='3d')
X, Y = np.meshgrid(range(len(pivot_sym.columns)), range(len(pivot_sym.index)))
Z = pivot_sym.values
surf = ax2.plot_surface(X, Y, Z, cmap='RdYlGn', alpha=0.8, edgecolor='none')
ax2.set_xlabel('Stop/Target Multiplier', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_ylabel('ATR Period', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_zlabel('Net Profit ($)', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_title('3D Surface Plot', fontsize=12, fontweight='bold', pad=20)
ax2.set_xticks(range(len(pivot_sym.columns)))
ax2.set_yticks(range(len(pivot_sym.index)))
ax2.set_xticklabels([f'{x:.1f}' for x in pivot_sym.columns], fontsize=8)
ax2.set_yticklabels([f'{int(y)}' for y in pivot_sym.index], fontsize=8)
ax2.view_init(elev=25, azim=45)
fig.colorbar(surf, ax=ax2, shrink=0.5, aspect=5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Heatmap_3D.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: Fixed_ATR_Symmetric_Short_Heatmap_3D.png")

# Strategy 2: Fixed ATR Asymmetric
print("\nGenerating Fixed ATR Asymmetric SHORT heatmap...")
df_asym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv')

atr_periods = sorted(df_asym['ATRPeriod'].unique())
fig, axes = plt.subplots(2, 2, figsize=(24, 18))
axes = axes.flatten()

for idx, atr_period in enumerate(atr_periods):
    df_atr = df_asym[df_asym['ATRPeriod'] == atr_period]
    
    pivot = df_atr.pivot_table(
        values='NetProfit',
        index='StopMultiplier',
        columns='TargetMultiplier',
        aggfunc='first'
    )
    
    ax = axes[idx]
    im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto', interpolation='nearest')
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels([f'{x:.1f}×' for x in pivot.columns], fontsize=11)
    ax.set_yticklabels([f'{y:.1f}×' for y in pivot.index], fontsize=11)
    ax.set_xlabel('Target Multiplier', fontsize=13, fontweight='bold')
    ax.set_ylabel('Stop Multiplier', fontsize=13, fontweight='bold')
    ax.set_title(f'ATR({int(atr_period)}) - Net Profit', fontsize=14, fontweight='bold', pad=15)
    
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.values[i, j]
            color = 'white' if value < -100000 or value > 200000 else 'black'
            ax.text(j, i, f'${value/1000:.0f}K', ha='center', va='center', color=color, fontsize=10, fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Net Profit ($)', fontsize=11, fontweight='bold')

plt.suptitle('Fixed ATR Asymmetric SHORT - Net Profit Heatmaps', fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.savefig(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Heatmap_4Panel.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: Fixed_ATR_Asymmetric_Short_Heatmap_4Panel.png")

# Strategy 3: ATR Breakeven Stop
print("\nGenerating ATR Breakeven Stop SHORT heatmap...")
df_be = pd.read_csv(OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Performance.csv')

pivot_be = df_be.pivot_table(
    values='NetProfit',
    index='BETrigger',
    columns='TargetMultiplier',
    aggfunc='first'
)

fig = plt.figure(figsize=(20, 10))

# Heatmap
ax1 = fig.add_subplot(121)
im = ax1.imshow(pivot_be.values, cmap='RdYlGn', aspect='auto', interpolation='nearest')
ax1.set_xticks(range(len(pivot_be.columns)))
ax1.set_yticks(range(len(pivot_be.index)))
ax1.set_xticklabels([f'{x:.1f}×' for x in pivot_be.columns], fontsize=10)
ax1.set_yticklabels([f'{y:.1f}×' for y in pivot_be.index], fontsize=10)
ax1.set_xlabel('Target Multiplier', fontsize=12, fontweight='bold')
ax1.set_ylabel('Breakeven Trigger', fontsize=12, fontweight='bold')
ax1.set_title('ATR Breakeven Stop SHORT - Net Profit Heatmap', fontsize=14, fontweight='bold', pad=20)

for i in range(len(pivot_be.index)):
    for j in range(len(pivot_be.columns)):
        value = pivot_be.values[i, j]
        color = 'white' if value < -150000 or value > 50000 else 'black'
        ax1.text(j, i, f'${value/1000:.0f}K', ha='center', va='center', color=color, fontsize=9)

cbar = plt.colorbar(im, ax=ax1)
cbar.set_label('Net Profit ($)', fontsize=11, fontweight='bold')

# 3D Surface
ax2 = fig.add_subplot(122, projection='3d')
X, Y = np.meshgrid(range(len(pivot_be.columns)), range(len(pivot_be.index)))
Z = pivot_be.values
surf = ax2.plot_surface(X, Y, Z, cmap='RdYlGn', alpha=0.8, edgecolor='none')
ax2.set_xlabel('Target Multiplier', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_ylabel('Breakeven Trigger', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_zlabel('Net Profit ($)', fontsize=10, fontweight='bold', labelpad=10)
ax2.set_title('3D Surface Plot', fontsize=12, fontweight='bold', pad=20)
ax2.set_xticks(range(len(pivot_be.columns)))
ax2.set_yticks(range(len(pivot_be.index)))
ax2.set_xticklabels([f'{x:.1f}' for x in pivot_be.columns], fontsize=8)
ax2.set_yticklabels([f'{y:.1f}' for y in pivot_be.index], fontsize=8)
ax2.view_init(elev=25, azim=45)
fig.colorbar(surf, ax=ax2, shrink=0.5, aspect=5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Heatmap_3D.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: ATR_Breakeven_Stop_Short_Heatmap_3D.png")

print("\n✓ All heatmaps generated successfully!")
