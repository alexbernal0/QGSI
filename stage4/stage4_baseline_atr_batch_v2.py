"""
QGSI Stage 4: Baseline ATR Strategy - Batch Processing (All 400 Symbols)
Uses local QGSI_AllSymbols_3Signals.parquet file with chunked loading
"""

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import duckdb
from datetime import datetime
import os

# Configuration
MOTHERDUCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'
DATA_FILE = '/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet'
PATH_DEP_FILE = '/home/ubuntu/path_dependency_results.parquet'
OUTPUT_DIR = '/home/ubuntu/stage4_results'
BATCH_SIZE = 40

# Strategy parameters
ATR_PERIOD = 30
ATR_MULT = 3.0
MAX_HOLD_BARS = 20
POSITION_SIZE = 100000

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load path dependency data once
print("Loading path dependency data...")
path_dep_data = pd.read_parquet(PATH_DEP_FILE)

def calculate_atr(df, period=30):
    """Calculate Average True Range"""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr

def run_backtest_single_direction(df, signal_type, path_data, atr_period=30, atr_mult=3.0, max_hold=20):
    """Run backtest for Long or Short signals"""
    
    # Calculate ATR on full dataframe first
    df = df.copy()
    df['ATR'] = calculate_atr(df, atr_period)
    
    # Filter for signal type
    signals = df[df['Signal'] == signal_type].copy()
    
    if len(signals) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    trades = []
    equity_curve = []
    current_equity = POSITION_SIZE
    peak_equity = POSITION_SIZE
    in_position = False
    
    for idx, signal_row in signals.iterrows():
        if in_position:
            continue
            
        entry_idx = idx
        entry_price = signal_row['Close']
        entry_time = signal_row['BarDateTime'] if 'BarDateTime' in signal_row else signal_row.name
        atr = signal_row['ATR']
        
        if pd.isna(atr) or atr == 0:
            continue
        
        # Set stop and target
        if signal_type == 1:  # Long
            stop_loss = entry_price - (atr * atr_mult)
            profit_target = entry_price + (atr * atr_mult)
        else:  # Short
            stop_loss = entry_price + (atr * atr_mult)
            profit_target = entry_price - (atr * atr_mult)
        
        # Get path dependency info
        path_info = path_data[
            (path_data['SignalIndex'] == signal_row.name) & 
            (path_data['SignalType'] == ('Long' if signal_type == 1 else 'Short'))
        ]
        
        # Simulate holding period
        entry_bar_idx = df.index.get_loc(entry_idx)
        exit_price = None
        exit_reason = None
        exit_time = None
        bars_in_trade = 0
        
        for i in range(1, max_hold + 1):
            if entry_bar_idx + i >= len(df):
                break
                
            bar = df.iloc[entry_bar_idx + i]
            bars_in_trade = i
            
            # Check stop/target
            if signal_type == 1:  # Long
                if bar['Low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_reason = 'STOP'
                    exit_time = bar['BarDateTime'] if 'BarDateTime' in bar else bar.name
                    break
                elif bar['High'] >= profit_target:
                    exit_price = profit_target
                    exit_reason = 'TARGET'
                    exit_time = bar['BarDateTime'] if 'BarDateTime' in bar else bar.name
                    break
            else:  # Short
                if bar['High'] >= stop_loss:
                    exit_price = stop_loss
                    exit_reason = 'STOP'
                    exit_time = bar['BarDateTime'] if 'BarDateTime' in bar else bar.name
                    break
                elif bar['Low'] <= profit_target:
                    exit_price = profit_target
                    exit_reason = 'TARGET'
                    exit_time = bar['BarDateTime'] if 'BarDateTime' in bar else bar.name
                    break
        
        # If no stop/target hit, exit at time limit
        if exit_price is None:
            final_bar = df.iloc[min(entry_bar_idx + max_hold, len(df) - 1)]
            exit_price = final_bar['Close']
            exit_reason = 'TIME'
            exit_time = final_bar['BarDateTime'] if 'BarDateTime' in final_bar else final_bar.name
            bars_in_trade = max_hold
        
        # Calculate P&L
        if signal_type == 1:  # Long
            pnl = exit_price - entry_price
        else:  # Short
            pnl = entry_price - exit_price
        
        pnl_pct = (pnl / entry_price) * 100
        pnl_dollars = (pnl / entry_price) * POSITION_SIZE
        
        # Update equity
        current_equity += pnl_dollars
        if current_equity > peak_equity:
            peak_equity = current_equity
        
        # Record trade
        trade_record = {
            'TradeNumber': len(trades) + 1,
            'SignalType': 'Long' if signal_type == 1 else 'Short',
            'EntryTime': entry_time,
            'EntryPrice': entry_price,
            'EntryBar': entry_bar_idx,
            'ExitTime': exit_time,
            'ExitPrice': exit_price,
            'ExitBar': entry_bar_idx + bars_in_trade,
            'StopLoss': stop_loss,
            'ProfitTarget': profit_target,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'NetProfit': pnl_dollars,
            'NetProfitPct': pnl_pct,
            'ATR': atr,
            'ATRMultiplier': atr_mult,
            'PathGroup': path_info['PathGroup'].values[0] if len(path_info) > 0 else 'Unknown',
            'SignalCount': signal_row['SignalCount'] if 'SignalCount' in signal_row else None,
            'FirstProfitTime': path_info['T_gain'].values[0] if len(path_info) > 0 else None,
            'FirstLossTime': path_info['T_loss'].values[0] if len(path_info) > 0 else None,
            'MAE': path_info['MAE'].values[0] if len(path_info) > 0 else None,
            'MFE': path_info['MFE'].values[0] if len(path_info) > 0 else None,
        }
        
        trades.append(trade_record)
        
        # Record equity point
        equity_record = {
            'TradeNumber': len(trades),
            'Equity': current_equity,
            'NetProfit': current_equity - POSITION_SIZE,
            'NetProfitPct': ((current_equity - POSITION_SIZE) / POSITION_SIZE) * 100,
            'PeakEquity': peak_equity,
            'Drawdown': peak_equity - current_equity,
            'DrawdownPct': ((peak_equity - current_equity) / peak_equity) * 100 if peak_equity > 0 else 0,
            'IsNewPeak': current_equity >= peak_equity
        }
        
        equity_curve.append(equity_record)
    
    return pd.DataFrame(trades), pd.DataFrame(equity_curve)

def process_symbol(symbol, all_data, path_data):
    """Process a single symbol"""
    
    # Filter data for this symbol
    df = all_data[all_data['Symbol'] == symbol].copy().reset_index(drop=True)
    
    if len(df) == 0:
        return None
    
    # Filter path data
    symbol_path_data = path_data[path_data['Symbol'] == symbol]
    
    # Run Long backtest
    long_trades, long_equity = run_backtest_single_direction(
        df, signal_type=1, path_data=symbol_path_data,
        atr_period=ATR_PERIOD, atr_mult=ATR_MULT, max_hold=MAX_HOLD_BARS
    )
    
    # Run Short backtest
    short_trades, short_equity = run_backtest_single_direction(
        df, signal_type=-1, path_data=symbol_path_data,
        atr_period=ATR_PERIOD, atr_mult=ATR_MULT, max_hold=MAX_HOLD_BARS
    )
    
    # Add symbol column
    if len(long_trades) > 0:
        long_trades['Symbol'] = symbol
        long_equity['Symbol'] = symbol
        long_equity['SignalType'] = 'Long'
    
    if len(short_trades) > 0:
        short_trades['Symbol'] = symbol
        short_equity['Symbol'] = symbol
        short_equity['SignalType'] = 'Short'
    
    # Calculate metrics
    long_wr = (long_trades['NetProfit'] > 0).mean() * 100 if len(long_trades) > 0 else 0
    short_wr = (short_trades['NetProfit'] > 0).mean() * 100 if len(short_trades) > 0 else 0
    long_return = long_equity['NetProfitPct'].iloc[-1] if len(long_equity) > 0 else 0
    short_return = short_equity['NetProfitPct'].iloc[-1] if len(short_equity) > 0 else 0
    
    print(f"  {symbol}: Long {len(long_trades)} trades, {long_wr:.1f}% WR, {long_return:+.2f}% | Short {len(short_trades)} trades, {short_wr:.1f}% WR, {short_return:+.2f}%")
    
    return {
        'long_trades': long_trades,
        'long_equity': long_equity,
        'short_trades': short_trades,
        'short_equity': short_equity
    }

# Main processing
print("="*80)
print("QGSI Stage 4: Baseline ATR Strategy - Batch Processing")
print("="*80)

# Get list of symbols from parquet file
parquet_file = pq.ParquetFile(DATA_FILE)
schema = parquet_file.schema_arrow

# Read symbols using DuckDB (more memory efficient)
conn_local = duckdb.connect()
symbols_df = conn_local.execute(f"""
    SELECT DISTINCT Symbol 
    FROM '{DATA_FILE}' 
    ORDER BY Symbol
""").df()

symbols = symbols_df['Symbol'].tolist()
print(f"Total symbols to process: {len(symbols)}")

# Process in batches
all_results = []

for batch_num in range(0, len(symbols), BATCH_SIZE):
    batch_symbols = symbols[batch_num:batch_num + BATCH_SIZE]
    
    print("="*80)
    print(f"BATCH {batch_num//BATCH_SIZE + 1}: Processing symbols {batch_num + 1} to {min(batch_num + BATCH_SIZE, len(symbols))}")
    print("="*80)
    
    # Load data for this batch
    batch_data = conn_local.execute(f"""
        SELECT * 
        FROM '{DATA_FILE}' 
        WHERE Symbol IN ({','.join([f"'{s}'" for s in batch_symbols])})
        ORDER BY Symbol, BarDateTime
    """).df()
    
    # Process each symbol
    for symbol in batch_symbols:
        print(f"Processing {symbol}...")
        result = process_symbol(symbol, batch_data, path_dep_data)
        
        if result:
            all_results.append(result)
    
    # Save batch results
    if all_results:
        # Combine all trades and equity curves
        all_long_trades = pd.concat([r['long_trades'] for r in all_results if len(r['long_trades']) > 0], ignore_index=True)
        all_short_trades = pd.concat([r['short_trades'] for r in all_results if len(r['short_trades']) > 0], ignore_index=True)
        all_long_equity = pd.concat([r['long_equity'] for r in all_results if len(r['long_equity']) > 0], ignore_index=True)
        all_short_equity = pd.concat([r['short_equity'] for r in all_results if len(r['short_equity']) > 0], ignore_index=True)
        
        # Save to parquet
        all_long_trades.to_parquet(f'{OUTPUT_DIR}/all_long_trades_batch{batch_num//BATCH_SIZE + 1}.parquet')
        all_short_trades.to_parquet(f'{OUTPUT_DIR}/all_short_trades_batch{batch_num//BATCH_SIZE + 1}.parquet')
        all_long_equity.to_parquet(f'{OUTPUT_DIR}/all_long_equity_batch{batch_num//BATCH_SIZE + 1}.parquet')
        all_short_equity.to_parquet(f'{OUTPUT_DIR}/all_short_equity_batch{batch_num//BATCH_SIZE + 1}.parquet')
        
        # Upload to MotherDuck
        conn_md = duckdb.connect(f'md:QGSI?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Combine trades
        all_trades = pd.concat([all_long_trades, all_short_trades], ignore_index=True)
        all_equity = pd.concat([all_long_equity, all_short_equity], ignore_index=True)
        
        # Upload (append mode)
        conn_md.execute("CREATE TABLE IF NOT EXISTS stage4_all_trades AS SELECT * FROM all_trades WHERE 1=0")
        conn_md.execute("INSERT INTO stage4_all_trades SELECT * FROM all_trades")
        
        conn_md.execute("CREATE TABLE IF NOT EXISTS stage4_all_equity AS SELECT * FROM all_equity WHERE 1=0")
        conn_md.execute("INSERT INTO stage4_all_equity SELECT * FROM all_equity")
        
        conn_md.close()
        
        print(f"Batch {batch_num//BATCH_SIZE + 1} saved to MotherDuck ({len(batch_symbols)} symbols)")

print("="*80)
print("PROCESSING COMPLETE!")
print("="*80)
print(f"Total symbols processed: {len(symbols)}")
print(f"Results saved to: {OUTPUT_DIR}/")
print("MotherDuck tables: stage4_all_trades, stage4_all_equity")
