#!/usr/bin/env python3.11
"""
Generate Combined LONG + SHORT Production Portfolio Report
Splices both complete reports together with placeholder for data exploration section
"""

import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

print("="*80)
print("GENERATING COMBINED LONG + SHORT PRODUCTION PORTFOLIO REPORT")
print("="*80)

# Load all data for both strategies
print("\n[1/4] Loading LONG strategy data...")
long_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Trades.parquet')
long_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Long_Equity.parquet')
long_summary = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Summary.csv')
long_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Extended_Metrics.csv', index_col=0)
long_drawdowns = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Drawdowns.csv')
long_monthly = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Table.csv', index_col=0)

print("[2/4] Loading SHORT strategy data...")
short_trades = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Trades.parquet')
short_equity = pd.read_parquet('/home/ubuntu/stage4_optimization/Production_Short_Equity.parquet')
short_summary = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Summary.csv')
short_metrics = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Extended_Metrics.csv', index_col=0)
short_drawdowns = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Drawdowns.csv')
short_monthly = pd.read_csv('/home/ubuntu/stage4_optimization/Production_Short_Monthly_Table.csv', index_col=0)

print("[3/4] Building combined report structure...")

# Create PDF with LANDSCAPE orientation for comprehensive report
pdf_file = '/home/ubuntu/stage4_optimization/Production_Portfolio_COMBINED_Report.pdf'
doc = SimpleDocTemplate(pdf_file, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
story = []
styles = getSampleStyleSheet()

# Custom styles - consistent blue theme
title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1f4788'), spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold')
section_style = ParagraphStyle('SectionTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1f4788'), spaceAfter=10, spaceBefore=15, alignment=TA_CENTER, fontName='Helvetica-Bold')
heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1f4788'), spaceAfter=8, spaceBefore=12, fontName='Helvetica-Bold')
small_heading_style = ParagraphStyle('SmallHeading', parent=styles['Heading3'], fontSize=10, textColor=colors.HexColor('#1f4788'), spaceAfter=6, spaceBefore=10, fontName='Helvetica-Bold')
body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=9, alignment=TA_JUSTIFY, spaceAfter=6)

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

def create_config_table(trades_df, equity_df, summary_df, strategy_name, trade_file, equity_file):
    """Create portfolio configuration table"""
    config_data = [
        ['Parameter', 'Value'],
        ['Starting Capital', f"${summary_df['StartingCapital'].iloc[0]:,.2f}"],
        ['Max Concurrent Positions', f"{int(summary_df['MaxPositions'].iloc[0])}"],
        ['Position Sizing', f"{summary_df['PositionSizePct'].iloc[0]:.0f}% of Current Equity"],
        ['Signal Priority', 'First-Come-First-Served (ATR Tiebreaker)'],
        ['Data Period', f"{trades_df['EntryTime'].min().strftime('%Y-%m-%d')} to {trades_df['ExitTime'].max().strftime('%Y-%m-%d')}"],
        ['Total Trading Days', f"{len(equity_df['Timestamp'].dt.date.unique())}"],
        ['Trade Log File', trade_file],
        ['Equity Curve File', equity_file],
    ]
    
    table = Table(config_data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
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
    return table

def create_metrics_table(metrics_list, extended_metrics, summary_df=None):
    """Create metrics table from list of (name, key) tuples"""
    data = [['Metric', 'Value']]
    for metric_name, metric_key in metrics_list:
        if metric_key.startswith('$'):  # Special formatting
            value = metric_key
        elif metric_key in extended_metrics.index:
            value = format_metric(extended_metrics.loc[metric_key, 'Value'])
        elif summary_df is not None and metric_key in summary_df.columns:
            value = format_metric(summary_df[metric_key].iloc[0])
        else:
            value = "N/A"
        data.append([metric_name, value])
    
    table = Table(data, colWidths=[4*inch, 3*inch])
    table.setStyle(TableStyle([
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
    return table

# ============================================================================
# TITLE PAGE
# ============================================================================
story.append(Paragraph("PRODUCTION PORTFOLIO", title_style))
story.append(Paragraph("COMBINED PERFORMANCE REPORT", title_style))
story.append(Paragraph("LONG + SHORT Strategies", title_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("QGSI Trading Strategy - ATR Trailing Stop", styles['Normal']))
story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
story.append(Spacer(1, 0.3*inch))

# Table of Contents
story.append(Paragraph("Table of Contents", heading_style))
toc_data = [
    ['Section', 'Description'],
    ['Part I', 'LONG Strategy Performance Report'],
    ['Part II', 'SHORT Strategy Performance Report'],
    ['Part III', 'Comparative Data Exploration (To Be Added)'],
    ['Appendix', 'FIFO Realistic Backtesting Methodology'],
]
toc_table = Table(toc_data, colWidths=[2*inch, 7*inch])
toc_table.setStyle(TableStyle([
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
story.append(toc_table)
story.append(PageBreak())

# ============================================================================
# PART I: LONG STRATEGY
# ============================================================================
print("  → Adding LONG strategy section...")
story.append(Paragraph("PART I: LONG STRATEGY PERFORMANCE", section_style))
story.append(Paragraph("ATR Trailing Stop (Period: 30, Multiplier: 5.0, Max Bars: 20)", styles['Normal']))
story.append(Spacer(1, 0.2*inch))

# LONG Configuration
story.append(Paragraph("Portfolio Configuration", heading_style))
story.append(create_config_table(long_trades, long_equity, long_summary, "LONG", "Production_Long_Trades.parquet", "Production_Long_Equity.parquet"))
story.append(Spacer(1, 0.15*inch))

# LONG Performance Summary
story.append(Paragraph("Performance Summary", heading_style))
long_perf_metrics = [
    ('Final Equity', f"${long_summary['FinalEquity'].iloc[0]:,.2f}"),
    ('Net Profit', f"${long_summary['NetProfit'].iloc[0]:,.2f}"),
    ('Total Return', f"{long_metrics.loc['Cumulative Return', 'Value']:.2f}%"),
    ('CAGR', f"{long_metrics.loc['CAGR', 'Value']:.2f}%"),
    ('Sharpe Ratio', f"{long_metrics.loc['Sharpe', 'Value']:.4f}"),
    ('Sortino Ratio', f"{long_metrics.loc['Sortino', 'Value']:.4f}"),
    ('Calmar Ratio', f"{long_metrics.loc['Calmar', 'Value']:.2f}"),
    ('Max Drawdown', f"{long_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Volatility (ann.)', f"{long_metrics.loc['Volatility (ann.)', 'Value']:.2f}%"),
    ('Profit Factor (Daily)', f"{long_metrics.loc['Profit Factor', 'Value']:.4f}"),
]
story.append(create_metrics_table(long_perf_metrics, long_metrics, long_summary))
story.append(PageBreak())

# LONG Risk-Adjusted + Return Distribution (side by side in landscape)
story.append(Paragraph("Risk-Adjusted Performance & Return Distribution", heading_style))

# Create side-by-side tables
long_risk_metrics = [
    ('Smart Sharpe', 'Smart Sharpe'),
    ('Smart Sortino', 'Smart Sortino'),
    ('Prob. Sharpe Ratio', 'Prob. Sharpe Ratio'),
    ('Omega Ratio', 'Omega'),
    ('Recovery Factor', 'Recovery Factor'),
    ('Ulcer Index', 'Ulcer Index'),
    ('Serenity Index', 'Serenity Index'),
]

long_dist_metrics = [
    ('Expected Daily', 'Expected Daily'),
    ('Expected Monthly', 'Expected Monthly'),
    ('Best Day', 'Best Day'),
    ('Worst Day', 'Worst Day'),
    ('Best Month', 'Best Month'),
    ('Worst Month', 'Worst Month'),
    ('Skewness', 'Skew'),
    ('Kurtosis', 'Kurtosis'),
]

# Build side-by-side data
combined_data = [['Risk-Adjusted Metric', 'Value', '', 'Return Distribution', 'Value']]
for i in range(max(len(long_risk_metrics), len(long_dist_metrics))):
    row = []
    if i < len(long_risk_metrics):
        name, key = long_risk_metrics[i]
        val = long_metrics.loc[key, 'Value'] if key in long_metrics.index else "N/A"
        if key == 'Prob. Sharpe Ratio':
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    row.append('')  # Spacer column
    
    if i < len(long_dist_metrics):
        name, key = long_dist_metrics[i]
        val = long_metrics.loc[key, 'Value'] if key in long_metrics.index else "N/A"
        if 'Daily' in name or 'Monthly' in name or 'Day' in name or 'Month' in name:
            row.extend([name, f"{val:.4f}%" if abs(val) < 1 else f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    combined_data.append(row)

combined_table = Table(combined_data, colWidths=[3*inch, 1.5*inch, 0.5*inch, 3*inch, 1.5*inch])
combined_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
    ('BACKGROUND', (3, 0), (4, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
    ('TEXTCOLOR', (3, 0), (4, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
    ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (1, -1), colors.beige),
    ('BACKGROUND', (3, 1), (4, -1), colors.beige),
    ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
    ('GRID', (3, 0), (4, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(combined_table)
story.append(Spacer(1, 0.15*inch))

# LONG Drawdown Analysis
story.append(Paragraph("Drawdown Analysis", heading_style))
long_dd_metrics = [
    ('Max Drawdown', f"{long_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Avg. Drawdown', f"{long_metrics.loc['Avg. Drawdown', 'Value']:.2f}%"),
    ('Longest DD Days', f"{int(long_metrics.loc['Longest DD Days', 'Value'])}"),
    ('Avg. Drawdown Days', f"{long_metrics.loc['Avg. Drawdown Days', 'Value']:.1f}"),
]
story.append(create_metrics_table(long_dd_metrics, long_metrics))
story.append(Spacer(1, 0.1*inch))

# Top 5 Worst Drawdowns
story.append(Paragraph("Top 5 Worst Drawdowns", small_heading_style))
worst_dd_long = long_drawdowns.head(5)
dd_data = [['Rank', 'Drawdown', 'Days', 'Started', 'Recovered']]
for i, row in worst_dd_long.iterrows():
    dd_data.append([str(i+1), f"{row['Drawdown']:.2f}%", str(int(row['Days'])), row['Started'][:10], row['Recovered'][:10]])

dd_table = Table(dd_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 2*inch, 2*inch])
dd_table.setStyle(TableStyle([
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
story.append(dd_table)
story.append(PageBreak())

# LONG Win/Loss + Risk Metrics (side by side)
story.append(Paragraph("Win/Loss Statistics & Risk Metrics", heading_style))

long_winloss = [
    ('Win Days %', 'Win Days %'),
    ('Win Month %', 'Win Month %'),
    ('Win Quarter %', 'Win Quarter %'),
    ('Payoff Ratio', 'Payoff Ratio'),
    ('Gain/Pain Ratio', 'Gain/Pain Ratio'),
    ('CPC Index', 'CPC Index'),
    ('Tail Ratio', 'Tail Ratio'),
]

long_risk = [
    ('Daily VaR', 'Daily Value-at-Risk'),
    ('Expected Shortfall', 'Expected Shortfall (cVaR)'),
    ('Kelly Criterion', 'Kelly Criterion'),
    ('Outlier Win Ratio', 'Outlier Win Ratio'),
    ('Outlier Loss Ratio', 'Outlier Loss Ratio'),
]

combined_data2 = [['Win/Loss Metric', 'Value', '', 'Risk Metric', 'Value']]
for i in range(max(len(long_winloss), len(long_risk))):
    row = []
    if i < len(long_winloss):
        name, key = long_winloss[i]
        val = long_metrics.loc[key, 'Value'] if key in long_metrics.index else "N/A"
        if '%' in key:
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    row.append('')
    
    if i < len(long_risk):
        name, key = long_risk[i]
        val = long_metrics.loc[key, 'Value'] if key in long_metrics.index else "N/A"
        if 'VaR' in name or 'Shortfall' in name:
            row.extend([name, f"{val:.4f}%"])
        elif 'Kelly' in name:
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    combined_data2.append(row)

combined_table2 = Table(combined_data2, colWidths=[3*inch, 1.5*inch, 0.5*inch, 3*inch, 1.5*inch])
combined_table2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
    ('BACKGROUND', (3, 0), (4, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
    ('TEXTCOLOR', (3, 0), (4, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
    ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (1, -1), colors.beige),
    ('BACKGROUND', (3, 1), (4, -1), colors.beige),
    ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
    ('GRID', (3, 0), (4, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(combined_table2)
story.append(Spacer(1, 0.15*inch))

# LONG Trade Statistics
story.append(Paragraph("Trade Statistics", heading_style))
long_trade_metrics = [
    ('Total Trades', f"{long_summary['TotalTrades'].iloc[0]:,.0f}"),
    ('Winning Trades', f"{long_summary['WinningTrades'].iloc[0]:,.0f} ({long_summary['WinRate'].iloc[0]:.1f}%)"),
    ('Losing Trades', f"{long_summary['LosingTrades'].iloc[0]:,.0f} ({100-long_summary['WinRate'].iloc[0]:.1f}%)"),
    ('Gross Profit', f"${long_summary['GrossProfit'].iloc[0]:,.2f}"),
    ('Gross Loss', f"${long_summary['GrossLoss'].iloc[0]:,.2f}"),
    ('Average Win', f"${long_summary['AvgWin'].iloc[0]:,.2f}"),
    ('Average Loss', f"${long_summary['AvgLoss'].iloc[0]:,.2f}"),
    ('Largest Win', f"${long_summary['LargestWin'].iloc[0]:,.2f}"),
    ('Largest Loss', f"${long_summary['LargestLoss'].iloc[0]:,.2f}"),
]
story.append(create_metrics_table(long_trade_metrics, long_metrics, long_summary))
story.append(PageBreak())

# LONG Charts
story.append(Paragraph("LONG Strategy Equity Curve", heading_style))
long_equity_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Equity_Curve.png', width=9*inch, height=5*inch)
story.append(long_equity_img)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("LONG Strategy Monthly Returns", heading_style))
long_monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Long_Monthly_Returns.png', width=9*inch, height=3.5*inch)
story.append(long_monthly_img)
story.append(PageBreak())

# ============================================================================
# PART II: SHORT STRATEGY
# ============================================================================
print("  → Adding SHORT strategy section...")
story.append(Paragraph("PART II: SHORT STRATEGY PERFORMANCE", section_style))
story.append(Paragraph("ATR Trailing Stop (Period: 30, Multiplier: 1.5, Max Bars: 20)", styles['Normal']))
story.append(Spacer(1, 0.2*inch))

# SHORT Configuration
story.append(Paragraph("Portfolio Configuration", heading_style))
story.append(create_config_table(short_trades, short_equity, short_summary, "SHORT", "Production_Short_Trades.parquet", "Production_Short_Equity.parquet"))
story.append(Spacer(1, 0.15*inch))

# SHORT Performance Summary
story.append(Paragraph("Performance Summary", heading_style))
short_perf_metrics = [
    ('Final Equity', f"${short_summary['FinalEquity'].iloc[0]:,.2f}"),
    ('Net Profit', f"${short_summary['NetProfit'].iloc[0]:,.2f}"),
    ('Total Return', f"{short_metrics.loc['Cumulative Return', 'Value']:.2f}%"),
    ('CAGR', f"{short_metrics.loc['CAGR', 'Value']:.2f}%"),
    ('Sharpe Ratio', f"{short_metrics.loc['Sharpe', 'Value']:.4f}"),
    ('Sortino Ratio', f"{short_metrics.loc['Sortino', 'Value']:.4f}"),
    ('Calmar Ratio', f"{short_metrics.loc['Calmar', 'Value']:.2f}"),
    ('Max Drawdown', f"{short_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Volatility (ann.)', f"{short_metrics.loc['Volatility (ann.)', 'Value']:.2f}%"),
    ('Profit Factor (Daily)', f"{short_metrics.loc['Profit Factor', 'Value']:.4f}"),
]
story.append(create_metrics_table(short_perf_metrics, short_metrics, short_summary))
story.append(PageBreak())

# SHORT Risk-Adjusted + Return Distribution
story.append(Paragraph("Risk-Adjusted Performance & Return Distribution", heading_style))

short_risk_metrics = [
    ('Smart Sharpe', 'Smart Sharpe'),
    ('Smart Sortino', 'Smart Sortino'),
    ('Prob. Sharpe Ratio', 'Prob. Sharpe Ratio'),
    ('Omega Ratio', 'Omega'),
    ('Recovery Factor', 'Recovery Factor'),
    ('Ulcer Index', 'Ulcer Index'),
    ('Serenity Index', 'Serenity Index'),
]

short_dist_metrics = [
    ('Expected Daily', 'Expected Daily'),
    ('Expected Monthly', 'Expected Monthly'),
    ('Best Day', 'Best Day'),
    ('Worst Day', 'Worst Day'),
    ('Best Month', 'Best Month'),
    ('Worst Month', 'Worst Month'),
    ('Skewness', 'Skew'),
    ('Kurtosis', 'Kurtosis'),
]

combined_data3 = [['Risk-Adjusted Metric', 'Value', '', 'Return Distribution', 'Value']]
for i in range(max(len(short_risk_metrics), len(short_dist_metrics))):
    row = []
    if i < len(short_risk_metrics):
        name, key = short_risk_metrics[i]
        val = short_metrics.loc[key, 'Value'] if key in short_metrics.index else "N/A"
        if key == 'Prob. Sharpe Ratio':
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    row.append('')
    
    if i < len(short_dist_metrics):
        name, key = short_dist_metrics[i]
        val = short_metrics.loc[key, 'Value'] if key in short_metrics.index else "N/A"
        if 'Daily' in name or 'Monthly' in name or 'Day' in name or 'Month' in name:
            row.extend([name, f"{val:.4f}%" if abs(val) < 1 else f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    combined_data3.append(row)

combined_table3 = Table(combined_data3, colWidths=[3*inch, 1.5*inch, 0.5*inch, 3*inch, 1.5*inch])
combined_table3.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
    ('BACKGROUND', (3, 0), (4, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
    ('TEXTCOLOR', (3, 0), (4, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
    ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (1, -1), colors.beige),
    ('BACKGROUND', (3, 1), (4, -1), colors.beige),
    ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
    ('GRID', (3, 0), (4, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(combined_table3)
story.append(Spacer(1, 0.15*inch))

# SHORT Drawdown Analysis
story.append(Paragraph("Drawdown Analysis", heading_style))
short_dd_metrics = [
    ('Max Drawdown', f"{short_metrics.loc['Max Drawdown', 'Value']:.2f}%"),
    ('Avg. Drawdown', f"{short_metrics.loc['Avg. Drawdown', 'Value']:.2f}%"),
    ('Longest DD Days', f"{int(short_metrics.loc['Longest DD Days', 'Value'])}"),
    ('Avg. Drawdown Days', f"{short_metrics.loc['Avg. Drawdown Days', 'Value']:.1f}"),
]
story.append(create_metrics_table(short_dd_metrics, short_metrics))
story.append(Spacer(1, 0.1*inch))

# Top 5 Worst Drawdowns
story.append(Paragraph("Top 5 Worst Drawdowns", small_heading_style))
worst_dd_short = short_drawdowns.head(5)
dd_data2 = [['Rank', 'Drawdown', 'Days', 'Started', 'Recovered']]
for i, row in worst_dd_short.iterrows():
    dd_data2.append([str(i+1), f"{row['Drawdown']:.2f}%", str(int(row['Days'])), row['Started'][:10], row['Recovered'][:10]])

dd_table2 = Table(dd_data2, colWidths=[0.8*inch, 1.5*inch, 1*inch, 2*inch, 2*inch])
dd_table2.setStyle(TableStyle([
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
story.append(dd_table2)
story.append(PageBreak())

# SHORT Win/Loss + Risk Metrics
story.append(Paragraph("Win/Loss Statistics & Risk Metrics", heading_style))

short_winloss = [
    ('Win Days %', 'Win Days %'),
    ('Win Month %', 'Win Month %'),
    ('Win Quarter %', 'Win Quarter %'),
    ('Payoff Ratio', 'Payoff Ratio'),
    ('Gain/Pain Ratio', 'Gain/Pain Ratio'),
    ('CPC Index', 'CPC Index'),
    ('Tail Ratio', 'Tail Ratio'),
]

short_risk = [
    ('Daily VaR', 'Daily Value-at-Risk'),
    ('Expected Shortfall', 'Expected Shortfall (cVaR)'),
    ('Kelly Criterion', 'Kelly Criterion'),
    ('Outlier Win Ratio', 'Outlier Win Ratio'),
    ('Outlier Loss Ratio', 'Outlier Loss Ratio'),
]

combined_data4 = [['Win/Loss Metric', 'Value', '', 'Risk Metric', 'Value']]
for i in range(max(len(short_winloss), len(short_risk))):
    row = []
    if i < len(short_winloss):
        name, key = short_winloss[i]
        val = short_metrics.loc[key, 'Value'] if key in short_metrics.index else "N/A"
        if '%' in key:
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    row.append('')
    
    if i < len(short_risk):
        name, key = short_risk[i]
        val = short_metrics.loc[key, 'Value'] if key in short_metrics.index else "N/A"
        if 'VaR' in name or 'Shortfall' in name:
            row.extend([name, f"{val:.4f}%"])
        elif 'Kelly' in name:
            row.extend([name, f"{val:.2f}%"])
        else:
            row.extend([name, format_metric(val)])
    else:
        row.extend(['', ''])
    
    combined_data4.append(row)

combined_table4 = Table(combined_data4, colWidths=[3*inch, 1.5*inch, 0.5*inch, 3*inch, 1.5*inch])
combined_table4.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
    ('BACKGROUND', (3, 0), (4, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
    ('TEXTCOLOR', (3, 0), (4, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (3, 0), (3, -1), 'LEFT'),
    ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (1, -1), colors.beige),
    ('BACKGROUND', (3, 1), (4, -1), colors.beige),
    ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
    ('GRID', (3, 0), (4, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
story.append(combined_table4)
story.append(Spacer(1, 0.15*inch))

# SHORT Trade Statistics
story.append(Paragraph("Trade Statistics", heading_style))
short_trade_metrics = [
    ('Total Trades', f"{short_summary['TotalTrades'].iloc[0]:,.0f}"),
    ('Winning Trades', f"{short_summary['WinningTrades'].iloc[0]:,.0f} ({short_summary['WinRate'].iloc[0]:.1f}%)"),
    ('Losing Trades', f"{short_summary['LosingTrades'].iloc[0]:,.0f} ({100-short_summary['WinRate'].iloc[0]:.1f}%)"),
    ('Gross Profit', f"${short_summary['GrossProfit'].iloc[0]:,.2f}"),
    ('Gross Loss', f"${short_summary['GrossLoss'].iloc[0]:,.2f}"),
    ('Average Win', f"${short_summary['AvgWin'].iloc[0]:,.2f}"),
    ('Average Loss', f"${short_summary['AvgLoss'].iloc[0]:,.2f}"),
    ('Largest Win', f"${short_summary['LargestWin'].iloc[0]:,.2f}"),
    ('Largest Loss', f"${short_summary['LargestLoss'].iloc[0]:,.2f}"),
]
story.append(create_metrics_table(short_trade_metrics, short_metrics, short_summary))
story.append(PageBreak())

# SHORT Charts
story.append(Paragraph("SHORT Strategy Equity Curve", heading_style))
short_equity_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Equity_Curve.png', width=9*inch, height=5*inch)
story.append(short_equity_img)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("SHORT Strategy Monthly Returns", heading_style))
short_monthly_img = Image('/home/ubuntu/stage4_optimization/Production_Short_Monthly_Returns.png', width=9*inch, height=3.5*inch)
story.append(short_monthly_img)
story.append(PageBreak())

# ============================================================================
# PART III: PLACEHOLDER FOR DATA EXPLORATION
# ============================================================================
print("  → Adding placeholder for data exploration section...")
story.append(Paragraph("PART III: COMPARATIVE DATA EXPLORATION", section_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("This section will contain comparative analysis of LONG and SHORT strategies, including:", body_style))
story.append(Spacer(1, 0.1*inch))

placeholder_items = [
    "• Side-by-side performance comparison",
    "• Correlation analysis between strategies",
    "• Combined portfolio simulation (LONG + SHORT)",
    "• Trade distribution analysis",
    "• Symbol overlap and timing analysis",
    "• Risk-adjusted return comparison",
    "• Drawdown period correlation",
    "• Monthly performance comparison",
]

for item in placeholder_items:
    story.append(Paragraph(item, body_style))

story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("[TO BE ADDED BY USER]", ParagraphStyle('Placeholder', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, fontName='Helvetica-Bold')))
story.append(PageBreak())

# ============================================================================
# APPENDIX
# ============================================================================
print("  → Adding appendix...")
story.append(Paragraph("APPENDIX: FIFO Realistic Backtesting Methodology", section_style))
story.append(Spacer(1, 0.2*inch))

appendix_sections = [
    ("Overview", "This appendix documents the First-In-First-Out (FIFO) realistic backtesting process implemented to ensure the production portfolio simulator accurately replicates real-world fund performance. The methodology addresses critical challenges in portfolio-level backtesting that are often overlooked in traditional signal-level analysis."),
    ("The Challenge", "Traditional backtesting systems evaluate trading signals in isolation, assuming unlimited capital, no position limits, perfect execution, and instantaneous position entry. This creates a significant gap between theoretical signal performance and actual fund performance. A production trading fund faces concrete limitations: fixed capital ($1M), position limits (max 10 concurrent), position sizing (10% of equity), signal competition, and execution sequencing."),
    ("FIFO Methodology", "The FIFO methodology ensures that trade sequencing, position management, and capital allocation exactly mirror how a live fund would operate. All entry and exit signals are processed in strict chronological order based on timestamp, ensuring earlier signals are evaluated first with no future information influencing past decisions. The simulator maintains real-time portfolio state tracking current open positions, available capital, position count, and equity curve at every timestamp."),
    ("Key Constraints", "When a new signal arrives, the simulator enforces: (1) Position limit check - if 10 positions are open, skip the signal; (2) Capital allocation - position size calculated dynamically as 10% of current equity, not starting capital; (3) Signal priority - when multiple signals occur simultaneously, priority determined by timestamp first, then ATR value (higher ATR = higher priority); (4) Exit processing - stops triggered immediately when price hits stop loss or maximum bars reached."),
    ("Baseline vs Production - LONG", f"Baseline (theoretical) assumed every signal is taken with unlimited capital, resulting in 31,823 trades for LONG strategy. Production (realistic) applies real fund constraints with 10-position limit and 10% sizing, resulting in 16,754 trades (52.6% of signals). The remaining 15,069 signals (47.4%) were skipped due to max positions reached."),
    ("Baseline vs Production - SHORT", f"Baseline (theoretical) assumed every signal is taken with unlimited capital, resulting in 60,111 trades for SHORT strategy. Production (realistic) applies real fund constraints with 10-position limit and 10% sizing, resulting in only 1,424 trades (2.4% of signals). The remaining 58,687 signals (97.6%) were skipped due to max positions reached. This demonstrates that SHORT signals are highly concentrated in time."),
    ("Key Functions", "process_baseline_to_production() - Main orchestrator converting baseline trades to production trades. check_position_availability() - Determines if new position can be opened. calculate_position_size() - Computes shares based on current equity. update_equity_curve() - Records equity at each timestamp. process_exits() - Checks all open positions for exit conditions. calculate_performance_metrics() - Computes comprehensive performance statistics including Sharpe, Sortino, drawdown, win rate, and profit factor."),
    ("Validation", "The system ensures: (1) No look-ahead bias - all decisions use only information available at the time; (2) Capital conservation - total deployed capital never exceeds available equity; (3) Position integrity - no duplicate symbols, all exits matched to entries, PnL verified; (4) Equity curve continuity - continuous with no gaps, every trade impact recorded, drawdowns measured from running peak."),
    ("Conclusion", "The FIFO realistic backtesting methodology transforms theoretical signal performance into achievable fund performance by enforcing real-world constraints, respecting temporal sequencing, simulating actual portfolio management, and eliminating look-ahead bias. This approach provides institutional-grade backtesting that accurately represents what a live trading fund would experience.")
]

for section_title, section_text in appendix_sections:
    story.append(Paragraph(section_title, small_heading_style))
    story.append(Paragraph(section_text, body_style))
    story.append(Spacer(1, 0.1*inch))

# Build PDF
print("\n[4/4] Building PDF...")
doc.build(story)

print("\n" + "="*80)
print(f"✓ Combined report generated: {pdf_file}")
print(f"  - Part I: LONG Strategy (complete)")
print(f"  - Part II: SHORT Strategy (complete)")
print(f"  - Part III: Data Exploration (placeholder)")
print(f"  - Appendix: FIFO Methodology")
print(f"  - Format: Landscape orientation")
print(f"  - All content from both reports included")
print("="*80)
