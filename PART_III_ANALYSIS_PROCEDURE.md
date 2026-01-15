# Part III Analysis Procedure Documentation
## Comparative Analysis & Stock Universe Exploration

**Purpose:** Complete procedure for reproducing the Part III analysis of LONG and SHORT trading strategies, including strategy comparison, combined portfolio simulation, stock characteristics analysis, and capital deployment capacity estimation.

**Date Created:** January 15, 2026  
**Author:** QGSI Quantitative Research Team  
**Environment:** Python 3.11, Ubuntu 22.04

---

## Prerequisites

### Required Python Packages
```bash
sudo pip3 install pandas numpy matplotlib seaborn pyarrow
```

### Required Input Files
1. `Production_Long_Trades.parquet` - LONG strategy trade log (16,754 trades)
2. `Production_Short_Trades.parquet` - SHORT strategy trade log (1,424 trades)
3. `Production_Long_Equity.parquet` - LONG strategy equity curve
4. `Production_Short_Equity.parquet` - SHORT strategy equity curve
5. `Production_Long_Extended_Metrics.csv` - LONG strategy performance metrics
6. `Production_Short_Extended_Metrics.csv` - SHORT strategy performance metrics

### Directory Structure
```
/home/ubuntu/stage4_optimization/
├── Production_Long_Trades.parquet
├── Production_Short_Trades.parquet
├── Production_Long_Equity.parquet
├── Production_Short_Equity.parquet
├── Production_Long_Extended_Metrics.csv
├── Production_Short_Extended_Metrics.csv
├── part3_section_a_strategy_comparison.py
├── part3_section_b_stock_characteristics.py
├── part3_generate_visualizations.py
└── [output files will be created here]
```

---

## SECTION A: Strategy Comparison Analysis

### Step 1: Run Strategy Comparison Script

**Script:** `part3_section_a_strategy_comparison.py`

**What it does:**
- Compares LONG vs SHORT performance metrics
- Simulates combined portfolio with shared capital and position limits
- Calculates correlation between strategies
- Analyzes trade distribution patterns
- Identifies symbol overlap and performance
- Calculates risk contribution
- Determines optimal allocation

**Execution:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 part3_section_a_strategy_comparison.py
```

**Expected Runtime:** ~2-3 minutes

**Output Files (16 files):**
1. `part3_a1_performance_comparison.csv` - Side-by-side metrics
2. `part3_a2_combined_portfolio_summary.csv` - Combined portfolio results
3. `part3_a2_combined_equity_curve.csv` - Combined equity curve (timestamp-level)
4. `part3_a2_combined_trades.csv` - All trades from combined simulation
5. `part3_a3_correlation_summary.csv` - Correlation statistics
6. `part3_a3_daily_returns_correlation.csv` - Daily returns with rolling correlation
7. `part3_a4_trades_by_hour.csv` - Hourly trade distribution
8. `part3_a4_trades_by_dayofweek.csv` - Day-of-week distribution
9. `part3_a4_trades_by_month.csv` - Monthly distribution
10. `part3_a5_symbol_summary.csv` - Symbol overlap statistics
11. `part3_a5_long_symbol_performance.csv` - Per-symbol LONG performance
12. `part3_a5_short_symbol_performance.csv` - Per-symbol SHORT performance
13. `part3_a5_top20_long_symbols.csv` - Top 20 LONG symbols
14. `part3_a5_top20_short_symbols.csv` - Top 20 SHORT symbols
15. `part3_a6_risk_contribution.csv` - Risk contribution analysis
16. `part3_a7_optimal_allocation.csv` - Allocation optimization results (21 scenarios)

### Key Functions in Section A Script

#### 1. `simulate_combined_portfolio()`
```python
def simulate_combined_portfolio(long_trades, short_trades, starting_capital, max_positions):
    """
    Simulates LONG + SHORT strategies with shared capital and position limits.
    
    Logic:
    - Merges both trade logs by EntryTime
    - Sorts by timestamp (FIFO)
    - Uses ATR as tiebreaker for simultaneous signals
    - Tracks shared position count
    - Allocates 10% of current equity per trade
    - Skips trades when max_positions reached
    - Calculates combined equity curve
    
    Returns: equity_curve_df, trades_df, summary_dict
    """
```

#### 2. `calculate_correlation_metrics()`
```python
def calculate_correlation_metrics(long_equity, short_equity):
    """
    Calculates correlation between LONG and SHORT daily returns.
    
    Includes:
    - Pearson correlation
    - 30-day rolling correlation
    - Drawdown overlap analysis
    
    Returns: correlation_summary_df, daily_returns_df
    """
```

#### 3. `analyze_symbol_overlap()`
```python
def analyze_symbol_overlap(long_trades, short_trades):
    """
    Identifies which symbols appear in both strategies.
    
    Calculates:
    - LONG only symbols
    - SHORT only symbols
    - Overlap symbols
    - Performance comparison for overlap symbols
    
    Returns: summary_df, long_symbol_perf_df, short_symbol_perf_df
    """
```

#### 4. `optimize_allocation()`
```python
def optimize_allocation(long_metrics, short_metrics, correlation):
    """
    Tests 21 allocation scenarios (0/100 to 100/0 in 5% increments).
    
    For each allocation:
    - Calculates weighted return
    - Calculates weighted volatility
    - Calculates Sharpe ratio
    - Calculates Calmar ratio
    
    Returns: allocation_df with all scenarios
    """
```

---

## SECTION B: Stock Characteristics Analysis

### Step 2: Run Stock Characteristics Script

**Script:** `part3_section_b_stock_characteristics.py`

**What it does:**
- Calculates stock-level metrics (price, volatility, trading frequency)
- Estimates liquidity scores and market cap tiers
- Analyzes performance by market cap, liquidity, and volatility
- Identifies top and bottom performers
- Estimates capital deployment capacity
- Generates exclusion and sizing recommendations

**Execution:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 part3_section_b_stock_characteristics.py
```

**Expected Runtime:** ~3-4 minutes

**Output Files (26 files):**
1. `part3_b1_universe_overview.csv` - Stock universe statistics
2. `part3_b2_long_stock_characteristics.csv` - LONG stock metrics (400 symbols)
3. `part3_b2_short_stock_characteristics.csv` - SHORT stock metrics (208 symbols)
4. `part3_b3_long_performance_by_mcap.csv` - LONG by market cap tier
5. `part3_b3_short_performance_by_mcap.csv` - SHORT by market cap tier
6. `part3_b4_long_performance_by_liquidity.csv` - LONG by liquidity tier
7. `part3_b4_short_performance_by_liquidity.csv` - SHORT by liquidity tier
8. `part3_b5_long_performance_by_volatility.csv` - LONG by volatility quintile
9. `part3_b5_short_performance_by_volatility.csv` - SHORT by volatility quintile
10. `part3_b6_long_top20_performers.csv` - Top 20 LONG symbols
11. `part3_b6_short_top20_performers.csv` - Top 20 SHORT symbols
12. `part3_b6_long_bottom20_performers.csv` - Bottom 20 LONG symbols
13. `part3_b6_short_bottom20_performers.csv` - Bottom 20 SHORT symbols
14. `part3_b6_long_top_vs_bottom_comparison.csv` - LONG comparison stats
15. `part3_b6_short_top_vs_bottom_comparison.csv` - SHORT comparison stats
16. `part3_b7_capacity_summary.csv` - Overall capacity analysis
17. `part3_b7_long_capacity_by_mcap.csv` - LONG capacity by market cap
18. `part3_b7_short_capacity_by_mcap.csv` - SHORT capacity by market cap
19. `part3_b7_long_capacity_by_liquidity.csv` - LONG capacity by liquidity
20. `part3_b7_short_capacity_by_liquidity.csv` - SHORT capacity by liquidity
21. `part3_b8_long_exclusion_list.csv` - LONG symbols to exclude
22. `part3_b8_short_exclusion_list.csv` - SHORT symbols to exclude
23. `part3_b8_long_exclusion_impact.csv` - LONG exclusion impact
24. `part3_b8_short_exclusion_impact.csv` - SHORT exclusion impact
25. `part3_b9_long_size_up_list.csv` - LONG symbols for larger sizing
26. `part3_b9_short_size_up_list.csv` - SHORT symbols for larger sizing

### Key Functions in Section B Script

#### 1. `calculate_stock_metrics()`
```python
def calculate_stock_metrics(trades_df, symbol):
    """
    Calculates per-symbol trading characteristics.
    
    Metrics:
    - Average entry price
    - Average position value
    - Annualized volatility (from trade returns)
    - Total trades
    - Trading days
    - Trades per day
    
    Returns: dict with all metrics
    """
```

#### 2. `estimate_liquidity_tier()`
```python
def estimate_liquidity_tier(row):
    """
    Estimates liquidity tier based on position size and trading frequency.
    
    Logic:
    - Assumes position is ~2% of daily volume
    - Estimates daily dollar volume
    - Calculates liquidity score = Daily Volume / Position Size
    - Assigns tier based on score thresholds
    - Estimates market impact
    
    Returns: Series with liquidity metrics
    """
```

#### 3. `estimate_market_cap_tier()`
```python
def estimate_market_cap_tier(row):
    """
    Estimates market cap tier based on price and liquidity.
    
    Heuristic:
    - Higher price + higher liquidity = larger cap
    - Uses thresholds to classify into 6 tiers:
      * Mega-cap ($200B+)
      * Large-cap ($10B-$200B)
      * Mid-cap ($2B-$10B)
      * Small-cap ($300M-$2B)
      * Micro-cap ($50M-$300M)
      * Nano-cap (<$50M)
    
    Returns: string with tier classification
    """
```

#### 4. `analyze_by_category()`
```python
def analyze_by_category(df, category_col, strategy_name):
    """
    Aggregates performance by any categorical column.
    
    Calculates:
    - Number of symbols
    - Total PnL
    - Average PnL per trade
    - Total trades
    - Average liquidity score
    - Average market impact
    - Average volatility
    - Win rate (requires going back to trade log)
    
    Returns: grouped DataFrame
    """
```

#### 5. `calculate_capacity()`
```python
# Capacity calculation (inline in script)
# Max deployable per stock = Daily Volume × 0.05 (5% limit)
long_full['Max_Deployable'] = long_full['Estimated_Daily_Volume'] * 0.05
long_total_capacity = long_full['Max_Deployable'].sum()
```

---

## SECTION C: Visualization Generation

### Step 3: Generate All Visualizations

**Script:** `part3_generate_visualizations.py`

**What it does:**
- Creates 11 publication-quality charts
- Section A: 6 strategy comparison charts
- Section B: 5 stock characteristics charts

**Execution:**
```bash
cd /home/ubuntu/stage4_optimization
python3.11 part3_generate_visualizations.py
```

**Expected Runtime:** ~1-2 minutes

**Output Files (11 PNG files):**

**Section A Visualizations:**
1. `part3_viz_combined_equity_curves.png` - LONG, SHORT, and combined equity curves
2. `part3_viz_correlation_analysis.png` - Scatter plot + rolling correlation
3. `part3_viz_trades_by_hour.png` - Hourly trade distribution
4. `part3_viz_symbol_overlap.png` - Symbol overlap bar chart
5. `part3_viz_risk_contribution.png` - Risk contribution pie chart
6. `part3_viz_optimal_allocation.png` - Efficient frontier + Sharpe by allocation

**Section B Visualizations:**
7. `part3_viz_performance_by_mcap.png` - PnL and win rate by market cap
8. `part3_viz_performance_by_liquidity.png` - PnL by liquidity tier
9. `part3_viz_performance_by_volatility.png` - Win rate and avg PnL by volatility quintile
10. `part3_viz_capital_capacity.png` - Current vs max capacity
11. `part3_viz_top_vs_bottom_comparison.png` - Top 20 vs bottom 20 characteristics

### Visualization Specifications

**Color Scheme:**
- LONG: `#2E86AB` (blue)
- SHORT: `#A23B72` (purple)
- Combined: `#F18F01` (orange)

**Style:**
- Base: `seaborn-v0_8-whitegrid`
- DPI: 300 (publication quality)
- Font sizes: Title 14pt bold, Axis labels 12pt bold, Legend 10pt

**Chart Types:**
- Line charts: Equity curves, rolling correlation
- Bar charts: Trade distribution, performance by category
- Scatter plots: Correlation analysis
- Pie charts: Risk contribution
- Grouped bar charts: Comparative analysis

---

## Complete Workflow

### Full Analysis Pipeline
```bash
#!/bin/bash
# Complete Part III analysis workflow

cd /home/ubuntu/stage4_optimization

echo "Step 1: Strategy Comparison Analysis..."
python3.11 part3_section_a_strategy_comparison.py
if [ $? -ne 0 ]; then
    echo "Error in Section A"
    exit 1
fi

echo "Step 2: Stock Characteristics Analysis..."
python3.11 part3_section_b_stock_characteristics.py
if [ $? -ne 0 ]; then
    echo "Error in Section B"
    exit 1
fi

echo "Step 3: Generate Visualizations..."
python3.11 part3_generate_visualizations.py
if [ $? -ne 0 ]; then
    echo "Error in visualizations"
    exit 1
fi

echo "Part III analysis complete!"
echo "Output files:"
ls -lh part3_*.csv part3_*.png | wc -l
echo "files generated"
```

### Verification Checklist

After running all scripts, verify:

**Section A (16 CSV files):**
- [ ] `part3_a1_performance_comparison.csv` exists and has 2 rows (LONG, SHORT)
- [ ] `part3_a2_combined_equity_curve.csv` has >1000 rows (timestamp-level)
- [ ] `part3_a3_daily_returns_correlation.csv` has 147 rows (one per trading day)
- [ ] `part3_a7_optimal_allocation.csv` has 21 rows (allocation scenarios)

**Section B (26 CSV files):**
- [ ] `part3_b2_long_stock_characteristics.csv` has 400 rows (all LONG symbols)
- [ ] `part3_b2_short_stock_characteristics.csv` has 208 rows (all SHORT symbols)
- [ ] `part3_b7_capacity_summary.csv` has 2 rows (LONG, SHORT)
- [ ] `part3_b8_long_exclusion_list.csv` has 127 rows (symbols to exclude)

**Visualizations (11 PNG files):**
- [ ] All 11 PNG files exist
- [ ] File sizes are reasonable (50KB - 500KB each)
- [ ] Images are 300 DPI

### Quick Validation Script
```python
import pandas as pd
import os

# Validate key outputs
files_to_check = [
    ('part3_a2_combined_equity_curve.csv', 1000, None),
    ('part3_a7_optimal_allocation.csv', 21, 21),
    ('part3_b2_long_stock_characteristics.csv', 400, 400),
    ('part3_b7_capacity_summary.csv', 2, 2),
]

all_good = True
for filename, min_rows, exact_rows in files_to_check:
    if not os.path.exists(filename):
        print(f"❌ Missing: {filename}")
        all_good = False
        continue
    
    df = pd.read_csv(filename)
    if exact_rows and len(df) != exact_rows:
        print(f"❌ {filename}: Expected {exact_rows} rows, got {len(df)}")
        all_good = False
    elif min_rows and len(df) < min_rows:
        print(f"❌ {filename}: Expected >{min_rows} rows, got {len(df)}")
        all_good = False
    else:
        print(f"✓ {filename}: {len(df)} rows")

if all_good:
    print("\n✓ All validations passed!")
else:
    print("\n❌ Some validations failed")
```

---

## Troubleshooting

### Common Issues

**Issue 1: "ValueError: shape mismatch" in visualizations**
- **Cause:** Different number of categories in LONG vs SHORT data
- **Solution:** Run `fix_viz.py` to align categories before visualization
```python
# Reindex both dataframes to have all categories
all_categories = sorted(set(long_df['Category'].tolist() + short_df['Category'].tolist()))
long_df = long_df.set_index('Category').reindex(all_categories, fill_value=0).reset_index()
short_df = short_df.set_index('Category').reindex(all_categories, fill_value=0).reset_index()
```

**Issue 2: "ValueError: Bin labels must be one fewer than the number of bin edges"**
- **Cause:** Volatility quintile calculation with duplicates
- **Solution:** Use `labels=False` for numeric labels instead of string labels
```python
df['Volatility_Quintile'] = pd.qcut(df['Volatility_Ann'], q=5, labels=False, duplicates='drop')
```

**Issue 3: Memory error with large datasets**
- **Cause:** Loading all trades into memory simultaneously
- **Solution:** Process in chunks or use Parquet file filtering
```python
# Read only required columns
trades = pd.read_parquet('trades.parquet', columns=['Symbol', 'EntryTime', 'NetProfit'])
```

**Issue 4: Slow combined portfolio simulation**
- **Cause:** Nested loops for position tracking
- **Solution:** Already optimized with vectorized operations where possible
- **Expected runtime:** ~60 seconds for 18K trades

---

## Customization Options

### Modify Analysis Parameters

**Change liquidity estimation:**
```python
# In part3_section_b_stock_characteristics.py, line ~150
estimated_daily_volume = position_value * 50  # Change multiplier (default: 50)
```

**Change exclusion criteria:**
```python
# In part3_section_b_stock_characteristics.py, line ~420
long_exclude = long_full[
    (long_full['Liquidity_Score'] < 20) |  # Change threshold
    (long_full['Market_Impact_Est'] > 5) |  # Change threshold
    ((long_full['Total_PnL'] < 0) & (long_full['Trade_Count'] > 5))  # Change threshold
]
```

**Change capacity calculation:**
```python
# In part3_section_b_stock_characteristics.py, line ~400
long_full['Max_Deployable'] = long_full['Estimated_Daily_Volume'] * 0.05  # Change 5% limit
```

**Change allocation test range:**
```python
# In part3_section_a_strategy_comparison.py, line ~280
allocations = np.arange(0, 101, 5)  # Change step size (default: 5%)
```

---

## Output Summary

**Total Files Generated:** 53
- CSV files: 42
- PNG files: 11

**Total Data Size:** ~15 MB
- CSV files: ~10 MB
- PNG files: ~5 MB

**Analysis Coverage:**
- 400 unique symbols analyzed
- 18,178 total trades processed
- 147 trading days analyzed
- 21 allocation scenarios tested
- 11 visualizations created

---

## Integration with Main Report

The Part III analysis is designed to be integrated into the combined LONG+SHORT production portfolio report. Key sections to include:

1. **Executive Summary:** Combined portfolio results ($2.05M final equity, 104.6% return)
2. **Strategy Comparison Table:** Side-by-side metrics from `part3_a1_performance_comparison.csv`
3. **Combined Equity Curve:** Chart from `part3_viz_combined_equity_curves.png`
4. **Correlation Analysis:** Chart from `part3_viz_correlation_analysis.png`
5. **Optimal Allocation:** Chart from `part3_viz_optimal_allocation.png`
6. **Stock Universe Summary:** Table from `part3_b1_universe_overview.csv`
7. **Performance by Market Cap:** Chart from `part3_viz_performance_by_mcap.png`
8. **Capital Capacity:** Chart from `part3_viz_capital_capacity.png`
9. **Recommendations:** From `PART_III_COMPREHENSIVE_SUMMARY.md`

---

## Reproducibility Notes

**Environment:**
- Python 3.11.0rc1
- Pandas 2.0+
- NumPy 1.24+
- Matplotlib 3.7+
- Seaborn 0.12+

**Random Seed:** Not applicable (deterministic calculations)

**Data Dependencies:**
- All analysis depends on production portfolio simulator outputs
- Production simulator uses FIFO methodology (deterministic)
- No random sampling or Monte Carlo simulation

**Expected Variations:**
- None - all calculations are deterministic
- Results should be identical across runs with same input data

---

## Future Enhancements

**Planned Improvements:**
1. **Real Volume Data Integration:** Replace estimated liquidity with actual volume data from MotherDuck
2. **Sector Analysis:** Add sector-level performance breakdown
3. **Market Regime Analysis:** Analyze performance by volatility regime (VIX levels)
4. **Transaction Cost Modeling:** Add realistic slippage and commission models
5. **Monte Carlo Simulation:** Add bootstrap analysis for confidence intervals
6. **Walk-Forward Analysis:** Test strategy stability across different time periods

**Data Requirements for Enhancements:**
- Real-time or historical volume data (from MotherDuck `stock_fundamentals` table)
- Sector classifications (from MotherDuck)
- VIX historical data (for regime analysis)
- Actual execution data (for transaction cost modeling)

---

## Contact & Support

**Questions or Issues:**
- Review this procedure document first
- Check troubleshooting section
- Verify all input files exist and are current
- Check Python package versions

**Documentation Version:** 1.0  
**Last Updated:** January 15, 2026  
**Maintained By:** QGSI Quantitative Research Team
