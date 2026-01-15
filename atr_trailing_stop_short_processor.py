"""
QGSI Stage 4 Phase 2: ATR Trailing Stop - SHORT SIGNALS
===============================================================================
Processes SHORT signals with trailing stop that moves DOWN as price falls.
Uses chunked processing to conserve memory and save intermediate results.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time

# Configuration
STRATEGY_NAME = "ATR_Trailing_Stop"
ATR_PERIOD = 30
MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
MAX_BARS = 20
POSITION_SIZE = 100000.0
BATCH_SIZE = 10

DATA_PATH = Path('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')
OUTPUT_DIR.mkdir(exist_ok=True)


def calculate_atr(df, period=30):
    """Calculate Average True Range."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def backtest_short_trailing(df, symbol, multiplier):
    """Backtest ATR Trailing Stop on SHORT signals."""
    
    trades = []
    signal_indices = df[df['Signal'] == -1].index.tolist()
    
    if len(signal_indices) == 0:
        return trades
    
    atr_col = f'ATR_{ATR_PERIOD}'
    if atr_col not in df.columns:
        return trades
    
    high_arr = df['High'].values
    low_arr = df['Low'].values
    close_arr = df['Close'].values
    atr_arr = df[atr_col].values
    datetime_arr = df.index.values
    
    trade_number = 0
    
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        trade_number += 1
        entry_price = close_arr[entry_bar_idx]
        entry_atr = atr_arr[entry_bar_idx]
        entry_time = datetime_arr[entry_bar_idx]
        
        if np.isnan(entry_atr) or entry_atr == 0:
            continue
        
        shares = POSITION_SIZE / entry_price
        
        # For SHORTS: Initial stop ABOVE entry (loss if price rises)
        initial_stop = entry_price + (multiplier * entry_atr)
        current_stop = initial_stop
        
        exit_price = None
        exit_reason = None
        bars_in_trade = 0
        
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            bars_in_trade += 1
            current_atr = atr_arr[i]
            
            if not np.isnan(current_atr) and current_atr > 0:
                # For SHORTS: Trailing stop moves DOWN (gets tighter) as price falls
                # Stop = MIN(previous_stop, Current HIGH + ATR × Multiplier)
                new_stop = high_arr[i] + (multiplier * current_atr)
                current_stop = min(current_stop, new_stop)
            
            # Check if stopped out (price rises to hit stop)
            if high_arr[i] >= current_stop:
                exit_price = current_stop
                exit_reason = 'STOP'
                exit_bar_idx = i
                exit_time = datetime_arr[i]
                break
            
            # Time limit
            if bars_in_trade >= MAX_BARS:
                exit_price = close_arr[i]
                exit_reason = 'TIME'
                exit_bar_idx = i
                exit_time = datetime_arr[i]
                break
        
        # If no exit found, close at time limit
        if exit_price is None:
            exit_bar_idx = min(entry_bar_idx + MAX_BARS, len(df) - 1)
            exit_price = close_arr[exit_bar_idx]
            exit_reason = 'TIME'
            exit_time = datetime_arr[exit_bar_idx]
            bars_in_trade = exit_bar_idx - entry_bar_idx
        
        # For SHORTS: Profit when exit price < entry price
        net_profit = (entry_price - exit_price) * shares
        net_profit_pct = (net_profit / POSITION_SIZE) * 100
        
        trades.append({
            'TradeNumber': trade_number,
            'SignalType': 'Short',
            'Symbol': symbol,
            'EntryTime': pd.Timestamp(entry_time),
            'EntryPrice': entry_price,
            'ExitTime': pd.Timestamp(exit_time),
            'ExitPrice': exit_price,
            'InitialStopLoss': initial_stop,
            'FinalStopLoss': current_stop,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'Shares': shares,
            'NetProfit': net_profit,
            'NetProfitPct': net_profit_pct,
            'ATR': entry_atr,
            'ATRPeriod': ATR_PERIOD,
            'Multiplier': multiplier,
            'StrategyName': STRATEGY_NAME
        })
    
    return trades


def calculate_performance_metrics(trades_df):
    """Calculate comprehensive performance metrics."""
    
    if len(trades_df) == 0:
        return {
            'TotalTrades': 0, 'WinningTrades': 0, 'LosingTrades': 0,
            'WinRate': 0.0, 'TotalProfit': 0.0, 'TotalLoss': 0.0,
            'NetProfit': 0.0, 'ProfitFactor': 0.0, 'AvgWin': 0.0,
            'AvgLoss': 0.0, 'AvgWinLossRatio': 0.0, 'SystemScore': 0.0,
            'AvgBarsInTrade': 0.0
        }
    
    winning_trades = trades_df[trades_df['NetProfit'] > 0]
    losing_trades = trades_df[trades_df['NetProfit'] < 0]
    
    total_profit = winning_trades['NetProfit'].sum() if len(winning_trades) > 0 else 0.0
    total_loss = abs(losing_trades['NetProfit'].sum()) if len(losing_trades) > 0 else 0.0
    net_profit = trades_df['NetProfit'].sum()
    
    profit_factor = total_profit / total_loss if total_loss > 0 else (10.0 if total_profit > 0 else 0.0)
    avg_win = winning_trades['NetProfit'].mean() if len(winning_trades) > 0 else 0.0
    avg_loss = abs(losing_trades['NetProfit'].mean()) if len(losing_trades) > 0 else 0.0
    avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0
    system_score = net_profit * profit_factor
    avg_bars = trades_df['BarsInTrade'].mean()
    
    return {
        'TotalTrades': len(trades_df),
        'WinningTrades': len(winning_trades),
        'LosingTrades': len(losing_trades),
        'WinRate': len(winning_trades) / len(trades_df) if len(trades_df) > 0 else 0.0,
        'TotalProfit': total_profit,
        'TotalLoss': total_loss,
        'NetProfit': net_profit,
        'ProfitFactor': profit_factor,
        'AvgWin': avg_win,
        'AvgLoss': avg_loss,
        'AvgWinLossRatio': avg_win_loss_ratio,
        'SystemScore': system_score,
        'AvgBarsInTrade': avg_bars
    }


def main():
    """Main processing function."""
    
    print("="*80)
    print("QGSI STAGE 4 PHASE 2: ATR TRAILING STOP - SHORT SIGNALS")
    print("="*80)
    print(f"Strategy: {STRATEGY_NAME}")
    print(f"Signal Type: SHORT ONLY")
    print(f"ATR Period: {ATR_PERIOD} (Fixed)")
    print(f"Multipliers: {MULTIPLIERS}")
    print(f"Total Combinations: {len(MULTIPLIERS)}")
    print(f"Max Bars in Trade: {MAX_BARS}")
    print("="*80)
    
    start_time = time.time()
    
    # Get symbols
    print("\n[1/3] Loading symbol list...")
    df_symbols = pd.read_parquet(DATA_PATH, columns=['Symbol'])
    symbols = sorted(df_symbols['Symbol'].unique())
    print(f"✓ Found {len(symbols)} symbols")
    del df_symbols
    
    # Create symbol batches
    symbol_batches = [symbols[i:i+BATCH_SIZE] for i in range(0, len(symbols), BATCH_SIZE)]
    print(f"✓ Created {len(symbol_batches)} batches of {BATCH_SIZE} symbols each")
    
    # Process each multiplier
    print(f"\n[2/3] Processing {len(MULTIPLIERS)} multipliers...")
    all_results = []
    
    for mult_idx, multiplier in enumerate(MULTIPLIERS, 1):
        mult_start = time.time()
        print(f"\n  [{mult_idx}/{len(MULTIPLIERS)}] Multiplier: {multiplier:.1f}×")
        
        mult_trades = []
        
        # Process each batch
        for batch_num, symbols_batch in enumerate(symbol_batches, 1):
            # Load data for batch
            df_batch = pd.read_parquet(DATA_PATH, filters=[('Symbol', 'in', symbols_batch)])
            
            for symbol in symbols_batch:
                df_symbol = df_batch[df_batch['Symbol'] == symbol].copy()
                
                if len(df_symbol) == 0:
                    continue
                
                df_symbol = df_symbol.sort_values('BarDateTime').reset_index(drop=True)
                df_symbol.set_index('BarDateTime', inplace=True)
                df_symbol[f'ATR_{ATR_PERIOD}'] = calculate_atr(df_symbol, period=ATR_PERIOD)
                
                trades = backtest_short_trailing(df_symbol, symbol, multiplier)
                mult_trades.extend(trades)
            
            if batch_num % 10 == 0:
                print(f"    Batch {batch_num}/{len(symbol_batches)}... {len(mult_trades)} trades")
        
        # Calculate metrics
        trades_df = pd.DataFrame(mult_trades)
        metrics = calculate_performance_metrics(trades_df)
        
        result = {
            'StrategyName': STRATEGY_NAME,
            'SignalType': 'Short',
            'ATRPeriod': ATR_PERIOD,
            'Multiplier': multiplier,
            **metrics
        }
        all_results.append(result)
        
        elapsed = time.time() - mult_start
        print(f"    ✓ {metrics['TotalTrades']} trades, ${metrics['NetProfit']:,.0f}, PF:{metrics['ProfitFactor']:.3f} ({elapsed:.1f}s)")
    
    # Save results
    print(f"\n[3/3] Saving results...")
    results_df = pd.DataFrame(all_results)
    results_df = results_df.sort_values('SystemScore', ascending=False).reset_index(drop=True)
    results_df.insert(0, 'Rank', range(1, len(results_df) + 1))
    
    output_file = OUTPUT_DIR / 'ATR_Trailing_Stop_Short_Performance.csv'
    results_df.to_csv(output_file, index=False)
    print(f"✓ Saved performance: {output_file}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("="*80)
    print("TOP 5 CONFIGURATIONS")
    print("="*80)
    print(results_df[['Rank', 'Multiplier', 'SystemScore', 'NetProfit', 'ProfitFactor', 
                      'WinRate', 'TotalTrades']].head(5).to_string(index=False))
    
    total_time = time.time() - start_time
    print(f"\n✓ Total processing time: {total_time/60:.1f} minutes")
    print("="*80)


if __name__ == '__main__':
    main()
