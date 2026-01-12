"""
QGSI Stage 4 Diagnostics: Investigate Abnormally Large Losses
==============================================================

Purpose: Investigate symbols with abnormally large losses in Stage 4 baseline ATR strategy.
         With a fixed 3.0× ATR stop loss, massive drawdowns should not occur unless there
         are implementation issues or data quality problems.

Author: QGSI Research Team
Date: 2026-01-11
Repository: https://github.com/alexbernal0/QGSI

Analysis Steps:
1. Query MotherDuck for worst performing symbols (both Long and Short)
2. Examine individual trade logs for these symbols
3. Calculate statistics: max loss per trade, consecutive losses, stop loss execution
4. Identify anomalies: trades exceeding expected 3.0× ATR loss, missing stops, etc.
5. Generate diagnostic report with findings

Expected Behavior:
- Maximum loss per trade should be ~3.0× ATR (plus slippage)
- Large cumulative losses should come from many small losses, not single huge losses
- Stop losses should be executed consistently

Red Flags:
- Single trade losses > 5× ATR
- Trades with no stop loss execution
- Gaps in trade sequence suggesting missing data
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# MotherDuck connection
MOTHERDUCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs"

print("=" * 80)
print("QGSI STAGE 4 DIAGNOSTICS: INVESTIGATING LARGE LOSSES")
print("=" * 80)

# Connect to MotherDuck
conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')

print("\n[1/6] Querying worst performing symbols...")

# Get summary statistics by symbol and signal type
query_summary = """
SELECT 
    Symbol,
    SignalType,
    COUNT(*) as TotalTrades,
    SUM(NetProfit) as TotalNetProfit,
    AVG(NetProfit) as AvgNetProfit,
    MIN(NetProfit) as WorstTrade,
    MAX(NetProfit) as BestTrade,
    SUM(CASE WHEN NetProfit > 0 THEN 1 ELSE 0 END) as WinningTrades,
    SUM(CASE WHEN NetProfit <= 0 THEN 1 ELSE 0 END) as LosingTrades,
    SUM(CASE WHEN NetProfit > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as WinRate,
    MIN(NetProfitPct) as WorstTradePct,
    MAX(MAE) as MaxMAE,
    AVG(ATR) as AvgATR
FROM QGSI.stage4_all_trades
GROUP BY Symbol, SignalType
ORDER BY TotalNetProfit ASC
LIMIT 50
"""

worst_performers = conn.execute(query_summary).df()
print(f"✓ Found {len(worst_performers)} worst performing symbol-signal combinations")
print("\nTop 20 Worst Performers:")
print(worst_performers.head(20).to_string(index=False))

print("\n[2/6] Examining individual trades for worst performers...")

# Get detailed trades for top 10 worst performers
worst_symbols = worst_performers.head(10)[['Symbol', 'SignalType']].values

all_problem_trades = []

for symbol, signal_type in worst_symbols:
    print(f"\n  Analyzing {symbol} {signal_type}...")
    
    query_trades = f"""
    SELECT *
    FROM QGSI.stage4_all_trades
    WHERE Symbol = '{symbol}' AND SignalType = '{signal_type}'
    ORDER BY EntryTime
    """
    
    trades = conn.execute(query_trades).df()
    
    # Identify problem trades (losses > 5% which is abnormally large for 3× ATR)
    # or trades where loss exceeds 4× ATR
    problem_trades = trades[
        (trades['NetProfitPct'] < -5.0) | 
        ((trades['ExitReason'] == 'StopLoss') & (abs(trades['NetProfitPct']) > 4.0))
    ].copy()
    
    if len(problem_trades) > 0:
        print(f"    ⚠️  Found {len(problem_trades)} trades with abnormal losses")
        problem_trades['Symbol'] = symbol
        problem_trades['SignalTypeName'] = signal_type
        all_problem_trades.append(problem_trades)
    
    # Check for consecutive losses
    trades['IsLoss'] = trades['NetProfit'] < 0
    trades['ConsecLosses'] = trades['IsLoss'].groupby((~trades['IsLoss']).cumsum()).cumsum()
    max_consec = trades['ConsecLosses'].max()
    
    print(f"    Total trades: {len(trades)}")
    print(f"    Worst single trade: ${trades['NetProfit'].min():.2f} ({trades['NetProfitPct'].min():.2f}%)")
    print(f"    Max MAE: ${trades['MAE'].min():.2f}")
    print(f"    Max consecutive losses: {max_consec}")
    print(f"    Total P&L: ${trades['NetProfit'].sum():.2f}")
    print(f"    Avg ATR: ${trades['ATR'].mean():.4f}")

if all_problem_trades:
    problem_df = pd.concat(all_problem_trades, ignore_index=True)
    print(f"\n✓ Total problem trades identified: {len(problem_df)}")
else:
    print("\n✓ No trades with abnormally large losses found")
    problem_df = pd.DataFrame()

print("\n[3/6] Analyzing stop loss execution patterns...")

# Analyze exit reasons
query_exit_reasons = """
SELECT 
    ExitReason,
    COUNT(*) as Count,
    AVG(NetProfit) as AvgProfit,
    MIN(NetProfit) as MinProfit,
    MAX(NetProfit) as MaxProfit,
    AVG(NetProfitPct) as AvgProfitPct,
    MIN(NetProfitPct) as MinProfitPct
FROM QGSI.stage4_all_trades
WHERE ExitReason IS NOT NULL
GROUP BY ExitReason
ORDER BY Count DESC
"""

exit_reasons = conn.execute(query_exit_reasons).df()
print("✓ Exit reason distribution:")
print(exit_reasons.to_string(index=False))

print("\n[4/6] Checking for data quality issues...")

# Check for missing or invalid data
query_data_quality = """
SELECT 
    COUNT(*) as TotalTrades,
    SUM(CASE WHEN EntryPrice IS NULL OR EntryPrice <= 0 THEN 1 ELSE 0 END) as InvalidEntryPrice,
    SUM(CASE WHEN ExitPrice IS NULL OR ExitPrice <= 0 THEN 1 ELSE 0 END) as InvalidExitPrice,
    SUM(CASE WHEN ATR IS NULL OR ATR <= 0 THEN 1 ELSE 0 END) as InvalidATR,
    SUM(CASE WHEN StopLoss IS NULL THEN 1 ELSE 0 END) as MissingStopLoss,
    SUM(CASE WHEN ProfitTarget IS NULL THEN 1 ELSE 0 END) as MissingTarget,
    SUM(CASE WHEN ExitReason IS NULL THEN 1 ELSE 0 END) as MissingExitReason
FROM QGSI.stage4_all_trades
"""

data_quality = conn.execute(query_data_quality).df()
print("✓ Data quality check:")
print(data_quality.to_string(index=False))

print("\n[5/6] Analyzing loss distribution across all trades...")

# Get distribution of worst losses
query_loss_dist = """
SELECT 
    Symbol,
    SignalType,
    NetProfit,
    NetProfitPct,
    EntryPrice,
    ExitPrice,
    ATR,
    StopLoss,
    ProfitTarget,
    ExitReason,
    BarsInTrade,
    MAE,
    MFE,
    PathGroup
FROM QGSI.stage4_all_trades
WHERE NetProfit < 0
ORDER BY NetProfit ASC
LIMIT 100
"""

worst_losses = conn.execute(query_loss_dist).df()

# Calculate how many ATR the loss represents
worst_losses['LossInATR'] = abs(worst_losses['ExitPrice'] - worst_losses['EntryPrice']) / worst_losses['ATR']

print(f"✓ Analyzed {len(worst_losses)} worst individual trades")
print("\nTop 20 Worst Individual Trades:")
print(worst_losses[['Symbol', 'SignalType', 'NetProfit', 'NetProfitPct', 'LossInATR', 'ExitReason', 'BarsInTrade', 'PathGroup']].head(20).to_string(index=False))

# Check if losses exceed expected 3× ATR
excessive_losses = worst_losses[worst_losses['LossInATR'] > 4.0]  # 4× ATR = concerning
print(f"\n⚠️  Trades with loss > 4× ATR: {len(excessive_losses)}")

if len(excessive_losses) > 0:
    print("\nExcessive loss examples:")
    print(excessive_losses[['Symbol', 'SignalType', 'NetProfit', 'NetProfitPct', 'LossInATR', 'ExitReason', 'StopLoss', 'EntryPrice', 'ExitPrice']].head(10).to_string(index=False))

# Analyze stop loss exits specifically
print("\n[6/6] Analyzing stop loss exits in detail...")

query_stop_losses = """
SELECT 
    Symbol,
    SignalType,
    NetProfit,
    NetProfitPct,
    EntryPrice,
    ExitPrice,
    StopLoss,
    ATR,
    BarsInTrade
FROM QGSI.stage4_all_trades
WHERE ExitReason = 'StopLoss'
ORDER BY NetProfitPct ASC
LIMIT 50
"""

stop_loss_trades = conn.execute(query_stop_losses).df()

# Calculate actual stop distance vs expected
stop_loss_trades['ActualStopDistance'] = abs(stop_loss_trades['ExitPrice'] - stop_loss_trades['EntryPrice'])
stop_loss_trades['ExpectedStopDistance'] = abs(stop_loss_trades['StopLoss'] - stop_loss_trades['EntryPrice'])
stop_loss_trades['StopDistanceRatio'] = stop_loss_trades['ActualStopDistance'] / stop_loss_trades['ExpectedStopDistance']
stop_loss_trades['LossInATR'] = stop_loss_trades['ActualStopDistance'] / stop_loss_trades['ATR']

print(f"✓ Analyzed {len(stop_loss_trades)} stop loss exits")
print("\nWorst stop loss exits:")
print(stop_loss_trades[['Symbol', 'SignalType', 'NetProfit', 'NetProfitPct', 'LossInATR', 'StopDistanceRatio', 'BarsInTrade']].head(20).to_string(index=False))

# Check for stops that went way beyond expected
bad_stops = stop_loss_trades[stop_loss_trades['StopDistanceRatio'] > 1.5]
print(f"\n⚠️  Stop losses that exceeded expected distance by >50%: {len(bad_stops)}")

if len(bad_stops) > 0:
    print("\nExamples of stops that went too far:")
    print(bad_stops[['Symbol', 'SignalType', 'NetProfitPct', 'StopDistanceRatio', 'LossInATR', 'EntryPrice', 'ExitPrice', 'StopLoss']].head(10).to_string(index=False))

print("\n[7/7] Saving diagnostic results...")

# Save results
output_dir = Path('/home/ubuntu/stage4_diagnostics')
output_dir.mkdir(exist_ok=True)

worst_performers.to_parquet(output_dir / 'worst_performers_summary.parquet')
worst_losses.to_parquet(output_dir / 'worst_individual_trades.parquet')
exit_reasons.to_parquet(output_dir / 'exit_reason_analysis.parquet')
stop_loss_trades.to_parquet(output_dir / 'stop_loss_analysis.parquet')

if not problem_df.empty:
    problem_df.to_parquet(output_dir / 'problem_trades_abnormal.parquet')

data_quality.to_parquet(output_dir / 'data_quality_check.parquet')

print(f"✓ Results saved to {output_dir}")

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

print(f"\n📊 Total trades analyzed: {data_quality['TotalTrades'].iloc[0]:,}")
print(f"📊 Worst performers identified: {len(worst_performers)}")
print(f"📊 Problem trades (abnormal losses): {len(problem_df) if not problem_df.empty else 0}")
print(f"📊 Trades with loss > 4× ATR: {len(excessive_losses)}")
print(f"📊 Stop losses exceeding expected by >50%: {len(bad_stops)}")

print("\n🔍 KEY FINDINGS:")

if len(excessive_losses) > 0:
    print(f"⚠️  CRITICAL: Found {len(excessive_losses)} trades with losses exceeding 4× ATR")
    print("   This suggests stop loss may not be executing properly or there are data gaps")
    
if len(bad_stops) > 0:
    print(f"⚠️  WARNING: Found {len(bad_stops)} stop losses that exceeded expected distance by >50%")
    print("   This could indicate slippage, gaps, or stop calculation errors")

if data_quality['InvalidEntryPrice'].iloc[0] > 0 or data_quality['InvalidExitPrice'].iloc[0] > 0:
    print(f"⚠️  WARNING: Found invalid price data (Entry: {data_quality['InvalidEntryPrice'].iloc[0]}, Exit: {data_quality['InvalidExitPrice'].iloc[0]})")

if data_quality['MissingStopLoss'].iloc[0] > 0:
    print(f"⚠️  WARNING: Found {data_quality['MissingStopLoss'].iloc[0]} trades with missing stop loss")

# Get worst symbol overall
worst_symbol = worst_performers.iloc[0]
print(f"\n🏆 Worst Performer: {worst_symbol['Symbol']} ({worst_symbol['SignalType']})")
print(f"   Total P&L: ${worst_symbol['TotalNetProfit']:.2f}")
print(f"   Total Trades: {worst_symbol['TotalTrades']}")
print(f"   Win Rate: {worst_symbol['WinRate']:.1f}%")
print(f"   Worst Single Trade: ${worst_symbol['WorstTrade']:.2f} ({worst_symbol['WorstTradePct']:.2f}%)")

conn.close()
print("\n✓ Analysis complete!")
