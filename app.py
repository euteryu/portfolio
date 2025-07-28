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
    "🚀 Aggressive Growth": {"stocks": 0.70, "bonds": 0.05, "etf": 0.20, "reits": 0.05, "cash": 0.00},
    "📈 Growth": {"stocks": 0.60, "bonds": 0.15, "etf": 0.15, "reits": 0.05, "cash": 0.05},
    
    # Balanced approaches  
    "⚖️ Balanced Growth": {"stocks": 0.50, "bonds": 0.20, "etf": 0.15, "reits": 0.05, "cash": 0.10},
    "🎯 Target Date 2040": {"stocks": 0.45, "bonds": 0.25, "etf": 0.15, "reits": 0.05, "cash": 0.10},
    "🌍 Global Diversified": {"stocks": 0.35, "bonds": 0.25, "etf": 0.20, "reits": 0.05, "cash": 0.15},
    
    # Conservative approaches (much higher cash allocations)
    "🛡️ Conservative": {"stocks": 0.20, "bonds": 0.30, "etf": 0.15, "reits": 0.05, "cash": 0.30},
    "🏦 Income Focus": {"stocks": 0.15, "bonds": 0.35, "etf": 0.10, "reits": 0.05, "cash": 0.35},
    "💤 Capital Preservation": {"stocks": 0.10, "bonds": 0.30, "etf": 0.10, "reits": 0.00, "cash": 0.50},
    
    # Cash-heavy strategies
    "🏠 Real Estate Heavy": {"stocks": 0.25, "bonds": 0.20, "etf": 0.10, "reits": 0.25, "cash": 0.20},
    "💸 Cash Heavy": {"stocks": 0.05, "bonds": 0.15, "etf": 0.05, "reits": 0.05, "cash": 0.70},
    "💰 Cash Only": {"stocks": 0.00, "bonds": 0.00, "etf": 0.00, "reits": 0.00, "cash": 1.00},
}

# Quick scenario presets with detailed descriptions
SCENARIO_PRESETS = {
    "Conservative Retiree (안전한 은퇴자)": {
        "start_capital": 200000,
        "annual_withdrawal": 8000,
        "strategies": ["🛡️ Conservative", "💰 Cash Only"],
        "description": "Lower risk, steady income - ideal for risk-averse retirees | 낮은 위험, 안정적 수입 - 위험 회피 은퇴자에게 이상적"
    },
    "Moderate Growth (중간 성장)": {
        "start_capital": 150000,
        "annual_withdrawal": 6000,
        "strategies": ["⚖️ Balanced Growth", "🎯 Target Date 2040"],
        "description": "Balanced risk/reward - good for long-term growth | 균형잡힌 위험/수익 - 장기 성장에 적합"
    },
    "Aggressive Growth (적극적 성장)": {
        "start_capital": 100000,
        "annual_withdrawal": 4000,
        "strategies": ["🚀 Aggressive Growth", "📈 Growth"],
        "description": "Higher risk, higher potential returns - for growth-focused investors | 높은 위험, 높은 잠재 수익 - 성장 중심 투자자용"
    }
}

# Korean translations
TRANSLATIONS = {
    "en": {
        "title": "💰 Retirement Portfolio Simulator",
        "subtitle": "Compare investment strategies with real historical data",
        "simulation_settings": "📊 Simulation Settings",
        "quick_start": "Quick Start",
        "preset_help": "Pre-configured scenarios for common retirement situations",
        "time_period": "📅 Time Period",
        "starting_year": "Starting year",
        "ending_year": "Ending year",
        "starting_year_help": "When you start withdrawing from your portfolio",
        "ending_year_help": "When your retirement period ends",
        "money_settings": "💷 Money Settings",
        "starting_money": "Starting money (£)",
        "yearly_withdrawal": "Yearly withdrawal (£)",
        "starting_money_help": "How much you have saved when you start retirement",
        "yearly_withdrawal_help": "How much you plan to withdraw each year",
        "inflation_adj": "Adjust for inflation (2% yearly)",
        "inflation_help": "If checked, your withdrawal amount increases by 2% each year to maintain purchasing power",
        "investment_strategies": "🎯 Investment Strategies",
        "select_strategies": "Select strategies to compare:",
        "strategies_help": "Choose different investment approaches to compare",
        "advanced_options": "🔧 Advanced Options",
        "market_crash": "Simulate market crash",
        "crash_year": "Crash year (relative to start)",
        "crash_severity": "Crash severity",
        "crash_help": "-0.3 means a 30% market crash",
        "starting_capital": "Starting Capital",
        "annual_withdrawal": "Annual Withdrawal",
        "time_period_metric": "Time Period",
        "inflation_adjusted": "Inflation Adjusted",
        "strategy_comparison": "📋 Strategy Comparison",
        "key_insights": "🔍 Key Insights",
        "portfolio_allocations": "📊 View Portfolio Allocations",
        "understanding_results": "📚 Understanding the Results",
        "warning_select": "⚠️ Please select at least one investment strategy from the sidebar.",
        "years_text": "years",
        "outperformed": "outperformed",
        "by": "by",
        "more": "more",
        "preserved_capital": "preserved capital while",
        "depleted": "was completely depleted"
    },
    "kr": {
        "title": "💰 은퇴 포트폴리오 시뮬레이터",
        "subtitle": "실제 역사적 데이터로 투자 전략 비교",
        "simulation_settings": "📊 시뮬레이션 설정",
        "quick_start": "빠른 시작",
        "preset_help": "일반적인 은퇴 상황을 위한 사전 구성된 시나리오",
        "time_period": "📅 기간 설정",
        "starting_year": "시작 연도",
        "ending_year": "종료 연도",
        "starting_year_help": "포트폴리오에서 인출을 시작하는 시점",
        "ending_year_help": "은퇴 기간이 끝나는 시점",
        "money_settings": "💷 자금 설정",
        "starting_money": "시작 자금 (£)",
        "yearly_withdrawal": "연간 인출액 (£)",
        "starting_money_help": "은퇴 시작 시 보유한 저축액",
        "yearly_withdrawal_help": "매년 인출할 계획인 금액",
        "inflation_adj": "인플레이션 조정 (연 2%)",
        "inflation_help": "체크하면 구매력 유지를 위해 인출액이 매년 2%씩 증가합니다",
        "investment_strategies": "🎯 투자 전략",
        "select_strategies": "비교할 전략 선택:",
        "strategies_help": "비교할 다양한 투자 접근법을 선택하세요",
        "advanced_options": "🔧 고급 옵션",
        "market_crash": "시장 폭락 시뮬레이션",
        "crash_year": "폭락 연도 (시작 기준)",
        "crash_severity": "폭락 정도",
        "crash_help": "-0.3은 30% 시장 폭락을 의미합니다",
        "starting_capital": "시작 자본",
        "annual_withdrawal": "연간 인출액",
        "time_period_metric": "기간",
        "inflation_adjusted": "인플레이션 조정",
        "strategy_comparison": "📋 전략 비교",
        "key_insights": "🔍 주요 인사이트",
        "portfolio_allocations": "📊 포트폴리오 배분 보기",
        "understanding_results": "📚 결과 이해하기",
        "warning_select": "⚠️ 사이드바에서 최소 하나의 투자 전략을 선택해주세요.",
        "years_text": "년",
        "outperformed": "이(가)",
        "by": "보다",
        "more": "더 나은 성과",
        "preserved_capital": "자본을 보존한 반면",
        "depleted": "완전히 고갈되었습니다"
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
    """Create an enhanced comparison chart with better colors"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Portfolio Value Over Time', 'Annual Returns Comparison'),
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    # Use distinct, non-light colors that are easily visible
    colors = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange  
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf',  # Cyan
        '#aec7e8',  # Light Blue
        '#ffbb78'   # Light Orange
    ]
    
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
                marker=dict(size=5, color=color),
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
        hovermode="x unified",
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(title_text="Year", row=2, col=1, gridcolor='lightgray')
    fig.update_yaxes(title_text="Portfolio Value (£)", row=1, col=1, gridcolor='lightgray')
    fig.update_yaxes(title_text="Annual Return (%)", row=2, col=1, gridcolor='lightgray')
    
    return fig

def create_allocation_table(strategies_selected, lang="en"):
    """Create a clean allocation table without any highlighting or formatting issues"""
    if not strategies_selected:
        return None
    
    # Headers based on language
    if lang == "kr":
        headers = ["ID", "전략명", "주식", "채권", "ETF", "부동산", "현금"]
    else:
        headers = ["ID", "Strategy Name", "Stocks", "Bonds", "ETFs", "REITs", "Cash"]
    
    table_data = []
    for i, strategy in enumerate(strategies_selected, 1):
        allocation = PRESET_STRATEGIES[strategy]
        # Clean strategy name (remove emoji)
        clean_name = strategy.split(' ', 1)[1] if ' ' in strategy else strategy
        if lang == "kr" and '(' in clean_name and ')' in clean_name:
            # Extract Korean name from parentheses
            korean_part = clean_name[clean_name.find('(')+1:clean_name.find(')')]
            clean_name = korean_part if korean_part else clean_name
        elif lang == "en" and '(' in clean_name:
            # Remove Korean part for English
            clean_name = clean_name.split('(')[0].strip()
            
        table_data.append([
            chr(65 + i - 1),  # A, B, C, etc.
            clean_name,
            f"{allocation['stocks']*100:.0f}%",
            f"{allocation['bonds']*100:.0f}%",
            f"{allocation['etf']*100:.0f}%",
            f"{allocation['reits']*100:.0f}%",
            f"{allocation['cash']*100:.0f}%"
        ])
    
    # Create DataFrame
    df = pd.DataFrame(table_data, columns=headers)
    return df

def main():
    # Language toggle
    col1, col2 = st.columns([4, 1])
    with col2:
        lang = st.selectbox("언어/Language", ["English", "한국어"], index=0)
        lang_code = "kr" if lang == "한국어" else "en"
    
    # Get translations
    t = TRANSLATIONS[lang_code]
    
    with col1:
        st.title(t["title"])
        st.markdown(f"### {t['subtitle']}")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header(t["simulation_settings"])
        
        # Quick scenario selector
        st.subheader(t["quick_start"])
        
        preset_options = ["Custom"] + list(SCENARIO_PRESETS.keys())
        selected_preset = st.selectbox(
            f"Choose a starting scenario:",
            preset_options,
            help="These presets just set starting capital, withdrawal amount, and suggest 2 strategies to compare. You can still change everything below."
        )
        
        # Show preset description
        if selected_preset != "Custom":
            preset = SCENARIO_PRESETS[selected_preset]
            st.info(f"💡 {preset['description']}")
            st.write(f"**Sets:** £{preset['start_capital']:,} starting capital, £{preset['annual_withdrawal']:,} yearly withdrawal")
            default_capital = preset["start_capital"]
            default_withdrawal = preset["annual_withdrawal"]
            default_strategies = preset["strategies"]
        else:
            default_capital = 170000
            default_withdrawal = 1500
            default_strategies = ["⚖️ Balanced Growth", "💰 Cash Only"]
        
        st.divider()
        
        # Time period
        st.subheader(t["time_period"])
        start_year = st.slider(
            t["starting_year"],
            1990, 2024, 2005,
            help=t["starting_year_help"]
        )
        end_year = st.slider(
            t["ending_year"],
            start_year + 1, 2025, 2025,
            help=t["ending_year_help"]
        )
        
        # Financial inputs
        st.subheader(t["money_settings"])
        start_capital = st.number_input(
            t["starting_money"],
            min_value=1000,
            value=default_capital,
            step=5000,
            help=t["starting_money_help"]
        )
        
        annual_withdrawal = st.number_input(
            t["yearly_withdrawal"],
            min_value=0,
            value=default_withdrawal,
            step=250,
            help=t["yearly_withdrawal_help"]
        )
        
        inflation_adj = st.checkbox(
            t["inflation_adj"],
            value=True,
            help=t["inflation_help"]
        )
        
        # Strategy selection
        st.subheader(t["investment_strategies"])
        strategies_selected = st.multiselect(
            t["select_strategies"],
            options=list(PRESET_STRATEGIES.keys()),
            default=default_strategies,
            help=t["strategies_help"]
        )
        
        # Advanced options
        with st.expander(t["advanced_options"]):
            simulate_shock = st.checkbox(t["market_crash"], value=False)
            if simulate_shock:
                shock_year = st.slider(t["crash_year"], 1, min(10, end_year - start_year), 1)
                shock_severity = st.slider(t["crash_severity"], -0.5, -0.1, -0.3, 0.05,
                                         help=t["crash_help"])
    
    # Main content area
    if not strategies_selected:
        st.warning(t["warning_select"])
        st.stop()
    
    # Show selected parameters summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t["starting_capital"], f"£{start_capital:,}")
    with col2:
        st.metric(t["annual_withdrawal"], f"£{annual_withdrawal:,}")
    with col3:
        st.metric(t["time_period_metric"], f"{end_year - start_year + 1} {t['years_text']}")
    with col4:
        inflation_text = "Yes" if inflation_adj else "No"
        if lang_code == "kr":
            inflation_text = "예" if inflation_adj else "아니오"
        st.metric(t["inflation_adjusted"], inflation_text)
    
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
    st.subheader(t["strategy_comparison"])
    
    # Create comparison table
    summary_data = {}
    for strat, data in results.items():
        summary_data[strat] = data["summary"]
        # Add health indicator
        final_val = data["portfolio_values"][-1]
        summary_data[strat]["Health"] = get_portfolio_health_color(final_val, start_capital)
    
    summary_df = pd.DataFrame(summary_data).T
    st.dataframe(summary_df, use_container_width=True)
    
    # Compact allocation table  
    st.subheader(t["portfolio_allocations"])
    allocation_df = create_allocation_table(strategies_selected, lang_code)
    if allocation_df is not None:
        # Show clean table without any styling issues
        st.dataframe(
            allocation_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                col: st.column_config.TextColumn(width="medium") 
                for col in allocation_df.columns
            }
        )
        
        st.caption("💡 The allocation percentages above determine how your portfolio performs. Each strategy spreads your money differently across asset types.")
    
    # Educational sections
    if lang_code == "kr":
        with st.expander("📚 자산 클래스란 무엇인가? (투자 기초 지식)"):
            st.markdown("""
            ### 🏛️ **주식 (Stocks)**
            - **정의**: 회사의 소유권 일부를 나타내는 증권
            - **수익원**: 주가 상승 + 배당금
            - **위험도**: 높음 (시장 변동성에 크게 영향받음)
            - **예시**: 삼성전자, 애플, 구글 등 개별 기업 주식
            - **장기 수익률**: 역사적으로 연평균 7-10% (인플레이션 조정 후)
            
            ### 🏦 **채권 (Bonds)**
            - **정의**: 정부나 기업에 돈을 빌려주고 이자를 받는 증권
            - **수익원**: 고정 이자 지급 + 만기 시 원금 회수
            - **위험도**: 낮음~중간 (정부채 < 회사채)
            - **예시**: 한국 국채, 기업 회사채
            - **역할**: 포트폴리오 안정성 제공, 주식 하락 시 방어막
            
            ### 📈 **ETF (상장지수펀드)**
            - **정의**: 여러 주식/채권을 묶어서 거래소에서 거래하는 펀드
            - **장점**: 한 번에 수백 개 기업에 분산투자 가능
            - **수수료**: 일반 펀드보다 저렴 (연 0.1-0.8%)
            - **예시**: KODEX 200 (한국 대형주 200개), S&P 500 ETF
            - **특징**: 실시간 거래 가능, 투명한 구성
            
            ### 🏠 **부동산 투자신탁 (REITs)**
            - **정의**: 부동산에 투자하는 회사의 주식
            - **수익원**: 임대료 수입 + 부동산 가치 상승
            - **장점**: 적은 돈으로 대형 빌딩/쇼핑몰에 간접 투자
            - **배당**: 일반적으로 높은 배당 수익률 (4-8%)
            - **예시**: 오피스 빌딩, 쇼핑센터, 물류창고 투자 리츠
            
            ### 💰 **현금 (Cash)**
            - **정의**: 은행 예금, 적금, 단기 금융상품
            - **장점**: 100% 안전, 언제든 사용 가능
            - **단점**: 인플레이션에 구매력 감소
            - **현실**: 한국 예금 금리 2-3% vs 물가상승률 3-4%
            - **역할**: 비상자금, 단기 지출 대비용
            """)
            
        with st.expander("🎯 투자 전략 이해하기"):
            st.markdown("""
            ### 전략별 특징:
            
            **🚀 공격적 성장 (70% 주식)**
            - 젊은 나이 (20-30대)에 적합
            - 10-20년 장기투자 가능한 사람
            - 단기 손실 감수 가능한 성격
            
            **⚖️ 균형 성장 (50% 주식)**
            - 중년층 (40-50대)에 적합  
            - 성장과 안정성 모두 원하는 경우
            - 가장 일반적인 추천 전략
            
            **🛡️ 보수적 (20% 주식, 30% 현금)**
            - 은퇴 직전/후 (60대 이상)
            - 원금 손실을 절대 피하고 싶은 경우
            - 하지만 인플레이션 위험은 있음
            
            **💰 현금만 (100% 현금)**
            - 시장 위험은 0%
            - 하지만 구매력은 매년 2-3% 감소
            - 장기적으로는 가장 위험한 전략!
            """)
    else:
        with st.expander("📚 What Are Asset Classes? (Investment Basics)"):
            st.markdown("""
            ### 🏛️ **Stocks (Equities)**
            - **Definition**: Shares representing ownership in a company
            - **Returns**: Capital appreciation + dividends
            - **Risk**: High (subject to market volatility)
            - **Examples**: Individual company shares like Apple, Microsoft, Samsung
            - **Historical Returns**: ~7-10% annually (inflation-adjusted) over long term
            
            ### 🏦 **Bonds (Fixed Income)**
            - **Definition**: Loans to governments or corporations in exchange for interest
            - **Returns**: Fixed interest payments + principal repayment at maturity
            - **Risk**: Low to moderate (government bonds < corporate bonds)
            - **Examples**: UK Government Gilts, Corporate bonds
            - **Role**: Portfolio stability, defensive asset during stock market declines
            
            ### 📈 **ETFs (Exchange-Traded Funds)**
            - **Definition**: Funds that hold many stocks/bonds and trade on exchanges
            - **Advantage**: Instant diversification across hundreds of companies
            - **Fees**: Lower than mutual funds (typically 0.1-0.8% annually)
            - **Examples**: S&P 500 ETF, Total Stock Market ETF
            - **Features**: Real-time trading, transparent holdings
            
            ### 🏠 **REITs (Real Estate Investment Trusts)**
            - **Definition**: Companies that own income-generating real estate
            - **Returns**: Rental income + property value appreciation
            - **Advantage**: Access to commercial real estate with small amounts
            - **Dividends**: Typically high yield (4-8% annually)
            - **Examples**: Office buildings, shopping centers, warehouses
            
            ### 💰 **Cash (Cash Equivalents)**
            - **Definition**: Bank deposits, savings accounts, short-term instruments
            - **Advantage**: 100% safe, immediately available
            - **Disadvantage**: Loses purchasing power to inflation
            - **Reality**: UK savings rates 2-3% vs inflation 3-4% = negative real return
            - **Purpose**: Emergency fund, short-term expenses
            """)
            
        with st.expander("🎯 Understanding Investment Strategies"):
            st.markdown("""
            ### Strategy Characteristics:
            
            **🚀 Aggressive Growth (70% stocks)**
            - Suitable for young investors (20s-30s)
            - Can invest for 10-20+ years
            - Comfortable with short-term losses
            
            **⚖️ Balanced Growth (50% stocks)**
            - Good for middle-aged investors (40s-50s)
            - Want both growth and stability
            - Most commonly recommended strategy
            
            **🛡️ Conservative (20% stocks, 30% cash)**
            - Pre/post retirement (60+ years old)
            - Cannot afford major losses
            - But still exposed to inflation risk
            
            **💰 Cash Only (100% cash)**
            - Zero market risk
            - But purchasing power declines 2-3% annually
            - Ironically the riskiest long-term strategy!
            """)
    
    # Additional useful sections
    if lang_code == "kr":
        with st.expander("⚠️ 투자 시 주의사항 및 팁"):
            st.markdown("""
            ### 🎯 **성공적인 투자를 위한 원칙:**
            
            **1. 분산투자가 핵심**
            - 한 바구니에 모든 달걀을 담지 마세요
            - 여러 자산 클래스에 나누어 투자
            - 지역적 분산 (한국 + 해외)
            
            **2. 시간이 가장 강력한 무기**
            - 복리 효과: 돈이 돈을 벌어주는 효과
            - 10년 vs 20년 투자 시 결과는 2배가 아닌 4배 차이
            - 일찍 시작할수록 유리
            
            **3. 감정적 투자 금지**
            - 주식이 오를 때 더 사고 싶고
            - 떨어질 때 팔고 싶은 것이 인간 심리
            - 하지만 이는 손실로 이어짐
            
            **4. 정기적 투자 (달러 비용 평균화)**
            - 매월 일정 금액씩 투자
            - 시장 타이밍을 예측할 필요 없음
            - 장기적으로 평균 매입가 안정화
            
            ### ⚠️ **피해야 할 실수들:**
            - 단기 수익률에 집착
            - 남의 투자 성공담만 듣고 따라하기
            - 투자 목적 없이 무작정 시작
            - 비상자금 없이 전액 투자
            - 이해하지 못하는 상품에 투자
            """)
    else:
        with st.expander("⚠️ Investment Guidelines & Tips"):
            st.markdown("""
            ### 🎯 **Principles for Successful Investing:**
            
            **1. Diversification is Key**
            - Don't put all eggs in one basket
            - Spread across different asset classes
            - Geographic diversification (domestic + international)
            
            **2. Time is Your Most Powerful Tool**
            - Compound interest: money making money
            - 10 years vs 20 years isn't 2x difference, it's 4x+
            - Starting early gives massive advantages
            
            **3. Avoid Emotional Investing**
            - Human nature: buy high (when excited), sell low (when scared)
            - This leads to poor returns
            - Stick to your strategy through ups and downs
            
            **4. Regular Investing (Dollar-Cost Averaging)**
            - Invest fixed amounts regularly (monthly)
            - No need to time the market
            - Smooths out average purchase prices over time
            
            ### ⚠️ **Common Mistakes to Avoid:**
            - Focusing on short-term performance
            - Following others' success stories blindly
            - Investing without clear goals
            - Investing emergency funds
            - Buying investments you don't understand
            """)
    
    # Key insights
    st.subheader(t["key_insights"])
    
    if len(results) >= 2:
        # Compare best vs worst performer
        final_values = {k: v["portfolio_values"][-1] for k, v in results.items()}
        best_strategy = max(final_values, key=final_values.get)
        worst_strategy = min(final_values, key=final_values.get)
        
        best_value = final_values[best_strategy]
        worst_value = final_values[worst_strategy]
        
        if worst_value > 0:
            improvement = ((best_value - worst_value) / worst_value) * 100
            st.success(f"💡 **{best_strategy}** {t['outperformed']} **{worst_strategy}** {t['by']} **{improvement:.0f}%** ({best_value - worst_value:,.0f} {t['more']})")
        else:
            st.success(f"💡 **{best_strategy}** {t['preserved_capital']} **{worst_strategy}** {t['depleted']}")
    
    # Educational content
    with st.expander(t["understanding_results"]):
        if lang_code == "kr":
            st.markdown("""
            **주요 지표 설명:**
            - **최종 가치**: 기간 말 남은 자금
            - **총 인출액**: 모든 연간 인출액의 합계 (인플레이션 조정 포함)
            - **최대 낙폭**: 기간 중 최대 고점에서 저점까지의 하락폭
            - **변동성**: 연간 수익률 변동 정도 (높을수록 변동성이 큼)
            - **지속 기간**: 포트폴리오가 인출을 제공한 기간
            - **성공률**: 전체 기간 동안 포트폴리오가 유지되었는지 여부
            
            **자산 클래스:**
            - **주식**: 기업 주식 (높은 위험, 높은 잠재 수익)
            - **채권**: 정부/기업 부채 (낮은 위험, 안정적 수입)
            - **ETF**: 분산투자 펀드 (중간 위험)
            - **부동산**: 부동산 투자 신탁 (부동산 노출)
            - **현금**: 저축 계좌 (최저 위험, 최저 수익)
            """)
        else:
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