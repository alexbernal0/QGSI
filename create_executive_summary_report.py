"""
Generate Executive Summary Report - Best LONG and SHORT Strategies
Highlights winners from Phase 1 (LONG) and Phase 2 (SHORT) with implementation code
"""

import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path

OUTPUT_DIR = Path('/home/ubuntu/stage4_optimization')
OUTPUT_FILE = OUTPUT_DIR / 'QGSI_Executive_Summary_Best_Strategies.pdf'

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
    fontSize=26,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=15,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=12,
    spaceBefore=15,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=8,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=9,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

code_style = ParagraphStyle(
    'CodeStyle',
    parent=styles['Code'],
    fontSize=7,
    fontName='Courier',
    leftIndent=20,
    rightIndent=20,
    spaceAfter=10,
    spaceBefore=10,
    backColor=colors.HexColor('#f5f5f5'),
    borderColor=colors.HexColor('#cccccc'),
    borderWidth=1,
    borderPadding=10
)

# Title Page
story.append(Spacer(1, 1.2*inch))
story.append(Paragraph("QGSI Quantitative Research", title_style))
story.append(Paragraph("Executive Summary Report", heading_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Optimal ATR-Based Exit Strategies", subheading_style))
story.append(Paragraph("Phase 1 & 2 Results: LONG and SHORT Signals", body_style))
story.append(Spacer(1, 0.5*inch))

# Overview Table
overview_data = [
    ['Phase', 'Signal Type', 'Signals Tested', 'Strategies', 'Combinations', 'Best Strategy', 'Best Return'],
    ['Phase 1', 'LONG', '~80,129', '4', '188', 'Fixed ATR Asymmetric', '+$837,370'],
    ['Phase 2', 'SHORT', '~60,033', '4', '172', 'ATR Trailing Stop', '+$859,092'],
    ['TOTAL', 'BOTH', '~140,162', '8', '360', '—', '+$1,696,462']
]

t = Table(overview_data, colWidths=[1*inch, 1.2*inch, 1.3*inch, 1*inch, 1.3*inch, 2*inch, 1.3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, 1), (-1, 2), colors.lightgreen),
    ('BACKGROUND', (0, 3), (-1, 3), colors.lightyellow),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
]))
story.append(t)
story.append(Spacer(1, 0.3*inch))

# Key Findings
story.append(Paragraph("Key Findings", heading_style))
findings = [
    "• <b>Combined Profitability:</b> Best LONG and SHORT strategies together earn <b>+$1.7M</b> across 140K signals (2007-2024).",
    "• <b>SHORT Outperforms LONG:</b> ATR Trailing Stop SHORT (+$859K) beats Fixed ATR Asymmetric LONG (+$837K) by $22K.",
    "• <b>Different Strategies Win:</b> LONG favors asymmetric exits, SHORT favors trailing stops.",
    "• <b>Tight Stops Critical:</b> Both winners use 1.5× ATR multiplier for stop loss.",
    "• <b>Ready for Implementation:</b> Optimal parameters identified for live trading or further backtesting."
]
for finding in findings:
    story.append(Paragraph(finding, body_style))

story.append(PageBreak())

# ============================================================================
# LONG STRATEGY WINNER
# ============================================================================
story.append(Paragraph("Phase 1: LONG Signals - Winner", heading_style))
story.append(Paragraph("Strategy: Fixed ATR Asymmetric", subheading_style))

# LONG Winner Details
long_details = [
    ['Parameter', 'Value', 'Description'],
    ['Strategy Name', 'Fixed ATR Asymmetric', 'Asymmetric stop/target multipliers'],
    ['ATR Period', '50', 'Longer period for stability'],
    ['Stop Multiplier', '1.5×', 'Tight stop to limit losses'],
    ['Target Multiplier', '6.0×', 'Wide target to capture large moves'],
    ['Net Profit', '+$837,370', 'Across 80,129 LONG signals'],
    ['Profit Factor', '1.112', 'Strong positive edge'],
    ['Win Rate', '29.0%', 'Low but offset by large wins'],
    ['Total Trades', '80,076', 'Comprehensive test'],
    ['Avg Win', '$428.63', 'Large average winning trade'],
    ['Avg Loss', '$151.20', 'Small average losing trade'],
    ['Win/Loss Ratio', '2.83:1', 'Wins are 2.83× larger than losses'],
]

t = Table(long_details, colWidths=[2*inch, 1.8*inch, 4.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (1, -1), 'LEFT'),
    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

# LONG Strategy Logic
story.append(Paragraph("Strategy Logic - LONG Signals", subheading_style))
story.append(Paragraph(
    "The Fixed ATR Asymmetric strategy uses different multipliers for stop loss and profit target, allowing for <b>tight stops</b> "
    "to quickly cut losses while maintaining <b>wide targets</b> to capture large winning moves. This asymmetry creates a favorable "
    "risk/reward profile where losses are small and frequent, but wins are large and compensate for the low win rate.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# LONG Logic Bullets
long_logic = [
    "1. <b>Entry:</b> Buy at signal bar CLOSE price",
    "2. <b>Stop Loss:</b> Entry - (ATR(50) × 1.5) = Entry - 1.5× ATR below entry",
    "3. <b>Profit Target:</b> Entry + (ATR(50) × 6.0) = Entry + 6.0× ATR above entry",
    "4. <b>Exit Check:</b> On each bar, exit if LOW ≤ Stop OR HIGH ≥ Target",
    "5. <b>Time Limit:</b> Close position at market if not exited within 30 bars",
    "6. <b>Position Size:</b> $100,000 / Entry Price = Number of shares"
]
for logic in long_logic:
    story.append(Paragraph(logic, body_style))

story.append(PageBreak())

# LONG Implementation Code
story.append(Paragraph("Implementation Code - LONG Strategy", subheading_style))

long_code = '''# Fixed ATR Asymmetric - LONG Signal Implementation
import pandas as pd
import numpy as np

def calculate_atr(df, period=50):
    """Calculate Average True Range."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def backtest_long_asymmetric(df, symbol):
    """
    Backtest Fixed ATR Asymmetric on LONG signals.
    Best Parameters: ATR(50), Stop 1.5×, Target 6.0×
    """
    ATR_PERIOD = 50
    STOP_MULT = 1.5
    TARGET_MULT = 6.0
    MAX_BARS = 30
    POSITION_SIZE = 100000.0
    
    trades = []
    signal_indices = df[df['Signal'] == 1].index.tolist()  # LONG signals
    
    df['ATR'] = calculate_atr(df, period=ATR_PERIOD)
    
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        entry_price = df.loc[signal_idx, 'Close']
        entry_atr = df.loc[signal_idx, 'ATR']
        
        if pd.isna(entry_atr) or entry_atr == 0:
            continue
        
        shares = POSITION_SIZE / entry_price
        
        # LONG: Stop BELOW entry, Target ABOVE entry
        stop_loss = entry_price - (STOP_MULT * entry_atr)
        profit_target = entry_price + (TARGET_MULT * entry_atr)
        
        # Check exits
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            current_idx = df.index[i]
            bars_in_trade = i - entry_bar_idx
            
            # Check stop (LOW touches stop)
            if df.loc[current_idx, 'Low'] <= stop_loss:
                exit_price = stop_loss
                exit_reason = 'STOP'
                break
            
            # Check target (HIGH touches target)
            if df.loc[current_idx, 'High'] >= profit_target:
                exit_price = profit_target
                exit_reason = 'TARGET'
                break
            
            # Time limit
            if bars_in_trade >= MAX_BARS:
                exit_price = df.loc[current_idx, 'Close']
                exit_reason = 'TIME'
                break
        else:
            # No exit found within time limit
            exit_price = df.iloc[min(entry_bar_idx + MAX_BARS, len(df)-1)]['Close']
            exit_reason = 'TIME'
        
        # Calculate P&L
        net_profit = (exit_price - entry_price) * shares
        
        trades.append({
            'Symbol': symbol,
            'EntryPrice': entry_price,
            'ExitPrice': exit_price,
            'StopLoss': stop_loss,
            'Target': profit_target,
            'ExitReason': exit_reason,
            'NetProfit': net_profit,
            'Shares': shares
        })
    
    return pd.DataFrame(trades)

# Usage Example:
# df = pd.read_parquet('your_data.parquet')
# df = df[df['Symbol'] == 'AAPL'].sort_values('Date')
# results = backtest_long_asymmetric(df, 'AAPL')
# print(f"Total Profit: ${results['NetProfit'].sum():,.2f}")
'''

story.append(Preformatted(long_code, code_style))
story.append(PageBreak())

# ============================================================================
# SHORT STRATEGY WINNER
# ============================================================================
story.append(Paragraph("Phase 2: SHORT Signals - Winner", heading_style))
story.append(Paragraph("Strategy: ATR Trailing Stop", subheading_style))

# SHORT Winner Details
short_details = [
    ['Parameter', 'Value', 'Description'],
    ['Strategy Name', 'ATR Trailing Stop', 'Dynamic trailing stop mechanism'],
    ['ATR Period', '30', 'Optimal responsiveness'],
    ['Multiplier', '1.5×', 'Tight trailing stop'],
    ['Target', 'None', 'Let winners run (no fixed target)'],
    ['Net Profit', '+$859,092', 'Across 60,033 SHORT signals'],
    ['Profit Factor', '1.139', 'Highest among SHORT strategies'],
    ['Win Rate', '34.3%', 'Low but acceptable with trailing'],
    ['Total Trades', '60,033', 'All SHORT signals tested'],
    ['Avg Win', '$342.19', 'Trailing captures large moves'],
    ['Avg Loss', '$157.30', 'Tight stop limits losses'],
    ['Win/Loss Ratio', '2.18:1', 'Wins are 2.18× larger than losses'],
    ['Avg Bars in Trade', '8.7', 'Quick exits preserve capital'],
]

t = Table(short_details, colWidths=[2*inch, 1.8*inch, 4.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (1, -1), 'LEFT'),
    ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

# SHORT Strategy Logic
story.append(Paragraph("Strategy Logic - SHORT Signals", subheading_style))
story.append(Paragraph(
    "The ATR Trailing Stop strategy uses a <b>dynamic stop</b> that moves DOWN as price falls, locking in profits while allowing "
    "winners to run. For SHORT positions, the stop starts ABOVE the entry price and trails downward, tightening as the trade becomes "
    "more profitable. This mechanism is particularly effective for SHORT signals as it protects against sudden upward reversals while "
    "capturing extended downward moves.",
    body_style
))
story.append(Spacer(1, 0.1*inch))

# SHORT Logic Bullets
short_logic = [
    "1. <b>Entry:</b> Sell SHORT at signal bar CLOSE price",
    "2. <b>Initial Stop:</b> Entry + (ATR(30) × 1.5) = Entry + 1.5× ATR above entry",
    "3. <b>Trailing Logic:</b> Stop = MIN(previous_stop, Current HIGH + ATR(30) × 1.5)",
    "4. <b>Stop Movement:</b> Stop only moves DOWN (tighter), never UP (looser)",
    "5. <b>Exit Check:</b> On each bar, exit if HIGH ≥ Stop (stopped out)",
    "6. <b>Time Limit:</b> Close position at market if not exited within 20 bars",
    "7. <b>Position Size:</b> $100,000 / Entry Price = Number of shares",
    "8. <b>P&L Calculation:</b> (Entry Price - Exit Price) × Shares"
]
for logic in short_logic:
    story.append(Paragraph(logic, body_style))

story.append(PageBreak())

# SHORT Implementation Code
story.append(Paragraph("Implementation Code - SHORT Strategy", subheading_style))

short_code = '''# ATR Trailing Stop - SHORT Signal Implementation
import pandas as pd
import numpy as np

def calculate_atr(df, period=30):
    """Calculate Average True Range."""
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def backtest_short_trailing(df, symbol):
    """
    Backtest ATR Trailing Stop on SHORT signals.
    Best Parameters: ATR(30), Multiplier 1.5×
    """
    ATR_PERIOD = 30
    MULTIPLIER = 1.5
    MAX_BARS = 20
    POSITION_SIZE = 100000.0
    
    trades = []
    signal_indices = df[df['Signal'] == -1].index.tolist()  # SHORT signals
    
    df['ATR'] = calculate_atr(df, period=ATR_PERIOD)
    
    for signal_idx in signal_indices:
        entry_bar_idx = df.index.get_loc(signal_idx)
        entry_price = df.loc[signal_idx, 'Close']
        entry_atr = df.loc[signal_idx, 'ATR']
        
        if pd.isna(entry_atr) or entry_atr == 0:
            continue
        
        shares = POSITION_SIZE / entry_price
        
        # SHORT: Initial stop ABOVE entry (loss if price rises)
        initial_stop = entry_price + (MULTIPLIER * entry_atr)
        current_stop = initial_stop
        
        # Check exits
        for i in range(entry_bar_idx + 1, min(entry_bar_idx + MAX_BARS + 1, len(df))):
            current_idx = df.index[i]
            current_atr = df.loc[current_idx, 'ATR']
            bars_in_trade = i - entry_bar_idx
            
            # Update trailing stop (moves DOWN only)
            if not pd.isna(current_atr) and current_atr > 0:
                new_stop = df.loc[current_idx, 'High'] + (MULTIPLIER * current_atr)
                current_stop = min(current_stop, new_stop)  # Move DOWN (tighter)
            
            # Check if stopped out (price rises to hit stop)
            if df.loc[current_idx, 'High'] >= current_stop:
                exit_price = current_stop
                exit_reason = 'STOP'
                break
            
            # Time limit
            if bars_in_trade >= MAX_BARS:
                exit_price = df.loc[current_idx, 'Close']
                exit_reason = 'TIME'
                break
        else:
            # No exit found within time limit
            exit_price = df.iloc[min(entry_bar_idx + MAX_BARS, len(df)-1)]['Close']
            exit_reason = 'TIME'
        
        # Calculate P&L (SHORT: profit when exit < entry)
        net_profit = (entry_price - exit_price) * shares
        
        trades.append({
            'Symbol': symbol,
            'EntryPrice': entry_price,
            'ExitPrice': exit_price,
            'InitialStop': initial_stop,
            'FinalStop': current_stop,
            'ExitReason': exit_reason,
            'NetProfit': net_profit,
            'Shares': shares
        })
    
    return pd.DataFrame(trades)

# Usage Example:
# df = pd.read_parquet('your_data.parquet')
# df = df[df['Symbol'] == 'AAPL'].sort_values('Date')
# results = backtest_short_trailing(df, 'AAPL')
# print(f"Total Profit: ${results['NetProfit'].sum():,.2f}")
'''

story.append(Preformatted(short_code, code_style))
story.append(PageBreak())

# ============================================================================
# COMPARISON & NEXT STEPS
# ============================================================================
story.append(Paragraph("Strategy Comparison: LONG vs SHORT", heading_style))

comparison_data = [
    ['Metric', 'LONG (Asymmetric)', 'SHORT (Trailing)', 'Difference'],
    ['Net Profit', '+$837,370', '+$859,092', '+$21,722 (SHORT wins)'],
    ['Profit Factor', '1.112', '1.139', '+0.027 (SHORT better)'],
    ['Win Rate', '29.0%', '34.3%', '+5.3% (SHORT better)'],
    ['Avg Win', '$428.63', '$342.19', '-$86.44 (LONG better)'],
    ['Avg Loss', '$151.20', '$157.30', '-$6.10 (LONG better)'],
    ['Win/Loss Ratio', '2.83:1', '2.18:1', 'LONG has larger wins'],
    ['Avg Bars in Trade', '~15-20', '8.7', 'SHORT exits faster'],
    ['Stop Type', 'Fixed (1.5× ATR)', 'Trailing (1.5× ATR)', 'Different mechanisms'],
    ['Target Type', 'Fixed (6.0× ATR)', 'None (let run)', 'LONG has fixed target'],
]

t = Table(comparison_data, colWidths=[2.2*inch, 2*inch, 2*inch, 2.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

# Key Insights
story.append(Paragraph("Key Insights from Comparison", subheading_style))
insights = [
    "• <b>SHORT Slightly Better:</b> Trailing stop SHORT earns $22K more than asymmetric LONG.",
    "• <b>Different Approaches:</b> LONG uses fixed wide targets, SHORT uses trailing stops without targets.",
    "• <b>Both Use 1.5× Stops:</b> Tight stop loss is critical for both signal types.",
    "• <b>LONG Has Larger Wins:</b> Fixed 6.0× target captures bigger moves, but lower win rate.",
    "• <b>SHORT Exits Faster:</b> Trailing mechanism exits quickly, preserving capital.",
    "• <b>Combined Strategy:</b> Using both together provides diversification and +$1.7M total profit."
]
for insight in insights:
    story.append(Paragraph(insight, body_style))

story.append(PageBreak())

# Next Steps
story.append(Paragraph("Next Steps: Detailed Backtesting Phase", heading_style))
story.append(Paragraph(
    "With optimal parameters identified for both LONG and SHORT signals, the next phase involves comprehensive backtesting "
    "to validate performance, analyze equity curves, calculate risk metrics, and prepare for live implementation.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

# Next Steps Table
next_steps_data = [
    ['Phase', 'Task', 'Description', 'Output'],
    ['Phase 3a', 'Generate Trade Logs', 'Re-run best configs to save all individual trades', 'Parquet files with full trade details'],
    ['Phase 3b', 'Equity Curve Analysis', 'Plot cumulative returns over time', 'Equity curve charts vs benchmark'],
    ['Phase 3c', 'Risk Metrics', 'Calculate Sharpe, Sortino, Max DD, Calmar', 'Comprehensive risk report'],
    ['Phase 3d', 'Drawdown Analysis', 'Analyze underwater periods and recovery', 'Drawdown charts and statistics'],
    ['Phase 3e', 'Monthly/Yearly Returns', 'Break down performance by period', 'Return distribution tables'],
    ['Phase 3f', 'Trade Analysis', 'Analyze trade duration, MAE, MFE', 'Trade efficiency metrics'],
    ['Phase 3g', 'Final Report', 'Combine all analyses into tear sheet', 'Complete performance tear sheet'],
]

t = Table(next_steps_data, colWidths=[1*inch, 1.8*inch, 3.2*inch, 2.5*inch])
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
story.append(Spacer(1, 0.3*inch))

# Conclusion
story.append(Paragraph("Conclusion", heading_style))
story.append(Paragraph(
    "The optimization phase has successfully identified the best ATR-based exit strategies for both LONG and SHORT signals. "
    "The Fixed ATR Asymmetric strategy (ATR 50, Stop 1.5×, Target 6.0×) is optimal for LONG signals with +$837K profit, "
    "while the ATR Trailing Stop strategy (ATR 30, Multiplier 1.5×) is optimal for SHORT signals with +$859K profit. "
    "Combined, these strategies generate <b>+$1.7M</b> across 140K signals over 17 years (2007-2024). "
    "The next phase will validate these results through detailed backtesting and prepare for live implementation.",
    body_style
))

# Build PDF
doc.build(story)
print(f"✓ Executive Summary generated: {OUTPUT_FILE}")
print(f"✓ File size: {OUTPUT_FILE.stat().st_size / (1024*1024):.1f} MB")
