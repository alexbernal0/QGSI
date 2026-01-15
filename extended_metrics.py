#!/usr/bin/env python3.11
"""
Extended Performance Metrics Module
Comprehensive quantitative metrics for portfolio analysis
"""

import pandas as pd
import numpy as np

def cum_returns(ret):
    """Calculate cumulative returns"""
    return (1 + ret).cumprod() - 1

def cagr(ret, periods_per_year=252):
    """Compound Annual Growth Rate"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret).iloc[-1]
    years = len(ret) / periods_per_year
    return (1 + cum) ** (1 / years) - 1 if years > 0 else 0

def max_drawdown(ret):
    """Maximum drawdown"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret) + 1
    dd = cum / cum.cummax() - 1
    return dd.min()

def drawdown_duration(ret):
    """Longest drawdown duration in days"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret) + 1
    peak = cum.cummax()
    dd = cum / peak - 1
    in_dd = dd < 0
    dd_groups = (in_dd != in_dd.shift()).cumsum()
    dd_durations = in_dd.groupby(dd_groups).cumcount() + 1
    return dd_durations.max() if in_dd.any() else 0

def volatility(ret, periods_per_year=252):
    """Annualized volatility"""
    return ret.std() * np.sqrt(periods_per_year) if len(ret) > 0 else 0

def downside_dev(ret, rf=0):
    """Downside deviation (annualized)"""
    if len(ret) == 0:
        return 0
    downside = ret[ret < rf]
    return np.sqrt((downside - rf).pow(2).mean()) * np.sqrt(252) if not downside.empty else 0

def sharpe(ret, rf=0, periods_per_year=252):
    """Sharpe ratio"""
    if len(ret) == 0:
        return 0
    excess = ret - rf / periods_per_year
    return excess.mean() / excess.std() * np.sqrt(periods_per_year) if excess.std() != 0 else 0

def sortino(ret, rf=0, periods_per_year=252):
    """Sortino ratio"""
    if len(ret) == 0:
        return 0
    excess = ret - rf / periods_per_year
    down_std = np.sqrt((excess[excess < 0] ** 2).mean()) * np.sqrt(periods_per_year) if len(excess[excess < 0]) > 0 else 0
    return excess.mean() * periods_per_year / down_std if down_std != 0 else 0

def calmar(ret):
    """Calmar ratio"""
    if len(ret) == 0:
        return 0
    md = abs(max_drawdown(ret))
    return cagr(ret) / md if md != 0 else np.inf

def omega(ret, rf=0):
    """Omega ratio"""
    if len(ret) == 0:
        return np.inf
    threshold = rf / 252
    pos = (ret[ret > threshold] - threshold).sum()
    neg = abs((ret[ret < threshold] - threshold).sum())
    return pos / neg if neg != 0 else np.inf

def recovery_factor(ret):
    """Recovery factor"""
    if len(ret) == 0:
        return np.inf
    cum_ret = cum_returns(ret).iloc[-1]
    md = abs(max_drawdown(ret))
    return cum_ret / md if md != 0 else np.inf

def ulcer_index(ret):
    """Ulcer index"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret) + 1
    dd = (cum - cum.cummax()) / cum.cummax()
    return np.sqrt((dd ** 2).mean())

def serenity_index(ret, rf=0):
    """Serenity index"""
    if len(ret) == 0:
        return np.inf
    excess_ret = cagr(ret) - rf
    ui = ulcer_index(ret)
    return excess_ret / (ui ** 2) if ui != 0 else np.inf

def value_at_risk(ret, level=0.05):
    """Value at Risk"""
    if len(ret) == 0:
        return 0
    return ret.quantile(level) if len(ret) > 1 else 0

def conditional_var(ret, level=0.05):
    """Conditional VaR (Expected Shortfall)"""
    if len(ret) == 0:
        return 0
    var = value_at_risk(ret, level)
    tail = ret[ret <= var]
    return tail.mean() if not tail.empty else 0

def kelly_criterion(ret):
    """Kelly Criterion"""
    if len(ret) == 0:
        return 0
    win_prob = (ret > 0).mean()
    win_loss_ratio = ret[ret > 0].mean() / abs(ret[ret < 0].mean()) if (ret < 0).any() else np.inf
    return win_prob - (1 - win_prob) / win_loss_ratio if win_loss_ratio != 0 else 0

def payoff_ratio(ret):
    """Payoff ratio (avg win / avg loss)"""
    if len(ret) == 0 or not (ret < 0).any():
        return np.inf
    return ret[ret > 0].mean() / abs(ret[ret < 0].mean())

def profit_factor(ret):
    """Profit factor"""
    if len(ret) == 0 or not (ret < 0).any():
        return np.inf
    return ret[ret > 0].sum() / abs(ret[ret < 0].sum())

def gain_pain_ratio(ret):
    """Gain/Pain ratio"""
    if len(ret) == 0 or not (ret < 0).any():
        return np.inf
    return ret.mean() / abs(ret[ret < 0].mean())

def common_sense_ratio(ret):
    """Common Sense ratio"""
    pf = profit_factor(ret)
    tr = tail_ratio(ret)
    return pf * tr if tr != np.inf else np.inf

def cpc_index(ret):
    """CPC Index"""
    return payoff_ratio(ret) * profit_factor(ret) * (ret > 0).mean()

def tail_ratio(ret):
    """Tail ratio"""
    if len(ret) < 2:
        return np.inf
    q05 = ret.quantile(0.05)
    return ret.quantile(0.95) / abs(q05) if q05 != 0 else np.inf

def outlier_win_ratio(ret):
    """Outlier win ratio"""
    if len(ret) == 0 or not (ret > 0).any():
        return 0
    upper = ret.mean() + 3 * ret.std()
    lower = ret.mean() - 3 * ret.std()
    outliers = ret[(ret > upper) | (ret < lower)]
    win_out = outliers[outliers > 0]
    return win_out.mean() / ret[ret > 0].mean() if not win_out.empty else 0

def outlier_loss_ratio(ret):
    """Outlier loss ratio"""
    if len(ret) == 0 or not (ret < 0).any():
        return 0
    upper = ret.mean() + 3 * ret.std()
    lower = ret.mean() - 3 * ret.std()
    outliers = ret[(ret > upper) | (ret < lower)]
    loss_out = outliers[outliers < 0]
    return abs(loss_out.mean()) / abs(ret[ret < 0].mean()) if not loss_out.empty else 0

def avg_drawdown(ret):
    """Average drawdown"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret) + 1
    dd = (cum - cum.cummax()) / cum.cummax()
    in_dd = dd < 0
    dd_groups = (in_dd != in_dd.shift()).cumsum()
    avg_dd = dd[in_dd].groupby(dd_groups).mean().mean() if in_dd.any() else 0
    return avg_dd

def avg_dd_days(ret):
    """Average drawdown days"""
    if len(ret) == 0:
        return 0
    cum = cum_returns(ret) + 1
    dd = (cum - cum.cummax()) / cum.cummax()
    in_dd = dd < 0
    dd_groups = (in_dd != in_dd.shift()).cumsum()
    dd_lengths = in_dd.groupby(dd_groups).sum()
    return dd_lengths.mean() if not dd_lengths.empty else 0

def win_rate(ret, period='D'):
    """Win rate by period"""
    if len(ret) == 0:
        return 0
    resampled = ret.resample(period).sum()
    return (resampled > 0).mean() * 100 if len(resampled) > 0 else 0

def calculate_all_metrics(returns, rf=0.0):
    """
    Calculate comprehensive performance metrics
    
    Parameters:
    -----------
    returns : pd.Series
        Daily returns series with datetime index
    rf : float
        Risk-free rate (annualized)
    
    Returns:
    --------
    dict : Dictionary of all metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics['Risk-Free Rate'] = rf * 100
    metrics['Time in Market'] = (returns != 0).mean() * 100 if len(returns) > 0 else 0
    metrics['Cumulative Return'] = cum_returns(returns).iloc[-1] * 100 if len(returns) > 0 else 0
    metrics['CAGR'] = cagr(returns) * 100
    metrics['Sharpe'] = sharpe(returns, rf)
    metrics['Sortino'] = sortino(returns, rf)
    metrics['Sortino/√2'] = metrics['Sortino'] / np.sqrt(2) if 'Sortino' in metrics else 0
    metrics['Omega'] = omega(returns, rf)
    metrics['Max Drawdown'] = max_drawdown(returns) * 100
    metrics['Longest DD Days'] = drawdown_duration(returns)
    metrics['Volatility (ann.)'] = volatility(returns) * 100
    metrics['Calmar'] = calmar(returns)
    metrics['Skew'] = returns.skew() if len(returns) > 2 else 0
    metrics['Kurtosis'] = returns.kurt() if len(returns) > 3 else 0
    
    # Expected returns
    metrics['Expected Daily'] = returns.mean() * 100 if len(returns) > 0 else 0
    metrics['Expected Monthly'] = returns.resample('M').sum().mean() * 100 if len(returns) > 0 else 0
    metrics['Expected Yearly'] = returns.resample('Y').sum().mean() * 100 if len(returns) > 0 else 0
    
    # Risk metrics
    metrics['Kelly Criterion'] = kelly_criterion(returns) * 100
    metrics['Daily Value-at-Risk'] = value_at_risk(returns) * 100
    metrics['Expected Shortfall (cVaR)'] = conditional_var(returns) * 100
    
    # Gain/Pain metrics
    metrics['Gain/Pain Ratio'] = gain_pain_ratio(returns)
    metrics['Gain/Pain (1M)'] = gain_pain_ratio(returns.resample('M').sum())
    metrics['Payoff Ratio'] = payoff_ratio(returns)
    metrics['Profit Factor'] = profit_factor(returns)
    metrics['Common Sense Ratio'] = common_sense_ratio(returns)
    metrics['CPC Index'] = cpc_index(returns)
    metrics['Tail Ratio'] = tail_ratio(returns)
    metrics['Outlier Win Ratio'] = outlier_win_ratio(returns)
    metrics['Outlier Loss Ratio'] = outlier_loss_ratio(returns)
    
    # Time-based returns
    metrics['MTD'] = returns[returns.index >= returns.index[-1] - pd.Timedelta(30, 'D')].sum() * 100 if len(returns) > 0 else 0
    metrics['3M'] = returns[returns.index >= returns.index[-1] - pd.Timedelta(90, 'D')].sum() * 100 if len(returns) > 0 else 0
    metrics['6M'] = returns[returns.index >= returns.index[-1] - pd.Timedelta(180, 'D')].sum() * 100 if len(returns) > 0 else 0
    metrics['YTD'] = returns[returns.index.year == returns.index[-1].year].sum() * 100 if len(returns) > 0 else 0
    metrics['1Y'] = returns[returns.index >= returns.index[-1] - pd.Timedelta(365, 'D')].sum() * 100 if len(returns) > 0 else 0
    metrics['All-time (ann.)'] = cagr(returns) * 100
    
    # Best/Worst
    metrics['Best Day'] = returns.max() * 100 if len(returns) > 0 else 0
    metrics['Worst Day'] = returns.min() * 100 if len(returns) > 0 else 0
    metrics['Best Month'] = returns.resample('M').sum().max() * 100 if len(returns) > 0 else 0
    metrics['Worst Month'] = returns.resample('M').sum().min() * 100 if len(returns) > 0 else 0
    metrics['Best Year'] = returns.resample('Y').sum().max() * 100 if len(returns) > 0 else 0
    metrics['Worst Year'] = returns.resample('Y').sum().min() * 100 if len(returns) > 0 else 0
    
    # Drawdown metrics
    metrics['Avg. Drawdown'] = avg_drawdown(returns) * 100
    metrics['Avg. Drawdown Days'] = avg_dd_days(returns)
    metrics['Recovery Factor'] = recovery_factor(returns)
    metrics['Ulcer Index'] = ulcer_index(returns)
    metrics['Serenity Index'] = serenity_index(returns, rf)
    
    # Monthly metrics
    metrics['Avg. Up Month'] = returns.resample('M').sum()[returns.resample('M').sum() > 0].mean() * 100 if len(returns.resample('M').sum()[returns.resample('M').sum() > 0]) > 0 else 0
    metrics['Avg. Down Month'] = returns.resample('M').sum()[returns.resample('M').sum() < 0].mean() * 100 if len(returns.resample('M').sum()[returns.resample('M').sum() < 0]) > 0 else 0
    
    # Win rates
    metrics['Win Days %'] = win_rate(returns, 'D')
    metrics['Win Month %'] = win_rate(returns, 'M')
    metrics['Win Quarter %'] = win_rate(returns, 'Q')
    metrics['Win Year %'] = win_rate(returns, 'Y')
    
    # Advanced metrics
    if len(returns) > 1:
        n = len(returns)
        sr = sharpe(returns, rf)
        metrics['Prob. Sharpe Ratio'] = (1 / (1 + np.exp(-sr * np.sqrt(n)))) * 100
        autocorr = returns.autocorr(lag=1)
        adj_std = returns.std() * np.sqrt((1 + 2 * autocorr) / (1 - autocorr)) if autocorr != 1 else returns.std()
        metrics['Smart Sharpe'] = (returns.mean() - rf/252) / adj_std * np.sqrt(252) if adj_std != 0 else 0
        metrics['Smart Sortino'] = sortino(returns, rf) / np.sqrt(1 + 2 * autocorr) if 1 + 2 * autocorr > 0 else sortino(returns, rf)
        metrics['Smart Sortino/√2'] = metrics['Smart Sortino'] / np.sqrt(2) if 'Smart Sortino' in metrics else 0
    else:
        metrics['Prob. Sharpe Ratio'] = 0
        metrics['Smart Sharpe'] = 0
        metrics['Smart Sortino'] = 0
        metrics['Smart Sortino/√2'] = 0
    
    return metrics

def get_drawdowns(returns):
    """Get detailed drawdown periods"""
    if len(returns) == 0:
        return pd.DataFrame()
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    dd = (cum / peak - 1) * 100
    in_dd = dd < 0
    dd_starts = dd[(dd.shift(1) >= 0) & (dd < 0)].index
    dd_ends = dd[(dd.shift(-1) >= 0) & (dd < 0)].index
    drawdowns = []
    for start, end in zip(dd_starts, dd_ends):
        period_dd = dd[start:end]
        min_dd = period_dd.min()
        days = (end - start).days
        drawdowns.append({'Started': start, 'Recovered': end, 'Drawdown': min_dd, 'Days': days})
    df_dd = pd.DataFrame(drawdowns).sort_values('Drawdown').reset_index(drop=True)
    return df_dd

def get_monthly_table(returns):
    """Get monthly performance grid"""
    if len(returns) == 0:
        return pd.DataFrame()
    monthly = returns.resample('M').sum() * 100
    monthly_df = pd.DataFrame({'Return': monthly.values}, index=monthly.index)
    monthly_df['Year'] = monthly_df.index.year
    monthly_df['Month'] = monthly_df.index.month
    pivot = monthly_df.pivot(index='Year', columns='Month', values='Return')
    pivot.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(pivot.columns)]
    pivot['Year Total'] = pivot.sum(axis=1)
    return pivot
