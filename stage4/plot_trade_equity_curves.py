"""
Plot trade-by-trade equity curves for baseline ATR strategy.

X-axis: Trade number (1, 2, 3, ...)
Y-axis: Cumulative equity after each trade

This shows the P&L progression trade-by-trade rather than bar-by-bar.
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

# Load trades
symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'

trades_df = pd.read_parquet(f'/home/ubuntu/stage4_strategy/{symbol}_trades.parquet')

# Separate Long and Short
long_trades = trades_df[trades_df['SignalType'] == 'long'].copy().sort_values('EntryBar').reset_index(drop=True)
short_trades = trades_df[trades_df['SignalType'] == 'short'].copy().sort_values('EntryBar').reset_index(drop=True)

# Calculate cumulative equity for Long
starting_capital = 100000
long_trades['TradeNumber'] = range(1, len(long_trades) + 1)
long_trades['CumulativeEquity'] = starting_capital + long_trades['PnL'].cumsum()

# Calculate cumulative equity for Short
short_trades['TradeNumber'] = range(1, len(short_trades) + 1)
short_trades['CumulativeEquity'] = starting_capital + short_trades['PnL'].cumsum()

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot Long trade-by-trade equity curve
ax1.plot(long_trades['TradeNumber'], long_trades['CumulativeEquity'], 
         linewidth=2, color='green', marker='o', markersize=3, label='Long Strategy')
ax1.axhline(y=starting_capital, color='gray', linestyle='--', linewidth=1, label='Starting Capital')
ax1.fill_between(long_trades['TradeNumber'], starting_capital, long_trades['CumulativeEquity'], 
                  where=(long_trades['CumulativeEquity'] >= starting_capital), alpha=0.3, color='green')
ax1.fill_between(long_trades['TradeNumber'], starting_capital, long_trades['CumulativeEquity'], 
                  where=(long_trades['CumulativeEquity'] < starting_capital), alpha=0.3, color='red')

ax1.set_title(f'{symbol} - Long Strategy: Trade-by-Trade Equity Curve (Baseline ATR)', 
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Trade Number', fontsize=11)
ax1.set_ylabel('Equity ($)', fontsize=11)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, len(long_trades) + 1)

# Add metrics text for Long
final_equity_long = long_trades['CumulativeEquity'].iloc[-1]
net_profit_long = final_equity_long - starting_capital
pct_return_long = (net_profit_long / starting_capital) * 100
total_trades_long = len(long_trades)
winning_trades_long = len(long_trades[long_trades['PnL'] > 0])
win_rate_long = (winning_trades_long / total_trades_long) * 100

text_long = ('Final Equity: ${:,.2f}\n' +
             'Net Profit: ${:,.2f} ({:.2f}%)\n' +
             'Trades: {} (Win Rate: {:.1f}%)').format(
    final_equity_long, net_profit_long, pct_return_long, total_trades_long, win_rate_long)
ax1.text(0.02, 0.98, text_long,
         transform=ax1.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# Plot Short trade-by-trade equity curve
ax2.plot(short_trades['TradeNumber'], short_trades['CumulativeEquity'], 
         linewidth=2, color='red', marker='o', markersize=3, label='Short Strategy')
ax2.axhline(y=starting_capital, color='gray', linestyle='--', linewidth=1, label='Starting Capital')
ax2.fill_between(short_trades['TradeNumber'], starting_capital, short_trades['CumulativeEquity'], 
                  where=(short_trades['CumulativeEquity'] >= starting_capital), alpha=0.3, color='green')
ax2.fill_between(short_trades['TradeNumber'], starting_capital, short_trades['CumulativeEquity'], 
                  where=(short_trades['CumulativeEquity'] < starting_capital), alpha=0.3, color='red')

ax2.set_title(f'{symbol} - Short Strategy: Trade-by-Trade Equity Curve (Baseline ATR)', 
              fontsize=14, fontweight='bold')
ax2.set_xlabel('Trade Number', fontsize=11)
ax2.set_ylabel('Equity ($)', fontsize=11)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, len(short_trades) + 1)

# Add metrics text for Short
final_equity_short = short_trades['CumulativeEquity'].iloc[-1]
net_profit_short = final_equity_short - starting_capital
pct_return_short = (net_profit_short / starting_capital) * 100
total_trades_short = len(short_trades)
winning_trades_short = len(short_trades[short_trades['PnL'] > 0])
win_rate_short = (winning_trades_short / total_trades_short) * 100

text_short = ('Final Equity: ${:,.2f}\n' +
              'Net Profit: ${:,.2f} ({:.2f}%)\n' +
              'Trades: {} (Win Rate: {:.1f}%)').format(
    final_equity_short, net_profit_short, pct_return_short, total_trades_short, win_rate_short)
ax2.text(0.02, 0.98, text_short,
         transform=ax2.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

plt.tight_layout()
plt.savefig(f'/home/ubuntu/stage4_strategy/{symbol}_trade_equity_curves.png', dpi=150, bbox_inches='tight')
print(f'✅ Saved: {symbol}_trade_equity_curves.png')
print(f'   Long: {total_trades_long} trades, Final Equity: ${final_equity_long:,.2f}')
print(f'   Short: {total_trades_short} trades, Final Equity: ${final_equity_short:,.2f}')
