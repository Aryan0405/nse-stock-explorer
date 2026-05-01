import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# Page Config
st.set_page_config(page_title="Stock Price Analysis", layout="wide")
st.title("Stock Price Analysis")

# Sidebar
stocks = st.sidebar.multiselect(
    "Select the stock(s) to analyze:",
    ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS",
     "MARUTI.NS", "SUNPHARMA.NS", "BAJFINANCE.NS",
     "ASIANPAINT.NS", "ONGC.NS", "ADANIENT.NS", "^NSEI"],
    default=["RELIANCE.NS", "HDFCBANK.NS"]
)

start_date, end_date = st.sidebar.date_input(
    "Select the date range for analysis:",
    [pd.to_datetime("2019-01-01"), pd.to_datetime("2024-12-31")]
)

if not stocks:
    st.warning("Please select at least one stock from the sidebar.")
    st.stop()

@st.cache_data
def load_data(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        threads=True
    )
    return data

# Ensure Benchmark is always included for calculations
tickers = list(set(stocks + ["^NSEI"]))
data = load_data(tuple(sorted(tickers)), start_date, end_date)

def computation(close):
    log_returns = np.log(close / close.shift(1)).dropna()
    rolling_volatility = log_returns.rolling(window=21).std() * np.sqrt(252)
    
    cumulative_returns = (1 + log_returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    
    daily_risk_free_rate = 0.07 / 252
    mean_return = log_returns.rolling(63).mean()
    std_of_return = log_returns.rolling(63).std()
    sharpe_ratio = ((mean_return - daily_risk_free_rate) / std_of_return) * np.sqrt(252)
    
    correlation_matrix = log_returns.corr()
    return log_returns, rolling_volatility, cumulative_returns, drawdown, sharpe_ratio, correlation_matrix

# Process Data
close = data["Close"].ffill()
log_returns, rolling_vol, cum_returns, drawdown, sharpe, corr = computation(close)

# Define Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Log Returns Dist",
    "Normalized Price",
    "Rolling Volatility",
    "Drawdown",
    "Sharpe Ratio",
    "Correlation"
])

benchmark = "^NSEI"
# Consistent list: Only plot individual stocks, excluding benchmark
plot_stocks = [s for s in stocks if s != benchmark]

# --- Tab 1: Log Returns Distribution ---
with tab1:
    st.subheader("Returns Distribution & Normality")
    for i in plot_stocks:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(log_returns[i], bins=50, density=True, color='steelblue', alpha=0.7, edgecolor='white', label=f"{i} Log Returns")
        ax.axvline(log_returns[i].mean(), color='orange', linestyle='--', label='Mean')
        ax.axvline(log_returns[i].median(), color='green', linestyle='--', label='Median')
        
        mu, std = log_returns[i].mean(), log_returns[i].std()
        x = np.linspace(log_returns[i].min(), log_returns[i].max(), 200)
        ax.plot(x, stats.norm.pdf(x, mu, std), 'k--', label="Normal Fit")
        
        ax.set_title(f"{i} Distribution (Kurtosis: {log_returns[i].kurt():.2f}, Skew: {log_returns[i].skew():.2f})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        st.pyplot(fig)
        plt.close(fig)

# --- Tab 2: Normalized Price (Growth) ---
with tab2:
    st.subheader("Price Growth (Base 100)")
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in plot_stocks:
        base100 = close[i] / close[i].dropna().iloc[0] * 100
        ax.plot(base100.index, base100.values, label=i)

    if benchmark in close.columns:
        nifty = close[benchmark] / close[benchmark].dropna().iloc[0] * 100
        ax.plot(nifty.index, nifty.values, color='black', linestyle="--", linewidth=2, label="NIFTY50")

    ax.set_ylabel("Normalized Price")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    st.pyplot(fig)
    plt.close(fig)

# --- Tab 3: Rolling Volatility ---
with tab3:
    st.subheader("21-Day Rolling Volatility (Annualized)")
    for i in plot_stocks:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(rolling_vol.index, rolling_vol[i], label=f"{i} Vol", color='#e67e22')
        ax.fill_between(rolling_vol[i].index, rolling_vol[i].values, color='#e67e22', alpha=0.2)
        ax.axhline(rolling_vol[i].mean(), color='red', linestyle='--', alpha=0.6, label='Mean Vol')
        ax.set_title(f"{i} Volatility")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        st.pyplot(fig)
        plt.close(fig)

# --- Tab 4: Drawdown ---
with tab4:
    st.subheader("Historical Drawdowns")
    for i in plot_stocks:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(drawdown.index, drawdown[i], color='#e74c3c')
        ax.fill_between(drawdown.index, drawdown[i], color='#e74c3c', alpha=0.4)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{i} Drawdown Profile")
        ax.set_axisbelow(True)  
        st.pyplot(fig)
        plt.close(fig)

# --- Tab 5: Sharpe Ratio ---
with tab5:
    st.subheader("Rolling 63-Day Sharpe Ratio")
    for i in plot_stocks:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(sharpe.index, sharpe[i], color='#2ecc71')
        ax.axhline(0, color='black', linewidth=1)
        ax.fill_between(sharpe.index, sharpe[i], where=(sharpe[i] > 0), color='#2ecc71', alpha=0.3)
        ax.set_title(f"{i} Sharpe Ratio")
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        st.pyplot(fig)
        plt.close(fig)

# --- Tab 6: Correlation ---
with tab6:
    st.subheader("Asset Correlation Matrix")
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", mask=mask, 
                vmin=-1, vmax=1, square=True, linewidths=0.5)
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    st.pyplot(fig)
    plt.close(fig)