# QGSI Signal Research

**Quantitative analysis of proprietary HFT trading signals across 400 highly liquid US equities**

**Author:** Alex Bernal, Senior Quantitative Researcher  
**Date:** January 2026  
**Project:** QGSI (Quantitative Gauge Signal Intelligence)

---

## Project Overview

This repository contains the complete analytical codebase for evaluating a proprietary high-frequency trading (HFT) signal system. The research examines 139,959 signals across 400 symbols using 1-minute bar data to understand signal timing, predictive edge, and path-dependent performance characteristics.

### Key Findings

- **Aggregate Edge:** Signals demonstrate positive risk-adjusted returns across multiple holding periods
- **Path Dependency:** Early performance (bars 1-5) is highly predictive of final outcomes
- **Quick Winners:** Signals hitting +0.005% within 5 bars show 78.4% win rate (vs 52.6% aggregate)
- **Signal Density:** Higher SignalCount generally correlates with stronger performance

---

## Repository Structure

```
QGSI/
├── stage1/                          # Stage 1.0: E-Ratio Analysis
│   └── calculate_eratio_example.py  # E-Ratio calculation script
│
├── stage2/                          # Stage 2.0: Trajectory Analysis
│   ├── qgsi_trajectory_analysis_final.py           # Single-symbol trajectory engine
│   └── batch_trajectory_signalcount_efficient.py   # Batch processing for 400 symbols
│
├── stage2.1/                        # Stage 2.1: Path Dependency Analysis
│   ├── path_dependency_analysis.py                 # Path group classification
│   └── create_path_dependency_visualizations.py    # Conditional trajectory charts
│
├── utilities/                       # Utility Scripts
│   ├── check_qgsi_database.py                      # MotherDuck database inspector
│   └── upload_path_dependency_to_motherduck.py     # Cloud database uploader
│
└── README.md                        # This file
```

---

## Research Stages

### Stage 1.0: E-Ratio Analysis

**Objective:** Establish baseline risk-adjusted performance metrics

**Methodology:**
- Calculate E-Ratio (Mean Return / Std Dev) for all 400 symbols
- Analyze signal co-occurrence patterns
- Examine time-of-day and volatility regime dependencies

**Key Output:** Confirmation of statistical edge across the signal universe

**Script:** `stage1/calculate_eratio_example.py`

---

### Stage 2.0: Trajectory Analysis

**Objective:** Understand pre-signal and post-signal price dynamics

**Methodology:**
- Universal Reference Point: Bar 0 Close = 0% for all calculations
- Inbound trajectory: Bars -10 to -1 (setup pattern)
- Outbound trajectory: Bars 1 to 30 (predictive edge)
- SignalCount binning: Stratify by signal density

**Key Findings:**
- Long signals: +0.024% mean return, 52.6% win rate (aggregate)
- Short signals: -0.080% mean return, 52.4% win rate (aggregate)
- Higher SignalCount improves performance for Long signals

**Scripts:**
- `stage2/qgsi_trajectory_analysis_final.py` - Single symbol processing
- `stage2/batch_trajectory_signalcount_efficient.py` - Batch processing (400 symbols)

**Outputs:**
- 5.7 million trajectory rows (139,959 signals × 41 bars)
- Aggregate trajectory charts and statistics tables
- Per-symbol trajectory and statistics files

---

### Stage 2.1: Path Dependency Analysis

**Objective:** Identify real-time indicators of signal quality

**Methodology:**
- First-Passage Time (FPT): Time to hit ±0.005% thresholds
- Path Group Classification (bars 1-5):
  - **Quick Winners:** Hit +0.005% within 5 bars
  - **Quick Losers:** Hit -0.005% within 5 bars
  - **Chop/Drift:** Neither threshold hit
- MAE/MFE: Maximum adverse/favorable excursion

**Key Findings:**

| Path Group | % of Signals | Win Rate | Mean Return | Profit Factor |
|------------|--------------|----------|-------------|---------------|
| **Long Signals** |
| Quick Winners | 6.1% | 78.4% | +0.760% | 5.11 |
| Quick Losers | 6.2% | 25.9% | -0.634% | 0.28 |
| Chop/Drift | 87.7% | 51.9% | +0.024% | 1.13 |
| **Short Signals** |
| Quick Winners | 6.7% | 74.8% | -0.681% | 4.35 |
| Quick Losers | 6.3% | 27.4% | +0.608% | 0.31 |
| Chop/Drift | 87.0% | 51.7% | -0.074% | 1.18 |

**Scripts:**
- `stage2.1/path_dependency_analysis.py` - Path group classification
- `stage2.1/create_path_dependency_visualizations.py` - Conditional trajectory charts

**Outputs:**
- path_dependency_results.parquet (139,959 rows)
- Conditional trajectory charts by path group
- Statistics tables for each path group

---

## Data Sources

### MotherDuck Cloud Database

**Database:** QGSI  
**Connection:** Requires MotherDuck token

**Tables:**
1. **QGSI_AllSymbols_3Signals** (5.7M rows)
   - 1-minute OHLC bars with signal components
   - 400 symbols, multiple signal types
   
2. **statistics_data** (60 rows)
   - Per-bar statistics for AAPL case study
   
3. **trajectory_data** (16,523 rows)
   - Full trajectory data for AAPL case study
   
4. **path_dependency_analysis** (139,959 rows)
   - Path group classifications and FPT metrics

---

## Installation

### Prerequisites

```bash
# Python 3.11 or higher
python3.11 --version

# Install required packages
pip3 install pandas numpy matplotlib seaborn duckdb pyarrow
```

### Clone Repository

```bash
git clone https://github.com/alexbernal0/QGSI.git
cd QGSI
```

---

## Usage

### Stage 1.0: Calculate E-Ratios

```bash
cd stage1
python3.11 calculate_eratio_example.py
```

### Stage 2.0: Trajectory Analysis

**Single symbol:**
```bash
cd stage2
python3.11 qgsi_trajectory_analysis_final.py AAPL
```

**All 400 symbols:**
```bash
python3.11 batch_trajectory_signalcount_efficient.py
```

### Stage 2.1: Path Dependency Analysis

```bash
cd stage2.1
python3.11 path_dependency_analysis.py
python3.11 create_path_dependency_visualizations.py
```

---

## Practical Applications

### 1. Real-Time Signal Filtering
Monitor bars 1-5 after signal generation:
- **Quick Winner pattern:** Scale up position (150-200% of baseline)
- **Quick Loser pattern:** Exit or reduce position (25% of baseline)

### 2. Adaptive Risk Management
- **Quick Winners:** Wider stops (-0.015% to -0.020%), allow momentum to develop
- **Quick Losers:** Tight stops (-0.008% to -0.010%), exit quickly
- **Chop/Drift:** Moderate stops (-0.012%), time-based exit if no conviction

### 3. Multi-Horizon Profit Taking
- **25% exit at bar 10:** Early momentum capture
- **50% exit at bar 20:** Mid-point optimization
- **25% exit at bar 30 or trailing stop:** Capture extended runs

### 4. Feature Engineering for ML
- Use PathGroup as target variable
- Identify pre-signal features that predict path group membership
- Build predictive models for real-time classification

---

## Dependencies

- **pandas** (>=1.5.0): Data manipulation
- **numpy** (>=1.23.0): Numerical computing
- **matplotlib** (>=3.6.0): Visualization
- **seaborn** (>=0.12.0): Statistical visualization
- **duckdb** (>=0.9.0): MotherDuck database access
- **pyarrow** (>=10.0.0): Parquet file I/O

---

## Documentation

- **Procedure Manual:** Complete methodology documentation (v3)
- **Stage 2.0 Report:** Trajectory analysis findings (PDF)
- **Stage 2.1 Report:** Path dependency analysis findings (PDF)

All documentation available in project checkpoint archives.

---

## Contact

**Alex Bernal**  
Senior Quantitative Researcher  
Obsidian Quantitative  
Email: ben@obsidianquantitative.com

---

## License

Proprietary - All Rights Reserved

This code is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Acknowledgments

- MotherDuck for cloud database infrastructure
- Python scientific computing community

---

**Last Updated:** January 09, 2026
