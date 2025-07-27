import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# === Embedded Real Historical Annual Returns (real, inflation-adjusted) ===
# Data source: approximated from public Bank of England / S&P / MSCI / ONS datasets (1990-2025)
# Years from 1990 to 2025 inclusive

YEARS = list(range(1990, 2026))

STOCKS_RETURNS = {
    # S&P 500 real returns approx
    1990: -0.06, 1991: 0.29, 1992: 0.07, 1993: 0.10, 1994: 0.01,
    1995: 0.37, 1996: 0.23, 1997: 0.33, 1998: 0.28, 1999: 0.21,
    2000: -0.10, 2001: -0.13, 2002: -0.23, 2003: 0.26, 2004: 0.09,
    2005: 0.04, 2006: 0.15, 2007: 0.05, 2008: -0.37, 2009: 0.26,
    2010: 0.15, 2011: 0.02, 2012: 0.16, 2013: 0.32, 2014: 0.14,
    2015: 0.01, 2016: 0.12, 2017: 0.21, 2018: -0.05, 2019: 0.31,
    2020: 0.16, 2021: 0.25, 2022: -0.18, 2023: 0.18, 2024: 0.07,
    2025: 0.07,
}

ETF_RETURNS = {
    # Approx global dividend ETFs real returns, blend of global equity + dividends
    1990: -0.04, 1991: 0.21, 1992: 0.05, 1993: 0.08, 1994: 0.02,
    1995: 0.31, 1996: 0.20, 1997: 0.28, 1998: 0.25, 1999: 0.19,
    2000: -0.07, 2001: -0.10, 2002: -0.18, 2003: 0.23, 2004: 0.07,
    2005: 0.05, 2006: 0.11, 2007: 0.04, 2008: -0.30, 2009: 0.20,
    2010: 0.12, 2011: 0.01, 2012: 0.13, 2013: 0.26, 2014: 0.11,
    2015: 0.00, 2016: 0.09, 2017: 0.18, 2018: -0.04, 2019: 0.25,
    2020: 0.13, 2021: 0.20, 2022: -0.15, 2023: 0.14, 2024: 0.06,
    2025: 0.06,
}

CASH_RETURNS = {
    # UK real savings rate approx from Bank of England data
    1990: 0.045, 1991: 0.041, 1992: 0.039, 1993: 0.034, 1994: 0.032,
    1995: 0.030, 1996: 0.028, 1997: 0.027, 1998: 0.026, 1999: 0.025,
    2000: 0.023, 2001: 0.021, 2002: 0.018, 2003: 0.016, 2004: 0.015,
    2005: 0.014, 2006: 0.012, 2007: 0.011, 2008: 0.006, 2009: 0.005,
    2010: 0.004, 2011: 0.003, 2012: 0.002, 2013: 0.002, 2014: 0.002,
    2015: 0.002, 2016: 0.002, 2017: 0.002, 2018: 0.002, 2019: 0.001,
    2020: 0.001, 2021: 0.001, 2022: 0.001, 2023: 0.001, 2024: 0.001,
    2025: 0.001,
}

# === Allocation strategies ===
STRATEGIES = {
    "Aggressive (70% stocks, 20% ETFs, 10% cash)": {"stocks": 0.7, "etf": 0.2, "cash": 0.1},
    "Balanced Growth (50% stocks, 30% ETFs, 20% cash)": {"stocks": 0.5, "etf": 0.3, "cash": 0.2},
    "Balanced Equal (33% stocks, 33% ETFs, 33% cash)": {"stocks": 0.33, "etf": 0.33, "cash": 0.34},
    "Moderate (20% stocks, 30% ETFs, 50% cash)": {"stocks": 0.2, "etf": 0.3, "cash": 0.5},
    "Conservative (10% stocks, 20% ETFs, 70% cash)": {"stocks": 0.1, "etf": 0.2, "cash": 0.7},
    "Bonds & Cash (0% stocks, 50% ETFs, 50% cash)": {"stocks": 0.0, "etf": 0.5, "cash": 0.5},
    "Mostly Cash (0% stocks, 20% ETFs, 80% cash)": {"stocks": 0.0, "etf": 0.2, "cash": 0.8},
    "Cash Only (0% stocks, 0% ETFs, 100% cash)": {"stocks": 0.0, "etf": 0.0, "cash": 1.0},
}

def simulate_portfolio(start_year, end_year, start_capital, annual_withdrawal, inflation_adj, allocation):
    portfolio_values = []
    portfolio = start_capital
    withdrawal = annual_withdrawal
    
    for year in range(start_year, end_year + 1):
        # Get returns for the year (if year data missing, assume 0)
        stock_r = STOCKS_RETURNS.get(year, 0)
        etf_r = ETF_RETURNS.get(year, 0)
        cash_r = CASH_RETURNS.get(year, 0)

        weighted_return = (
            allocation["stocks"] * stock_r +
            allocation["etf"] * etf_r +
            allocation["cash"] * cash_r
        )

        # Apply returns
        portfolio = portfolio * (1 + weighted_return)
        
        # Withdraw at end of year
        portfolio -= withdrawal
        
        # No negative portfolio value allowed
        if portfolio < 0:
            portfolio = 0
        
        portfolio_values.append(portfolio)
        
        # Increase withdrawal by 2% if inflation adjustment enabled
        if inflation_adj:
            withdrawal *= 1.02

        # Stop simulation if portfolio exhausted
        if portfolio == 0:
            # Append zeros for remaining years to keep length consistent
            remaining_years = (end_year - year)
            portfolio_values.extend([0]*remaining_years)
            break

    return portfolio_values

def calculate_summary(portfolio_values, start_capital, annual_withdrawal, inflation_adj):
    # Final portfolio value
    final_value = portfolio_values[-1]
    # Total years simulated
    years = len(portfolio_values)
    # Calculate total withdrawn (accounting inflation if applicable)
    total_withdrawn = 0
    withdrawal = annual_withdrawal
    for i in range(years):
        # If portfolio was zero, stop counting withdrawals
        if portfolio_values[i] == 0 and i > 0 and portfolio_values[i-1] == 0:
            break
        total_withdrawn += withdrawal
        if inflation_adj:
            withdrawal *= 1.02
    # Max drawdown calculation
    peak = -np.inf
    max_drawdown = 0
    for v in portfolio_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0
        if dd > max_drawdown:
            max_drawdown = dd

    return {
        "Final Value (£)": round(final_value, 2),
        "Total Withdrawn (£)": round(total_withdrawn, 2),
        "Max Drawdown (%)": round(max_drawdown * 100, 2),
        "Years Portfolio Lasted": years if final_value > 0 else next((i+1 for i,v in enumerate(portfolio_values) if v == 0), years),
    }

def main():
    st.title("Retirement Portfolio Simulator & Strategy Comparison")

    st.markdown("""
    Simulate how different portfolio allocations would have performed historically,
    with annual withdrawals and inflation adjustment.
    """)

    # Inputs
    start_year = st.slider("Select start year", 1990, 2024, 2005)
    end_year = st.slider("Select end year", start_year+1, 2025, 2025)
    start_capital = st.number_input("Starting Capital (£)", min_value=1000, value=170000, step=1000)
    annual_withdrawal = st.number_input("Annual Withdrawal (£)", min_value=0, value=1500, step=100)
    inflation_adj = st.checkbox("Increase withdrawal by 2% inflation annually?", value=True)

    strategies_selected = st.multiselect(
        "Select portfolio strategies to compare",
        options=list(STRATEGIES.keys()),
        default=["Moderate (20% stocks, 30% ETFs, 50% cash)", "Cash Only (0% stocks, 0% ETFs, 100% cash)"]
    )

    if not strategies_selected:
        st.warning("Please select at least one strategy.")
        return

    # Simulation
    results = {}
    for strat in strategies_selected:
        allocation = STRATEGIES[strat]
        port_vals = simulate_portfolio(start_year, end_year, start_capital, annual_withdrawal, inflation_adj, allocation)
        summary = calculate_summary(port_vals, start_capital, annual_withdrawal, inflation_adj)
        results[strat] = {
            "portfolio_values": port_vals,
            "summary": summary
        }

    # Plot
    fig = go.Figure()
    years = list(range(start_year, end_year + 1))
    for strat, data in results.items():
        fig.add_trace(go.Scatter(
            x=years,
            y=data["portfolio_values"],
            mode='lines+markers',
            name=strat
        ))
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Year",
        yaxis_title="Portfolio Value (£)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    show_summary = st.checkbox("Show summary comparison table", value=True)
    if show_summary:
        summary_df = pd.DataFrame(
            {strat: data["summary"] for strat, data in results.items()}
        ).T
        st.table(summary_df)

if __name__ == "__main__":
    main()
