# Fix the market cap visualization to handle different category counts
import pandas as pd

# Read both files
long_by_mcap = pd.read_csv('part3_b3_long_performance_by_mcap.csv')
short_by_mcap = pd.read_csv('part3_b3_short_performance_by_mcap.csv')

# Get all unique categories
all_categories = sorted(set(long_by_mcap['Market_Cap_Tier'].tolist() + short_by_mcap['Market_Cap_Tier'].tolist()))

# Reindex both dataframes to have all categories
long_by_mcap = long_by_mcap.set_index('Market_Cap_Tier').reindex(all_categories, fill_value=0).reset_index()
short_by_mcap = short_by_mcap.set_index('Market_Cap_Tier').reindex(all_categories, fill_value=0).reset_index()

# Fill NaN values
for col in long_by_mcap.columns:
    if col != 'Market_Cap_Tier':
        long_by_mcap[col] = long_by_mcap[col].fillna(0)
        short_by_mcap[col] = short_by_mcap[col].fillna(0)

# Save back
long_by_mcap.to_csv('part3_b3_long_performance_by_mcap.csv', index=False)
short_by_mcap.to_csv('part3_b3_short_performance_by_mcap.csv', index=False)

print(f"✓ Fixed market cap data: {len(all_categories)} categories")
print(f"  Categories: {all_categories}")

# Do the same for liquidity tiers
long_by_liq = pd.read_csv('part3_b4_long_performance_by_liquidity.csv')
short_by_liq = pd.read_csv('part3_b4_short_performance_by_liquidity.csv')

all_liq_tiers = sorted(set(long_by_liq['Liquidity_Tier'].tolist() + short_by_liq['Liquidity_Tier'].tolist()))
long_by_liq = long_by_liq.set_index('Liquidity_Tier').reindex(all_liq_tiers, fill_value=0).reset_index()
short_by_liq = short_by_liq.set_index('Liquidity_Tier').reindex(all_liq_tiers, fill_value=0).reset_index()

for col in long_by_liq.columns:
    if col != 'Liquidity_Tier':
        long_by_liq[col] = long_by_liq[col].fillna(0)
        short_by_liq[col] = short_by_liq[col].fillna(0)

long_by_liq.to_csv('part3_b4_long_performance_by_liquidity.csv', index=False)
short_by_liq.to_csv('part3_b4_short_performance_by_liquidity.csv', index=False)

print(f"✓ Fixed liquidity data: {len(all_liq_tiers)} tiers")

# Fix volatility quintiles
long_by_vol = pd.read_csv('part3_b5_long_performance_by_volatility.csv')
short_by_vol = pd.read_csv('part3_b5_short_performance_by_volatility.csv')

all_quintiles = sorted(set(long_by_vol['Volatility_Quintile'].tolist() + short_by_vol['Volatility_Quintile'].tolist()))
long_by_vol = long_by_vol.set_index('Volatility_Quintile').reindex(all_quintiles, fill_value=0).reset_index()
short_by_vol = short_by_vol.set_index('Volatility_Quintile').reindex(all_quintiles, fill_value=0).reset_index()

for col in long_by_vol.columns:
    if col != 'Volatility_Quintile':
        long_by_vol[col] = long_by_vol[col].fillna(0)
        short_by_vol[col] = short_by_vol[col].fillna(0)

long_by_vol.to_csv('part3_b5_long_performance_by_volatility.csv', index=False)
short_by_vol.to_csv('part3_b5_short_performance_by_volatility.csv', index=False)

print(f"✓ Fixed volatility data: {len(all_quintiles)} quintiles")
