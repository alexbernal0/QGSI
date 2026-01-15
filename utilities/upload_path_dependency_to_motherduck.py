#!/usr/bin/env python3.11
"""
Upload path dependency analysis results to MotherDuck
"""

import duckdb
import pandas as pd
from pathlib import Path

# Connect to MotherDuck
MOTHERDUCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'
con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')

print("Loading path dependency data from parquet file...")
parquet_file = '/home/ubuntu/path_dependency_results.parquet'
df = pd.read_parquet(parquet_file)

print(f"Loaded {len(df):,} rows")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head())

# Upload to MotherDuck
print("\nUploading to MotherDuck QGSI database...")
con.execute("CREATE OR REPLACE TABLE QGSI.path_dependency_analysis AS SELECT * FROM df")

# Verify upload
count = con.execute("SELECT COUNT(*) as count FROM QGSI.path_dependency_analysis").df()
print(f"\nVerification: {count['count'].iloc[0]:,} rows in QGSI.path_dependency_analysis")

# Show schema
schema = con.execute("DESCRIBE QGSI.path_dependency_analysis").df()
print("\nTable schema:")
print(schema.to_string(index=False))

con.close()
print("\nUpload complete!")
