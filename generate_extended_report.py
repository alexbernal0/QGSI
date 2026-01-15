#!/usr/bin/env python3.11
"""
Generate Extended Performance Report with Comprehensive Metrics
"""

import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

print("="*80)
print("GENERATING EXTENDED PERFORMANCE REPORT")
print("="*80)

# Load data
print("\n[1/4] Loading data...")
trades_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
summary_df = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Summary.csv')
extended_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv', index_col=0)
drawdowns = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Drawdowns.csv')
monthly_table = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Table.csv', index_col=0)

print(f"✓ Loaded all data files")

# Create PDF
print("\n[2/4] Generating PDF report...")

pdf_file = '/home/ubuntu/stage4_optimization/Production_Portfolio_Extended_Report.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
story = []
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=8,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

small_heading_style = ParagraphStyle(
    'SmallHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=6,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

# Title Page
story.append(Paragraph("PRODUCTION PORTFOLIO", title_style))
story.append(Paragraph("EXTENDED PERFORMANCE REPORT", title_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("QGSI Trading Strategy - LONG Signals", styles['Normal']))
story.append(Paragraph(f"ATR Trailing Stop (Period: 30, Multiplier: 5.0, Max Bars: 20)", styles['Normal']))
story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Portfolio Configuration
story.append(Paragraph("Portfolio Configuration", heading_style))
config_data = [
    ['Parameter', 'Value'],
    ['Starting Capital', f"${summary_df['StartingCapital'].iloc[0]:,.2f}"],
    ['Max Concurrent Positions', f"{int(summary_df['MaxPositions'].iloc[0])}"],
    ['Position Sizing', f"{summary_df['PositionSizePct'].iloc[0]:.0f}% of Current Equity"],
    ['Signal Priority', 'First-Come-First-Served (ATR Tiebreaker)'],
    ['Data Period', f"{trades_df['EntryTime'].min().strftime('%Y-%m-%d')} to {trades_df['ExitTime'].max().strftime('%Y-%m-%d')}"],
    ['Total Trading Days', f"{len(equity_df['Timestamp'].dt.date.unique())}"],
]

config_table = Table(config_data, colWidths=[3*inch, 3*inch])
config_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(config_table)
story.append(Spacer(1, 0.2*inch))

# Performance Summary
story.append(Paragraph("Performance Summary", heading_style))

def format_metric(value):
    """Format metric value for display"""
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    elif isinstance(value, (float, np.floating)):
        if np.isinf(value):
            return "∞"
        elif abs(value) > 1000:
            return f"{value:,.2f}"
        elif abs(value) > 10:
            return f"{value:.2f}"
        else:
            return f"{value:.4f}"
    else:
        return str(value)

perf_data = [['Metric', 'Value']]
perf_metrics = [
    ('Final Equity', f"${summary_df['FinalEquity'].iloc[0]:,.2f}"),
    ('Net Profit', f"${summary_df['NetProfit'].iloc[0]:,.2f}"),
    ('Total Return', f"{extended_metrics.loc['Cumulative Return', 'Value']:.2f}%"),
    ('CAGR', f"{extended_metrics.loc['CAGR', 'Value']:.2f}%"),
    ('Sharpe Ratio', f"{extended_metrics.loc['Sharpe', 'Value']:.4f}"),
    ('Sortino Ratio', f"{extended_metrics.loc['Sortino', 'Value']:.4f}"),
    ('Calmar Ratio', f"{extended_metrics.loc['Calmar', 'Value']:.2f}"),
    ('Max Drawdown', f"{extended_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Volatility (ann.)', f"{extended_metrics.loc['Volatility (ann.)', 'Value']:.2f}%"),
    ('Profit Factor (Daily)', f"{extended_metrics.loc['Profit Factor', 'Value']:.4f}"),
]

for metric, value in perf_metrics:
    perf_data.append([metric, value])

perf_table = Table(perf_data, colWidths=[3.5*inch, 2.5*inch])
perf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(perf_table)
story.append(Spacer(1, 0.2*inch))

# Risk-Adjusted Metrics
story.append(Paragraph("Risk-Adjusted Performance", heading_style))
risk_data = [['Metric', 'Value']]
risk_metrics = [
    ('Smart Sharpe', extended_metrics.loc['Smart Sharpe', 'Value']),
    ('Smart Sortino', extended_metrics.loc['Smart Sortino', 'Value']),
    ('Prob. Sharpe Ratio', f"{extended_metrics.loc['Prob. Sharpe Ratio', 'Value']:.2f}%"),
    ('Omega Ratio', extended_metrics.loc['Omega', 'Value']),
    ('Recovery Factor', extended_metrics.loc['Recovery Factor', 'Value']),
    ('Ulcer Index', extended_metrics.loc['Ulcer Index', 'Value']),
    ('Serenity Index', extended_metrics.loc['Serenity Index', 'Value']),
]

for metric, value in risk_metrics:
    risk_data.append([metric, format_metric(value)])

risk_table = Table(risk_data, colWidths=[3.5*inch, 2.5*inch])
risk_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(risk_table)
story.append(Spacer(1, 0.2*inch))

# Return Distribution
story.append(Paragraph("Return Distribution", heading_style))
dist_data = [['Metric', 'Value']]
dist_metrics = [
    ('Expected Daily', f"{extended_metrics.loc['Expected Daily', 'Value']:.4f}%"),
    ('Expected Monthly', f"{extended_metrics.loc['Expected Monthly', 'Value']:.2f}%"),
    ('Best Day', f"{extended_metrics.loc['Best Day', 'Value']:.2f}%"),
    ('Worst Day', f"{extended_metrics.loc['Worst Day', 'Value']:.2f}%"),
    ('Best Month', f"{extended_metrics.loc['Best Month', 'Value']:.2f}%"),
    ('Worst Month', f"{extended_metrics.loc['Worst Month', 'Value']:.2f}%"),
    ('Skewness', extended_metrics.loc['Skew', 'Value']),
    ('Kurtosis', extended_metrics.loc['Kurtosis', 'Value']),
]

for metric, value in dist_metrics:
    if isinstance(value, str):
        dist_data.append([metric, value])
    else:
        dist_data.append([metric, format_metric(value)])

dist_table = Table(dist_data, colWidths=[3.5*inch, 2.5*inch])
dist_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(dist_table)
story.append(PageBreak())

# Drawdown Analysis
story.append(Paragraph("Drawdown Analysis", heading_style))
dd_data = [['Metric', 'Value']]
dd_metrics = [
    ('Max Drawdown', f"{extended_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Avg. Drawdown', f"{extended_metrics.loc['Avg. Drawdown', 'Value']:.2f}%"),
    ('Longest DD Days', f"{int(extended_metrics.loc['Longest DD Days', 'Value'])}"),
    ('Avg. Drawdown Days', f"{extended_metrics.loc['Avg. Drawdown Days', 'Value']:.1f}"),
]

for metric, value in dd_metrics:
    dd_data.append([metric, value])

dd_table = Table(dd_data, colWidths=[3.5*inch, 2.5*inch])
dd_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(dd_table)
story.append(Spacer(1, 0.2*inch))

# Top 5 Worst Drawdowns
story.append(Paragraph("Top 5 Worst Drawdowns", small_heading_style))
worst_dd = drawdowns.head(5)
dd_detail_data = [['Rank', 'Drawdown', 'Days', 'Started', 'Recovered']]
for i, row in worst_dd.iterrows():
    dd_detail_data.append([
        str(i+1),
        f"{row['Drawdown']:.2f}%",
        str(int(row['Days'])),
        row['Started'][:10],
        row['Recovered'][:10]
    ])

dd_detail_table = Table(dd_detail_data, colWidths=[0.6*inch, 1.2*inch, 0.8*inch, 1.7*inch, 1.7*inch])
dd_detail_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
]))
story.append(dd_detail_table)
story.append(Spacer(1, 0.2*inch))

# Win/Loss Statistics
story.append(Paragraph("Win/Loss Statistics", heading_style))
winloss_data = [['Metric', 'Value']]
winloss_metrics = [
    ('Win Days %', f"{extended_metrics.loc['Win Days %', 'Value']:.2f}%"),
    ('Win Month %', f"{extended_metrics.loc['Win Month %', 'Value']:.2f}%"),
    ('Win Quarter %', f"{extended_metrics.loc['Win Quarter %', 'Value']:.2f}%"),
    ('Avg. Up Month', f"{extended_metrics.loc['Avg. Up Month', 'Value']:.2f}%"),
    ('Avg. Down Month', f"{extended_metrics.loc['Avg. Down Month', 'Value']:.2f}%"),
    ('Payoff Ratio', extended_metrics.loc['Payoff Ratio', 'Value']),
    ('Gain/Pain Ratio', extended_metrics.loc['Gain/Pain Ratio', 'Value']),
    ('CPC Index', extended_metrics.loc['CPC Index', 'Value']),
    ('Tail Ratio', extended_metrics.loc['Tail Ratio', 'Value']),
]

for metric, value in winloss_metrics:
    if isinstance(value, str):
        winloss_data.append([metric, value])
    else:
        winloss_data.append([metric, format_metric(value)])

winloss_table = Table(winloss_data, colWidths=[3.5*inch, 2.5*inch])
winloss_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(winloss_table)
story.append(Spacer(1, 0.2*inch))

# Risk Metrics
story.append(Paragraph("Risk Metrics", heading_style))
risk2_data = [['Metric', 'Value']]
risk2_metrics = [
    ('Daily Value-at-Risk', f"{extended_metrics.loc['Daily Value-at-Risk', 'Value']:.4f}%"),
    ('Expected Shortfall (cVaR)', f"{extended_metrics.loc['Expected Shortfall (cVaR)', 'Value']:.4f}%"),
    ('Kelly Criterion', f"{extended_metrics.loc['Kelly Criterion', 'Value']:.2f}%"),
    ('Outlier Win Ratio', extended_metrics.loc['Outlier Win Ratio', 'Value']),
    ('Outlier Loss Ratio', extended_metrics.loc['Outlier Loss Ratio', 'Value']),
]

for metric, value in risk2_metrics:
    if isinstance(value, str):
        risk2_data.append([metric, value])
    else:
        risk2_data.append([metric, format_metric(value)])

risk2_table = Table(risk2_data, colWidths=[3.5*inch, 2.5*inch])
risk2_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(risk2_table)
story.append(PageBreak())

# Monthly Performance Table
story.append(Paragraph("Monthly Performance Grid", heading_style))
monthly_data = [['Year'] + list(monthly_table.columns)]
for year, row in monthly_table.iterrows():
    monthly_data.append([str(year)] + [f"{v:.2f}%" if not pd.isna(v) else "-" for v in row])

col_widths = [0.6*inch] + [0.6*inch] * len(monthly_table.columns)
monthly_perf_table = Table(monthly_data, colWidths=col_widths)
monthly_perf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 8),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 7),
]))
story.append(monthly_perf_table)
story.append(Spacer(1, 0.2*inch))

# Trade Statistics (from original report)
story.append(Paragraph("Trade Statistics", heading_style))
trade_data = [['Metric', 'Value']]
trade_metrics = [
    ('Total Trades', f"{summary_df['TotalTrades'].iloc[0]:,.0f}"),
    ('Winning Trades', f"{summary_df['WinningTrades'].iloc[0]:,.0f} ({summary_df['WinRate'].iloc[0]:.1f}%)"),
    ('Losing Trades', f"{summary_df['LosingTrades'].iloc[0]:,.0f} ({100-summary_df['WinRate'].iloc[0]:.1f}%)"),
    ('Gross Profit', f"${summary_df['GrossProfit'].iloc[0]:,.2f}"),
    ('Gross Loss', f"${summary_df['GrossLoss'].iloc[0]:,.2f}"),
    ('Average Win', f"${summary_df['AvgWin'].iloc[0]:,.2f}"),
    ('Average Loss', f"${summary_df['AvgLoss'].iloc[0]:,.2f}"),
    ('Largest Win', f"${summary_df['LargestWin'].iloc[0]:,.2f}"),
    ('Largest Loss', f"${summary_df['LargestLoss'].iloc[0]:,.2f}"),
]

for metric, value in trade_metrics:
    trade_data.append([metric, value])

trade_table = Table(trade_data, colWidths=[3.5*inch, 2.5*inch])
trade_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(trade_table)
story.append(PageBreak())

# Add charts
story.append(Paragraph("Equity Curve", heading_style))
equity_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Equity_Curve.png', width=7*inch, height=5*inch)
story.append(equity_img)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("Monthly Returns", heading_style))
monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Returns.png', width=7*inch, height=3.5*inch)
story.append(monthly_img)

# Build PDF
doc.build(story)
print(f"✓ PDF report generated: {pdf_file}")

print("\n[3/4] Report statistics...")
print(f"  Total metrics calculated: {len(extended_metrics)}")
print(f"  Drawdown periods analyzed: {len(drawdowns)}")
print(f"  Monthly data points: {len(monthly_table)}")

print("\n[4/4] Complete!")
print("="*80)
print(f"Extended report saved to: {pdf_file}")
print("="*80)
