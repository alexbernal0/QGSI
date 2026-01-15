"""
Split large parquet file using streaming/batched reading
Never loads full dataset into memory
"""

import pyarrow.parquet as pq
import pyarrow as pa
import os

print("=" * 80)
print("SPLITTING LARGE PARQUET FILE (STREAMING MODE)")
print("=" * 80)

data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
chunks_dir = '/home/ubuntu/stage4_optimization/data_chunks'
os.makedirs(chunks_dir, exist_ok=True)

print("\n[1/2] Reading parquet file metadata...")
parquet_file = pq.ParquetFile(data_path)
print(f"✓ Total rows: {parquet_file.metadata.num_rows:,}")
print(f"✓ Total row groups: {parquet_file.num_row_groups}")

# Read in batches and group by symbol
print("\n[2/2] Processing in batches...")

BATCH_SIZE = 100000  # Read 100K rows at a time
symbol_buffers = {}  # Store rows by symbol
SYMBOLS_PER_CHUNK = 10  # Group 10 symbols per chunk file
chunk_counter = 0

for batch_num, batch in enumerate(parquet_file.iter_batches(batch_size=BATCH_SIZE)):
    df_batch = batch.to_pandas()
    
    # Group by symbol
    for symbol in df_batch['Symbol'].unique():
        if symbol not in symbol_buffers:
            symbol_buffers[symbol] = []
        
        symbol_data = df_batch[df_batch['Symbol'] == symbol]
        symbol_buffers[symbol].append(symbol_data)
    
    # When we have enough symbols, write a chunk
    if len(symbol_buffers) >= SYMBOLS_PER_CHUNK:
        # Take first SYMBOLS_PER_CHUNK symbols
        symbols_to_write = list(symbol_buffers.keys())[:SYMBOLS_PER_CHUNK]
        
        # Combine their data
        chunk_dfs = []
        for sym in symbols_to_write:
            sym_df = pa.concat_tables([pa.Table.from_pandas(df) for df in symbol_buffers[sym]]).to_pandas()
            chunk_dfs.append(sym_df)
            del symbol_buffers[sym]
        
        # Write chunk
        import pandas as pd
        chunk_df = pd.concat(chunk_dfs, ignore_index=True)
        chunk_path = f'{chunks_dir}/chunk_{chunk_counter:03d}.parquet'
        chunk_df.to_parquet(chunk_path, index=False)
        
        file_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"  Chunk {chunk_counter}: {len(symbols_to_write)} symbols, "
              f"{len(chunk_df):,} rows, {file_size_mb:.1f} MB")
        
        chunk_counter += 1
        del chunk_df, chunk_dfs
    
    if (batch_num + 1) % 10 == 0:
        print(f"  Processed {(batch_num + 1) * BATCH_SIZE:,} rows...")

# Write remaining symbols
if symbol_buffers:
    chunk_dfs = []
    for sym, dfs in symbol_buffers.items():
        import pandas as pd
        sym_df = pd.concat(dfs, ignore_index=True)
        chunk_dfs.append(sym_df)
    
    chunk_df = pd.concat(chunk_dfs, ignore_index=True)
    chunk_path = f'{chunks_dir}/chunk_{chunk_counter:03d}.parquet'
    chunk_df.to_parquet(chunk_path, index=False)
    
    file_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
    print(f"  Chunk {chunk_counter}: {len(symbol_buffers)} symbols, "
          f"{len(chunk_df):,} rows, {file_size_mb:.1f} MB")

print(f"\n{'='*80}")
print(f"✓ Created {chunk_counter + 1} chunk files in: {chunks_dir}")
print(f"✓ SPLITTING COMPLETE!")
print(f"{'='*80}\n")
