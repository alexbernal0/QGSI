# QGSI Production Portfolio - Complete Procedures & Program Documentation

**Last Updated:** January 16, 2026  
**Project:** QGSI Data Science - Stage 4 Optimization & Production Portfolio Analysis  
**GitHub Repository:** https://github.com/alexbernal0/QGSI  
**Working Directory:** `/home/ubuntu/stage4_optimization/`

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Phase 1: Baseline Trade Generation](#phase-1-baseline-trade-generation)
3. [Phase 2: Production Portfolio Simulation](#phase-2-production-portfolio-simulation)
4. [Phase 3: Extended Metrics Calculation](#phase-3-extended-metrics-calculation)
5. [Phase 4: Part III Comparative Analysis](#phase-4-part-iii-comparative-analysis)
6. [Phase 5: 1-Year CAGR Estimation](#phase-5-1-year-cagr-estimation)
7. [Phase 6: Comprehensive Report Generation](#phase-6-comprehensive-report-generation)
8. [Utility Functions & Modules](#utility-functions--modules)
9. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Required Packages

```bash
sudo pip3 install pandas numpy pyarrow matplotlib seaborn scipy reportlab
```

### Directory Structure

```bash
cd /home/ubuntu
mkdir -p stage4_optimization
cd stage4_optimization
```

### Data Requirements

- Baseline trade logs (parquet format)
- Intraday market data (for baseline generation)
- Stock fundamental data (optional, for Part III enhancement)

---

## Phase 1: Baseline Trade Generation

### Objective
Generate all possible trades from optimized strategies without position limits or capital constraints.

### Program: `run_baseline_chunked.py`

**Purpose:** Process 400 symbols in chunks to generate baseline trades for LONG strategy.

**Key Parameters:**
```python
CHUNK_SIZE = 40  # Process 40 symbols at a time
ATR_PERIOD = 30
ATR_MULTIPLIER = 5.0
MAX_BARS = 20
SIGNAL_TYPE = 'Long'
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 run_baseline_chunked.py
```

**Output:**
- `Production_Long_Baseline.parquet` - 31,823 baseline LONG trades

**Columns:**
- Symbol, Entry_Time, Entry_Price, Exit_Time, Exit_Price, PnL, Signal, Duration_Minutes

---

### Program: `prepare_short_baseline.py`

**Purpose:** Prepare SHORT baseline trades for production simulator.

**Key Parameters:**
```python
ATR_PERIOD = 30
ATR_MULTIPLIER = 1.5
MAX_BARS = 20
SIGNAL_TYPE = 'Short'
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 prepare_short_baseline.py
```

**Output:**
- `Production_Short_Baseline.parquet` - 60,111 baseline SHORT trades

---

## Phase 2: Production Portfolio Simulation

### Objective
Apply realistic trading constraints with FIFO (First-In-First-Out) methodology.

### Program: `production_portfolio_simulator.py`

**Purpose:** Simulate LONG strategy with realistic constraints.

**Key Parameters:**
```python
STARTING_CAPITAL = 1_000_000
MAX_POSITIONS = 10
POSITION_SIZE_PCT = 0.10  # 10% of equity per trade
```

**FIFO Algorithm:**
```python
1. Load baseline trades sorted by Entry_Time
2. Initialize portfolio:
   - equity = $1,000,000
   - positions = []
   - max_positions = 10
3. For each signal in chronological order:
   a. Check position limit: len(positions) < 10
   b. Check capital: equity * 0.10 available
   c. Check duplicates: symbol not in active positions
   d. If all pass:
      - Calculate shares = (equity * 0.10) / entry_price
      - Open position
      - Add to active positions
   e. If any fail:
      - Skip signal (record reason)
   f. Check for exits on active positions
   g. Close positions at exit price
   h. Update equity
4. Generate equity curve and trade log
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 production_portfolio_simulator.py
```

**Output:**
- `Production_Long_Trades.parquet` - 16,754 executed trades
- `Production_Long_Equity.parquet` - Timestamp-level equity curve
- `Production_Long_Summary.csv` - Summary statistics

**Key Metrics:**
- Final Equity: $1,465,042
- Total Return: 46.50%
- Trades Executed: 16,754 / 31,823 (52.6% utilization)
- Win Rate: 50.2%

---

### Program: `production_portfolio_simulator_short.py`

**Purpose:** Simulate SHORT strategy with realistic constraints.

**Parameters:** Same as LONG simulator

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 production_portfolio_simulator_short.py
```

**Output:**
- `Production_Short_Trades.parquet` - 1,424 executed trades
- `Production_Short_Equity.parquet` - Timestamp-level equity curve
- `Production_Short_Summary.csv` - Summary statistics

**Key Metrics:**
- Final Equity: $1,362,947
- Total Return: 36.29%
- Trades Executed: 1,424 / 60,111 (2.4% utilization)
- Win Rate: 62.4%

---

## Phase 3: Extended Metrics Calculation

### Objective
Calculate 56+ institutional-grade quantitative metrics.

### Module: `extended_metrics.py`

**Purpose:** Reusable module for calculating extended performance metrics.

**Key Functions:**

```python
def calculate_all_metrics(returns, rf=0.0):
    """
    Calculate all extended metrics from daily returns.
    
    Parameters:
    -----------
    returns : pd.Series
        Daily returns (decimal format, e.g., 0.01 for 1%)
    rf : float
        Risk-free rate (annualized, decimal format)
    
    Returns:
    --------
    dict : All calculated metrics
    """
    
def get_drawdowns(returns):
    """
    Calculate all drawdown periods with dates.
    
    Returns:
    --------
    pd.DataFrame : Drawdown periods with start/end dates, depth, duration
    """
    
def calculate_sharpe_ratio(returns, rf=0.0):
    """Sharpe ratio = (mean - rf) / std * sqrt(252)"""
    
def calculate_sortino_ratio(returns, rf=0.0):
    """Sortino ratio = (mean - rf) / downside_std * sqrt(252)"""
    
def calculate_calmar_ratio(returns):
    """Calmar ratio = CAGR / Max Drawdown"""
    
def calculate_omega_ratio(returns, threshold=0.0):
    """Omega ratio = Sum(gains above threshold) / Sum(losses below threshold)"""
```

**Metrics Calculated:**
1. **Risk-Adjusted Performance (7):** Sharpe, Sortino, Smart Sharpe, Smart Sortino, Probabilistic Sharpe, Calmar, Omega, Recovery Factor, Ulcer Index, Serenity Index
2. **Return Distribution (8):** Expected daily/monthly/yearly, Best/Worst day/month/year, Skewness, Kurtosis
3. **Drawdown Analysis (5):** Max DD, Avg DD, Longest DD days, Avg DD days, Recovery factor
4. **Win/Loss Statistics (9):** Win rates by period, Payoff ratio, Gain/Pain ratio, CPC Index, Tail ratio, Outlier ratios
5. **Risk Metrics (5):** VaR, cVaR, Kelly Criterion, Volatility

---

### Program: `calculate_extended_metrics.py`

**Purpose:** Calculate and save extended metrics for both strategies.

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 calculate_extended_metrics.py
```

**Process:**
```python
1. Load equity curves (parquet)
2. Aggregate to daily end-of-day equity
3. Calculate daily returns
4. Call calculate_all_metrics()
5. Save to CSV
```

**Output:**
- `Production_Long_Extended_Metrics.csv` - 56 LONG metrics
- `Production_Short_Extended_Metrics.csv` - 56 SHORT metrics

---

## Phase 4: Part III Comparative Analysis

### Objective
Compare strategies, simulate combined portfolio, analyze stock universe.

### Section A: Strategy Comparison

#### Program: `part3_section_a_strategy_comparison.py`

**Purpose:** Comprehensive strategy comparison analysis.

**Key Analyses:**

**1. Performance Comparison Table**
```python
metrics = ['Final_Equity', 'Total_Return', 'CAGR', 'Sharpe', 'Sortino', 
           'Max_DD', 'Win_Rate', 'Profit_Factor', 'Trades']
comparison_df = pd.DataFrame({
    'LONG': long_metrics,
    'SHORT': short_metrics
})
```

**2. Combined Portfolio Simulation**
```python
# Merge LONG and SHORT trades
combined_trades = pd.concat([long_trades, short_trades])
combined_trades = combined_trades.sort_values('Entry_Time')

# Run FIFO simulator on combined trades
# Same constraints: $1M capital, 10 positions, 10% sizing
```

**3. Correlation Analysis**
```python
# Calculate daily returns correlation
long_returns = long_equity.pct_change()
short_returns = short_equity.pct_change()
correlation = long_returns.corr(short_returns)

# Rolling correlation
rolling_corr = long_returns.rolling(30).corr(short_returns)
```

**4. Trade Distribution**
```python
# Analyze temporal patterns
by_hour = trades.groupby(trades['Entry_Time'].dt.hour).size()
by_day = trades.groupby(trades['Entry_Time'].dt.dayofweek).size()
by_month = trades.groupby(trades['Entry_Time'].dt.month).size()
```

**5. Symbol Analysis**
```python
# Symbol overlap
long_symbols = set(long_trades['Symbol'].unique())
short_symbols = set(short_trades['Symbol'].unique())
overlap = long_symbols & short_symbols

# Performance by symbol
symbol_pnl = trades.groupby('Symbol')['PnL'].agg(['sum', 'count', 'mean'])
```

**6. Risk Contribution**
```python
# Volatility contribution
long_vol = long_returns.std() * np.sqrt(252)
short_vol = short_returns.std() * np.sqrt(252)
combined_vol = combined_returns.std() * np.sqrt(252)

# Diversification benefit
diversification_benefit = (long_vol + short_vol) - combined_vol
```

**7. Optimal Allocation**
```python
# Test allocations from 0/100 to 100/0 in 5% increments
allocations = np.arange(0, 1.05, 0.05)
for alloc in allocations:
    portfolio_returns = alloc * long_returns + (1-alloc) * short_returns
    sharpe = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)
    # Find allocation with max Sharpe
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 part3_section_a_strategy_comparison.py
```

**Output Files:**
- `part3_a1_performance_comparison.csv`
- `part3_a2_combined_portfolio_summary.csv`
- `part3_a2_combined_equity_curve.csv`
- `part3_a3_correlation_analysis.csv`
- `part3_a4_trade_distribution.csv`
- `part3_a5_symbol_summary.csv`
- `part3_a6_risk_contribution.csv`
- `part3_a7_optimal_allocation.csv`

---

### Section B: Stock Universe & Characteristics

#### Program: `part3_section_b_stock_characteristics.py`

**Purpose:** Analyze stock universe, liquidity, performance by characteristics.

**Key Analyses:**

**1. Stock Universe Overview**
```python
# Extract all traded symbols
long_symbols = long_trades['Symbol'].unique()
short_symbols = short_trades['Symbol'].unique()

# Calculate turnover
long_turnover = len(long_symbols) / 400
short_turnover = len(short_symbols) / 400
```

**2. Liquidity Calculation**
```python
# Estimate daily dollar volume for each symbol
for symbol in all_symbols:
    symbol_trades = trades[trades['Symbol'] == symbol]
    avg_price = symbol_trades['Entry_Price'].mean()
    # Estimate volume from trade frequency
    estimated_daily_volume = calculate_volume_estimate(symbol_trades)
    liquidity_score = avg_price * estimated_daily_volume
```

**3. Performance by Market Cap**
```python
# Categorize by market cap
market_cap_categories = ['Mega', 'Large', 'Mid', 'Small', 'Micro', 'Nano']

# Calculate performance by category
for category in market_cap_categories:
    category_trades = trades[trades['Market_Cap_Category'] == category]
    total_pnl = category_trades['PnL'].sum()
    win_rate = (category_trades['PnL'] > 0).mean()
    avg_pnl = category_trades['PnL'].mean()
```

**4. Performance by Liquidity Tier**
```python
# Create 7 liquidity tiers based on percentiles
percentiles = [0, 10, 25, 40, 60, 75, 90, 100]
liquidity_tiers = pd.qcut(stock_chars['Liquidity_Score'], 
                          q=len(percentiles)-1, 
                          labels=['Very Low', 'Low', 'Medium-Low', 'Medium', 
                                  'Medium-High', 'High', 'Very High'])

# Calculate performance by tier
for tier in liquidity_tiers.unique():
    tier_trades = trades[trades['Liquidity_Tier'] == tier]
    # Calculate metrics
```

**5. Performance by Volatility Quintile**
```python
# Calculate volatility for each symbol
for symbol in all_symbols:
    symbol_trades = trades[trades['Symbol'] == symbol]
    returns = symbol_trades['PnL'] / symbol_trades['Entry_Price']
    volatility = returns.std() * np.sqrt(252)

# Create quintiles
volatility_quintiles = pd.qcut(stock_chars['Volatility'], 
                               q=5, 
                               labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
```

**6. Top & Bottom Performers**
```python
# Calculate total PnL by symbol
symbol_pnl = trades.groupby('Symbol')['PnL'].sum().sort_values()

# Top 20 and Bottom 20
top20 = symbol_pnl.tail(20)
bottom20 = symbol_pnl.head(20)

# Compare characteristics
top20_chars = stock_chars[stock_chars['Symbol'].isin(top20.index)]
bottom20_chars = stock_chars[stock_chars['Symbol'].isin(bottom20.index)]
```

**7. Capital Deployment Capacity**
```python
# Calculate max capacity for each symbol
for symbol in all_symbols:
    estimated_daily_volume = stock_chars.loc[symbol, 'Estimated_Daily_Volume']
    avg_price = stock_chars.loc[symbol, 'Avg_Price']
    daily_dollar_volume = estimated_daily_volume * avg_price
    
    # Conservative: 5% of daily dollar volume
    max_capacity_per_symbol = daily_dollar_volume * 0.05

# Sum across all symbols
total_capacity = max_capacity_per_symbol.sum()
```

**8. Stock Exclusion Recommendations**
```python
# Criteria for exclusion:
# 1. Negative total PnL
# 2. Liquidity score below 10th percentile
# 3. Win rate below 40%

exclusion_criteria = (
    (symbol_pnl < 0) | 
    (stock_chars['Liquidity_Score'] < liquidity_threshold) |
    (symbol_win_rate < 0.40)
)

excluded_symbols = stock_chars[exclusion_criteria]['Symbol'].tolist()
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 part3_section_b_stock_characteristics.py
```

**Output Files:**
- `part3_b1_universe_overview.csv`
- `part3_b2_stock_characteristics.csv`
- `part3_b3_long_marketcap_performance.csv`
- `part3_b3_short_marketcap_performance.csv`
- `part3_b4_long_liquidity_performance.csv`
- `part3_b4_short_liquidity_performance.csv`
- `part3_b5_long_volatility_performance.csv`
- `part3_b5_short_volatility_performance.csv`
- `part3_b6_top20_performers.csv`
- `part3_b6_bottom20_performers.csv`
- `part3_b7_capacity_summary.csv`
- `part3_b8_long_exclusion_impact.csv`
- `part3_b8_short_exclusion_impact.csv`

---

#### Program: `recalculate_liquidity_tiers.py`

**Purpose:** Recalculate liquidity tiers with 7 granular bins.

**Liquidity Tiers:**
```python
percentiles = [0, 10, 25, 40, 60, 75, 90, 100]
tier_labels = ['Very Low', 'Low', 'Medium-Low', 'Medium', 
               'Medium-High', 'High', 'Very High']

liquidity_tiers = pd.qcut(stock_chars['Liquidity_Score'], 
                          q=len(percentiles)-1, 
                          labels=tier_labels)
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 recalculate_liquidity_tiers.py
```

---

### Visualization Generation

#### Program: `regenerate_all_visualizations.py`

**Purpose:** Generate all Part III visualizations with stock counts.

**Visualizations:**

**1. Combined Equity Curves**
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(long_equity['Date'], long_equity['Equity'], label='LONG', color='blue')
ax.plot(short_equity['Date'], short_equity['Equity'], label='SHORT', color='red')
ax.plot(combined_equity['Date'], combined_equity['Equity'], label='Combined', color='green')
ax.set_title('Combined Portfolio Equity Curves')
ax.legend()
plt.savefig('part3_viz_combined_equity_curves.png', dpi=150, bbox_inches='tight')
```

**2. Correlation Analysis**
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
# Scatter plot
ax1.scatter(long_returns, short_returns, alpha=0.5)
ax1.set_title(f'Daily Returns Correlation: {correlation:.4f}')
# Rolling correlation
ax2.plot(rolling_corr)
ax2.set_title('30-Day Rolling Correlation')
plt.savefig('part3_viz_correlation_analysis.png', dpi=150, bbox_inches='tight')
```

**3. Optimal Allocation**
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(allocations * 100, sharpe_ratios, marker='o')
ax.axvline(optimal_allocation * 100, color='red', linestyle='--', 
           label=f'Optimal: {optimal_allocation*100:.0f}% LONG')
ax.set_xlabel('% Allocation to LONG')
ax.set_ylabel('Sharpe Ratio')
ax.set_title('Optimal Allocation Efficient Frontier')
ax.legend()
plt.savefig('part3_viz_optimal_allocation.png', dpi=150, bbox_inches='tight')
```

**4. Performance by Market Cap**
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
# LONG
long_mcap_perf.plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_title(f'LONG Strategy: Performance by Market Cap')
# Add stock counts
for i, (cat, pnl) in enumerate(long_mcap_perf.items()):
    count = long_mcap_counts[cat]
    ax1.text(i, pnl, f'(n={count})', ha='center', va='bottom')
# SHORT
short_mcap_perf.plot(kind='bar', ax=ax2, color='coral')
ax2.set_title(f'SHORT Strategy: Performance by Market Cap')
# Add stock counts
for i, (cat, pnl) in enumerate(short_mcap_perf.items()):
    count = short_mcap_counts[cat]
    ax2.text(i, pnl, f'(n={count})', ha='center', va='bottom')
plt.savefig('part3_viz_performance_by_mcap.png', dpi=150, bbox_inches='tight')
```

**5. Performance by Liquidity Tier**
```python
# Same structure as market cap, but with 7 tiers
# Include stock counts (n=X) on each bar
```

**6. Performance by Volatility Quintile**
```python
# Same structure as market cap, but with 5 quintiles
# Include stock counts (n=X) on each bar
```

**7. Capital Deployment Capacity**
```python
fig, ax = plt.subplots(figsize=(10, 6))
categories = ['LONG', 'SHORT']
current = [1.0, 1.0]  # Current $1M each
max_capacity = [72.9, 60.6]  # Maximum capacity in $M
x = np.arange(len(categories))
width = 0.35
ax.bar(x - width/2, current, width, label='Current Capital', color='orange')
ax.bar(x + width/2, max_capacity, width, label='Max Capacity', color='steelblue')
ax.set_ylabel('Capital ($M)')
ax.set_title('Capital Deployment Capacity Analysis')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
plt.savefig('part3_viz_capital_capacity.png', dpi=150, bbox_inches='tight')
```

**8. Trade Distribution by Hour**
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
long_by_hour.plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_title('LONG Strategy: Trades by Hour')
short_by_hour.plot(kind='bar', ax=ax2, color='coral')
ax2.set_title('SHORT Strategy: Trades by Hour')
plt.savefig('part3_viz_trades_by_hour.png', dpi=150, bbox_inches='tight')
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 regenerate_all_visualizations.py
```

**Output:** 11 PNG files with all Part III visualizations

---

## Phase 5: 1-Year CAGR Estimation

### Objective
Project 1-year performance with statistical confidence intervals using bootstrap resampling.

### Program: `calculate_cagr_confidence_intervals.py`

**Purpose:** Bootstrap resampling to estimate 1-year CAGR distribution.

**Methodology:**

```python
# 1. Load combined equity curve
combined_equity = pd.read_csv('part3_a2_combined_equity_curve.csv')

# 2. Aggregate to daily end-of-day equity
combined_equity['Date'] = pd.to_datetime(combined_equity['Timestamp']).dt.date
daily_equity = combined_equity.groupby('Date')['Equity'].last()

# 3. Calculate daily returns
daily_returns = daily_equity.pct_change().dropna()

# 4. Bootstrap resampling
n_simulations = 10000
trading_days_per_year = 252
cagr_distribution = []

for i in range(n_simulations):
    # Resample 252 days with replacement
    resampled_returns = np.random.choice(daily_returns, size=trading_days_per_year, replace=True)
    
    # Calculate cumulative return
    cumulative_return = (1 + resampled_returns).prod() - 1
    
    # Annualize to CAGR
    cagr = cumulative_return
    cagr_distribution.append(cagr * 100)  # Convert to percentage

# 5. Calculate statistics
results = {
    'Expected_CAGR_Mean': np.mean(cagr_distribution),
    'Median_CAGR': np.median(cagr_distribution),
    'Std_Dev': np.std(cagr_distribution),
    'CI_95_Lower': np.percentile(cagr_distribution, 2.5),
    'CI_95_Upper': np.percentile(cagr_distribution, 97.5),
    'CI_68_Lower': np.percentile(cagr_distribution, 16),
    'CI_68_Upper': np.percentile(cagr_distribution, 84),
    'Pessimistic_10th': np.percentile(cagr_distribution, 10),
    'Optimistic_90th': np.percentile(cagr_distribution, 90),
    'Prob_Positive': (np.array(cagr_distribution) > 0).mean() * 100,
    'Current_Annualized': (daily_equity.iloc[-1] / daily_equity.iloc[0]) ** (252 / len(daily_returns)) - 1
}
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 calculate_cagr_confidence_intervals.py
```

**Output:**
- `cagr_confidence_intervals_results.csv` - Summary statistics
- `cagr_bootstrap_distribution.csv` - Full 10,000 simulation results

**Key Results:**
- Expected CAGR: 247.61%
- 95% CI: [165.81%, 351.78%]
- Pessimistic (10th): 190.45%
- Optimistic (90th): 309.26%
- Probability of Positive: 100.0%

---

### Program: `generate_cagr_visualization.py`

**Purpose:** Create 3-panel comprehensive CAGR visualization.

**Visualization Structure:**

```python
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 0.8], hspace=0.3)

# Panel 1: Distribution Histogram
ax1 = fig.add_subplot(gs[0])
ax1.hist(cagr_distribution, bins=50, color='steelblue', alpha=0.7, edgecolor='black')

# Add shaded regions
pessimistic_threshold = np.percentile(cagr_distribution, 10)
optimistic_threshold = np.percentile(cagr_distribution, 90)
ax1.axvspan(min(cagr_distribution), pessimistic_threshold, alpha=0.2, color='red', label='Pessimistic')
ax1.axvspan(pessimistic_threshold, optimistic_threshold, alpha=0.2, color='navy', label='Expected')
ax1.axvspan(optimistic_threshold, max(cagr_distribution), alpha=0.2, color='green', label='Optimistic')

# Add vertical lines
ax1.axvline(np.mean(cagr_distribution), color='gold', linestyle='--', linewidth=2, label='Expected (Mean)')
ax1.axvline(np.median(cagr_distribution), color='orange', linestyle='--', linewidth=2, label='Median')
ax1.axvline(current_cagr, color='black', linestyle=':', linewidth=2, label='Current (147 days)')

ax1.set_xlabel('1-Year CAGR (%)')
ax1.set_ylabel('Frequency')
ax1.set_title('1-Year CAGR Distribution (10,000 Bootstrap Simulations)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel 2: Scenario Analysis Box Plot
ax2 = fig.add_subplot(gs[1])
ax2.boxplot(cagr_distribution, vert=False, widths=0.5)

# Add scenario markers
ax2.plot(pessimistic_threshold, 1, 'rv', markersize=10, label='Pessimistic (10th)')
ax2.plot(np.mean(cagr_distribution), 1, 'y^', markersize=10, label='Expected (Mean)')
ax2.plot(np.median(cagr_distribution), 1, 'o', color='orange', markersize=10, label='Median (50th)')
ax2.plot(optimistic_threshold, 1, 'g^', markersize=10, label='Optimistic (90th)')
ax2.axvline(current_cagr, color='black', linestyle=':', linewidth=2, label='Current')

ax2.set_xlabel('1-Year CAGR (%)')
ax2.set_title('Scenario Analysis')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

# Panel 3: Statistical Summary Table
ax3 = fig.add_subplot(gs[2])
ax3.axis('off')

table_data = [
    ['Expected CAGR (Mean)', f"{results['Expected_CAGR_Mean']:.2f}%"],
    ['Median CAGR', f"{results['Median_CAGR']:.2f}%"],
    ['95% Confidence Interval', f"[{results['CI_95_Lower']:.2f}%, {results['CI_95_Upper']:.2f}%]"],
    ['68% Confidence Interval', f"[{results['CI_68_Lower']:.2f}%, {results['CI_68_Upper']:.2f}%]"],
    ['Pessimistic (10th percentile)', f"{results['Pessimistic_10th']:.2f}%"],
    ['Optimistic (90th percentile)', f"{results['Optimistic_90th']:.2f}%"],
    ['Probability of Positive Return', f"{results['Prob_Positive']:.2f}%"],
    ['Current Annualized (147 days)', f"{results['Current_Annualized']*100:.2f}%"]
]

table = ax3.table(cellText=table_data, cellLoc='left', loc='center',
                  colWidths=[0.6, 0.4],
                  bbox=[0, 0, 1, 1])
table.auto_set_font_size(False)
table.set_fontsize(9)

# Highlight expected CAGR row
for i in range(2):
    table[(0, i)].set_facecolor('#FFEB9C')
    table[(0, i)].set_text_props(weight='bold')

plt.savefig('part3_cagr_confidence_intervals.png', dpi=150, bbox_inches='tight')
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 generate_cagr_visualization.py
```

**Output:**
- `part3_cagr_confidence_intervals.png` - 3-panel visualization

---

## Phase 6: Comprehensive Report Generation

### Objective
Create institutional-grade PDF report with all analyses.

### Program: `generate_final_report_with_analysis.py`

**Purpose:** Generate comprehensive 17-page PDF report.

**Report Structure:**

```python
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import inch

# Page setup
doc = SimpleDocTemplate(
    'Production_Portfolio_COMPREHENSIVE_Report.pdf',
    pagesize=landscape(letter),
    topMargin=0.5*inch,
    bottomMargin=0.5*inch,
    leftMargin=0.5*inch,
    rightMargin=0.5*inch
)

# Styles
heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=8,
    fontName='Helvetica-Bold'
)

analysis_style = ParagraphStyle(
    'AnalysisText',
    parent=styles['BodyText'],
    fontSize=9,
    leading=12,
    spaceAfter=10
)

# Page number callback
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(10.5*inch, 0.3*inch, text)
    canvas.restoreState()

# Build report
story = []

# Title Page
story.append(Paragraph("PRODUCTION PORTFOLIO PERFORMANCE REPORT", heading_style))
story.append(Paragraph("Combined LONG + SHORT Strategy Analysis", subheading_style))
# ... add strategy parameters, data sources, etc.
story.append(PageBreak())

# Executive Summary
story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
# ... add performance comparison table
# ... add key findings
story.append(PageBreak())

# Part I: LONG Strategy
story.append(Paragraph("PART I: LONG STRATEGY PERFORMANCE", heading_style))
# ... add equity curve image
story.append(Image('Production_Long_Equity_Curve.png', width=7*inch, height=3.5*inch))
# ... add performance metrics table
# ... add analysis summary
story.append(PageBreak())

# Part II: SHORT Strategy
story.append(Paragraph("PART II: SHORT STRATEGY PERFORMANCE", heading_style))
# ... add equity curve image (2 subplots only)
story.append(Image('Production_Short_Equity_Curve.png', width=7*inch, height=3.5*inch))
# ... add performance metrics table
# ... add analysis summary
story.append(PageBreak())

# Part III: Comparative Analysis
story.append(Paragraph("PART III: COMPARATIVE ANALYSIS & STOCK UNIVERSE EXPLORATION", heading_style))

# Section A: Strategy Comparison
story.append(Paragraph("Section A: Strategy Comparison", subheading_style))
# ... add combined equity curves
story.append(Image('part3_viz_combined_equity_curves.png', width=7*inch, height=3.5*inch))
# ... add analysis summary
# ... add correlation analysis
story.append(Image('part3_viz_correlation_analysis.png', width=7*inch, height=3.5*inch))
# ... add optimal allocation
story.append(Image('part3_viz_optimal_allocation.png', width=7*inch, height=3.5*inch))
story.append(PageBreak())

# Section B: Stock Universe & Characteristics
story.append(Paragraph("Section B: Stock Universe & Trading Characteristics", subheading_style))
# ... add performance by market cap
story.append(Image('part3_viz_performance_by_mcap.png', width=7*inch, height=3.5*inch))
# ... add analysis summary
# ... add performance by liquidity
story.append(Image('part3_viz_performance_by_liquidity.png', width=7*inch, height=3.5*inch))
# ... add analysis summary
# ... add performance by volatility
story.append(Image('part3_viz_performance_by_volatility.png', width=7*inch, height=3.5*inch))
# ... add analysis summary
# ... add capital capacity
story.append(Image('part3_viz_capital_capacity.png', width=7*inch, height=3.5*inch))
# ... add analysis summary

# 1-Year CAGR Estimation
story.append(Paragraph("1-Year CAGR Estimation with Statistical Confidence Intervals", subheading_style))
story.append(Image('part3_cagr_confidence_intervals.png', width=7*inch, height=6*inch))
# ... add analysis summary
story.append(PageBreak())

# Overall Summary & Trading Operations
story.append(Paragraph("OVERALL SUMMARY & TRADING OPERATIONS", heading_style))
# ... add executive overview with CAGR findings
# ... add strategic assessment
# ... add phased deployment plan
story.append(PageBreak())

# Recommendations
story.append(Paragraph("RECOMMENDATIONS & NEXT STEPS", heading_style))
# ... add 10 recommendations
story.append(PageBreak())

# Appendix: FIFO Methodology
story.append(Paragraph("APPENDIX: FIFO REALISTIC BACKTESTING METHODOLOGY", heading_style))
# ... add methodology documentation
# ... add key functions
# ... add validation procedures

# Build PDF with page numbers
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
```

**Usage:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 generate_final_report_with_analysis.py
```

**Output:**
- `Production_Portfolio_COMPREHENSIVE_Report.pdf` - 17 pages, 3.90 MB

**Report Contents:**
1. Title Page
2. Executive Summary (with Win Rate & Profit Factor)
3. Part I: LONG Strategy Performance
4. Part II: SHORT Strategy Performance
5-11. Part III: Comparative Analysis & Stock Universe Exploration
12-13. Overall Summary & Trading Operations
14-15. Recommendations & Next Steps
16-17. Appendix: FIFO Methodology

---

## Utility Functions & Modules

### Equity Curve Plotting

```python
def plot_equity_curve_with_positions(equity_df, output_file, title):
    """
    Plot equity curve with position count subplot.
    
    Parameters:
    -----------
    equity_df : pd.DataFrame
        Equity curve with columns: Timestamp, Equity, Position_Count
    output_file : str
        Output PNG filename
    title : str
        Chart title
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), 
                                     gridspec_kw={'height_ratios': [3, 1]})
    
    # Equity curve
    ax1.plot(equity_df['Timestamp'], equity_df['Equity'], color='steelblue', linewidth=1.5)
    ax1.set_ylabel('Equity ($)', fontsize=10)
    ax1.set_title(title, fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(1000000, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    # Final equity annotation
    final_equity = equity_df['Equity'].iloc[-1]
    ax1.text(equity_df['Timestamp'].iloc[-1], final_equity, 
             f'Final: ${final_equity:,.0f}', 
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
             fontsize=9, ha='right', va='bottom')
    
    # Position count
    ax2.fill_between(equity_df['Timestamp'], equity_df['Position_Count'], 
                     color='coral', alpha=0.6)
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('Number of Positions', fontsize=10)
    ax2.set_title('Portfolio Position Count', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(10, color='red', linestyle='--', linewidth=1, 
                label='Max Positions (10)')
    ax2.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
```

### Monthly Returns Bar Chart

```python
def plot_monthly_returns(equity_df, output_file, title):
    """
    Plot monthly returns bar chart.
    
    Parameters:
    -----------
    equity_df : pd.DataFrame
        Equity curve with Timestamp and Equity columns
    output_file : str
        Output PNG filename
    title : str
        Chart title
    """
    # Aggregate to monthly
    equity_df['Month'] = pd.to_datetime(equity_df['Timestamp']).dt.to_period('M')
    monthly_equity = equity_df.groupby('Month')['Equity'].last()
    monthly_returns = monthly_equity.pct_change().dropna() * 100
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ['green' if r > 0 else 'red' for r in monthly_returns]
    monthly_returns.plot(kind='bar', ax=ax, color=colors, edgecolor='black')
    
    # Add value labels
    for i, v in enumerate(monthly_returns):
        ax.text(i, v, f'{v:.1f}%', ha='center', va='bottom' if v > 0 else 'top', 
                fontsize=9)
    
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Return (%)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
```

---

## Troubleshooting

### Common Issues

**1. Parquet File Column Mismatch**

**Problem:** Column names don't match expected names.

**Solution:**
```python
# Check column names
import pyarrow.parquet as pq
pf = pq.read_table('file.parquet')
print(pf.column_names)

# Rename columns if needed
df = pd.read_parquet('file.parquet')
df = df.rename(columns={'OldName': 'NewName'})
```

**2. Memory Issues with Large Files**

**Problem:** Out of memory when processing large parquet files.

**Solution:**
```python
# Read in chunks
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('large_file.parquet')
for batch in parquet_file.iter_batches(batch_size=10000):
    df_chunk = batch.to_pandas()
    # Process chunk
```

**3. Visualization Not Showing Stock Counts**

**Problem:** Stock counts (n=X) not appearing on charts.

**Solution:**
```python
# Ensure counts are calculated before plotting
category_counts = df.groupby('Category').size()

# Add text annotations
for i, (cat, value) in enumerate(category_performance.items()):
    count = category_counts[cat]
    ax.text(i, value, f'(n={count})', ha='center', va='bottom', fontsize=8)
```

**4. Report Generation Fails**

**Problem:** PDF report generation fails with encoding errors.

**Solution:**
```python
# Use HTML encoding for special characters
from reportlab.lib.utils import simpleSplit
text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# Or use Paragraph with proper encoding
from reportlab.platypus import Paragraph
p = Paragraph(text, style)
```

**5. Bootstrap CAGR Calculation Too Slow**

**Problem:** 10,000 simulations take too long.

**Solution:**
```python
# Use vectorized operations
import numpy as np

# Instead of loop
resampled_indices = np.random.randint(0, len(daily_returns), 
                                      size=(n_simulations, 252))
resampled_returns = daily_returns.values[resampled_indices]
cumulative_returns = (1 + resampled_returns).prod(axis=1) - 1
cagr_distribution = cumulative_returns * 100
```

---

## Validation Checklist

### Before Running Production Simulator

- [ ] Baseline trades loaded and sorted by Entry_Time
- [ ] No duplicate entries in baseline trades
- [ ] All Entry_Time and Exit_Time are valid timestamps
- [ ] All prices are positive
- [ ] Starting capital set correctly ($1,000,000)
- [ ] Max positions set correctly (10)
- [ ] Position sizing percentage set correctly (10%)

### After Running Production Simulator

- [ ] Final equity > 0
- [ ] Number of executed trades < baseline trades
- [ ] Equity curve is monotonic or has reasonable drawdowns
- [ ] Position count never exceeds max positions
- [ ] All closed positions have valid PnL
- [ ] Sum of all PnL = Final Equity - Starting Capital

### Before Generating Report

- [ ] All CSV files exist and are not empty
- [ ] All PNG visualizations exist and are valid images
- [ ] Metrics calculated correctly (no NaN or Inf values)
- [ ] Analysis summaries written and formatted
- [ ] Page numbers configured correctly

### After Generating Report

- [ ] PDF opens without errors
- [ ] All pages rendered correctly
- [ ] All images visible and properly sized
- [ ] All tables formatted correctly
- [ ] Page numbers on all pages
- [ ] No text overflow or truncation

---

## Performance Optimization Tips

### For Large Datasets

**1. Use Parquet Instead of CSV**
```python
# Parquet is 10x faster and 5x smaller
df.to_parquet('file.parquet', compression='snappy')
df = pd.read_parquet('file.parquet')
```

**2. Use Categorical Data Types**
```python
# Reduce memory usage for repeated strings
df['Symbol'] = df['Symbol'].astype('category')
df['Signal'] = df['Signal'].astype('category')
```

**3. Filter Early**
```python
# Filter before loading full dataset
df = pd.read_parquet('file.parquet', 
                     filters=[('Date', '>=', '2025-06-01')])
```

**4. Use Vectorized Operations**
```python
# Instead of loop
for i in range(len(df)):
    df.loc[i, 'Result'] = df.loc[i, 'A'] * df.loc[i, 'B']

# Use vectorization
df['Result'] = df['A'] * df['B']
```

**5. Parallel Processing**
```python
from multiprocessing import Pool

def process_symbol(symbol):
    # Process single symbol
    return result

with Pool(4) as pool:
    results = pool.map(process_symbol, symbols)
```

---

## Appendix: Complete File Listing

### Python Programs (25 files)

```
run_baseline_chunked.py
prepare_short_baseline.py
production_portfolio_simulator.py
production_portfolio_simulator_short.py
extended_metrics.py
calculate_extended_metrics.py
plot_production_equity.py
generate_production_report.py
generate_extended_report.py
part3_section_a_strategy_comparison.py
part3_section_b_stock_characteristics.py
recalculate_liquidity_tiers.py
regenerate_all_visualizations.py
regenerate_short_curve.py
calculate_cagr_confidence_intervals.py
generate_cagr_visualization.py
generate_comprehensive_combined_report.py
generate_final_report_with_analysis.py
expand_liquidity_tiers.py
part3_generate_visualizations.py
generate_long_report_with_files.py
generate_short_extended_report_corrected.py
generate_extended_report_with_appendix.py
save_production_to_motherduck.py
```

### Data Files (50+ files)

**Parquet:**
```
Production_Long_Baseline.parquet
Production_Short_Baseline.parquet
Production_Long_Trades.parquet
Production_Short_Trades.parquet
Production_Long_Equity.parquet
Production_Short_Equity.parquet
```

**CSV:**
```
Production_Long_Summary.csv
Production_Short_Summary.csv
Production_Long_Extended_Metrics.csv
Production_Short_Extended_Metrics.csv
part3_a1_performance_comparison.csv
part3_a2_combined_portfolio_summary.csv
part3_a2_combined_equity_curve.csv
part3_a3_correlation_analysis.csv
part3_a4_trade_distribution.csv
part3_a5_symbol_summary.csv
part3_a6_risk_contribution.csv
part3_a7_optimal_allocation.csv
part3_b1_universe_overview.csv
part3_b2_stock_characteristics.csv
part3_b3_long_marketcap_performance.csv
part3_b3_short_marketcap_performance.csv
part3_b4_long_liquidity_performance.csv
part3_b4_short_liquidity_performance.csv
part3_b5_long_volatility_performance.csv
part3_b5_short_volatility_performance.csv
part3_b6_top20_performers.csv
part3_b6_bottom20_performers.csv
part3_b7_capacity_summary.csv
part3_b8_long_exclusion_impact.csv
part3_b8_short_exclusion_impact.csv
cagr_confidence_intervals_results.csv
cagr_bootstrap_distribution.csv
```

### Visualizations (11 files)

```
Production_Long_Equity_Curve.png
Production_Short_Equity_Curve.png
Production_Long_Monthly_Returns.png
Production_Short_Monthly_Returns.png
part3_viz_combined_equity_curves.png
part3_viz_correlation_analysis.png
part3_viz_optimal_allocation.png
part3_viz_performance_by_mcap.png
part3_viz_performance_by_liquidity.png
part3_viz_performance_by_volatility.png
part3_viz_capital_capacity.png
part3_viz_trades_by_hour.png
part3_cagr_confidence_intervals.png
```

### Documentation (15 files)

```
PROJECT_STATUS.md
PROCEDURE.md
PART_III_OUTLINE.md
PART_III_COMPREHENSIVE_SUMMARY.md
PART_III_ANALYSIS_PROCEDURE.md
PRODUCTION_PORTFOLIO_SUMMARY.md
FIFO_METHODOLOGY_APPENDIX.md
CAGR_ANALYSIS_SUMMARY.md
senior_quant_analysis_summaries.md
overall_summary_trading_operations.md
analysis_summaries.md
production_observations.md
report_comparison.txt
final_report_verification.txt
FINAL_REPORT_IMPROVEMENTS_SUMMARY.md
```

### Reports (3 files)

```
Production_Portfolio_COMPREHENSIVE_Report.pdf
Production_Portfolio_Extended_Report.pdf
Production_Portfolio_SHORT_Extended_Report.pdf
```

---

**END OF PROCEDURE DOCUMENT**

This document provides complete step-by-step procedures for reproducing all analyses in the QGSI Production Portfolio project. All programs are documented with usage instructions, key parameters, and expected outputs.
