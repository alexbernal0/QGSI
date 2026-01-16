"""
Backtest Integration Utilities
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026

This module provides utilities for integrating transaction cost estimation
into backtesting frameworks.
"""

import pandas as pd
from typing import Optional
from .transaction_cost_estimator import TransactionCostEstimator
from .symbol_data_repository import SymbolDataRepository


def apply_transaction_costs_to_backtest(
    trades_df: pd.DataFrame,
    estimator: TransactionCostEstimator,
    symbol_repo: SymbolDataRepository,
    removes_liquidity: bool = True,
    impact_model: str = 'square_root'
) -> pd.DataFrame:
    """
    Apply transaction costs to a backtest trade log.
    
    Parameters:
    -----------
    trades_df : pd.DataFrame
        Trade log with columns: date, symbol, shares, price, direction
    estimator : TransactionCostEstimator
        Cost estimator instance
    symbol_repo : SymbolDataRepository
        Symbol data repository
    removes_liquidity : bool
        Whether orders remove liquidity (default: True)
    impact_model : str
        Market impact model to use (default: 'square_root')
        
    Returns:
    --------
    pd.DataFrame : Trade log with cost columns added
    """
    cost_results = []
    
    for _, trade in trades_df.iterrows():
        symbol_data = symbol_repo.get_symbol_data(trade['symbol'])
        
        cost = estimator.calculate_total_cost(
            shares=abs(trade['shares']),
            price=trade['price'],
            direction='buy' if trade['shares'] > 0 else 'sell',
            symbol_data=symbol_data,
            removes_liquidity=removes_liquidity,
            impact_model=impact_model
        )
        
        cost_results.append(cost)
    
    # Add cost columns to original dataframe
    cost_df = pd.DataFrame(cost_results)
    result_df = pd.concat([trades_df.reset_index(drop=True), cost_df], axis=1)
    
    return result_df


def calculate_strategy_cost_metrics(
    trades_with_costs: pd.DataFrame,
    initial_capital: float = 1_000_000
) -> dict:
    """
    Calculate aggregate cost metrics for a strategy.
    
    Parameters:
    -----------
    trades_with_costs : pd.DataFrame
        Trade log with cost columns (output from apply_transaction_costs_to_backtest)
    initial_capital : float
        Initial capital for the strategy
        
    Returns:
    --------
    dict : Dictionary of cost metrics
    """
    total_cost = trades_with_costs['total_cost'].sum()
    total_trade_value = trades_with_costs['trade_value'].sum()
    num_trades = len(trades_with_costs)
    
    # Calculate turnover
    turnover = total_trade_value / initial_capital
    
    # Average cost per trade
    avg_cost_per_trade = total_cost / num_trades if num_trades > 0 else 0
    avg_cost_bps = trades_with_costs['total_cost_bps'].mean()
    
    # Cost breakdown
    total_brokerage = trades_with_costs['total_brokerage'].sum()
    total_spread = trades_with_costs['spread_cost'].sum()
    total_impact = trades_with_costs['impact_cost'].sum()
    
    # Cost as percentage of capital
    cost_pct_of_capital = (total_cost / initial_capital) * 100
    
    return {
        'total_cost': total_cost,
        'total_trade_value': total_trade_value,
        'num_trades': num_trades,
        'turnover': turnover,
        'avg_cost_per_trade': avg_cost_per_trade,
        'avg_cost_bps': avg_cost_bps,
        'total_brokerage': total_brokerage,
        'total_spread': total_spread,
        'total_impact': total_impact,
        'cost_pct_of_capital': cost_pct_of_capital,
        'brokerage_pct': (total_brokerage / total_cost) * 100 if total_cost > 0 else 0,
        'spread_pct': (total_spread / total_cost) * 100 if total_cost > 0 else 0,
        'impact_pct': (total_impact / total_cost) * 100 if total_cost > 0 else 0
    }


def estimate_annual_cost_drag(
    avg_cost_bps: float,
    annual_turnover: float
) -> float:
    """
    Estimate annual cost drag on returns.
    
    Parameters:
    -----------
    avg_cost_bps : float
        Average cost per trade in basis points
    annual_turnover : float
        Annual turnover as a multiple of capital (e.g., 2.0 for 200%)
        
    Returns:
    --------
    float : Annual cost drag as a percentage
    """
    # Convert bps to percentage
    cost_pct = avg_cost_bps / 10000
    
    # Annual cost = cost per trade × turnover
    annual_cost_pct = cost_pct * annual_turnover * 100
    
    return annual_cost_pct


def generate_cost_report(
    trades_with_costs: pd.DataFrame,
    initial_capital: float = 1_000_000,
    time_period_days: Optional[int] = None
) -> str:
    """
    Generate a formatted cost analysis report.
    
    Parameters:
    -----------
    trades_with_costs : pd.DataFrame
        Trade log with cost columns
    initial_capital : float
        Initial capital for the strategy
    time_period_days : int, optional
        Number of days in the backtest period (for annualization)
        
    Returns:
    --------
    str : Formatted report text
    """
    metrics = calculate_strategy_cost_metrics(trades_with_costs, initial_capital)
    
    report = []
    report.append("=" * 80)
    report.append("TRANSACTION COST ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    report.append(f"Initial Capital: ${initial_capital:,.2f}")
    report.append(f"Number of Trades: {metrics['num_trades']:,}")
    report.append(f"Total Trade Value: ${metrics['total_trade_value']:,.2f}")
    report.append(f"Turnover: {metrics['turnover']:.2f}x")
    report.append("")
    report.append("-" * 80)
    report.append("COST BREAKDOWN")
    report.append("-" * 80)
    report.append(f"Total Transaction Costs: ${metrics['total_cost']:,.2f}")
    report.append(f"  - Brokerage Fees: ${metrics['total_brokerage']:,.2f} ({metrics['brokerage_pct']:.1f}%)")
    report.append(f"  - Spread Costs: ${metrics['total_spread']:,.2f} ({metrics['spread_pct']:.1f}%)")
    report.append(f"  - Market Impact: ${metrics['total_impact']:,.2f} ({metrics['impact_pct']:.1f}%)")
    report.append("")
    report.append(f"Average Cost per Trade: ${metrics['avg_cost_per_trade']:.2f}")
    report.append(f"Average Cost (bps): {metrics['avg_cost_bps']:.2f}")
    report.append(f"Cost as % of Capital: {metrics['cost_pct_of_capital']:.2f}%")
    report.append("")
    
    if time_period_days:
        annualization_factor = 252 / time_period_days
        annual_turnover = metrics['turnover'] * annualization_factor
        annual_cost_drag = estimate_annual_cost_drag(metrics['avg_cost_bps'], annual_turnover)
        
        report.append("-" * 80)
        report.append("ANNUALIZED METRICS")
        report.append("-" * 80)
        report.append(f"Annualized Turnover: {annual_turnover:.2f}x")
        report.append(f"Estimated Annual Cost Drag: {annual_cost_drag:.2f}%")
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)
