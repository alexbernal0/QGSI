"""
Symbol Data Repository for Transaction Cost Estimation
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026

This module provides a repository for storing and retrieving symbol-specific
trading cost parameters such as spreads, volatility, and average daily volume.
"""

import pandas as pd
from typing import Dict, Optional


class SymbolDataRepository:
    """
    Repository for symbol-specific trading cost parameters.
    """
    
    def __init__(self):
        self.data = {}
    
    def add_symbol(
        self,
        symbol: str,
        avg_daily_dollar_volume: float,
        avg_relative_spread: float,
        daily_volatility: float,
        impact_coefficient: float = 0.7,
        liquidity_tier: str = 'unknown'
    ):
        """
        Add symbol-specific parameters.
        
        Parameters:
        -----------
        symbol : str
            Ticker symbol
        avg_daily_dollar_volume : float
            Average daily dollar volume (e.g., 500_000_000 for $500M)
        avg_relative_spread : float
            Average relative spread (e.g., 0.0002 for 2 bps)
        daily_volatility : float
            Daily price volatility (e.g., 0.015 for 1.5%)
        impact_coefficient : float
            Calibrated market impact coefficient (default: 0.7)
        liquidity_tier : str
            'mega_cap', 'large_cap', 'mid_cap', etc.
        """
        self.data[symbol] = {
            'avg_daily_dollar_volume': avg_daily_dollar_volume,
            'avg_relative_spread': avg_relative_spread,
            'daily_volatility': daily_volatility,
            'impact_coefficient': impact_coefficient,
            'liquidity_tier': liquidity_tier
        }
    
    def get_symbol_data(self, symbol: str) -> Dict:
        """Retrieve symbol data, with defaults if not found."""
        if symbol in self.data:
            return self.data[symbol]
        else:
            # Return conservative defaults for unknown symbols
            return {
                'avg_daily_dollar_volume': 100_000_000,  # $100M
                'avg_relative_spread': 0.0005,  # 5 bps
                'daily_volatility': 0.020,  # 2%
                'impact_coefficient': 0.7,
                'liquidity_tier': 'unknown'
            }
    
    def load_from_dataframe(self, df: pd.DataFrame):
        """
        Load symbol data from a pandas DataFrame.
        
        Expected columns:
        - symbol
        - avg_daily_dollar_volume
        - avg_relative_spread
        - daily_volatility
        - impact_coefficient (optional)
        - liquidity_tier (optional)
        """
        for _, row in df.iterrows():
            self.add_symbol(
                symbol=row['symbol'],
                avg_daily_dollar_volume=row['avg_daily_dollar_volume'],
                avg_relative_spread=row['avg_relative_spread'],
                daily_volatility=row['daily_volatility'],
                impact_coefficient=row.get('impact_coefficient', 0.7),
                liquidity_tier=row.get('liquidity_tier', 'unknown')
            )
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Export repository data to a pandas DataFrame.
        
        Returns:
        --------
        pd.DataFrame : DataFrame with all symbol data
        """
        records = []
        for symbol, data in self.data.items():
            record = {'symbol': symbol}
            record.update(data)
            records.append(record)
        
        return pd.DataFrame(records)
    
    def get_all_symbols(self) -> list:
        """Return list of all symbols in the repository."""
        return list(self.data.keys())
    
    def remove_symbol(self, symbol: str):
        """Remove a symbol from the repository."""
        if symbol in self.data:
            del self.data[symbol]
    
    def update_symbol(self, symbol: str, **kwargs):
        """
        Update specific parameters for a symbol.
        
        Parameters:
        -----------
        symbol : str
            Ticker symbol
        **kwargs : dict
            Parameters to update (e.g., avg_daily_dollar_volume=500000000)
        """
        if symbol not in self.data:
            raise ValueError(f"Symbol {symbol} not found in repository")
        
        for key, value in kwargs.items():
            if key in self.data[symbol]:
                self.data[symbol][key] = value
            else:
                raise ValueError(f"Invalid parameter: {key}")
