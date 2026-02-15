import numpy as np
import pandas as pd

def calculate_volatility(returns,annualize=True,trading_days=252):
    volatility = returns.std().item()
    if annualize:
        annual_vol = volatility*np.sqrt(trading_days)
        return annual_vol
    return volatility

def calculate_sharpe_ratio (returns):
    annual_returns = 
# from data_loader import download_stock_data
# from returns_calc import calculate_returns

# df = download_stock_data('RELIANCE.NS', period='1y')
# prices = df['Close'].squeeze()
# returns = calculate_returns(prices)

# # Test both daily and annual
# daily_vol = calculate_volatility(returns, annualize=False)
# annual_vol = calculate_volatility(returns, annualize=True)

# print(f"Daily Volatility: {daily_vol:.4f} ({daily_vol*100:.2f}%)")
# print(f"Annual Volatility: {annual_vol:.4f} ({annual_vol*100:.2f}%)")
# print(f"Ratio: {annual_vol/daily_vol:.2f} (should be close to 15.87)")