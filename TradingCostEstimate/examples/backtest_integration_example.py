"""
Backtest Integration Example: Transaction Cost Estimation
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026

This example demonstrates how to integrate transaction cost estimation
into a backtesting workflow.
"""

import sys
sys.path.append('../src')

import pandas as pd
from transaction_cost_estimator import TransactionCostEstimator
from symbol_data_repository import SymbolDataRepository
from backtest_integration import (
    apply_transaction_costs_to_backtest,
    calculate_strategy_cost_metrics,
    generate_cost_report
)


def create_sample_trades():
    """Create a sample trade log for demonstration."""
    trades = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=20, freq='D'),
        'symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'] * 4,
        'shares': [1000, 500, 200, 300, 400] * 4,
        'price': [180.0, 400.0, 140.0, 170.0, 500.0] * 4,
    })
    
    # Alternate between buys and sells
    trades['shares'] = trades['shares'] * (trades.index % 2 * 2 - 1)
    trades['direction'] = trades['shares'].apply(lambda x: 'buy' if x > 0 else 'sell')
    trades['shares'] = trades['shares'].abs()
    
    return trades


def setup_symbol_repository():
    """Set up symbol repository with S&P 500 mega-cap stocks."""
    repo = SymbolDataRepository()
    
    # Add mega-cap stocks
    mega_caps = {
        'AAPL': (15_000_000_000, 0.00008, 0.018),
        'MSFT': (12_000_000_000, 0.00010, 0.016),
        'GOOGL': (8_000_000_000, 0.00012, 0.020),
        'AMZN': (10_000_000_000, 0.00015, 0.022),
        'NVDA': (20_000_000_000, 0.00010, 0.030)
    }
    
    for symbol, (adv, spread, vol) in mega_caps.items():
        repo.add_symbol(
            symbol=symbol,
            avg_daily_dollar_volume=adv,
            avg_relative_spread=spread,
            daily_volatility=vol,
            impact_coefficient=0.6,
            liquidity_tier='mega_cap'
        )
    
    return repo


def main():
    print("=" * 80)
    print("BACKTEST INTEGRATION EXAMPLE")
    print("=" * 80)
    print()
    
    # 1. Create sample trade log
    print("Step 1: Creating sample trade log...")
    trades_df = create_sample_trades()
    print(f"Generated {len(trades_df)} trades")
    print()
    
    # 2. Set up cost estimator and symbol repository
    print("Step 2: Initializing cost estimator and symbol repository...")
    estimator = TransactionCostEstimator(broker='ibkr_tiered')
    repo = setup_symbol_repository()
    print(f"Loaded {len(repo.get_all_symbols())} symbols")
    print()
    
    # 3. Apply transaction costs to backtest
    print("Step 3: Calculating transaction costs for all trades...")
    trades_with_costs = apply_transaction_costs_to_backtest(
        trades_df=trades_df,
        estimator=estimator,
        symbol_repo=repo,
        removes_liquidity=True,
        impact_model='square_root'
    )
    print("Cost calculation complete")
    print()
    
    # 4. Display sample results
    print("=" * 80)
    print("SAMPLE TRADE RESULTS (First 5 Trades)")
    print("=" * 80)
    print()
    
    display_cols = ['date', 'symbol', 'shares', 'price', 'trade_value', 
                    'total_cost', 'total_cost_bps']
    print(trades_with_costs[display_cols].head().to_string(index=False))
    print()
    
    # 5. Calculate aggregate metrics
    print("=" * 80)
    print("AGGREGATE COST METRICS")
    print("=" * 80)
    print()
    
    metrics = calculate_strategy_cost_metrics(
        trades_with_costs=trades_with_costs,
        initial_capital=1_000_000
    )
    
    print(f"Total Transaction Costs: ${metrics['total_cost']:,.2f}")
    print(f"Average Cost per Trade: ${metrics['avg_cost_per_trade']:.2f}")
    print(f"Average Cost (bps): {metrics['avg_cost_bps']:.2f}")
    print(f"Turnover: {metrics['turnover']:.2f}x")
    print(f"Cost as % of Capital: {metrics['cost_pct_of_capital']:.2f}%")
    print()
    print("Cost Breakdown:")
    print(f"  Brokerage: {metrics['brokerage_pct']:.1f}%")
    print(f"  Spread: {metrics['spread_pct']:.1f}%")
    print(f"  Market Impact: {metrics['impact_pct']:.1f}%")
    print()
    
    # 6. Generate full report
    print("=" * 80)
    print("FULL COST ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    report = generate_cost_report(
        trades_with_costs=trades_with_costs,
        initial_capital=1_000_000,
        time_period_days=20
    )
    print(report)
    
    # 7. Export results
    output_file = 'backtest_with_costs.csv'
    trades_with_costs.to_csv(output_file, index=False)
    print()
    print(f"Results exported to: {output_file}")


if __name__ == '__main__':
    main()
