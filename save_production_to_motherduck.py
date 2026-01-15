#!/usr/bin/env python3.11
"""
Save Production Portfolio Results to MotherDuck
"""

import duckdb
import pandas as pd
import os

print("="*80)
print("SAVING PRODUCTION RESULTS TO MOTHERDUCK")
print("="*80)

# Connect to MotherDuck
print("\n[1/3] Connecting to MotherDuck...")
token = os.environ.get('MOTHERDUCK_TOKEN')
if not token:
    print("ERROR: MOTHERDUCK_TOKEN not found in environment")
    exit(1)

conn = duckdb.connect(f'md:?motherduck_token={token}')
conn.execute("USE QGSI")
print("✓ Connected to MotherDuck database: QGSI")

# Load production results
print("\n[2/3] Loading production results...")
trades_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
summary_df = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Summary.csv')

print(f"✓ Loaded {len(trades_df):,} trades")
print(f"✓ Loaded {len(equity_df):,} equity points")
print(f"✓ Loaded summary statistics")

# Save to MotherDuck
print("\n[3/3] Saving to MotherDuck...")

# Drop tables if they exist
conn.execute("DROP TABLE IF EXISTS production_long_trades")
conn.execute("DROP TABLE IF EXISTS production_long_equity")
conn.execute("DROP TABLE IF EXISTS production_long_summary")

# Create and populate trades table
conn.execute("""
    CREATE TABLE production_long_trades AS 
    SELECT * FROM trades_df
""")
print(f"✓ Created table: production_long_trades ({len(trades_df):,} rows)")

# Create and populate equity table
conn.execute("""
    CREATE TABLE production_long_equity AS 
    SELECT * FROM equity_df
""")
print(f"✓ Created table: production_long_equity ({len(equity_df):,} rows)")

# Create and populate summary table
conn.execute("""
    CREATE TABLE production_long_summary AS 
    SELECT * FROM summary_df
""")
print(f"✓ Created table: production_long_summary (1 row)")

# Verify
print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

tables = conn.execute("SHOW TABLES").fetchall()
print("\nTables in QGSI database:")
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
    print(f"  • {table[0]}: {count:,} rows")

conn.close()

print("\n" + "="*80)
print("✓ MOTHERDUCK SAVE COMPLETE")
print("="*80)
