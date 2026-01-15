"""
QGSI Stage 4 Phase 2: Fixed ATR Asymmetric - SHORT SIGNALS (CHUNKED)
===============================================================================

Processes one ATR period at a time and saves intermediate results.
This prevents data loss from sandbox resets.

Author: QGSI Research Team
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time
import sys

# Configuration
STRATEGY_NAME = "Fixed_ATR_Asymmetric"
ATR_PERIODS = [14, 20, 30, 50]
STOP_MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
TARGET_MULTIPLIERS = [3.0, 4.0, 5.0, 6.0]
MAX_BARS = 30
POSITION_SIZE = 100000.0
BATCH_SIZE = 10

DATA_PATH = Path('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')
OUTPUT_DIR.mkdir(exist_ok=True)


def calculate_atr(df, period=14):
    """Calculate Average True Range."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def backtest_short_signals(df, symbol, atr_period, stop_mult, target_mult):
    """Backtest SHORT signals with asymmetric exits."""
    trades = []
    signal_indices = df[df['Signal'] == -1].index.tolist()
    
    if len(signal_indices) == 0:
        return trades
    
    atr_col = f'ATR_{atr_period}'
    if atr_col not in df.columns:
        return trades
    
    high_arr = df['High'].values
    low_arr = df['Low'].values
    close_arr = df['Close'].values
    atr_arr = df[atr_col].values
    
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        entry_price = close_arr[entry_bar_idx]
        entry_atr = atr_arr[entry_bar_idx]
        
        if np.isnan(entry_atr) or entry_atr == 0:
            continue
        
        shares = POSITION_SIZE / entry_price
        stop_loss = entry_price + (stop_mult * entry_atr)
        profit_target = entry_price - (target_mult * entry_atr)
        
        exit_price = None
        exit_reason = None
        bars_in_trade = 0
        
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            bars_in_trade += 1
            
            if high_arr[i] >= stop_loss:
                exit_price = stop_loss
                exit_reason = 'STOP'
                exit_bar_idx = i
                break
            elif low_arr[i] <= profit_target:
                exit_price = profit_target
                exit_reason = 'TARGET'
                exit_bar_idx = i
                break
            
            if bars_in_trade >= MAX_BARS:
                exit_price = close_arr[i]
                exit_reason = 'TIME'
                exit_bar_idx = i
                break
        
        if exit_price is None:
            exit_bar_idx = min(entry_bar_idx + MAX_BARS, len(df) - 1)
            exit_price = close_arr[exit_bar_idx]
            exit_reason = 'TIME'
            bars_in_trade = exit_bar_idx - entry_bar_idx
        
        net_profit = (entry_price - exit_price) * shares
        
        trades.append({
            'SignalType': 'Short',
            'EntryPrice': entry_price,
            'ExitPrice': exit_price,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'NetProfit': net_profit,
            'ATRPeriod': atr_period,
            'StopMultiplier': stop_mult,
            'TargetMultiplier': target_mult,
            'Symbol': symbol,
            'StrategyName': STRATEGY_NAME
        })
    
    return trades


def calculate_performance_metrics(trades_df):
    """Calculate performance metrics."""
    if len(trades_df) == 0:
        return {
            'TotalTrades': 0, 'WinningTrades': 0, 'LosingTrades': 0,
            'WinRate': 0.0, 'TotalProfit': 0.0, 'TotalLoss': 0.0,
            'NetProfit': 0.0, 'ProfitFactor': 0.0, 'AvgWin': 0.0,
            'AvgLoss': 0.0, 'AvgWinLossRatio': 0.0, 'SystemScore': 0.0
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
        'SystemScore': system_score
    }


def process_atr_period(atr_period, symbols):
    """Process all combinations for one ATR period."""
    print(f"\n{'='*80}")
    print(f"PROCESSING ATR PERIOD: {atr_period}")
    print(f"{'='*80}")
    
    period_start = time.time()
    results = []
    
    # Create symbol batches
    symbol_batches = [symbols[i:i+BATCH_SIZE] for i in range(0, len(symbols), BATCH_SIZE)]
    
    combo_num = 0
    total_combos = len([1 for s in STOP_MULTIPLIERS for t in TARGET_MULTIPLIERS if t >= s])
    
    for stop_mult in STOP_MULTIPLIERS:
        for target_mult in TARGET_MULTIPLIERS:
            if target_mult < stop_mult:
                continue
            
            combo_num += 1
            combo_start = time.time()
            
            print(f"  [{combo_num}/{total_combos}] Stop:{stop_mult:.1f}× Target:{target_mult:.1f}×...", end=" ", flush=True)
            
            combo_trades = []
            
            for batch_num, symbols_batch in enumerate(symbol_batches):
                df_batch = pd.read_parquet(DATA_PATH, filters=[('Symbol', 'in', symbols_batch)])
                
                for symbol in symbols_batch:
                    df_symbol = df_batch[df_batch['Symbol'] == symbol].copy()
                    if len(df_symbol) == 0:
                        continue
                    
                    df_symbol = df_symbol.sort_values('BarDateTime').reset_index(drop=True)
                    df_symbol.set_index('BarDateTime', inplace=True)
                    df_symbol[f'ATR_{atr_period}'] = calculate_atr(df_symbol, period=atr_period)
                    
                    trades = backtest_short_signals(df_symbol, symbol, atr_period, stop_mult, target_mult)
                    combo_trades.extend(trades)
            
            trades_df = pd.DataFrame(combo_trades)
            metrics = calculate_performance_metrics(trades_df)
            
            result = {
                'StrategyName': STRATEGY_NAME,
                'SignalType': 'Short',
                'ATRPeriod': atr_period,
                'StopMultiplier': stop_mult,
                'TargetMultiplier': target_mult,
                **metrics
            }
            results.append(result)
            
            elapsed = time.time() - combo_start
            print(f"{metrics['TotalTrades']} trades, ${metrics['NetProfit']:,.0f}, PF:{metrics['ProfitFactor']:.3f} ({elapsed:.1f}s)")
    
    # Save results for this ATR period
    results_df = pd.DataFrame(results)
    output_file = OUTPUT_DIR / f'Fixed_ATR_Asymmetric_Short_ATR{atr_period}_Performance.csv'
    results_df.to_csv(output_file, index=False)
    
    period_elapsed = time.time() - period_start
    print(f"\n✓ ATR({atr_period}) complete in {period_elapsed/60:.1f} minutes")
    print(f"✓ Saved: {output_file}")
    
    return results_df


def main():
    """Main processing function."""
    
    print("="*80)
    print("QGSI STAGE 4 PHASE 2: FIXED ATR ASYMMETRIC - SHORT (CHUNKED)")
    print("="*80)
    print(f"Strategy: {STRATEGY_NAME}")
    print(f"Processing: ONE ATR PERIOD AT A TIME (4 chunks)")
    print(f"Combinations per chunk: 28")
    print(f"Total combinations: 112")
    print("="*80)
    
    start_time = time.time()
    
    # Get symbols
    print("\n[1/2] Loading symbol list...")
    df_symbols = pd.read_parquet(DATA_PATH, columns=['Symbol', 'Signal'])
    symbols = sorted(df_symbols['Symbol'].unique())
    short_signals = df_symbols[df_symbols['Signal'] == -1].shape[0]
    print(f"✓ Found {len(symbols)} symbols, {short_signals:,} SHORT signals")
    del df_symbols
    
    # Process each ATR period
    print("\n[2/2] Processing ATR periods...")
    all_results = []
    
    for atr_period in ATR_PERIODS:
        results_df = process_atr_period(atr_period, symbols)
        all_results.append(results_df)
    
    # Combine all results
    print("\n" + "="*80)
    print("COMBINING RESULTS")
    print("="*80)
    
    combined_df = pd.concat(all_results, ignore_index=True)
    combined_df = combined_df.sort_values('SystemScore', ascending=False).reset_index(drop=True)
    combined_df.insert(0, 'Rank', range(1, len(combined_df) + 1))
    
    final_output = OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv'
    combined_df.to_csv(final_output, index=False)
    print(f"✓ Saved combined results: {final_output}")
    
    # Print summary
    print("\n" + "="*80)
    print("TOP 5 CONFIGURATIONS")
    print("="*80)
    print(combined_df[['Rank', 'ATRPeriod', 'StopMultiplier', 'TargetMultiplier',
                       'SystemScore', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']].head(5).to_string(index=False))
    
    total_time = time.time() - start_time
    print(f"\n✓ Total processing time: {total_time/60:.1f} minutes")
    print("="*80)


if __name__ == '__main__':
    main()
