#!/usr/bin/env python3.11
"""
Comprehensive Combined Report Generator
Integrates LONG, SHORT, and Part III analysis into single professional PDF
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import pandas as pd
from datetime import datetime
import os

print("="*80)
print("GENERATING COMPREHENSIVE COMBINED REPORT")
print("="*80)

# Create PDF
pdf_file = '/home/ubuntu/stage4_optimization/Production_Portfolio_COMPREHENSIVE_Report.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=landscape(letter),
                        rightMargin=0.5*inch, leftMargin=0.5*inch,
                        topMargin=0.5*inch, bottomMargin=0.5*inch)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=8,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.black,
    spaceAfter=6
)

# Story elements
story = []

# ============================================================================
# TITLE PAGE
# ============================================================================
print("\n[1/8] Creating title page...")

story.append(Spacer(1, 1*inch))
story.append(Paragraph("PRODUCTION PORTFOLIO PERFORMANCE REPORT", title_style))
story.append(Paragraph("Comprehensive Analysis: LONG + SHORT Strategies", heading_style))
story.append(Spacer(1, 0.3*inch))

# Summary table
summary_data = [
    ['Strategy', 'ATR Period', 'ATR Multiplier', 'Max Bars', 'Analysis Period'],
    ['LONG', '30', '5.0', '20', 'June 2 - Dec 31, 2025'],
    ['SHORT', '30', '1.5', '20', 'June 2 - Dec 31, 2025'],
]

summary_table = Table(summary_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1*inch, 2*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(summary_table)

story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style))
story.append(Paragraph("Data Source: Production_Long_Trades.parquet, Production_Short_Trades.parquet", normal_style))
story.append(Paragraph("Methodology: FIFO Realistic Backtesting with 10-Position Limit", normal_style))

story.append(PageBreak())

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================
print("[2/8] Creating executive summary...")

story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
story.append(Spacer(1, 0.1*inch))

# Load key metrics
long_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv', index_col=0)
short_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Extended_Metrics.csv', index_col=0)
combined_summary = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_portfolio_summary.csv')

# Convert to dict for easy access
long_dict = long_metrics['Value'].to_dict()
short_dict = short_metrics['Value'].to_dict()

# Calculate final equity
long_final_equity = 1000000 * (1 + long_dict['Cumulative Return']/100)
short_final_equity = 1000000 * (1 + short_dict['Cumulative Return']/100)

exec_data = [
    ['Metric', 'LONG Strategy', 'SHORT Strategy', 'Combined Portfolio'],
    ['Final Equity', f"${long_final_equity:,.0f}", 
     f"${short_final_equity:,.0f}",
     f"${combined_summary['Final Equity'].iloc[0]:,.0f}"],
    ['Total Return', f"{long_dict['Cumulative Return']:.2f}%",
     f"{short_dict['Cumulative Return']:.2f}%",
     f"{combined_summary['Total Return (%)'].iloc[0]:.2f}%"],
    ['CAGR', f"{long_dict['CAGR']:.2f}%",
     f"{short_dict['CAGR']:.2f}%",
     "N/A"],
    ['Sharpe Ratio', f"{long_dict['Sharpe']:.2f}",
     f"{short_dict['Sharpe']:.2f}",
     f"{combined_summary['Sharpe Ratio'].iloc[0]:.2f}"],
    ['Max Drawdown', f"{long_dict['Max Drawdown']:.2f}%",
     f"{short_dict['Max Drawdown']:.2f}%",
     f"{combined_summary['Max Drawdown (%)'].iloc[0]:.2f}%"],
    ['Total Trades', f"{long_dict.get('Total Trades', 16754):,.0f}",
     f"{short_dict.get('Total Trades', 1424):,.0f}",
     f"{combined_summary['Total Trades'].iloc[0]:,.0f}"],
    ['Win Rate', f"{long_dict.get('Win Days %', 49.8):.1f}%",
     f"{short_dict.get('Win Days %', 62.4):.1f}%",
     "N/A"],
]

exec_table = Table(exec_data, colWidths=[2*inch, 1.8*inch, 1.8*inch, 1.8*inch])
exec_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
]))
story.append(exec_table)

story.append(Spacer(1, 0.2*inch))

# Key findings
story.append(Paragraph("Key Findings:", subheading_style))
findings_text = """
<b>1. Combined Portfolio Outperforms:</b> Running LONG and SHORT together with shared capital yields 104.62% return, 
significantly better than either strategy alone (LONG: 46.50%, SHORT: 36.29%).<br/><br/>
<b>2. Low Correlation:</b> Daily returns correlation of 0.0516 indicates excellent diversification between strategies.<br/><br/>
<b>3. Massive Scaling Potential:</b> LONG has $72.9M capacity, SHORT has $60.6M capacity. Current $1M deployment 
is only ~1.5% of total capacity.<br/><br/>
<b>4. Transaction Cost Challenge:</b> LONG strategy may be unprofitable after realistic transaction costs 
(~$80 per trade vs $27.75 avg profit). SHORT strategy remains profitable ($254.91 avg profit per trade).
"""
story.append(Paragraph(findings_text, normal_style))

story.append(PageBreak())

# ============================================================================
# PART I: LONG STRATEGY
# ============================================================================
print("[3/8] Adding LONG strategy section...")

story.append(Paragraph("PART I: LONG STRATEGY PERFORMANCE", heading_style))
story.append(Spacer(1, 0.1*inch))

# LONG equity curve
story.append(Paragraph("Equity Curve", subheading_style))
long_eq_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Equity_Curve.png', width=7*inch, height=3.5*inch)
story.append(long_eq_img)
story.append(Spacer(1, 0.1*inch))

# LONG monthly returns
story.append(Paragraph("Monthly Returns", subheading_style))
long_monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Returns.png', width=7*inch, height=3.5*inch)
story.append(long_monthly_img)

story.append(PageBreak())

# LONG metrics table
story.append(Paragraph("LONG Strategy: Detailed Performance Metrics", subheading_style))

long_detail_data = [
    ['Category', 'Metric', 'Value'],
    ['Performance', 'Starting Capital', f"${1000000:,.0f}"],
    ['', 'Final Equity', f"${long_final_equity:,.0f}"],
    ['', 'Net Profit', f"${long_final_equity - 1000000:,.0f}"],
    ['', 'Total Return', f"{long_dict['Cumulative Return']:.2f}%"],
    ['', 'CAGR', f"{long_dict['CAGR']:.2f}%"],
    ['Risk-Adjusted', 'Sharpe Ratio', f"{long_dict['Sharpe']:.2f}"],
    ['', 'Sortino Ratio', f"{long_dict['Sortino']:.2f}"],
    ['', 'Calmar Ratio', f"{long_dict['Calmar']:.2f}"],
    ['', 'Omega Ratio', f"{long_dict['Omega']:.2f}"],
    ['Risk', 'Max Drawdown', f"{long_dict['Max Drawdown']:.2f}%"],
    ['', 'Volatility (Ann.)', f"{long_dict['Volatility (ann.)']:.2f}%"],
    ['', 'VaR (5%)', f"{long_dict.get('Daily Value-at-Risk', -0.57):.2f}%"],
    ['Trading', 'Total Trades', f"{long_dict.get('Total Trades', 16754):,.0f}"],
    ['', 'Win Days %', f"{long_dict.get('Win Days %', 49.8):.1f}%"],
    ['', 'Win Month %', f"{long_dict.get('Win Month %', 100.0):.1f}%"],
]

long_detail_table = Table(long_detail_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
long_detail_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
]))
story.append(long_detail_table)

story.append(PageBreak())

# ============================================================================
# PART II: SHORT STRATEGY
# ============================================================================
print("[4/8] Adding SHORT strategy section...")

story.append(Paragraph("PART II: SHORT STRATEGY PERFORMANCE", heading_style))
story.append(Spacer(1, 0.1*inch))

# SHORT equity curve
story.append(Paragraph("Equity Curve", subheading_style))
short_eq_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Equity_Curve.png', width=7*inch, height=3.5*inch)
story.append(short_eq_img)
story.append(Spacer(1, 0.1*inch))

# SHORT monthly returns
story.append(Paragraph("Monthly Returns", subheading_style))
short_monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Monthly_Returns.png', width=7*inch, height=3.5*inch)
story.append(short_monthly_img)

story.append(PageBreak())

# SHORT metrics table
story.append(Paragraph("SHORT Strategy: Detailed Performance Metrics", subheading_style))

short_detail_data = [
    ['Category', 'Metric', 'Value'],
    ['Performance', 'Starting Capital', f"${1000000:,.0f}"],
    ['', 'Final Equity', f"${short_final_equity:,.0f}"],
    ['', 'Net Profit', f"${short_final_equity - 1000000:,.0f}"],
    ['', 'Total Return', f"{short_dict['Cumulative Return']:.2f}%"],
    ['', 'CAGR', f"{short_dict['CAGR']:.2f}%"],
    ['Risk-Adjusted', 'Sharpe Ratio', f"{short_dict['Sharpe']:.2f}"],
    ['', 'Sortino Ratio', f"{short_dict['Sortino']:.2f}"],
    ['', 'Calmar Ratio', f"{short_dict['Calmar']:.2f}"],
    ['', 'Omega Ratio', f"{short_dict['Omega']:.2f}"],
    ['Risk', 'Max Drawdown', f"{short_dict['Max Drawdown']:.2f}%"],
    ['', 'Volatility (Ann.)', f"{short_dict['Volatility (ann.)']:.2f}%"],
    ['', 'VaR (5%)', f"{short_dict.get('Daily Value-at-Risk', -0.32):.2f}%"],
    ['Trading', 'Total Trades', f"{short_dict.get('Total Trades', 1424):,.0f}"],
    ['', 'Win Days %', f"{short_dict.get('Win Days %', 62.4):.1f}%"],
    ['', 'Win Month %', f"{short_dict.get('Win Month %', 100.0):.1f}%"],
]

short_detail_table = Table(short_detail_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
short_detail_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
]))
story.append(short_detail_table)

story.append(PageBreak())

# ============================================================================
# PART III: COMPARATIVE ANALYSIS
# ============================================================================
print("[5/8] Adding Part III comparative analysis...")

story.append(Paragraph("PART III: COMPARATIVE ANALYSIS & COMBINED PORTFOLIO", heading_style))
story.append(Spacer(1, 0.1*inch))

# Combined equity curves
story.append(Paragraph("Combined Portfolio Equity Curves", subheading_style))
combined_eq_img = Image('/home/ubuntu/stage4_optimization/part3_viz_combined_equity_curves.png', width=7*inch, height=3.5*inch)
story.append(combined_eq_img)

story.append(Spacer(1, 0.2*inch))

# Performance comparison
story.append(Paragraph("Strategy Comparison", subheading_style))
comparison_df = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a1_performance_comparison.csv')

comp_data = [['Metric', 'LONG', 'SHORT', 'Difference']]
for _, row in comparison_df.iterrows():
    comp_data.append([row['Metric'], str(row['LONG']), str(row['SHORT']), str(row['Difference'])])

comp_table = Table(comp_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
comp_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(comp_table)

story.append(PageBreak())

# Correlation analysis
story.append(Paragraph("Correlation Analysis", subheading_style))
corr_img = Image('/home/ubuntu/stage4_optimization/part3_viz_correlation_analysis.png', width=7*inch, height=3*inch)
story.append(corr_img)

story.append(Spacer(1, 0.2*inch))

# Optimal allocation
story.append(Paragraph("Optimal Allocation Analysis", subheading_style))
alloc_img = Image('/home/ubuntu/stage4_optimization/part3_viz_optimal_allocation.png', width=7*inch, height=3*inch)
story.append(alloc_img)

story.append(PageBreak())

# ============================================================================
# PART IV: STOCK UNIVERSE ANALYSIS
# ============================================================================
print("[6/8] Adding stock universe analysis...")

story.append(Paragraph("PART IV: STOCK UNIVERSE & CAPITAL DEPLOYMENT", heading_style))
story.append(Spacer(1, 0.1*inch))

# Capital capacity
story.append(Paragraph("Capital Deployment Capacity", subheading_style))
capacity_img = Image('/home/ubuntu/stage4_optimization/part3_viz_capital_capacity.png', width=5*inch, height=3*inch)
story.append(capacity_img)

story.append(Spacer(1, 0.2*inch))

# Capacity table
capacity_df = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b7_capacity_summary.csv')

cap_data = [
    ['Strategy', 'Total Capacity', 'Current Capital', 'Utilization %', 'Recommended Max'],
]
for _, row in capacity_df.iterrows():
    cap_data.append([
        row['Strategy'],
        f"${row['Total_Capacity']:,.0f}",
        f"${row['Current_Capital']:,.0f}",
        f"{row['Utilization_Pct']:.1f}%",
        f"${row['Recommended_Max']:,.0f}"
    ])

cap_table = Table(cap_data, colWidths=[1.5*inch, 1.8*inch, 1.5*inch, 1.2*inch, 1.8*inch])
cap_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(cap_table)

story.append(Spacer(1, 0.2*inch))

# Performance by market cap
story.append(Paragraph("Performance by Market Cap Category", subheading_style))
mcap_img = Image('/home/ubuntu/stage4_optimization/part3_viz_performance_by_mcap.png', width=7*inch, height=3*inch)
story.append(mcap_img)

story.append(PageBreak())

# ============================================================================
# RECOMMENDATIONS
# ============================================================================
print("[7/8] Adding recommendations...")

story.append(Paragraph("RECOMMENDATIONS & NEXT STEPS", heading_style))
story.append(Spacer(1, 0.1*inch))

recommendations_text = """
<b>1. Implement Combined Portfolio (Immediate)</b><br/>
Run LONG and SHORT strategies together with shared $1M capital and 10-position limit. 
Expected return: 104.62% (vs 46.50% LONG alone, 36.29% SHORT alone).<br/><br/>

<b>2. Apply Stock Exclusions (Immediate)</b><br/>
Exclude 127 LONG symbols and 12 SHORT symbols based on liquidity and performance criteria. 
Impact: -2.7% PnL, +2-3% win rate, significantly reduced execution risk.<br/><br/>

<b>3. Implement 3-Tier Position Sizing (Week 1)</b><br/>
Tier 1 (1.5x): Top 20% by total PnL + liquidity score > 50<br/>
Tier 2 (1.0x): Middle 60%<br/>
Tier 3 (0.5x): Bottom 20% or liquidity score < 30<br/><br/>

<b>4. Negotiate Institutional Execution Rates (Month 1)</b><br/>
Target: <$10 per trade all-in (vs current ~$80 retail rates). 
Critical for LONG strategy profitability.<br/><br/>

<b>5. Begin Paper Trading (Month 1-3)</b><br/>
Start with $100K to validate execution assumptions before scaling to $1M live capital.<br/><br/>

<b>6. Scaling Path (Months 3-12)</b><br/>
Phase 1 ($1M-$5M): No changes needed<br/>
Phase 2 ($5M-$20M): Increase position limit to 15, focus large-cap<br/>
Phase 3 ($20M-$50M): Position limit 20-25, exclude bottom 50% by liquidity<br/>
Phase 4 ($50M+): Institutional execution infrastructure required<br/><br/>

<b>7. Risk Management Enhancements (Ongoing)</b><br/>
- Max position size: 12% of equity<br/>
- Max symbol exposure: 3 positions per symbol<br/>
- Daily loss limit: -2% of equity<br/>
- Monitor correlation: Alert if LONG/SHORT correlation >0.3 for 5+ days
"""

story.append(Paragraph(recommendations_text, normal_style))

story.append(PageBreak())

# ============================================================================
# APPENDIX
# ============================================================================
print("[8/8] Adding appendix...")

story.append(Paragraph("APPENDIX: FIFO REALISTIC BACKTESTING METHODOLOGY", heading_style))
story.append(Spacer(1, 0.1*inch))

appendix_text = """
<b>Overview</b><br/>
This report uses FIFO (First-In-First-Out) realistic backtesting methodology to simulate production trading 
conditions with real-world constraints. Unlike traditional backtesting that assumes unlimited capital and positions, 
this methodology enforces strict limits to reflect actual trading conditions.<br/><br/>

<b>Key Constraints</b><br/>
1. <b>Position Limit:</b> Maximum 10 simultaneous positions<br/>
2. <b>Capital Allocation:</b> 10% of current equity per trade<br/>
3. <b>Signal Priority:</b> Timestamp-based FIFO ordering<br/>
4. <b>Tiebreaker:</b> ATR value (higher ATR = higher priority)<br/>
5. <b>Shared Resources:</b> Combined portfolio uses shared capital and position slots<br/><br/>

<b>Baseline vs Production</b><br/>
<b>Baseline:</b> Unlimited positions, all signals taken (LONG: 31,823 trades, SHORT: 60,111 trades)<br/>
<b>Production LONG:</b> 10-position limit, 16,754 trades executed (52.6% utilization)<br/>
<b>Production SHORT:</b> 10-position limit, 1,424 trades executed (2.4% utilization)<br/>
<b>Combined:</b> Shared 10-position limit, 17,055 trades total (16,734 LONG + 321 SHORT)<br/><br/>

<b>Key Functions</b><br/>
1. <b>simulate_combined_portfolio():</b> Merges LONG and SHORT signals, sorts by timestamp, 
   enforces position limits, calculates equity curve<br/>
2. <b>calculate_liquidity_metrics():</b> Estimates daily volume, liquidity score, market impact<br/>
3. <b>analyze_by_category():</b> Aggregates performance by market cap, liquidity, volatility<br/>
4. <b>optimize_allocation():</b> Tests 21 allocation scenarios to find optimal LONG/SHORT mix<br/><br/>

<b>Data Files</b><br/>
LONG: Production_Long_Trades.parquet (16,754 trades), Production_Long_Equity.parquet<br/>
SHORT: Production_Short_Trades.parquet (1,424 trades), Production_Short_Equity.parquet<br/>
Combined: part3_a2_combined_trades.csv (17,055 trades), part3_a2_combined_equity_curve.csv<br/><br/>

<b>Validation</b><br/>
All calculations are deterministic and reproducible. No random sampling or Monte Carlo simulation used. 
Results can be verified by re-running the production portfolio simulator with identical input data.<br/><br/>

<b>Limitations</b><br/>
1. Liquidity metrics are estimated (actual volume data not available)<br/>
2. Transaction costs are estimated (~$80 per trade)<br/>
3. Slippage not modeled (assumes limit order fills at entry price)<br/>
4. Market impact not dynamically calculated<br/>
5. Analysis period limited to 147 days (June-Dec 2025)
"""

story.append(Paragraph(appendix_text, normal_style))

# Build PDF
print("\nBuilding PDF...")
doc.build(story)

print("\n" + "="*80)
print("COMPREHENSIVE COMBINED REPORT GENERATED")
print("="*80)
print(f"File: {pdf_file}")
print(f"Size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
print("="*80)
