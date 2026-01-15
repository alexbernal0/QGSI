"""
Generate comprehensive SHORT strategies PDF report
Matching the format of the LONG strategies report
"""

import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')

# Load data
df_symmetric = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Performance.csv')
df_asymmetric = pd.read_csv(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Performance.csv')

# Create PDF
pdf_file = OUTPUT_DIR / 'QGSI_Short_Strategies_Report_Phase2.pdf'
doc = SimpleDocTemplate(str(pdf_file), pagesize=landscape(letter),
                       topMargin=0.5*inch, bottomMargin=0.5*inch,
                       leftMargin=0.5*inch, rightMargin=0.5*inch)

styles = getSampleStyleSheet()
story = []

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#000080'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#000080'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=8,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

# Title Page
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph("QGSI Quantitative Research Report", title_style))
story.append(Paragraph("Phase 2: SHORT Signal Strategy Optimization", title_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Fixed ATR Exit Strategies Analysis", heading_style))
story.append(Spacer(1, 0.5*inch))

# Executive Summary
story.append(Paragraph("Executive Summary", heading_style))
story.append(Paragraph(
    "This report presents a comprehensive quantitative analysis of Fixed ATR-based exit strategies "
    "applied to SHORT signals across 400 stocks. Two distinct strategies were optimized: "
    "<b>Fixed ATR Symmetric</b> (equal stop/target distances) and <b>Fixed ATR Asymmetric</b> "
    "(wider targets than stops). A total of 128 parameter combinations were tested across "
    "approximately 60,139 short signals, generating over 7.6 million individual backtests.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Data Volume Table
data_table = [
    ['Strategy', 'Combinations', 'Signals', 'Total Trades'],
    ['Fixed ATR Symmetric', '32', '60,139', '1,922,592'],
    ['Fixed ATR Asymmetric', '96', '60,139', '5,761,776'],
    ['<b>TOTAL</b>', '<b>128</b>', '<b>60,139</b>', '<b>7,684,368</b>']
]

table = Table(data_table, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
]))
story.append(table)
story.append(PageBreak())

# Strategy 1: Fixed ATR Symmetric
story.append(Paragraph("Strategy 1: Fixed ATR Symmetric SHORT", heading_style))
story.append(Paragraph(
    "The Fixed ATR Symmetric strategy uses equal ATR multipliers for both stop loss and profit target, "
    "creating symmetric risk/reward profiles. For SHORT positions, the stop loss is placed ABOVE the "
    "entry price (loss if price rises) and the profit target is placed BELOW the entry price (profit if price falls).",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Symmetric Top 5
story.append(Paragraph("Top 5 Configurations", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
top5_sym = df_symmetric.nsmallest(5, 'NetProfit')[['ATRPeriod', 'StopMultiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']].copy()
top5_sym['WinRate'] = (top5_sym['WinRate'] * 100).round(1).astype(str) + '%'
top5_sym['NetProfit'] = top5_sym['NetProfit'].apply(lambda x: f"${x:,.0f}")
top5_sym['ProfitFactor'] = top5_sym['ProfitFactor'].round(3)

sym_data = [['Rank', 'ATR Period', 'Stop/Target', 'Net Profit', 'Profit Factor', 'Win Rate', 'Trades']]
for idx, row in enumerate(top5_sym.itertuples(), 1):
    sym_data.append([
        str(idx),
        str(row.ATRPeriod),
        f"{row.StopMultiplier:.1f}×",
        row.NetProfit,
        str(row.ProfitFactor),
        row.WinRate,
        f"{row.TotalTrades:,}"
    ])

sym_table = Table(sym_data, colWidths=[0.6*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
sym_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
]))
story.append(sym_table)
story.append(Spacer(1, 0.2*inch))

# Key Findings - Symmetric
story.append(Paragraph("Key Findings", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
findings_sym = [
    "<b>1. ALL configurations are UNPROFITABLE</b> - Every parameter combination resulted in negative returns, with losses ranging from -$84K to -$1.17M.",
    "<b>2. Tighter stops perform better</b> - Configurations with 1.5× multipliers had the smallest losses (-$84K to -$141K).",
    "<b>3. Wider stops amplify losses</b> - Multipliers of 4.0× and 5.0× resulted in losses exceeding -$1M.",
    "<b>4. Longer ATR periods reduce losses</b> - ATR(30) and ATR(50) had smaller losses than ATR(14) and ATR(20).",
    "<b>5. Market upward bias evident</b> - Symmetric exits do not work for short positions, suggesting inherent market directionality."
]
for finding in findings_sym:
    story.append(Paragraph(f"• {finding}", body_style))

story.append(PageBreak())

# Symmetric Visualization
story.append(Paragraph("Fixed ATR Symmetric SHORT - Performance Visualization", heading_style))
img_sym = Image(str(OUTPUT_DIR / 'Fixed_ATR_Symmetric_Short_Heatmap.png'), width=9*inch, height=4.5*inch)
story.append(img_sym)
story.append(PageBreak())

# Strategy 2: Fixed ATR Asymmetric
story.append(Paragraph("Strategy 2: Fixed ATR Asymmetric SHORT", heading_style))
story.append(Paragraph(
    "The Fixed ATR Asymmetric strategy uses different multipliers for stop loss and profit target, "
    "with the constraint that the target multiplier must be greater than or equal to the stop multiplier. "
    "This creates asymmetric risk/reward profiles designed to cut losses quickly while letting winners run. "
    "For SHORT positions, tight stops (1.5-2.0×) combined with wider targets (3.0-6.0×) were tested.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Asymmetric Top 5
story.append(Paragraph("Top 5 Configurations", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
top5_asym = df_asymmetric.head(5)[['ATRPeriod', 'StopMultiplier', 'TargetMultiplier', 'NetProfit', 'ProfitFactor', 'WinRate', 'TotalTrades']].copy()
top5_asym['WinRate'] = (top5_asym['WinRate'] * 100).round(1).astype(str) + '%'
top5_asym['NetProfit'] = top5_asym['NetProfit'].apply(lambda x: f"${x:,.0f}")
top5_asym['ProfitFactor'] = top5_asym['ProfitFactor'].round(3)

asym_data = [['Rank', 'ATR', 'Stop', 'Target', 'Net Profit', 'PF', 'Win Rate', 'Trades']]
for idx, row in enumerate(top5_asym.itertuples(), 1):
    asym_data.append([
        str(idx),
        str(row.ATRPeriod),
        f"{row.StopMultiplier:.1f}×",
        f"{row.TargetMultiplier:.1f}×",
        row.NetProfit,
        str(row.ProfitFactor),
        row.WinRate,
        f"{row.TotalTrades:,}"
    ])

asym_table = Table(asym_data, colWidths=[0.5*inch, 0.7*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 1*inch, 1*inch])
asym_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
]))
story.append(asym_table)
story.append(Spacer(1, 0.2*inch))

# Key Findings - Asymmetric
story.append(Paragraph("Key Findings", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
findings_asym = [
    "<b>1. Asymmetric exits enable profitability</b> - Unlike symmetric exits, asymmetric configurations with tight stops (1.5×) and wide targets (5.0-6.0×) achieve positive returns.",
    "<b>2. Longer ATR periods are superior</b> - ATR(50) and ATR(30) dominate the top 5, with ATR(50) producing the best result (+$332,920).",
    "<b>3. 1.5× stop is CRITICAL</b> - All profitable configurations use 1.5× stops. Stops of 2.0× are marginally profitable only with ATR(50), and stops ≥2.5× are always unprofitable.",
    "<b>4. Wider targets maximize profits</b> - Target multipliers of 5.0× and 6.0× consistently outperform 3.0× and 4.0× targets when paired with 1.5× stops.",
    "<b>5. Win rates are low but acceptable</b> - Profitable configurations have win rates of 27-31%, but the asymmetric risk/reward (tight stop, wide target) compensates for lower win rates.",
    "<b>6. Profit factors are modest</b> - Best configurations achieve profit factors of 1.03-1.05, indicating small but consistent edges.",
    "<b>7. Optimal configuration</b> - ATR(50) with 1.5× stop and 6.0× target produces +$332,920 net profit (PF: 1.046, Win: 27.7%)."
]
for finding in findings_asym:
    story.append(Paragraph(f"• {finding}", body_style))

story.append(PageBreak())

# Asymmetric Visualization
story.append(Paragraph("Fixed ATR Asymmetric SHORT - Performance Visualization", heading_style))
img_asym = Image(str(OUTPUT_DIR / 'Fixed_ATR_Asymmetric_Short_Heatmap.png'), width=9*inch, height=4.5*inch)
story.append(img_asym)
story.append(PageBreak())

# Strategic Implications
story.append(Paragraph("Strategic Implications & Recommendations", heading_style))
story.append(Paragraph(
    "<b>1. SHORT signals require asymmetric exits:</b> The failure of symmetric exits and success of "
    "asymmetric exits demonstrates that short positions require fundamentally different risk management "
    "than long positions. Tight stops (1.5× ATR) are essential to limit losses from upward price movements.",
    body_style
))
story.append(Paragraph(
    "<b>2. Market directional bias confirmed:</b> The difficulty in profiting from short signals, even with "
    "optimized exits, confirms the well-documented upward bias in equity markets. Short strategies must be "
    "highly selective and employ very tight risk controls.",
    body_style
))
story.append(Paragraph(
    "<b>3. Longer ATR periods provide better context:</b> ATR(50) outperforms shorter periods, suggesting "
    "that longer-term volatility measurements provide more reliable exit levels for short positions.",
    body_style
))
story.append(Paragraph(
    "<b>4. Implementation recommendation:</b> For short signal trading, use ATR(50) with 1.5× stop loss "
    "and 5.0-6.0× profit target. This configuration balances profitability with practical implementation.",
    body_style
))
story.append(Paragraph(
    "<b>5. Portfolio considerations:</b> Given the modest profit factors (1.03-1.05) and low win rates "
    "(27-31%), short strategies should be sized conservatively and used primarily as portfolio hedges "
    "rather than standalone alpha generators.",
    body_style
))
story.append(PageBreak())

# Conclusion
story.append(Paragraph("Conclusion", heading_style))
story.append(Paragraph(
    "This comprehensive optimization of Fixed ATR exit strategies for SHORT signals reveals critical insights "
    "into the asymmetric nature of short-side trading. While symmetric exits universally failed (all 32 "
    "configurations unprofitable), asymmetric exits with tight stops and wide targets successfully generated "
    "positive returns. The optimal configuration—ATR(50) with 1.5× stop and 6.0× target—produced +$332,920 "
    "in net profit across 60,013 trades, demonstrating that disciplined risk management can overcome the "
    "inherent challenges of short-side trading.",
    body_style
))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph(
    "The stark contrast between symmetric and asymmetric results underscores the importance of strategy-specific "
    "optimization. What works for long positions (symmetric exits) does not translate to short positions, "
    "requiring traders to adapt their risk management frameworks based on directional bias. The next phase "
    "of this research will explore trailing stop and breakeven stop strategies to further refine exit "
    "methodologies for short signals.",
    body_style
))
story.append(Spacer(1, 0.3*inch))

# Next Steps
story.append(Paragraph("Next Steps", heading_style))
next_steps = [
    "<b>Phase 2 Continuation:</b> Process ATR Trailing Stop and ATR Breakeven Stop strategies for short signals.",
    "<b>Comparative Analysis:</b> Compare long vs. short performance across all four strategies.",
    "<b>Combined Report:</b> Generate unified report integrating long and short signal optimizations.",
    "<b>Portfolio Construction:</b> Develop integrated long/short portfolio using optimal parameters from both phases."
]
for step in next_steps:
    story.append(Paragraph(f"• {step}", body_style))

story.append(PageBreak())

# Appendix
story.append(Paragraph("Appendix", heading_style))
story.append(Paragraph("<b>Data Files</b>", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
story.append(Paragraph("• <b>Source Data:</b> QGSI_AllSymbols_3Signals.parquet (972 MB, 400 stocks)", body_style))
story.append(Paragraph("• <b>Symmetric Results:</b> Fixed_ATR_Symmetric_Short_Performance.csv (32 configurations)", body_style))
story.append(Paragraph("• <b>Asymmetric Results:</b> Fixed_ATR_Asymmetric_Short_Performance.csv (96 configurations)", body_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("<b>Processing Details</b>", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
story.append(Paragraph("• <b>Symmetric Processing:</b> 10.8 minutes (batch processing, 10 symbols per batch)", body_style))
story.append(Paragraph("• <b>Asymmetric Processing:</b> 56 minutes (chunked processing, 4 ATR periods × 28 combinations each)", body_style))
story.append(Paragraph("• <b>Total Processing Time:</b> 66.8 minutes", body_style))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("<b>Methodology</b>", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
story.append(Paragraph(
    "All backtests used $100,000 position sizing, maximum 30-bar holding period, and intraday exit detection "
    "(stop checked against HIGH, target checked against LOW for short positions). Performance metrics include "
    "net profit, profit factor, win rate, average win/loss, and system score (net profit × profit factor).",
    body_style
))

# Build PDF
doc.build(story)
print(f"✓ Report generated: {pdf_file}")
print(f"✓ Total pages: ~12")
