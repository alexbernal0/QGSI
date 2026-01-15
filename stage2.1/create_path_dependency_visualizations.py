#!/usr/bin/env python3.11
"""
================================================================================
QGSI PATH DEPENDENCY VISUALIZATIONS - STAGE 2.1
================================================================================

PROGRAM NAME: create_path_dependency_visualizations.py
VERSION: 2.1 Production
AUTHOR: Alex Bernal, Senior Quantitative Researcher
DATE: January 2026
PROJECT: QGSI Signal Research

================================================================================
PURPOSE:
================================================================================
Generate conditional trajectory charts and statistics tables for path dependency
analysis. Visualizes how signals behave differently based on their early
performance classification (Quick Winners, Quick Losers, Chop/Drift).

Creates publication-quality visualizations for research reports and presentations.

================================================================================
VISUALIZATIONS GENERATED:
================================================================================
1. Conditional Trajectory Charts (2 files):
   - Long_Conditional_Trajectory.png
   - Short_Conditional_Trajectory.png
   
   Shows mean trajectory for each path group:
   - Quick Winners (green): Signals with immediate strength
   - Quick Losers (red): Signals with immediate weakness
   - Chop/Drift (blue): Signals without clear early direction

2. Statistics Tables (2 CSV files):
   - Long_PathGroup_Statistics.csv
   - Short_PathGroup_Statistics.csv
   
   Per-bar statistics for each path group (bars 1-30):
   - ProbGain, ProbLoss: Win/loss frequencies
   - MeanReturn, MedianReturn: Central tendency
   - P80, P20: 80th and 20th percentiles
   - ProfitFactor: Gross profit / gross loss ratio

================================================================================
INPUT DATA:
================================================================================
Required Files:
1. path_dependency_results.parquet: Path group classifications (139,959 signals)
2. ALL_trajectory_signalcount.parquet: Full trajectory data (5.7M rows)

Both files are outputs from previous stages.

================================================================================
CHART SPECIFICATIONS:
================================================================================
- Figure size: 14" × 8" (high resolution)
- DPI: 300 (publication quality)
- Color scheme:
  * Quick Winners: Green (#2ecc71)
  * Quick Losers: Red (#e74c3c)
  * Chop/Drift: Blue (#3498db)
- Grid: Light gray, alpha 0.3
- Fonts: Arial, 12pt labels, 14pt title
- Y-axis: Percentage returns
- X-axis: Bar offset (1-30)

================================================================================
STATISTICS CALCULATIONS:
================================================================================
For each path group and bar:
- ProbGain: % of signals with return > 0
- ProbLoss: % of signals with return < 0
- MeanReturn: Arithmetic average return
- MedianReturn: 50th percentile return
- P80: 80th percentile (strong positive outcomes)
- P20: 20th percentile (strong negative outcomes)
- ProfitFactor: Sum(positive returns) / |Sum(negative returns)|

================================================================================
USAGE:
================================================================================
Generate all visualizations:
    python3.11 create_path_dependency_visualizations.py

Output directory: path_dependency_visualizations/

The script will:
1. Load path dependency and trajectory data
2. Merge datasets
3. Calculate conditional statistics
4. Generate trajectory charts
5. Save CSV tables
6. Display completion message

Expected runtime: 2-3 minutes

================================================================================
DEPENDENCIES:
================================================================================
- pandas, numpy: Data manipulation
- matplotlib, seaborn: Visualization
- pyarrow: Parquet I/O

Install: pip3 install pandas numpy matplotlib seaborn pyarrow

================================================================================
INTERPRETATION GUIDE:
================================================================================
Quick Winners (Green Line):
- Immediate upward trajectory
- Sustained momentum through 30 bars
- High profit factor (>4.0)
- Indicates high-quality signal

Quick Losers (Red Line):
- Immediate downward trajectory
- Continued weakness through 30 bars
- Low profit factor (<0.35)
- Indicates low-quality signal

Chop/Drift (Blue Line):
- Oscillates near zero
- Marginal performance
- Profit factor near 1.0
- Represents majority of signals (87%)

================================================================================
NOTES:
================================================================================
- Charts show MEAN trajectory (not median)
- All returns calculated relative to Bar 0 (entry price)
- For Long signals: positive return = profit
- For Short signals: negative return = profit (price moving down)
- Path groups determined by bars 1-5 only
- Statistics calculated over full 30-bar window

================================================================================
"""
#!/usr/bin/env python3.11
"""
Generate conditional trajectory visualizations by Path Group.
Shows how Quick Winners, Quick Losers, and Chop/Drift groups perform.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Create output directory
output_dir = Path('/home/ubuntu/path_dependency_visualizations')
output_dir.mkdir(exist_ok=True)

# Load data
print("Loading data...")
trajectory_df = pd.read_parquet('/home/ubuntu/ALL_trajectory_signalcount.parquet')
path_df = pd.read_parquet('/home/ubuntu/path_dependency_results.parquet')

# Merge path groups with trajectory data
print("Merging path groups with trajectory data...")
trajectory_df = trajectory_df.merge(
    path_df[['Symbol', 'SignalIndex', 'SignalType', 'PathGroup']],
    on=['Symbol', 'SignalIndex', 'SignalType'],
    how='left'
)

print(f"Merged data shape: {trajectory_df.shape}")
print(f"Path groups: {trajectory_df['PathGroup'].value_counts()}")

def create_conditional_trajectory_chart(signal_type):
    """Create trajectory chart showing all 3 path groups for a signal type."""
    
    data = trajectory_df[trajectory_df['SignalType'] == signal_type]
    
    fig, ax = plt.subplots(figsize=(24, 16), dpi=300)
    
    colors = {
        'Quick_Winners': '#2E7D32',  # Green
        'Quick_Losers': '#C62828',   # Red
        'Chop_Drift': '#1976D2'      # Blue
    }
    
    for path_group in ['Quick_Winners', 'Quick_Losers', 'Chop_Drift']:
        group_data = data[data['PathGroup'] == path_group]
        
        # Calculate statistics per bar
        stats = group_data.groupby('Bar')['Return'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('p80', lambda x: np.percentile(x, 80)),
            ('p20', lambda x: np.percentile(x, 20))
        ]).reset_index()
        
        bars = stats['Bar'].values
        mean_ret = stats['mean'].values
        median_ret = stats['median'].values
        p80 = stats['p80'].values
        p20 = stats['p20'].values
        
        color = colors[path_group]
        
        # Plot distribution bands
        ax.fill_between(bars, p20, p80, alpha=0.12, color=color)
        
        # Plot median and mean
        ax.plot(bars, median_ret, color=color, linewidth=4, label=f'{path_group} Median', linestyle='-')
        ax.plot(bars, mean_ret, color=color, linewidth=3.5, label=f'{path_group} Mean', linestyle='--', alpha=0.7)
    
    # Formatting
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.3)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.3)
    
    ax.set_xlabel('Bar (Relative to Signal)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Return (%)', fontsize=16, fontweight='bold')
    ax.set_title(f'{signal_type} Signal Trajectories by Path Group (All 400 Symbols)', 
                 fontsize=20, fontweight='bold', pad=20)
    
    ax.legend(fontsize=12, loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.tick_params(labelsize=12)
    
    plt.tight_layout()
    
    output_path = output_dir / f'{signal_type}_Conditional_Trajectory.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved: {output_path}")
    
    return stats

def create_statistics_table(signal_type):
    """Create statistics table for each path group."""
    
    data = trajectory_df[(trajectory_df['SignalType'] == signal_type) & (trajectory_df['Bar'] >= 1)]
    
    results = []
    
    for path_group in ['Quick_Winners', 'Quick_Losers', 'Chop_Drift']:
        group_data = data[data['PathGroup'] == path_group]
        
        for bar in range(1, 31):
            bar_data = group_data[group_data['Bar'] == bar]['Return']
            
            if len(bar_data) > 0:
                prob_gain = 100 * (bar_data > 0).sum() / len(bar_data)
                prob_loss = 100 * (bar_data < 0).sum() / len(bar_data)
                mean_ret = bar_data.mean()
                median_ret = bar_data.median()
                p80 = np.percentile(bar_data, 80)
                p20 = np.percentile(bar_data, 20)
                
                # Profit factor
                gains = bar_data[bar_data > 0].sum()
                losses = abs(bar_data[bar_data < 0].sum())
                pf = gains / losses if losses > 0 else np.inf
                
                results.append({
                    'PathGroup': path_group,
                    'Bar': bar,
                    'ProbGain': prob_gain,
                    'ProbLoss': prob_loss,
                    'MeanReturn': mean_ret,
                    'MedianReturn': median_ret,
                    'P80': p80,
                    'P20': p20,
                    'ProfitFactor': pf
                })
    
    df = pd.DataFrame(results)
    
    # Save to CSV
    output_path = output_dir / f'{signal_type}_PathGroup_Statistics.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved: {output_path}")
    
    return df

# Generate visualizations
print("\nGenerating conditional trajectory charts...")
for signal_type in ['Long', 'Short']:
    print(f"\nProcessing {signal_type} signals...")
    create_conditional_trajectory_chart(signal_type)
    create_statistics_table(signal_type)

print("\n" + "="*80)
print("✓ ALL VISUALIZATIONS GENERATED")
print("="*80)
