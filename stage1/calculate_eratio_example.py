#!/usr/bin/env python3.11
"""
Example E-Ratio Calculation Script for QGSI Stage 1.0

This script demonstrates how to calculate E-Ratios for a single symbol
from the QGSI dataset.
"""

import duckdb
import pandas as pd
import numpy as np

def calculate_eratio(symbol, con, holding_period=30):
    """
    Calculate E-Ratio for a given symbol and holding period.
    
    Parameters:
    -----------
    symbol : str
        Stock ticker symbol
    con : duckdb.Connection
        MotherDuck database connection
    holding_period : int
        Number of bars to hold position (default: 30)
    
    Returns:
    --------
    dict : E-Ratio results for Long and Short signals
    """
    
    # Query signal data for the symbol
    query = f"""
    SELECT 
        Record,
        BarDateTime,
        Close,
        Signal,
        SignalCount
    FROM QGSI.QGSI_AllSymbols_3Signals
    WHERE Symbol = '{symbol}'
    ORDER BY Record
    """
    
    df = con.execute(query).df()
    print(f"Loaded {len(df):,} bars for {symbol}")
    
    # Calculate returns for each signal
    results = {'Long': [], 'Short': []}
    
    for signal_type, signal_code in [('Long', 1), ('Short', 2)]:
        signal_indices = df[df['Signal'] == signal_code].index
        print(f"\nFound {len(signal_indices)} {signal_type} signals")
        
        for idx in signal_indices:
            # Check if we have enough forward bars
            if idx + holding_period >= len(df):
                continue
            
            entry_price = df.loc[idx, 'Close']
            exit_price = df.loc[idx + holding_period, 'Close']
            
            # Calculate return based on signal type
            if signal_type == 'Long':
                pct_return = (exit_price - entry_price) / entry_price
            else:  # Short
                pct_return = (entry_price - exit_price) / entry_price
            
            results[signal_type].append(pct_return)
    
    # Calculate E-Ratios
    eratio_results = {}
    
    for signal_type in ['Long', 'Short']:
        returns = np.array(results[signal_type])
        
        if len(returns) > 0:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            eratio = mean_return / std_return if std_return > 0 else 0
            
            eratio_results[signal_type] = {
                'n_signals': len(returns),
                'mean_return': mean_return,
                'std_return': std_return,
                'eratio': eratio,
                'win_rate': np.sum(returns > 0) / len(returns) if len(returns) > 0 else 0
            }
        else:
            eratio_results[signal_type] = {
                'n_signals': 0,
                'mean_return': 0,
                'std_return': 0,
                'eratio': 0,
                'win_rate': 0
            }
    
    return eratio_results


def main():
    """Main execution function"""
    
    # Connect to MotherDuck
    MOTHERDUCK_TOKEN = 'YOUR_TOKEN_HERE'
    con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
    
    # Example: Calculate E-Ratio for AAPL
    symbol = 'AAPL'
    holding_period = 30
    
    print(f"Calculating E-Ratio for {symbol} with {holding_period}-bar holding period...")
    results = calculate_eratio(symbol, con, holding_period)
    
    print(f"\n{'='*60}")
    print(f"E-Ratio Results for {symbol}")
    print(f"{'='*60}")
    
    for signal_type in ['Long', 'Short']:
        print(f"\n{signal_type} Signals:")
        print(f"  N Signals:   {results[signal_type]['n_signals']}")
        print(f"  Mean Return: {results[signal_type]['mean_return']:.6f}")
        print(f"  Std Return:  {results[signal_type]['std_return']:.6f}")
        print(f"  E-Ratio:     {results[signal_type]['eratio']:.4f}")
        print(f"  Win Rate:    {results[signal_type]['win_rate']:.2%}")
    
    con.close()


if __name__ == '__main__':
    main()
