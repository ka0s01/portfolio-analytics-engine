"""
Main script to analyze portfolio performance.

Usage:
1. Create portfolio.csv with your holdings
2. Run: python main.py
"""

import os
import pandas as pd
from portfolio import Portfolio


def main():
    """Main entry point for portfolio analysis."""
    
    print("=" * 60)
    print("PORTFOLIO PERFORMANCE ANALYZER")
    print("=" * 60)
    print()
    
    # Check if portfolio.csv exists
    if not os.path.exists('portfolio.csv'):
        print("✗ portfolio.csv not found!\n")
        print("Creating example portfolio.csv...\n")
        create_example_csv()
        print("✓ Created portfolio.csv with example data")
        print("\nPlease edit portfolio.csv with your actual holdings and run again.")
        print("\nFormat:")
        print("  Ticker,Amount")
        print("  RELIANCE.NS,25000")
        print("  TCS.NS,20000")
        print("  ...\n")
        return
    
    # Check if CSV is empty or invalid
    try:
        df = pd.read_csv('portfolio.csv')
        
        # Check if empty
        if df.empty or len(df) == 0:
            print("✗ portfolio.csv is empty!\n")
            print("Please add your holdings to portfolio.csv")
            print("\nFormat:")
            print("  Ticker,Amount")
            print("  RELIANCE.NS,25000")
            print("  TCS.NS,20000")
            print("  ...\n")
            return
        
        # Check if required columns exist
        if 'Ticker' not in df.columns or 'Amount' not in df.columns:
            print("✗ portfolio.csv has incorrect format!\n")
            print("Required columns: Ticker, Amount")
            print("\nExample:")
            print("  Ticker,Amount")
            print("  RELIANCE.NS,25000")
            print("  TCS.NS,20000\n")
            return
        
        # Check if there's at least one stock
        if len(df) < 1:
            print("✗ No stocks found in portfolio.csv!\n")
            print("Please add at least one stock.\n")
            return
        
        print(f"✓ Found portfolio.csv with {len(df)} stock(s)\n")
        
    except Exception as e:
        print(f"✗ Error reading portfolio.csv: {e}\n")
        print("Please check the file format.\n")
        return
    
    # Ask user for time period
    print("Select analysis period:")
    print("  1. Last 6 months (6mo)")
    print("  2. Last 1 year (1y) [DEFAULT]")
    print("  3. Last 2 years (2y)")
    print("  4. Last 5 years (5y)")
    print("  5. Custom dates")
    
    choice = input("\nChoice (1-5, press Enter for default): ").strip()
    
    if choice == '1':
        period = '6mo'
    elif choice == '3':
        period = '2y'
    elif choice == '4':
        period = '5y'
    elif choice == '5':
        start = input("Start date (YYYY-MM-DD): ")
        end = input("End date (YYYY-MM-DD): ")
        period = None
    else:
        period = '1y'  # Default
    
    print()
    
    # Load portfolio
    try:
        portfolio = Portfolio.from_csv('portfolio.csv')
        
        # Run analysis
        if choice == '5':
            portfolio.analyze(start_date=start, end_date=end)
        else:
            portfolio.analyze(period=period)
            
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        print("\nPlease check:")
        print("  1. Ticker symbols are valid (e.g., RELIANCE.NS for NSE)")
        print("  2. Amounts are positive numbers")
        print("  3. You have internet connection\n")


def create_example_csv():
    """Create an example portfolio.csv file."""
    example = """Ticker,Amount
RELIANCE.NS,25000
TCS.NS,20000
HDFCBANK.NS,15000
INFY.NS,15000
ICICIBANK.NS,25000"""
    
    with open('portfolio.csv', 'w') as f:
        f.write(example)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("\nIf the issue persists, please check your portfolio.csv file.")