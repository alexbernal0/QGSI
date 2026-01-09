#!/usr/bin/env python3.11
"""
Check QGSI database tables
"""

import duckdb
import pandas as pd

# Connect to MotherDuck
MOTHERDUCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'
con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')

print("=== QGSI Database Tables ===\n")

# List tables in QGSI database
tables = con.execute("SHOW TABLES FROM QGSI").df()
print(f"Found {len(tables)} tables:\n")
print(tables)
print()

# For each table, show schema and row count
for table_name in tables['name']:
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print(f"{'='*60}")
    
    # Get row count
    try:
        count = con.execute(f"SELECT COUNT(*) as count FROM QGSI.{table_name}").df()
        print(f"Row count: {count['count'].iloc[0]:,}")
    except Exception as e:
        print(f"Error getting count: {e}")
    
    # Get schema
    try:
        schema = con.execute(f"DESCRIBE QGSI.{table_name}").df()
        print("\nSchema:")
        print(schema.to_string(index=False))
    except Exception as e:
        print(f"Error getting schema: {e}")
    
    # Show first few rows
    try:
        sample = con.execute(f"SELECT * FROM QGSI.{table_name} LIMIT 3").df()
        print(f"\nSample data (first 3 rows):")
        print(sample.to_string(index=False))
    except Exception as e:
        print(f"Error getting sample: {e}")

con.close()
