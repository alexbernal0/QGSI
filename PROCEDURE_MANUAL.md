# QGSI Stage 4: ATR Exit Strategy Optimization - Procedure Manual

**Version:** 1.0  
**Date:** 2026-01-13  
**Author:** QGSI Research Team

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Data Preparation](#data-preparation)
4. [Strategy Processing Pipeline](#strategy-processing-pipeline)
5. [Analysis & Visualization](#analysis--visualization)
6. [Report Generation](#report-generation)
7. [GitHub Repository Structure](#github-repository-structure)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This procedure manual documents the complete process for optimizing ATR-based exit strategies across 400 US equities. The process has been successfully completed for **Phase 1: Long Signals** (~80K signals) and will be replicated for **Phase 2: Short Signals** (~60K signals).

### Key Metrics
- **Total Strategies:** 4 (Fixed Symmetric, Fixed Asymmetric, Trailing Stop, Breakeven Stop)
- **Total Parameter Combinations:** 188
- **Total Backtests per Phase:** ~15 Million
- **Processing Time per Phase:** ~6 Hours
- **Output:** Comprehensive quantitative research report (16 pages)

---

## Prerequisites

### Environment Setup
```bash
# Python 3.11 with required packages
sudo pip3 install pandas numpy duckdb pyarrow matplotlib seaborn reportlab scipy

# Verify installations
python3.11 --version
pip3 list | grep -E "pandas|numpy|duckdb|pyarrow|matplotlib|seaborn|reportlab|scipy"
```

### Data Requirements
- **Source File:** `QGSI_AllSymbols_3Signals.parquet` (972 MB)
- **Location:** `/home/ubuntu/upload/`
- **Contents:** 400 symbols, ~2.5M bars, 80,129 long signals, 60,139 short signals
- **Columns:** Symbol, Date, Open, High, Low, Close, Volume, Signal, ATR_14, ATR_20, ATR_30, ATR_50

### Directory Structure
```
/home/ubuntu/stage4_optimization/
├── PROCEDURE_MANUAL.md                          # This file
├── fixed_atr_all_signals_processor.py           # Strategy 1: Fixed Symmetric
├── fixed_atr_asymmetric_optimizer.py            # Strategy 2: Fixed Asymmetric
├── atr_trailing_stop_optimizer_v3.py            # Strategy 3: Trailing Stop
├── atr_breakeven_all_signals_processor.py       # Strategy 4: Breakeven Stop
├── create_heatmaps_with_3d.py                   # Visualization generator
├── create_complete_report.py                    # Final report generator
├── save_individual_performance_csvs.py          # Results aggregator
├── upload_*_to_motherduck.py                    # Database upload scripts
└── [output files]
```

---

## Data Preparation

### Step 1: Verify Source Data
```bash
cd /home/ubuntu/upload
ls -lh QGSI_AllSymbols_3Signals.parquet

# Expected output: -rw-r--r-- 1 ubuntu ubuntu 972M Jan 13 10:00 QGSI_AllSymbols_3Signals.parquet
```

### Step 2: Inspect Data Schema
```python
import pandas as pd

df = pd.read_parquet('/home/ubuntu/upload/QGSI_AllSymbols_3Signals.parquet')
print(f"Total Rows: {len(df):,}")
print(f"Columns: {df.columns.tolist()}")
print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Unique Symbols: {df['Symbol'].nunique()}")

# Count signals
long_signals = df[df['Signal'] == 1].shape[0]
short_signals = df[df['Signal'] == -1].shape[0]
print(f"Long Signals: {long_signals:,}")
print(f"Short Signals: {short_signals:,}")
```

**Expected Output:**
```
Total Rows: 2,500,000+
Columns: ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Signal', 'ATR_14', 'ATR_20', 'ATR_30', 'ATR_50']
Date Range: 2020-01-01 to 2023-12-31
Unique Symbols: 400
Long Signals: 80,129
Short Signals: 60,139
```

---

## Strategy Processing Pipeline

### Phase 1: Long Signals (COMPLETED)

#### Strategy 1: Fixed ATR Symmetric
**File:** `fixed_atr_all_signals_processor.py`  
**Parameters:** 4 ATR periods × 8 multipliers = 32 combinations  
**Processing Time:** ~45 minutes

```bash
cd /home/ubuntu/stage4_optimization
python3.11 fixed_atr_all_signals_processor.py
```

**Output Files:**
- `Fixed_ATR_Symmetric_Long_Performance.csv` (32 rows)
- MotherDuck table: `fixed_atr_all_signals_long`

**Key Logic:**
```python
# Entry: Buy at signal bar CLOSE
# Stop Loss: Entry - (ATR × Multiplier)
# Target: Entry + (ATR × Multiplier)
# Time Limit: 30 bars
# Exit: First of STOP, TARGET, or TIME
```

---

#### Strategy 2: Fixed ATR Asymmetric
**File:** `fixed_atr_asymmetric_optimizer.py`  
**Parameters:** 4 ATR periods × 7 stop multipliers × 4 target multipliers = 112 combinations  
**Processing Time:** ~90 minutes

```bash
python3.11 fixed_atr_asymmetric_optimizer.py
```

**Output Files:**
- `Fixed_ATR_Asymmetric_Long_Performance.csv` (112 rows)
- MotherDuck table: `fixed_atr_asymmetric_long`

**Key Logic:**
```python
# Entry: Buy at signal bar CLOSE
# Stop Loss: Entry - (ATR × StopMultiplier)
# Target: Entry + (ATR × TargetMultiplier)
# Time Limit: 30 bars
# Constraint: TargetMultiplier >= StopMultiplier
```

---

#### Strategy 3: ATR Trailing Stop
**File:** `atr_trailing_stop_optimizer_v3.py`  
**Parameters:** Fixed ATR(30) × 8 multipliers = 8 combinations  
**Processing Time:** ~30 minutes

```bash
python3.11 atr_trailing_stop_optimizer_v3.py
```

**Output Files:**
- `ATR_Trailing_Stop_Long_Performance.csv` (8 rows)
- MotherDuck table: `atr_trailing_stop_long`

**Key Logic:**
```python
# Entry: Buy at signal bar CLOSE
# Initial Stop: Entry LOW - (ATR × Multiplier)
# Trailing Stop: MAX(previous_stop, Current LOW - (ATR × Multiplier))
# Target: None (let winners run)
# Time Limit: 20 bars
# Exit: STOP or TIME only
```

---

#### Strategy 4: ATR Breakeven Stop
**File:** `atr_breakeven_all_signals_processor.py`  
**Parameters:** Fixed ATR(30) × 6 BE triggers × 6 targets = 36 combinations  
**Processing Time:** ~60 minutes

```bash
python3.11 atr_breakeven_all_signals_processor.py
```

**Output Files:**
- `ATR_Breakeven_Stop_Long_Performance.csv` (36 rows)
- MotherDuck table: `atr_breakeven_long`

**Key Logic:**
```python
# Entry: Buy at signal bar CLOSE
# Initial Stop: Entry - (ATR × 2.0)  # Fixed 2.0× stop
# Breakeven Trigger: Entry + (ATR × BETrigger)
# Once triggered: Move stop to Entry (zero loss)
# Target: Entry + (ATR × TargetMultiplier)
# Time Limit: 30 bars
```

---

### Phase 2: Short Signals (TO BE PROCESSED)

**Critical Difference:** All exit logic must be **INVERTED** for short positions.

#### Inverted Logic for Shorts:
```python
# LONG (Buy):
# Entry: Buy at CLOSE
# Stop: Entry - (ATR × Multiplier)  # Below entry
# Target: Entry + (ATR × Multiplier)  # Above entry

# SHORT (Sell):
# Entry: Sell at CLOSE
# Stop: Entry + (ATR × Multiplier)  # Above entry (loss if price rises)
# Target: Entry - (ATR × Multiplier)  # Below entry (profit if price falls)
```

#### Trailing Stop Inversion:
```python
# LONG Trailing:
# Stop = MAX(previous_stop, Current LOW - ATR × Multiplier)  # Rises with price

# SHORT Trailing:
# Stop = MIN(previous_stop, Current HIGH + ATR × Multiplier)  # Falls with price
```

#### Breakeven Inversion:
```python
# LONG Breakeven:
# If (Current HIGH >= Entry + ATR × BETrigger): Move stop to Entry

# SHORT Breakeven:
# If (Current LOW <= Entry - ATR × BETrigger): Move stop to Entry
```

---

## Analysis & Visualization

### Step 1: Aggregate Results
**File:** `save_individual_performance_csvs.py`

```bash
python3.11 save_individual_performance_csvs.py
```

**Output:**
- `All_Strategies_Long_Performance_Summary.csv` (4 rows, best from each strategy)
- `best_strategy_settings.json` (optimal parameters for equity curves)

---

### Step 2: Generate Heatmaps with 3D Surface Plots
**File:** `create_heatmaps_with_3d.py`

```bash
python3.11 create_heatmaps_with_3d.py
```

**Output (4 PNG files):**
- `Fixed_ATR_Symmetric_with_3D.png`
- `Fixed_ATR_Asymmetric_with_3D.png`
- `ATR_Trailing_Stop_with_3D.png`
- `ATR_Breakeven_Stop_with_3D.png`

**Each file contains:**
- Top: System Score heatmap (ATR period × Multiplier)
- Middle: Net Profit heatmap, Profit Factor heatmap
- Bottom: 3D surface plot showing optimization landscape

---

### Step 3: Generate Comprehensive Report
**File:** `create_complete_report.py`

```bash
python3.11 create_complete_report.py
```

**Output:**
- `QGSI_Complete_Quantitative_Research_Report_Phase1.pdf` (16 pages)

**Report Sections:**
1. Executive Summary
2. Data Preparation & Methodology
3. Optimization Process
4. Strategy Comparison & Results
5. Detailed Strategy Analysis (with 3D heatmaps)
6. Statistical Analysis & Robustness
7. Strategic Implications & Recommendations
8. Conclusion & Next Steps
9. Appendix

---

## Report Generation

### Report Structure Template

```python
# Section 1: Executive Summary
- Overview paragraph (4-6 sentences)
- Data volume table (7 metrics)

# Section 2: Data Preparation & Methodology
- 2.1 Dataset Dimensions
- 2.2 ATR Calculation Methodology
- 2.3 Data Preprocessing & Quality Control

# Section 3: Optimization Process
- 3.1 Objective Function: System Score
- 3.2 Parameter Space Design
- 3.3 Backtesting Engine Architecture

# Section 4: Strategy Comparison & Results
- Comparison table (4 strategies)
- 4.1 Key Insights (7 bullet points)

# Section 5: Detailed Strategy Analysis
- 5.1 Fixed ATR Symmetric (with 3D heatmap)
- 5.2 Fixed ATR Asymmetric (with 3D heatmap)
- 5.3 ATR Trailing Stop (with 3D heatmap)
- 5.4 ATR Breakeven Stop (with 3D heatmap)

# Section 6: Statistical Analysis & Robustness
- 6.1 Performance Metrics Deep Dive
- 6.2 Parameter Sensitivity Analysis
- 6.3 Cross-Symbol Consistency

# Section 7: Strategic Implications & Recommendations
- 7.1 Optimal Strategy Selection by Objective
- 7.2 Risk Management Considerations
- 7.3 Implementation Roadmap

# Section 8: Conclusion & Next Steps
- Conclusion paragraph
- 8.1 Best Settings Summary table
- 8.2 Immediate Next Steps (8 bullet points)

# Section 9: Appendix
- 9.1 Data Files & Reproducibility
- 9.2 GitHub Repository
- 9.3 References & Prior Research
- 9.4 Acknowledgments
```

---

## GitHub Repository Structure

### Repository: https://github.com/alexbernal0/QGSI/tree/main/stage4

```
stage4/
├── README.md                                    # Overview and quick start
├── PROCEDURE_MANUAL.md                          # This comprehensive guide
├── data/
│   └── QGSI_AllSymbols_3Signals.parquet        # Source dataset (not in repo, too large)
├── processors/
│   ├── fixed_atr_all_signals_processor.py      # Strategy 1 processor
│   ├── fixed_atr_asymmetric_optimizer.py       # Strategy 2 processor
│   ├── atr_trailing_stop_optimizer_v3.py       # Strategy 3 processor
│   └── atr_breakeven_all_signals_processor.py  # Strategy 4 processor
├── analytics/
│   ├── save_individual_performance_csvs.py     # Results aggregator
│   ├── create_heatmaps_with_3d.py              # Visualization generator
│   └── create_complete_report.py               # Report generator
├── database/
│   ├── upload_fixed_atr_all_signals.py         # Upload Strategy 1 to MotherDuck
│   ├── upload_atr_ts_to_motherduck.py          # Upload Strategy 3 to MotherDuck
│   └── upload_breakeven_all_signals.py         # Upload Strategy 4 to MotherDuck
├── results/
│   ├── long/                                    # Phase 1 results
│   │   ├── Fixed_ATR_Symmetric_Long_Performance.csv
│   │   ├── Fixed_ATR_Asymmetric_Long_Performance.csv
│   │   ├── ATR_Trailing_Stop_Long_Performance.csv
│   │   ├── ATR_Breakeven_Stop_Long_Performance.csv
│   │   ├── All_Strategies_Long_Performance_Summary.csv
│   │   ├── best_strategy_settings.json
│   │   ├── Fixed_ATR_Symmetric_with_3D.png
│   │   ├── Fixed_ATR_Asymmetric_with_3D.png
│   │   ├── ATR_Trailing_Stop_with_3D.png
│   │   ├── ATR_Breakeven_Stop_with_3D.png
│   │   └── QGSI_Complete_Quantitative_Research_Report_Phase1.pdf
│   └── short/                                   # Phase 2 results (to be generated)
└── utils/
    └── verify_signal_coverage.py                # Data validation utility
```

---

## Troubleshooting

### Issue 1: Memory Error During Processing
**Symptom:** `MemoryError` or process killed  
**Solution:** Process in smaller batches

```python
# Modify batch size in processor file
BATCH_SIZE = 5  # Reduce from 10 to 5 symbols per batch
```

---

### Issue 2: Missing ATR Data
**Symptom:** Signals skipped due to insufficient ATR initialization  
**Expected:** 258 long signals skipped (99.82% coverage)

```python
# This is normal - first 30 bars of each symbol lack ATR(30) data
# Verify coverage:
python3.11 verify_signal_coverage.py
```

---

### Issue 3: MotherDuck Upload Failure
**Symptom:** `duckdb.IOException: Failed to upload`  
**Solution:** Check credentials and retry

```bash
# Verify MotherDuck connection
python3.11 -c "import duckdb; conn = duckdb.connect('md:'); print('Connected')"

# Retry upload
python3.11 upload_fixed_atr_all_signals.py
```

---

### Issue 4: Heatmap Generation Error
**Symptom:** `ValueError: x and y must have same first dimension`  
**Solution:** Ensure all CSV files exist and have correct format

```bash
# Verify CSV files
ls -lh *_Performance.csv

# Check row counts
wc -l *_Performance.csv
```

---

## Phase 2 Execution Checklist

### Pre-Processing
- [ ] Verify all Phase 1 results are saved
- [ ] Update GitHub with all Phase 1 files
- [ ] Create `results/short/` directory
- [ ] Verify short signal count: ~60,139 signals

### Strategy Processing (Same Order)
- [ ] Strategy 1: Fixed ATR Symmetric (32 combinations)
- [ ] Strategy 2: Fixed ATR Asymmetric (112 combinations)
- [ ] Strategy 3: ATR Trailing Stop (8 combinations)
- [ ] Strategy 4: ATR Breakeven Stop (36 combinations)

### Post-Processing
- [ ] Aggregate short results
- [ ] Generate short heatmaps
- [ ] Generate short report (matching long report format)
- [ ] Combine long + short reports

---

## Key Parameters Reference

### Fixed ATR Symmetric
```python
ATR_PERIODS = [14, 20, 30, 50]
MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
TIME_LIMIT = 30
```

### Fixed ATR Asymmetric
```python
ATR_PERIODS = [14, 20, 30, 50]
STOP_MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
TARGET_MULTIPLIERS = [3.0, 4.0, 5.0, 6.0]
TIME_LIMIT = 30
```

### ATR Trailing Stop
```python
ATR_PERIOD = 30  # Fixed
MULTIPLIERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
TIME_LIMIT = 20
STOP_ANCHOR = "LOW"  # Use bar LOW, not entry price
```

### ATR Breakeven Stop
```python
ATR_PERIOD = 30  # Fixed
BE_TRIGGERS = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
TARGET_MULTIPLIERS = [4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
TIME_LIMIT = 30
INITIAL_STOP = 2.0  # Fixed 2.0× ATR
```

---

## Performance Benchmarks

### Phase 1: Long Signals
- **Total Signals:** 80,129
- **Total Combinations:** 188
- **Total Backtests:** ~15 Million
- **Processing Time:** ~6 Hours
- **Best Strategy:** ATR Trailing Stop (System Score: $1,392K)

### Phase 2: Short Signals (Expected)
- **Total Signals:** 60,139 (75% of long)
- **Total Combinations:** 188 (same)
- **Total Backtests:** ~11 Million
- **Processing Time:** ~4.5 Hours (estimated)
- **Best Strategy:** TBD

---

## Contact & Support

**GitHub Issues:** https://github.com/alexbernal0/QGSI/issues  
**Research Team:** QGSI Research Team  
**Last Updated:** 2026-01-13

---

**End of Procedure Manual**
