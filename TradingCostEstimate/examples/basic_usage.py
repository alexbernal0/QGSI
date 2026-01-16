"""
Basic Usage Example: Transaction Cost Estimation
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026

This example demonstrates how to use the transaction cost estimation framework
for a single trade calculation.
"""

import sys
sys.path.append('../src')

from transaction_cost_estimator import TransactionCostEstimator
from symbol_data_repository import SymbolDataRepository


def main():
    # 1. Initialize estimator with IBKR Pro Tiered pricing
    estimator = TransactionCostEstimator(broker='ibkr_tiered')
    
    # 2. Set up symbol repository
    repo = SymbolDataRepository()
    
    # Add AAPL (mega-cap, highly liquid)
    repo.add_symbol(
        symbol='AAPL',
        avg_daily_dollar_volume=15_000_000_000,  # $15B daily volume
        avg_relative_spread=0.00008,  # 0.8 bps
        daily_volatility=0.018,  # 1.8% daily vol
        impact_coefficient=0.6,  # Low impact for mega-cap
        liquidity_tier='mega_cap'
    )
    
    # Add a mid-cap S&P 500 stock for comparison
    repo.add_symbol(
        symbol='XYZ',
        avg_daily_dollar_volume=200_000_000,  # $200M daily volume
        avg_relative_spread=0.00055,  # 5.5 bps
        daily_volatility=0.025,  # 2.5% daily vol
        impact_coefficient=0.7,
        liquidity_tier='mid_large'
    )
    
    # 3. Calculate cost for a $1M buy order of AAPL
    print("=" * 80)
    print("EXAMPLE 1: $1M Buy Order - AAPL (Mega-Cap)")
    print("=" * 80)
    
    symbol_data = repo.get_symbol_data('AAPL')
    cost_breakdown = estimator.calculate_total_cost(
        shares=5000,
        price=200.0,
        direction='buy',
        symbol_data=symbol_data,
        removes_liquidity=True,
        impact_model='square_root'
    )
    
    print(f"\nTrade Value: ${cost_breakdown['trade_value']:,.2f}")
    print(f"Total Cost: ${cost_breakdown['total_cost']:.2f}")
    print(f"Total Cost (bps): {cost_breakdown['total_cost_bps']:.2f}")
    print(f"\nBreakdown:")
    print(f"  Commission:        ${cost_breakdown['commission']:>10.2f}")
    print(f"  Exchange/Clearing: ${cost_breakdown['exchange_fee'] + cost_breakdown['clearing_fee']:>10.2f}")
    print(f"  Spread Cost:       ${cost_breakdown['spread_cost']:>10.2f} ({cost_breakdown['spread_cost_bps']:.2f} bps)")
    print(f"  Market Impact:     ${cost_breakdown['impact_cost']:>10.2f} ({cost_breakdown['impact_cost_bps']:.2f} bps)")
    print(f"  Participation Rate: {cost_breakdown['participation_rate']:.4%}")
    
    # 4. Calculate cost for the same $1M order of a mid-cap stock
    print("\n" + "=" * 80)
    print("EXAMPLE 2: $1M Buy Order - XYZ (Mid-Large Cap)")
    print("=" * 80)
    
    symbol_data = repo.get_symbol_data('XYZ')
    cost_breakdown = estimator.calculate_total_cost(
        shares=5000,
        price=200.0,
        direction='buy',
        symbol_data=symbol_data,
        removes_liquidity=True,
        impact_model='square_root'
    )
    
    print(f"\nTrade Value: ${cost_breakdown['trade_value']:,.2f}")
    print(f"Total Cost: ${cost_breakdown['total_cost']:.2f}")
    print(f"Total Cost (bps): {cost_breakdown['total_cost_bps']:.2f}")
    print(f"\nBreakdown:")
    print(f"  Commission:        ${cost_breakdown['commission']:>10.2f}")
    print(f"  Exchange/Clearing: ${cost_breakdown['exchange_fee'] + cost_breakdown['clearing_fee']:>10.2f}")
    print(f"  Spread Cost:       ${cost_breakdown['spread_cost']:>10.2f} ({cost_breakdown['spread_cost_bps']:.2f} bps)")
    print(f"  Market Impact:     ${cost_breakdown['impact_cost']:>10.2f} ({cost_breakdown['impact_cost_bps']:.2f} bps)")
    print(f"  Participation Rate: {cost_breakdown['participation_rate']:.4%}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Mid-cap stock costs 5x more than mega-cap for same trade size!")
    print("=" * 80)


if __name__ == '__main__':
    main()
