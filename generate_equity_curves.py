"""
Generate equity curves for all symbols from LONG strategy trade logs
Calculate cumulative % gain starting from $100,000 per symbol
Save to CSV and create visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

print("=" * 80)
print("GENERATING EQUITY CURVES FOR ALL SYMBOLS")
print("=" * 80)

# Load trade logs
print("\n[1/5] Loading trade logs...")
trades_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet'
trades = pd.read_parquet(trades_path)
print(f"✓ Loaded {len(trades):,} trades")

# Get unique symbols
symbols = sorted(trades['Symbol'].unique())
print(f"✓ Found {len(symbols)} symbols")

# Calculate equity curves
print(f"\n[2/5] Calculating equity curves...")
STARTING_BALANCE = 100000.0

equity_curves = []

for symbol in symbols:
    # Get symbol trades sorted by entry date
    symbol_trades = trades[trades['Symbol'] == symbol].sort_values('EntryDate').reset_index(drop=True)
    
    if len(symbol_trades) == 0:
        continue
    
    # Calculate cumulative equity
    symbol_trades['CumulativeProfit'] = symbol_trades['NetProfit'].cumsum()
    symbol_trades['Equity'] = STARTING_BALANCE + symbol_trades['CumulativeProfit']
    symbol_trades['EquityPctGain'] = ((symbol_trades['Equity'] - STARTING_BALANCE) / STARTING_BALANCE) * 100
    symbol_trades['TradeNumber'] = range(1, len(symbol_trades) + 1)
    
    # Store equity curve data
    for idx, row in symbol_trades.iterrows():
        equity_curves.append({
            'Symbol': symbol,
            'TradeNumber': row['TradeNumber'],
            'EntryDate': row['EntryDate'],
            'ExitDate': row['ExitDate'],
            'NetProfit': row['NetProfit'],
            'CumulativeProfit': row['CumulativeProfit'],
            'Equity': row['Equity'],
            'EquityPctGain': row['EquityPctGain']
        })

# Convert to DataFrame
equity_df = pd.DataFrame(equity_curves)
print(f"✓ Calculated {len(equity_df):,} equity curve points")

# Save to CSV
print(f"\n[3/5] Saving equity curves...")
csv_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_Equity_Curves.csv'
equity_df.to_csv(csv_path, index=False)
print(f"✓ Saved to: {csv_path}")

# Also save to parquet
parquet_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_Equity_Curves.parquet'
equity_df.to_parquet(parquet_path, index=False)
print(f"✓ Saved to: {parquet_path}")

# Calculate summary statistics per symbol
print(f"\n[4/5] Calculating summary statistics...")
symbol_stats = []

for symbol in symbols:
    symbol_equity = equity_df[equity_df['Symbol'] == symbol]
    
    if len(symbol_equity) == 0:
        continue
    
    final_equity = symbol_equity['Equity'].iloc[-1]
    final_pct_gain = symbol_equity['EquityPctGain'].iloc[-1]
    total_trades = len(symbol_equity)
    max_equity = symbol_equity['Equity'].max()
    min_equity = symbol_equity['Equity'].min()
    max_drawdown_pct = ((min_equity - max_equity) / max_equity) * 100 if max_equity > 0 else 0
    
    symbol_stats.append({
        'Symbol': symbol,
        'TotalTrades': total_trades,
        'StartingEquity': STARTING_BALANCE,
        'FinalEquity': final_equity,
        'TotalProfit': final_equity - STARTING_BALANCE,
        'PctGain': final_pct_gain,
        'MaxEquity': max_equity,
        'MinEquity': min_equity,
        'MaxDrawdownPct': max_drawdown_pct
    })

stats_df = pd.DataFrame(symbol_stats)
stats_path = '/home/ubuntu/stage4_optimization/Best_Long_Strategy_Symbol_Stats.csv'
stats_df.to_csv(stats_path, index=False)
print(f"✓ Symbol statistics saved to: {stats_path}")

# Print summary
print(f"\nSummary Statistics:")
print(f"  Symbols with gains: {len(stats_df[stats_df['PctGain'] > 0])}")
print(f"  Symbols with losses: {len(stats_df[stats_df['PctGain'] < 0])}")
print(f"  Avg % gain per symbol: {stats_df['PctGain'].mean():.2f}%")
print(f"  Best performer: {stats_df.loc[stats_df['PctGain'].idxmax(), 'Symbol']} ({stats_df['PctGain'].max():.2f}%)")
print(f"  Worst performer: {stats_df.loc[stats_df['PctGain'].idxmin(), 'Symbol']} ({stats_df['PctGain'].min():.2f}%)")

# Create visualizations
print(f"\n[5/5] Creating visualizations...")

# Figure 1: All equity curves together
fig1, ax1 = plt.subplots(figsize=(16, 10))

for symbol in symbols:
    symbol_equity = equity_df[equity_df['Symbol'] == symbol]
    if len(symbol_equity) > 0:
        ax1.plot(symbol_equity['TradeNumber'], symbol_equity['EquityPctGain'], 
                alpha=0.3, linewidth=0.5)

ax1.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7, label='Breakeven')
ax1.set_xlabel('Trade Number', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cumulative % Gain', fontsize=12, fontweight='bold')
ax1.set_title('All Symbol Equity Curves - LONG Strategy (ATR Trailing Stop)\n400 Symbols, $100K Starting Balance Each', 
             fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()

plt.tight_layout()
fig1_path = '/home/ubuntu/stage4_optimization/All_Equity_Curves_Long.png'
plt.savefig(fig1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved all equity curves: {fig1_path}")

# Figure 2: Top 20 and Bottom 20 performers
fig2 = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1], hspace=0.3)

# Top 20
ax_top = fig2.add_subplot(gs[0])
top_20 = stats_df.nlargest(20, 'PctGain')

for symbol in top_20['Symbol']:
    symbol_equity = equity_df[equity_df['Symbol'] == symbol]
    final_pct = symbol_equity['EquityPctGain'].iloc[-1]
    ax_top.plot(symbol_equity['TradeNumber'], symbol_equity['EquityPctGain'], 
               linewidth=1.5, alpha=0.7, label=f'{symbol} ({final_pct:.1f}%)')

ax_top.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax_top.set_xlabel('Trade Number', fontsize=11, fontweight='bold')
ax_top.set_ylabel('Cumulative % Gain', fontsize=11, fontweight='bold')
ax_top.set_title('Top 20 Performing Symbols', fontsize=13, fontweight='bold')
ax_top.grid(True, alpha=0.3)
ax_top.legend(loc='upper left', fontsize=7, ncol=2)

# Bottom 20
ax_bottom = fig2.add_subplot(gs[1])
bottom_20 = stats_df.nsmallest(20, 'PctGain')

for symbol in bottom_20['Symbol']:
    symbol_equity = equity_df[equity_df['Symbol'] == symbol]
    final_pct = symbol_equity['EquityPctGain'].iloc[-1]
    ax_bottom.plot(symbol_equity['TradeNumber'], symbol_equity['EquityPctGain'], 
                  linewidth=1.5, alpha=0.7, label=f'{symbol} ({final_pct:.1f}%)')

ax_bottom.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
ax_bottom.set_xlabel('Trade Number', fontsize=11, fontweight='bold')
ax_bottom.set_ylabel('Cumulative % Gain', fontsize=11, fontweight='bold')
ax_bottom.set_title('Bottom 20 Performing Symbols', fontsize=13, fontweight='bold')
ax_bottom.grid(True, alpha=0.3)
ax_bottom.legend(loc='lower left', fontsize=7, ncol=2)

fig2_path = '/home/ubuntu/stage4_optimization/Top_Bottom_20_Equity_Curves_Long.png'
plt.savefig(fig2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved top/bottom 20: {fig2_path}")

# Figure 3: Distribution of final % gains
fig3, ax3 = plt.subplots(figsize=(14, 8))

ax3.hist(stats_df['PctGain'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Breakeven')
ax3.axvline(x=stats_df['PctGain'].mean(), color='green', linestyle='--', linewidth=2, 
           label=f'Mean: {stats_df["PctGain"].mean():.2f}%')
ax3.axvline(x=stats_df['PctGain'].median(), color='orange', linestyle='--', linewidth=2,
           label=f'Median: {stats_df["PctGain"].median():.2f}%')

ax3.set_xlabel('Final % Gain', fontsize=12, fontweight='bold')
ax3.set_ylabel('Number of Symbols', fontsize=12, fontweight='bold')
ax3.set_title('Distribution of Final % Gains Across All Symbols\nLONG Strategy (ATR Trailing Stop)', 
             fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.legend(fontsize=11)

plt.tight_layout()
fig3_path = '/home/ubuntu/stage4_optimization/Pct_Gain_Distribution_Long.png'
plt.savefig(fig3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved distribution: {fig3_path}")

print(f"\n{'='*80}")
print(f"✓ EQUITY CURVE GENERATION COMPLETE!")
print(f"{'='*80}\n")

print(f"Files created:")
print(f"  1. {csv_path}")
print(f"  2. {parquet_path}")
print(f"  3. {stats_path}")
print(f"  4. {fig1_path}")
print(f"  5. {fig2_path}")
print(f"  6. {fig3_path}")
