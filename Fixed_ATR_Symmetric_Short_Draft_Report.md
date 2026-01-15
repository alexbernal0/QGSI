# QGSI Stage 4 Phase 2: Fixed ATR Symmetric - SHORT SIGNALS ONLY
## Draft Report - Strategy 1 of 4

**Date:** 2026-01-13  
**Strategy:** Fixed ATR Symmetric  
**Signal Type:** SHORT (Signal = -1)  
**Processing Time:** 10.8 minutes  
**Status:** ✅ COMPLETE

---

## Executive Summary

The Fixed ATR Symmetric strategy was tested on **60,139 SHORT signals** across **400 US equities** using **32 parameter combinations** (4 ATR periods × 8 multipliers). A total of **1,921,480 individual trades** were executed and analyzed.

**CRITICAL FINDING: All 32 configurations produced NEGATIVE net profits**, with profit factors ranging from 0.912 to 0.985 (all below 1.0). This indicates that symmetric stop/target exits are **not profitable for short positions** in this dataset, suggesting either:
1. Market has an upward bias during the test period
2. Short signals require different exit management than long signals
3. Asymmetric exits may be necessary for shorts to achieve profitability

---

## Data Processing Summary

| Metric | Value |
|--------|-------|
| Total SHORT Signals | 60,139 |
| Total Symbols | 400 |
| ATR Periods Tested | 4 (14, 20, 30, 50) |
| Multipliers Tested | 8 (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0) |
| Total Combinations | 32 |
| Total Trades Executed | 1,921,480 |
| Signals Skipped (No ATR) | 106 (0.18%) |
| Signal Coverage | 99.82% |
| Processing Method | Batch processing (10 symbols per batch) |

---

## Top 5 Configurations (Ranked by System Score)

All configurations are ranked by System Score (Net Profit × Profit Factor), with higher (less negative) scores being "better."

| Rank | ATR Period | Multiplier | Total Trades | Net Profit | Profit Factor | Win Rate | System Score |
|------|------------|------------|--------------|------------|---------------|----------|--------------|
| 1 | 30 | 1.5× | 60,033 | **-$84,173** | 0.985 | 49.21% | -$82,927 |
| 2 | 20 | 1.5× | 60,058 | **-$99,694** | 0.984 | 49.33% | -$98,069 |
| 3 | 50 | 2.0× | 60,013 | **-$118,613** | 0.983 | 49.23% | -$116,556 |
| 4 | 50 | 1.5× | 60,013 | **-$127,386** | 0.976 | 48.94% | -$124,312 |
| 5 | 14 | 1.5× | 60,081 | **-$140,685** | 0.979 | 49.34% | -$137,679 |

**Best Configuration:** ATR(30) with 1.5× multiplier  
- Least negative net profit: -$84,173  
- Profit Factor: 0.985 (closest to breakeven)  
- Win Rate: 49.21% (slightly below 50%)  
- Average Win: $189.66  
- Average Loss: $186.70  
- Win/Loss Ratio: 1.016 (winners slightly larger than losers)

---

## Bottom 5 Configurations (Worst Performers)

| Rank | ATR Period | Multiplier | Total Trades | Net Profit | Profit Factor | Win Rate | System Score |
|------|------------|------------|--------------|------------|---------------|----------|--------------|
| 28 | 20 | 4.5× | 60,058 | -$879,700 | 0.930 | 48.71% | -$818,247 |
| 29 | 30 | 5.0× | 60,033 | -$892,544 | 0.929 | 48.68% | -$829,595 |
| 30 | 14 | 4.0× | 60,081 | -$937,142 | 0.925 | 48.73% | -$866,678 |
| 31 | 20 | 5.0× | 60,058 | -$1,034,512 | 0.920 | 48.59% | -$952,190 |
| 32 | 14 | 5.0× | 60,081 | **-$1,166,700** | 0.912 | 48.58% | **-$1,064,355** |

**Worst Configuration:** ATR(14) with 5.0× multiplier  
- Most negative net profit: -$1,166,700  
- Profit Factor: 0.912 (farthest from breakeven)  
- Win Rate: 48.58%  
- Losses compound with wider stops

---

## Key Findings & Analysis

### 1. All Configurations Unprofitable
- **100% of combinations** produced negative net profits
- Profit factors range from 0.912 to 0.985 (all < 1.0)
- This indicates **systematic losses** across all parameter settings
- Even "best" configuration loses $84K on $100K position sizing

### 2. Tighter Stops Perform Better
- **1.5× and 2.0× multipliers** consistently rank higher
- Wider stops (4.0-5.0×) produce significantly larger losses
- Pattern: As multiplier increases, losses compound
- Example: ATR(14) goes from -$141K (1.5×) to -$1.17M (5.0×)

### 3. Win Rates Cluster Around 49%
- All configurations show win rates between 48.6% and 49.3%
- Consistently **below 50%**, indicating slight edge against shorts
- Win/Loss ratios near 1.0 (winners and losers similar size)
- No configuration achieves positive expectancy

### 4. ATR Period Impact is Modest
- ATR(30) and ATR(50) perform slightly better than ATR(14) and ATR(20)
- Longer ATR periods (30, 50) provide more stable volatility measurement
- But even best ATR period cannot overcome negative expectancy

### 5. Market Bias Evident
- Consistent losses across all parameters suggest **upward market bias**
- Short positions systematically underperform
- Compare to LONG signals: Best long config = +$753K, Best short config = -$84K
- **$837K performance gap** between long and short with same strategy

---

## Statistical Analysis

### Performance Distribution

**Net Profit Distribution:**
- Best (least bad): -$84,173
- Worst: -$1,166,700
- Range: $1,082,527
- Median: -$450,000 (approx)

**Profit Factor Distribution:**
- Best: 0.985
- Worst: 0.912
- All below 1.0 (losing money)
- Average: ~0.950

**Win Rate Distribution:**
- Highest: 49.34%
- Lowest: 48.58%
- All below 50%
- Average: ~49.0%

### Trade Count Consistency
- All combinations processed ~60,000 trades
- Minor variations due to ATR initialization (first 30-50 bars)
- ATR(14): 60,081 trades (99.90% coverage)
- ATR(30): 60,033 trades (99.82% coverage)
- ATR(50): 60,013 trades (99.79% coverage)

---

## Exit Reason Analysis

Based on sample analysis of best configuration (ATR 30, 1.5×):

| Exit Reason | Percentage | Interpretation |
|-------------|------------|----------------|
| STOP | ~51% | Majority hit stop loss (price moved against position) |
| TARGET | ~41% | Profit target hit (price moved favorably) |
| TIME | ~8% | Reached 30-bar time limit without hitting stop or target |

**Key Insight:** Even though 41% hit profit targets, the 51% stop exits are large enough to create net losses. This suggests stops are too tight OR targets are too tight relative to market movement for shorts.

---

## Comparison to LONG Signals (Phase 1)

| Metric | LONG (Phase 1) | SHORT (Phase 2) | Difference |
|--------|----------------|-----------------|------------|
| Best Net Profit | +$753,424 | -$84,173 | **-$837,597** |
| Best Profit Factor | 1.047 | 0.985 | -0.062 |
| Best Win Rate | 51.15% | 49.21% | -1.94pp |
| Best Configuration | ATR(20) 5.0× | ATR(30) 1.5× | Opposite ends |
| Total Signals | 80,129 | 60,139 | -19,990 |

**Critical Observations:**
1. **Long signals profitable, short signals not** with same strategy
2. **Opposite optimal parameters:** Longs prefer wide stops (5.0×), shorts prefer tight stops (1.5×)
3. **Win rate gap:** Longs achieve >50%, shorts stay <50%
4. **Market directional bias:** Clear upward bias evident

---

## Strategic Implications

### 1. Symmetric Exits Inadequate for Shorts
The symmetric risk/reward structure (1:1 stop:target ratio) does not work for short positions in this dataset. Potential reasons:
- **Volatility asymmetry:** Downward moves may be sharper but shorter than upward moves
- **Market structure:** Stocks trend up gradually but fall quickly (requires different exit timing)
- **Signal quality:** Short signals may have lower accuracy than long signals

### 2. Recommendations for Remaining Strategies

**Strategy 2: Fixed ATR Asymmetric**
- Test **tighter stops, wider targets** (e.g., 1.0× stop, 3.0× target)
- Hypothesis: Shorts need to cut losses quickly but let winners run longer
- Priority: High (most likely to improve results)

**Strategy 3: ATR Trailing Stop**
- Test **trailing stops that tighten quickly** on favorable moves
- Hypothesis: Lock in gains faster for shorts than longs
- Priority: Medium (may help but uncertain)

**Strategy 4: ATR Breakeven Stop**
- Test **aggressive breakeven triggers** (e.g., 1.5× ATR move → lock breakeven)
- Hypothesis: Protect capital quickly on shorts
- Priority: Medium (defensive approach)

### 3. Consider Abandoning Short Signals
If all 4 strategies fail to produce profitable short configurations:
- **Focus exclusively on long signals** for production trading
- Use short signals only for **hedging** or **market-neutral** strategies
- Investigate **alternative short entry criteria** (current signals may be flawed)

---

## Data Files Generated

| File Name | Description | Size | Rows |
|-----------|-------------|------|------|
| `Fixed_ATR_Symmetric_Short_Performance.csv` | Performance summary for 32 combinations | 3 KB | 32 |
| `Fixed_ATR_Symmetric_Short_All_Trades.parquet` | Detailed trade logs for all combinations | ~150 MB | 1,921,480 |

**Trade Log Columns:**
- TradeNumber, SignalType, EntryTime, EntryPrice, EntryBar
- ExitTime, ExitPrice, ExitBar, StopLoss, ProfitTarget
- ExitReason, BarsInTrade, NetProfit, NetProfitPct
- ATR, ATRPeriod, Multiplier, Symbol, StrategyName

---

## Next Steps

### Immediate Actions
1. ✅ Review this draft report for accuracy
2. ⏳ Proceed to **Strategy 2: Fixed ATR Asymmetric** (112 combinations)
3. ⏳ Test asymmetric stop/target ratios optimized for shorts
4. ⏳ Compare results to determine if shorts can be made profitable

### Future Analysis
- **Correlation analysis:** Are short losses correlated with specific sectors or market conditions?
- **Time period analysis:** Do shorts perform better in bear markets vs bull markets?
- **Signal quality review:** Are short entry signals fundamentally flawed?
- **Hybrid approach:** Combine best long + best short strategies for market-neutral portfolio

---

## Conclusion

The Fixed ATR Symmetric strategy, which performed moderately well on long signals (+$753K best case), **completely fails on short signals** (-$84K best case, -$1.17M worst case). All 32 parameter combinations produced negative returns with profit factors below 1.0.

The consistent underperformance across all parameters suggests a **systematic issue** rather than a parameter optimization problem. Tighter stops (1.5-2.0×) minimize losses but do not achieve profitability.

**Recommendation:** Proceed with remaining 3 strategies (Asymmetric, Trailing Stop, Breakeven) to determine if alternative exit logic can make short signals profitable. If all strategies fail, consider abandoning short signals or fundamentally revising short entry criteria.

---

**Report Status:** DRAFT - Awaiting Review  
**Next Strategy:** Fixed ATR Asymmetric (112 combinations, ~90 minutes processing time)
