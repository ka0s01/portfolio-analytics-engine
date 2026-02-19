import numpy as np
import pandas as pd
from returns_calc import *

def calculate_excess_returns(potfolio_returns,benchmark_returns):
    exr = potfolio_returns - benchmark_returns
    return exr

def annualize_excess_returns(portfolio_returns,benchmark_returns):
    return annualized_returns(portfolio_returns)-annualized_returns(benchmark_returns)

def tracking_error(excess_returns):
    return excess_returns.std() * np.sqrt(252)
    

def calculate_information_ratio(portfolio_returns, benchmark_returns):
    excess = calculate_excess_returns(portfolio_returns, benchmark_returns)
    return annualized_returns(excess) / tracking_error(excess)

def calculate_beta(portfolio_returns,benchmark_returns):
    return portfolio_returns.cov(benchmark_returns)/benchmark_returns.var()




