#!/usr/bin/env python3.11
"""
Comprehensive Combined Report Generator V2
Includes complete Part III data exploration section
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
print("GENERATING COMPREHENSIVE COMBINED REPORT V2")
print("WITH COMPLETE PART III DATA EXPLORATION")
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

small_style = ParagraphStyle(
    'CustomSmall',
    parent=styles['Normal'],
    fontSize=7,
    textColor=colors.black,
    spaceAfter=4
)

# Story elements
story = []

# Helper function to create tables
def create_table(data, col_widths):
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
    ]))
    return table

print("\n[1/12] Creating title page...")
# Title page (same as before)
story.append(Spacer(1, 1*inch))
story.append(Paragraph("PRODUCTION PORTFOLIO PERFORMANCE REPORT", title_style))
story.append(Paragraph("Comprehensive Analysis: LONG + SHORT Strategies", heading_style))
story.append(Spacer(1, 0.3*inch))

summary_data = [
    ['Strategy', 'ATR Period', 'ATR Multiplier', 'Max Bars', 'Analysis Period'],
    ['LONG', '30', '5.0', '20', 'June 2 - Dec 31, 2025'],
    ['SHORT', '30', '1.5', '20', 'June 2 - Dec 31, 2025'],
]

summary_table = create_table(summary_data, [1.5*inch, 1*inch, 1.2*inch, 1*inch, 2*inch])
story.append(summary_table)
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", normal_style))
story.append(Paragraph("Data Source: Production_Long_Trades.parquet, Production_Short_Trades.parquet", normal_style))
story.append(Paragraph("Methodology: FIFO Realistic Backtesting with 10-Position Limit", normal_style))
story.append(PageBreak())

print("[2/12] Creating executive summary...")
# Executive summary (abbreviated for space)
story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
story.append(Spacer(1, 0.1*inch))

long_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv', index_col=0)
short_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Extended_Metrics.csv', index_col=0)
combined_summary = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a2_combined_portfolio_summary.csv')

long_dict = long_metrics['Value'].to_dict()
short_dict = short_metrics['Value'].to_dict()
long_final_equity = 1000000 * (1 + long_dict['Cumulative Return']/100)
short_final_equity = 1000000 * (1 + short_dict['Cumulative Return']/100)

exec_data = [
    ['Metric', 'LONG', 'SHORT', 'Combined'],
    ['Final Equity', f"${long_final_equity:,.0f}", f"${short_final_equity:,.0f}", f"${combined_summary['Final Equity'].iloc[0]:,.0f}"],
    ['Total Return', f"{long_dict['Cumulative Return']:.2f}%", f"{short_dict['Cumulative Return']:.2f}%", f"{combined_summary['Total Return (%)'].iloc[0]:.2f}%"],
    ['Sharpe Ratio', f"{long_dict['Sharpe']:.2f}", f"{short_dict['Sharpe']:.2f}", f"{combined_summary['Sharpe Ratio'].iloc[0]:.2f}"],
    ['Max Drawdown', f"{long_dict['Max Drawdown']:.2f}%", f"{short_dict['Max Drawdown']:.2f}%", f"{combined_summary['Max Drawdown (%)'].iloc[0]:.2f}%"],
]

exec_table = create_table(exec_data, [2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
story.append(exec_table)
story.append(PageBreak())

print("[3/12] Adding LONG strategy (abbreviated)...")
# LONG strategy (abbreviated - just key chart and metrics)
story.append(Paragraph("PART I: LONG STRATEGY PERFORMANCE", heading_style))
long_eq_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Equity_Curve.png', width=7*inch, height=3*inch)
story.append(long_eq_img)
story.append(Paragraph(f"Final Equity: ${long_final_equity:,.0f} | Return: {long_dict['Cumulative Return']:.2f}% | Sharpe: {long_dict['Sharpe']:.2f} | Max DD: {long_dict['Max Drawdown']:.2f}%", normal_style))
story.append(PageBreak())

print("[4/12] Adding SHORT strategy (abbreviated)...")
# SHORT strategy (abbreviated)
story.append(Paragraph("PART II: SHORT STRATEGY PERFORMANCE", heading_style))
short_eq_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Equity_Curve.png', width=7*inch, height=3*inch)
story.append(short_eq_img)
story.append(Paragraph(f"Final Equity: ${short_final_equity:,.0f} | Return: {short_dict['Cumulative Return']:.2f}% | Sharpe: {short_dict['Sharpe']:.2f} | Max DD: {short_dict['Max Drawdown']:.2f}%", normal_style))
story.append(PageBreak())

print("[5/12] Adding Part III Section A: Strategy Comparison...")
# PART III: COMPARATIVE ANALYSIS
story.append(Paragraph("PART III: COMPARATIVE ANALYSIS & DATA EXPLORATION", heading_style))
story.append(Paragraph("Section A: Strategy Comparison", subheading_style))

# Combined equity curves
combined_eq_img = Image('/home/ubuntu/stage4_optimization/part3_viz_combined_equity_curves.png', width=7*inch, height=3*inch)
story.append(combined_eq_img)
story.append(Spacer(1, 0.1*inch))

# Correlation analysis
corr_img = Image('/home/ubuntu/stage4_optimization/part3_viz_correlation_analysis.png', width=7*inch, height=2.5*inch)
story.append(corr_img)
story.append(PageBreak())

# Optimal allocation
story.append(Paragraph("Optimal Allocation Analysis", subheading_style))
alloc_img = Image('/home/ubuntu/stage4_optimization/part3_viz_optimal_allocation.png', width=7*inch, height=3*inch)
story.append(alloc_img)

# Symbol overlap
story.append(Spacer(1, 0.1*inch))
symbol_summary = pd.read_csv('/home/ubuntu/stage4_optimization/part3_a5_symbol_summary.csv')
symbol_data = [['Metric', 'Count']]
for col in symbol_summary.columns:
    symbol_data.append([col, str(symbol_summary[col].iloc[0])])
symbol_table = create_table(symbol_data, [3*inch, 2*inch])
story.append(symbol_table)
story.append(PageBreak())

print("[6/12] Adding Part III Section B: Stock Universe Overview...")
# SECTION B: STOCK UNIVERSE & CHARACTERISTICS
story.append(Paragraph("Section B: Stock Universe & Trading Characteristics", subheading_style))

# Universe overview
universe_df = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b1_universe_overview.csv')
univ_data = [['Metric', 'Value']]
univ_data.append(['Total Unique Symbols', str(universe_df['Total Unique Symbols'].iloc[0])])
univ_data.append(['LONG Symbols', str(universe_df['LONG Symbols'].iloc[0])])
univ_data.append(['SHORT Symbols', str(universe_df['SHORT Symbols'].iloc[0])])
univ_data.append(['Avg Symbols/Day (LONG)', f"{universe_df['Avg Symbols per Day (LONG)'].iloc[0]:.1f}"])
univ_data.append(['Avg Symbols/Day (SHORT)', f"{universe_df['Avg Symbols per Day (SHORT)'].iloc[0]:.1f}"])
univ_table = create_table(univ_data, [3*inch, 2*inch])
story.append(univ_table)
story.append(PageBreak())

print("[7/12] Adding Performance by Market Cap...")
# Performance by Market Cap
story.append(Paragraph("Performance by Market Cap Category", subheading_style))
mcap_img = Image('/home/ubuntu/stage4_optimization/part3_viz_performance_by_mcap.png', width=7*inch, height=3*inch)
story.append(mcap_img)
story.append(Spacer(1, 0.1*inch))

# Market cap tables
long_mcap = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b3_long_performance_by_mcap.csv')
short_mcap = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b3_short_performance_by_mcap.csv')

mcap_data = [['Market Cap', 'LONG Symbols', 'LONG PnL', 'SHORT Symbols', 'SHORT PnL']]
for i in range(max(len(long_mcap), len(short_mcap))):
    long_cat = long_mcap.iloc[i]['Market_Cap_Tier'] if i < len(long_mcap) else ''
    long_sym = str(int(long_mcap.iloc[i]['Num_Symbols'])) if i < len(long_mcap) else ''
    long_pnl = f"${long_mcap.iloc[i]['Total_PnL']:,.0f}" if i < len(long_mcap) else ''
    short_cat = short_mcap.iloc[i]['Market_Cap_Tier'] if i < len(short_mcap) else ''
    short_sym = str(int(short_mcap.iloc[i]['Num_Symbols'])) if i < len(short_mcap) else ''
    short_pnl = f"${short_mcap.iloc[i]['Total_PnL']:,.0f}" if i < len(short_mcap) else ''
    
    if i == 0:
        mcap_data.append([long_cat, long_sym, long_pnl, short_sym, short_pnl])
    else:
        mcap_data.append(['', long_sym, long_pnl, short_sym, short_pnl])

mcap_table = create_table(mcap_data, [1.5*inch, 1*inch, 1.2*inch, 1*inch, 1.2*inch])
story.append(mcap_table)
story.append(PageBreak())

print("[8/12] Adding Performance by Liquidity...")
# Performance by Liquidity
story.append(Paragraph("Performance by Liquidity Tier", subheading_style))
liq_img = Image('/home/ubuntu/stage4_optimization/part3_viz_performance_by_liquidity.png', width=7*inch, height=3*inch)
story.append(liq_img)
story.append(Spacer(1, 0.1*inch))

long_liq = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b4_long_performance_by_liquidity.csv')
short_liq = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b4_short_performance_by_liquidity.csv')

liq_data = [['Liquidity Tier', 'LONG Symbols', 'LONG PnL', 'SHORT Symbols', 'SHORT PnL']]
for i in range(max(len(long_liq), len(short_liq))):
    long_tier = long_liq.iloc[i]['Liquidity_Tier'] if i < len(long_liq) else ''
    long_sym = str(int(long_liq.iloc[i]['Num_Symbols'])) if i < len(long_liq) else ''
    long_pnl = f"${long_liq.iloc[i]['Total_PnL']:,.0f}" if i < len(long_liq) else ''
    short_tier = short_liq.iloc[i]['Liquidity_Tier'] if i < len(short_liq) else ''
    short_sym = str(int(short_liq.iloc[i]['Num_Symbols'])) if i < len(short_liq) else ''
    short_pnl = f"${short_liq.iloc[i]['Total_PnL']:,.0f}" if i < len(short_liq) else ''
    
    if i == 0:
        liq_data.append([long_tier, long_sym, long_pnl, short_sym, short_pnl])
    else:
        liq_data.append(['', long_sym, long_pnl, short_sym, short_pnl])

liq_table = create_table(liq_data, [1.5*inch, 1*inch, 1.2*inch, 1*inch, 1.2*inch])
story.append(liq_table)
story.append(PageBreak())

print("[9/12] Adding Performance by Volatility...")
# Performance by Volatility
story.append(Paragraph("Performance by Volatility Quintile", subheading_style))
vol_img = Image('/home/ubuntu/stage4_optimization/part3_viz_performance_by_volatility.png', width=7*inch, height=3*inch)
story.append(vol_img)
story.append(Spacer(1, 0.1*inch))

long_vol = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b5_long_performance_by_volatility.csv')
short_vol = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b5_short_performance_by_volatility.csv')

vol_data = [['Volatility Q', 'LONG Symbols', 'LONG PnL', 'SHORT Symbols', 'SHORT PnL']]
for i in range(max(len(long_vol), len(short_vol))):
    long_q = f"Q{int(long_vol.iloc[i]['Volatility_Quintile'])+1}" if i < len(long_vol) else ''
    long_sym = str(int(long_vol.iloc[i]['Num_Symbols'])) if i < len(long_vol) else ''
    long_pnl = f"${long_vol.iloc[i]['Total_PnL']:,.0f}" if i < len(long_vol) else ''
    short_q = f"Q{int(short_vol.iloc[i]['Volatility_Quintile'])+1}" if i < len(short_vol) else ''
    short_sym = str(int(short_vol.iloc[i]['Num_Symbols'])) if i < len(short_vol) else ''
    short_pnl = f"${short_vol.iloc[i]['Total_PnL']:,.0f}" if i < len(short_vol) else ''
    
    vol_data.append([long_q, long_sym, long_pnl, short_sym, short_pnl])

vol_table = create_table(vol_data, [1.5*inch, 1*inch, 1.2*inch, 1*inch, 1.2*inch])
story.append(vol_table)
story.append(PageBreak())

print("[10/12] Adding Top vs Bottom Performers...")
# Top vs Bottom Performers
story.append(Paragraph("Top 20 vs Bottom 20 Performers Comparison", subheading_style))
topbot_img = Image('/home/ubuntu/stage4_optimization/part3_viz_top_vs_bottom_comparison.png', width=7*inch, height=3*inch)
story.append(topbot_img)
story.append(Spacer(1, 0.1*inch))

# Top 20 LONG
long_top20 = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b6_long_top20_performers.csv')
top20_data = [['Rank', 'Symbol', 'PnL', 'Trades', 'Liq Score']]
for i, row in long_top20.head(10).iterrows():
    top20_data.append([
        str(i+1),
        row['Symbol'],
        f"${row['Total_PnL']:,.0f}",
        str(int(row['Trade_Count'])),
        f"{row['Liquidity_Score']:.0f}"
    ])

top20_table = create_table(top20_data, [0.6*inch, 0.8*inch, 1*inch, 0.7*inch, 0.9*inch])
story.append(Paragraph("Top 10 LONG Symbols", small_style))
story.append(top20_table)
story.append(PageBreak())

print("[11/12] Adding Capital Deployment Capacity...")
# Capital Deployment Capacity
story.append(Paragraph("Capital Deployment Capacity Analysis", subheading_style))
capacity_img = Image('/home/ubuntu/stage4_optimization/part3_viz_capital_capacity.png', width=6*inch, height=3*inch)
story.append(capacity_img)
story.append(Spacer(1, 0.1*inch))

capacity_df = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b7_capacity_summary.csv')
cap_data = [['Strategy', 'Total Capacity', 'Current', 'Utilization', 'Recommended Max']]
for _, row in capacity_df.iterrows():
    cap_data.append([
        row['Strategy'],
        f"${row['Total_Capacity']:,.0f}",
        f"${row['Current_Capital']:,.0f}",
        f"{row['Utilization_Pct']:.1f}%",
        f"${row['Recommended_Max']:,.0f}"
    ])

cap_table = create_table(cap_data, [1.2*inch, 1.5*inch, 1.2*inch, 1*inch, 1.5*inch])
story.append(cap_table)
story.append(Spacer(1, 0.2*inch))

# Exclusion recommendations
story.append(Paragraph("Stock Exclusion Recommendations", subheading_style))
long_excl_impact = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b8_long_exclusion_impact.csv')
short_excl_impact = pd.read_csv('/home/ubuntu/stage4_optimization/part3_b8_short_exclusion_impact.csv')

excl_data = [['Strategy', 'Symbols to Exclude', 'Trades Impact', 'PnL Impact']]
excl_data.append([
    'LONG',
    str(int(long_excl_impact[long_excl_impact['Category']=='Excluded']['Num_Symbols'].iloc[0])),
    f"{long_excl_impact[long_excl_impact['Category']=='Excluded']['Trade_Pct'].iloc[0]:.1f}%",
    f"{long_excl_impact[long_excl_impact['Category']=='Excluded']['PnL_Pct'].iloc[0]:.1f}%"
])
excl_data.append([
    'SHORT',
    str(int(short_excl_impact[short_excl_impact['Category']=='Excluded']['Num_Symbols'].iloc[0])),
    f"{short_excl_impact[short_excl_impact['Category']=='Excluded']['Trade_Pct'].iloc[0]:.1f}%",
    f"{short_excl_impact[short_excl_impact['Category']=='Excluded']['PnL_Pct'].iloc[0]:.1f}%"
])

excl_table = create_table(excl_data, [1.5*inch, 1.8*inch, 1.5*inch, 1.5*inch])
story.append(excl_table)
story.append(PageBreak())

print("[12/12] Adding Recommendations and Appendix...")
# RECOMMENDATIONS
story.append(Paragraph("RECOMMENDATIONS & NEXT STEPS", heading_style))
recommendations_text = """
<b>1. Implement Combined Portfolio:</b> Run LONG + SHORT with shared $1M capital. Expected return: 104.62%.<br/>
<b>2. Apply Stock Exclusions:</b> Exclude 127 LONG and 12 SHORT symbols. Impact: -2.7% PnL, improved risk metrics.<br/>
<b>3. Implement 3-Tier Position Sizing:</b> 1.5x for top performers, 1.0x standard, 0.5x for low liquidity.<br/>
<b>4. Negotiate Institutional Rates:</b> Target <$10/trade (vs current ~$80) for LONG strategy profitability.<br/>
<b>5. Begin Paper Trading:</b> Start with $100K to validate execution before scaling to $1M live.<br/>
<b>6. Scaling Path:</b> Phase 1 ($1M-$5M) no changes, Phase 2 ($5M-$20M) increase to 15 positions, Phase 3 ($20M-$50M) algorithmic execution.<br/>
<b>7. Risk Management:</b> Max 12% position size, 3 positions per symbol, -2% daily loss limit, monitor correlation.
"""
story.append(Paragraph(recommendations_text, normal_style))
story.append(PageBreak())

# APPENDIX
story.append(Paragraph("APPENDIX: FIFO REALISTIC BACKTESTING METHODOLOGY", heading_style))
appendix_text = """
<b>Overview:</b> FIFO (First-In-First-Out) realistic backtesting simulates production trading with real-world constraints.<br/><br/>
<b>Key Constraints:</b> 10-position limit, 10% capital per trade, timestamp-based FIFO ordering, ATR tiebreaker, shared resources for combined portfolio.<br/><br/>
<b>Baseline vs Production:</b> Baseline unlimited positions (LONG: 31,823, SHORT: 60,111). Production LONG: 16,754 (52.6%), SHORT: 1,424 (2.4%), Combined: 17,055 total.<br/><br/>
<b>Data Files:</b> Production_Long_Trades.parquet, Production_Short_Trades.parquet, part3_a2_combined_trades.csv<br/><br/>
<b>Limitations:</b> Estimated liquidity metrics, estimated transaction costs (~$80/trade), no dynamic slippage modeling, 147-day analysis period.
"""
story.append(Paragraph(appendix_text, normal_style))

# Build PDF
print("\nBuilding PDF...")
doc.build(story)

print("\n" + "="*80)
print("COMPREHENSIVE COMBINED REPORT V2 GENERATED")
print("="*80)
print(f"File: {pdf_file}")
print(f"Size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
print("="*80)
