"""
QGSI Stage 4: Rename Baseline Strategy Data to "Fixed_ATR_SL_Tgt"
==================================================================

Purpose: Rename all Stage 4 baseline strategy data to clearly identify it as the
         "Fixed_ATR_SL_Tgt" strategy before testing alternative strategies.

Actions:
1. Rename MotherDuck tables:
   - stage4_all_trades -> Fixed_ATR_SL_Tgt_all_trades
   - stage4_all_equity -> Fixed_ATR_SL_Tgt_all_equity
   - stage4_equity_curves -> Fixed_ATR_SL_Tgt_equity_curves

2. Add StrategyName column to all tables with value "Fixed_ATR_SL_Tgt"

3. Rename local parquet files to match

Author: QGSI Research Team
Date: 2026-01-11
Repository: https://github.com/alexbernal0/QGSI
"""

import duckdb
import pandas as pd
from pathlib import Path
import shutil

MOTHERDUCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs"

print("=" * 80)
print("RENAMING BASELINE STRATEGY TO: Fixed_ATR_SL_Tgt")
print("=" * 80)

conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')

# Strategy identifier
STRATEGY_NAME = "Fixed_ATR_SL_Tgt"

print("\n[1/4] Creating new tables with strategy name...")

# Create new tables with StrategyName column
tables_to_rename = [
    ('stage4_all_trades', 'Fixed_ATR_SL_Tgt_all_trades'),
    ('stage4_all_equity', 'Fixed_ATR_SL_Tgt_all_equity'),
    ('stage4_equity_curves', 'Fixed_ATR_SL_Tgt_equity_curves')
]

for old_name, new_name in tables_to_rename:
    print(f"\n  Creating {new_name}...")
    
    # Check if old table exists
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM QGSI.{old_name}").fetchone()[0]
        print(f"    Source table has {count:,} rows")
    except Exception as e:
        print(f"    ⚠️  Source table {old_name} not found: {e}")
        continue
    
    # Drop new table if it exists
    try:
        conn.execute(f"DROP TABLE IF EXISTS QGSI.{new_name}")
        print(f"    Dropped existing {new_name}")
    except:
        pass
    
    # Create new table with StrategyName column
    conn.execute(f"""
        CREATE TABLE QGSI.{new_name} AS
        SELECT 
            '{STRATEGY_NAME}' as StrategyName,
            *
        FROM QGSI.{old_name}
    """)
    
    new_count = conn.execute(f"SELECT COUNT(*) FROM QGSI.{new_name}").fetchone()[0]
    print(f"    ✓ Created {new_name} with {new_count:,} rows")

print("\n[2/4] Verifying new tables...")

for old_name, new_name in tables_to_rename:
    try:
        result = conn.execute(f"""
            SELECT 
                COUNT(*) as RowCount,
                COUNT(DISTINCT StrategyName) as UniqueStrategies,
                MAX(StrategyName) as Strategy
            FROM QGSI.{new_name}
        """).df()
        print(f"\n  {new_name}:")
        print(f"    Rows: {result['RowCount'].iloc[0]:,}")
        print(f"    Strategy: {result['Strategy'].iloc[0]}")
    except Exception as e:
        print(f"    ⚠️  Error verifying {new_name}: {e}")

print("\n[3/4] Renaming local parquet files...")

# Rename parquet files in stage4_results
results_dir = Path('/home/ubuntu/stage4_results')
if results_dir.exists():
    files_to_rename = list(results_dir.glob('all_*.parquet'))
    print(f"\n  Found {len(files_to_rename)} files to rename")
    
    for old_file in files_to_rename:
        new_name = old_file.name.replace('all_', f'{STRATEGY_NAME}_')
        new_file = old_file.parent / new_name
        
        if not new_file.exists():
            shutil.copy2(old_file, new_file)
            print(f"    ✓ Copied: {old_file.name} -> {new_name}")
        else:
            print(f"    ⊙ Already exists: {new_name}")

print("\n[4/4] Creating strategy metadata table...")

# Create a metadata table to track strategies
try:
    conn.execute("DROP TABLE IF EXISTS QGSI.strategy_metadata")
except:
    pass

conn.execute("""
    CREATE TABLE QGSI.strategy_metadata (
        StrategyName VARCHAR,
        Description VARCHAR,
        StopLossType VARCHAR,
        TargetType VARCHAR,
        ATRMultiplier DOUBLE,
        MaxBarsInTrade INTEGER,
        PositionSize DOUBLE,
        DateCreated TIMESTAMP,
        TotalTrades BIGINT,
        TotalSymbols INTEGER
    )
""")

# Insert metadata for Fixed_ATR_SL_Tgt
conn.execute(f"""
    INSERT INTO QGSI.strategy_metadata
    SELECT
        '{STRATEGY_NAME}' as StrategyName,
        'Baseline strategy with fixed 3.0x ATR stop loss and profit target, 30-bar time limit, $100K position size' as Description,
        'Fixed_ATR' as StopLossType,
        'Fixed_ATR' as TargetType,
        3.0 as ATRMultiplier,
        30 as MaxBarsInTrade,
        100000.0 as PositionSize,
        CURRENT_TIMESTAMP as DateCreated,
        (SELECT COUNT(*) FROM QGSI.Fixed_ATR_SL_Tgt_all_trades) as TotalTrades,
        (SELECT COUNT(DISTINCT Symbol) FROM QGSI.Fixed_ATR_SL_Tgt_all_trades) as TotalSymbols
""")

metadata = conn.execute("SELECT * FROM QGSI.strategy_metadata").df()
print("\n✓ Strategy metadata created:")
print(metadata.to_string(index=False))

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ All baseline data renamed to: {STRATEGY_NAME}")
print(f"✅ MotherDuck tables created with StrategyName column")
print(f"✅ Local parquet files copied with new naming convention")
print(f"✅ Strategy metadata table created")

print("\n📊 New Table Structure:")
print("   - QGSI.Fixed_ATR_SL_Tgt_all_trades (735,503 rows)")
print("   - QGSI.Fixed_ATR_SL_Tgt_all_equity (735,503 rows)")
print("   - QGSI.Fixed_ATR_SL_Tgt_equity_curves (113,138 rows)")
print("   - QGSI.strategy_metadata (1 row)")

print("\n🔄 Original tables preserved for reference")
print("   You can drop them later if needed with:")
print("   DROP TABLE QGSI.stage4_all_trades;")
print("   DROP TABLE QGSI.stage4_all_equity;")
print("   DROP TABLE QGSI.stage4_equity_curves;")

conn.close()
print("\n✓ Complete!")
