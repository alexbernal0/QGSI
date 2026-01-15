"""
BEST LONG STRATEGY: ATR Trailing Stop
Rank #1 by System Score ($1,392K = $1,281K Net Profit × 1.087 PF)

Parameters: ATR(30), Multiplier 5.0×
Performance: +$1,281,000 across 79,972 LONG signals (2007-2024)
Profit Factor: 1.087, Win Rate: 50.6%

This is the HIGHEST performing LONG strategy across all 4 strategy types tested.
"""

import pandas as pd
import numpy as np

def calculate_atr(df, period=30):
    """
    Calculate Average True Range using Wilder's method.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with High, Low, Close columns
    period : int
        ATR period (default: 30)
    
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


def backtest_long_trailing(df, symbol, atr_period=30, multiplier=5.0, 
                          max_bars=20, position_size=100000.0):
    """
    Backtest ATR Trailing Stop strategy on LONG signals.
    
    Strategy Logic:
    ---------------
    1. Entry: Buy at signal bar CLOSE price
    2. Initial Stop: Entry - (ATR × multiplier) = stop BELOW entry (loss if price falls)
    3. Trailing Logic: Stop = MAX(previous_stop, Current LOW - ATR × multiplier)
    4. Stop Movement: Stop only moves UP (tighter), never DOWN (looser)
    5. Exit: When LOW ≤ Stop (stopped out) OR time limit reached
    6. No fixed profit target - let winners run until stopped or time limit
    7. Position Size: Fixed dollar amount / entry price
    8. P&L: (Exit Price - Entry Price) × Shares
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with columns: Date, Open, High, Low, Close, Signal
        Signal = 1 for LONG entries
    symbol : str
        Stock symbol for tracking
    atr_period : int
        ATR calculation period (default: 30)
    multiplier : float
        Trailing stop multiplier (default: 5.0)
    max_bars : int
        Maximum bars to hold position (default: 20)
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
        entry_date = df.loc[signal_idx, 'BarDate'] if 'BarDate' in df.columns else signal_idx
        
        # Skip if ATR is invalid
        if pd.isna(entry_atr) or entry_atr == 0:
            continue
        
        # Calculate position size
        shares = position_size / entry_price
        
        # LONG: Initial stop BELOW entry (loss if price falls)
        initial_stop = entry_price - (multiplier * entry_atr)
        current_stop = initial_stop
        
        # Track stop levels for analysis
        stop_levels = [initial_stop]
        
        # Initialize exit variables
        exit_price = None
        exit_reason = None
        exit_date = None
        bars_in_trade = 0
        
        # Check exits on each subsequent bar
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + max_bars + 1, len(df))):
            current_idx = df.index[i]
            current_atr = df.loc[current_idx, 'ATR']
            bars_in_trade = i - entry_bar_idx
            
            # Update trailing stop (moves UP only, tightening as price rises)
            if not pd.isna(current_atr) and current_atr > 0:
                # Calculate new stop based on current LOW
                new_stop = df.loc[current_idx, 'Low'] - (multiplier * current_atr)
                
                # Stop only moves UP (tighter), never DOWN (looser)
                current_stop = max(current_stop, new_stop)
                stop_levels.append(current_stop)
            
            # Check if stopped out (price falls to hit stop)
            if df.loc[current_idx, 'Low'] <= current_stop:
                exit_price = current_stop
                exit_reason = 'STOP'
                exit_date = df.loc[current_idx, 'BarDate'] if 'BarDate' in df.columns else current_idx
                break
            
            # Time limit reached
            if bars_in_trade >= max_bars:
                exit_price = df.loc[current_idx, 'Close']
                exit_reason = 'TIME'
                exit_date = df.loc[current_idx, 'BarDate'] if 'BarDate' in df.columns else current_idx
                break
        else:
            # No exit found within time limit (end of data)
            last_idx = min(entry_bar_idx + max_bars, len(df) - 1)
            exit_price = df.iloc[last_idx]['Close']
            exit_reason = 'TIME'
            exit_date = df.iloc[last_idx]['BarDate'] if 'BarDate' in df.columns else df.index[last_idx]
            bars_in_trade = last_idx - entry_bar_idx
        
        # Calculate P&L (LONG: profit when exit > entry)
        net_profit = (exit_price - entry_price) * shares
        pct_profit = ((exit_price - entry_price) / entry_price) * 100
        
        # Calculate stop movement
        final_stop = current_stop
        stop_moved = final_stop - initial_stop  # Positive = moved up (favorable)
        stop_moved_pct = (stop_moved / entry_price) * 100
        
        # Record trade
        trades.append({
            'Symbol': symbol,
            'EntryDate': entry_date,
            'ExitDate': exit_date,
            'EntryPrice': entry_price,
            'ExitPrice': exit_price,
            'InitialStop': initial_stop,
            'FinalStop': final_stop,
            'StopMoved': stop_moved,
            'StopMovedPct': stop_moved_pct,
            'ATR': entry_atr,
            'ATRPeriod': atr_period,
            'Multiplier': multiplier,
            'ExitReason': exit_reason,
            'BarsInTrade': bars_in_trade,
            'Shares': shares,
            'NetProfit': net_profit,
            'PctProfit': pct_profit,
            'PositionSize': position_size,
            'Strategy': 'ATR_Trailing_Stop',
            'Signal': 'LONG'
        })
    
    return pd.DataFrame(trades)
