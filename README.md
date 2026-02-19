# Portfolio Analyzer Dashboard

A comprehensive  dashboard for analyzing stock portfolio performance with market comparison, risk metrics, and behavioral analysis.

## 📖 What This Project Is

This is a **portfolio diagnostic tool** designed to help  investors understand their investment performance and risk profile. It answers four critical questions:

1. **Am I outperforming the market?** - Compare your returns against a benchmark (like NIFTY 50)
2. **Is my portfolio survivable long-term?** - Assess volatility, drawdowns, and risk-adjusted returns
3. **What positions actually drive my performance?** - Identify which stocks contribute most to returns
4. **Is my diversification real or an illusion?** - Measure true diversification beyond just counting stocks


**Important: This tool evaluates portfolio STRATEGIES, not personal P&L.**

When you run an analysis, you're asking: "How would THIS allocation have performed over THIS period?" — not "What did I personally make on my actual investments?"

The difference:
- **Strategy Testing** ✅ - "A portfolio of 40% RELIANCE, 30% TCS, 30% INFY returned 18% with 22% volatility over the past year"
- **Personal P&L** ❌ - "I bought RELIANCE in March, TCS in June, and INFY in September. What's my actual return accounting for when I bought each stock?"


## 📸 Dashboard Preview
<img width="1909" height="931" alt="image" src="https://github.com/user-attachments/assets/67011614-1493-4513-9d68-2af3f9d25b21" />

<img width="1916" height="883" alt="image" src="https://github.com/user-attachments/assets/b8984f5d-2037-4ce1-97c6-39c7c5745a90" />
<img width="1580" height="580" alt="image" src="https://github.com/user-attachments/assets/e2558c14-0c4f-495a-bc28-4771183fcc90" />
<img width="282" height="903" alt="image" src="https://github.com/user-attachments/assets/d94ac90e-1d8e-478e-9f66-31dea742c38d" />
<img width="283" height="915" alt="image" src="https://github.com/user-attachments/assets/83da3796-d154-453c-8f74-79eeb2dcb87e" />



## ✅ What This Tool CAN Do

### Performance Analysis
- Calculate annualized returns, volatility, Sharpe ratio, Sortino ratio
- Show cumulative returns over time
- Compare your performance against market benchmarks
- Identify maximum drawdown periods

### Market Comparison
- Calculate beta (how your portfolio moves with the market)
- Measure tracking error (consistency of deviation from benchmark)
- Compute information ratio (risk-adjusted outperformance)
- Quantify excess returns vs benchmark

### Risk Assessment
- Compare your volatility to market volatility
- Analyze downside deviation (losses only)
- Evaluate risk-adjusted returns vs benchmark
- Assess relative drawdowns

### Portfolio Structure
- Show contribution by each stock to total returns
- Identify largest contributors and draggers
- Measure concentration risk
- Calculate effective diversification (not just number of stocks)

### Behavioral Analysis
- Calculate win rate (percentage of positive days)
- Measure average gain vs average loss
- Show rolling 1-year CAGR (requires sufficient data)
- Evaluate consistency of performance

### Data & Export
- Download complete analysis as JSON
- Generate interactive charts
- View all metrics in one dashboard

## ❌ What This Tool CANNOT Be Used For

### ⚠️ NOT for Trading Signals
This tool **does not**:
- Predict future stock prices
- Generate buy/sell recommendations
- Provide timing signals for entry/exit
- Suggest which stocks to add or remove


### ⚠️ NOT for Tax or Personal P&L Tracking

**This is a STRATEGY analyzer, not a personal portfolio tracker.**

This tool **does not**:
- Track when you bought each stock (all stocks treated as bought on day 1)
- Calculate your actual realized gains/losses based on your purchase prices
- Account for dividends reinvested
- Handle different purchase dates per stock
- Handle partial sales or additions over time
- Compute tax obligations or cost basis
- Track your actual cash invested vs current value


## Use Cases

### ✅ Testing Portfolio Strategies

Examples:
- "How would a 50-30-20 split between these three stocks have performed?"
- "Is my current allocation better than equal weights?"
- "How does a tech-heavy portfolio compare to a diversified one?"

### ✅ Compare Strategies
Upload different portfolio files to compare:
- Current portfolio vs equal-weight version
- Active picks vs index holdings
- Conservative vs aggressive allocations
- Growth vs value tilt
- Sector rotation strategies

### ✅ Learn About Risk
Understand concepts like:
- Beta: "My portfolio moves 0.6x with the market"
- Sharpe ratio: "I'm getting decent returns for the risk taken"
- Tracking error: "I deviate this much from the index"
- Effective N: "I really only have 6.3 stocks, not 8"

### ✅ Identify Problems
Spot issues like:
- One stock representing 30% of portfolio (concentration)
- High beta with low returns (taking risk without reward)
- Low information ratio (inconsistent outperformance)
- Large drawdowns relative to market




## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Required Files

Make sure these files are in the same directory:

- `dashboard.py` - Main Streamlit application
- `portfolio.py` - Portfolio class and orchestration
- `data_loader.py` - Data downloading functions
- `returns_calc.py` - Return calculation functions
- `risk_metrics.py` - Risk and statistical metrics
- `market_metrics.py` - Benchmark comparison metrics
- `portfolio_metrics.py` - Portfolio structure metrics


## 🎯 Features

### 1. Performance Summary
- Annualized Return
- Volatility
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown

### 2. Market Comparison
- Beta (market sensitivity)
- Information Ratio
- Tracking Error
- Excess Return
- Cumulative returns chart (Portfolio vs Benchmark)

### 3. Risk Quality
- Volatility comparison
- Sharpe ratio comparison
- Downside deviation comparison
- Visual bar charts for all metrics

### 4. Portfolio Structure
- Pie chart of portfolio weights
- Bar chart of return contribution by stock
- Largest contributor and dragger
- Concentration metrics
- Effective diversification (Effective N)

### 5. Behaviour Consistency
- Rolling 1-year CAGR (if data sufficient)
- Win rate (% of positive days)
- Average gain vs average loss
- Gain/loss ratio

### 6. Export
- Download complete analysis as JSON


## 🛠️ Troubleshooting

**Error: "No data downloaded"**
- Check ticker symbols are correct (use .NS for NSE, .BO for BSE)
- Verify internet connection
- Try a longer time period

**Error: "Insufficient aligned data"**
- Need at least 60 trading days
- Some stocks may be newly listed
- Try removing problematic tickers

**Rolling CAGR not showing**
- Needs at least 252 trading days (1 year)
- Select a longer analysis period (2y or 5y)

## 📝 Analysis Flow

1. Upload `portfolio.csv`
2. Select benchmark (default: ^NSEI for Indian market)
3. Choose period (recommend 1y or 2y for comprehensive analysis)
4. Click "🚀 Run Analysis"
5. Wait for data download and calculation (~30 seconds)
6. Explore results section by section
7. Download JSON for record-keeping


## 🔄 Updates

Current version: 1.0.0

Features:
- ✅ Full portfolio analysis
- ✅ Interactive charts with Plotly
- ✅ Benchmark comparison
- ✅ JSON export
- ✅ Risk quality assessment
- ✅ Behavioral analysis

---

Built with Streamlit, Pandas, Plotly, and yfinance.
