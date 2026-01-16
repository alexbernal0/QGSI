# Transaction Cost Estimates: Dollars to Donuts

**Author:** Alex Bernal, Senior Quantitative Analyst, QGSI  
**Date:** January 16, 2026

## Executive Summary: What Does a Trade Actually Cost?

Based on Interactive Brokers Pro Tiered pricing and S&P 500 stock characteristics, here are the concrete dollar estimates for typical trades:

---

## Quick Answer: Cost Per Trade

### For a **$1,000,000 Trade** (Most Common Reference Size):

| Liquidity Tier | Total Cost | Cost in Basis Points | Examples |
|----------------|------------|---------------------|----------|
| **Mega-Cap (Top 50)** | **$135** | **1.35 bps** | AAPL, MSFT, GOOGL, AMZN, NVDA |
| **Large-Cap (Next 200)** | **$285** | **2.85 bps** | Most S&P 500 stocks |
| **Mid-Large (Bottom 250)** | **$695** | **6.95 bps** | Smaller S&P 500 names |

**Average/Typical S&P 500 Trade: $285 (2.85 bps)**

---

## Detailed Breakdown by Trade Size

### Small Trade: $50,000 (100 shares @ $500)

| Component | Mega-Cap | Large-Cap | Mid-Large |
|-----------|----------|-----------|-----------|
| Commission | $0.35 (min) | $0.35 (min) | $0.35 (min) |
| Exchange/Clearing | $0.30 | $0.30 | $0.30 |
| Spread | $5.00 | $11.00 | $27.50 |
| Market Impact | $0.50 | $2.00 | $6.00 |
| **TOTAL** | **$6.15** | **$13.65** | **$34.15** |
| **Basis Points** | **1.23 bps** | **2.73 bps** | **6.83 bps** |

---

### Medium Trade: $100,000 (500 shares @ $200)

| Component | Mega-Cap | Large-Cap | Mid-Large |
|-----------|----------|-----------|-----------|
| Commission | $1.00 | $1.00 | $1.00 |
| Exchange/Clearing | $1.50 | $1.50 | $1.50 |
| Spread | $10.00 | $22.00 | $55.00 |
| Market Impact | $1.00 | $4.00 | $12.00 |
| **TOTAL** | **$13.50** | **$28.50** | **$69.50** |
| **Basis Points** | **1.35 bps** | **2.85 bps** | **6.95 bps** |

---

### Large Trade: $500,000 (1,000 shares @ $500)

| Component | Mega-Cap | Large-Cap | Mid-Large |
|-----------|----------|-----------|-----------|
| Commission | $2.00 | $2.00 | $2.00 |
| Exchange/Clearing | $3.00 | $3.00 | $3.00 |
| Spread | $50.00 | $110.00 | $275.00 |
| Market Impact | $5.00 | $20.00 | $60.00 |
| **TOTAL** | **$60.00** | **$135.00** | **$340.00** |
| **Basis Points** | **1.20 bps** | **2.70 bps** | **6.80 bps** |

---

### Very Large Trade: $1,000,000 (5,000 shares @ $200)

| Component | Mega-Cap | Large-Cap | Mid-Large |
|-----------|----------|-----------|-----------|
| Commission | $10.00 | $10.00 | $10.00 |
| Exchange/Clearing | $15.00 | $15.00 | $15.00 |
| Spread | $100.00 | $220.00 | $550.00 |
| Market Impact | $10.00 | $40.00 | $120.00 |
| **TOTAL** | **$135.00** | **$285.00** | **$695.00** |
| **Basis Points** | **1.35 bps** | **2.85 bps** | **6.95 bps** |

---

### Institutional Trade: $2,000,000 (10,000 shares @ $200)

| Component | Mega-Cap | Large-Cap | Mid-Large |
|-----------|----------|-----------|-----------|
| Commission | $20.00 | $20.00 | $20.00 |
| Exchange/Clearing | $30.00 | $30.00 | $30.00 |
| Spread | $200.00 | $440.00 | $1,100.00 |
| Market Impact | $20.00 | $80.00 | $240.00 |
| **TOTAL** | **$270.00** | **$570.00** | **$1,390.00** |
| **Basis Points** | **1.35 bps** | **2.85 bps** | **6.95 bps** |

---

## Summary Table: Cost Ranges

| Trade Size | Trade Value | Low End (Mega-Cap) | Mid Range (Large-Cap) | High End (Mid-Large) |
|------------|-------------|-------------------|----------------------|---------------------|
| 100 sh @ $500 | $50,000 | **$6.15** (1.23 bps) | **$13.65** (2.73 bps) | **$34.15** (6.83 bps) |
| 500 sh @ $200 | $100,000 | **$13.50** (1.35 bps) | **$28.50** (2.85 bps) | **$69.50** (6.95 bps) |
| 1,000 sh @ $500 | $500,000 | **$60.00** (1.20 bps) | **$135.00** (2.70 bps) | **$340.00** (6.80 bps) |
| 5,000 sh @ $200 | $1,000,000 | **$135.00** (1.35 bps) | **$285.00** (2.85 bps) | **$695.00** (6.95 bps) |
| 10,000 sh @ $200 | $2,000,000 | **$270.00** (1.35 bps) | **$570.00** (2.85 bps) | **$1,390.00** (6.95 bps) |

---

## Key Insights

### 1. **Typical Cost: $13-$285 per trade**
For most S&P 500 strategies trading $100k-$1M per position, expect **$13-$285 in total transaction costs per trade**.

### 2. **Commission is Now Negligible**
IBKR commission is only **$0.35-$20** per trade. The spread and market impact now dominate total costs.

### 3. **Liquidity Matters More Than Ever**
Trading mega-cap stocks (AAPL, MSFT, GOOGL) costs **3-5x less** than mid-large S&P 500 names for the same dollar amount.

### 4. **Scale Economics**
Larger trades have slightly better per-dollar costs due to the fixed $0.35 minimum commission, but market impact increases with size.

### 5. **Comparison to Generic 20 bps Model**

For a $1,000,000 trade:
- **Generic Model (20 bps):** $2,000 per trade
- **Actual Cost (Large-Cap S&P 500):** $285 per trade
- **Difference:** **7x overestimate**

---

## Practical Recommendations

### For High-Frequency Strategies (400%+ Turnover):
- **Stick to mega-cap stocks** (Top 50-100 S&P 500)
- Expected cost: **$135 per $1M** = **1.35 bps**
- Annual cost drag with 400% turnover: **5.4%**

### For Medium-Frequency Strategies (100-200% Turnover):
- **Trade top 200 S&P 500 stocks** (large-caps)
- Expected cost: **$285 per $1M** = **2.85 bps**
- Annual cost drag with 200% turnover: **5.7%**

### For Lower-Frequency Strategies (< 100% Turnover):
- **Full S&P 500 universe acceptable**
- Expected cost: **$285-$695 per $1M** = **2.85-6.95 bps**
- Annual cost drag with 50% turnover: **1.4-3.5%**

---

## Bottom Line

**For a typical S&P 500 quantitative strategy:**

- **Low-end estimate (mega-cap):** $135 per $1M trade (1.35 bps)
- **Average estimate (large-cap):** $285 per $1M trade (2.85 bps)
- **High-end estimate (mid-large):** $695 per $1M trade (6.95 bps)

**Use $285 (2.85 bps) as your baseline for S&P 500 backtesting.**

This is **7-10x lower** than the commonly cited 20 bps generic assumption, which can transform an apparently unprofitable strategy into a viable one.
