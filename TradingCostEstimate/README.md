# Transaction Cost Estimation Framework

**Author:** Alex Bernal, Senior Quantitative Analyst, QGSI  
**Date:** January 16, 2026  
**Version:** 1.0.0

## Overview

This repository contains a comprehensive transaction cost estimation framework optimized for S&P 500 trading strategies using Interactive Brokers Pro Tiered pricing. The framework provides accurate, symbol-specific cost calculations that are 5-20x more precise than generic academic assumptions.

## Key Features

- **Broker-Specific Models:** Complete Interactive Brokers Pro Tiered commission structure with all regulatory fees
- **Symbol-Specific Parameters:** Customizable spread, volatility, and market impact coefficients per symbol
- **Multiple Impact Models:** Square-root (recommended), linear, and power-law market impact models
- **Backtest Integration:** Ready-to-use functions for applying costs to trade logs
- **Comprehensive Reporting:** Automated cost analysis and performance attribution

## Quick Start

### Basic Usage

```python
from src.transaction_cost_estimator import TransactionCostEstimator
from src.symbol_data_repository import SymbolDataRepository

# Initialize estimator
estimator = TransactionCostEstimator(broker='ibkr_tiered')

# Set up symbol repository
repo = SymbolDataRepository()
repo.add_symbol(
    symbol='AAPL',
    avg_daily_dollar_volume=15_000_000_000,
    avg_relative_spread=0.00008,
    daily_volatility=0.018,
    impact_coefficient=0.6,
    liquidity_tier='mega_cap'
)

# Calculate cost for a trade
symbol_data = repo.get_symbol_data('AAPL')
cost = estimator.calculate_total_cost(
    shares=5000,
    price=200.0,
    direction='buy',
    symbol_data=symbol_data
)

print(f"Total Cost: ${cost['total_cost']:.2f} ({cost['total_cost_bps']:.2f} bps)")
```

### Backtest Integration

```python
from src.backtest_integration import apply_transaction_costs_to_backtest

# Apply costs to your trade log
trades_with_costs = apply_transaction_costs_to_backtest(
    trades_df=your_trades,
    estimator=estimator,
    symbol_repo=repo
)

# Calculate aggregate metrics
from src.backtest_integration import calculate_strategy_cost_metrics
metrics = calculate_strategy_cost_metrics(trades_with_costs, initial_capital=1_000_000)
```

## Repository Structure

```
TradingCostEstimate/
├── README.md                           # This file
├── src/                                # Source code
│   ├── __init__.py                     # Package initialization
│   ├── transaction_cost_estimator.py  # Core cost estimator
│   ├── symbol_data_repository.py      # Symbol data management
│   └── backtest_integration.py        # Backtest integration utilities
├── examples/                           # Usage examples
│   ├── basic_usage.py                  # Basic usage example
│   └── backtest_integration_example.py # Backtest integration example
└── docs/                               # Documentation
    ├── final_trading_cost_report.pdf   # Full research report (PDF)
    ├── final_trading_cost_report.md    # Full research report (Markdown)
    └── cost_estimates_summary.md       # Quick reference guide
```

## Cost Estimates: Quick Reference

### Typical S&P 500 Trade ($1M)

| Liquidity Tier | Total Cost | Basis Points |
|----------------|------------|--------------|
| **Mega-Cap (Top 50)** | **$135** | **1.35 bps** |
| **Large-Cap (Next 200)** | **$285** | **2.85 bps** |
| **Mid-Large (Bottom 250)** | **$695** | **6.95 bps** |

**Recommended baseline for S&P 500 backtesting: 2.85 bps**

## Key Findings

1. **Commission is Negligible:** IBKR Pro Tiered commissions are only $0.35-$20 per trade, representing <10% of total costs for liquid stocks

2. **Spread + Impact Dominate:** Implicit costs now constitute 90%+ of total transaction costs

3. **Liquidity is Critical:** Mega-cap stocks cost 3-5x less than mid-large S&P 500 names

4. **Generic 20 bps Model is 7x Too High:** For $1M trade, actual cost is $285 vs. $2,000 assumption

## Documentation

### Full Research Report
- **PDF:** `docs/final_trading_cost_report.pdf`
- **Markdown:** `docs/final_trading_cost_report.md`

Comprehensive 40+ page report covering:
- Hudson & Thames case study deconstruction
- Interactive Brokers fee structure analysis
- S&P 500 liquidity advantage quantification
- Symbol-specific cost estimation framework
- Complete Python implementation guide

### Quick Reference
- **Cost Estimates:** `docs/cost_estimates_summary.md`

Practical dollar and basis point estimates for various trade sizes and liquidity tiers.

## Examples

### Run Basic Usage Example
```bash
cd examples
python basic_usage.py
```

### Run Backtest Integration Example
```bash
cd examples
python backtest_integration_example.py
```

## Implementation Recommendations

### For High-Frequency Strategies (400%+ Turnover)
- **Stick to mega-cap stocks** (Top 50-100 S&P 500)
- Expected cost: **1.35 bps**
- Annual cost drag with 400% turnover: **5.4%**

### For Medium-Frequency Strategies (100-200% Turnover)
- **Trade top 200 S&P 500 stocks**
- Expected cost: **2.85 bps**
- Annual cost drag with 200% turnover: **5.7%**

### For Lower-Frequency Strategies (< 100% Turnover)
- **Full S&P 500 universe acceptable**
- Expected cost: **2.85-6.95 bps**
- Annual cost drag with 50% turnover: **1.4-3.5%**

## Dependencies

```python
numpy
pandas
```

## Version History

- **v1.0.0** (January 16, 2026): Initial release
  - Complete IBKR Pro Tiered implementation
  - Symbol-specific cost framework
  - Backtest integration utilities
  - Comprehensive documentation

## Contact

**Alex Bernal**  
Senior Quantitative Analyst  
QGSI

## License

Internal use only - QGSI Proprietary

---

*For detailed methodology, academic references, and implementation details, please refer to the full research report in the `docs/` directory.*
