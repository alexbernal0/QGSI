#!/usr/bin/env python3.11
"""
Generate 3-Panel CAGR Confidence Intervals Visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

print("="*80)
print("GENERATING CAGR CONFIDENCE INTERVALS VISUALIZATION")
print("="*80)

# Load bootstrap distribution
bootstrap_df = pd.read_csv('/home/ubuntu/stage4_optimization/cagr_bootstrap_distribution.csv')
cagrs = bootstrap_df['CAGR'].values

# Load results
results_df = pd.read_csv('/home/ubuntu/stage4_optimization/cagr_confidence_intervals_results.csv')

# Extract key metrics
mean_cagr = float(results_df[results_df['Metric'] == 'Expected CAGR (Mean)']['Value'].iloc[0].rstrip('%'))
median_cagr = float(results_df[results_df['Metric'] == 'Median CAGR']['Value'].iloc[0].rstrip('%'))
ci_95_lower = float(results_df[results_df['Metric'] == '95% CI Lower']['Value'].iloc[0].rstrip('%'))
ci_95_upper = float(results_df[results_df['Metric'] == '95% CI Upper']['Value'].iloc[0].rstrip('%'))
ci_68_lower = float(results_df[results_df['Metric'] == '68% CI Lower']['Value'].iloc[0].rstrip('%'))
ci_68_upper = float(results_df[results_df['Metric'] == '68% CI Upper']['Value'].iloc[0].rstrip('%'))
pessimistic = float(results_df[results_df['Metric'] == 'Pessimistic (10th percentile)']['Value'].iloc[0].rstrip('%'))
optimistic = float(results_df[results_df['Metric'] == 'Optimistic (90th percentile)']['Value'].iloc[0].rstrip('%'))
prob_positive = float(results_df[results_df['Metric'] == 'Probability of Positive Return (%)']['Value'].iloc[0].rstrip('%'))
current_cagr = float(results_df[results_df['Metric'] == 'Current Annualized CAGR (147 days)']['Value'].iloc[0].rstrip('%'))

print(f"\nKey metrics loaded:")
print(f"  Mean CAGR: {mean_cagr:.2f}%")
print(f"  95% CI: [{ci_95_lower:.2f}%, {ci_95_upper:.2f}%]")
print(f"  Current CAGR: {current_cagr:.2f}%")

# Create figure with 3 panels
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 0.8], hspace=0.35)

# Color scheme
navy = '#1f4788'
green = '#2ca02c'
red = '#d62728'
yellow = '#ffd700'
light_blue = '#add8e6'

# Panel 1: Distribution Histogram
ax1 = fig.add_subplot(gs[0])

# Plot histogram
n, bins, patches = ax1.hist(cagrs, bins=50, alpha=0.7, color=navy, edgecolor='black', linewidth=0.5)

# Color regions
for i, patch in enumerate(patches):
    bin_center = (bins[i] + bins[i+1]) / 2
    if bin_center < pessimistic:
        patch.set_facecolor(red)
        patch.set_alpha(0.3)
    elif bin_center > optimistic:
        patch.set_facecolor(green)
        patch.set_alpha(0.3)
    else:
        patch.set_facecolor(navy)
        patch.set_alpha(0.7)

# Add vertical lines
ax1.axvline(mean_cagr, color=yellow, linestyle='--', linewidth=2.5, label=f'Expected (Mean): {mean_cagr:.1f}%')
ax1.axvline(median_cagr, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_cagr:.1f}%')
ax1.axvline(current_cagr, color='purple', linestyle=':', linewidth=2, label=f'Current (147 days): {current_cagr:.1f}%')

# Add shaded confidence intervals
ax1.axvspan(ci_95_lower, ci_95_upper, alpha=0.1, color='gray', label=f'95% CI: [{ci_95_lower:.1f}%, {ci_95_upper:.1f}%]')

ax1.set_xlabel('1-Year CAGR (%)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('1-Year CAGR Distribution (10,000 Bootstrap Simulations)', fontsize=13, fontweight='bold', color=navy)
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3, linestyle='--')

# Panel 2: Box Plot with Scenarios
ax2 = fig.add_subplot(gs[1])

# Create box plot data
box_data = [cagrs]
bp = ax2.boxplot(box_data, vert=False, widths=0.5, patch_artist=True,
                  boxprops=dict(facecolor=light_blue, color=navy, linewidth=2),
                  whiskerprops=dict(color=navy, linewidth=2),
                  capprops=dict(color=navy, linewidth=2),
                  medianprops=dict(color='red', linewidth=2.5),
                  flierprops=dict(marker='o', markerfacecolor=navy, markersize=3, alpha=0.3))

# Add scenario markers
ax2.plot(pessimistic, 1, 'rv', markersize=12, label=f'Pessimistic (10th): {pessimistic:.1f}%', zorder=10)
ax2.plot(mean_cagr, 1, 'y^', markersize=12, label=f'Expected (Mean): {mean_cagr:.1f}%', zorder=10)
ax2.plot(median_cagr, 1, 'o', color='orange', markersize=10, label=f'Median (50th): {median_cagr:.1f}%', zorder=10)
ax2.plot(optimistic, 1, 'g^', markersize=12, label=f'Optimistic (90th): {optimistic:.1f}%', zorder=10)

# Add current CAGR reference line
ax2.axvline(current_cagr, color='purple', linestyle=':', linewidth=2, alpha=0.7)

ax2.set_xlabel('1-Year CAGR (%)', fontsize=11, fontweight='bold')
ax2.set_yticks([])
ax2.set_title('Scenario Analysis', fontsize=13, fontweight='bold', color=navy)
ax2.legend(loc='upper right', fontsize=8, ncol=2)
ax2.grid(True, alpha=0.3, linestyle='--', axis='x')

# Panel 3: Summary Table
ax3 = fig.add_subplot(gs[2])
ax3.axis('off')

# Create table data
table_data = [
    ['Expected CAGR (Mean)', f'{mean_cagr:.2f}%'],
    ['Median CAGR', f'{median_cagr:.2f}%'],
    ['95% Confidence Interval', f'[{ci_95_lower:.2f}%, {ci_95_upper:.2f}%]'],
    ['68% Confidence Interval', f'[{ci_68_lower:.2f}%, {ci_68_upper:.2f}%]'],
    ['Pessimistic (10th percentile)', f'{pessimistic:.2f}%'],
    ['Optimistic (90th percentile)', f'{optimistic:.2f}%'],
    ['Probability of Positive Return', f'{prob_positive:.1f}%'],
    ['Current Annualized (147 days)', f'{current_cagr:.2f}%']
]

# Create table
table = ax3.table(cellText=table_data, cellLoc='left',
                  colWidths=[0.6, 0.4],
                  loc='center',
                  bbox=[0.05, 0.0, 0.9, 1.0])

table.auto_set_font_size(False)
table.set_fontsize(9)

# Style table
for i, key in enumerate(table_data):
    cell = table[(i, 0)]
    cell.set_facecolor('#f0f0f0')
    cell.set_text_props(weight='bold', color=navy)
    cell.set_edgecolor(navy)
    cell.set_linewidth(1.5)
    
    cell = table[(i, 1)]
    cell.set_facecolor('white')
    cell.set_text_props(weight='bold')
    cell.set_edgecolor(navy)
    cell.set_linewidth(1.5)
    
    # Highlight key rows
    if i == 0:  # Expected CAGR
        table[(i, 1)].set_facecolor(yellow)
        table[(i, 1)].set_alpha(0.3)

ax3.set_title('Statistical Summary', fontsize=13, fontweight='bold', color=navy, pad=10)

# Add overall title
fig.suptitle('1-Year CAGR Estimation with Statistical Confidence Intervals\nCombined Portfolio (LONG + SHORT Strategies)', 
             fontsize=14, fontweight='bold', color=navy, y=0.98)

# Save figure
output_path = '/home/ubuntu/stage4_optimization/part3_cagr_confidence_intervals.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Visualization saved: {output_path}")

plt.close()

print("="*80)
print("VISUALIZATION GENERATION COMPLETE")
print("="*80)
