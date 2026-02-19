import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from portfolio import Portfolio
from returns_calc import calculate_cumulative_returns
import json

# Page configuration
st.set_page_config(
    page_title="Portfolio Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Fix metric visibility */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #ffffff;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #cccccc;
    }
    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }
    /* Style metric containers */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("Portfolio Analyzer Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Portfolio CSV",
        type=['csv'],
        help="CSV file with columns: Ticker, Amount"
    )
    
    # Benchmark selector
    benchmark = st.selectbox(
        "📈 Benchmark",
        ["^NSEI", "^GSPC", "^DJI", "^IXIC"],
        index=0,
        help="Select market benchmark for comparison"
    )
    
    # Period selector
    period = st.selectbox(
        "📅 Analysis Period",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        help="Historical period for analysis"
    )
    
    # Risk-free rate
    risk_free_rate = st.number_input(
        "🎯 Risk-Free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=6.5,
        step=0.1,
        help="Annual risk-free rate for Sharpe/Sortino calculation"
    ) / 100
    
    st.markdown("---")
    
    # Run analysis button
    run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# Main content
if uploaded_file is not None:
    if run_analysis:
        try:
            # Save uploaded file temporarily
            with open("temp_portfolio.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Initialize portfolio
            with st.spinner("Loading portfolio..."):
                portfolio = Portfolio.from_csv("temp_portfolio.csv")
                portfolio.benchmark_ticker = benchmark
            
            # Download data
            with st.spinner(f"Downloading {period} of market data..."):
                portfolio.download_data(period=period)
            
            # Validate data
            with st.spinner("Validating data quality..."):
                portfolio._validate_stock_data()
            
            # Calculate returns
            with st.spinner("Calculating returns..."):
                portfolio.calculate_portfolio_returns()
            
            # Get metrics
            with st.spinner("Computing metrics..."):
                metrics = portfolio.get_metrics(risk_free_rate)
            
            # Store in session state
            st.session_state['portfolio'] = portfolio
            st.session_state['metrics'] = metrics
            st.session_state['analysis_complete'] = True
            
            st.success("✅ Analysis complete!")
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.stop()

# Display results if analysis is complete
if 'analysis_complete' in st.session_state and st.session_state['analysis_complete']:
    portfolio = st.session_state['portfolio']
    metrics = st.session_state['metrics']
    
    # =====================================================================
    # SECTION 1: PERFORMANCE SUMMARY
    # =====================================================================
    st.header(" Performance Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Annual Return",
            f"{metrics['annual_return']:.2%}",
            delta=f"{metrics['annual_return']:.2%}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Volatility",
            f"{metrics['volatility']:.2%}",
            help="Annualized standard deviation of returns"
        )
    
    with col3:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.3f}",
            help="Risk-adjusted return metric"
        )
    
    with col4:
        st.metric(
            "Sortino Ratio",
            f"{metrics['sortino_ratio']:.3f}",
            help="Downside risk-adjusted return"
        )
    
    with col5:
        st.metric(
            "Max Drawdown",
            f"{metrics['max_drawdown']:.2%}",
            delta=f"{metrics['max_drawdown']:.2%}",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # =====================================================================
    # SECTION 2: MARKET COMPARISON
    # =====================================================================
    st.header(" Market Comparison")
    
    from market_metrics import (
        calculate_excess_returns,
        annualize_excess_returns,
        tracking_error,
        calculate_information_ratio,
        calculate_beta
    )
    
    excess_ret = calculate_excess_returns(portfolio.portfolio_returns, portfolio.benchmark_returns)
    ann_excess = annualize_excess_returns(portfolio.portfolio_returns, portfolio.benchmark_returns)
    te = tracking_error(excess_ret)
    ir = calculate_information_ratio(portfolio.portfolio_returns, portfolio.benchmark_returns)
    beta = calculate_beta(portfolio.portfolio_returns, portfolio.benchmark_returns)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Key Metrics")
        
        st.metric("Beta", f"{beta:.3f}", help="Portfolio sensitivity to market movements")
        st.metric("Information Ratio", f"{ir:.3f}", help="Excess return per unit of tracking error")
        st.metric("Tracking Error", f"{te:.2%}", help="Volatility of excess returns")
        st.metric("Excess Return", f"{ann_excess:.2%}", help="Annualized outperformance vs benchmark")
        
        # Interpretation
        st.markdown("**Interpretation:**")
        if ann_excess > 0:
            st.success(f"✓ Outperformed by {ann_excess:.2%}")
        else:
            st.error(f"✗ Underperformed by {abs(ann_excess):.2%}")
        
        if ir > 0.5:
            st.success("✓ Good risk-adjusted outperformance")
        elif ir > 0:
            st.info("○ Modest outperformance")
        else:
            st.error("✗ Negative information ratio")
    
    with col2:
        st.subheader("Cumulative Returns Comparison")
        
        # Calculate cumulative returns
        portfolio_cum = calculate_cumulative_returns(portfolio.portfolio_returns)
        benchmark_cum = calculate_cumulative_returns(portfolio.benchmark_returns)
        
        # Create comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_cum.index,
            y=portfolio_cum.values * 100,
            name="Portfolio",
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=benchmark_cum.index,
            y=benchmark_cum.values * 100,
            name=benchmark,
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="Portfolio vs Benchmark Performance",
            xaxis_title="Date",
            yaxis_title="Cumulative Return (%)",
            hovermode='x unified',
            height=400,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # =====================================================================
    # SECTION 3: RISK QUALITY
    # =====================================================================
    st.header(" Risk Quality")
    
    from risk_metrics import (
        calculate_volatility,
        calculate_max_drawdown,
        calculate_sharpe_ratio,
        calculate_downside_deviation
    )
    
    portfolio_vol = calculate_volatility(portfolio.portfolio_returns)
    market_vol = calculate_volatility(portfolio.benchmark_returns)
    
    portfolio_dd = calculate_max_drawdown(portfolio.portfolio_returns)
    market_dd = calculate_max_drawdown(portfolio.benchmark_returns)
    
    portfolio_sharpe = calculate_sharpe_ratio(portfolio.portfolio_returns, risk_free_rate)
    market_sharpe = calculate_sharpe_ratio(portfolio.benchmark_returns, risk_free_rate)
    
    portfolio_downside = calculate_downside_deviation(portfolio.portfolio_returns)
    market_downside = calculate_downside_deviation(portfolio.benchmark_returns)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Volatility")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Portfolio', 'Market'],
            y=[portfolio_vol * 100, market_vol * 100],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{portfolio_vol:.2%}", f"{market_vol:.2%}"],
            textposition='auto'
        ))
        fig.update_layout(
            yaxis_title="Annual Volatility (%)",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sharpe Ratio")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Portfolio', 'Market'],
            y=[portfolio_sharpe, market_sharpe],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{portfolio_sharpe:.3f}", f"{market_sharpe:.3f}"],
            textposition='auto'
        ))
        fig.update_layout(
            yaxis_title="Sharpe Ratio",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("Downside Deviation")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Portfolio', 'Market'],
            y=[portfolio_downside * 100, market_downside * 100],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{portfolio_downside:.2%}", f"{market_downside:.2%}"],
            textposition='auto'
        ))
        fig.update_layout(
            yaxis_title="Downside Deviation (%)",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # =====================================================================
    # SECTION 4: PORTFOLIO STRUCTURE
    # =====================================================================
    st.header(" Portfolio Structure")
    
    from portfolio_metrics import (
        total_contribution_by_stock,
        identify_top_contributors,
        calculate_concentration,
        calculate_effective_n_stocks
    )
    
    contributions = total_contribution_by_stock(portfolio.stock_returns_df, portfolio.weights)
    top_bottom = identify_top_contributors(portfolio.stock_returns_df, portfolio.weights)
    concentration = calculate_concentration(portfolio.weights)
    effective_n = calculate_effective_n_stocks(portfolio.weights)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Weights")
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=portfolio.tickers,
            values=portfolio.weights,
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Weight: %{percent}<br>Value: %{value:.2%}<extra></extra>'
        )])
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Return Contribution")
        
        # Sort contributions
        contrib_sorted = contributions.sort_values(ascending=True)
        
        # Create bar chart
        colors = ['red' if x < 0 else 'green' for x in contrib_sorted.values]
        
        fig = go.Figure(data=[go.Bar(
            x=contrib_sorted.values * 100,
            y=contrib_sorted.index,
            orientation='h',
            marker_color=colors,
            text=[f"{x:.2%}" for x in contrib_sorted.values],
            textposition='auto'
        )])
        
        fig.update_layout(
            xaxis_title="Contribution (%)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top/Bottom contributors
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Top Contributor",
            top_bottom['top_contributor'],
            delta=f"{top_bottom['top_contributor_value']:.2%}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Top Dragger",
            top_bottom['top_dragger'],
            delta=f"{top_bottom['top_dragger_value']:.2%}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Max Concentration",
            f"{concentration:.1%}",
            help="Largest single position weight"
        )
    
    with col4:
        st.metric(
            "Effective N Stocks",
            f"{effective_n:.1f}",
            help="True diversification level"
        )
    
    st.markdown("---")
    
    # =====================================================================
    # SECTION 5: BEHAVIOUR CONSISTENCY
    # =====================================================================
    st.header(" Behaviour Consistency")
    
    from risk_metrics import (
        calculate_rolling_cagr,
        calculate_win_rate,
        calculate_avg_gain_loss
    )
    
    win_rate = calculate_win_rate(portfolio.portfolio_returns)
    gain_loss = calculate_avg_gain_loss(portfolio.portfolio_returns)
    benchmark_win_rate = calculate_win_rate(portfolio.benchmark_returns)
    benchmark_gain_loss = calculate_avg_gain_loss(portfolio.benchmark_returns)
    
    # Rolling CAGR chart
    n_days = len(portfolio.portfolio_returns)
    if n_days >= 252:
        st.subheader("Rolling 1-Year CAGR")
        
        rolling_cagr = calculate_rolling_cagr(portfolio.portfolio_returns)
        rolling_cagr_clean = rolling_cagr.dropna()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=rolling_cagr_clean.index,
            y=rolling_cagr_clean.values * 100,
            mode='lines',
            name='Rolling 1Y CAGR',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="CAGR (%)",
            hovermode='x unified',
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"ℹ️ Need at least 252 days for rolling CAGR (currently have {n_days} days)")
    
    # Win rate and gain/loss
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Win Rate")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Portfolio', 'Benchmark'],
            y=[win_rate * 100, benchmark_win_rate * 100],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{win_rate:.1%}", f"{benchmark_win_rate:.1%}"],
            textposition='auto'
        ))
        fig.update_layout(
            yaxis_title="Win Rate (%)",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Gain/Loss Ratio")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Portfolio', 'Benchmark'],
            y=[gain_loss['gain_loss_ratio'], benchmark_gain_loss['gain_loss_ratio']],
            marker_color=['#1f77b4', '#ff7f0e'],
            text=[f"{gain_loss['gain_loss_ratio']:.2f}x", f"{benchmark_gain_loss['gain_loss_ratio']:.2f}x"],
            textposition='auto'
        ))
        fig.update_layout(
            yaxis_title="Gain/Loss Ratio",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Details
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Avg Daily Gain", f"{gain_loss['avg_gain']:.2%}")
        st.metric("Avg Daily Loss", f"{gain_loss['avg_loss']:.2%}")
    
    with col2:
        st.metric("Benchmark Avg Gain", f"{benchmark_gain_loss['avg_gain']:.2%}")
        st.metric("Benchmark Avg Loss", f"{benchmark_gain_loss['avg_loss']:.2%}")
    
    st.markdown("---")
    
    # =====================================================================
    # EXPORT
    # =====================================================================
    st.header(" Export Results")
    
    # Prepare export data
    export_data = {
        "portfolio_composition": {
            "tickers": portfolio.tickers,
            "weights": portfolio.weights
        },
        "performance_metrics": {
            "annual_return": float(metrics['annual_return']),
            "volatility": float(metrics['volatility']),
            "sharpe_ratio": float(metrics['sharpe_ratio']),
            "sortino_ratio": float(metrics['sortino_ratio']),
            "max_drawdown": float(metrics['max_drawdown'])
        },
        "market_comparison": {
            "beta": float(beta),
            "information_ratio": float(ir),
            "tracking_error": float(te),
            "excess_return": float(ann_excess)
        },
        "risk_quality": {
            "portfolio_volatility": float(portfolio_vol),
            "market_volatility": float(market_vol),
            "portfolio_sharpe": float(portfolio_sharpe),
            "market_sharpe": float(market_sharpe),
            "portfolio_downside": float(portfolio_downside),
            "market_downside": float(market_downside)
        },
        "portfolio_structure": {
            "max_concentration": float(concentration),
            "effective_n_stocks": float(effective_n),
            "top_contributor": top_bottom['top_contributor'],
            "top_dragger": top_bottom['top_dragger']
        },
        "behaviour": {
            "win_rate": float(win_rate),
            "avg_gain": float(gain_loss['avg_gain']),
            "avg_loss": float(gain_loss['avg_loss']),
            "gain_loss_ratio": float(gain_loss['gain_loss_ratio'])
        }
    }
    
    json_str = json.dumps(export_data, indent=2)
    
    st.download_button(
        label="📥 Download Results as JSON",
        data=json_str,
        file_name="portfolio_analysis.json",
        mime="application/json",
        use_container_width=True
    )

else:
    # Welcome screen
    st.info("👈 Upload a portfolio CSV file and configure settings in the sidebar to get started.")
    
    st.markdown("""
    ### CSV File Format
    
    Your CSV file should have two columns:
    - **Ticker**: Stock ticker symbol (e.g., RELIANCE.NS for NSE stocks)
    - **Amount**: Investment amount in INR
    
    Example:
    ```
    Ticker,Amount
    RELIANCE.NS,10000
    TCS.NS,15000
    INFY.NS,12000
    ```
    
    ### What This Dashboard Provides
    
    1. **Performance Summary** - Key metrics at a glance
    2. **Market Comparison** - How you stack up against the benchmark
    3. **Risk Quality** - Risk-adjusted performance evaluation
    4. **Portfolio Structure** - Contribution and diversification analysis
    5. **Behaviour Consistency** - Win rate and consistency metrics
    
    Click **Run Analysis** after uploading your portfolio file!
    """)