#!/usr/bin/env python3.11
"""
================================================================================
QGSI TRAJECTORY ANALYSIS - STAGE 2.0
================================================================================

PROGRAM NAME: qgsi_trajectory_analysis_final.py
VERSION: 2.0 Final
AUTHOR: Alex Bernal, Senior Quantitative Researcher
DATE: January 2026
PROJECT: QGSI Signal Research

================================================================================
PURPOSE:
================================================================================
Analyze pre-signal and post-signal price trajectories to understand signal 
timing characteristics and forward-looking performance. This is the core
single-symbol trajectory calculation engine.

Key Innovation: Uses "Universal Reference Point" methodology where Bar 0 
(signal bar Close price) serves as the reference for ALL return calculations,
both inbound and outbound. This eliminates visual discontinuities and provides
intuitive interpretation.

================================================================================
METHODOLOGY:
================================================================================
1. Universal Reference Point: Bar 0 Close price = 0% for all calculations

2. Inbound Trajectory (Bars -10 to -1):
   - Calculates how price deviated from entry point BEFORE signal
   - Formula: (Close[bar] - Close[0]) / Close[0]
   - Reveals setup pattern (pullback, rally, etc.)

3. Outbound Trajectory (Bars 1 to 30):
   - Calculates how price moves AFTER signal
   - Formula: (Close[bar] - Close[0]) / Close[0]
   - Reveals predictive edge and optimal holding period

4. Separate Analysis:
   - Long signals (Signal=1): Buy signals
   - Short signals (Signal=2): Sell/short signals

================================================================================
INPUT DATA:
================================================================================
- Source: QGSI_AllSymbols_3Signals.parquet (1-minute OHLC bars)
- Required Columns: Symbol, Close, Signal, SignalCount
- Signal Encoding: 0=No signal, 1=Long, 2=Short

================================================================================
OUTPUT:
================================================================================
For each symbol:
1. {symbol}_trajectory_data.parquet: Full trajectory data (bars -10 to +30)
2. {symbol}_statistics_data.parquet: Per-bar statistics (prob gain/loss, etc.)
3. {symbol}_Long_Trajectory.png: Visualization for Long signals
4. {symbol}_Short_Trajectory.png: Visualization for Short signals
5. {symbol}_Long_Statistics.png: Statistics table for Long signals
6. {symbol}_Short_Statistics.png: Statistics table for Short signals

================================================================================
USAGE:
================================================================================
Single symbol:
    python3.11 qgsi_trajectory_analysis_final.py AAPL

Multiple symbols:
    python3.11 qgsi_trajectory_analysis_final.py AAPL MSFT GOOGL

================================================================================
DEPENDENCIES:
================================================================================
- pandas, numpy: Data manipulation
- matplotlib, seaborn: Visualization
- duckdb: Database operations (optional)
- pyarrow: Parquet file I/O

Install: pip3 install pandas numpy matplotlib seaborn duckdb pyarrow

================================================================================
NOTES:
================================================================================
- Requires sufficient forward bars (30) after each signal
- Signals near end of dataset are excluded
- Memory efficient: processes one symbol at a time
- For batch processing of all 400 symbols, use:
  batch_trajectory_signalcount_efficient.py

================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb
from pathlib import Path
import sys

# Configuration
DATA_PATH = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
PRE_SIGNAL_BARS = 10   # Look back 10 bars before signal
POST_SIGNAL_BARS = 30  # Look forward 30 bars after signal
OUTPUT_DIR = '/home/ubuntu/trajectory_output'

def calculate_trajectory(symbol, df):
    """
    Calculate trajectory data for a single symbol.
    
    Parameters:
    -----------
    symbol : str
        Stock symbol
    df : pd.DataFrame
        Price data with signals for the symbol
    
    Returns:
    --------
    trajectory_df : pd.DataFrame
        Trajectory data with returns calculated relative to bar 0
    """
    print(f"Processing {symbol}...")
    
    # Sort by datetime
    df = df.sort_values('BarDateTime').reset_index(drop=True)
    
    # Identify signals
    signal_mask = df['Signal'].isin([1, -1])
    signal_indices = df[signal_mask].index.tolist()
    
    # Filter signals with sufficient data
    valid_signals = []
    for idx in signal_indices:
        if idx >= PRE_SIGNAL_BARS and idx + POST_SIGNAL_BARS < len(df):
            valid_signals.append(idx)
    
    print(f"  Found {len(valid_signals):,} valid signals")
    
    # Calculate trajectories
    trajectory_records = []
    
    for signal_idx in valid_signals:
        signal_type = df.loc[signal_idx, 'Signal']
        entry_price = df.loc[signal_idx, 'Close']  # Bar 0 Close - UNIVERSAL REFERENCE
        
        # Pre-signal trajectory (bars -10 to -1)
        # Reference: Close at bar 0 (entry price)
        # Calculate how far back in time price deviated from entry
        for i in range(-PRE_SIGNAL_BARS, 0):  # -10 to -1
            bar_idx = signal_idx + i
            bar_price = df.loc[bar_idx, 'Close']
            pct_return = (bar_price - entry_price) / entry_price  # Relative to bar 0
            
            trajectory_records.append({
                'Symbol': symbol,
                'SignalIndex': signal_idx,
                'SignalType': 'Long' if signal_type == 1 else 'Short',
                'SignalDateTime': df.loc[signal_idx, 'BarDateTime'],
                'Bar': i,
                'BarDateTime': df.loc[bar_idx, 'BarDateTime'],
                'Price': bar_price,
                'EntryPrice': entry_price,
                'Return': pct_return
            })
        
        # Bar 0 (signal bar) - always 0% return (universal reference point)
        trajectory_records.append({
            'Symbol': symbol,
            'SignalIndex': signal_idx,
            'SignalType': 'Long' if signal_type == 1 else 'Short',
            'SignalDateTime': df.loc[signal_idx, 'BarDateTime'],
            'Bar': 0,
            'BarDateTime': df.loc[signal_idx, 'BarDateTime'],
            'Price': entry_price,
            'EntryPrice': entry_price,
            'Return': 0.0
        })
        
        # Post-signal trajectory (bars 1 to 30)
        # Reference: Close at bar 0 (entry price)
        for i in range(1, POST_SIGNAL_BARS + 1):  # 1 to 30
            bar_idx = signal_idx + i
            bar_price = df.loc[bar_idx, 'Close']
            pct_return = (bar_price - entry_price) / entry_price
            
            trajectory_records.append({
                'Symbol': symbol,
                'SignalIndex': signal_idx,
                'SignalType': 'Long' if signal_type == 1 else 'Short',
                'SignalDateTime': df.loc[signal_idx, 'BarDateTime'],
                'Bar': i,
                'BarDateTime': df.loc[bar_idx, 'BarDateTime'],
                'Price': bar_price,
                'EntryPrice': entry_price,
                'Return': pct_return
            })
    
    trajectory_df = pd.DataFrame(trajectory_records)
    return trajectory_df


def calculate_statistics(trajectory_df):
    """
    Calculate per-bar statistics from trajectory data.
    
    Parameters:
    -----------
    trajectory_df : pd.DataFrame
        Trajectory data for symbol(s)
    
    Returns:
    --------
    statistics_df : pd.DataFrame
        Per-bar statistics including profit factor
    """
    statistics_records = []
    
    symbols = trajectory_df['Symbol'].unique()
    
    for symbol in symbols:
        symbol_data = trajectory_df[trajectory_df['Symbol'] == symbol]
        
        for signal_type in ['Long', 'Short']:
            signal_data = symbol_data[symbol_data['SignalType'] == signal_type]
            
            if len(signal_data) == 0:
                continue
            
            # Calculate statistics for post-signal bars (1-30)
            for bar in range(1, POST_SIGNAL_BARS + 1):
                bar_data = signal_data[signal_data['Bar'] == bar]['Return']
                
                if len(bar_data) > 0:
                    # Basic statistics
                    prob_gain = (bar_data > 0).sum() / len(bar_data)
                    prob_loss = (bar_data < 0).sum() / len(bar_data)
                    mean_return = bar_data.mean()
                    median_return = bar_data.median()
                    percentile_80 = bar_data.quantile(0.80)
                    percentile_20 = bar_data.quantile(0.20)
                    
                    # Profit Factor calculation
                    gains = bar_data[bar_data > 0].sum()
                    losses = abs(bar_data[bar_data < 0].sum())
                    profit_factor = gains / losses if losses > 0 else np.inf
                    
                    statistics_records.append({
                        'Symbol': symbol,
                        'SignalType': signal_type,
                        'Bar': bar,
                        'Count': len(bar_data),
                        'ProbGain': prob_gain,
                        'ProbLoss': prob_loss,
                        'MeanReturn': mean_return,
                        'MedianReturn': median_return,
                        'Percentile80': percentile_80,
                        'Percentile20': percentile_20,
                        'ProfitFactor': profit_factor
                    })
    
    statistics_df = pd.DataFrame(statistics_records)
    return statistics_df


def create_trajectory_chart(trajectory_df, symbol, signal_type, output_path):
    """
    Create high-resolution trajectory chart with percentile bands.
    
    Parameters:
    -----------
    trajectory_df : pd.DataFrame
        Trajectory data for the symbol
    symbol : str
        Stock symbol
    signal_type : str
        'Long' or 'Short'
    output_path : str
        Path to save the chart
    """
    signal_data = trajectory_df[(trajectory_df['Symbol'] == symbol) & 
                                 (trajectory_df['SignalType'] == signal_type)]
    
    if len(signal_data) == 0:
        print(f"  No {signal_type} signals for {symbol}")
        return
    
    # Calculate percentiles per bar
    percentiles = signal_data.groupby('Bar')['Return'].agg([
        ('p10', lambda x: x.quantile(0.10)),
        ('p20', lambda x: x.quantile(0.20)),
        ('p30', lambda x: x.quantile(0.30)),
        ('p40', lambda x: x.quantile(0.40)),
        ('median', 'median'),
        ('p60', lambda x: x.quantile(0.60)),
        ('p70', lambda x: x.quantile(0.70)),
        ('p80', lambda x: x.quantile(0.80)),
        ('p90', lambda x: x.quantile(0.90)),
        ('mean', 'mean')
    ]).reset_index()
    
    # Convert to percentage
    for col in percentiles.columns:
        if col != 'Bar':
            percentiles[col] = percentiles[col] * 100
    
    # Create figure with 2x height
    fig, ax = plt.subplots(figsize=(24, 20))
    
    bars = percentiles['Bar'].values
    
    # Plot percentile bands with transparency
    ax.fill_between(bars, percentiles['p10'], percentiles['p90'], 
                     alpha=0.08, color='blue', label='10th-90th Percentile')
    ax.fill_between(bars, percentiles['p20'], percentiles['p80'], 
                     alpha=0.12, color='blue', label='20th-80th Percentile')
    ax.fill_between(bars, percentiles['p30'], percentiles['p70'], 
                     alpha=0.16, color='blue', label='30th-70th Percentile')
    ax.fill_between(bars, percentiles['p40'], percentiles['p60'], 
                     alpha=0.20, color='blue', label='40th-60th Percentile')
    
    # Plot median and mean with thick lines
    ax.plot(bars, percentiles['median'], 'o-', linewidth=4, markersize=7,
            color='darkblue', label='Median', zorder=10)
    ax.plot(bars, percentiles['mean'], 's--', linewidth=3.5, markersize=6,
            color='red', label='Mean', zorder=10)
    
    # Add vertical line at bar 0 (signal/entry point)
    ax.axvline(x=0, color='green', linestyle='--', linewidth=3, 
               label='Signal/Entry Point (Bar 0)', alpha=0.8, zorder=5)
    
    # Add horizontal line at 0%
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.6)
    
    # Styling
    ax.set_xlabel('Bar Number (Relative to Signal)', fontsize=18, fontweight='bold')
    ax.set_ylabel('Return (%)', fontsize=18, fontweight='bold')
    ax.set_title(f'{symbol} {signal_type} Signals - Price Trajectory Analysis (Bars -10 to +30)',
                 fontsize=22, fontweight='bold', pad=20)
    
    # Set x-axis to show every bar
    ax.set_xticks(bars)
    ax.set_xticklabels(bars, fontsize=11)
    ax.tick_params(axis='y', labelsize=14)
    
    # Fine dot grid
    ax.grid(True, alpha=0.4, linestyle=':', linewidth=0.8)
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(which='minor', alpha=0.2, linestyle=':', linewidth=0.5)
    
    # Legend
    ax.legend(loc='best', fontsize=13, framealpha=0.95)
    
    # Add signal count
    signal_count = len(signal_data['SignalIndex'].unique())
    ax.text(0.02, 0.98, f'N = {signal_count} signals', 
            transform=ax.transAxes, fontsize=15, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {output_path}")


def create_statistics_table(statistics_df, symbol, signal_type, output_path):
    """
    Create pivoted statistics table with bars as columns.
    
    Parameters:
    -----------
    statistics_df : pd.DataFrame
        Statistics data for the symbol
    symbol : str
        Stock symbol
    signal_type : str
        'Long' or 'Short'
    output_path : str
        Path to save the table
    """
    stats_subset = statistics_df[(statistics_df['Symbol'] == symbol) & 
                                  (statistics_df['SignalType'] == signal_type)]
    
    if len(stats_subset) == 0:
        print(f"  No {signal_type} statistics for {symbol}")
        return
    
    # Create pivoted data structure
    bars = sorted(stats_subset['Bar'].unique())
    
    table_data = []
    row_labels = ['Prob Gain', 'Prob Loss', 'Mean Return', 'Median Return', 
                  '80th %ile', '20th %ile', 'Profit Factor']
    
    for label in row_labels:
        row = []
        for bar in bars:
            bar_stats = stats_subset[stats_subset['Bar'] == bar].iloc[0]
            
            if label == 'Prob Gain':
                value = f"{bar_stats['ProbGain']*100:.1f}%"
            elif label == 'Prob Loss':
                value = f"{bar_stats['ProbLoss']*100:.1f}%"
            elif label == 'Mean Return':
                value = f"{bar_stats['MeanReturn']*100:.3f}%"
            elif label == 'Median Return':
                value = f"{bar_stats['MedianReturn']*100:.3f}%"
            elif label == '80th %ile':
                value = f"{bar_stats['Percentile80']*100:.3f}%"
            elif label == '20th %ile':
                value = f"{bar_stats['Percentile20']*100:.3f}%"
            elif label == 'Profit Factor':
                pf = bar_stats['ProfitFactor']
                value = f"{pf:.2f}" if pf < 100 else "∞"
            
            row.append(value)
        
        table_data.append(row)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(30, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Column headers (bar numbers)
    col_labels = [f'Bar {b}' for b in bars]
    
    # Create table
    table = ax.table(cellText=table_data,
                     rowLabels=row_labels,
                     colLabels=col_labels,
                     cellLoc='center',
                     rowLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Color header row
    for i in range(len(col_labels)):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # Color row labels
    for i in range(len(row_labels)):
        cell = table[(i+1, -1)]
        cell.set_facecolor('#D9E1F2')
        cell.set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            cell = table[(i+1, j)]
            if i % 2 == 0:
                cell.set_facecolor('#F2F2F2')
            else:
                cell.set_facecolor('white')
    
    # Title
    plt.title(f'{symbol} {signal_type} Signals - Statistics Per Bar (1-30 Bars Forward)',
              fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved {output_path}")


def main():
    """Main execution function."""
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Get symbol from command line or default to AAPL
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    print(f"\n{'='*60}")
    print(f"QGSI Trajectory Analysis - {symbol}")
    print(f"{'='*60}\n")
    
    # Load data
    print(f"Loading data for {symbol}...")
    df = pd.read_parquet(DATA_PATH, filters=[('Symbol', '=', symbol)])
    print(f"Loaded {len(df):,} rows")
    
    # Calculate trajectory
    trajectory_df = calculate_trajectory(symbol, df)
    print(f"\nTrajectory data: {trajectory_df.shape}")
    
    # Calculate statistics
    statistics_df = calculate_statistics(trajectory_df)
    print(f"Statistics data: {statistics_df.shape}")
    
    # Save data
    trajectory_path = f'{OUTPUT_DIR}/{symbol}_trajectory_data.parquet'
    statistics_path = f'{OUTPUT_DIR}/{symbol}_statistics_data.parquet'
    
    trajectory_df.to_parquet(trajectory_path, index=False)
    statistics_df.to_parquet(statistics_path, index=False)
    print(f"\n✓ Saved trajectory data: {trajectory_path}")
    print(f"✓ Saved statistics data: {statistics_path}")
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    for signal_type in ['Long', 'Short']:
        # Trajectory chart
        chart_path = f'{OUTPUT_DIR}/{symbol}_{signal_type}_Trajectory.png'
        create_trajectory_chart(trajectory_df, symbol, signal_type, chart_path)
        
        # Statistics table
        table_path = f'{OUTPUT_DIR}/{symbol}_{signal_type}_Statistics.png'
        create_statistics_table(statistics_df, symbol, signal_type, table_path)
    
    print(f"\n{'='*60}")
    print(f"✓ Analysis complete for {symbol}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
