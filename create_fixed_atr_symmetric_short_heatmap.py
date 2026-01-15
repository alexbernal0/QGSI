"""
Generate Heatmaps with 3D Surface Plots for Fixed ATR Symmetric SHORT Strategy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from pathlib import Path

# Configuration
INPUT_FILE = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_Performance.csv')
OUTPUT_FILE = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_with_3D.png')

print("="*80)
print("GENERATING HEATMAPS WITH 3D SURFACE PLOTS - FIXED ATR SYMMETRIC SHORT")
print("="*80)

# Load data
print("\n[1/3] Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df)} configurations")

# Create figure with 2x2 grid + 3D plot
fig = plt.figure(figsize=(20, 15))
fig.suptitle('Fixed ATR Symmetric Stop/Target - SHORT SIGNALS (All 400 Stocks)\n'
             'ATR Period vs Multiplier, 30-Bar Time Limit, ~60K Short Signals',
             fontsize=16, fontweight='bold', y=0.98)

# Prepare data for heatmaps
atr_periods = sorted(df['ATRPeriod'].unique())
multipliers = sorted(df['StopMultiplier'].unique())

# Create pivot tables
system_score_pivot = df.pivot_table(values='SystemScore', 
                                     index='ATRPeriod', 
                                     columns='StopMultiplier')

net_profit_pivot = df.pivot_table(values='NetProfit', 
                                   index='ATRPeriod', 
                                   columns='StopMultiplier')

profit_factor_pivot = df.pivot_table(values='ProfitFactor', 
                                      index='ATRPeriod', 
                                      columns='StopMultiplier')

print("\n[2/3] Creating heatmaps...")

# 1. System Score Heatmap (Top Left)
ax1 = plt.subplot(2, 3, 1)
sns.heatmap(system_score_pivot/1000, annot=True, fmt='.0f', cmap='RdYlGn', 
            cbar_kws={'label': 'System Score ($K)'}, ax=ax1, center=0)
ax1.set_title('System Score = NetProfit × ProfitFactor', fontsize=12, fontweight='bold')
ax1.set_xlabel('ATR Multiplier (Stop = Target)', fontsize=10)
ax1.set_ylabel('ATR Period', fontsize=10)

# 2. Net Profit Heatmap (Top Middle)
ax2 = plt.subplot(2, 3, 2)
sns.heatmap(net_profit_pivot/1000, annot=True, fmt='.0f', cmap='RdYlGn', 
            cbar_kws={'label': 'Net Profit ($K)'}, ax=ax2, center=0)
ax2.set_title('Net Profit ($K)', fontsize=12, fontweight='bold')
ax2.set_xlabel('ATR Multiplier (Stop = Target)', fontsize=10)
ax2.set_ylabel('ATR Period', fontsize=10)

# 3. Profit Factor Heatmap (Top Right)
ax3 = plt.subplot(2, 3, 3)
sns.heatmap(profit_factor_pivot, annot=True, fmt='.3f', cmap='RdYlGn', 
            cbar_kws={'label': 'Profit Factor'}, ax=ax3, center=1.0, vmin=0.9, vmax=1.0)
ax3.set_title('Profit Factor', fontsize=12, fontweight='bold')
ax3.set_xlabel('ATR Multiplier (Stop = Target)', fontsize=10)
ax3.set_ylabel('ATR Period', fontsize=10)

print("✓ Heatmaps created")

# 4. 3D Surface Plot (Bottom - spans all 3 columns)
print("\n[3/3] Creating 3D surface plot...")
ax4 = plt.subplot(2, 1, 2, projection='3d')

# Create meshgrid
X, Y = np.meshgrid(multipliers, atr_periods)
Z = system_score_pivot.values / 1000  # Convert to $K

# Create surface plot
surf = ax4.plot_surface(X, Y, Z, cmap='RdYlGn', alpha=0.8, 
                        edgecolor='black', linewidth=0.5)

# Add contour lines at the bottom
ax4.contour(X, Y, Z, zdir='z', offset=Z.min(), cmap='RdYlGn', alpha=0.5)

# Labels and title
ax4.set_xlabel('ATR Multiplier', fontsize=11, labelpad=10)
ax4.set_ylabel('ATR Period', fontsize=11, labelpad=10)
ax4.set_zlabel('Net Profit × ProfitFactor ($K)', fontsize=11, labelpad=10)
ax4.set_title('System Score 3D Surface (ATR 20)', fontsize=12, fontweight='bold', pad=20)

# Set viewing angle
ax4.view_init(elev=25, azim=45)

# Add colorbar
fig.colorbar(surf, ax=ax4, shrink=0.5, aspect=10, label='System Score ($K)')

# Add grid
ax4.grid(True, alpha=0.3)

print("✓ 3D surface plot created")

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save figure
print(f"\n[4/4] Saving figure...")
plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {OUTPUT_FILE}")

# Print summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Best System Score: ${df['SystemScore'].max():,.0f} (ATR {df.loc[df['SystemScore'].idxmax(), 'ATRPeriod']}, {df.loc[df['SystemScore'].idxmax(), 'StopMultiplier']:.1f}x)")
print(f"Worst System Score: ${df['SystemScore'].min():,.0f} (ATR {df.loc[df['SystemScore'].idxmin(), 'ATRPeriod']}, {df.loc[df['SystemScore'].idxmin(), 'StopMultiplier']:.1f}x)")
print(f"Best Net Profit: ${df['NetProfit'].max():,.0f}")
print(f"Worst Net Profit: ${df['NetProfit'].min():,.0f}")
print(f"Best Profit Factor: {df['ProfitFactor'].max():.3f}")
print(f"Worst Profit Factor: {df['ProfitFactor'].min():.3f}")
print("="*80)

plt.close()
print("\n✓ Complete!")
