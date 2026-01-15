"""
QGSI Stage 4 Phase 2: Fixed ATR Asymmetric - SHORT SIGNALS ONLY
===============================================================================

Asymmetric stop loss and profit target strategy with INVERTED logic for shorts.
Processing SHORT signals with tighter stops and wider targets.

Strategy Parameters:
- ATR Periods: [14, 20, 30, 50]
- Stop Multipliers: [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
- Target Multipliers: [3.0, 4.0, 5.0, 6.0]
- Total Combinations: 112 (4 × 7 × 4)
- Constraint: TargetMultiplier >= StopMultiplier
- Max Bars: 30
- Position Size: $100,000
- Signal Type: SHORT ONLY (Signal = -1)

CRITICAL: SHORT LOGIC INVERSION
- Entry: SELL at signal bar CLOSE
- Stop Loss: Entry + (ATR × StopMultiplier)  ← ABOVE entry (loss if price rises)
- Profit Target: Entry - (ATR × TargetMultiplier)  ← BELOW entry (profit if price falls)
- Exit Check: HIGH >= Stop (loss) OR LOW <= Target (profit)

Author: QGSI Research Team
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time

# Configuration
STRATEGY_NAME = "Fixed_ATR_Asymmetric"
ATR_PERIODS = [14, 20, 30, 50]
STOP_MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
TARGET_MULTIPLIERS = [3.0, 4.0, 5.0, 6.0]
MAX_BARS = 30
POSITION_SIZE = 100000.0
BATCH_SIZE = 10  # Process 10 symbols at a time

DATA_PATH = Path('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')
OUTPUT_DIR.mkdir(exist_ok=True)


def calculate_atr(df, period=14):
    """Calculate Average True Range using Wilder's smoothing."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def backtest_short_signals(df, symbol, atr_period, stop_mult, target_mult):
    """
    Backtest Fixed ATR Asymmetric on SHORT signals with INVERTED logic.
    
    SHORT POSITION:
    - Entry: SELL at CLOSE
    - Stop: Entry + (ATR × StopMult) ← Price rises = loss
    - Target: Entry - (ATR × TargetMult) ← Price falls = profit
    - Asymmetric: Target wider than Stop (TargetMult >= StopMult)
    
    Returns list of trade dictionaries.
    """
    
    trades = []
    
    # Filter for SHORT signals only (Signal = -1)
    signal_indices = df[df['Signal'] == -1].index.tolist()
    
    if len(signal_indices) == 0:
        return trades
    
    # Get ATR column name
    atr_col = f'ATR_{atr_period}'
    if atr_col not in df.columns:
        return trades
    
    # Convert to numpy for speed
    high_arr = df['High'].values
    low_arr = df['Low'].values
    close_arr = df['Close'].values
    atr_arr = df[atr_col].values
    
    trade_number = 0
    
    # Process EVERY SHORT signal independently
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        
        trade_number += 1
        entry_price = close_arr[entry_bar_idx]
        entry_atr = atr_arr[entry_bar_idx]
        
        # Skip if ATR not available
        if np.isnan(entry_atr) or entry_atr == 0:
            continue
        
        # Calculate shares (short position)
        shares = POSITION_SIZE / entry_price
        
        # SHORT LOGIC: Stop ABOVE entry, Target BELOW entry (ASYMMETRIC)
        stop_loss = entry_price + (stop_mult * entry_atr)        # Loss if price rises
        profit_target = entry_price - (target_mult * entry_atr)  # Profit if price falls (wider)
        
        # Simulate bars after entry
        exit_price = None
        exit_reason = None
        bars_in_trade = 0
        
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            bars_in_trade += 1
            
            # SHORT EXIT CHECK: HIGH hits stop (loss), LOW hits target (profit)
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
            
            # Time limit exit
            if bars_in_trade >= MAX_BARS:
                exit_price = close_arr[i]
                exit_reason = 'TIME'
                exit_bar_idx = i
                break
        
        # If no exit found, exit at time limit
        if exit_price is None:
            exit_bar_idx = min(entry_bar_idx + MAX_BARS, len(df) - 1)
            exit_price = close_arr[exit_bar_idx]
            exit_reason = 'TIME'
            bars_in_trade = exit_bar_idx - entry_bar_idx
        
        # Calculate P&L for SHORT position
        # Profit = Entry - Exit (we sold high, buy back low)
        net_profit = (entry_price - exit_price) * shares
        net_profit_pct = (net_profit / POSITION_SIZE) * 100
        
        # Record trade
        trades.append({
            'TradeNumber': trade_number,
            'SignalType': 'Short',
            'EntryTime': df.index[entry_bar_idx],
            'EntryPrice': entry_price,
            'EntryBar': entry_bar_idx,
            'ExitTime': df.index[exit_bar_idx],
            'ExitPrice': exit_price,
            'ExitBar': exit_bar_idx,
            'StopLoss': stop_loss,
            'ProfitTarget': profit_target,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'NetProfit': net_profit,
            'NetProfitPct': net_profit_pct,
            'ATR': entry_atr,
            'ATRPeriod': atr_period,
            'StopMultiplier': stop_mult,
            'TargetMultiplier': target_mult,
            'Symbol': symbol,
            'StrategyName': STRATEGY_NAME
        })
    
    return trades


def calculate_performance_metrics(trades_df):
    """Calculate comprehensive performance metrics."""
    
    if len(trades_df) == 0:
        return {
            'TotalTrades': 0,
            'WinningTrades': 0,
            'LosingTrades': 0,
            'WinRate': 0.0,
            'TotalProfit': 0.0,
            'TotalLoss': 0.0,
            'NetProfit': 0.0,
            'ProfitFactor': 0.0,
            'AvgWin': 0.0,
            'AvgLoss': 0.0,
            'AvgWinLossRatio': 0.0,
            'SystemScore': 0.0
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
    
    # System Score = Net Profit × Profit Factor
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


def process_batch(symbols_batch, batch_num, atr_period, stop_mult, target_mult):
    """Process one batch of symbols for one parameter combination."""
    
    # Load data for batch
    df_batch = pd.read_parquet(DATA_PATH, filters=[('Symbol', 'in', symbols_batch)])
    
    all_trades = []
    
    for symbol in symbols_batch:
        # Filter symbol data
        df_symbol = df_batch[df_batch['Symbol'] == symbol].copy()
        
        if len(df_symbol) == 0:
            continue
        
        df_symbol = df_symbol.sort_values('BarDateTime').reset_index(drop=True)
        df_symbol.set_index('BarDateTime', inplace=True)
        
        # Calculate ATR for this period
        df_symbol[f'ATR_{atr_period}'] = calculate_atr(df_symbol, period=atr_period)
        
        # Run backtest
        trades = backtest_short_signals(df_symbol, symbol, atr_period, stop_mult, target_mult)
        all_trades.extend(trades)
    
    return all_trades


def main():
    """Main processing function."""
    
    print("="*80)
    print("QGSI STAGE 4 PHASE 2: FIXED ATR ASYMMETRIC - SHORT SIGNALS")
    print("="*80)
    print(f"Strategy: {STRATEGY_NAME}")
    print(f"Signal Type: SHORT ONLY (Signal = -1)")
    print(f"ATR Periods: {ATR_PERIODS}")
    print(f"Stop Multipliers: {STOP_MULTIPLIERS}")
    print(f"Target Multipliers: {TARGET_MULTIPLIERS}")
    print(f"Total Combinations: {len(ATR_PERIODS) * len(STOP_MULTIPLIERS) * len(TARGET_MULTIPLIERS)}")
    print(f"Constraint: Target >= Stop")
    print(f"Max Bars: {MAX_BARS}")
    print(f"Position Size: ${POSITION_SIZE:,.0f}")
    print(f"Batch Size: {BATCH_SIZE} symbols")
    print("="*80)
    
    start_time = time.time()
    
    # Get unique symbols
    print("\n[1/5] Loading symbol list...")
    df_symbols = pd.read_parquet(DATA_PATH, columns=['Symbol', 'Signal'])
    symbols = sorted(df_symbols['Symbol'].unique())
    print(f"✓ Found {len(symbols)} symbols")
    
    # Count SHORT signals
    short_signals = df_symbols[df_symbols['Signal'] == -1].shape[0]
    print(f"✓ Found {short_signals:,} SHORT signals")
    del df_symbols
    
    # Create symbol batches
    symbol_batches = [symbols[i:i+BATCH_SIZE] for i in range(0, len(symbols), BATCH_SIZE)]
    print(f"✓ Created {len(symbol_batches)} batches of {BATCH_SIZE} symbols")
    
    # Process all combinations
    total_combos = len(ATR_PERIODS) * len(STOP_MULTIPLIERS) * len(TARGET_MULTIPLIERS)
    print(f"\n[2/5] Processing {total_combos} combinations...")
    
    results = []
    all_trades_list = []  # Store ALL trades for parquet export
    combo_num = 0
    
    for atr_period in ATR_PERIODS:
        for stop_mult in STOP_MULTIPLIERS:
            for target_mult in TARGET_MULTIPLIERS:
                # Skip if target < stop (constraint)
                if target_mult < stop_mult:
                    continue
                
                combo_num += 1
                combo_start = time.time()
                
                print(f"\n  [{combo_num}/{total_combos}] ATR({atr_period}) Stop:{stop_mult:.1f}× Target:{target_mult:.1f}×")
                
                combo_trades = []
                
                # Process each batch
                for batch_num, symbols_batch in enumerate(symbol_batches, 1):
                    if batch_num % 10 == 0:
                        print(f"    Batch {batch_num}/{len(symbol_batches)}...", end=" ")
                    
                    batch_trades = process_batch(symbols_batch, batch_num, atr_period, stop_mult, target_mult)
                    combo_trades.extend(batch_trades)
                    
                    if batch_num % 10 == 0:
                        print(f"{len(batch_trades)} trades")
                
                all_trades_list.extend(combo_trades)
                
                # Calculate metrics
                trades_df = pd.DataFrame(combo_trades)
                metrics = calculate_performance_metrics(trades_df)
                
                # Store result
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
                print(f"    ✓ {metrics['TotalTrades']} trades, ${metrics['NetProfit']:,.0f}, PF:{metrics['ProfitFactor']:.3f} ({elapsed:.1f}s)")
    
    # Save performance results
    print("\n[3/5] Saving performance results...")
    results_df = pd.DataFrame(results)
    
    # Sort by System Score
    results_df = results_df.sort_values('SystemScore', ascending=False).reset_index(drop=True)
    results_df.insert(0, 'Rank', range(1, len(results_df) + 1))
    
    output_file = OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv'
    results_df.to_csv(output_file, index=False)
    print(f"✓ Saved performance summary: {output_file}")
    
    # Save all trade logs to parquet
    print("\n[4/5] Saving trade logs...")
    if len(all_trades_list) > 0:
        trades_df = pd.DataFrame(all_trades_list)
        parquet_file = OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_All_Trades.parquet'
        trades_df.to_parquet(parquet_file, index=False)
        print(f"✓ Saved {len(trades_df):,} trade logs to: {parquet_file}")
    else:
        print("⚠ No trades to save")
    
    # Print summary
    print("\n[5/5] Summary")
    print("="*80)
    print("TOP 5 CONFIGURATIONS (SHORT SIGNALS)")
    print("="*80)
    print(results_df[['Rank', 'ATRPeriod', 'StopMultiplier', 'TargetMultiplier', 
                      'SystemScore', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']].head(5).to_string(index=False))
    
    total_time = time.time() - start_time
    print(f"\n✓ Processing complete in {total_time/60:.1f} minutes")
    print(f"✓ Total trades processed: {len(all_trades_list):,}")
    print("="*80)


if __name__ == '__main__':
    main()
