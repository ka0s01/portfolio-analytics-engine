import numpy as np
import pandas as pd
from returns_calc import *
def calculate_volatility(returns,annualize=True,trading_days=252):
    volatility = returns.std().item()
    if annualize:
        annual_vol = volatility*np.sqrt(trading_days)
        return annual_vol
    return volatility

def calculate_sharpe_ratio (returns,risk_free_rate = 0.065,trading_days=252):
    annual_returns = annualized_returns(returns)
    annual_volatility = calculate_volatility(returns,annualize=True)
    excess_return = annual_returns - risk_free_rate
    sharpe_ratio = excess_return/annual_volatility
    return sharpe_ratio


def calculate_max_drawdown(returns):
    cum_returns = calculate_cumulative_returns(returns)
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max)/(1+running_max)
    max_dd = drawdown.min()
    return max_dd


def calculate_downside_deviation(returns,annualize=True,trading_days=252):
    negative_returns = returns[returns<0].dropna()
    negative_volatility = calculate_volatility(negative_returns,annualize=annualize)
    return negative_volatility


def calculate_sortino_ratio(returns,risk_free_rate = 0.065,trading_days=252):
    annual_returns = annualized_returns(returns)
    excess_return = annual_returns-risk_free_rate
    downside_deviation = calculate_downside_deviation(returns)
    sortino_ratio = excess_return/downside_deviation
    return sortino_ratio



def calculate_rolling_cagr(returns, window=252):
    """
    Calculate rolling CAGR over a specified window.
    
    Args:
        returns: Series of daily returns
        window: Rolling window size in days (default 252 = 1 year)
        
    Returns:
        Series of rolling CAGR values
    """
    def cagr_for_window(window_returns):
        total_growth = (1 + window_returns).prod()
        n_days = len(window_returns)
        if n_days == 0:
            return np.nan
        cagr = total_growth ** (252 / n_days) - 1
        return cagr
    
    rolling_cagr = returns.rolling(window=window).apply(cagr_for_window, raw=False)
    return rolling_cagr


def calculate_win_rate(returns):
    """
    Calculate the percentage of positive return days.
    
    Returns:
        Float: win rate as a decimal (e.g., 0.55 for 55%)
    """
    positive_days = (returns > 0).sum()
    total_days = len(returns)
    return positive_days / total_days


def calculate_avg_gain_loss(returns):
    """
    Calculate average gain on winning days vs average loss on losing days.
    
    Returns:
        Dictionary with 'avg_gain', 'avg_loss', and 'gain_loss_ratio'
    """
    gains = returns[returns > 0]
    losses = returns[returns < 0]
    
    avg_gain = gains.mean() if len(gains) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    
    # Gain/loss ratio (how much you make on wins vs lose on losses)
    gain_loss_ratio = abs(avg_gain / avg_loss) if avg_loss != 0 else np.inf
    
    return {
        'avg_gain': avg_gain,
        'avg_loss': avg_loss,
        'gain_loss_ratio': gain_loss_ratio
    }