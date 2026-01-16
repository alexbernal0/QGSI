#!/usr/bin/env python3.11
"""
Recalculate liquidity scores properly and assign 7-tier classification
"""
import pandas as pd
import numpy as np

print("Recalculating liquidity scores and tiers...")

# Load stock characteristics
long_df = pd.read_csv('part3_b2_long_stock_characteristics.csv')
short_df = pd.read_csv('part3_b2_short_stock_characteristics.csv')

# Recalculate liquidity score as Estimated_Daily_Volume (dollar volume)
long_df['Liquidity_Score'] = long_df['Estimated_Daily_Volume']
short_df['Liquidity_Score'] = short_df['Estimated_Daily_Volume']

# Define 7-tier classification based on percentiles
def assign_liquidity_tier_percentile(df):
    """Assign tiers based on percentile distribution"""
    scores = df['Liquidity_Score']
    
    # Calculate percentile thresholds
    p90 = scores.quantile(0.90)
    p75 = scores.quantile(0.75)
    p60 = scores.quantile(0.60)
    p40 = scores.quantile(0.40)
    p25 = scores.quantile(0.25)
    p10 = scores.quantile(0.10)
    
    def classify(score):
        if score >= p90:
            return 'Very High'
        elif score >= p75:
            return 'High'
        elif score >= p60:
            return 'Medium-High'
        elif score >= p40:
            return 'Medium'
        elif score >= p25:
            return 'Medium-Low'
        elif score >= p10:
            return 'Low'
        else:
            return 'Very Low'
    
    return df['Liquidity_Score'].apply(classify)

# Assign tiers
long_df['Liquidity_Tier'] = assign_liquidity_tier_percentile(long_df)
short_df['Liquidity_Tier'] = assign_liquidity_tier_percentile(short_df)

# Save updated characteristics
long_df.to_csv('part3_b2_long_stock_characteristics_updated.csv', index=False)
short_df.to_csv('part3_b2_short_stock_characteristics_updated.csv', index=False)

# Aggregate by liquidity tier
tier_order = ['Very High', 'High', 'Medium-High', 'Medium', 'Medium-Low', 'Low', 'Very Low']

for strategy, df in [('LONG', long_df), ('SHORT', short_df)]:
    by_tier = df.groupby('Liquidity_Tier').agg({
        'Symbol': 'count',
        'Total_PnL': 'sum',
        'Trade_Count': 'sum',
        'Avg_PnL': 'mean',
        'Volatility_Ann': 'mean',
        'Liquidity_Score': 'mean'
    }).reset_index()
    
    by_tier.columns = ['Liquidity_Tier', 'Stock_Count', 'Total_PnL', 'Trade_Count', 
                       'Avg_PnL_Per_Stock', 'Avg_Volatility', 'Avg_Liquidity_Score']
    
    # Sort by tier order
    by_tier['Tier_Order'] = by_tier['Liquidity_Tier'].apply(lambda x: tier_order.index(x) if x in tier_order else 99)
    by_tier = by_tier.sort_values('Tier_Order').drop('Tier_Order', axis=1)
    
    # Save
    filename = f'part3_b4_{strategy.lower()}_by_liquidity_7tier.csv'
    by_tier.to_csv(filename, index=False)
    
    print(f"\n{strategy} Strategy - Stocks by Liquidity Tier:")
    for _, row in by_tier.iterrows():
        print(f"  {row['Liquidity_Tier']:15s}: n={int(row['Stock_Count']):3d} stocks, "
              f"${row['Total_PnL']:>10,.0f} PnL, ${row['Avg_Liquidity_Score']:>12,.0f} avg liquidity")

print("\n✓ Liquidity tiers recalculated and saved")
