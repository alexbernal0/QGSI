import pandas as pd
import matplotlib.pyplot as plt
import sys

# Load equity curves
symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'

equity_df = pd.read_parquet(f'/home/ubuntu/stage4_strategy/{symbol}_equity_curves.parquet')

# Separate Long and Short
long_equity = equity_df[equity_df['SignalType'] == 'LONG'].copy()
short_equity = equity_df[equity_df['SignalType'] == 'SHORT'].copy()

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot Long equity curve
ax1.plot(long_equity['BarIndex'], long_equity['Equity'], linewidth=1.5, color='green', label='Long Strategy')
ax1.axhline(y=100000, color='gray', linestyle='--', linewidth=1, label='Starting Capital')
ax1.fill_between(long_equity['BarIndex'], 100000, long_equity['Equity'], 
                  where=(long_equity['Equity'] >= 100000), alpha=0.3, color='green')
ax1.fill_between(long_equity['BarIndex'], 100000, long_equity['Equity'], 
                  where=(long_equity['Equity'] < 100000), alpha=0.3, color='red')
ax1.set_title(f'{symbol} - Long Strategy Equity Curve (Baseline ATR)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Bar Index', fontsize=11)
ax1.set_ylabel('Equity ($)', fontsize=11)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(long_equity['Equity'].min() * 0.99, long_equity['Equity'].max() * 1.01)

# Add metrics text
final_equity_long = long_equity['Equity'].iloc[-1]
net_profit_long = final_equity_long - 100000
pct_return_long = (net_profit_long / 100000) * 100
text_long = 'Final Equity: ${:,.2f}\nNet Profit: ${:,.2f} ({:.2f}%)'.format(final_equity_long, net_profit_long, pct_return_long)
ax1.text(0.02, 0.98, text_long,
         transform=ax1.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot Short equity curve
ax2.plot(short_equity['BarIndex'], short_equity['Equity'], linewidth=1.5, color='red', label='Short Strategy')
ax2.axhline(y=100000, color='gray', linestyle='--', linewidth=1, label='Starting Capital')
ax2.fill_between(short_equity['BarIndex'], 100000, short_equity['Equity'], 
                  where=(short_equity['Equity'] >= 100000), alpha=0.3, color='green')
ax2.fill_between(short_equity['BarIndex'], 100000, short_equity['Equity'], 
                  where=(short_equity['Equity'] < 100000), alpha=0.3, color='red')
ax2.set_title(f'{symbol} - Short Strategy Equity Curve (Baseline ATR)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Bar Index', fontsize=11)
ax2.set_ylabel('Equity ($)', fontsize=11)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(short_equity['Equity'].min() * 0.99, short_equity['Equity'].max() * 1.01)

# Add metrics text
final_equity_short = short_equity['Equity'].iloc[-1]
net_profit_short = final_equity_short - 100000
pct_return_short = (net_profit_short / 100000) * 100
text_short = 'Final Equity: ${:,.2f}\nNet Profit: ${:,.2f} ({:.2f}%)'.format(final_equity_short, net_profit_short, pct_return_short)
ax2.text(0.02, 0.98, text_short,
         transform=ax2.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(f'/home/ubuntu/stage4_strategy/{symbol}_equity_curves.png', dpi=150, bbox_inches='tight')
print(f'✅ Saved: {symbol}_equity_curves.png')
