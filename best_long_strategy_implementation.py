"""
BEST LONG STRATEGY IMPLEMENTATION
Strategy: Fixed ATR Asymmetric
Best Parameters: ATR(50), Stop 1.5×, Target 6.0×
Performance: +$837,370 across 80,129 LONG signals (2007-2024)
Profit Factor: 1.112, Win Rate: 29.0%
"""

import pandas as pd
import numpy as np

def calculate_atr(df, period=50):
    """
    Calculate Average True Range using Wilder's method.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with High, Low, Close columns
    period : int
        ATR period (default: 50)
    
    Returns:
    --------
    pd.Series
        ATR values
    """
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def backtest_long_asymmetric(df, symbol, atr_period=50, stop_mult=1.5, target_mult=6.0, 
                             max_bars=30, position_size=100000.0):
    """
    Backtest Fixed ATR Asymmetric strategy on LONG signals.
    
    Strategy Logic:
    ---------------
    1. Entry: Buy at signal bar CLOSE price
    2. Stop Loss: Entry - (ATR × stop_mult) = tight stop BELOW entry
    3. Profit Target: Entry + (ATR × target_mult) = wide target ABOVE entry
    4. Exit: When LOW ≤ Stop OR HIGH ≥ Target OR time limit reached
    5. Position Size: Fixed dollar amount / entry price
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with columns: Date, Open, High, Low, Close, Signal
        Signal = 1 for LONG entries
    symbol : str
        Stock symbol for tracking
    atr_period : int
        ATR calculation period (default: 50)
    stop_mult : float
        Stop loss multiplier (default: 1.5)
    target_mult : float
        Profit target multiplier (default: 6.0)
    max_bars : int
        Maximum bars to hold position (default: 30)
    position_size : float
        Fixed dollar amount per trade (default: $100,000)
    
    Returns:
    --------
    pd.DataFrame
        Trade log with all trade details
    """
    trades = []
    
    # Get LONG signal indices
    signal_indices = df[df['Signal'] == 1].index.tolist()
    
    # Calculate ATR
    df['ATR'] = calculate_atr(df, period=atr_period)
    
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        entry_price = df.loc[signal_idx, 'Close']
        entry_atr = df.loc[signal_idx, 'ATR']
        entry_date = df.loc[signal_idx, 'Date'] if 'Date' in df.columns else signal_idx
        
        # Skip if ATR is invalid
        if pd.isna(entry_atr) or entry_atr == 0:
            continue
        
        # Calculate position size
        shares = position_size / entry_price
        
        # LONG: Stop BELOW entry, Target ABOVE entry
        stop_loss = entry_price - (stop_mult * entry_atr)
        profit_target = entry_price + (target_mult * entry_atr)
        
        # Initialize exit variables
        exit_price = None
        exit_reason = None
        exit_date = None
        bars_in_trade = 0
        
        # Check exits on each subsequent bar
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + max_bars + 1, len(df))):
            current_idx = df.index[i]
            bars_in_trade = i - entry_bar_idx
            
            # Check stop loss (LOW touches stop)
            if df.loc[current_idx, 'Low'] <= stop_loss:
                exit_price = stop_loss
                exit_reason = 'STOP'
                exit_date = df.loc[current_idx, 'Date'] if 'Date' in df.columns else current_idx
                break
            
            # Check profit target (HIGH touches target)
            if df.loc[current_idx, 'High'] >= profit_target:
                exit_price = profit_target
                exit_reason = 'TARGET'
                exit_date = df.loc[current_idx, 'Date'] if 'Date' in df.columns else current_idx
                break
            
            # Time limit reached
            if bars_in_trade >= max_bars:
                exit_price = df.loc[current_idx, 'Close']
                exit_reason = 'TIME'
                exit_date = df.loc[current_idx, 'Date'] if 'Date' in df.columns else current_idx
                break
        else:
            # No exit found within time limit (end of data)
            last_idx = min(entry_bar_idx + max_bars, len(df) - 1)
            exit_price = df.iloc[last_idx]['Close']
            exit_reason = 'TIME'
            exit_date = df.iloc[last_idx]['Date'] if 'Date' in df.columns else df.index[last_idx]
            bars_in_trade = last_idx - entry_bar_idx
        
        # Calculate P&L
        net_profit = (exit_price - entry_price) * shares
        pct_profit = ((exit_price - entry_price) / entry_price) * 100
        
        # Record trade
        trades.append({
            'Symbol': symbol,
            'EntryDate': entry_date,
            'ExitDate': exit_date,
            'EntryPrice': entry_price,
            'ExitPrice': exit_price,
            'StopLoss': stop_loss,
            'ProfitTarget': profit_target,
            'ATR': entry_atr,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'Shares': shares,
            'NetProfit': net_profit,
            'PctProfit': pct_profit,
            'PositionSize': position_size
        })
    
    return pd.DataFrame(trades)


def analyze_results(trades_df):
    """
    Analyze backtest results and print summary statistics.
    
    Parameters:
    -----------
    trades_df : pd.DataFrame
        Trade log from backtest_long_asymmetric()
    """
    if len(trades_df) == 0:
        print("No trades found.")
        return
    
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['NetProfit'] > 0])
    losing_trades = len(trades_df[trades_df['NetProfit'] < 0])
    
    total_profit = trades_df['NetProfit'].sum()
    gross_profit = trades_df[trades_df['NetProfit'] > 0]['NetProfit'].sum()
    gross_loss = abs(trades_df[trades_df['NetProfit'] < 0]['NetProfit'].sum())
    
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
    win_rate = (winning_trades / total_trades) * 100
    
    avg_win = trades_df[trades_df['NetProfit'] > 0]['NetProfit'].mean() if winning_trades > 0 else 0
    avg_loss = abs(trades_df[trades_df['NetProfit'] < 0]['NetProfit'].mean()) if losing_trades > 0 else 0
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else np.inf
    
    print("=" * 60)
    print("BACKTEST RESULTS - LONG ASYMMETRIC STRATEGY")
    print("=" * 60)
    print(f"Total Trades:        {total_trades:,}")
    print(f"Winning Trades:      {winning_trades:,} ({win_rate:.1f}%)")
    print(f"Losing Trades:       {losing_trades:,} ({100-win_rate:.1f}%)")
    print(f"\nNet Profit:          ${total_profit:,.2f}")
    print(f"Gross Profit:        ${gross_profit:,.2f}")
    print(f"Gross Loss:          ${gross_loss:,.2f}")
    print(f"Profit Factor:       {profit_factor:.3f}")
    print(f"\nAverage Win:         ${avg_win:,.2f}")
    print(f"Average Loss:        ${avg_loss:,.2f}")
    print(f"Win/Loss Ratio:      {win_loss_ratio:.2f}:1")
    print(f"\nAvg Bars in Trade:   {trades_df['BarsInTrade'].mean():.1f}")
    print("=" * 60)
    
    # Exit reason breakdown
    print("\nExit Reason Breakdown:")
    exit_counts = trades_df['ExitReason'].value_counts()
    for reason, count in exit_counts.items():
        pct = (count / total_trades) * 100
        print(f"  {reason:10s}: {count:,} ({pct:.1f}%)")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    """
    Example usage of the LONG Asymmetric strategy.
    
    Required data format:
    - DataFrame with columns: Date, Open, High, Low, Close, Signal
    - Signal = 1 for LONG entry signals
    - Data should be sorted by Date
    """
    
    # Example: Load your data
    # df = pd.read_parquet('QGSI_AllSymbols_3Signals.parquet')
    # df = df[df['Symbol'] == 'AAPL'].sort_values('Date').reset_index(drop=True)
    
    # Example: Create sample data for demonstration
    print("Creating sample data for demonstration...")
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=1000, freq='D')
    sample_df = pd.DataFrame({
        'Date': dates,
        'Open': 100 + np.random.randn(1000).cumsum(),
        'High': 100 + np.random.randn(1000).cumsum() + 2,
        'Low': 100 + np.random.randn(1000).cumsum() - 2,
        'Close': 100 + np.random.randn(1000).cumsum(),
        'Signal': 0
    })
    
    # Add some random LONG signals
    signal_indices = np.random.choice(range(100, 900), size=50, replace=False)
    sample_df.loc[signal_indices, 'Signal'] = 1
    
    # Run backtest
    print("\nRunning backtest on sample data...")
    results = backtest_long_asymmetric(
        df=sample_df,
        symbol='SAMPLE',
        atr_period=50,
        stop_mult=1.5,
        target_mult=6.0,
        max_bars=30,
        position_size=100000.0
    )
    
    # Analyze results
    analyze_results(results)
    
    # Save results
    # results.to_csv('long_asymmetric_trades.csv', index=False)
    # print("\n✓ Trade log saved to: long_asymmetric_trades.csv")
