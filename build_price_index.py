"""
Build lightweight price/ATR index for portfolio simulation
"""

import pandas as pd
import numpy as np
import os

print("Building price/ATR index...")

chunk_files = sorted([f for f in os.listdir('/home/ubuntu/stage4_optimization/data_chunks') 
                      if f.startswith('chunk_') and f.endswith('.parquet')])

price_index = []

for i, chunk_file in enumerate(chunk_files):
    print(f"Processing chunk {i+1}/{len(chunk_files)}...")
    chunk_path = f'/home/ubuntu/stage4_optimization/data_chunks/{chunk_file}'
    df = pd.read_parquet(chunk_path)
    
    for symbol in df['Symbol'].unique():
        symbol_data = df[df['Symbol'] == symbol].copy().sort_values('BarDate')
        
        # Calculate ATR
        high_low = symbol_data['High'] - symbol_data['Low']
        high_close = np.abs(symbol_data['High'] - symbol_data['Close'].shift())
        low_close = np.abs(symbol_data['Low'] - symbol_data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        symbol_data['ATR'] = tr.ewm(alpha=1/30, adjust=False).mean()
        
        # Keep only essential columns
        essential = symbol_data[['Symbol', 'BarDate', 'Open', 'High', 'Low', 'Close', 'Signal', 'ATR']].copy()
        price_index.append(essential)

print("Combining and saving...")
price_index_df = pd.concat(price_index, ignore_index=True)
price_index_df.to_parquet('/home/ubuntu/stage4_optimization/price_index.parquet', index=False)

print(f"✓ Price index saved: {len(price_index_df):,} rows")
print(f"✓ File size: {os.path.getsize('/home/ubuntu/stage4_optimization/price_index.parquet')/(1024*1024):.1f} MB")
