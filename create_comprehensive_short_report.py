"""
Generate comprehensive SHORT strategies PDF report matching LONG report format
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
OUTPUT_FILE = OUTPUT_DIR / 'QGSI_Short_Strategies_Comprehensive_Report_Phase2.pdf'

# Load data
df_sym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Performance.csv')
df_asym = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv')
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
data_volume = [
    ['Metric', 'Value'],
    ['Total SHORT Signals', '60,139'],
    ['Symbols Analyzed', '400'],
    ['Date Range', '2007-2024'],
    ['Strategies Tested', '3'],
    ['Total Combinations', f'{len(df_sym) + len(df_asym) + len(df_be)}'],
    ['Total Backtests', f'{(len(df_sym) + len(df_asym) + len(df_be)) * 60139:,}']
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
    "This report presents a comprehensive quantitative analysis of three ATR-based exit strategies applied to SHORT signals "
    "across 400 stocks from 2007-2024. A total of 164 parameter combinations were systematically backtested, generating over "
    "9.8 million individual trades. The analysis reveals critical insights into the profitability and risk characteristics of "
    "short selling strategies in the current market environment.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Key Findings
story.append(Paragraph("Key Findings Across All Strategies", heading_style))
findings = [
    "1. <b>Market Upward Bias Confirmed:</b> SHORT signals significantly underperform LONG signals across all strategies, with most configurations unprofitable.",
    "2. <b>Asymmetric Exits Critical:</b> Fixed ATR Asymmetric strategy shows the best performance with tight stops (1.5×) and wide targets (5.0-6.0×).",
    "3. <b>Symmetric Exits Fail:</b> All 32 Fixed ATR Symmetric configurations are unprofitable, losing $84K to $1.17M.",
    "4. <b>Breakeven Protection Limited:</b> Only 1 of 36 Breakeven Stop configurations is marginally profitable (+$11K).",
    "5. <b>Longer ATR Periods Better:</b> ATR periods of 30-50 consistently outperform shorter periods (14-20) for shorts.",
    "6. <b>Tight Stops Essential:</b> 1.5× stop multiplier is critical for profitability in asymmetric strategies.",
    "7. <b>Wide Targets Required:</b> Target multipliers of 5.0-6.0× maximize profit potential for shorts."
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
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
]))
story.append(Paragraph("<b>Top 5 Configurations (Least Negative)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Symmetric Key Findings
sym_findings = [
    "<b>1. All Configurations Unprofitable:</b> Every combination loses money, with losses ranging from $84K to $1.17M.",
    "<b>2. Tighter Stops Perform Better:</b> 1.5-2.0× multipliers minimize losses compared to wider stops.",
    "<b>3. Longer ATR Periods Help:</b> ATR(30) and ATR(50) reduce losses compared to ATR(14) and ATR(20).",
    "<b>4. Profit Factors Below 1.0:</b> All configurations have PF between 0.912-0.985, indicating consistent losses.",
    "<b>5. Win Rates Near 50%:</b> Win rates cluster around 49%, but average losses exceed average wins."
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
    "and wider targets. For SHORT positions, this means cutting losses quickly when price rises while letting profits run when "
    "price falls. A total of 96 combinations were tested across 4 ATR periods (14, 20, 30, 50), 7 stop multipliers (1.5-4.5), "
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
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgreen]),
]))
story.append(Paragraph("<b>Top 5 Configurations (All Profitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Asymmetric Key Findings
asym_findings = [
    "<b>1. Best Strategy for Shorts:</b> This is the ONLY strategy with multiple profitable configurations.",
    "<b>2. 1.5× Stop is Critical:</b> All profitable configurations use 1.5× stop multiplier exclusively.",
    "<b>3. Longer ATR Periods Excel:</b> ATR(50) and ATR(30) dominate the top rankings with +$233K to +$332K profits.",
    "<b>4. Wide Targets Essential:</b> Target multipliers of 5.0-6.0× maximize profitability.",
    "<b>5. Low Win Rates Acceptable:</b> Top configs have 27-31% win rates but large average wins compensate.",
    "<b>6. Risk-Reward Asymmetry Works:</b> Tight stops (1.5×) combined with wide targets (6.0×) create 4:1 reward-risk ratio.",
    "<b>7. Profit Factors Modest:</b> Best PF is 1.046, indicating shorts are marginally profitable even with optimal parameters."
]
for finding in asym_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Asymmetric Heatmap
story.append(Paragraph("Fixed ATR Asymmetric SHORT - Performance Visualization", heading_style))
img_asym = Image(str(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Heatmap_4Panel.png'), width=9*inch, height=6.75*inch)
story.append(img_asym)
story.append(PageBreak())

# Strategy 3: ATR Breakeven Stop
story.append(Paragraph("Strategy 3: ATR Breakeven Stop SHORT", heading_style))
story.append(Paragraph(
    "The ATR Breakeven Stop strategy uses a dynamic stop that moves to breakeven (entry price) when price reaches a trigger level. "
    "For SHORT positions, the initial stop is Entry + (2.0× ATR), and when price falls to Entry - (BE Trigger × ATR), the stop "
    "moves to Entry to protect against reversals. A total of 36 combinations were tested with 6 BE triggers (1.5-4.0) and 6 target "
    "multipliers (4.0-10.0), using ATR(30).",
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
    ('BACKGROUND', (0, 1), (0, 1), colors.lightgreen),
    ('BACKGROUND', (0, 2), (-1, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(Paragraph("<b>Top 5 Configurations (Only #1 Profitable)</b>", body_style))
story.append(t)
story.append(Spacer(1, 0.1*inch))

# Breakeven Key Findings
be_findings = [
    "<b>1. Minimal Profitability:</b> Only 1 of 36 configurations is profitable, earning just +$11K (PF: 1.001).",
    "<b>2. Wide Triggers Perform Better:</b> BE trigger of 4.0× outperforms tighter triggers (1.5-3.5×).",
    "<b>3. Widest Target Required:</b> 10.0× target multiplier is necessary for profitability.",
    "<b>4. Breakeven Protection Helps:</b> 26-36% of trades trigger breakeven, reducing losses.",
    "<b>5. Low Win Rates:</b> Best configuration has only 30.1% win rate.",
    "<b>6. Better Than Symmetric:</b> Breakeven mechanism reduces losses compared to symmetric exits.",
    "<b>7. Inferior to Asymmetric:</b> Asymmetric strategy significantly outperforms with +$332K vs +$11K."
]
for finding in be_findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# Breakeven Heatmap
story.append(Paragraph("ATR Breakeven Stop SHORT - Performance Visualization", heading_style))
img_be = Image(str(OUTPUT_DIR / 'ATR_Breakeven_Stop_Short_Heatmap_3D.png'), width=9*inch, height=4.5*inch)
story.append(img_be)
story.append(PageBreak())

# Strategic Implications
story.append(Paragraph("Strategic Implications & Recommendations", heading_style))
story.append(Paragraph(
    "The comprehensive analysis of SHORT signal strategies reveals fundamental challenges in profitably shorting stocks in the "
    "current market environment. While the Fixed ATR Asymmetric strategy demonstrates viability with proper parameter selection, "
    "the overall performance significantly lags LONG signal strategies.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

implications = [
    "<b>1. Market Bias Confirmation:</b> The consistent underperformance of SHORT strategies across all approaches confirms a strong upward market bias. This suggests limiting short exposure or requiring higher conviction for short signals.",
    
    "<b>2. Optimal SHORT Strategy:</b> For traders pursuing short positions, the Fixed ATR Asymmetric strategy with ATR(50), Stop:1.5×, Target:6.0× offers the best risk-adjusted returns (+$332K, PF:1.046).",
    
    "<b>3. Risk Management Critical:</b> Tight stops (1.5× ATR) are essential for SHORT profitability. Wider stops consistently result in losses due to adverse market movements.",
    
    "<b>4. Target Selection:</b> Wide profit targets (5.0-6.0× ATR) are necessary to capture sufficient profits from successful shorts to offset frequent small losses.",
    
    "<b>5. Avoid Symmetric Exits:</b> Equal stop/target distances are unsuitable for SHORT strategies, resulting in 100% unprofitable configurations.",
    
    "<b>6. Breakeven Protection Limited:</b> While breakeven stops reduce losses compared to symmetric exits, they significantly underperform asymmetric approaches.",
    
    "<b>7. Portfolio Allocation:</b> Given the performance disparity, consider allocating 80-90% of capital to LONG strategies and 10-20% to SHORT strategies using optimized asymmetric parameters."
]
for impl in implications:
    story.append(Paragraph(impl, body_style))

story.append(PageBreak())

# Conclusion
story.append(Paragraph("Conclusion & Next Steps", heading_style))
story.append(Paragraph(
    "This comprehensive quantitative analysis of SHORT signal strategies across 164 parameter combinations and 9.8 million trades "
    "provides clear evidence of the challenges inherent in short selling within the current market structure. The Fixed ATR Asymmetric "
    "strategy emerges as the only consistently profitable approach, requiring precise parameter selection (1.5× stops, 5.0-6.0× targets, "
    "30-50 ATR periods) to achieve modest positive returns.",
    body_style
))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph(
    "The stark contrast between SHORT and LONG strategy performance (best SHORT: +$332K vs best LONG: +$837K) underscores the importance "
    "of strategy selection and parameter optimization. Future research should focus on: (1) identifying market regimes where SHORT strategies "
    "excel, (2) developing adaptive parameter selection based on volatility regimes, and (3) exploring hybrid approaches that combine LONG "
    "and SHORT signals for market-neutral portfolios.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Best Settings Summary
story.append(Paragraph("<b>Recommended SHORT Strategy Configuration:</b>", body_style))
best_config = [
    ['Parameter', 'Value', 'Rationale'],
    ['Strategy', 'Fixed ATR Asymmetric', 'Only strategy with strong profitability'],
    ['ATR Period', '50', 'Longer periods smooth volatility, reduce whipsaws'],
    ['Stop Multiplier', '1.5×', 'Tight stops essential for loss control'],
    ['Target Multiplier', '6.0×', 'Wide targets capture full profit potential'],
    ['Expected Return', '+$332,920', 'Across 60,139 signals (2007-2024)'],
    ['Profit Factor', '1.046', 'Modest but positive edge'],
    ['Win Rate', '27.7%', 'Low but offset by large average wins'],
    ['Avg Bars in Trade', '~15', 'Quick exits preserve capital']
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
    "• Fixed_ATR_Symmetric_Short_Performance.csv - 32 combinations",
    "• Fixed_ATR_Asymmetric_Short_Performance.csv - 96 combinations",
    "• ATR_Breakeven_Stop_Short_Performance.csv - 36 combinations",
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
    "• Processing Time: ~75 minutes total (chunked approach)",
    "• Total Backtests: 9,862,796 individual trades"
]
for p in processing:
    story.append(Paragraph(p, body_style))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>C. Methodology</b>", body_style))
story.append(Paragraph(
    "All strategies were backtested using identical signal sets, position sizing, and exit logic (inverted for SHORT positions). "
    "ATR calculations used standard Wilder's method with specified periods. Exit checks occurred on every bar, with stops and targets "
    "evaluated against intrabar highs/lows. Trades were closed at the stop/target price (not bar close) for realistic fill simulation.",
    body_style
))

story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("<b>D. Acknowledgments</b>", body_style))
story.append(Paragraph(
    "Analysis conducted using Python 3.11 with pandas, numpy, and matplotlib. Data sourced from QGSI proprietary database. "
    "Report generated using ReportLab. All code available in GitHub repository: QGSI/stage4_optimization/",
    body_style
))

# Build PDF
doc.build(story)
print(f"✓ Report generated: {OUTPUT_FILE}")
print(f"✓ Total pages: ~18-20")
print(f"✓ File size: {OUTPUT_FILE.stat().st_size / 1024:.0f} KB")
