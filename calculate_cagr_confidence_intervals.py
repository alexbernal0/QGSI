#!/usr/bin/env python3.11
"""
Calculate 1-Year CAGR Estimation with Statistical Confidence Intervals
Using Bootstrap Resampling from Combined Portfolio Daily Returns
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("1-YEAR CAGR ESTIMATION WITH CONFIDENCE INTERVALS")
print("="*80)

# Load combined portfolio equity curve
equity_file = Path("/home/ubuntu/stage4_optimization/part3_a2_combined_equity_curve.csv")
equity_df = pd.read_csv(equity_file, parse_dates=['Date'])

print(f"\nLoaded combined equity curve: {len(equity_df)} timestamps")

# Aggregate to end-of-day equity (last timestamp of each day)
daily_equity = equity_df.groupby('Date').agg({
    'Equity': 'last'
}).reset_index()

print(f"Aggregated to daily data: {len(daily_equity)} trading days")
print(f"Date range: {daily_equity['Date'].min()} to {daily_equity['Date'].max()}")
print(f"Starting equity: ${daily_equity['Equity'].iloc[0]:,.2f}")
print(f"Ending equity: ${daily_equity['Equity'].iloc[-1]:,.2f}")

# Calculate daily returns
daily_equity['Daily_Return'] = daily_equity['Equity'].pct_change()
daily_returns = daily_equity['Daily_Return'].dropna().values

print(f"\nDaily returns calculated: {len(daily_returns)} days")
print(f"Mean daily return: {daily_returns.mean():.4f} ({daily_returns.mean()*100:.2f}%)")
print(f"Std daily return: {daily_returns.std():.4f} ({daily_returns.std()*100:.2f}%)")

# Calculate current annualized return (from actual 147 days)
actual_days = len(daily_returns)
actual_total_return = (daily_equity['Equity'].iloc[-1] / daily_equity['Equity'].iloc[0]) - 1
actual_cagr = (1 + actual_total_return) ** (252 / actual_days) - 1

print(f"\nActual performance over {actual_days} days:")
print(f"Total return: {actual_total_return*100:.2f}%")
print(f"Annualized CAGR: {actual_cagr*100:.2f}%")

# Bootstrap resampling
print("\n" + "="*80)
print("BOOTSTRAP RESAMPLING (10,000 SIMULATIONS)")
print("="*80)

np.random.seed(42)
n_simulations = 10000
trading_days_per_year = 252

bootstrap_cagrs = []

for i in range(n_simulations):
    # Resample daily returns with replacement
    sampled_returns = np.random.choice(daily_returns, size=trading_days_per_year, replace=True)
    
    # Calculate CAGR for this sample
    cumulative_return = np.prod(1 + sampled_returns) - 1
    bootstrap_cagrs.append(cumulative_return * 100)  # Convert to percentage
    
    if (i + 1) % 2000 == 0:
        print(f"Progress: {i+1:,} / {n_simulations:,} simulations complete")

bootstrap_cagrs = np.array(bootstrap_cagrs)

print("\n" + "="*80)
print("STATISTICAL RESULTS")
print("="*80)

# Calculate statistics
mean_cagr = np.mean(bootstrap_cagrs)
median_cagr = np.median(bootstrap_cagrs)
std_cagr = np.std(bootstrap_cagrs)

# Confidence intervals
ci_95_lower = np.percentile(bootstrap_cagrs, 2.5)
ci_95_upper = np.percentile(bootstrap_cagrs, 97.5)
ci_68_lower = np.percentile(bootstrap_cagrs, 16)
ci_68_upper = np.percentile(bootstrap_cagrs, 84)

# Scenarios
pessimistic = np.percentile(bootstrap_cagrs, 10)
optimistic = np.percentile(bootstrap_cagrs, 90)

# Probability of positive return
prob_positive = (bootstrap_cagrs > 0).sum() / len(bootstrap_cagrs) * 100

print(f"\nExpected CAGR (Mean): {mean_cagr:.2f}%")
print(f"Median CAGR: {median_cagr:.2f}%")
print(f"Standard Deviation: {std_cagr:.2f}%")
print(f"\n95% Confidence Interval: [{ci_95_lower:.2f}%, {ci_95_upper:.2f}%]")
print(f"68% Confidence Interval: [{ci_68_lower:.2f}%, {ci_68_upper:.2f}%]")
print(f"\nPessimistic Scenario (10th percentile): {pessimistic:.2f}%")
print(f"Optimistic Scenario (90th percentile): {optimistic:.2f}%")
print(f"\nProbability of Positive Return: {prob_positive:.1f}%")
print(f"Current Annualized CAGR (147 days): {actual_cagr*100:.2f}%")

# Save results
results = {
    'Metric': [
        'Expected CAGR (Mean)',
        'Median CAGR',
        'Standard Deviation',
        '95% CI Lower',
        '95% CI Upper',
        '68% CI Lower',
        '68% CI Upper',
        'Pessimistic (10th percentile)',
        'Optimistic (90th percentile)',
        'Probability of Positive Return (%)',
        'Current Annualized CAGR (147 days)'
    ],
    'Value': [
        f"{mean_cagr:.2f}%",
        f"{median_cagr:.2f}%",
        f"{std_cagr:.2f}%",
        f"{ci_95_lower:.2f}%",
        f"{ci_95_upper:.2f}%",
        f"{ci_68_lower:.2f}%",
        f"{ci_68_upper:.2f}%",
        f"{pessimistic:.2f}%",
        f"{optimistic:.2f}%",
        f"{prob_positive:.1f}%",
        f"{actual_cagr*100:.2f}%"
    ]
}

results_df = pd.DataFrame(results)
results_df.to_csv('/home/ubuntu/stage4_optimization/cagr_confidence_intervals_results.csv', index=False)

# Save bootstrap distribution for visualization
bootstrap_df = pd.DataFrame({
    'CAGR': bootstrap_cagrs
})
bootstrap_df.to_csv('/home/ubuntu/stage4_optimization/cagr_bootstrap_distribution.csv', index=False)

print("\n" + "="*80)
print("RESULTS SAVED")
print("="*80)
print("Files created:")
print("  - cagr_confidence_intervals_results.csv")
print("  - cagr_bootstrap_distribution.csv")
print("="*80)
