"""
QGSI: Professional PDF Report Generator
========================================

Purpose: Create a clean, crisp PDF report combining equity curve chart
         and performance statistics for easy sharing and archiving.

Author: QGSI Research Team
Date: 2026-01-11
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import duckdb
import pandas as pd
from datetime import datetime
from pathlib import Path

MOTHERDUCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs"

SYMBOL = "AAPL"
STRATEGY_NAME = "Fixed_ATR_SL_Tgt"
STARTING_CAPITAL = 100000.0

print("=" * 80)
print(f"GENERATING PDF REPORT: {SYMBOL} - {STRATEGY_NAME}")
print("=" * 80)

# Load data
conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
query = f"""
SELECT *
FROM QGSI.Fixed_ATR_SL_Tgt_all_trades
WHERE Symbol = '{SYMBOL}'
ORDER BY EntryTime
"""
trades = conn.execute(query).df()
conn.close()

print(f"\n✓ Loaded {len(trades)} trades for {SYMBOL}")

# Calculate metrics
trades['CumulativeProfit'] = trades['NetProfit'].cumsum()
trades['Equity'] = STARTING_CAPITAL + trades['CumulativeProfit']
trades['Peak'] = trades['Equity'].cummax()
trades['Drawdown'] = trades['Equity'] - trades['Peak']
trades['DrawdownPct'] = (trades['Drawdown'] / trades['Peak'] * 100)

total_net_profit = trades['NetProfit'].sum()
total_trades = len(trades)
winning_trades = len(trades[trades['NetProfit'] > 0])
losing_trades = len(trades[trades['NetProfit'] <= 0])
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

gross_profit = trades[trades['NetProfit'] > 0]['NetProfit'].sum()
gross_loss = abs(trades[trades['NetProfit'] <= 0]['NetProfit'].sum())
profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

avg_trade = total_net_profit / total_trades if total_trades > 0 else 0
avg_winning_trade = trades[trades['NetProfit'] > 0]['NetProfit'].mean() if winning_trades > 0 else 0
avg_losing_trade = trades[trades['NetProfit'] <= 0]['NetProfit'].mean() if losing_trades > 0 else 0

largest_winning_trade = trades['NetProfit'].max()
largest_losing_trade = trades['NetProfit'].min()

max_drawdown = trades['Drawdown'].min()
max_drawdown_pct = trades['DrawdownPct'].min()

trades['IsWin'] = trades['NetProfit'] > 0
trades['WinStreak'] = trades['IsWin'].groupby((trades['IsWin'] != trades['IsWin'].shift()).cumsum()).cumsum()
trades['LossStreak'] = (~trades['IsWin']).groupby((trades['IsWin'] != trades['IsWin'].shift()).cumsum()).cumsum()
max_consec_winners = trades['WinStreak'].max()
max_consec_losers = trades['LossStreak'].max()

avg_bars_in_trade = trades['BarsInTrade'].mean()
avg_bars_winning = trades[trades['NetProfit'] > 0]['BarsInTrade'].mean() if winning_trades > 0 else 0
avg_bars_losing = trades[trades['NetProfit'] <= 0]['BarsInTrade'].mean() if losing_trades > 0 else 0

exit_reason_counts = trades['ExitReason'].value_counts()
signal_type_counts = trades['SignalType'].value_counts()

print("✓ Metrics calculated")

# Create PDF
output_dir = Path('/home/ubuntu/stage4_reports')
pdf_path = output_dir / f'{SYMBOL}_{STRATEGY_NAME}_Performance_Report.pdf'

doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=0.5*inch,
    leftMargin=0.5*inch,
    topMargin=0.5*inch,
    bottomMargin=0.5*inch
)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()

# Custom styles with smaller fonts
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Normal'],
    fontSize=10,
    textColor=colors.HexColor('#666666'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=11,
    textColor=colors.HexColor('#2E86AB'),
    spaceAfter=6,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

small_text = ParagraphStyle(
    'SmallText',
    parent=styles['Normal'],
    fontSize=7,
    textColor=colors.HexColor('#333333'),
    fontName='Helvetica'
)

# Title
elements.append(Paragraph(f"<b>{SYMBOL} Trading Strategy Performance Report</b>", title_style))
elements.append(Paragraph(f"Strategy: {STRATEGY_NAME} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
elements.append(Spacer(1, 0.1*inch))

# Equity curve image
chart_path = output_dir / f'{SYMBOL}_{STRATEGY_NAME}_equity_curve.png'
if chart_path.exists():
    img = Image(str(chart_path), width=7*inch, height=4.67*inch)
    elements.append(img)
    elements.append(Spacer(1, 0.15*inch))

# Overall Performance Summary
elements.append(Paragraph("<b>Overall Performance Summary</b>", heading_style))

perf_data = [
    ['Starting Capital', f'${STARTING_CAPITAL:,.2f}', 'Ending Capital', f'${trades["Equity"].iloc[-1]:,.2f}'],
    ['Net Profit', f'${total_net_profit:,.2f}', 'Net Profit %', f'{(total_net_profit/STARTING_CAPITAL*100):.2f}%'],
    ['Gross Profit', f'${gross_profit:,.2f}', 'Gross Loss', f'${-gross_loss:,.2f}'],
    ['Profit Factor', f'{profit_factor:.2f}', 'Total Trades', f'{total_trades:,}'],
]

perf_table = Table(perf_data, colWidths=[1.5*inch, 1.25*inch, 1.5*inch, 1.25*inch])
perf_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(perf_table)
elements.append(Spacer(1, 0.12*inch))

# Trade Analysis
elements.append(Paragraph("<b>Trade Analysis</b>", heading_style))

trade_data = [
    ['Winning Trades', f'{winning_trades:,} ({win_rate:.1f}%)', 'Losing Trades', f'{losing_trades:,} ({100-win_rate:.1f}%)'],
    ['Avg Trade', f'${avg_trade:,.2f}', 'Avg Win', f'${avg_winning_trade:,.2f}'],
    ['Avg Loss', f'${avg_losing_trade:,.2f}', 'Win/Loss Ratio', f'{abs(avg_winning_trade/avg_losing_trade):.2f}'],
    ['Largest Win', f'${largest_winning_trade:,.2f}', 'Largest Loss', f'${largest_losing_trade:,.2f}'],
    ['Max Consec Wins', f'{max_consec_winners:,}', 'Max Consec Losses', f'{max_consec_losers:,}'],
]

trade_table = Table(trade_data, colWidths=[1.5*inch, 1.25*inch, 1.5*inch, 1.25*inch])
trade_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(trade_table)
elements.append(Spacer(1, 0.12*inch))

# Two-column layout for remaining sections
# Time & Drawdown Analysis
elements.append(Paragraph("<b>Time & Drawdown Analysis</b>", heading_style))

time_dd_data = [
    ['Avg Bars in Trade', f'{avg_bars_in_trade:.1f}', 'Max Drawdown', f'${max_drawdown:,.2f}'],
    ['Avg Bars (Wins)', f'{avg_bars_winning:.1f}', 'Max DD %', f'{max_drawdown_pct:.2f}%'],
    ['Avg Bars (Losses)', f'{avg_bars_losing:.1f}', '', ''],
]

time_dd_table = Table(time_dd_data, colWidths=[1.5*inch, 1.25*inch, 1.5*inch, 1.25*inch])
time_dd_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(time_dd_table)
elements.append(Spacer(1, 0.12*inch))

# Exit Reason & Signal Type Distribution
elements.append(Paragraph("<b>Exit Reason Distribution</b>", heading_style))

exit_data = [['Exit Reason', 'Count', 'Percentage']]
for reason, count in exit_reason_counts.items():
    pct = count / total_trades * 100
    exit_data.append([reason, f'{count:,}', f'{pct:.1f}%'])

exit_table = Table(exit_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
exit_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(exit_table)
elements.append(Spacer(1, 0.12*inch))

# Signal Type Performance
elements.append(Paragraph("<b>Signal Type Performance</b>", heading_style))

sig_data = [['Signal Type', 'Trades', 'Total P&L', 'Win Rate']]
for sig_type, count in signal_type_counts.items():
    pct = count / total_trades * 100
    sig_profit = trades[trades['SignalType'] == sig_type]['NetProfit'].sum()
    sig_win_rate = len(trades[(trades['SignalType'] == sig_type) & (trades['NetProfit'] > 0)]) / count * 100
    sig_data.append([sig_type, f'{count:,}', f'${sig_profit:,.2f}', f'{sig_win_rate:.1f}%'])

sig_table = Table(sig_data, colWidths=[1.5*inch, 1.25*inch, 1.5*inch, 1.25*inch])
sig_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(sig_table)
elements.append(Spacer(1, 0.12*inch))

# Path Group Analysis
elements.append(Paragraph("<b>Path Group Analysis</b>", heading_style))

pg_data = [['Path Group', 'Trades', 'Total P&L', 'Avg P&L', 'Win Rate']]
for pg in trades['PathGroup'].unique():
    pg_trades = trades[trades['PathGroup'] == pg]
    pg_count = len(pg_trades)
    pg_profit = pg_trades['NetProfit'].sum()
    pg_avg = pg_trades['NetProfit'].mean()
    pg_win_rate = len(pg_trades[pg_trades['NetProfit'] > 0]) / pg_count * 100
    pg_data.append([pg, f'{pg_count:,}', f'${pg_profit:,.2f}', f'${pg_avg:,.2f}', f'{pg_win_rate:.1f}%'])

pg_table = Table(pg_data, colWidths=[1.5*inch, 0.9*inch, 1.2*inch, 1.0*inch, 0.9*inch])
pg_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(pg_table)
elements.append(Spacer(1, 0.12*inch))

# Signal Count Analysis
elements.append(Paragraph("<b>Signal Count Analysis</b>", heading_style))

sc_data = [['Signal Count', 'Trades', 'Total P&L', 'Avg P&L', 'Win Rate']]
for sc in sorted(trades['SignalCount'].unique()):
    sc_trades = trades[trades['SignalCount'] == sc]
    sc_count = len(sc_trades)
    sc_profit = sc_trades['NetProfit'].sum()
    sc_avg = sc_trades['NetProfit'].mean()
    sc_win_rate = len(sc_trades[sc_trades['NetProfit'] > 0]) / sc_count * 100
    sc_data.append([f'{sc}', f'{sc_count:,}', f'${sc_profit:,.2f}', f'${sc_avg:,.2f}', f'{sc_win_rate:.1f}%'])

sc_table = Table(sc_data, colWidths=[1.2*inch, 0.9*inch, 1.2*inch, 1.0*inch, 0.9*inch])
sc_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(sc_table)

# Build PDF
doc.build(elements)

print(f"\n✓ PDF report generated: {pdf_path}")
print("\n" + "=" * 80)
print("PDF REPORT COMPLETE")
print("=" * 80)
print(f"\n📄 File: {pdf_path}")
print(f"📊 Pages: Professional single-page layout")
print(f"📈 Includes: Equity curve + all performance metrics")
print(f"✅ Format: Clean, crisp, small font for easy printing/sharing")
