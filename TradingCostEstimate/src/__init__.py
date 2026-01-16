"""
Transaction Cost Estimation Framework
Author: Alex Bernal, Senior Quantitative Analyst, QGSI
Date: January 16, 2026
"""

from .transaction_cost_estimator import TransactionCostEstimator
from .symbol_data_repository import SymbolDataRepository
from .backtest_integration import (
    apply_transaction_costs_to_backtest,
    calculate_strategy_cost_metrics,
    estimate_annual_cost_drag,
    generate_cost_report
)

__all__ = [
    'TransactionCostEstimator',
    'SymbolDataRepository',
    'apply_transaction_costs_to_backtest',
    'calculate_strategy_cost_metrics',
    'estimate_annual_cost_drag',
    'generate_cost_report'
]

__version__ = '1.0.0'
__author__ = 'Alex Bernal, Senior Quantitative Analyst, QGSI'
