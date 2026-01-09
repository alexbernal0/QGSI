"""
QGSI Stage 4: Baseline ATR Strategy - AAPL Test Case

Author: Alex Bernal, Senior Quantitative Researcher
Date: January 09, 2026
Version: 1.0

DESCRIPTION:
    Baseline trading strategy using fixed ATR-based stops and targets.
    This serves as the benchmark for comparing more sophisticated strategies.
    
STRATEGY LOGIC:
    Entry:
        - Long: Enter on close price when Signal = 1
        - Short: Enter on close price when Signal = -1
        - Only one position at a time (no overlapping)
    
    Position Sizing:
        - Fixed $100,000 per trade (100% of starting capital)
        - No leverage, no fractional shares
    
    Stop Loss & Profit Target:
        - ATR Period: 30 bars (default)
        - ATR Multiplier: 3.0 (default)
        - Stop Loss: Entry - (ATR_Mult × ATR) for Long, Entry + (ATR_Mult × ATR) for Short
        - Profit Target: Entry + (ATR_Mult × ATR) for Long, Entry - (ATR_Mult × ATR) for Short
        - Equal risk/reward ratio (1:1)
    
    Exit:
        - Exit at close price when:
            1. Profit target hit (high >= target for Long, low <= target for Short)
            2. Stop loss hit (low <= stop for Long, high >= stop for Short)
            3. 20 bars elapsed since entry (time-based exit)
        - Whichever comes first
    
    Separate Backtests:
        - Long signals only (Signal = 1)
        - Short signals only (Signal = -1)
        - Starting capital: $100,000 each
        - No slippage, no commissions

DATA SOURCE:
    - MotherDuck: QGSI.QGSI_AllSymbols_3Signals table
    - Symbol: AAPL
    - 1-minute OHLC bars with signal column

OUTPUT:
    - Equity curves (bar-by-bar portfolio value)
    - Trade log (entry/exit prices, P&L, duration)
    - Performance metrics (Win Rate, Profit Factor, Max DD, Sharpe)
    - Saved to parquet and MotherDuck

USAGE:
    python3.11 stage4_baseline_atr_strategy.py --symbol AAPL --atr_period 30 --atr_mult 3.0
"""

import pandas as pd
import numpy as np
import duckdb
from datetime import datetime
import argparse

# MotherDuck token
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs'


def calculate_atr(df, period=30):
    """
    Calculate Average True Range (ATR) for volatility measurement.
    
    Args:
        df: DataFrame with OHLC data
        period: ATR period (default 30)
    
    Returns:
        Series with ATR values
    """
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def backtest_strategy(df, signal_type='long', atr_period=30, atr_mult=3.0, 
                     starting_capital=100000, max_bars=20):
    """
    Backtest the baseline ATR strategy.
    
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
    """
    
    # Calculate ATR
    df['ATR'] = calculate_atr(df, period=atr_period)
    
    # Filter signals
    if signal_type == 'long':
        signal_value = 1
    else:
        signal_value = -1
    
    # Initialize tracking variables
    equity = starting_capital
    equity_curve = []
    trades = []
    
    in_position = False
    entry_price = 0
    entry_bar = 0
    stop_loss = 0
    profit_target = 0
    position_size = 0
    
    # Iterate through bars
    for i in range(len(df)):
        row = df.iloc[i]
        
        # Record equity at each bar
        equity_curve.append({
            'BarIndex': i,
            'Datetime': row['Datetime'],
            'Equity': equity,
            'InPosition': in_position
        })
        
        # Check for exit if in position
        if in_position:
            bars_held = i - entry_bar
            exit_triggered = False
            exit_reason = ''
            exit_price = row['Close']
            
            # Check profit target
            if signal_type == 'long' and row['High'] >= profit_target:
                exit_triggered = True
                exit_reason = 'Profit Target'
                exit_price = profit_target
            elif signal_type == 'short' and row['Low'] <= profit_target:
                exit_triggered = True
                exit_reason = 'Profit Target'
                exit_price = profit_target
            
            # Check stop loss
            elif signal_type == 'long' and row['Low'] <= stop_loss:
                exit_triggered = True
                exit_reason = 'Stop Loss'
                exit_price = stop_loss
            elif signal_type == 'short' and row['High'] >= stop_loss:
                exit_triggered = True
                exit_reason = 'Stop Loss'
                exit_price = stop_loss
            
            # Check time-based exit
            elif bars_held >= max_bars:
                exit_triggered = True
                exit_reason = 'Time Exit (20 bars)'
                exit_price = row['Close']
            
            # Execute exit
            if exit_triggered:
                if signal_type == 'long':
                    pnl = (exit_price - entry_price) * position_size
                else:  # short
                    pnl = (entry_price - exit_price) * position_size
                
                equity += pnl
                
                trades.append({
                    'EntryBar': entry_bar,
                    'EntryDatetime': df.iloc[entry_bar]['Datetime'],
                    'EntryPrice': entry_price,
                    'ExitBar': i,
                    'ExitDatetime': row['Datetime'],
                    'ExitPrice': exit_price,
                    'ExitReason': exit_reason,
                    'BarsHeld': bars_held,
                    'PositionSize': position_size,
                    'PnL': pnl,
                    'PnL_Pct': (pnl / starting_capital) * 100,
                    'StopLoss': stop_loss,
                    'ProfitTarget': profit_target,
                    'SignalType': signal_type
                })
                
                in_position = False
        
        # Check for entry if not in position
        if not in_position and row['Signal'] == signal_value:
            # Ensure ATR is available
            if pd.isna(row['ATR']):
                continue
            
            entry_price = row['Close']
            entry_bar = i
            
            # Calculate stop and target
            if signal_type == 'long':
                stop_loss = entry_price - (atr_mult * row['ATR'])
                profit_target = entry_price + (atr_mult * row['ATR'])
            else:  # short
                stop_loss = entry_price + (atr_mult * row['ATR'])
                profit_target = entry_price - (atr_mult * row['ATR'])
            
            # Calculate position size (number of shares)
            position_size = int(starting_capital / entry_price)
            
            in_position = True
    
    # Convert to DataFrames
    equity_df = pd.DataFrame(equity_curve)
    trades_df = pd.DataFrame(trades)
    
    # Calculate performance metrics
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
        
        # Calculate max drawdown
        equity_df['Peak'] = equity_df['Equity'].cummax()
        equity_df['Drawdown'] = equity_df['Equity'] - equity_df['Peak']
        equity_df['Drawdown_Pct'] = (equity_df['Drawdown'] / equity_df['Peak']) * 100
        max_drawdown = equity_df['Drawdown'].min()
        max_drawdown_pct = equity_df['Drawdown_Pct'].min()
        
        # Calculate Sharpe Ratio (assuming 252 trading days, 390 minutes per day)
        returns = equity_df['Equity'].pct_change().dropna()
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
            'FinalEquity': equity_df['Equity'].iloc[-1],
            'StartingCapital': starting_capital
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
            'StartingCapital': starting_capital
        }
    
    return equity_df, trades_df, metrics


def main():
    parser = argparse.ArgumentParser(description='QGSI Stage 4 Baseline ATR Strategy')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Symbol to backtest')
    parser.add_argument('--atr_period', type=int, default=30, help='ATR period')
    parser.add_argument('--atr_mult', type=float, default=3.0, help='ATR multiplier')
    parser.add_argument('--starting_capital', type=float, default=100000, help='Starting capital')
    parser.add_argument('--max_bars', type=int, default=20, help='Max bars to hold position')
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"QGSI Stage 4: Baseline ATR Strategy - {args.symbol}")
    print(f"{'='*80}\n")
    
    # Load data from MotherDuck
    print(f"Loading {args.symbol} data from MotherDuck...")
    conn = duckdb.connect(f'md:?motherduck_token={TOKEN}')
    
    query = f"""
        SELECT BarDateTime as Datetime, Open, High, Low, Close, Signal, SignalCount
        FROM QGSI.signal_data
        WHERE Symbol = '{args.symbol}'
        ORDER BY BarDateTime
    """
    
    df = conn.execute(query).df()
    conn.close()
    
    print(f"Loaded {len(df):,} bars")
    print(f"Signals: {len(df[df['Signal'] == 1])} Long, {len(df[df['Signal'] == -1])} Short\n")
    
    # Backtest Long signals
    print("Backtesting LONG signals...")
    equity_long, trades_long, metrics_long = backtest_strategy(
        df.copy(), 
        signal_type='long',
        atr_period=args.atr_period,
        atr_mult=args.atr_mult,
        starting_capital=args.starting_capital,
        max_bars=args.max_bars
    )
    
    # Backtest Short signals
    print("Backtesting SHORT signals...")
    equity_short, trades_short, metrics_short = backtest_strategy(
        df.copy(),
        signal_type='short',
        atr_period=args.atr_period,
        atr_mult=args.atr_mult,
        starting_capital=args.starting_capital,
        max_bars=args.max_bars
    )
    
    # Print results
    print(f"\n{'='*80}")
    print(f"BACKTEST RESULTS - {args.symbol}")
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
    print(f"\n{'='*80}\n")
    
    # Save results
    print("Saving results...")
    
    # Add symbol and strategy info to dataframes
    equity_long['Symbol'] = args.symbol
    equity_long['Strategy'] = 'Baseline_ATR'
    equity_long['SignalType'] = 'LONG'
    equity_long['ATR_Period'] = args.atr_period
    equity_long['ATR_Mult'] = args.atr_mult
    
    equity_short['Symbol'] = args.symbol
    equity_short['Strategy'] = 'Baseline_ATR'
    equity_short['SignalType'] = 'SHORT'
    equity_short['ATR_Period'] = args.atr_period
    equity_short['ATR_Mult'] = args.atr_mult
    
    trades_long['Symbol'] = args.symbol
    trades_long['Strategy'] = 'Baseline_ATR'
    trades_long['ATR_Period'] = args.atr_period
    trades_long['ATR_Mult'] = args.atr_mult
    
    trades_short['Symbol'] = args.symbol
    trades_short['Strategy'] = 'Baseline_ATR'
    trades_short['ATR_Period'] = args.atr_period
    trades_short['ATR_Mult'] = args.atr_mult
    
    # Combine equity curves
    equity_combined = pd.concat([equity_long, equity_short], ignore_index=True)
    
    # Combine trades
    trades_combined = pd.concat([trades_long, trades_short], ignore_index=True)
    
    # Save to parquet
    equity_combined.to_parquet(f'/home/ubuntu/stage4_strategy/{args.symbol}_equity_curves.parquet')
    trades_combined.to_parquet(f'/home/ubuntu/stage4_strategy/{args.symbol}_trades.parquet')
    
    print(f"✅ Saved equity curves: {args.symbol}_equity_curves.parquet")
    print(f"✅ Saved trades: {args.symbol}_trades.parquet")
    
    # Save to MotherDuck
    conn = duckdb.connect(f'md:?motherduck_token={TOKEN}')
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_equity_curves AS 
        SELECT * FROM equity_combined
    """)
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_trades AS 
        SELECT * FROM trades_combined
    """)
    
    # Save metrics
    metrics_df = pd.DataFrame([metrics_long, metrics_short])
    metrics_df['Symbol'] = args.symbol
    metrics_df['Strategy'] = 'Baseline_ATR'
    metrics_df['ATR_Period'] = args.atr_period
    metrics_df['ATR_Mult'] = args.atr_mult
    
    conn.execute(f"""
        CREATE OR REPLACE TABLE QGSI.stage4_metrics AS 
        SELECT * FROM metrics_df
    """)
    
    conn.close()
    
    print(f"✅ Saved to MotherDuck: stage4_equity_curves, stage4_trades, stage4_metrics")
    print(f"\n{'='*80}")
    print("BACKTEST COMPLETE!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
