"""
Generate comprehensive summary report for Stage 4 baseline ATR strategy
"""

import pandas as pd
import duckdb

MOTHERDUCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'

# Connect to MotherDuck
conn = duckdb.connect(f'md:QGSI?motherduck_token={MOTHERDUCK_TOKEN}')

print("="*80)
print("QGSI STAGE 4: BASELINE ATR STRATEGY - COMPREHENSIVE SUMMARY")
print("="*80)
print()

# Load all trades
print("Loading data from MotherDuck...")
all_trades = conn.execute("SELECT * FROM stage4_all_trades").df()
all_equity = conn.execute("SELECT * FROM stage4_all_equity").df()

print(f"Total trades loaded: {len(all_trades):,}")
print(f"Total equity records: {len(all_equity):,}")
print()

# Overall Statistics
print("="*80)
print("1. OVERALL STATISTICS")
print("="*80)

total_symbols = all_trades['Symbol'].nunique()
long_trades = all_trades[all_trades['SignalType'] == 'Long']
short_trades = all_trades[all_trades['SignalType'] == 'Short']

print(f"Total Symbols Backtested: {total_symbols}")
print(f"Total Trades: {len(all_trades):,}")
print(f"  - Long Trades: {len(long_trades):,} ({len(long_trades)/len(all_trades)*100:.1f}%)")
print(f"  - Short Trades: {len(short_trades):,} ({len(short_trades)/len(all_trades)*100:.1f}%)")
print()

# Long Performance
print("-"*80)
print("LONG SIGNALS PERFORMANCE")
print("-"*80)
long_winners = (long_trades['NetProfit'] > 0).sum()
long_losers = (long_trades['NetProfit'] < 0).sum()
long_wr = (long_trades['NetProfit'] > 0).mean() * 100
long_total_profit = long_trades[long_trades['NetProfit'] > 0]['NetProfit'].sum()
long_total_loss = abs(long_trades[long_trades['NetProfit'] < 0]['NetProfit'].sum())
long_pf = long_total_profit / long_total_loss if long_total_loss > 0 else 0

print(f"Winning Trades: {long_winners:,} ({long_wr:.2f}%)")
print(f"Losing Trades: {long_losers:,}")
print(f"Win Rate: {long_wr:.2f}%")
print(f"Profit Factor: {long_pf:.2f}")
print(f"Total Gross Profit: ${long_total_profit:,.2f}")
print(f"Total Gross Loss: ${long_total_loss:,.2f}")
print(f"Net Profit: ${long_total_profit - long_total_loss:,.2f}")
print(f"Average Trade: ${long_trades['NetProfit'].mean():.2f}")
print(f"Average Winner: ${long_trades[long_trades['NetProfit'] > 0]['NetProfit'].mean():.2f}")
print(f"Average Loser: ${long_trades[long_trades['NetProfit'] < 0]['NetProfit'].mean():.2f}")
print()

# Short Performance
print("-"*80)
print("SHORT SIGNALS PERFORMANCE")
print("-"*80)
short_winners = (short_trades['NetProfit'] > 0).sum()
short_losers = (short_trades['NetProfit'] < 0).sum()
short_wr = (short_trades['NetProfit'] > 0).mean() * 100
short_total_profit = short_trades[short_trades['NetProfit'] > 0]['NetProfit'].sum()
short_total_loss = abs(short_trades[short_trades['NetProfit'] < 0]['NetProfit'].sum())
short_pf = short_total_profit / short_total_loss if short_total_loss > 0 else 0

print(f"Winning Trades: {short_winners:,} ({short_wr:.2f}%)")
print(f"Losing Trades: {short_losers:,}")
print(f"Win Rate: {short_wr:.2f}%")
print(f"Profit Factor: {short_pf:.2f}")
print(f"Total Gross Profit: ${short_total_profit:,.2f}")
print(f"Total Gross Loss: ${short_total_loss:,.2f}")
print(f"Net Profit: ${short_total_profit - short_total_loss:,.2f}")
print(f"Average Trade: ${short_trades['NetProfit'].mean():.2f}")
print(f"Average Winner: ${short_trades[short_trades['NetProfit'] > 0]['NetProfit'].mean():.2f}")
print(f"Average Loser: ${short_trades[short_trades['NetProfit'] < 0]['NetProfit'].mean():.2f}")
print()

# Per-Symbol Summary
print("="*80)
print("2. PER-SYMBOL SUMMARY")
print("="*80)

symbol_summary = []

for symbol in sorted(all_trades['Symbol'].unique()):
    sym_long = long_trades[long_trades['Symbol'] == symbol]
    sym_short = short_trades[short_trades['Symbol'] == symbol]
    
    long_equity_final = all_equity[(all_equity['Symbol'] == symbol) & (all_equity['SignalType'] == 'Long')]
    short_equity_final = all_equity[(all_equity['Symbol'] == symbol) & (all_equity['SignalType'] == 'Short')]
    
    long_return = long_equity_final['NetProfitPct'].iloc[-1] if len(long_equity_final) > 0 else 0
    short_return = short_equity_final['NetProfitPct'].iloc[-1] if len(short_equity_final) > 0 else 0
    
    symbol_summary.append({
        'Symbol': symbol,
        'LongTrades': len(sym_long),
        'LongWR': (sym_long['NetProfit'] > 0).mean() * 100 if len(sym_long) > 0 else 0,
        'LongReturn': long_return,
        'ShortTrades': len(sym_short),
        'ShortWR': (sym_short['NetProfit'] > 0).mean() * 100 if len(sym_short) > 0 else 0,
        'ShortReturn': short_return,
        'TotalTrades': len(sym_long) + len(sym_short),
        'CombinedReturn': long_return + short_return
    })

symbol_summary_df = pd.DataFrame(symbol_summary)

print(f"{'Symbol':<8} {'Long Trades':<12} {'Long WR':<10} {'Long Ret%':<12} {'Short Trades':<13} {'Short WR':<10} {'Short Ret%':<12}")
print("-"*80)

for _, row in symbol_summary_df.head(20).iterrows():
    print(f"{row['Symbol']:<8} {row['LongTrades']:<12} {row['LongWR']:>8.1f}% {row['LongReturn']:>10.2f}% {row['ShortTrades']:<13} {row['ShortWR']:>8.1f}% {row['ShortReturn']:>10.2f}%")

print(f"\n... (showing first 20 of {len(symbol_summary_df)} symbols)")
print()

# Top Performers
print("="*80)
print("3. TOP 10 PERFORMERS (By Combined Long + Short Return)")
print("="*80)

top_performers = symbol_summary_df.nlargest(10, 'CombinedReturn')

print(f"{'Rank':<6} {'Symbol':<8} {'Long Ret%':<12} {'Short Ret%':<12} {'Combined%':<12} {'Total Trades':<12}")
print("-"*80)

for idx, (_, row) in enumerate(top_performers.iterrows(), 1):
    print(f"{idx:<6} {row['Symbol']:<8} {row['LongReturn']:>10.2f}% {row['ShortReturn']:>10.2f}% {row['CombinedReturn']:>10.2f}% {row['TotalTrades']:<12.0f}")

print()

# Worst Performers
print("="*80)
print("4. BOTTOM 10 PERFORMERS (By Combined Long + Short Return)")
print("="*80)

worst_performers = symbol_summary_df.nsmallest(10, 'CombinedReturn')

print(f"{'Rank':<6} {'Symbol':<8} {'Long Ret%':<12} {'Short Ret%':<12} {'Combined%':<12} {'Total Trades':<12}")
print("-"*80)

for idx, (_, row) in enumerate(worst_performers.iterrows(), 1):
    print(f"{idx:<6} {row['Symbol']:<8} {row['LongReturn']:>10.2f}% {row['ShortReturn']:>10.2f}% {row['CombinedReturn']:>10.2f}% {row['TotalTrades']:<12.0f}")

print()

# Exit Reason Analysis
print("="*80)
print("5. EXIT REASON ANALYSIS")
print("="*80)

exit_reasons = all_trades.groupby(['SignalType', 'ExitReason']).agg({
    'TradeNumber': 'count',
    'NetProfit': ['mean', 'sum']
}).round(2)

print(exit_reasons)
print()

# Path Group Analysis
print("="*80)
print("6. PATH GROUP PERFORMANCE")
print("="*80)

path_groups = all_trades.groupby(['SignalType', 'PathGroup']).agg({
    'TradeNumber': 'count',
    'NetProfit': ['mean', lambda x: (x > 0).mean() * 100]
}).round(2)

path_groups.columns = ['Count', 'AvgProfit', 'WinRate']
print(path_groups)
print()

# Save summary
symbol_summary_df.to_csv('/home/ubuntu/stage4_results/symbol_summary.csv', index=False)
print("Summary saved to: /home/ubuntu/stage4_results/symbol_summary.csv")
print()

print("="*80)
print("SUMMARY GENERATION COMPLETE!")
print("="*80)
