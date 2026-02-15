import pandas as pd
import numpy as np

def calculate_returns(prices):
    returns = prices.pct_change()
    returns = returns.dropna()

    return returns

def calculate_cumulative_returns(returns):
    multipliers = returns+1
    cumulative_multiplier = multipliers.cumprod()
    cumulative_returns = cumulative_multiplier-1
    cumulative_returns.dropna()
    #returns CR as a series
    return cumulative_returns 

def calculate_cagr(prices):
    start_val = prices.iloc[0].item()
    end_val = prices.iloc[-1].item()
    years = len(prices)/252
    cagr = (end_val/start_val)**(1/years) -1
    #returns as a float
    return cagr

def annualized_returns(returns):
    total_growth = (1+returns).prod()
    n_days = len(returns)
    ann_returns = total_growth ** (252/n_days)-1
    return ann_returns