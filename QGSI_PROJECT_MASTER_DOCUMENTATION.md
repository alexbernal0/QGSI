# QGSI Quantitative Research Project: Master Documentation

**Version:** 1.0
**Date:** 2026-01-15
**Author:** Manus AI

## 1. Project Overview

This document provides a comprehensive overview and replication guide for the QGSI Quantitative Research Project. The project aims to identify, optimize, and backtest systematic trading strategies for a universe of 400 US stocks over a 17+ year period (2007-2024). The project is divided into several distinct phases, from initial signal evaluation to final performance analysis.

## 2. Data Architecture

The project relies on a single source data file and generates several intermediate and final data tables, primarily stored in Parquet format and uploaded to a MotherDuck database.

### 2.1. Source Data

- **File:** `QGSI_AllSymbols_3Signals.parquet` (972 MB)
- **Description:** Contains daily OHLCV data and three signal types (Signal 1, 2, 3) for 400 US stocks from 2007 to 2024.

### 2.2. Intermediate Data

- **Files:** `data_chunks/chunk_*.parquet` (42 files, ~20-30 MB each)
- **Description:** The source data split into smaller, manageable chunks of 10 symbols each to overcome memory constraints during processing.
- **Program:** `split_parquet_streaming.py`

### 2.3. Final Output Tables

| Table Name                          | Format          | Description                                         |
|-------------------------------------|-----------------|-----------------------------------------------------|
| `best_long_strategy_trades`         | Parquet, MD Table | Full trade log for the best LONG strategy (80,060 trades) |
| `best_long_strategy_equity_curves`  | Parquet, MD Table | Equity curve data for each symbol (LONG)            |
| `best_short_strategy_trades`        | Parquet, MD Table | Full trade log for the best SHORT strategy (60,111 trades)|
| `best_short_strategy_equity_curves` | Parquet, MD Table | Equity curve data for each symbol (SHORT)           |

## 3. Phase 1: E-Ratio & Trajectory Analysis

*(Details of this phase were conducted prior to this chat session but are included for completeness)*

- **Objective:** Evaluate the predictive power of the three initial signals using E-Ratio and trajectory analysis.
- **Key Finding:** Signal 3 was identified as the most promising signal for further development.

## 4. Phase 2: Statistical Testing

*(Details of this phase were conducted prior to this chat session but are included for completeness)*

- **Objective:** Perform rigorous statistical tests on Signal 3 to validate its non-random nature and predictive edge.
- **Key Finding:** Signal 3 demonstrated statistically significant predictive power, justifying its use in strategy development.

## 5. Phase 3: Strategy Optimization (LONG)

- **Objective:** Optimize four distinct strategy types using LONG signals (Signal = 1) to find the best performing parameters.
- **Strategies Tested:**
  1. Fixed ATR Symmetric
  2. Fixed ATR Asymmetric
  3. ATR Trailing Stop
  4. ATR Breakeven Stop
- **Programs Used:** Various optimization processors (e.g., `fixed_atr_asymmetric_long_processor.py` - *Note: these files were superseded by the final backtest processors*)
- **Best Strategy Found:** **ATR Trailing Stop**
  - **Parameters:** ATR(30), Multiplier 5.0×
  - **Performance:** +$1,281,000 Net Profit, 1.087 Profit Factor

## 6. Phase 4: Strategy Optimization (SHORT)

- **Objective:** Optimize the same four strategy types using SHORT signals (Signal = -1).
- **Programs Used:**
  - `fixed_atr_symmetric_short_processor.py`
  - `fixed_atr_asymmetric_short_chunked.py`
  - `atr_breakeven_short_chunked.py`
  - `atr_trailing_stop_short_processor.py`
- **Best Strategy Found:** **ATR Trailing Stop**
  - **Parameters:** ATR(30), Multiplier 1.5×
  - **Performance:** +$859,092 Net Profit, 1.139 Profit Factor

## 7. Phase 5: Baseline Backtesting

- **Objective:** Perform a full, detailed backtest of the single best LONG and SHORT strategies across the entire dataset to generate comprehensive trade logs and equity curves.

### 7.1. LONG Strategy Backtest

- **Program:** `process_best_long_from_chunks.py`
- **Strategy:** ATR Trailing Stop, ATR(30), Multiplier 5.0×
- **Final Result:** **+$10,861,663 Net Profit**, 1.782 Profit Factor

### 7.2. SHORT Strategy Backtest

- **Program:** `process_best_short_strategy_all_trades.py`
- **Strategy:** ATR Trailing Stop, ATR(30), Multiplier 1.5×
- **Final Result:** **+$14,392,080 Net Profit**, 4.436 Profit Factor

## 8. Replication Guide

1.  **Prerequisites:**
    - Python 3.11+
    - Required packages: `pandas`, `numpy`, `pyarrow`, `duckdb`, `reportlab`, `matplotlib`
    - Access to the source data file: `QGSI_AllSymbols_3Signals.parquet`
    - MotherDuck token with write access to the `qgsi` database.

2.  **Step-by-Step Instructions:**
    1.  Place the source parquet file in `/home/ubuntu/upload/`.
    2.  Run `split_parquet_streaming.py` to create the data chunks.
    3.  Run `process_best_long_from_chunks.py` to generate LONG trade logs.
    4.  Run `process_best_short_strategy_all_trades.py` to generate SHORT trade logs.
    5.  Run `generate_equity_curves.py` for LONG equity curves.
    6.  Run `generate_equity_curves_short.py` for SHORT equity curves.
    7.  Set the `MOTHERDUCK_TOKEN` environment variable.
    8.  Run `upload_backtest_data_to_motherduck.py` to populate the database.
    9.  Run `create_optimized_strategy_backtests_report.py` to generate the final PDF report.

## 9. File Inventory

*(A complete list of all 43 project files, including Python scripts, CSVs, Parquets, PDFs, and PNGs, is included in the `QGSI_Stage4_Complete_Backup_20260115.zip` archive)*

## 10. MotherDuck Database Schema

- **Database:** `qgsi`
- **Tables:**
  - `best_long_strategy_trades`
  - `best_long_strategy_equity_curves`
  - `best_short_strategy_trades`
  - `best_short_strategy_equity_curves`

*(All tables share a similar schema with columns for Symbol, Date, Price, Profit, etc., as detailed in the Python processing scripts)*
