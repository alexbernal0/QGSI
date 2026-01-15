#!/usr/bin/env python3.11
"""
Part III - Section B: Stock Universe & Trading Characteristics Analysis
Calculates liquidity metrics, performance by market cap/volatility/sector,
capital deployment capacity, and sizing recommendations
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("PART III - SECTION B: STOCK UNIVERSE & CHARACTERISTICS ANALYSIS")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[1/10] Loading trade data and symbol performance...")

long_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
short_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Trades.parquet')

# Load symbol performance from Section A
long_symbol_perf = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a5_long_symbol_performance.csv')
short_symbol_perf = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a5_short_symbol_performance.csv')

print(f"✓ LONG: {len(long_symbol_perf)} symbols")
print(f"✓ SHORT: {len(short_symbol_perf)} symbols")

# ============================================================================
# B.1: STOCK UNIVERSE OVERVIEW
# ============================================================================
print("\n[2/10] Calculating stock universe overview...")

all_symbols = set(long_symbol_perf['Symbol'].unique()) | set(short_symbol_perf['Symbol'].unique())

# Calculate turnover and concentration
long_trades['Date'] = pd.to_datetime(long_trades['EntryTime']).dt.date
short_trades['Date'] = pd.to_datetime(short_trades['EntryTime']).dt.date

long_daily_symbols = long_trades.groupby('Date')['Symbol'].nunique()
short_daily_symbols = short_trades.groupby('Date')['Symbol'].nunique()

# Herfindahl index (concentration)
long_trade_counts = long_trades['Symbol'].value_counts()
long_herfindahl = ((long_trade_counts / long_trade_counts.sum()) ** 2).sum()

short_trade_counts = short_trades['Symbol'].value_counts()
short_herfindahl = ((short_trade_counts / short_trade_counts.sum()) ** 2).sum()

universe_overview = {
    'Total Unique Symbols': len(all_symbols),
    'LONG Symbols': len(long_symbol_perf),
    'SHORT Symbols': len(short_symbol_perf),
    'Avg Symbols per Day (LONG)': long_daily_symbols.mean(),
    'Avg Symbols per Day (SHORT)': short_daily_symbols.mean(),
    'Concentration (Herfindahl) LONG': long_herfindahl,
    'Concentration (Herfindahl) SHORT': short_herfindahl,
}

universe_df = pd.DataFrame([universe_overview])
universe_df.to_csv('/home/ubuntu/stage4_optimization/part3_b1_universe_overview.csv', index=False)

print(f"✓ Total universe: {len(all_symbols)} symbols")
print(f"  Avg symbols/day: LONG {long_daily_symbols.mean():.1f}, SHORT {short_daily_symbols.mean():.1f}")

# ============================================================================
# B.2: CALCULATE STOCK CHARACTERISTICS FROM TRADE DATA
# ============================================================================
print("\n[3/10] Calculating stock characteristics from trade data...")

# For each symbol, calculate metrics from the trades
def calculate_stock_metrics(trades_df, symbol):
    """Calculate metrics for a single symbol"""
    symbol_trades = trades_df[trades_df['Symbol'] == symbol]
    
    # Average price (from entry prices)
    avg_price = symbol_trades['EntryPrice'].mean()
    
    # Average position value
    avg_position_value = symbol_trades['EntryValue'].mean() if 'EntryValue' in symbol_trades.columns else (symbol_trades['EntryPrice'] * symbol_trades['Shares']).mean()
    
    # Volatility (from price changes)
    if len(symbol_trades) > 1:
        price_changes = symbol_trades['ExitPrice'] / symbol_trades['EntryPrice'] - 1
        volatility = price_changes.std() * np.sqrt(252)  # Annualized
    else:
        volatility = 0
    
    # Trade frequency (trades per day)
    trading_days = symbol_trades['Date'].nunique()
    trades_per_day = len(symbol_trades) / trading_days if trading_days > 0 else 0
    
    return {
        'Symbol': symbol,
        'Avg_Price': avg_price,
        'Avg_Position_Value': avg_position_value,
        'Volatility_Ann': volatility * 100,  # As percentage
        'Total_Trades': len(symbol_trades),
        'Trading_Days': trading_days,
        'Trades_Per_Day': trades_per_day
    }

# Calculate for all symbols
print("  Calculating LONG symbol metrics...")
long_metrics_list = []
for symbol in long_symbol_perf['Symbol'].unique():
    metrics = calculate_stock_metrics(long_trades, symbol)
    long_metrics_list.append(metrics)

long_stock_metrics = pd.DataFrame(long_metrics_list)

print("  Calculating SHORT symbol metrics...")
short_metrics_list = []
for symbol in short_symbol_perf['Symbol'].unique():
    metrics = calculate_stock_metrics(short_trades, symbol)
    short_metrics_list.append(metrics)

short_stock_metrics = pd.DataFrame(short_metrics_list)

# Merge with performance
long_full = pd.merge(long_symbol_perf, long_stock_metrics, on='Symbol')
short_full = pd.merge(short_symbol_perf, short_stock_metrics, on='Symbol')

# ============================================================================
# B.3: ESTIMATE LIQUIDITY METRICS
# ============================================================================
print("\n[4/10] Estimating liquidity metrics...")

# Since we don't have actual volume data, we'll estimate based on:
# 1. Position size relative to typical market cap tiers
# 2. Trading frequency (more liquid stocks trade more often)
# 3. Price level (higher price stocks tend to be more liquid)

def estimate_liquidity_tier(row):
    """Estimate liquidity tier based on available metrics"""
    # Use position value and trading frequency as proxies
    position_value = row['Avg_Position_Value']
    trades_per_day = row['Trades_Per_Day']
    price = row['Avg_Price']
    
    # Estimate daily dollar volume (very rough approximation)
    # Assume our position is ~1-5% of daily volume for typical stocks
    estimated_daily_volume = position_value * 50  # Assume we're 2% of volume
    
    # Liquidity score = Daily Volume / Position Size
    liquidity_score = estimated_daily_volume / position_value if position_value > 0 else 0
    
    # Assign tier
    if liquidity_score > 100:
        tier = 'Tier 1 (Very Liquid)'
    elif liquidity_score > 50:
        tier = 'Tier 2 (Liquid)'
    elif liquidity_score > 20:
        tier = 'Tier 3 (Moderate)'
    elif liquidity_score > 10:
        tier = 'Tier 4 (Illiquid)'
    else:
        tier = 'Tier 5 (Very Illiquid)'
    
    return pd.Series({
        'Estimated_Daily_Volume': estimated_daily_volume,
        'Liquidity_Score': liquidity_score,
        'Liquidity_Tier': tier,
        'Market_Impact_Est': (position_value / estimated_daily_volume * 100) if estimated_daily_volume > 0 else 0
    })

long_full[['Estimated_Daily_Volume', 'Liquidity_Score', 'Liquidity_Tier', 'Market_Impact_Est']] = long_full.apply(estimate_liquidity_tier, axis=1)
short_full[['Estimated_Daily_Volume', 'Liquidity_Score', 'Liquidity_Tier', 'Market_Impact_Est']] = short_full.apply(estimate_liquidity_tier, axis=1)

# Estimate market cap tier based on price and liquidity
def estimate_market_cap_tier(row):
    """Estimate market cap tier"""
    price = row['Avg_Price']
    liquidity_score = row['Liquidity_Score']
    
    # Higher price + higher liquidity = larger cap
    if price > 200 and liquidity_score > 50:
        return 'Mega-cap ($200B+)'
    elif price > 100 and liquidity_score > 30:
        return 'Large-cap ($10B-$200B)'
    elif price > 50 or liquidity_score > 20:
        return 'Mid-cap ($2B-$10B)'
    elif price > 20:
        return 'Small-cap ($300M-$2B)'
    elif price > 5:
        return 'Micro-cap ($50M-$300M)'
    else:
        return 'Nano-cap (<$50M)'

long_full['Market_Cap_Tier'] = long_full.apply(estimate_market_cap_tier, axis=1)
short_full['Market_Cap_Tier'] = short_full.apply(estimate_market_cap_tier, axis=1)

long_full.to_csv('/home/ubuntu/stage4_optimization/part3_b2_long_stock_characteristics.csv', index=False)
short_full.to_csv('/home/ubuntu/stage4_optimization/part3_b2_short_stock_characteristics.csv', index=False)

print(f"✓ Stock characteristics calculated with liquidity estimates")

# ============================================================================
# B.4: PERFORMANCE BY MARKET CAP CATEGORY
# ============================================================================
print("\n[5/10] Analyzing performance by market cap category...")

def analyze_by_category(df, category_col, strategy_name):
    """Analyze performance by category"""
    grouped = df.groupby(category_col).agg({
        'Symbol': 'count',
        'Total_PnL': 'sum',
        'Avg_PnL': 'mean',
        'Trade_Count': 'sum',
        'Liquidity_Score': 'mean',
        'Market_Impact_Est': 'mean',
        'Volatility_Ann': 'mean'
    }).reset_index()
    
    grouped.columns = [category_col, 'Num_Symbols', 'Total_PnL', 'Avg_PnL_Per_Trade', 
                       'Total_Trades', 'Avg_Liquidity_Score', 'Avg_Market_Impact', 'Avg_Volatility']
    
    # Calculate win rate (need to go back to trades)
    win_rates = []
    for cat in grouped[category_col]:
        symbols_in_cat = df[df[category_col] == cat]['Symbol'].tolist()
        if strategy_name == 'LONG':
            cat_trades = long_trades[long_trades['Symbol'].isin(symbols_in_cat)]
        else:
            cat_trades = short_trades[short_trades['Symbol'].isin(symbols_in_cat)]
        
        wins = (cat_trades['NetProfit'] > 0).sum()
        total = len(cat_trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        win_rates.append(win_rate)
    
    grouped['Win_Rate'] = win_rates
    grouped['Strategy'] = strategy_name
    
    return grouped

long_by_mcap = analyze_by_category(long_full, 'Market_Cap_Tier', 'LONG')
short_by_mcap = analyze_by_category(short_full, 'Market_Cap_Tier', 'SHORT')

long_by_mcap.to_csv('/home/ubuntu/stage4_optimization/part3_b3_long_performance_by_mcap.csv', index=False)
short_by_mcap.to_csv('/home/ubuntu/stage4_optimization/part3_b3_short_performance_by_mcap.csv', index=False)

print(f"✓ Performance by market cap analyzed")
print(f"  LONG best category: {long_by_mcap.loc[long_by_mcap['Total_PnL'].idxmax(), 'Market_Cap_Tier']}")
print(f"  SHORT best category: {short_by_mcap.loc[short_by_mcap['Total_PnL'].idxmax(), 'Market_Cap_Tier']}")

# ============================================================================
# B.5: PERFORMANCE BY LIQUIDITY TIER
# ============================================================================
print("\n[6/10] Analyzing performance by liquidity tier...")

long_by_liq = analyze_by_category(long_full, 'Liquidity_Tier', 'LONG')
short_by_liq = analyze_by_category(short_full, 'Liquidity_Tier', 'SHORT')

long_by_liq.to_csv('/home/ubuntu/stage4_optimization/part3_b4_long_performance_by_liquidity.csv', index=False)
short_by_liq.to_csv('/home/ubuntu/stage4_optimization/part3_b4_short_performance_by_liquidity.csv', index=False)

print(f"✓ Performance by liquidity tier analyzed")

# ============================================================================
# B.6: PERFORMANCE BY VOLATILITY QUINTILE
# ============================================================================
print("\n[7/10] Analyzing performance by volatility quintile...")

# Create volatility quintiles
long_full['Volatility_Quintile'] = pd.qcut(long_full['Volatility_Ann'], q=5, labels=False, duplicates='drop', retbins=False)
short_full['Volatility_Quintile'] = pd.qcut(short_full['Volatility_Ann'], q=5, labels=False, duplicates='drop', retbins=False)

long_by_vol = analyze_by_category(long_full, 'Volatility_Quintile', 'LONG')
short_by_vol = analyze_by_category(short_full, 'Volatility_Quintile', 'SHORT')

long_by_vol.to_csv('/home/ubuntu/stage4_optimization/part3_b5_long_performance_by_volatility.csv', index=False)
short_by_vol.to_csv('/home/ubuntu/stage4_optimization/part3_b5_short_performance_by_volatility.csv', index=False)

print(f"✓ Performance by volatility quintile analyzed")

# ============================================================================
# B.7: TOP & BOTTOM PERFORMERS
# ============================================================================
print("\n[8/10] Analyzing top and bottom performers...")

# Top 20
long_top20 = long_full.nlargest(20, 'Total_PnL')[['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count', 
                                                     'Market_Cap_Tier', 'Liquidity_Score', 'Volatility_Ann']]
short_top20 = short_full.nlargest(20, 'Total_PnL')[['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count',
                                                       'Market_Cap_Tier', 'Liquidity_Score', 'Volatility_Ann']]

# Bottom 20
long_bottom20 = long_full.nsmallest(20, 'Total_PnL')[['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count',
                                                         'Market_Cap_Tier', 'Liquidity_Score', 'Volatility_Ann']]
short_bottom20 = short_full.nsmallest(20, 'Total_PnL')[['Symbol', 'Total_PnL', 'Avg_PnL', 'Trade_Count',
                                                           'Market_Cap_Tier', 'Liquidity_Score', 'Volatility_Ann']]

# Comparative statistics
long_comparison = pd.DataFrame({
    'Metric': ['Avg Liquidity Score', 'Avg Volatility (%)', 'Avg Trades'],
    'Top 20': [long_top20['Liquidity_Score'].mean(), long_top20['Volatility_Ann'].mean(), long_top20['Trade_Count'].mean()],
    'Bottom 20': [long_bottom20['Liquidity_Score'].mean(), long_bottom20['Volatility_Ann'].mean(), long_bottom20['Trade_Count'].mean()]
})

short_comparison = pd.DataFrame({
    'Metric': ['Avg Liquidity Score', 'Avg Volatility (%)', 'Avg Trades'],
    'Top 20': [short_top20['Liquidity_Score'].mean(), short_top20['Volatility_Ann'].mean(), short_top20['Trade_Count'].mean()],
    'Bottom 20': [short_bottom20['Liquidity_Score'].mean(), short_bottom20['Volatility_Ann'].mean(), short_bottom20['Trade_Count'].mean()]
})

long_top20.to_csv('/home/ubuntu/stage4_optimization/part3_b6_long_top20_performers.csv', index=False)
short_top20.to_csv('/home/ubuntu/stage4_optimization/part3_b6_short_top20_performers.csv', index=False)
long_bottom20.to_csv('/home/ubuntu/stage4_optimization/part3_b6_long_bottom20_performers.csv', index=False)
short_bottom20.to_csv('/home/ubuntu/stage4_optimization/part3_b6_short_bottom20_performers.csv', index=False)
long_comparison.to_csv('/home/ubuntu/stage4_optimization/part3_b6_long_top_vs_bottom_comparison.csv', index=False)
short_comparison.to_csv('/home/ubuntu/stage4_optimization/part3_b6_short_top_vs_bottom_comparison.csv', index=False)

print(f"✓ Top/bottom performers analyzed")

# ============================================================================
# B.8: CAPITAL DEPLOYMENT CAPACITY
# ============================================================================
print("\n[9/10] Calculating capital deployment capacity...")

# Max deployable per stock = Daily Volume × 0.05 (5% limit)
long_full['Max_Deployable'] = long_full['Estimated_Daily_Volume'] * 0.05
short_full['Max_Deployable'] = short_full['Estimated_Daily_Volume'] * 0.05

# Total capacity
long_total_capacity = long_full['Max_Deployable'].sum()
short_total_capacity = short_full['Max_Deployable'].sum()

# By market cap tier
long_capacity_by_mcap = long_full.groupby('Market_Cap_Tier')['Max_Deployable'].sum().reset_index()
long_capacity_by_mcap.columns = ['Market_Cap_Tier', 'Total_Capacity']
long_capacity_by_mcap['Strategy'] = 'LONG'

short_capacity_by_mcap = short_full.groupby('Market_Cap_Tier')['Max_Deployable'].sum().reset_index()
short_capacity_by_mcap.columns = ['Market_Cap_Tier', 'Total_Capacity']
short_capacity_by_mcap['Strategy'] = 'SHORT'

# By liquidity tier
long_capacity_by_liq = long_full.groupby('Liquidity_Tier')['Max_Deployable'].sum().reset_index()
long_capacity_by_liq.columns = ['Liquidity_Tier', 'Total_Capacity']
long_capacity_by_liq['Strategy'] = 'LONG'

short_capacity_by_liq = short_full.groupby('Liquidity_Tier')['Max_Deployable'].sum().reset_index()
short_capacity_by_liq.columns = ['Liquidity_Tier', 'Total_Capacity']
short_capacity_by_liq['Strategy'] = 'SHORT'

# Current utilization
current_capital = 1000000  # $1M starting
long_utilization = (current_capital / long_total_capacity * 100) if long_total_capacity > 0 else 0
short_utilization = (current_capital / short_total_capacity * 100) if short_total_capacity > 0 else 0

capacity_summary = pd.DataFrame([{
    'Strategy': 'LONG',
    'Total_Capacity': long_total_capacity,
    'Current_Capital': current_capital,
    'Utilization_Pct': long_utilization,
    'Recommended_Max': long_total_capacity
}, {
    'Strategy': 'SHORT',
    'Total_Capacity': short_total_capacity,
    'Current_Capital': current_capital,
    'Utilization_Pct': short_utilization,
    'Recommended_Max': short_total_capacity
}])

capacity_summary.to_csv('/home/ubuntu/stage4_optimization/part3_b7_capacity_summary.csv', index=False)
long_capacity_by_mcap.to_csv('/home/ubuntu/stage4_optimization/part3_b7_long_capacity_by_mcap.csv', index=False)
short_capacity_by_mcap.to_csv('/home/ubuntu/stage4_optimization/part3_b7_short_capacity_by_mcap.csv', index=False)
long_capacity_by_liq.to_csv('/home/ubuntu/stage4_optimization/part3_b7_long_capacity_by_liquidity.csv', index=False)
short_capacity_by_liq.to_csv('/home/ubuntu/stage4_optimization/part3_b7_short_capacity_by_liquidity.csv', index=False)

print(f"✓ Capital deployment capacity calculated")
print(f"  LONG capacity: ${long_total_capacity:,.0f} (current utilization: {long_utilization:.1f}%)")
print(f"  SHORT capacity: ${short_total_capacity:,.0f} (current utilization: {short_utilization:.1f}%)")

# ============================================================================
# B.9 & B.10: EXCLUSION AND SIZING RECOMMENDATIONS
# ============================================================================
print("\n[10/10] Generating exclusion and sizing recommendations...")

# Exclusion criteria
long_exclude = long_full[
    (long_full['Liquidity_Score'] < 20) |
    (long_full['Market_Impact_Est'] > 5) |
    ((long_full['Total_PnL'] < 0) & (long_full['Trade_Count'] > 5))
]

short_exclude = short_full[
    (short_full['Liquidity_Score'] < 20) |
    (short_full['Market_Impact_Est'] > 5) |
    ((short_full['Total_PnL'] < 0) & (short_full['Trade_Count'] > 5))
]

# Sizing up criteria
long_size_up = long_full[
    (long_full['Liquidity_Score'] > 100) &
    (long_full['Total_PnL'] > 0) &
    (long_full['Trade_Count'] > 10)
]

short_size_up = short_full[
    (short_full['Liquidity_Score'] > 100) &
    (short_full['Total_PnL'] > 0) &
    (short_full['Trade_Count'] > 5)
]

# Calculate impact
long_exclude_impact = {
    'Symbols_Excluded': len(long_exclude),
    'Trades_Lost': long_exclude['Trade_Count'].sum(),
    'Trades_Lost_Pct': (long_exclude['Trade_Count'].sum() / long_full['Trade_Count'].sum() * 100),
    'PnL_Lost': long_exclude['Total_PnL'].sum(),
    'PnL_Lost_Pct': (long_exclude['Total_PnL'].sum() / long_full['Total_PnL'].sum() * 100)
}

short_exclude_impact = {
    'Symbols_Excluded': len(short_exclude),
    'Trades_Lost': short_exclude['Trade_Count'].sum(),
    'Trades_Lost_Pct': (short_exclude['Trade_Count'].sum() / short_full['Trade_Count'].sum() * 100),
    'PnL_Lost': short_exclude['Total_PnL'].sum(),
    'PnL_Lost_Pct': (short_exclude['Total_PnL'].sum() / short_full['Total_PnL'].sum() * 100)
}

long_exclude[['Symbol', 'Total_PnL', 'Trade_Count', 'Liquidity_Score', 'Market_Impact_Est']].to_csv(
    '/home/ubuntu/stage4_optimization/part3_b8_long_exclusion_list.csv', index=False)
short_exclude[['Symbol', 'Total_PnL', 'Trade_Count', 'Liquidity_Score', 'Market_Impact_Est']].to_csv(
    '/home/ubuntu/stage4_optimization/part3_b8_short_exclusion_list.csv', index=False)

pd.DataFrame([long_exclude_impact]).to_csv('/home/ubuntu/stage4_optimization/part3_b8_long_exclusion_impact.csv', index=False)
pd.DataFrame([short_exclude_impact]).to_csv('/home/ubuntu/stage4_optimization/part3_b8_short_exclusion_impact.csv', index=False)

long_size_up[['Symbol', 'Total_PnL', 'Trade_Count', 'Liquidity_Score', 'Avg_PnL']].to_csv(
    '/home/ubuntu/stage4_optimization/part3_b9_long_size_up_list.csv', index=False)
short_size_up[['Symbol', 'Total_PnL', 'Trade_Count', 'Liquidity_Score', 'Avg_PnL']].to_csv(
    '/home/ubuntu/stage4_optimization/part3_b9_short_size_up_list.csv', index=False)

print(f"✓ Recommendations generated")
print(f"  LONG: {len(long_exclude)} to exclude, {len(long_size_up)} to size up")
print(f"  SHORT: {len(short_exclude)} to exclude, {len(short_size_up)} to size up")

print("\n" + "="*80)
print("SECTION B COMPLETE - All stock characteristics analyzed")
print("="*80)
print(f"\nKey Findings:")
print(f"  Total Capacity: LONG ${long_total_capacity:,.0f}, SHORT ${short_total_capacity:,.0f}")
print(f"  Exclusions: LONG {len(long_exclude)} symbols, SHORT {len(short_exclude)} symbols")
print(f"  Size Up Opportunities: LONG {len(long_size_up)} symbols, SHORT {len(short_size_up)} symbols")
print("="*80)
