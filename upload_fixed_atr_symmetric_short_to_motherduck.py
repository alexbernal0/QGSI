"""
Upload Fixed ATR Symmetric SHORT trade logs to MotherDuck
"""

import duckdb
import pandas as pd
from pathlib import Path

# Configuration
PARQUET_FILE = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_All_Trades.parquet')
TABLE_NAME = 'fixed_atr_symmetric_short_trades'

print("="*80)
print("UPLOADING FIXED ATR SYMMETRIC SHORT TRADES TO MOTHERDUCK")
print("="*80)

# Connect to MotherDuck
print("\n[1/3] Connecting to MotherDuck...")
conn = duckdb.connect('md:')
print("✓ Connected")

# Load parquet file
print(f"\n[2/3] Loading parquet file...")
df = pd.read_parquet(PARQUET_FILE)
print(f"✓ Loaded {len(df):,} trades")
print(f"  Columns: {df.columns.tolist()}")

# Upload to MotherDuck
print(f"\n[3/3] Uploading to table '{TABLE_NAME}'...")
conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
conn.execute(f"CREATE TABLE {TABLE_NAME} AS SELECT * FROM df")

# Verify upload
count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
print(f"✓ Uploaded {count:,} rows to MotherDuck")

# Show sample
print("\nSample data:")
sample = conn.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 3").df()
print(sample.to_string(index=False))

# Show summary stats
print("\nSummary statistics:")
stats = conn.execute(f"""
    SELECT 
        COUNT(*) as TotalTrades,
        SUM(CASE WHEN NetProfit > 0 THEN 1 ELSE 0 END) as Winners,
        SUM(CASE WHEN NetProfit < 0 THEN 1 ELSE 0 END) as Losers,
        ROUND(SUM(NetProfit), 2) as TotalNetProfit,
        ROUND(AVG(NetProfit), 2) as AvgNetProfit,
        COUNT(DISTINCT Symbol) as UniqueSymbols,
        COUNT(DISTINCT ATRPeriod) as ATRPeriods,
        COUNT(DISTINCT Multiplier) as Multipliers
    FROM {TABLE_NAME}
""").df()
print(stats.to_string(index=False))

conn.close()
print("\n✓ Upload complete!")
print("="*80)
