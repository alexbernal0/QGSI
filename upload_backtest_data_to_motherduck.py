"""
Upload backtest data to MotherDuck database
Creates tables for trade logs and equity curves
"""

import duckdb
import os

# MotherDuck connection
MOTHERDUCK_TOKEN = os.environ.get('MOTHERDUCK_TOKEN')

print("=" * 80)
print("UPLOADING BACKTEST DATA TO MOTHERDUCK")
print("=" * 80)

# Connect to MotherDuck
print("\n[1/5] Connecting to MotherDuck...")
conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
print("✓ Connected")

# Create QGSI database if not exists
print("\n[2/5] Creating/using QGSI database...")
conn.execute("CREATE DATABASE IF NOT EXISTS qgsi")
conn.execute("USE qgsi")
print("✓ Using QGSI database")

# Upload LONG strategy trade logs
print("\n[3/5] Uploading LONG strategy data...")
print("  - Trade logs...")
conn.execute("""
    CREATE OR REPLACE TABLE best_long_strategy_trades AS 
    SELECT * FROM read_parquet('/home/ubuntu/stage4_optimization/Best_Long_Strategy_ATR_Trailing_Trades.parquet')
""")
long_trades_count = conn.execute("SELECT COUNT(*) FROM best_long_strategy_trades").fetchone()[0]
print(f"    ✓ {long_trades_count:,} trades uploaded")

print("  - Equity curves...")
conn.execute("""
    CREATE OR REPLACE TABLE best_long_strategy_equity_curves AS 
    SELECT * FROM read_parquet('/home/ubuntu/stage4_optimization/Best_Long_Strategy_Equity_Curves.parquet')
""")
long_equity_count = conn.execute("SELECT COUNT(*) FROM best_long_strategy_equity_curves").fetchone()[0]
print(f"    ✓ {long_equity_count:,} equity points uploaded")

# Upload SHORT strategy trade logs
print("\n[4/5] Uploading SHORT strategy data...")
print("  - Trade logs...")
conn.execute("""
    CREATE OR REPLACE TABLE best_short_strategy_trades AS 
    SELECT * FROM read_parquet('/home/ubuntu/stage4_optimization/Best_Short_Strategy_ATR_Trailing_Trades.parquet')
""")
short_trades_count = conn.execute("SELECT COUNT(*) FROM best_short_strategy_trades").fetchone()[0]
print(f"    ✓ {short_trades_count:,} trades uploaded")

print("  - Equity curves...")
conn.execute("""
    CREATE OR REPLACE TABLE best_short_strategy_equity_curves AS 
    SELECT * FROM read_parquet('/home/ubuntu/stage4_optimization/Best_Short_Strategy_Equity_Curves.parquet')
""")
short_equity_count = conn.execute("SELECT COUNT(*) FROM best_short_strategy_equity_curves").fetchone()[0]
print(f"    ✓ {short_equity_count:,} equity points uploaded")

# Verify tables
print("\n[5/5] Verifying tables...")
tables = conn.execute("SHOW TABLES").fetchall()
print(f"✓ Tables in QGSI database:")
for table in tables:
    table_name = table[0]
    if 'best_' in table_name.lower() and 'strategy' in table_name.lower():
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  - {table_name}: {count:,} rows")

conn.close()

print(f"\n{'='*80}")
print(f"✓ UPLOAD COMPLETE!")
print(f"{'='*80}\n")

print("Tables created in MotherDuck (qgsi database):")
print("  1. best_long_strategy_trades")
print("  2. best_long_strategy_equity_curves")
print("  3. best_short_strategy_trades")
print("  4. best_short_strategy_equity_curves")
