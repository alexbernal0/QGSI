#!/usr/bin/env python3.11
"""
Generate TradeStation-style Performance Report for Production Portfolio
"""

import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

print("="*80)
print("GENERATING TRADESTATION-STYLE PERFORMANCE REPORT")
print("="*80)

# Load data
print("\n[1/4] Loading data...")
trades_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
equity_df = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
summary_df = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Summary.csv')

print(f"✓ Loaded {len(trades_df):,} trades")

# Calculate additional metrics
print("\n[2/4] Calculating metrics...")

trades_df['EntryTime'] = pd.to_datetime(trades_df['EntryTime'])
trades_df['ExitTime'] = pd.to_datetime(trades_df['ExitTime'])
equity_df['Timestamp'] = pd.to_datetime(equity_df['Timestamp'])

# Drawdown analysis
equity_df['Peak'] = equity_df['Equity'].cummax()
equity_df['Drawdown'] = (equity_df['Equity'] - equity_df['Peak']) / equity_df['Peak'] * 100
max_drawdown = equity_df['Drawdown'].min()
max_dd_date = equity_df.loc[equity_df['Drawdown'].idxmin(), 'Timestamp']

# Consecutive wins/losses
trades_df['IsWin'] = trades_df['NetProfit'] > 0
wins_losses = trades_df['IsWin'].astype(int).diff().ne(0).cumsum()
consecutive_counts = trades_df.groupby(wins_losses)['IsWin'].agg(['sum', 'count'])
max_consecutive_wins = consecutive_counts[consecutive_counts['sum'] == consecutive_counts['count']]['count'].max()
max_consecutive_losses = consecutive_counts[consecutive_counts['sum'] == 0]['count'].max()

# Win/Loss streaks
trades_df['Streak'] = (trades_df['IsWin'] != trades_df['IsWin'].shift()).cumsum()
streak_stats = trades_df.groupby('Streak').agg({
    'NetProfit': 'sum',
    'IsWin': 'first'
})

# Trade duration analysis
trades_df['Duration'] = (trades_df['ExitTime'] - trades_df['EntryTime']).dt.total_seconds() / 60  # minutes
avg_duration = trades_df['Duration'].mean()

# Monthly analysis
trades_df['Month'] = trades_df['EntryTime'].dt.to_period('M')
monthly_stats = trades_df.groupby('Month').agg({
    'NetProfit': 'sum',
    'Symbol': 'count'
}).rename(columns={'Symbol': 'Trades'})

winning_trades = trades_df[trades_df['NetProfit'] > 0]
losing_trades = trades_df[trades_df['NetProfit'] < 0]

print("✓ Metrics calculated")

# Create PDF
print("\n[3/4] Generating PDF report...")

pdf_file = '/home/ubuntu/stage4_optimization/Production_Portfolio_Performance_Report.pdf'
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

# Title
story.append(Paragraph("PRODUCTION PORTFOLIO PERFORMANCE REPORT", title_style))
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
perf_data = [
    ['Metric', 'Value'],
    ['Final Equity', f"${summary_df['FinalEquity'].iloc[0]:,.2f}"],
    ['Net Profit', f"${summary_df['NetProfit'].iloc[0]:,.2f}"],
    ['Total Return', f"{summary_df['TotalReturn'].iloc[0]:.2f}%"],
    ['Max Drawdown', f"{max_drawdown:.2f}%"],
    ['Max DD Date', max_dd_date.strftime('%Y-%m-%d')],
    ['Profit Factor', f"{summary_df['ProfitFactor'].iloc[0]:.3f}"],
]

perf_table = Table(perf_data, colWidths=[3*inch, 3*inch])
perf_table.setStyle(TableStyle([
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
story.append(perf_table)
story.append(Spacer(1, 0.2*inch))

# Trade Statistics
story.append(Paragraph("Trade Statistics", heading_style))
trade_data = [
    ['Metric', 'Value'],
    ['Total Trades', f"{summary_df['TotalTrades'].iloc[0]:,.0f}"],
    ['Winning Trades', f"{summary_df['WinningTrades'].iloc[0]:,.0f} ({summary_df['WinRate'].iloc[0]:.1f}%)"],
    ['Losing Trades', f"{summary_df['LosingTrades'].iloc[0]:,.0f} ({100-summary_df['WinRate'].iloc[0]:.1f}%)"],
    ['Gross Profit', f"${summary_df['GrossProfit'].iloc[0]:,.2f}"],
    ['Gross Loss', f"${summary_df['GrossLoss'].iloc[0]:,.2f}"],
    ['Average Win', f"${summary_df['AvgWin'].iloc[0]:,.2f}"],
    ['Average Loss', f"${summary_df['AvgLoss'].iloc[0]:,.2f}"],
    ['Largest Win', f"${summary_df['LargestWin'].iloc[0]:,.2f}"],
    ['Largest Loss', f"${summary_df['LargestLoss'].iloc[0]:,.2f}"],
    ['Avg Trade Duration', f"{avg_duration:.0f} minutes"],
    ['Max Consecutive Wins', f"{int(max_consecutive_wins)}"],
    ['Max Consecutive Losses', f"{int(max_consecutive_losses)}"],
]

trade_table = Table(trade_data, colWidths=[3*inch, 3*inch])
trade_table.setStyle(TableStyle([
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
story.append(trade_table)
story.append(Spacer(1, 0.2*inch))

# Signal Utilization
story.append(Paragraph("Signal Utilization", heading_style))
signal_data = [
    ['Metric', 'Value'],
    ['Baseline Signals', f"{summary_df['BaselineSignals'].iloc[0]:,.0f}"],
    ['Signals Traded', f"{summary_df['TotalTrades'].iloc[0]:,.0f}"],
    ['Signals Skipped', f"{summary_df['SignalsSkipped'].iloc[0]:,.0f}"],
    ['Utilization Rate', f"{(summary_df['TotalTrades'].iloc[0] / summary_df['BaselineSignals'].iloc[0] * 100):.1f}%"],
]

signal_table = Table(signal_data, colWidths=[3*inch, 3*inch])
signal_table.setStyle(TableStyle([
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
story.append(signal_table)
story.append(Spacer(1, 0.2*inch))

# Monthly Performance
story.append(Paragraph("Monthly Performance", heading_style))
monthly_data = [['Month', 'Trades', 'Net Profit', 'Return %']]

for month, row in monthly_stats.iterrows():
    # Calculate month return
    month_start_equity = equity_df[equity_df['Timestamp'].dt.to_period('M') == month]['Equity'].iloc[0] if len(equity_df[equity_df['Timestamp'].dt.to_period('M') == month]) > 0 else 1000000
    month_end_equity = equity_df[equity_df['Timestamp'].dt.to_period('M') == month]['Equity'].iloc[-1] if len(equity_df[equity_df['Timestamp'].dt.to_period('M') == month]) > 0 else 1000000
    month_return = ((month_end_equity - month_start_equity) / month_start_equity * 100)
    
    monthly_data.append([
        str(month),
        f"{int(row['Trades'])}",
        f"${row['NetProfit']:,.2f}",
        f"{month_return:.2f}%"
    ])

monthly_table = Table(monthly_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
monthly_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(monthly_table)
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

print("\n[4/4] Complete!")
print("="*80)
print(f"Report saved to: {pdf_file}")
print("="*80)
