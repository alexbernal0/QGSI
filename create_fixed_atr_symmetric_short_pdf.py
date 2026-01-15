"""
Generate Professional PDF Report for Fixed ATR Symmetric SHORT Strategy
Matches the format and style of the LONG report
"""

import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
from datetime import datetime

# Configuration
PERFORMANCE_CSV = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_Performance.csv')
HEATMAP_IMAGE = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_with_3D.png')
OUTPUT_PDF = Path('/home/ubuntu/stage4_optimization/Fixed_ATR_Symmetric_Short_Report.pdf')

print("="*80)
print("GENERATING PDF REPORT - FIXED ATR SYMMETRIC SHORT")
print("="*80)

# Load data
print("\n[1/4] Loading data...")
df = pd.read_csv(PERFORMANCE_CSV)
print(f"✓ Loaded {len(df)} configurations")

# Create PDF
print("\n[2/4] Creating PDF document...")
doc = SimpleDocTemplate(str(OUTPUT_PDF), pagesize=landscape(letter),
                       topMargin=0.5*inch, bottomMargin=0.5*inch,
                       leftMargin=0.5*inch, rightMargin=0.5*inch)

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#1a365d'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Normal'],
    fontSize=11,
    textColor=colors.HexColor('#2d3748'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.HexColor('#1a365d'),
    spaceAfter=8,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=8,
    textColor=colors.HexColor('#2d3748'),
    spaceAfter=6,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=10
)

# Build content
story = []

# Title Page
story.append(Spacer(1, 1*inch))
story.append(Paragraph("QGSI Stage 4 Phase 2: Quantitative Research Report", title_style))
story.append(Paragraph("Fixed ATR Symmetric Strategy - SHORT SIGNALS ONLY", subtitle_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
story.append(Paragraph("<b>Author:</b> QGSI Research Team", subtitle_style))
story.append(Spacer(1, 0.5*inch))

# Executive Summary
story.append(Paragraph("Executive Summary", heading_style))
summary_text = """
This report presents the comprehensive optimization results for the Fixed ATR Symmetric exit strategy 
applied exclusively to SHORT signals across 400 US equities. The strategy employs symmetric stop loss 
and profit target levels based on Average True Range (ATR) multiples, with a 30-bar time limit. 
A total of 32 parameter combinations were tested (4 ATR periods × 8 multipliers), processing 60,139 
short signals and executing 1,921,480 individual trades. <b>CRITICAL FINDING:</b> All 32 configurations 
produced negative net profits with profit factors below 1.0, indicating that symmetric exit logic is 
not profitable for short positions in this dataset. The best configuration (ATR 30, 1.5× multiplier) 
lost $84,173, while the worst (ATR 14, 5.0× multiplier) lost $1,166,700. This systematic underperformance 
suggests either a market upward bias during the test period or that short signals require fundamentally 
different exit management than long signals.
"""
story.append(Paragraph(summary_text, body_style))
story.append(Spacer(1, 0.2*inch))

# Data Volume Table
data_volume_data = [
    ['Metric', 'Value'],
    ['Total SHORT Signals', '60,139'],
    ['Total Symbols', '400'],
    ['ATR Periods Tested', '4 (14, 20, 30, 50)'],
    ['Multipliers Tested', '8 (1.5 - 5.0)'],
    ['Total Combinations', '32'],
    ['Total Trades Executed', '1,921,480'],
    ['Signal Coverage', '99.82%'],
    ['Processing Time', '10.8 minutes']
]

data_volume_table = Table(data_volume_data, colWidths=[3*inch, 2*inch])
data_volume_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
]))
story.append(data_volume_table)

story.append(PageBreak())

# Strategy Description
story.append(Paragraph("Strategy Description", heading_style))
strategy_text = """
The Fixed ATR Symmetric strategy uses Average True Range (ATR) to set symmetric stop loss and profit 
target levels for short positions. <b>SHORT POSITION LOGIC (INVERTED):</b> Entry occurs at the signal 
bar CLOSE price via a short sale. The stop loss is placed ABOVE the entry price at Entry + (ATR × Multiplier), 
representing a loss if the price rises. The profit target is placed BELOW the entry price at Entry - (ATR × Multiplier), 
representing a profit if the price falls. The position exits when the bar HIGH reaches the stop loss (loss), 
the bar LOW reaches the profit target (profit), or 30 bars elapse (time limit). This inverted logic is 
critical for short positions: stops are above entry (losses occur when price rises) and targets are below 
entry (profits occur when price falls). Position sizing is fixed at $100,000 per trade.
"""
story.append(Paragraph(strategy_text, body_style))
story.append(Spacer(1, 0.2*inch))

# Top 5 Configurations
story.append(Paragraph("Top 5 Configurations (Ranked by System Score)", heading_style))
top5_text = """
All configurations are ranked by System Score (Net Profit × Profit Factor). Higher (less negative) scores 
indicate "better" performance, though all remain unprofitable. The best configuration minimizes losses 
while maintaining the highest profit factor closest to breakeven (1.0).
"""
story.append(Paragraph(top5_text, body_style))
story.append(Spacer(1, 0.1*inch))

top5_df = df.head(5)[['Rank', 'ATRPeriod', 'StopMultiplier', 'TotalTrades', 'NetProfit', 
                       'ProfitFactor', 'WinRate', 'SystemScore']]
top5_df['NetProfit'] = top5_df['NetProfit'].apply(lambda x: f"${x:,.0f}")
top5_df['SystemScore'] = top5_df['SystemScore'].apply(lambda x: f"${x:,.0f}")
top5_df['ProfitFactor'] = top5_df['ProfitFactor'].apply(lambda x: f"{x:.3f}")
top5_df['WinRate'] = top5_df['WinRate'].apply(lambda x: f"{x*100:.2f}%")
top5_df['TotalTrades'] = top5_df['TotalTrades'].apply(lambda x: f"{x:,}")

top5_data = [top5_df.columns.tolist()] + top5_df.values.tolist()
top5_table = Table(top5_data, colWidths=[0.5*inch, 1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch, 0.9*inch, 1.2*inch])
top5_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
]))
story.append(top5_table)
story.append(Spacer(1, 0.2*inch))

# Best Configuration Details
best_row = df.iloc[0]
best_text = f"""
<b>Best Configuration: ATR({int(best_row['ATRPeriod'])}) with {best_row['StopMultiplier']:.1f}× Multiplier</b><br/>
Net Profit: ${best_row['NetProfit']:,.0f} | Profit Factor: {best_row['ProfitFactor']:.3f} | Win Rate: {best_row['WinRate']*100:.2f}%<br/>
Total Trades: {int(best_row['TotalTrades']):,} | Winners: {int(best_row['WinningTrades']):,} | Losers: {int(best_row['LosingTrades']):,}<br/>
Average Win: ${best_row['AvgWin']:,.2f} | Average Loss: ${best_row['AvgLoss']:,.2f} | Win/Loss Ratio: {best_row['AvgWinLossRatio']:.3f}
"""
story.append(Paragraph(best_text, body_style))

story.append(PageBreak())

# Key Findings
story.append(Paragraph("Key Findings & Analysis", heading_style))
findings_text = """
<b>1. All Configurations Unprofitable:</b> 100% of the 32 parameter combinations produced negative net 
profits with profit factors below 1.0. This indicates systematic losses across all parameter settings, 
suggesting that symmetric exit logic is fundamentally incompatible with short positions in this dataset.<br/><br/>

<b>2. Tighter Stops Perform Better:</b> Configurations with 1.5× and 2.0× multipliers consistently rank 
higher than wider stops. As the multiplier increases from 1.5× to 5.0×, losses compound significantly. 
For example, ATR(14) loses $141K at 1.5× but $1.17M at 5.0×. This suggests that cutting losses quickly 
is critical for shorts, though still insufficient for profitability.<br/><br/>

<b>3. Win Rates Cluster Around 49%:</b> All configurations show win rates between 48.6% and 49.3%, 
consistently below 50%. This slight edge against short positions, combined with win/loss ratios near 1.0, 
creates negative expectancy. No configuration achieves the >50% win rate needed for profitability with 
symmetric exits.<br/><br/>

<b>4. Market Bias Evident:</b> The consistent underperformance across all parameters suggests a systematic 
upward market bias during the test period. Comparing to Phase 1 long signals, the best long configuration 
achieved +$753K while the best short configuration lost $84K—a performance gap of $837K using identical 
strategy logic.<br/><br/>

<b>5. Parameter Optimization Insufficient:</b> The fact that even the "best" parameters produce losses 
indicates that parameter optimization alone cannot solve the problem. Shorts likely require fundamentally 
different exit management approaches, such as asymmetric stop/target ratios or trailing stops that lock 
in gains more aggressively.
"""
story.append(Paragraph(findings_text, body_style))

story.append(PageBreak())

# Visualization
story.append(Paragraph("Performance Visualization", heading_style))
viz_text = """
The following heatmaps and 3D surface plot visualize the optimization landscape across all 32 parameter 
combinations. The top row shows System Score (Net Profit × Profit Factor), Net Profit, and Profit Factor 
as 2D heatmaps. The bottom 3D surface plot displays the System Score landscape, revealing how performance 
degrades as the ATR multiplier increases. All visualizations use a red-yellow-green color scheme, with 
green representing better (less negative) performance. Note that even the "greenest" areas remain in 
negative territory, confirming that no profitable configuration exists.
"""
story.append(Paragraph(viz_text, body_style))
story.append(Spacer(1, 0.1*inch))

# Add heatmap image
if HEATMAP_IMAGE.exists():
    img = Image(str(HEATMAP_IMAGE), width=9*inch, height=6.75*inch)
    story.append(img)
else:
    story.append(Paragraph("<i>Heatmap image not found</i>", body_style))

story.append(PageBreak())

# Strategic Implications
story.append(Paragraph("Strategic Implications & Recommendations", heading_style))
implications_text = """
<b>Symmetric Exits Inadequate for Shorts:</b> The symmetric 1:1 risk/reward structure that performed 
moderately well on long signals completely fails on short positions. This suggests that shorts require 
asymmetric exit management, potentially with tighter stops and wider targets to accommodate the different 
volatility characteristics of downward price movements.<br/><br/>

<b>Recommendations for Remaining Strategies:</b><br/>
<b>Strategy 2 - Fixed ATR Asymmetric:</b> Test tighter stops with wider targets (e.g., 1.0× stop, 3.0× target). 
Hypothesis: Shorts need to cut losses quickly but let winners run longer. Priority: HIGH.<br/>
<b>Strategy 3 - ATR Trailing Stop:</b> Test trailing stops that tighten quickly on favorable moves to lock 
in gains faster than for longs. Priority: MEDIUM.<br/>
<b>Strategy 4 - ATR Breakeven Stop:</b> Test aggressive breakeven triggers (e.g., 1.5× ATR move triggers 
breakeven lock) to protect capital quickly. Priority: MEDIUM.<br/><br/>

<b>Consider Abandoning Short Signals:</b> If all four strategies fail to produce profitable short configurations, 
the research team should consider focusing exclusively on long signals for production trading, using shorts 
only for hedging or investigating alternative short entry criteria.
"""
story.append(Paragraph(implications_text, body_style))
story.append(Spacer(1, 0.2*inch))

# Bottom 5 Configurations
story.append(Paragraph("Bottom 5 Configurations (Worst Performers)", heading_style))
bottom5_df = df.tail(5)[['Rank', 'ATRPeriod', 'StopMultiplier', 'TotalTrades', 'NetProfit', 
                          'ProfitFactor', 'WinRate', 'SystemScore']]
bottom5_df['NetProfit'] = bottom5_df['NetProfit'].apply(lambda x: f"${x:,.0f}")
bottom5_df['SystemScore'] = bottom5_df['SystemScore'].apply(lambda x: f"${x:,.0f}")
bottom5_df['ProfitFactor'] = bottom5_df['ProfitFactor'].apply(lambda x: f"{x:.3f}")
bottom5_df['WinRate'] = bottom5_df['WinRate'].apply(lambda x: f"{x*100:.2f}%")
bottom5_df['TotalTrades'] = bottom5_df['TotalTrades'].apply(lambda x: f"{x:,}")

bottom5_data = [bottom5_df.columns.tolist()] + bottom5_df.values.tolist()
bottom5_table = Table(bottom5_data, colWidths=[0.5*inch, 1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch, 0.9*inch, 1.2*inch])
bottom5_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#742a2a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')])
]))
story.append(bottom5_table)

story.append(PageBreak())

# Conclusion
story.append(Paragraph("Conclusion & Next Steps", heading_style))
conclusion_text = """
The Fixed ATR Symmetric strategy, which achieved moderate profitability on long signals (+$753K best case), 
completely fails when applied to short signals (-$84K best case, -$1.17M worst case). All 32 parameter 
combinations produced negative returns with profit factors below 1.0, indicating systematic losses rather 
than a parameter optimization problem.<br/><br/>

The consistent underperformance across all ATR periods and multipliers suggests that symmetric exit logic 
is fundamentally incompatible with short positions in this dataset. Tighter stops (1.5-2.0×) minimize 
losses but cannot achieve profitability. The $837K performance gap between best long and best short 
configurations using identical strategy logic points to either a strong upward market bias or fundamental 
differences in how long and short positions should be managed.<br/><br/>

<b>Immediate Next Steps:</b><br/>
1. Proceed to Strategy 2 (Fixed ATR Asymmetric) with 112 combinations testing asymmetric stop/target ratios<br/>
2. Focus on tighter stops (1.0-2.0×) paired with wider targets (3.0-6.0×) for shorts<br/>
3. Compare results to determine if asymmetric exits can make shorts profitable<br/>
4. If all four strategies fail, recommend abandoning short signals or revising entry criteria<br/><br/>

This report documents Strategy 1 of 4 in Phase 2 (Short Signals). The remaining three strategies 
(Asymmetric, Trailing Stop, Breakeven Stop) will be processed sequentially to determine if alternative 
exit logic can overcome the challenges identified in this symmetric approach.
"""
story.append(Paragraph(conclusion_text, body_style))
story.append(Spacer(1, 0.3*inch))

# Appendix
story.append(Paragraph("Appendix: Data Files", heading_style))
appendix_data = [
    ['File Name', 'Description', 'Rows'],
    ['Fixed_ATR_Symmetric_Short_Performance.csv', 'Performance summary (32 combinations)', '32'],
    ['Fixed_ATR_Symmetric_Short_All_Trades.parquet', 'Detailed trade logs', '1,921,480'],
    ['Fixed_ATR_Symmetric_Short_with_3D.png', 'Heatmaps + 3D surface plot', 'N/A']
]
appendix_table = Table(appendix_data, colWidths=[3.5*inch, 3.5*inch, 1*inch])
appendix_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
]))
story.append(appendix_table)

# Build PDF
print("\n[3/4] Building PDF...")
doc.build(story)
print(f"✓ PDF created: {OUTPUT_PDF}")

# Print summary
print("\n[4/4] Summary")
print("="*80)
print(f"Total Pages: ~8")
print(f"Total Configurations: {len(df)}")
print(f"Best Configuration: ATR({int(df.iloc[0]['ATRPeriod'])}) {df.iloc[0]['StopMultiplier']:.1f}×")
print(f"Best Net Profit: ${df.iloc[0]['NetProfit']:,.0f}")
print(f"Worst Net Profit: ${df.iloc[-1]['NetProfit']:,.0f}")
print("="*80)
print("\n✓ Report generation complete!")
