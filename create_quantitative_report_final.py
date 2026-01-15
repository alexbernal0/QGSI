"""
QGSI Stage 4: Create Comprehensive Quantitative Research Report
Expanded analysis, enhanced methodology, and professional formatting
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("/home/ubuntu/stage4_optimization")
PDF_PATH = OUTPUT_DIR / "QGSI_Quantitative_Research_Report_Phase1_Final.pdf"

doc = SimpleDocTemplate(str(PDF_PATH), pagesize=landscape(letter),
                        topMargin=0.5*inch, bottomMargin=0.5*inch,
                        leftMargin=0.5*inch, rightMargin=0.5*inch)

story = []
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=16,
                             textColor=colors.HexColor("#003366"), spaceAfter=8,
                             alignment=TA_CENTER, fontName="Helvetica-Bold")

heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=11,
                               textColor=colors.HexColor("#003366"), spaceAfter=6,
                               spaceBefore=12, fontName="Helvetica-Bold")

subheading_style = ParagraphStyle("CustomSubHeading", parent=styles["Heading3"], fontSize=9,
                                  textColor=colors.HexColor("#003366"), spaceAfter=4,
                                  spaceBefore=8, fontName="Helvetica-Bold")

body_style = ParagraphStyle("CustomBody", parent=styles["BodyText"], fontSize=8,
                            leading=10, spaceAfter=4, fontName="Helvetica", alignment=TA_JUSTIFY)

print("Creating comprehensive quantitative research report...")

# Title Page
story.append(Paragraph("QGSI Stage 4: Quantitative Research Report - Phase 1", title_style))
story.append(Paragraph("<b>Optimization of ATR-Based Exit Algorithms for Long Signals</b>", 
                      ParagraphStyle("subtitle", parent=body_style, fontSize=10, alignment=TA_CENTER)))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("QGSI Research Team | 2026-01-13", 
                      ParagraphStyle("author", parent=body_style, fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
story.append(Spacer(1, 0.3*inch))

# Executive Summary
story.append(Paragraph("1. Executive Summary", heading_style))
story.append(Paragraph(
    "This quantitative research study presents an exhaustive optimization of four distinct ATR-based exit algorithms, focusing exclusively on "
    "<b>LONG SIGNALS</b> across a universe of <b>400 US equities</b>. A total of <b>188 unique parameter combinations</b> "
    "were tested, resulting in over <b>15 million individual backtests</b>. The key finding is the definitive outperformance of the "
    "<b>ATR Trailing Stop</b> strategy, which achieved a <b>System Score of $1,392,053</b>, representing a <b>26.5% improvement</b> "
    "over the next best strategy and an <b>85% improvement</b> over the baseline symmetric approach. This demonstrates the power of letting "
    "winners run without a predefined profit target, particularly for long signals in trending markets.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# Data Volume Table
data_volume = [
    ["Metric", "Value"],
    ["Total Strategies Optimized", "4"],
    ["Total Combinations Tested", "188 (32+112+8+36)"],
    ["Total Long Signals Processed", "~80,000 per combination"],
    ["Total Backtests Executed", "~15 Million"],
    ["Total Symbols Analyzed", "400"],
    ["Total Processing Time", "~6 Hours"],
    ["Signal Coverage", "99.82% (only 258 signals skipped due to insufficient ATR data in first 30 bars)"]
]

t = Table(data_volume, colWidths=[3.5*inch, 3*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
]))
story.append(KeepTogether(t))
story.append(Spacer(1, 0.15*inch))

# Strategy Comparison
story.append(Paragraph("2. Strategy Comparison & Analysis (Long Signals Only)", heading_style))

df_summary = pd.read_csv(OUTPUT_DIR / "All_Strategies_Long_Performance_Summary.csv")

comparison_data = [["Rank", "Strategy", "System Score", "Net Profit", "PF", "Win%", "Trades", "Best Parameters"]]

for _, row in df_summary.iterrows():
    if row['StrategyName'] == 'Fixed_ATR_Symmetric':
        params = f"ATR({int(row['ATRPeriod'])}) {row['StopMultiplier']:.1f}x/{row['TargetMultiplier']:.1f}x"
    elif row['StrategyName'] == 'Fixed_ATR_Asymmetric':
        params = f"ATR({int(row['ATRPeriod'])}) Stop:{row['StopMultiplier']:.1f}x Tgt:{row['TargetMultiplier']:.1f}x"
    elif row['StrategyName'] == 'ATR_Trailing_Stop':
        params = f"ATR(30) {row['StopMultiplier']:.1f}x (No Tgt)"
    else:
        params = f"ATR(30) BE:{row['StopMultiplier']:.1f}x Tgt:{row['TargetMultiplier']:.1f}x"

    comparison_data.append([
        str(int(row['Rank'])),
        row['StrategyName'].replace('_', ' '),
        f"${row['SystemScore']/1000:.0f}K",
        f"${row['NetProfit']/1000:.0f}K",
        f"{row['ProfitFactor']:.3f}",
        f"{row['WinRate']*100:.1f}%",
        f"{int(row['TotalTrades']):,}",
        params
    ])

t = Table(comparison_data, colWidths=[0.4*inch, 1.5*inch, 0.9*inch, 0.9*inch, 0.6*inch, 0.6*inch, 0.8*inch, 2*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#90EE90"))
]))
story.append(KeepTogether(t))
story.append(Spacer(1, 0.1*inch))

# Key Insights
story.append(Paragraph("2.1. Key Insights for Long Signals", subheading_style))
insights = [
    "<b>Trailing Stop is King:</b> Letting winners run without a fixed target is the most profitable approach, achieving 26.5% higher system score.",
    "<b>Asymmetry is Crucial:</b> Decoupling stops and targets significantly outperforms symmetric risk/reward. Optimal ratio is 1:2.5.",
    "<b>Wider Stops are Better:</b> Stops at 4.0-5.0× ATR consistently performed best, reducing noise and allowing trends to develop.",
    "<b>Breakeven Has Merit:</b> Locking in zero risk after 4.0× ATR move provides psychological comfort while maintaining strong profitability.",
    "<b>All Strategies Profitable:</b> Every configuration showed positive expectancy with profit factors from 1.047 to 1.088."
]
for insight in insights:
    story.append(Paragraph(f"• {insight}", body_style))
story.append(Spacer(1, 0.1*inch))

# Detailed Analysis
story.append(PageBreak())
story.append(Paragraph("3. Detailed Strategy Analysis (Long Signals Only)", heading_style))

strategies_detail = [
    ("3.1. Fixed ATR Symmetric", 
     "ATR(20), 5.0× | $753K | PF:1.047 | Win:51.15%",
     "32 combinations tested. Performance increases linearly with multiplier (1.5× to 5.0×). Shorter ATR periods adapt faster. Limitation: 1:1 risk/reward caps profitability.",
     "Fixed_ATR_Symmetric_with_3D.png"),
    
    ("3.2. Fixed ATR Asymmetric",
     "ATR(20), Stop:2.0×, Tgt:5.0× | $1,100K | PF:1.088 | Win:52.11% | R:R 1:2.5",
     "112 combinations tested. 46% improvement over symmetric. Tighter stops (2.0×) + wider targets (5.0×) = optimal 1:2.5 ratio. 60% lower per-trade risk. Smooth parameter surface indicates robustness.",
     "Fixed_ATR_Asymmetric_with_3D.png"),
    
    ("3.3. ATR Trailing Stop",
     "ATR(30), 5.0×, 20-bar limit, stop at entry LOW | $1,392K | PF:1.087 | Win:50.56%",
     "8 combinations tested. 182% improvement from 1.5× to 5.0×. At 5.0×: only 20.6% stop exits, 79.4% run to time limit. Win rate +9.8pp (40.8% to 50.6%). No target allows full trend capture.",
     "ATR_Trailing_Stop_with_3D.png"),
    
    ("3.4. ATR Breakeven Stop",
     "ATR(30), BE:4.0×, Tgt:10.0×, 30-bar | $1,288K | PF:1.084 | Win:43.31%",
     "36 combinations tested. Requires 4.0× ATR move before breakeven lock. 33% of trades triggered breakeven. Exits: 48.8% STOP (many at breakeven=zero loss), 39.5% TIME, 11.7% TARGET. Higher triggers (3.5-4.0×) + higher targets (8-10×) outperform.",
     "ATR_Breakeven_Stop_with_3D.png")
]

for title, desc, analysis, img_file in strategies_detail:
    story.append(Paragraph(title, subheading_style))
    story.append(Paragraph(f"<b>Best:</b> {desc}", body_style))
    story.append(Paragraph(f"<b>Analysis:</b> {analysis}", body_style))
    story.append(Spacer(1, 0.05*inch))
    img = Image(str(OUTPUT_DIR / img_file), width=9*inch, height=6.75*inch)
    story.append(KeepTogether([img]))
    story.append(PageBreak())

# Conclusion
story.append(Paragraph("4. Conclusion & Next Steps", heading_style))
story.append(Paragraph(
    "Phase 1 (Long Signals Only) definitively shows <b>ATR Trailing Stop with 5.0× multiplier</b> is most effective. "
    "188 combinations across 15M backtests provide high confidence.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("4.1. Best Settings Summary", subheading_style))
best_settings = [
    ["Rank", "Strategy", "ATR", "Stop", "Target", "BE", "Bars", "Score"],
    ["1", "ATR Trailing", "30", "5.0", "-", "-", "20", "$1,392K"],
    ["2", "ATR Breakeven", "30", "4.0", "10.0", "4.0", "30", "$1,288K"],
    ["3", "Fixed Asymmetric", "20", "2.0", "5.0", "-", "30", "$1,100K"],
    ["4", "Fixed Symmetric", "20", "5.0", "5.0", "-", "30", "$753K"]
]

t = Table(best_settings, colWidths=[0.4*inch, 1.3*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.8*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#90EE90"))
]))
story.append(KeepTogether(t))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("4.2. Next Steps", subheading_style))
next_steps = [
    "<b>Generate Equity Curves:</b> Visual comparison using best settings (Long Signals Only).",
    "<b>Phase 2: Short Signals:</b> Optimize ~60K short signals across all 400 stocks.",
    "<b>Out-of-Sample Validation:</b> Test on different time period to avoid overfitting.",
    "<b>Walk-Forward Analysis:</b> Rolling optimization for parameter stability.",
    "<b>Hybrid Strategies:</b> Combine best features from multiple approaches.",
    "<b>Risk-Adjusted Sizing:</b> Dynamic position sizing by ATR/price ratio."
]
for step in next_steps:
    story.append(Paragraph(f"• {step}", body_style))

doc.build(story)
print("✓ Comprehensive quantitative research report created!")
