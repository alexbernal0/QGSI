"""
QGSI Stage 4: Baseline ATR Strategy - VectorBT Implementation

Author: Alex Bernal, Senior Quantitative Researcher
Date: January 09, 2026
Version: 1.0

DESCRIPTION:
    Vectorized implementation of baseline ATR strategy using VectorBT library.
    Significantly faster than manual pandas implementation for multi-symbol backtesting.
    
STRATEGY LOGIC:
    Same as manual pandas version (stage4_baseline_atr_strategy.py)
    
PERFORMANCE:
    VectorBT uses NumPy vectorization for ~10-100× speedup vs. manual iteration.
    Critical for scaling to all 400 symbols.

USAGE:
    python3.11 stage4_baseline_atr_vectorbt.py --symbol AAPL --atr_period 30 --atr_mult 3.0
"""

import pandas as pd
import numpy as np
import duckdb
import vectorbt as vbt
import time
import argparse

# MotherDuck token
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'


def calculate_atr(df, period=30):
    """Calculate ATR using vectorized operations."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def backtest_vectorbt(df, signal_type='long', atr_period=30, atr_mult=3.0, 
                      starting_capital=100000, max_bars=20):
    """
    Backtest using VectorBT for vectorized performance.
    
    Args:
        df: DataFrame with OHLC and Signal data
        signal_type: 'long' or 'short'
        atr_period: ATR calculation period
        atr_mult: ATR multiplier for stop/target
        starting_capital: Starting capital ($)
        max_bars: Maximum bars to hold position
    
    Returns:
        equity_curve: DataFrame with bar-by-bar equity
        trades: DataFrame with trade log
        metrics: Dict with performance metrics
        execution_time: Time taken for backtest
    """
    
    start_time = time.time()
    
    # Calculate ATR
    df['ATR'] = calculate_atr(df, period=atr_period)
    
    # Filter signals
    if signal_type == 'long':
        signal_value = 1
    else:
        signal_value = -1
    
    # Create entry signals
    entries = (df['Signal'] == signal_value).values
    
    # Create stop loss and profit target arrays
    stops = np.full(len(df), np.nan)
    targets = np.full(len(df), np.nan)
    
    # Calculate stops and targets at signal bars
    signal_indices = np.where(entries)[0]
    for idx in signal_indices:
        if pd.notna(df['ATR'].iloc[idx]):
            entry_price = df['Close'].iloc[idx]
            atr_value = df['ATR'].iloc[idx]
            
            if signal_type == 'long':
                stops[idx] = entry_price - (atr_mult * atr_value)
                targets[idx] = entry_price + (atr_mult * atr_value)
            else:
                stops[idx] = entry_price + (atr_mult * atr_value)
                targets[idx] = entry_price - (atr_mult * atr_value)
    
    # Forward fill stops and targets for active positions
    stops_series = pd.Series(stops).ffill()
    targets_series = pd.Series(targets).ffill()
    
    # Create exit signals
    if signal_type == 'long':
        stop_hit = df['Low'] <= stops_series
        target_hit = df['High'] >= targets_series
    else:
        stop_hit = df['High'] >= stops_series
        target_hit = df['Low'] <= targets_series
    
    # Time-based exit: create signal for max_bars after entry
    time_exit = np.zeros(len(df), dtype=bool)
    for idx in signal_indices:
        if idx + max_bars < len(df):
            time_exit[idx + max_bars] = True
    
    # Combine exit signals
    exits = stop_hit | target_hit | time_exit
    
    # Use VectorBT Portfolio to simulate trading
    # Calculate position size (number of shares per trade)
    position_sizes = (starting_capital / df['Close']).astype(int)
    
    # Create portfolio
    pf = vbt.Portfolio.from_signals(
        close=df['Close'],
        entries=entries,
        exits=exits,
        size=position_sizes,
        size_type='amount',
        init_cash=starting_capital,
        fees=0.0,  # No fees/slippage
        slippage=0.0,
        freq='1min'
    )
    
    execution_time = time.time() - start_time
    
    # Extract equity curve
    equity_curve = pd.DataFrame({
        'BarIndex': range(len(df)),
        'Datetime': df['Datetime'].values,
        'Equity': pf.value().values,
        'InPosition': pf.position_mask().values,
        'Symbol': df['Symbol'].iloc[0] if 'Symbol' in df.columns else 'UNKNOWN',
        'Strategy': 'Baseline_ATR_VectorBT',
        'SignalType': signal_type.upper(),
        'ATR_Period': atr_period,
        'ATR_Mult': atr_mult
    })
    
    # Extract trades
    trades_df = pf.trades.records_readable
    
    if len(trades_df) > 0:
        # Rename columns to match manual implementation
        trades_df = trades_df.rename(columns={
            'Entry Index': 'EntryBar',
            'Exit Index': 'ExitBar',
            'Entry Price': 'EntryPrice',
            'Exit Price': 'ExitPrice',
            'Size': 'PositionSize',
            'PnL': 'PnL',
            'Return': 'PnL_Pct'
        })
        
        # Add datetime columns
        trades_df['EntryDatetime'] = df['Datetime'].iloc[trades_df['EntryBar'].values].values
        trades_df['ExitDatetime'] = df['Datetime'].iloc[trades_df['ExitBar'].values].values
        
        # Calculate bars held
        trades_df['BarsHeld'] = trades_df['ExitBar'] - trades_df['EntryBar']
        
        # Add stop/target info
        trades_df['StopLoss'] = stops_series.iloc[trades_df['EntryBar'].values].values
        trades_df['ProfitTarget'] = targets_series.iloc[trades_df['EntryBar'].values].values
        
        # Determine exit reason
        def get_exit_reason(row):
            exit_bar = int(row['ExitBar'])
            if signal_type == 'long':
                if df['Low'].iloc[exit_bar] <= row['StopLoss']:
                    return 'Stop Loss'
                elif df['High'].iloc[exit_bar] >= row['ProfitTarget']:
                    return 'Profit Target'
            else:
                if df['High'].iloc[exit_bar] >= row['StopLoss']:
                    return 'Stop Loss'
                elif df['Low'].iloc[exit_bar] <= row['ProfitTarget']:
                    return 'Profit Target'
            return 'Time Exit (20 bars)'
        
        trades_df['ExitReason'] = trades_df.apply(get_exit_reason, axis=1)
        trades_df['SignalType'] = signal_type
        trades_df['Symbol'] = df['Symbol'].iloc[0] if 'Symbol' in df.columns else 'UNKNOWN'
        trades_df['Strategy'] = 'Baseline_ATR_VectorBT'
        trades_df['ATR_Period'] = atr_period
        trades_df['ATR_Mult'] = atr_mult
        
        # Convert PnL_Pct to percentage
        trades_df['PnL_Pct'] = trades_df['PnL_Pct'] * 100
    
    # Calculate metrics
    if len(trades_df) > 0:
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['PnL'] > 0])
        losing_trades = len(trades_df[trades_df['PnL'] < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_wins = trades_df[trades_df['PnL'] > 0]['PnL'].sum()
        total_losses = abs(trades_df[trades_df['PnL'] < 0]['PnL'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        net_profit = trades_df['PnL'].sum()
        avg_trade = trades_df['PnL'].mean()
        
        # Max drawdown
        equity_curve['Peak'] = equity_curve['Equity'].cummax()
        equity_curve['Drawdown'] = equity_curve['Equity'] - equity_curve['Peak']
        equity_curve['Drawdown_Pct'] = (equity_curve['Drawdown'] / equity_curve['Peak']) * 100
        max_drawdown = equity_curve['Drawdown'].min()
        max_drawdown_pct = equity_curve['Drawdown_Pct'].min()
        
        # Sharpe Ratio
        returns = equity_curve['Equity'].pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252 * 390) if returns.std() > 0 else 0
        
        metrics = {
            'SignalType': signal_type.upper(),
            'TotalTrades': total_trades,
            'WinningTrades': winning_trades,
            'LosingTrades': losing_trades,
            'WinRate': win_rate,
            'ProfitFactor': profit_factor,
            'NetProfit': net_profit,
            'NetProfit_Pct': (net_profit / starting_capital) * 100,
            'AvgTrade': avg_trade,
            'MaxDrawdown': max_drawdown,
            'MaxDrawdown_Pct': max_drawdown_pct,
            'SharpeRatio': sharpe_ratio,
            'FinalEquity': equity_curve['Equity'].iloc[-1],
            'StartingCapital': starting_capital,
            'ExecutionTime': execution_time
        }
    else:
        metrics = {
            'SignalType': signal_type.upper(),
            'TotalTrades': 0,
            'WinningTrades': 0,
            'LosingTrades': 0,
            'WinRate': 0,
            'ProfitFactor': 0,
            'NetProfit': 0,
            'NetProfit_Pct': 0,
            'AvgTrade': 0,
            'MaxDrawdown': 0,
            'MaxDrawdown_Pct': 0,
            'SharpeRatio': 0,
            'FinalEquity': starting_capital,
            'StartingCapital': starting_capital,
            'ExecutionTime': execution_time
        }
    
    return equity_curve, trades_df, metrics, execution_time


def main():
    parser = argparse.ArgumentParser(description='QGSI Stage 4 Baseline ATR Strategy - VectorBT')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Symbol to backtest')
    parser.add_argument('--atr_period', type=int, default=30, help='ATR period')
    parser.add_argument('--atr_mult', type=float, default=3.0, help='ATR multiplier')
    parser.add_argument('--starting_capital', type=float, default=100000, help='Starting capital')
    parser.add_argument('--max_bars', type=int, default=20, help='Max bars to hold position')
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"QGSI Stage 4: Baseline ATR Strategy (VectorBT) - {args.symbol}")
    print(f"{'='*80}\n")
    
    # Load data
    print(f"Loading {args.symbol} data from MotherDuck...")
    conn = duckdb.connect(f'md:?motherduck_token={TOKEN}')
    
    query = f"""
        SELECT BarDateTime as Datetime, Symbol, Open, High, Low, Close, Signal, SignalCount
        FROM QGSI.signal_data
        WHERE Symbol = '{args.symbol}'
        ORDER BY BarDateTime
    """
    
    df = conn.execute(query).df()
    conn.close()
    
    print(f"Loaded {len(df):,} bars")
    print(f"Signals: {len(df[df['Signal'] == 1])} Long, {len(df[df['Signal'] == -1])} Short\n")
    
    # Backtest Long
    print("Backtesting LONG signals (VectorBT)...")
    equity_long, trades_long, metrics_long, time_long = backtest_vectorbt(
        df.copy(),
        signal_type='long',
        atr_period=args.atr_period,
        atr_mult=args.atr_mult,
        starting_capital=args.starting_capital,
        max_bars=args.max_bars
    )
    
    # Backtest Short
    print("Backtesting SHORT signals (VectorBT)...")
    equity_short, trades_short, metrics_short, time_short = backtest_vectorbt(
        df.copy(),
        signal_type='short',
        atr_period=args.atr_period,
        atr_mult=args.atr_mult,
        starting_capital=args.starting_capital,
        max_bars=args.max_bars
    )
    
    # Print results
    print(f"\n{'='*80}")
    print(f"BACKTEST RESULTS - {args.symbol} (VectorBT)")
    print(f"{'='*80}\n")
    
    print(f"{'Metric':<25} {'LONG':>15} {'SHORT':>15}")
    print(f"{'-'*25} {'-'*15} {'-'*15}")
    print(f"{'Total Trades':<25} {metrics_long['TotalTrades']:>15} {metrics_short['TotalTrades']:>15}")
    print(f"{'Winning Trades':<25} {metrics_long['WinningTrades']:>15} {metrics_short['WinningTrades']:>15}")
    print(f"{'Losing Trades':<25} {metrics_long['LosingTrades']:>15} {metrics_short['LosingTrades']:>15}")
    print(f"{'Win Rate %':<25} {metrics_long['WinRate']:>15.2f} {metrics_short['WinRate']:>15.2f}")
    print(f"{'Profit Factor':<25} {metrics_long['ProfitFactor']:>15.2f} {metrics_short['ProfitFactor']:>15.2f}")
    print(f"{'Net Profit $':<25} {metrics_long['NetProfit']:>15,.2f} {metrics_short['NetProfit']:>15,.2f}")
    print(f"{'Net Profit %':<25} {metrics_long['NetProfit_Pct']:>15.2f} {metrics_short['NetProfit_Pct']:>15.2f}")
    print(f"{'Avg Trade $':<25} {metrics_long['AvgTrade']:>15,.2f} {metrics_short['AvgTrade']:>15,.2f}")
    print(f"{'Max Drawdown $':<25} {metrics_long['MaxDrawdown']:>15,.2f} {metrics_short['MaxDrawdown']:>15,.2f}")
    print(f"{'Max Drawdown %':<25} {metrics_long['MaxDrawdown_Pct']:>15.2f} {metrics_short['MaxDrawdown_Pct']:>15.2f}")
    print(f"{'Sharpe Ratio':<25} {metrics_long['SharpeRatio']:>15.2f} {metrics_short['SharpeRatio']:>15.2f}")
    print(f"{'Final Equity $':<25} {metrics_long['FinalEquity']:>15,.2f} {metrics_short['FinalEquity']:>15,.2f}")
    print(f"{'Execution Time (s)':<25} {time_long:>15.4f} {time_short:>15.4f}")
    print(f"\n{'='*80}\n")
    
    # Save results
    print("Saving results...")
    
    # Combine
    equity_combined = pd.concat([equity_long, equity_short], ignore_index=True)
    trades_combined = pd.concat([trades_long, trades_short], ignore_index=True)
    
    # Save to parquet
    equity_combined.to_parquet(f'/home/ubuntu/stage4_strategy/{args.symbol}_equity_curves_vectorbt.parquet')
    trades_combined.to_parquet(f'/home/ubuntu/stage4_strategy/{args.symbol}_trades_vectorbt.parquet')
    
    print(f"✅ Saved: {args.symbol}_equity_curves_vectorbt.parquet")
    print(f"✅ Saved: {args.symbol}_trades_vectorbt.parquet")
    
    # Save to MotherDuck
    conn = duckdb.connect(f'md:?motherduck_token={TOKEN}')
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_equity_curves_vectorbt AS 
        SELECT * FROM equity_combined
    """)
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_trades_vectorbt AS 
        SELECT * FROM trades_combined
    """)
    
    # Save metrics
    metrics_df = pd.DataFrame([metrics_long, metrics_short])
    metrics_df['Symbol'] = args.symbol
    metrics_df['Strategy'] = 'Baseline_ATR_VectorBT'
    metrics_df['ATR_Period'] = args.atr_period
    metrics_df['ATR_Mult'] = args.atr_mult
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_metrics_vectorbt AS 
        SELECT * FROM metrics_df
    """)
    
    conn.close()
    
    print(f"✅ Saved to MotherDuck: stage4_equity_curves_vectorbt, stage4_trades_vectorbt, stage4_metrics_vectorbt")
    print(f"\n{'='*80}")
    print("BACKTEST COMPLETE!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
