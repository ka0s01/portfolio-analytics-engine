from data_loader import download_stock_data
from returns_calc import *
from visualization import *
df = download_stock_data('RELIANCE.NS', period='1y')
prices = df['Close']

returns = calculate_returns(prices)
cum_returns = calculate_cumulative_returns(returns)
cagr = calculate_cagr(prices)

print(f"CAGR: {cagr:.2%}")
print(f"Final cumulative return: {cum_returns.iloc[-1].item():.2%}")
print(f"Match? {abs(cagr - cum_returns.iloc[-1].item()) < 0.01}")  # Should be close for 1 year

