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

def calculate_sortino_ratio(returns,risk_free_rate = 0.065,trading_days=252):
    annual_returns = annualized_returns(returns)
    excess_return = annual_returns-risk_free_rate
    negative_returns = returns[returns<0].dropna()
    negative_volatility = calculate_volatility(negative_returns)
    sortino_ratio = excess_return/negative_volatility
    return sortino_ratio

def calculate_max_drawdown(returns):
    cum_returns = calculate_cumulative_returns(returns)
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max)/(1+running_max)
    max_dd = drawdown.min()
    return max_dd