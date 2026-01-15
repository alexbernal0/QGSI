#!/usr/bin/env python3.11
"""
Part III - Section A: Strategy Comparison Analysis
Calculates all strategy comparison metrics, combined portfolio simulation,
correlation analysis, and optimal allocation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PART III - SECTION A: STRATEGY COMPARISON ANALYSIS")
print("="*80)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[1/8] Loading LONG and SHORT strategy data...")

long_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
long_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
long_summary = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Summary.csv')
long_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv', index_col=0)

short_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Trades.parquet')
short_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Equity.parquet')
short_summary = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Summary.csv')
short_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Extended_Metrics.csv', index_col=0)

print(f"✓ LONG: {len(long_trades)} trades, {len(long_equity)} equity points")
print(f"✓ SHORT: {len(short_trades)} trades, {len(short_equity)} equity points")

# ============================================================================
# A.1: PERFORMANCE COMPARISON TABLE
# ============================================================================
print("\n[2/8] Creating performance comparison table...")

comparison_data = []

metrics_to_compare = [
    ('Final Equity', 'FinalEquity', 'summary', '$'),
    ('Net Profit', 'NetProfit', 'summary', '$'),
    ('Total Return', 'Cumulative Return', 'metrics', '%'),
    ('CAGR', 'CAGR', 'metrics', '%'),
    ('Sharpe Ratio', 'Sharpe', 'metrics', ''),
    ('Sortino Ratio', 'Sortino', 'metrics', ''),
    ('Calmar Ratio', 'Calmar', 'metrics', ''),
    ('Max Drawdown', 'Max Drawdown', 'metrics', '%'),
    ('Volatility (ann.)', 'Volatility (ann.)', 'metrics', '%'),
    ('Profit Factor (Daily)', 'Profit Factor', 'metrics', ''),
    ('Win Rate', 'WinRate', 'summary', '%'),
    ('Total Trades', 'TotalTrades', 'summary', ''),
    ('Avg Trade Duration (min)', 'AvgTradeDuration', 'summary', 'min'),
    ('Avg Profit per Trade', 'AvgProfit', 'summary', '$'),
    ('Kelly Criterion', 'Kelly Criterion', 'metrics', '%'),
]

for metric_name, metric_key, source, unit in metrics_to_compare:
    if source == 'summary':
        long_val = long_summary[metric_key].iloc[0] if metric_key in long_summary.columns else 0
        short_val = short_summary[metric_key].iloc[0] if metric_key in short_summary.columns else 0
    else:  # metrics
        long_val = long_metrics.loc[metric_key, 'Value'] if metric_key in long_metrics.index else 0
        short_val = short_metrics.loc[metric_key, 'Value'] if metric_key in short_metrics.index else 0
    
    # Calculate difference
    if 'Drawdown' in metric_name:
        diff = short_val - long_val  # For drawdown, less negative is better
        better = 'SHORT' if diff > 0 else 'LONG'
    else:
        diff = short_val - long_val
        better = 'SHORT' if diff > 0 else 'LONG'
    
    comparison_data.append({
        'Metric': metric_name,
        'LONG': long_val,
        'SHORT': short_val,
        'Difference': diff,
        'Better': better,
        'Unit': unit
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df.to_csv('/home/ubuntu/stage4_optimization/part3_a1_performance_comparison.csv', index=False)
print(f"✓ Performance comparison table saved ({len(comparison_df)} metrics)")

# ============================================================================
# A.2: COMBINED PORTFOLIO SIMULATION
# ============================================================================
print("\n[3/8] Running combined portfolio simulation...")

# Prepare combined trade log
long_trades_sim = long_trades.copy()
long_trades_sim['Strategy'] = 'LONG'
short_trades_sim = short_trades.copy()
short_trades_sim['Strategy'] = 'SHORT'

combined_trades = pd.concat([long_trades_sim, short_trades_sim], ignore_index=True)
combined_trades = combined_trades.sort_values('EntryTime').reset_index(drop=True)

print(f"  Combined trade universe: {len(combined_trades)} potential trades")

# Simulate combined portfolio with shared capital and position limit
starting_capital = 1000000
max_positions = 10
position_size_pct = 0.10

equity = starting_capital
open_positions = []
equity_curve = []
taken_trades = []

for idx, trade in combined_trades.iterrows():
    entry_time = trade['EntryTime']
    
    # Process exits first
    closed_positions = []
    for pos in open_positions:
        if pos['ExitTime'] <= entry_time:
            # Close position
            equity += pos['PnL']
            closed_positions.append(pos)
    
    # Remove closed positions
    for pos in closed_positions:
        open_positions.remove(pos)
    
    # Check if we can take new position
    if len(open_positions) < max_positions:
        # Calculate position size
        position_value = equity * position_size_pct
        shares = int(position_value / trade['EntryPrice'])
        
        if shares > 0:
            # Take the trade
            position = {
                'Symbol': trade['Symbol'],
                'Strategy': trade['Strategy'],
                'EntryTime': trade['EntryTime'],
                'ExitTime': trade['ExitTime'],
                'EntryPrice': trade['EntryPrice'],
                'ExitPrice': trade['ExitPrice'],
                'Shares': shares,
                'PnL': trade['NetProfit'] * (shares / trade['Shares']) if trade['Shares'] > 0 else trade['NetProfit']
            }
            open_positions.append(position)
            taken_trades.append(position)
    
    # Record equity
    current_unrealized_pnl = sum([p['PnL'] for p in open_positions])
    equity_curve.append({
        'Timestamp': entry_time,
        'Equity': equity + current_unrealized_pnl,
        'OpenPositions': len(open_positions),
        'LongPositions': sum([1 for p in open_positions if p['Strategy'] == 'LONG']),
        'ShortPositions': sum([1 for p in open_positions if p['Strategy'] == 'SHORT'])
    })

# Close remaining positions
for pos in open_positions:
    equity += pos['PnL']

combined_equity_df = pd.DataFrame(equity_curve)
combined_trades_df = pd.DataFrame(taken_trades)

# Calculate combined metrics
final_equity = equity
net_profit = final_equity - starting_capital
total_return = (net_profit / starting_capital) * 100

# Calculate daily returns
combined_equity_df['Date'] = pd.to_datetime(combined_equity_df['Timestamp']).dt.date
daily_equity = combined_equity_df.groupby('Date')['Equity'].last().reset_index()
daily_equity['Returns'] = daily_equity['Equity'].pct_change()
daily_returns = daily_equity['Returns'].dropna()

sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
sortino = (daily_returns.mean() / daily_returns[daily_returns < 0].std()) * np.sqrt(252) if len(daily_returns[daily_returns < 0]) > 0 else 0

# Max drawdown
cummax = daily_equity['Equity'].cummax()
drawdown = (daily_equity['Equity'] - cummax) / cummax * 100
max_dd = drawdown.min()

combined_summary = {
    'Final Equity': final_equity,
    'Net Profit': net_profit,
    'Total Return (%)': total_return,
    'Sharpe Ratio': sharpe,
    'Sortino Ratio': sortino,
    'Max Drawdown (%)': max_dd,
    'Total Trades': len(combined_trades_df),
    'LONG Trades': len([t for t in taken_trades if t['Strategy'] == 'LONG']),
    'SHORT Trades': len([t for t in taken_trades if t['Strategy'] == 'SHORT']),
    'Avg Positions': combined_equity_df['OpenPositions'].mean(),
    'Max Positions Used': combined_equity_df['OpenPositions'].max(),
}

combined_summary_df = pd.DataFrame([combined_summary])
combined_summary_df.to_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_portfolio_summary.csv', index=False)
combined_equity_df.to_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_equity_curve.csv', index=False)
combined_trades_df.to_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_trades.csv', index=False)

print(f"✓ Combined portfolio: ${final_equity:,.2f} ({total_return:.2f}% return)")
print(f"  LONG trades: {combined_summary['LONG Trades']}, SHORT trades: {combined_summary['SHORT Trades']}")

# ============================================================================
# A.3: CORRELATION ANALYSIS
# ============================================================================
print("\n[4/8] Calculating correlation analysis...")

# Align equity curves by date
long_equity['Date'] = pd.to_datetime(long_equity['Timestamp']).dt.date
short_equity['Date'] = pd.to_datetime(short_equity['Timestamp']).dt.date

long_daily = long_equity.groupby('Date')['Equity'].last().reset_index()
short_daily = short_equity.groupby('Date')['Equity'].last().reset_index()

merged_daily = pd.merge(long_daily, short_daily, on='Date', suffixes=('_long', '_short'))
merged_daily['Long_Returns'] = merged_daily['Equity_long'].pct_change()
merged_daily['Short_Returns'] = merged_daily['Equity_short'].pct_change()

# Overall correlation
correlation = merged_daily[['Long_Returns', 'Short_Returns']].corr().iloc[0, 1]

# Rolling 30-day correlation
merged_daily['Rolling_Corr'] = merged_daily['Long_Returns'].rolling(30).corr(merged_daily['Short_Returns'])

# Drawdown correlation
long_cummax = merged_daily['Equity_long'].cummax()
short_cummax = merged_daily['Equity_short'].cummax()
merged_daily['Long_DD'] = (merged_daily['Equity_long'] - long_cummax) / long_cummax * 100
merged_daily['Short_DD'] = (merged_daily['Equity_short'] - short_cummax) / short_cummax * 100

merged_daily['Both_In_DD'] = (merged_daily['Long_DD'] < -0.1) & (merged_daily['Short_DD'] < -0.1)
dd_overlap_pct = merged_daily['Both_In_DD'].sum() / len(merged_daily) * 100

correlation_summary = {
    'Daily Returns Correlation': correlation,
    'Avg Rolling 30-Day Correlation': merged_daily['Rolling_Corr'].mean(),
    'Drawdown Overlap (% of days)': dd_overlap_pct,
    'Long Avg DD': merged_daily['Long_DD'].mean(),
    'Short Avg DD': merged_daily['Short_DD'].mean(),
}

correlation_df = pd.DataFrame([correlation_summary])
correlation_df.to_csv('/home/ubuntu/stage4_optimization/part3_a3_correlation_summary.csv', index=False)
merged_daily.to_csv('/home/ubuntu/stage4_optimization/part3_a3_daily_returns_correlation.csv', index=False)

print(f"✓ Correlation: {correlation:.4f}")
print(f"  Drawdown overlap: {dd_overlap_pct:.1f}% of days")

# ============================================================================
# A.4: TRADE DISTRIBUTION ANALYSIS
# ============================================================================
print("\n[5/8] Analyzing trade distribution patterns...")

# Add time features
long_trades['Hour'] = pd.to_datetime(long_trades['EntryTime']).dt.hour
long_trades['DayOfWeek'] = pd.to_datetime(long_trades['EntryTime']).dt.dayofweek
long_trades['Month'] = pd.to_datetime(long_trades['EntryTime']).dt.month
long_trades['Strategy'] = 'LONG'

short_trades['Hour'] = pd.to_datetime(short_trades['EntryTime']).dt.hour
short_trades['DayOfWeek'] = pd.to_datetime(short_trades['EntryTime']).dt.dayofweek
short_trades['Month'] = pd.to_datetime(short_trades['EntryTime']).dt.month
short_trades['Strategy'] = 'SHORT'

all_trades = pd.concat([long_trades, short_trades], ignore_index=True)

# Trades by hour
trades_by_hour = all_trades.groupby(['Strategy', 'Hour']).size().reset_index(name='Count')
trades_by_hour_pivot = trades_by_hour.pivot(index='Hour', columns='Strategy', values='Count').fillna(0)

# Trades by day of week
trades_by_dow = all_trades.groupby(['Strategy', 'DayOfWeek']).size().reset_index(name='Count')
trades_by_dow_pivot = trades_by_dow.pivot(index='DayOfWeek', columns='Strategy', values='Count').fillna(0)

# Trades by month
trades_by_month = all_trades.groupby(['Strategy', 'Month']).size().reset_index(name='Count')
trades_by_month_pivot = trades_by_month.pivot(index='Month', columns='Strategy', values='Count').fillna(0)

trades_by_hour_pivot.to_csv('/home/ubuntu/stage4_optimization/part3_a4_trades_by_hour.csv')
trades_by_dow_pivot.to_csv('/home/ubuntu/stage4_optimization/part3_a4_trades_by_dayofweek.csv')
trades_by_month_pivot.to_csv('/home/ubuntu/stage4_optimization/part3_a4_trades_by_month.csv')

print(f"✓ Trade distribution analysis complete")
print(f"  Peak hour - LONG: {trades_by_hour_pivot['LONG'].idxmax()}:00, SHORT: {trades_by_hour_pivot['SHORT'].idxmax()}:00")

# ============================================================================
# A.5: SYMBOL ANALYSIS
# ============================================================================
print("\n[6/8] Analyzing symbol overlap and performance...")

long_symbols = set(long_trades['Symbol'].unique())
short_symbols = set(short_trades['Symbol'].unique())

overlap_symbols = long_symbols & short_symbols
long_only_symbols = long_symbols - short_symbols
short_only_symbols = short_symbols - long_symbols

# Symbol performance
long_symbol_perf = long_trades.groupby('Symbol').agg({
    'NetProfit': ['sum', 'mean', 'count'],
    
}).reset_index()
long_symbol_perf.columns = ['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count']
long_symbol_perf['Strategy'] = 'LONG'

short_symbol_perf = short_trades.groupby('Symbol').agg({
    'NetProfit': ['sum', 'mean', 'count'],
    
}).reset_index()
short_symbol_perf.columns = ['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count']
short_symbol_perf['Strategy'] = 'SHORT'

# Top symbols
top_long = long_symbol_perf.nlargest(20, 'Total_PnL')
top_short = short_symbol_perf.nlargest(20, 'Total_PnL')

symbol_summary = {
    'Total Unique Symbols': len(long_symbols | short_symbols),
    'LONG Only': len(long_only_symbols),
    'SHORT Only': len(short_only_symbols),
    'Both Strategies': len(overlap_symbols),
    'Overlap Rate (%)': len(overlap_symbols) / len(long_symbols | short_symbols) * 100
}

symbol_summary_df = pd.DataFrame([symbol_summary])
symbol_summary_df.to_csv('/home/ubuntu/stage4_optimization/part3_a5_symbol_summary.csv', index=False)
long_symbol_perf.to_csv('/home/ubuntu/stage4_optimization/part3_a5_long_symbol_performance.csv', index=False)
short_symbol_perf.to_csv('/home/ubuntu/stage4_optimization/part3_a5_short_symbol_performance.csv', index=False)
top_long.to_csv('/home/ubuntu/stage4_optimization/part3_a5_top20_long_symbols.csv', index=False)
top_short.to_csv('/home/ubuntu/stage4_optimization/part3_a5_top20_short_symbols.csv', index=False)

print(f"✓ Symbol analysis complete")
print(f"  Total symbols: {symbol_summary['Total Unique Symbols']}, Overlap: {len(overlap_symbols)} ({symbol_summary['Overlap Rate (%)']:.1f}%)")

# ============================================================================
# A.6: RISK CONTRIBUTION ANALYSIS
# ============================================================================
print("\n[7/8] Calculating risk contribution...")

# Calculate individual volatilities
long_vol = daily_returns.std() * np.sqrt(252) if 'daily_returns' in dir() else long_metrics.loc['Volatility (ann.)', 'Value']
short_vol = short_metrics.loc['Volatility (ann.)', 'Value']

# For 50/50 portfolio
weight_long = 0.5
weight_short = 0.5

# Portfolio volatility (accounting for correlation)
portfolio_vol = np.sqrt(
    (weight_long**2 * (long_vol/100)**2) + 
    (weight_short**2 * (short_vol/100)**2) + 
    (2 * weight_long * weight_short * (long_vol/100) * (short_vol/100) * correlation)
) * 100

# Marginal risk contribution
long_marginal = (weight_long * (long_vol/100)**2 + weight_short * (long_vol/100) * (short_vol/100) * correlation) / (portfolio_vol/100)
short_marginal = (weight_short * (short_vol/100)**2 + weight_long * (long_vol/100) * (short_vol/100) * correlation) / (portfolio_vol/100)

# Risk contribution (%)
long_risk_contrib = (long_marginal * weight_long) / (portfolio_vol/100) * 100
short_risk_contrib = (short_marginal * weight_short) / (portfolio_vol/100) * 100

# Diversification benefit
weighted_avg_vol = weight_long * long_vol + weight_short * short_vol
diversification_benefit = weighted_avg_vol - portfolio_vol

risk_contrib = {
    'LONG Volatility (%)': long_vol,
    'SHORT Volatility (%)': short_vol,
    'Portfolio Volatility (50/50) (%)': portfolio_vol,
    'LONG Risk Contribution (%)': long_risk_contrib,
    'SHORT Risk Contribution (%)': short_risk_contrib,
    'Diversification Benefit (%)': diversification_benefit,
    'Correlation': correlation
}

risk_contrib_df = pd.DataFrame([risk_contrib])
risk_contrib_df.to_csv('/home/ubuntu/stage4_optimization/part3_a6_risk_contribution.csv', index=False)

print(f"✓ Risk contribution: LONG {long_risk_contrib:.1f}%, SHORT {short_risk_contrib:.1f}%")
print(f"  Diversification benefit: {diversification_benefit:.2f}%")

# ============================================================================
# A.7: OPTIMAL ALLOCATION ANALYSIS
# ============================================================================
print("\n[8/8] Finding optimal allocation...")

# Test allocations from 0/100 to 100/0
allocations = []

for long_weight in np.arange(0, 1.05, 0.05):
    short_weight = 1 - long_weight
    
    # Expected return (weighted)
    long_return = long_metrics.loc['CAGR', 'Value'] / 100
    short_return = short_metrics.loc['CAGR', 'Value'] / 100
    portfolio_return = long_weight * long_return + short_weight * short_return
    
    # Portfolio volatility
    port_vol = np.sqrt(
        (long_weight**2 * (long_vol/100)**2) + 
        (short_weight**2 * (short_vol/100)**2) + 
        (2 * long_weight * short_weight * (long_vol/100) * (short_vol/100) * correlation)
    )
    
    # Sharpe ratio
    sharpe_ratio = portfolio_return / port_vol if port_vol > 0 else 0
    
    # Max drawdown (weighted approximation)
    long_dd = abs(long_metrics.loc['Max Drawdown', 'Value'])
    short_dd = abs(short_metrics.loc['Max Drawdown', 'Value'])
    portfolio_dd = -(long_weight * long_dd + short_weight * short_dd)
    
    # Calmar ratio
    calmar_ratio = (portfolio_return * 100) / abs(portfolio_dd) if portfolio_dd != 0 else 0
    
    allocations.append({
        'LONG Weight (%)': long_weight * 100,
        'SHORT Weight (%)': short_weight * 100,
        'Expected Return (%)': portfolio_return * 100,
        'Volatility (%)': port_vol * 100,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown (%)': portfolio_dd,
        'Calmar Ratio': calmar_ratio
    })

allocation_df = pd.DataFrame(allocations)
allocation_df.to_csv('/home/ubuntu/stage4_optimization/part3_a7_optimal_allocation.csv', index=False)

# Find optimal
optimal_sharpe = allocation_df.loc[allocation_df['Sharpe Ratio'].idxmax()]
optimal_calmar = allocation_df.loc[allocation_df['Calmar Ratio'].idxmax()]

print(f"✓ Optimal allocation (max Sharpe): {optimal_sharpe['LONG Weight (%)']:.0f}% LONG / {optimal_sharpe['SHORT Weight (%)']:.0f}% SHORT")
print(f"  Sharpe: {optimal_sharpe['Sharpe Ratio']:.4f}, Return: {optimal_sharpe['Expected Return (%)']:.2f}%")

print("\n" + "="*80)
print("SECTION A COMPLETE - All strategy comparison metrics calculated")
print("="*80)
print(f"\nFiles created:")
print(f"  - part3_a1_performance_comparison.csv")
print(f"  - part3_a2_combined_portfolio_summary.csv")
print(f"  - part3_a2_combined_equity_curve.csv")
print(f"  - part3_a2_combined_trades.csv")
print(f"  - part3_a3_correlation_summary.csv")
print(f"  - part3_a3_daily_returns_correlation.csv")
print(f"  - part3_a4_trades_by_hour.csv")
print(f"  - part3_a4_trades_by_dayofweek.csv")
print(f"  - part3_a4_trades_by_month.csv")
print(f"  - part3_a5_symbol_summary.csv")
print(f"  - part3_a5_long_symbol_performance.csv")
print(f"  - part3_a5_short_symbol_performance.csv")
print(f"  - part3_a5_top20_long_symbols.csv")
print(f"  - part3_a5_top20_short_symbols.csv")
print(f"  - part3_a6_risk_contribution.csv")
print(f"  - part3_a7_optimal_allocation.csv")
print("="*80)
