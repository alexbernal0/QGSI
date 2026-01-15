"""
QGSI Stage 4 Phase 2: ATR Breakeven Stop - SHORT SIGNALS
===============================================================================

Breakeven stop strategy: Stop moves to entry (breakeven) when price reaches 
a favorable trigger level. Inverted logic for SHORT positions.

Strategy Parameters:
- ATR Period: 30 (fixed)
- Initial Stop: 2.0× ATR (fixed)
- BE Triggers: [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
- Target Multipliers: [4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
- Total Combinations: 36 (6 × 6)
- Max Bars: 30
- Position Size: $100,000
- Signal Type: SHORT ONLY (Signal = -1)

SHORT LOGIC:
- Entry: SELL at signal bar CLOSE
- Initial Stop: Entry + (2.0× ATR) ← ABOVE entry (loss if price rises)
- BE Trigger: Entry - (BE_Trigger × ATR) ← BELOW entry (favorable move)
- When LOW <= BE_Trigger: Move stop to Entry (breakeven protection)
- Profit Target: Entry - (Target × ATR) ← BELOW entry (profit if price falls)
- Exit Check: HIGH >= Stop (loss) OR LOW <= Target (profit)

Author: QGSI Research Team
Date: 2026-01-13
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time

# Configuration
STRATEGY_NAME = "ATR_Breakeven_Stop"
ATR_PERIOD = 30
INITIAL_STOP_MULT = 2.0
BE_TRIGGERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
TARGET_MULTIPLIERS = [4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
MAX_BARS = 30
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


def backtest_short_breakeven(df, symbol, be_trigger, target_mult):
    """
    Backtest ATR Breakeven Stop on SHORT signals.
    
    SHORT POSITION:
    - Entry: SELL at CLOSE
    - Initial Stop: Entry + (2.0× ATR) ← Above entry
    - BE Trigger: Entry - (BE_Trigger × ATR) ← Below entry
    - When LOW <= BE_Trigger: Move stop to Entry
    - Target: Entry - (Target × ATR) ← Below entry
    
    Returns list of trade dictionaries with full TradeStation metrics.
    """
    
    trades = []
    
    # Filter for SHORT signals only (Signal = -1)
    signal_indices = df[df['Signal'] == -1].index.tolist()
    
    if len(signal_indices) == 0:
        return trades
    
    # Get ATR column
    atr_col = f'ATR_{ATR_PERIOD}'
    if atr_col not in df.columns:
        return trades
    
    # Convert to numpy for speed
    high_arr = df['High'].values
    low_arr = df['Low'].values
    close_arr = df['Close'].values
    atr_arr = df[atr_col].values
    datetime_arr = df.index.values
    
    trade_number = 0
    
    # Process EVERY SHORT signal independently
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        
        trade_number += 1
        entry_price = close_arr[entry_bar_idx]
        entry_atr = atr_arr[entry_bar_idx]
        entry_time = datetime_arr[entry_bar_idx]
        
        # Skip if ATR not available
        if np.isnan(entry_atr) or entry_atr == 0:
            continue
        
        # Calculate shares (short position)
        shares = POSITION_SIZE / entry_price
        
        # SHORT LOGIC: Stop ABOVE entry, Trigger & Target BELOW entry
        initial_stop = entry_price + (INITIAL_STOP_MULT * entry_atr)  # Loss if price rises
        be_trigger_level = entry_price - (be_trigger * entry_atr)     # Profit if price falls
        profit_target = entry_price - (target_mult * entry_atr)       # Profit if price falls
        
        # Track stop level (starts at initial, may move to breakeven)
        current_stop = initial_stop
        breakeven_triggered = False
        
        # Simulate bars after entry
        exit_price = None
        exit_reason = None
        bars_in_trade = 0
        
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            bars_in_trade += 1
            
            # Check if breakeven trigger hit (price moved favorably DOWN)
            if not breakeven_triggered and low_arr[i] <= be_trigger_level:
                current_stop = entry_price  # Move stop to breakeven
                breakeven_triggered = True
            
            # SHORT EXIT CHECK: HIGH hits stop (loss), LOW hits target (profit)
            if high_arr[i] >= current_stop:
                exit_price = current_stop
                exit_reason = 'BREAKEVEN' if breakeven_triggered and current_stop == entry_price else 'STOP'
                exit_bar_idx = i
                exit_time = datetime_arr[i]
                break
            elif low_arr[i] <= profit_target:
                exit_price = profit_target
                exit_reason = 'TARGET'
                exit_bar_idx = i
                exit_time = datetime_arr[i]
                break
            
            # Time limit exit
            if bars_in_trade >= MAX_BARS:
                exit_price = close_arr[i]
                exit_reason = 'TIME'
                exit_bar_idx = i
                exit_time = datetime_arr[i]
                break
        
        # If no exit found, exit at time limit
        if exit_price is None:
            exit_bar_idx = min(entry_bar_idx + MAX_BARS, len(df) - 1)
            exit_price = close_arr[exit_bar_idx]
            exit_reason = 'TIME'
            exit_time = datetime_arr[exit_bar_idx]
            bars_in_trade = exit_bar_idx - entry_bar_idx
        
        # Calculate P&L for SHORT position
        # Profit = Entry - Exit (we sold high, buy back low)
        net_profit = (entry_price - exit_price) * shares
        net_profit_pct = (net_profit / POSITION_SIZE) * 100
        
        # Record trade with FULL TradeStation metrics
        trades.append({
            'TradeNumber': trade_number,
            'SignalType': 'Short',
            'Symbol': symbol,
            'EntryTime': pd.Timestamp(entry_time),
            'EntryPrice': entry_price,
            'EntryBar': entry_bar_idx,
            'ExitTime': pd.Timestamp(exit_time),
            'ExitPrice': exit_price,
            'ExitBar': exit_bar_idx,
            'InitialStopLoss': initial_stop,
            'FinalStopLoss': current_stop,
            'BETriggerLevel': be_trigger_level,
            'ProfitTarget': profit_target,
            'BreakevenTriggered': breakeven_triggered,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'Shares': shares,
            'NetProfit': net_profit,
            'NetProfitPct': net_profit_pct,
            'ATR': entry_atr,
            'ATRPeriod': ATR_PERIOD,
            'InitialStopMultiplier': INITIAL_STOP_MULT,
            'BETrigger': be_trigger,
            'TargetMultiplier': target_mult,
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
            'BreakevenTriggeredPct': 0.0, 'AvgBarsInTrade': 0.0
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
    
    breakeven_triggered_pct = (trades_df['BreakevenTriggered'].sum() / len(trades_df)) * 100
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
        'BreakevenTriggeredPct': breakeven_triggered_pct,
        'AvgBarsInTrade': avg_bars
    }


def process_batch(symbols_batch, batch_num, be_trigger, target_mult):
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
        
        # Calculate ATR
        df_symbol[f'ATR_{ATR_PERIOD}'] = calculate_atr(df_symbol, period=ATR_PERIOD)
        
        # Run backtest
        trades = backtest_short_breakeven(df_symbol, symbol, be_trigger, target_mult)
        all_trades.extend(trades)
    
    return all_trades


def main():
    """Main processing function."""
    
    print("="*80)
    print("QGSI STAGE 4 PHASE 2: ATR BREAKEVEN STOP - SHORT SIGNALS")
    print("="*80)
    print(f"Strategy: {STRATEGY_NAME}")
    print(f"Signal Type: SHORT ONLY (Signal = -1)")
    print(f"ATR Period: {ATR_PERIOD} (fixed)")
    print(f"Initial Stop: {INITIAL_STOP_MULT}× ATR (fixed)")
    print(f"BE Triggers: {BE_TRIGGERS}")
    print(f"Target Multipliers: {TARGET_MULTIPLIERS}")
    print(f"Total Combinations: {len(BE_TRIGGERS) * len(TARGET_MULTIPLIERS)}")
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
    total_combos = len(BE_TRIGGERS) * len(TARGET_MULTIPLIERS)
    print(f"\n[2/5] Processing {total_combos} combinations...")
    
    results = []
    all_trades_list = []  # Store ALL trades for parquet export
    combo_num = 0
    
    for be_trigger in BE_TRIGGERS:
        for target_mult in TARGET_MULTIPLIERS:
            combo_num += 1
            combo_start = time.time()
            
            print(f"\n  [{combo_num}/{total_combos}] BE:{be_trigger:.1f}× Target:{target_mult:.1f}×")
            
            combo_trades = []
            
            # Process each batch
            for batch_num, symbols_batch in enumerate(symbol_batches, 1):
                if batch_num % 10 == 0:
                    print(f"    Batch {batch_num}/{len(symbol_batches)}...", end=" ")
                
                batch_trades = process_batch(symbols_batch, batch_num, be_trigger, target_mult)
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
                'ATRPeriod': ATR_PERIOD,
                'InitialStopMultiplier': INITIAL_STOP_MULT,
                'BETrigger': be_trigger,
                'TargetMultiplier': target_mult,
                **metrics
            }
            results.append(result)
            
            elapsed = time.time() - combo_start
            print(f"    ✓ {metrics['TotalTrades']} trades, ${metrics['NetProfit']:,.0f}, PF:{metrics['ProfitFactor']:.3f}, BE%:{metrics['BreakevenTriggeredPct']:.1f}% ({elapsed:.1f}s)")
    
    # Save performance results
    print("\n[3/5] Saving performance results...")
    results_df = pd.DataFrame(results)
    
    # Sort by System Score
    results_df = results_df.sort_values('SystemScore', ascending=False).reset_index(drop=True)
    results_df.insert(0, 'Rank', range(1, len(results_df) + 1))
    
    output_file = OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Performance.csv'
    results_df.to_csv(output_file, index=False)
    print(f"✓ Saved performance summary: {output_file}")
    
    # Save all trade logs to parquet
    print("\n[4/5] Saving trade logs...")
    if len(all_trades_list) > 0:
        trades_df = pd.DataFrame(all_trades_list)
        parquet_file = OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_All_Trades.parquet'
        trades_df.to_parquet(parquet_file, index=False)
        print(f"✓ Saved {len(trades_df):,} trade logs to: {parquet_file}")
        print(f"✓ Trade log size: {parquet_file.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("⚠ No trades to save")
    
    # Print summary
    print("\n[5/5] Summary")
    print("="*80)
    print("TOP 5 CONFIGURATIONS (SHORT SIGNALS)")
    print("="*80)
    print(results_df[['Rank', 'BETrigger', 'TargetMultiplier', 
                      'SystemScore', 'NetProfit', 'ProfitFactor', 'WinRate', 
                      'BreakevenTriggeredPct', 'TotalTrades']].head(5).to_string(index=False))
    
    total_time = time.time() - start_time
    print(f"\n✓ Processing complete in {total_time/60:.1f} minutes")
    print(f"✓ Total trades processed: {len(all_trades_list):,}")
    print("="*80)


if __name__ == '__main__':
    main()
