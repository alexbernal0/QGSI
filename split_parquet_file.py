"""
Split the large 972MB parquet file into smaller chunks
This allows processing without memory issues
"""

import pandas as pd
import pyarrow.parquet as pq
import os

print("=" * 80)
print("SPLITTING LARGE PARQUET FILE INTO CHUNKS")
print("=" * 80)

# Load just the symbol list
print("\n[1/3] Getting symbol list...")
data_path = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
table = pq.read_table(data_path, columns=['Symbol'])
df_symbols = table.to_pandas()
all_symbols = sorted(df_symbols['Symbol'].unique())
del df_symbols, table

print(f"✓ Found {len(all_symbols)} symbols")

# Split into chunks
SYMBOLS_PER_CHUNK = 20  # 20 symbols per file
num_chunks = (len(all_symbols) + SYMBOLS_PER_CHUNK - 1) // SYMBOLS_PER_CHUNK

print(f"✓ Will create {num_chunks} chunk files ({SYMBOLS_PER_CHUNK} symbols each)")

# Create chunks directory
chunks_dir = '/home/ubuntu/stage4_optimization/data_chunks'
os.makedirs(chunks_dir, exist_ok=True)

print(f"\n[2/3] Creating chunk files...")

for chunk_num in range(num_chunks):
    start_idx = chunk_num * SYMBOLS_PER_CHUNK
    end_idx = min((chunk_num + 1) * SYMBOLS_PER_CHUNK, len(all_symbols))
    chunk_symbols = all_symbols[start_idx:end_idx]
    
    # Load only these symbols
    df_full = pd.read_parquet(data_path)
    df_chunk = df_full[df_full['Symbol'].isin(chunk_symbols)].copy()
    del df_full
    
    # Save chunk
    chunk_path = f'{chunks_dir}/chunk_{chunk_num:03d}.parquet'
    df_chunk.to_parquet(chunk_path, index=False)
    
    file_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
    print(f"  Chunk {chunk_num+1}/{num_chunks}: {len(chunk_symbols)} symbols, "
          f"{len(df_chunk):,} rows, {file_size_mb:.1f} MB")
    
    del df_chunk

print(f"\n[3/3] Summary...")
print(f"✓ Created {num_chunks} chunk files in: {chunks_dir}")
print(f"✓ Each chunk contains ~{SYMBOLS_PER_CHUNK} symbols")

# List chunk files
chunk_files = sorted([f for f in os.listdir(chunks_dir) if f.endswith('.parquet')])
total_size_mb = sum(os.path.getsize(os.path.join(chunks_dir, f)) for f in chunk_files) / (1024 * 1024)
print(f"✓ Total size: {total_size_mb:.1f} MB")

print(f"\n{'='*80}")
print(f"✓ SPLITTING COMPLETE!")
print(f"{'='*80}\n")
