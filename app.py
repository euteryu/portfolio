import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math

# Configure page
st.set_page_config(
    page_title="Retirement Portfolio Simulator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Enhanced Historical Returns with More Asset Classes ===
YEARS = list(range(1990, 2026))

# Real returns (inflation-adjusted)
STOCKS_RETURNS = {
    1990: -0.06, 1991: 0.29, 1992: 0.07, 1993: 0.10, 1994: 0.01,
    1995: 0.37, 1996: 0.23, 1997: 0.33, 1998: 0.28, 1999: 0.21,
    2000: -0.10, 2001: -0.13, 2002: -0.23, 2003: 0.26, 2004: 0.09,
    2005: 0.04, 2006: 0.15, 2007: 0.05, 2008: -0.37, 2009: 0.26,
    2010: 0.15, 2011: 0.02, 2012: 0.16, 2013: 0.32, 2014: 0.14,
    2015: 0.01, 2016: 0.12, 2017: 0.21, 2018: -0.05, 2019: 0.31,
    2020: 0.16, 2021: 0.25, 2022: -0.18, 2023: 0.18, 2024: 0.07,
    2025: 0.07,
}

BONDS_RETURNS = {
    # UK Government/Corporate bond returns (real)
    1990: 0.035, 1991: 0.041, 1992: 0.038, 1993: 0.042, 1994: -0.015,
    1995: 0.065, 1996: 0.032, 1997: 0.045, 1998: 0.055, 1999: -0.018,
    2000: 0.048, 2001: 0.025, 2002: 0.078, 2003: 0.022, 2004: 0.035,
    2005: 0.028, 2006: 0.015, 2007: 0.038, 2008: 0.125, 2009: 0.055,
    2010: 0.065, 2011: 0.145, 2012: 0.025, 2013: -0.035, 2014: 0.165,
    2015: 0.008, 2016: 0.095, 2017: 0.018, 2018: 0.002, 2019: 0.065,
    2020: 0.055, 2021: -0.045, 2022: -0.145, 2023: 0.015, 2024: 0.025,
    2025: 0.025,
}

ETF_RETURNS = {
    # Global dividend ETFs real returns
    1990: -0.04, 1991: 0.21, 1992: 0.05, 1993: 0.08, 1994: 0.02,
    1995: 0.31, 1996: 0.20, 1997: 0.28, 1998: 0.25, 1999: 0.19,
    2000: -0.07, 2001: -0.10, 2002: -0.18, 2003: 0.23, 2004: 0.07,
    2005: 0.05, 2006: 0.11, 2007: 0.04, 2008: -0.30, 2009: 0.20,
    2010: 0.12, 2011: 0.01, 2012: 0.13, 2013: 0.26, 2014: 0.11,
    2015: 0.00, 2016: 0.09, 2017: 0.18, 2018: -0.04, 2019: 0.25,
    2020: 0.13, 2021: 0.20, 2022: -0.15, 2023: 0.14, 2024: 0.06,
    2025: 0.06,
}

REITS_RETURNS = {
    # Real Estate Investment Trusts (approximated)
    1990: 0.02, 1991: 0.15, 1992: 0.08, 1993: 0.12, 1994: 0.04,
    1995: 0.18, 1996: 0.22, 1997: 0.14, 1998: -0.05, 1999: 0.08,
    2000: 0.25, 2001: 0.18, 2002: 0.06, 2003: 0.35, 2004: 0.28,
    2005: 0.12, 2006: 0.35, 2007: -0.18, 2008: -0.38, 2009: 0.28,
    2010: 0.28, 2011: 0.08, 2012: 0.19, 2013: 0.02, 2014: 0.29,
    2015: 0.02, 2016: 0.08, 2017: 0.05, 2018: -0.04, 2019: 0.23,
    2020: -0.08, 2021: 0.41, 2022: -0.24, 2023: 0.11, 2024: 0.08,
    2025: 0.08,
}

CASH_RETURNS = {
    # UK real savings rate
    1990: 0.045, 1991: 0.041, 1992: 0.039, 1993: 0.034, 1994: 0.032,
    1995: 0.030, 1996: 0.028, 1997: 0.027, 1998: 0.026, 1999: 0.025,
    2000: 0.023, 2001: 0.021, 2002: 0.018, 2003: 0.016, 2004: 0.015,
    2005: 0.014, 2006: 0.012, 2007: 0.011, 2008: 0.006, 2009: 0.005,
    2010: 0.004, 2011: 0.003, 2012: 0.002, 2013: 0.002, 2014: 0.002,
    2015: 0.002, 2016: 0.002, 2017: 0.002, 2018: 0.002, 2019: 0.001,
    2020: 0.001, 2021: 0.001, 2022: 0.001, 2023: 0.001, 2024: 0.001,
    2025: 0.001,
}

# === Enhanced Portfolio Strategies ===
PRESET_STRATEGIES = {
    # Growth-oriented
    "🚀 Aggressive Growth": {"stocks": 0.80, "bonds": 0.05, "etf": 0.10, "reits": 0.05, "cash": 0.00},
    "📈 Growth": {"stocks": 0.70, "bonds": 0.10, "etf": 0.15, "reits": 0.05, "cash": 0.00},
    
    # Balanced approaches
    "⚖️ Balanced Growth": {"stocks": 0.50, "bonds": 0.20, "etf": 0.20, "reits": 0.05, "cash": 0.05},
    "🎯 Target Date 2040": {"stocks": 0.54, "bonds": 0.36, "etf": 0.06, "reits": 0.04, "cash": 0.00},
    "🌍 Global Diversified": {"stocks": 0.40, "bonds": 0.25, "etf": 0.25, "reits": 0.10, "cash": 0.00},
    
    # Conservative approaches
    "🛡️ Conservative": {"stocks": 0.30, "bonds": 0.40, "etf": 0.15, "reits": 0.05, "cash": 0.10},
    "🏦 Income Focus": {"stocks": 0.20, "bonds": 0.50, "etf": 0.20, "reits": 0.10, "cash": 0.00},
    "💤 Capital Preservation": {"stocks": 0.15, "bonds": 0.60, "etf": 0.10, "reits": 0.05, "cash": 0.10},
    
    # Specialty strategies
    "🏠 Real Estate Heavy": {"stocks": 0.30, "bonds": 0.20, "etf": 0.15, "reits": 0.30, "cash": 0.05},
    "💸 Cash Heavy": {"stocks": 0.10, "bonds": 0.20, "etf": 0.10, "reits": 0.05, "cash": 0.55},
    "💰 Cash Only": {"stocks": 0.00, "bonds": 0.00, "etf": 0.00, "reits": 0.00, "cash": 1.00},
}

# Quick scenario presets
SCENARIO_PRESETS = {
    "Conservative Retiree": {
        "start_capital": 200000,
        "annual_withdrawal": 8000,
        "strategies": ["🛡️ Conservative", "💰 Cash Only"]
    },
    "Moderate Growth": {
        "start_capital": 150000,
        "annual_withdrawal": 6000,
        "strategies": ["⚖️ Balanced Growth", "🎯 Target Date 2040"]
    },
    "Aggressive Growth": {
        "start_capital": 100000,
        "annual_withdrawal": 4000,
        "strategies": ["🚀 Aggressive Growth", "📈 Growth"]
    }
}

def simulate_portfolio(start_year, end_year, start_capital, annual_withdrawal, inflation_adj, allocation, market_shock=None):
    """Enhanced simulation with market shock capability"""
    portfolio_values = []
    annual_returns = []
    portfolio = start_capital
    withdrawal = annual_withdrawal
    
    for i, year in enumerate(range(start_year, end_year + 1)):
        # Get returns for the year
        stock_r = STOCKS_RETURNS.get(year, 0)
        bond_r = BONDS_RETURNS.get(year, 0)
        etf_r = ETF_RETURNS.get(year, 0)
        reit_r = REITS_RETURNS.get(year, 0)
        cash_r = CASH_RETURNS.get(year, 0)
        
        # Apply market shock if specified
        if market_shock and i == market_shock["year_index"]:
            shock_multiplier = 1 + market_shock["severity"]
            stock_r *= shock_multiplier
            bond_r *= shock_multiplier * 0.5  # Bonds less affected
            etf_r *= shock_multiplier
            reit_r *= shock_multiplier * 0.8  # REITs moderately affected
            # Cash unaffected by market shocks

        weighted_return = (
            allocation["stocks"] * stock_r +
            allocation["bonds"] * bond_r +
            allocation["etf"] * etf_r +
            allocation["reits"] * reit_r +
            allocation["cash"] * cash_r
        )
        
        annual_returns.append(weighted_return)
        
        # Apply returns
        portfolio = portfolio * (1 + weighted_return)
        
        # Withdraw at end of year
        portfolio -= withdrawal
        
        # No negative portfolio value allowed
        if portfolio < 0:
            portfolio = 0
        
        portfolio_values.append(portfolio)
        
        # Increase withdrawal by inflation if enabled
        if inflation_adj:
            withdrawal *= 1.02

        # Stop simulation if portfolio exhausted
        if portfolio == 0:
            remaining_years = (end_year - year)
            portfolio_values.extend([0] * remaining_years)
            annual_returns.extend([0] * remaining_years)
            break

    return portfolio_values, annual_returns

def calculate_advanced_summary(portfolio_values, annual_returns, start_capital, annual_withdrawal, inflation_adj):
    """Calculate comprehensive portfolio statistics"""
    final_value = portfolio_values[-1]
    years = len(portfolio_values)
    
    # Calculate total withdrawn
    total_withdrawn = 0
    withdrawal = annual_withdrawal
    for i in range(years):
        if portfolio_values[i] == 0 and i > 0 and portfolio_values[i-1] == 0:
            break
        total_withdrawn += withdrawal
        if inflation_adj:
            withdrawal *= 1.02
    
    # Max drawdown
    peak = -np.inf
    max_drawdown = 0
    for v in portfolio_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0
        if dd > max_drawdown:
            max_drawdown = dd
    
    # Volatility (standard deviation of returns)
    volatility = np.std(annual_returns) if annual_returns else 0
    
    # Years portfolio lasted
    years_lasted = years if final_value > 0 else next((i+1 for i,v in enumerate(portfolio_values) if v == 0), years)
    
    # Success probability (simplified: did portfolio survive?)
    success_rate = 1.0 if final_value > 0 else 0.0
    
    return {
        "Final Value (£)": f"£{final_value:,.0f}",
        "Total Withdrawn (£)": f"£{total_withdrawn:,.0f}",
        "Max Drawdown": f"{max_drawdown * 100:.1f}%",
        "Volatility": f"{volatility * 100:.1f}%",
        "Years Lasted": f"{years_lasted}/{years}",
        "Success Rate": f"{success_rate * 100:.0f}%"
    }

def get_portfolio_health_color(final_value, start_capital):
    """Return color based on portfolio performance"""
    if final_value > start_capital * 1.5:
        return "🟢 Excellent"
    elif final_value > start_capital:
        return "🟡 Good"
    elif final_value > start_capital * 0.5:
        return "🟠 Moderate"
    else:
        return "🔴 Poor"

def create_comparison_chart(results, years):
    """Create an enhanced comparison chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Portfolio Value Over Time', 'Annual Returns Comparison'),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    colors = px.colors.qualitative.Set3
    
    for i, (strat, data) in enumerate(results.items()):
        color = colors[i % len(colors)]
        
        # Portfolio values
        fig.add_trace(
            go.Scatter(
                x=years,
                y=data["portfolio_values"],
                mode='lines+markers',
                name=strat,
                line=dict(color=color, width=3),
                marker=dict(size=4),
                hovertemplate=f'<b>{strat}</b><br>Year: %{{x}}<br>Value: £%{{y:,.0f}}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Annual returns
        fig.add_trace(
            go.Scatter(
                x=years,
                y=[r * 100 for r in data["annual_returns"]],
                mode='lines',
                name=f'{strat} Returns',
                line=dict(color=color, width=2, dash='dot'),
                showlegend=False,
                hovertemplate=f'<b>{strat}</b><br>Year: %{{x}}<br>Return: %{{y:.1f}}%<extra></extra>'
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=800,
        title_text="Portfolio Performance Analysis",
        hovermode="x unified"
    )
    
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Portfolio Value (£)", row=1, col=1)
    fig.update_yaxes(title_text="Annual Return (%)", row=2, col=1)
    
    return fig

def main():
    st.title("💰 Retirement Portfolio Simulator")
    st.markdown("### Compare investment strategies with real historical data")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📊 Simulation Settings")
        
        # Quick scenario selector
        st.subheader("Quick Start")
        selected_preset = st.selectbox(
            "Choose a preset scenario:",
            ["Custom"] + list(SCENARIO_PRESETS.keys()),
            help="Pre-configured scenarios for common retirement situations"
        )
        
        if selected_preset != "Custom":
            preset = SCENARIO_PRESETS[selected_preset]
            default_capital = preset["start_capital"]
            default_withdrawal = preset["annual_withdrawal"]
            default_strategies = preset["strategies"]
        else:
            default_capital = 170000
            default_withdrawal = 1500
            default_strategies = ["⚖️ Balanced Growth", "💰 Cash Only"]
        
        st.divider()
        
        # Time period
        st.subheader("📅 Time Period")
        start_year = st.slider(
            "Starting year",
            1990, 2024, 2005,
            help="When you start withdrawing from your portfolio"
        )
        end_year = st.slider(
            "Ending year",
            start_year + 1, 2025, 2025,
            help="When your retirement period ends"
        )
        
        # Financial inputs
        st.subheader("💷 Money Settings")
        start_capital = st.number_input(
            "Starting money (£)",
            min_value=1000,
            value=default_capital,
            step=5000,
            help="How much you have saved when you start retirement"
        )
        
        annual_withdrawal = st.number_input(
            "Yearly withdrawal (£)",
            min_value=0,
            value=default_withdrawal,
            step=250,
            help="How much you plan to withdraw each year"
        )
        
        inflation_adj = st.checkbox(
            "Adjust for inflation (2% yearly)",
            value=True,
            help="If checked, your withdrawal amount increases by 2% each year to maintain purchasing power"
        )
        
        # Strategy selection
        st.subheader("🎯 Investment Strategies")
        strategies_selected = st.multiselect(
            "Select strategies to compare:",
            options=list(PRESET_STRATEGIES.keys()),
            default=default_strategies,
            help="Choose different investment approaches to compare"
        )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            simulate_shock = st.checkbox("Simulate market crash", value=False)
            if simulate_shock:
                shock_year = st.slider("Crash year (relative to start)", 1, min(10, end_year - start_year), 1)
                shock_severity = st.slider("Crash severity", -0.5, -0.1, -0.3, 0.05,
                                         help="-0.3 means a 30% market crash")
    
    # Main content area
    if not strategies_selected:
        st.warning("⚠️ Please select at least one investment strategy from the sidebar.")
        st.stop()
    
    # Show selected parameters summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Starting Capital", f"£{start_capital:,}")
    with col2:
        st.metric("Annual Withdrawal", f"£{annual_withdrawal:,}")
    with col3:
        st.metric("Time Period", f"{end_year - start_year + 1} years")
    with col4:
        inflation_text = "Yes" if inflation_adj else "No"
        st.metric("Inflation Adjusted", inflation_text)
    
    # Run simulations
    results = {}
    years = list(range(start_year, end_year + 1))
    
    market_shock = None
    if simulate_shock:
        market_shock = {"year_index": shock_year - 1, "severity": shock_severity}
    
    for strat in strategies_selected:
        allocation = PRESET_STRATEGIES[strat]
        port_vals, returns = simulate_portfolio(
            start_year, end_year, start_capital, annual_withdrawal, 
            inflation_adj, allocation, market_shock
        )
        summary = calculate_advanced_summary(
            port_vals, returns, start_capital, annual_withdrawal, inflation_adj
        )
        results[strat] = {
            "portfolio_values": port_vals,
            "annual_returns": returns,
            "summary": summary,
            "allocation": allocation
        }
    
    # Create and display chart
    fig = create_comparison_chart(results, years)
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary comparison
    st.subheader("📋 Strategy Comparison")
    
    # Create comparison table
    summary_data = {}
    for strat, data in results.items():
        summary_data[strat] = data["summary"]
        # Add health indicator
        final_val = data["portfolio_values"][-1]
        summary_data[strat]["Health"] = get_portfolio_health_color(final_val, start_capital)
    
    summary_df = pd.DataFrame(summary_data).T
    st.dataframe(summary_df, use_container_width=True)
    
    # Key insights
    st.subheader("🔍 Key Insights")
    
    if len(results) >= 2:
        # Compare best vs worst performer
        final_values = {k: v["portfolio_values"][-1] for k, v in results.items()}
        best_strategy = max(final_values, key=final_values.get)
        worst_strategy = min(final_values, key=final_values.get)
        
        best_value = final_values[best_strategy]
        worst_value = final_values[worst_strategy]
        
        if worst_value > 0:
            improvement = ((best_value - worst_value) / worst_value) * 100
            st.success(f"💡 **{best_strategy}** outperformed **{worst_strategy}** by **{improvement:.0f}%** ({best_value - worst_value:,.0f} more)")
        else:
            st.success(f"💡 **{best_strategy}** preserved capital while **{worst_strategy}** was completely depleted")
    
    # Portfolio allocation details
    with st.expander("📊 View Portfolio Allocations"):
        for strat, data in results.items():
            st.write(f"**{strat}:**")
            allocation = data["allocation"]
            cols = st.columns(len(allocation))
            for i, (asset, weight) in enumerate(allocation.items()):
                if weight > 0:
                    cols[i % len(cols)].metric(asset.title(), f"{weight*100:.0f}%")
            st.divider()
    
    # Educational content
    with st.expander("📚 Understanding the Results"):
        st.markdown("""
        **Key Metrics Explained:**
        - **Final Value**: How much money is left at the end of the period
        - **Total Withdrawn**: Sum of all yearly withdrawals (adjusted for inflation if enabled)
        - **Max Drawdown**: Largest peak-to-trough decline during the period
        - **Volatility**: How much the returns varied year-to-year (higher = more volatile)
        - **Years Lasted**: How long the portfolio provided withdrawals before depletion
        - **Success Rate**: Whether the portfolio survived the entire period (simplified metric)
        
        **Asset Classes:**
        - **Stocks**: Company shares (higher risk, higher potential returns)
        - **Bonds**: Government/corporate debt (lower risk, steady income)
        - **ETFs**: Diversified investment funds (moderate risk)
        - **REITs**: Real estate investment trusts (property exposure)
        - **Cash**: Savings accounts (lowest risk, lowest returns)
        """)

if __name__ == "__main__":
    main()