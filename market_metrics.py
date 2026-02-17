import numpy as np
from returns_calc import *

def calculate_excess_returns(potfolio_returns,benchmark_returns):
    exr = potfolio_returns - benchmark_returns
    return exr

def annualize_excess_returns(portfolio_returns,benchmark_returns):
    return annualized_returns(portfolio_returns)-annualized_returns(benchmark_returns)
