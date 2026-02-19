import pandas as pd
import numpy as np
from data_loader import *
from returns_calc import *
from risk_metrics import *
from market_metrics import *


class Portfolio:
    def __init__(self, tickers, weights):
        if len(tickers) != len(weights):
            raise ValueError("Number of Tickers must be equal to Number of Weights")
        
        if abs(sum(weights) - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")
        
        self.tickers = tickers
        self.weights = weights
        self.stock_data = {}
        self.portfolio_returns = None
        self.benchmark_ticker = "^NSEI"
        self.benchmark_data = None
        self.benchmark_returns = None
    
    
    @classmethod
    def from_csv(cls, filepath):
        df = pd.read_csv(filepath)
        tickers = df['Ticker'].tolist()
        amounts = df['Amount'].tolist()
        total = sum(amounts)
        weights = [amount / total for amount in amounts]
        return cls(tickers, weights)
    
    
    def download_data(self, period='1y', start_date=None, end_date=None):
        print(f"Downloading data for {len(self.tickers)} stocks...")
        
        for ticker in self.tickers:
            try:
                df = download_stock_data(ticker, start_date=start_date, end_date=end_date, period=period)
                self.stock_data[ticker] = df
            except Exception as e:
                print(f"✗ Failed to download {ticker}: {e}")
        
        print(f"✓ Downloaded {len(self.stock_data)}/{len(self.tickers)} stocks\n")

        try:
            self.benchmark_data = download_stock_data(self.benchmark_ticker,start_date=start_date,end_date=end_date,period=period)
            print(f"Bench mark data downloaded")
        except Exception as e:
            print(F"Failed to download Benchmarks Data {e}")
            
    
    
    def _validate_stock_data(self):
        print("Validating stock data quality...")
        print("-" * 60)
        
        issues_found = False
        
        for ticker in self.tickers:
            if ticker not in self.stock_data:
                print(f"  ✗ {ticker}: No data downloaded")
                issues_found = True
                continue
            
            df = self.stock_data[ticker]
            prices = df['Close']
            
            if isinstance(prices, pd.DataFrame):
                prices = prices.squeeze()
            
            num_points = len(prices)
            print(f"  {ticker}: {num_points} days", end="")
            
            # Check for constant prices (bad ticker)
            if prices.nunique() == 1:
                print(" - ✗ WARNING: Constant price (bad ticker?)")
                issues_found = True
                continue
            
            # Check for too many identical consecutive prices
            price_changes = prices.pct_change().fillna(0)
            zero_changes = (price_changes == 0).sum()
            if zero_changes > num_points * 0.3:
                print(f" - ⚠ WARNING: {zero_changes} days with no price change")
                issues_found = True
            else:
                print(" - ✓")
        
        if issues_found:
            print("\n⚠ Data quality issues detected. Review warnings above.")
        else:
            print("\n✓ All stocks passed quality checks")
        
        print("-" * 60)
    
    
    def calculate_portfolio_returns(self):
        
        if not self.stock_data:
            raise ValueError("No data! Call download_data() first")
        
        # Build price DataFrame
        prices_df = pd.DataFrame()
        original_lengths = {}
        
        for ticker in self.tickers:
            close_prices = self.stock_data[ticker]['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.squeeze()
            
            prices_df[ticker] = close_prices
            original_lengths[ticker] = len(close_prices)
        
        # Check alignment quality BEFORE dropping
        print("\nData Alignment Analysis:")
        print("-" * 60)
        
        total_dates = len(prices_df)
        print(f"Total unique dates: {total_dates}")
        
        data_availability = prices_df.notna().sum(axis=1)
        fully_aligned_dates = (data_availability == len(self.tickers)).sum()
        
        print(f"Dates with ALL stocks: {fully_aligned_dates} ({fully_aligned_dates/total_dates*100:.1f}%)")
        
        # Check per-stock overlap
        print("\nPer-stock overlap:")
        for ticker in self.tickers:
            available = prices_df[ticker].notna().sum()
            overlap_pct = available / total_dates * 100
            
            if overlap_pct < 80:
                print(f"  ⚠ {ticker}: {available}/{total_dates} days ({overlap_pct:.1f}%) - LOW OVERLAP")
            else:
                print(f"  ✓ {ticker}: {available}/{total_dates} days ({overlap_pct:.1f}%)")
        
        # Drop missing data
        aligned_df = prices_df.dropna()
        dropped_dates = total_dates - len(aligned_df)
        
        print(f"\nAfter alignment:")
        print(f"  Kept: {len(aligned_df)} days")
        print(f"  Dropped: {dropped_dates} days ({dropped_dates/total_dates*100:.1f}%)")
        
        # Warn if too much data lost
        if dropped_dates / total_dates > 0.2:
            print(f"\n  ⚠ WARNING: Lost {dropped_dates/total_dates*100:.1f}% of data due to alignment")
            print(f"  This may indicate stocks trading on different exchanges or bad tickers")
        
        # Error if insufficient data
        if len(aligned_df) < 60:
            print(f"\n  ✗ ERROR: Only {len(aligned_df)} aligned days - insufficient for analysis")
            print(f"  Need at least 60 days. Check if tickers are valid.")
            raise ValueError("Insufficient aligned data")
        
        print("-" * 60)
        
        # Align with benchmark BEFORE calculating returns
        aligned_df = self._align_with_benchmark(aligned_df)
        
        # Calculate returns for each stock from aligned prices
        returns_df = pd.DataFrame()
        for ticker in self.tickers:
            returns_df[ticker] = calculate_returns(aligned_df[ticker])

        self.stock_returns_df = returns_df
        
        # Calculate weighted portfolio returns
        portfolio_returns = (returns_df * self.weights).sum(axis=1)
        self.portfolio_returns = portfolio_returns
        # Final safety alignment between portfolio and benchmark returns
        if self.benchmark_returns is not None:
            common_idx = self.portfolio_returns.index.intersection(self.benchmark_returns.index)
            self.portfolio_returns = self.portfolio_returns.loc[common_idx]
            self.benchmark_returns = self.benchmark_returns.loc[common_idx]

        return self.portfolio_returns
    
    
    def _align_with_benchmark(self, aligned_df):
        if self.benchmark_data is None:
            print("\n  WARNING: No benchmark data available")
            return aligned_df
        
        # Extract benchmark close prices
        benchmark_prices = self.benchmark_data['Close']
        if isinstance(benchmark_prices, pd.DataFrame):
            benchmark_prices = benchmark_prices.squeeze()
        
        # Find common dates between portfolio and benchmark
        common_dates = aligned_df.index.intersection(benchmark_prices.index)
        
        # Filter both to common dates
        aligned_df = aligned_df.loc[common_dates]
        aligned_benchmark_prices = benchmark_prices.loc[common_dates]
        
        # Calculate benchmark returns from filtered prices
        self.benchmark_returns = calculate_returns(aligned_benchmark_prices)
        
        print(f"\nBenchmark aligned: {len(common_dates)} common trading days")
        
        return aligned_df

    
    
    def get_metrics(self, risk_free_rate=0.065):
        if self.portfolio_returns is None:
            raise ValueError("Calculate portfolio returns first!")
        
        metrics = {
            'annual_return': annualized_returns(self.portfolio_returns),
            'volatility': calculate_volatility(self.portfolio_returns),
            'sharpe_ratio': calculate_sharpe_ratio(self.portfolio_returns, risk_free_rate),
            'sortino_ratio': calculate_sortino_ratio(self.portfolio_returns, risk_free_rate),
            'max_drawdown': calculate_max_drawdown(self.portfolio_returns)
        }
        
        return metrics
    def display_market_comparison(self):
        if self.benchmark_returns is None:
            print("No benchmark Data found")
            return
        print("\n" + "=" * 60)
        print("MARKET COMPARISON")
        print("=" * 60)
        excess_ret = calculate_excess_returns(self.portfolio_returns,self.benchmark_returns)
        annualized_excess_ret = annualize_excess_returns(self.portfolio_returns,self.benchmark_returns)
        te = tracking_error(excess_ret)
        ir = calculate_information_ratio(self.portfolio_returns,self.benchmark_returns)
        beta = calculate_beta(self.portfolio_returns,self.benchmark_returns)
        
        print(f"\nAnnualized Excess Return: {annualized_excess_ret:>10.2%}")
        print(f"Tracking Error:           {te:>10.2%}")
        print(f"Information Ratio:        {ir:>10.3f}")
        print(f"Beta:                     {beta:>10.3f}")


    
    def display_results(self, metrics):
        print("=" * 60)
        print("PORTFOLIO PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        print("\nPortfolio Composition:")
        print("-" * 60)
        for ticker, weight in zip(self.tickers, self.weights):
            print(f"  {ticker:<20} {weight:>8.1%}")
        print("-" * 60)
        print(f"  {'TOTAL':<20} {sum(self.weights):>8.1%}")
        
        print("\n\nPerformance Metrics:")
        print("-" * 60)
        print(f"  Annual Return:      {metrics['annual_return']:>10.2%}")
        print(f"  Volatility:         {metrics['volatility']:>10.2%}")
        print(f"  Max Drawdown:       {metrics['max_drawdown']:>10.2%}")
        print(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:>10.3f}")
        print(f"  Sortino Ratio:      {metrics['sortino_ratio']:>10.3f}")
        print("=" * 60)
        
        print()
    def display_risk_comparison(self, risk_free_rate=0.065):
        
        if self.benchmark_returns is None:
            print("No benchmark data available")
            return
        
        print("\n" + "=" * 60)
        print("RISK COMPARISON")
        print("=" * 60)
        
        from risk_metrics import (
            calculate_volatility,
            calculate_max_drawdown,
            calculate_sharpe_ratio,
            calculate_downside_deviation
        )
        
        # Calculate metrics
        portfolio_vol = calculate_volatility(self.portfolio_returns)
        market_vol = calculate_volatility(self.benchmark_returns)
        relative_vol = portfolio_vol / market_vol
        
        portfolio_dd = calculate_max_drawdown(self.portfolio_returns)
        market_dd = calculate_max_drawdown(self.benchmark_returns)
        relative_dd = portfolio_dd / market_dd
        
        portfolio_sharpe = calculate_sharpe_ratio(self.portfolio_returns, risk_free_rate)
        market_sharpe = calculate_sharpe_ratio(self.benchmark_returns, risk_free_rate)
        
        portfolio_downside = calculate_downside_deviation(self.portfolio_returns)
        market_downside = calculate_downside_deviation(self.benchmark_returns)
        
        # Display
        print("\nVolatility:")
        print(f"  Portfolio:     {portfolio_vol:>10.2%}")
        print(f"  Market:        {market_vol:>10.2%}")
        print(f"  Relative:      {relative_vol:>10.2f}x")
        
        print("\nMaximum Drawdown:")
        print(f"  Portfolio:     {portfolio_dd:>10.2%}")
        print(f"  Market:        {market_dd:>10.2%}")
        print(f"  Relative:      {relative_dd:>10.2f}x")
        
        print("\nSharpe Ratio:")
        print(f"  Portfolio:     {portfolio_sharpe:>10.3f}")
        print(f"  Market:        {market_sharpe:>10.3f}")
        
        print("\nDownside Deviation:")
        print(f"  Portfolio:     {portfolio_downside:>10.2%}")
        print(f"  Market:        {market_downside:>10.2%}")
    
        print("=" * 60)
    def display_portfolio_structure(self):
        
        print("\n" + "=" * 60)
        print("PORTFOLIO STRUCTURE")
        print("=" * 60)
        
        from portfolio_metrics import (
            total_contribution_by_stock,
            identify_top_contributors,
            calculate_concentration,
            calculate_effective_n_stocks
        )
        
        # Calculate metrics
        contributions = total_contribution_by_stock(self.stock_returns_df, self.weights)
        top_bottom = identify_top_contributors(self.stock_returns_df, self.weights)
        concentration = calculate_concentration(self.weights)
        effective_n = calculate_effective_n_stocks(self.weights)
        
        # Display contribution by stock
        print("\nReturn Contribution by Stock:")
        print("-" * 60)
        for ticker, contrib in contributions.sort_values(ascending=False).items():
            print(f"  {ticker:<20} {contrib:>10.2%}")
        
        # Display top/bottom
        print("\n" + "-" * 60)
        print(f"\nLargest Contributor:  {top_bottom['top_contributor']:<15} "
            f"{top_bottom['top_contributor_value']:>10.2%}")
        print(f"Largest Dragger:      {top_bottom['top_dragger']:<15} "
            f"{top_bottom['top_dragger_value']:>10.2%}")
        
        # Display diversification metrics
        print("\nDiversification Metrics:")
        print("-" * 60)
        print(f"  Max Concentration:       {concentration:>10.1%}")
        print(f"  Effective # of Stocks:   {effective_n:>10.1f}")
        
        


    def analyze(self, period='1y', risk_free_rate=0.065):
        
        # Download data
        self.download_data(period=period)
        
        # Validate data quality
        self._validate_stock_data()
        
        # Calculate portfolio returns (with alignment checks)
        print("\nCalculating portfolio returns...")
        self.calculate_portfolio_returns()
        
        # Calculate metrics
        print("\nCalculating risk metrics...")
        metrics = self.get_metrics(risk_free_rate)

        # Display results
        print()
        self.display_results(metrics)

        #calculate marketmetrics
        print("\nCalculating market metrics...")
        print()
        self.display_market_comparison()

        
        print()
        self.display_risk_comparison()
        
        print()
        self.display_portfolio_structure()
        return metrics


if __name__ == "__main__":
    portfolio = Portfolio.from_csv('portfolio.csv')
    portfolio.analyze(period='1y')