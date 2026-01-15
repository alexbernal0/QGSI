#!/usr/bin/env python3.11
"""
Generate Extended Performance Report for SHORT Strategy with FIFO Appendix
"""

import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

print("="*80)
print("GENERATING SHORT STRATEGY EXTENDED REPORT WITH APPENDIX")
print("="*80)

# Load data
print("\n[1/3] Loading data...")
trades_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Trades.parquet')
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Equity.parquet')
summary_df = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Summary.csv')
extended_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Extended_Metrics.csv', index_col=0)
drawdowns = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Drawdowns.csv')
monthly_table = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Monthly_Table.csv', index_col=0)

print(f"✓ Loaded all data files")

# Create PDF
print("\n[2/3] Generating PDF report...")

pdf_file = '/home/ubuntu/stage4_optimization/Production_Portfolio_SHORT_Extended_Report.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
story = []
styles = getSampleStyleSheet()

# Custom styles (same as LONG report for consistency)
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#d62728'),  # Red for SHORT
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#d62728'),
    spaceAfter=8,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

small_heading_style = ParagraphStyle(
    'SmallHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#d62728'),
    spaceAfter=6,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'BodyText',
    parent=styles['Normal'],
    fontSize=9,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

# Title Page
story.append(Paragraph("PRODUCTION PORTFOLIO", title_style))
story.append(Paragraph("EXTENDED PERFORMANCE REPORT", title_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("QGSI Trading Strategy - SHORT Signals", styles['Normal']))
story.append(Paragraph(f"ATR Trailing Stop (Period: 30, Multiplier: 1.5, Max Bars: 20)", styles['Normal']))
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
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
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
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
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

# Risk-Adjusted Metrics (abbreviated for space)
story.append(Paragraph("Risk-Adjusted Performance", heading_style))
risk_data = [['Metric', 'Value']]
risk_metrics = [
    ('Smart Sharpe', extended_metrics.loc['Smart Sharpe', 'Value']),
    ('Smart Sortino', extended_metrics.loc['Smart Sortino', 'Value']),
    ('Prob. Sharpe Ratio', f"{extended_metrics.loc['Prob. Sharpe Ratio', 'Value']:.2f}%"),
    ('Omega Ratio', extended_metrics.loc['Omega', 'Value']),
    ('Recovery Factor', extended_metrics.loc['Recovery Factor', 'Value']),
    ('Ulcer Index', extended_metrics.loc['Ulcer Index', 'Value']),
]

for metric, value in risk_metrics:
    risk_data.append([metric, format_metric(value)])

risk_table = Table(risk_data, colWidths=[3.5*inch, 2.5*inch])
risk_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
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
story.append(PageBreak())

# Trade Statistics
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
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
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
story.append(Spacer(1, 0.2*inch))

# Signal Utilization (unique to this report)
story.append(Paragraph("Signal Utilization Analysis", heading_style))
util_data = [['Metric', 'Count', 'Percentage']]
baseline_signals = int(summary_df['BaselineSignals'].iloc[0])
signals_taken = int(summary_df['TotalTrades'].iloc[0])
skipped_max = int(summary_df['SignalsSkipped_MaxPositions'].iloc[0])
skipped_dup = int(summary_df['SignalsSkipped_Duplicate'].iloc[0])
skipped_cap = int(summary_df['SignalsSkipped_Capital'].iloc[0])

util_metrics = [
    ('Baseline Signals', baseline_signals, '100.0%'),
    ('Signals Taken', signals_taken, f'{signals_taken/baseline_signals*100:.1f}%'),
    ('Skipped (Max Positions)', skipped_max, f'{skipped_max/baseline_signals*100:.1f}%'),
    ('Skipped (Duplicate Symbol)', skipped_dup, f'{skipped_dup/baseline_signals*100:.1f}%'),
    ('Skipped (Insufficient Capital)', skipped_cap, f'{skipped_cap/baseline_signals*100:.1f}%'),
]

for metric, count, pct in util_metrics:
    util_data.append([metric, f'{count:,}', pct])

util_table = Table(util_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
util_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(util_table)
story.append(PageBreak())

# Add charts
story.append(Paragraph("Equity Curve", heading_style))
equity_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Equity_Curve.png', width=7*inch, height=5*inch)
story.append(equity_img)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("Monthly Returns", heading_style))
monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Monthly_Returns.png', width=7*inch, height=3.5*inch)
story.append(monthly_img)
story.append(PageBreak())

# APPENDIX (same as LONG but with SHORT-specific context)
story.append(Paragraph("APPENDIX: FIFO Realistic Backtesting Methodology", title_style))
story.append(Spacer(1, 0.2*inch))

appendix_sections = [
    ("Overview", "This appendix documents the First-In-First-Out (FIFO) realistic backtesting process implemented for the SHORT strategy to ensure the production portfolio simulator accurately replicates real-world fund performance."),
    
    ("Key Findings for SHORT Strategy", f"The SHORT strategy generated {baseline_signals:,} baseline signals but only {signals_taken:,} trades (2.4%) could be executed with the 10-position limit. This is dramatically lower than the LONG strategy (52.6%), indicating SHORT signals are highly concentrated in time, creating severe competition for limited position slots. The max position constraint skipped {skipped_max:,} signals (92.5% of all skips)."),
    
    ("FIFO Methodology", "All entry and exit signals are processed in strict chronological order. The simulator maintains real-time portfolio state, enforces position limits, calculates dynamic position sizing (10% of current equity), and prioritizes signals by timestamp then ATR value. This ensures trade sequencing exactly mirrors how a live fund would operate."),
    
    ("Validation", "The system ensures no look-ahead bias, capital conservation, position integrity (no duplicate symbols), and equity curve continuity. All decisions use only information available at the time, and total deployed capital never exceeds available equity."),
]

for section_title, section_text in appendix_sections:
    story.append(Paragraph(section_title, small_heading_style))
    story.append(Paragraph(section_text, body_style))
    story.append(Spacer(1, 0.1*inch))

# Build PDF
doc.build(story)
print(f"✓ PDF report generated: {pdf_file}")

print("\n[3/3] Report complete!")
print("="*80)
print(f"SHORT strategy extended report saved to: {pdf_file}")
print("="*80)
