"""
Transaction Cost Estimator for S&P 500 Trading Strategies
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026

This module provides a comprehensive transaction cost estimation framework
optimized for Interactive Brokers Pro Tiered pricing and S&P 500 stocks.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Literal


class TransactionCostEstimator:
    """
    Comprehensive transaction cost estimator for equity trading.
    
    Supports:
    - Interactive Brokers Pro Tiered commission structure
    - Symbol-specific spread and market impact modeling
    - Dynamic cost calculation based on liquidity metrics
    """
    
    def __init__(self, broker: str = 'ibkr_tiered'):
        """
        Initialize the cost estimator.
        
        Parameters:
        -----------
        broker : str
            Broker commission structure. Options: 'ibkr_tiered', 'ibkr_fixed'
        """
        self.broker = broker
        self.monthly_volume = 0  # Track cumulative monthly volume for tiering
        
        # IBKR Pro Tiered commission schedule
        self.ibkr_tiered_schedule = [
            (300000, 0.0035),
            (3000000, 0.0020),
            (20000000, 0.0015),
            (100000000, 0.0010),
            (float('inf'), 0.0005)
        ]
        
        # Third-party fee rates
        self.exchange_fee_remove = 0.0028  # Removing liquidity (conservative)
        self.exchange_fee_add = -0.0020    # Adding liquidity (rebate)
        self.clearing_fee = 0.00020
        self.finra_taf = 0.000195  # Sells only
        self.sec_fee_rate = 0.0  # Currently negligible, update as needed
        
        # Pass-through rates
        self.nyse_passthrough_rate = 0.000175
        self.finra_passthrough_rate = 0.000565
    
    def calculate_tiered_commission(self, shares: int) -> float:
        """
        Calculate IBKR Pro Tiered commission on a marginal basis.
        
        Parameters:
        -----------
        shares : int
            Number of shares to trade
            
        Returns:
        --------
        float : Commission in dollars
        """
        commission = 0.0
        remaining_shares = shares
        current_volume = self.monthly_volume
        
        for tier_limit, rate in self.ibkr_tiered_schedule:
            if current_volume >= tier_limit:
                continue
            
            # Calculate shares in this tier
            shares_in_tier = min(remaining_shares, tier_limit - current_volume)
            commission += shares_in_tier * rate
            
            remaining_shares -= shares_in_tier
            current_volume += shares_in_tier
            
            if remaining_shares <= 0:
                break
        
        return commission
    
    def get_brokerage_cost(
        self, 
        shares: int, 
        price: float, 
        direction: Literal['buy', 'sell'],
        removes_liquidity: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total brokerage cost including all fees.
        
        Parameters:
        -----------
        shares : int
            Number of shares
        price : float
            Execution price per share
        direction : str
            'buy' or 'sell'
        removes_liquidity : bool
            True if order removes liquidity (market order), False if adds
            
        Returns:
        --------
        dict : Breakdown of all cost components
        """
        trade_value = shares * price
        
        # 1. Base commission
        if self.broker == 'ibkr_tiered':
            commission = self.calculate_tiered_commission(shares)
        elif self.broker == 'ibkr_fixed':
            commission = shares * 0.005
        else:
            raise ValueError(f"Unknown broker: {self.broker}")
        
        # Apply min/max constraints
        commission = max(commission, 0.35)  # IBKR minimum
        commission = min(commission, trade_value * 0.01)  # IBKR maximum (1%)
        
        # 2. Exchange fees
        if removes_liquidity:
            exchange_fee = shares * self.exchange_fee_remove
        else:
            exchange_fee = shares * self.exchange_fee_add  # Negative (rebate)
        
        # 3. Clearing fees
        clearing_fee = shares * self.clearing_fee
        
        # 4. Regulatory fees (sells only)
        if direction == 'sell':
            sec_fee = trade_value * self.sec_fee_rate
            finra_taf = shares * self.finra_taf
        else:
            sec_fee = 0.0
            finra_taf = 0.0
        
        # 5. Pass-through fees
        nyse_passthrough = commission * self.nyse_passthrough_rate
        finra_passthrough = commission * self.finra_passthrough_rate
        
        # Total
        total_brokerage = (
            commission + 
            exchange_fee + 
            clearing_fee + 
            sec_fee + 
            finra_taf + 
            nyse_passthrough + 
            finra_passthrough
        )
        
        return {
            'commission': commission,
            'exchange_fee': exchange_fee,
            'clearing_fee': clearing_fee,
            'sec_fee': sec_fee,
            'finra_taf': finra_taf,
            'nyse_passthrough': nyse_passthrough,
            'finra_passthrough': finra_passthrough,
            'total_brokerage': total_brokerage,
            'total_brokerage_bps': (total_brokerage / trade_value) * 10000
        }
    
    def get_spread_cost(
        self, 
        shares: int, 
        price: float, 
        symbol_data: Dict
    ) -> Dict[str, float]:
        """
        Calculate bid-ask spread cost.
        
        Parameters:
        -----------
        shares : int
            Number of shares
        price : float
            Mid-price
        symbol_data : dict
            Must contain 'avg_relative_spread' (e.g., 0.0002 for 2 bps)
            
        Returns:
        --------
        dict : Spread cost breakdown
        """
        trade_value = shares * price
        relative_spread = symbol_data.get('avg_relative_spread', 0.0002)
        
        # Cost is half the spread (one-way crossing)
        spread_cost = 0.5 * relative_spread * trade_value
        
        return {
            'spread_cost': spread_cost,
            'spread_cost_bps': (spread_cost / trade_value) * 10000,
            'relative_spread': relative_spread
        }
    
    def get_market_impact(
        self, 
        shares: int, 
        price: float, 
        symbol_data: Dict,
        model: str = 'square_root'
    ) -> Dict[str, float]:
        """
        Calculate market impact cost using various models.
        
        Parameters:
        -----------
        shares : int
            Number of shares
        price : float
            Current price
        symbol_data : dict
            Must contain:
            - 'avg_daily_dollar_volume': Average daily dollar volume
            - 'daily_volatility': Daily price volatility (e.g., 0.015 for 1.5%)
            - 'impact_coefficient': Calibrated coefficient (default: 0.7)
        model : str
            'square_root' (recommended), 'linear', or 'power_law'
            
        Returns:
        --------
        dict : Market impact breakdown
        """
        trade_value = shares * price
        adv = symbol_data.get('avg_daily_dollar_volume', 1e9)
        volatility = symbol_data.get('daily_volatility', 0.015)
        impact_coeff = symbol_data.get('impact_coefficient', 0.7)
        
        participation_rate = trade_value / adv
        
        if model == 'square_root':
            # Industry-standard square-root model
            impact_pct = (participation_rate ** 0.5) * volatility * impact_coeff
        elif model == 'linear':
            # Simple linear model (conservative for large trades)
            impact_pct = participation_rate * volatility * impact_coeff
        elif model == 'power_law':
            # Power-law model (exponent typically 0.6-0.7)
            impact_pct = (participation_rate ** 0.6) * volatility * impact_coeff
        else:
            raise ValueError(f"Unknown model: {model}")
        
        impact_cost = impact_pct * trade_value
        
        return {
            'impact_cost': impact_cost,
            'impact_cost_bps': (impact_cost / trade_value) * 10000,
            'participation_rate': participation_rate,
            'impact_pct': impact_pct,
            'model': model
        }
    
    def calculate_total_cost(
        self,
        shares: int,
        price: float,
        direction: Literal['buy', 'sell'],
        symbol_data: Dict,
        removes_liquidity: bool = True,
        impact_model: str = 'square_root'
    ) -> Dict[str, float]:
        """
        Calculate total transaction cost for a trade.
        
        Parameters:
        -----------
        shares : int
            Number of shares
        price : float
            Execution price
        direction : str
            'buy' or 'sell'
        symbol_data : dict
            Symbol-specific parameters (spread, ADV, volatility)
        removes_liquidity : bool
            Whether order removes liquidity
        impact_model : str
            Market impact model to use
            
        Returns:
        --------
        dict : Complete cost breakdown
        """
        trade_value = shares * price
        
        # Calculate each component
        brokerage = self.get_brokerage_cost(shares, price, direction, removes_liquidity)
        spread = self.get_spread_cost(shares, price, symbol_data)
        impact = self.get_market_impact(shares, price, symbol_data, impact_model)
        
        # Total cost
        total_cost = (
            brokerage['total_brokerage'] + 
            spread['spread_cost'] + 
            impact['impact_cost']
        )
        
        total_cost_bps = (total_cost / trade_value) * 10000
        
        # Update monthly volume tracker
        self.monthly_volume += shares
        
        return {
            'trade_value': trade_value,
            'shares': shares,
            'price': price,
            'direction': direction,
            
            # Brokerage breakdown
            'commission': brokerage['commission'],
            'exchange_fee': brokerage['exchange_fee'],
            'clearing_fee': brokerage['clearing_fee'],
            'regulatory_fees': brokerage['sec_fee'] + brokerage['finra_taf'],
            'total_brokerage': brokerage['total_brokerage'],
            'total_brokerage_bps': brokerage['total_brokerage_bps'],
            
            # Implicit costs
            'spread_cost': spread['spread_cost'],
            'spread_cost_bps': spread['spread_cost_bps'],
            'impact_cost': impact['impact_cost'],
            'impact_cost_bps': impact['impact_cost_bps'],
            
            # Total
            'total_cost': total_cost,
            'total_cost_bps': total_cost_bps,
            
            # Metadata
            'participation_rate': impact['participation_rate'],
            'monthly_volume': self.monthly_volume
        }
    
    def reset_monthly_volume(self):
        """Reset monthly volume tracker (call at start of each month)."""
        self.monthly_volume = 0
