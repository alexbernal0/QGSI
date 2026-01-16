#!/usr/bin/env python3.11
"""
Expand liquidity analysis with more granular tiers (7 tiers instead of 5)
Based on user's examples: Very High, High, Medium-High, Medium, Medium-Low, Low, Very Low
"""
import pandas as pd
import numpy as np

print("Expanding liquidity tiers analysis...")

# Load stock performance data
long_stock_perf = pd.read_csv('part3_b2_long_stock_characteristics.csv')
short_stock_perf = pd.read_csv('part3_b2_short_stock_characteristics.csv')

def calculate_liquidity_score(row):
    """Calculate liquidity score based on existing score"""
    return row['Liquidity_Score']

def assign_liquidity_tier(score):
    """Assign liquidity tier based on score (7 tiers)"""
    if score >= 1_000_000_000:  # $1B+ daily volume
        return 'Very High'
    elif score >= 100_000_000:  # $100M-$1B
        return 'High'
    elif score >= 50_000_000:   # $50M-$100M
        return 'Medium-High'
    elif score >= 10_000_000:   # $10M-$50M
        return 'Medium'
    elif score >= 5_000_000:    # $5M-$10M
        return 'Medium-Low'
    elif score >= 1_000_000:    # $1M-$5M
        return 'Low'
    else:                        # <$1M
        return 'Very Low'

# Calculate liquidity scores and tiers for LONG
long_stock_perf['Liquidity_Score'] = long_stock_perf.apply(calculate_liquidity_score, axis=1)
long_stock_perf['Liquidity_Tier'] = long_stock_perf['Liquidity_Score'].apply(assign_liquidity_tier)

# Calculate liquidity scores and tiers for SHORT
short_stock_perf['Liquidity_Score'] = short_stock_perf.apply(calculate_liquidity_score, axis=1)
short_stock_perf['Liquidity_Tier'] = short_stock_perf['Liquidity_Score'].apply(assign_liquidity_tier)

# Aggregate by liquidity tier for LONG
long_by_liquidity = long_stock_perf.groupby('Liquidity_Tier').agg({
    'Symbol': 'count',
    'Total_PnL': 'sum',
    'Trade_Count': 'sum',
    'Avg_PnL': 'mean',
    'Volatility_Ann': 'mean',
    'Liquidity_Score': 'mean'
}).reset_index()
long_by_liquidity.columns = ['Liquidity_Tier', 'Stock_Count', 'Total_PnL', 'Trade_Count', 
                               'Avg_PnL_Per_Stock', 'Avg_Volatility', 'Avg_Liquidity_Score']

# Aggregate by liquidity tier for SHORT
short_by_liquidity = short_stock_perf.groupby('Liquidity_Tier').agg({
    'Symbol': 'count',
    'Total_PnL': 'sum',
    'Trade_Count': 'sum',
    'Avg_PnL': 'mean',
    'Volatility_Ann': 'mean',
    'Liquidity_Score': 'mean'
}).reset_index()
short_by_liquidity.columns = ['Liquidity_Tier', 'Stock_Count', 'Total_PnL', 'Trade_Count', 
                                'Avg_PnL_Per_Stock', 'Avg_Volatility', 'Avg_Liquidity_Score']

# Sort by tier order
tier_order = ['Very High', 'High', 'Medium-High', 'Medium', 'Medium-Low', 'Low', 'Very Low']
long_by_liquidity['Tier_Order'] = long_by_liquidity['Liquidity_Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)
short_by_liquidity['Tier_Order'] = short_by_liquidity['Liquidity_Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)

long_by_liquidity = long_by_liquidity.sort_values('Tier_Order')
short_by_liquidity = short_by_liquidity.sort_values('Tier_Order')

# Save results
long_by_liquidity.to_csv('part3_b4_long_by_liquidity_7tier.csv', index=False)
short_by_liquidity.to_csv('part3_b4_short_by_liquidity_7tier.csv', index=False)

# Also save updated stock performance with liquidity tiers
long_stock_perf.to_csv('part3_b2_long_stock_performance_updated.csv', index=False)
short_stock_perf.to_csv('part3_b2_short_stock_performance_updated.csv', index=False)

print("✓ Liquidity tiers expanded to 7 categories")
print(f"\nLONG Strategy - Stocks by Liquidity Tier:")
for _, row in long_by_liquidity.iterrows():
    print(f"  {row['Liquidity_Tier']:15s}: {int(row['Stock_Count']):3d} stocks, ${row['Total_PnL']:,.0f} PnL")

print(f"\nSHORT Strategy - Stocks by Liquidity Tier:")
for _, row in short_by_liquidity.iterrows():
    print(f"  {row['Liquidity_Tier']:15s}: {int(row['Stock_Count']):3d} stocks, ${row['Total_PnL']:,.0f} PnL")
