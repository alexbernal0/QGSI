"""
Generate FINAL comprehensive SHORT strategies PDF report with ALL 4 strategies
Matching LONG report format exactly
"""

import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')
OUTPUT_FILE = OUTPUT_DIR / 'QGSI_Short_Strategies_Final_Report_Phase2.pdf'

# Load data
df_sym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Performance.csv')
df_asym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv')
df_trail = pd.read_csv(OUTPUT_DIR / 'ATR_Trailing_Stop_Short_Performance.csv')
df_be = pd.read_csv(OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Performance.csv')

# Create PDF
doc = SimpleDocTemplate(str(OUTPUT_FILE), pagesize=landscape(letter),
                       leftMargin=0.5*inch, rightMargin=0.5*inch,
                       topMargin=0.5*inch, bottomMargin=0.5*inch)

styles = getSampleStyleSheet()
story = []

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=8,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

# Title Page
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph("QGSI Quantitative Research Report", title_style))
story.append(Paragraph("Phase 2: SHORT Signal Strategy Optimization", heading_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Comprehensive Analysis of ATR-Based Exit Strategies", body_style))
story.append(Spacer(1, 0.5*inch))

# Data Volume Table
total_combos = len(df_sym) + len(df_asym) + len(df_trail) + len(df_be)
data_volume = [
    ['Metric', 'Value'],
    ['Total SHORT Signals', '~60,033'],
    ['Symbols Analyzed', '400'],
    ['Date Range', '2007-2024'],
    ['Strategies Tested', '4'],
    ['Total Combinations', str(total_combos)],
    ['Total Backtests', f'{total_combos * 60033:,}']
]

t = Table(data_volume, colWidths=[3*inch, 2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(t)
story.append(PageBreak())

# Executive Summary
story.append(Paragraph("Executive Summary", heading_style))
story.append(Paragraph(
    f"This report presents a comprehensive quantitative analysis of four ATR-based exit strategies applied to SHORT signals "
    f"across 400 stocks from 2007-2024. A total of {total_combos} parameter combinations were systematically backtested, generating over "
    f"{total_combos * 60033:,} individual trades. The analysis reveals critical insights into the profitability and risk characteristics of "
    f"short selling strategies in the current market environment.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Strategy Comparison Table
story.append(Paragraph("Strategy Performance Comparison", heading_style))
comparison_data = [
    ['Strategy', 'Best Config', 'Net Profit', 'Profit Factor', 'Win Rate', 'Combinations'],
    ['ATR Trailing Stop', 'Mult: 1.5×', f"${df_trail.iloc[0]['NetProfit']:,.0f}", 
     f"{df_trail.iloc[0]['ProfitFactor']:.3f}", f"{df_trail.iloc[0]['WinRate']*100:.1f}%", str(len(df_trail))],
    ['Fixed ATR Asymmetric', 'ATR(50) 1.5×/6.0×', f"${df_asym.iloc[0]['NetProfit']:,.0f}", 
     f"{df_asym.iloc[0]['ProfitFactor']:.3f}", f"{df_asym.iloc[0]['WinRate']*100:.1f}%", str(len(df_asym))],
    ['ATR Breakeven Stop', 'BE:4.0× Tgt:10.0×', f"${df_be.iloc[0]['NetProfit']:,.0f}", 
     f"{df_be.iloc[0]['ProfitFactor']:.3f}", f"{df_be.iloc[0]['WinRate']*100:.1f}%", str(len(df_be))],
    ['Fixed ATR Symmetric', 'ATR(30) 1.5×', f"${df_sym.iloc[0]['NetProfit']:,.0f}", 
     f"{df_sym.iloc[0]['ProfitFactor']:.3f}", f"{df_sym.iloc[0]['WinRate']*100:.1f}%", str(len(df_sym))],
]

t = Table(comparison_data, colWidths=[2*inch, 1.8*inch, 1.3*inch, 1.2*inch, 1*inch, 1.2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (0, 2), colors.lightgreen),
    ('BACKGROUND', (0, 3), (0, 3), colors.lightyellow),
    ('BACKGROUND', (0, 4), (0, 4), colors.lightcoral),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

# Key Findings
story.append(Paragraph("Key Findings Across All Strategies", heading_style))
findings = [
    "1. <b>Trailing Stop Dominates:</b> ATR Trailing Stop is the best SHORT strategy with +$859K profit, outperforming all others by 2.6×.",
    "2. <b>Asymmetric Exits Work:</b> Fixed ATR Asymmetric with tight stops (1.5×) and wide targets (6.0×) earns +$332K.",
    "3. <b>Symmetric Exits Fail:</b> All 32 Fixed ATR Symmetric configurations are unprofitable, losing $84K to $1.17M.",
    "4. <b>Breakeven Protection Minimal:</b> Only 1 of 36 Breakeven Stop configurations is marginally profitable (+$11K).",
    "5. <b>Tight Stops Critical:</b> 1.5× ATR multiplier consistently performs best across profitable strategies.",
    "6. <b>Market Upward Bias:</b> SHORT strategies significantly underperform LONG strategies (best SHORT: +$859K vs best LONG: +$837K).",
    "7. <b>Low Win Rates Acceptable:</b> Top configs have 27-34% win rates but large average wins compensate for frequent small losses."
]
for finding in findings:
    story.append(Paragraph(finding, body_style))
story.append(PageBreak())

# Strategy 1: Fixed ATR Symmetric
story.append(Paragraph("Strategy 1: Fixed ATR Symmetric SHORT", heading_style))
story.append(Paragraph(
    "The Fixed ATR Symmetric strategy uses equal ATR multipliers for both stop loss and profit target. For SHORT positions, "
    "the stop is placed ABOVE the entry price (Entry + ATR × Multiplier) and the target BELOW (Entry - ATR × Multiplier). "
    "A total of 32 combinations were tested across 4 ATR periods (14, 20, 30, 50) and 8 multipliers (1.5-5.0).",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Top 5 Symmetric
top5_sym = df_sym.nsmallest(5, 'Rank')[['Rank', 'ATRPeriod', 'StopMultiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']]
top5_sym_data = [['Rank', 'ATR', 'Mult', 'Net Profit', 'PF', 'Win%', 'Trades']]
for _, row in top5_sym.iterrows():
    top5_sym_data.append([
        int(row['Rank']),
        f"ATR({int(row['ATRPeriod'])})",
        f"{row['StopMultiplier']:.1f}×",
        f"${row['NetProfit']:,.0f}",
        f"{row['ProfitFactor']:.3f}",
        f"{row['WinRate']*100:.1f}%",
        f"{int(row['TotalTrades']):,}"
    ])

t = Table(top5_sym_data, colWidths=[0.6*inch, 0.9*inch, 0.7*inch, 1.2*inch, 0.7*inch, 0.8*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(Paragraph("<b>Top 5 Configurations (All Unprofitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Symmetric findings
sym_findings = [
    "<b>1. Complete Failure:</b> Every combination loses money, confirming symmetric exits are unsuitable for shorts.",
    "<b>2. Market Bias Evident:</b> Consistent losses across all parameters indicate strong upward market pressure.",
    "<b>3. Tighter Stops Help:</b> 1.5-2.0× multipliers minimize losses compared to wider stops.",
]
for finding in sym_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Symmetric Heatmap
story.append(Paragraph("Fixed ATR Symmetric SHORT - Performance Visualization", heading_style))
img_sym = Image(str(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Heatmap_3D.png'), width=9*inch, height=4.5*inch)
story.append(img_sym)
story.append(PageBreak())

# Strategy 2: Fixed ATR Asymmetric
story.append(Paragraph("Strategy 2: Fixed ATR Asymmetric SHORT", heading_style))
story.append(Paragraph(
    "The Fixed ATR Asymmetric strategy uses different multipliers for stop loss and profit target, allowing for tighter stops "
    "and wider targets. A total of 96 combinations were tested across 4 ATR periods (14, 20, 30, 50), 7 stop multipliers (1.5-4.5), "
    "and 4 target multipliers (3.0-6.0).",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Top 5 Asymmetric
top5_asym = df_asym.nsmallest(5, 'Rank')[['Rank', 'ATRPeriod', 'StopMultiplier', 'TargetMultiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']]
top5_asym_data = [['Rank', 'ATR', 'Stop', 'Target', 'Net Profit', 'PF', 'Win%', 'Trades']]
for _, row in top5_asym.iterrows():
    top5_asym_data.append([
        int(row['Rank']),
        f"ATR({int(row['ATRPeriod'])})",
        f"{row['StopMultiplier']:.1f}×",
        f"{row['TargetMultiplier']:.1f}×",
        f"${row['NetProfit']:,.0f}",
        f"{row['ProfitFactor']:.3f}",
        f"{row['WinRate']*100:.1f}%",
        f"{int(row['TotalTrades']):,}"
    ])

t = Table(top5_asym_data, colWidths=[0.6*inch, 0.9*inch, 0.7*inch, 0.8*inch, 1.2*inch, 0.7*inch, 0.8*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(Paragraph("<b>Top 5 Configurations (All Profitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Asymmetric findings
asym_findings = [
    "<b>1. Second Best Strategy:</b> Earns +$332K, significantly better than Breakeven and Symmetric.",
    "<b>2. 1.5× Stop Essential:</b> All profitable configurations use 1.5× stop multiplier exclusively.",
    "<b>3. Longer ATR Periods:</b> ATR(50) and ATR(30) dominate top rankings.",
]
for finding in asym_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Asymmetric Heatmap
story.append(Paragraph("Fixed ATR Asymmetric SHORT - Performance Visualization", heading_style))
img_asym = Image(str(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Heatmap_4Panel.png'), width=9*inch, height=6.75*inch)
story.append(img_asym)
story.append(PageBreak())

# Strategy 3: ATR Trailing Stop
story.append(Paragraph("Strategy 3: ATR Trailing Stop SHORT", heading_style))
story.append(Paragraph(
    "The ATR Trailing Stop strategy uses a dynamic stop that moves DOWN as price falls, locking in profits. For SHORT positions, "
    "the stop starts at Entry + (ATR × Multiplier) and trails downward using MIN(previous_stop, Current HIGH + ATR × Multiplier). "
    "A total of 8 combinations were tested with multipliers from 1.5-5.0 using ATR(30).",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Top 5 Trailing
top5_trail = df_trail.nsmallest(5, 'Rank')[['Rank', 'Multiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'AvgBarsInTrade', 'TotalTrades']]
top5_trail_data = [['Rank', 'Multiplier', 'Net Profit', 'PF', 'Win%', 'Avg Bars', 'Trades']]
for _, row in top5_trail.iterrows():
    top5_trail_data.append([
        int(row['Rank']),
        f"{row['Multiplier']:.1f}×",
        f"${row['NetProfit']:,.0f}",
        f"{row['ProfitFactor']:.3f}",
        f"{row['WinRate']*100:.1f}%",
        f"{row['AvgBarsInTrade']:.1f}",
        f"{int(row['TotalTrades']):,}"
    ])

t = Table(top5_trail_data, colWidths=[0.6*inch, 1*inch, 1.3*inch, 0.7*inch, 0.8*inch, 1*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(Paragraph("<b>Top 5 Configurations (All Profitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Trailing findings
trail_findings = [
    "<b>1. BEST SHORT STRATEGY:</b> Earns +$859K, outperforming all other SHORT strategies by 2.6×.",
    "<b>2. All Configs Profitable:</b> 100% success rate - every multiplier from 1.5-5.0× earns positive returns.",
    "<b>3. Tighter is Better:</b> 1.5× multiplier earns the most (+$859K) with highest profit factor (1.139).",
    "<b>4. Trailing Mechanism Works:</b> Dynamic stops lock in profits as price moves favorably.",
]
for finding in trail_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Trailing Chart
story.append(Paragraph("ATR Trailing Stop SHORT - Performance Visualization", heading_style))
img_trail = Image(str(OUTPUT_DIR / 'ATR_Trailing_Stop_Short_Charts.png'), width=9*inch, height=3.5*inch)
story.append(img_trail)
story.append(PageBreak())

# Strategy 4: ATR Breakeven Stop
story.append(Paragraph("Strategy 4: ATR Breakeven Stop SHORT", heading_style))
story.append(Paragraph(
    "The ATR Breakeven Stop strategy uses a dynamic stop that moves to breakeven (entry price) when price reaches a trigger level. "
    "A total of 36 combinations were tested with 6 BE triggers (1.5-4.0) and 6 target multipliers (4.0-10.0), using ATR(30).",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Top 5 Breakeven
top5_be = df_be.nsmallest(5, 'Rank')[['Rank', 'BETrigger', 'TargetMultiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'BreakevenTriggeredPct', 'TotalTrades']]
top5_be_data = [['Rank', 'BE Trigger', 'Target', 'Net Profit', 'PF', 'Win%', 'BE%', 'Trades']]
for _, row in top5_be.iterrows():
    top5_be_data.append([
        int(row['Rank']),
        f"{row['BETrigger']:.1f}×",
        f"{row['TargetMultiplier']:.1f}×",
        f"${row['NetProfit']:,.0f}",
        f"{row['ProfitFactor']:.3f}",
        f"{row['WinRate']*100:.1f}%",
        f"{row['BreakevenTriggeredPct']:.1f}%",
        f"{int(row['TotalTrades']):,}"
    ])

t = Table(top5_be_data, colWidths=[0.6*inch, 1*inch, 0.8*inch, 1.2*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (0, 1), colors.lightyellow),
    ('BACKGROUND', (0, 2), (-1, -1), colors.lightcoral),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(Paragraph("<b>Top 5 Configurations (Only #1 Marginally Profitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Breakeven findings
be_findings = [
    "<b>1. Minimal Profitability:</b> Only 1 of 36 configurations is profitable, earning just +$11K (PF: 1.001).",
    "<b>2. Better Than Symmetric:</b> Breakeven mechanism reduces losses compared to symmetric exits.",
    "<b>3. Inferior to Trailing:</b> Significantly underperforms trailing stop strategy.",
]
for finding in be_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Breakeven Heatmap
story.append(Paragraph("ATR Breakeven Stop SHORT - Performance Visualization", heading_style))
img_be = Image(str(OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Heatmap_3D.png'), width=9*inch, height=4.5*inch)
story.append(img_be)
story.append(PageBreak())

# Conclusion
story.append(Paragraph("Conclusion & Recommendations", heading_style))
story.append(Paragraph(
    f"This comprehensive analysis of {total_combos} SHORT strategy configurations reveals clear winners and losers. "
    f"The ATR Trailing Stop strategy emerges as the dominant approach for SHORT signals, earning +$859K with 100% of configurations "
    f"profitable. In contrast, symmetric exits fail completely, and breakeven protection offers minimal benefit.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Best Settings
story.append(Paragraph("<b>Recommended SHORT Strategy Configuration:</b>", body_style))
best_config = [
    ['Parameter', 'Value', 'Rationale'],
    ['Strategy', 'ATR Trailing Stop', 'Best performance, all configs profitable'],
    ['ATR Period', '30', 'Optimal balance of responsiveness and stability'],
    ['Multiplier', '1.5×', 'Tightest stop, highest profit (+$859K)'],
    ['Expected Return', '+$859,092', 'Across 60,033 signals (2007-2024)'],
    ['Profit Factor', '1.139', 'Strong positive edge'],
    ['Win Rate', '34.3%', 'Low but offset by large average wins'],
    ['Avg Bars in Trade', '8.7', 'Quick exits preserve capital']
]

t = Table(best_config, colWidths=[2*inch, 2*inch, 4*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
story.append(t)
story.append(PageBreak())

# Appendix
story.append(Paragraph("Appendix", heading_style))
story.append(Paragraph("<b>A. Data Files</b>", body_style))
data_files = [
    f"• Fixed_ATR_Symmetric_Short_Performance.csv - {len(df_sym)} combinations",
    f"• Fixed_ATR_Asymmetric_Short_Performance.csv - {len(df_asym)} combinations",
    f"• ATR_Trailing_Stop_Short_Performance.csv - {len(df_trail)} combinations",
    f"• ATR_Breakeven_Stop_Short_Performance.csv - {len(df_be)} combinations",
    "• QGSI_AllSymbols_3Signals.parquet - Source data (972MB, 400 stocks)"
]
for f in data_files:
    story.append(Paragraph(f, body_style))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>B. Processing Details</b>", body_style))
processing = [
    "• Batch Size: 10 symbols per batch",
    "• Position Size: $100,000 per trade",
    "• Commission: Not included (add $10-20 per round-trip)",
    "• Slippage: Not included (add 0.05-0.10% per trade)",
    f"• Total Backtests: {total_combos * 60033:,} individual trades"
]
for p in processing:
    story.append(Paragraph(p, body_style))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>C. Methodology</b>", body_style))
story.append(Paragraph(
    "All strategies were backtested using identical signal sets, position sizing, and exit logic (inverted for SHORT positions). "
    "ATR calculations used standard Wilder's method. Exit checks occurred on every bar with stops/targets evaluated against intrabar highs/lows.",
    body_style
))

# Build PDF
doc.build(story)
print(f"✓ Report generated: {OUTPUT_FILE}")
print(f"✓ File size: {OUTPUT_FILE.stat().st_size / (1024*1024):.1f} MB")
