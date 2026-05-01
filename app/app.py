import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Stock Price Analysis", layout="wide")
st.title("Stock Price Analysis")

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

tickers = list(set(stocks + ["^NSEI"]))

data = load_data(tuple(sorted(tickers)), start_date, end_date)

def computation(close):
    log_returns = np.log(close / close.shift(1)).dropna()
    rolling_volatility = log_returns.rolling(window=21).std() * np.sqrt(252)
    cumulative_returns=(1+log_returns).cumprod()
    rolling_max=cumulative_returns.cummax()
    drawdown=(cumulative_returns-rolling_max)/rolling_max
    daily_risk_free_rate = 0.07/252
    mean_return = log_returns.rolling(63).mean()
    std_of_return = log_returns.rolling(63).std()
    sharpe_ratio = ((mean_return - daily_risk_free_rate) / std_of_return )*np.sqrt(252)
    correlation_matrix = log_returns.corr()
    return log_returns, rolling_volatility, cumulative_returns, drawdown, sharpe_ratio, correlation_matrix

close = data["Close"].ffill()

log_returns, rolling_vol, cum_returns, drawdown, sharpe, corr = computation(close)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Normalized Price",
    "Rolling Volatility",
    "Drawdown",
    "Sharpe Ratio",
    "Correlation"
])

with tab1:
    fig, ax = plt.subplots(figsize=(12, 6))

    benchmark = "^NSEI"

    plot_stocks = [s for s in stocks if s != benchmark]

    for i in plot_stocks:
        base100 = close[i] / close[i].dropna().iloc[0] * 100
        ax.plot(base100.index, base100.values, label=i)

    if benchmark in close.columns:
        nifty = close[benchmark] / close[benchmark].dropna().iloc[0] * 100
        ax.plot(nifty.index, nifty.values, linestyle="--", linewidth=2, label="NIFTY50")

    ax.set_title("Growth vs NIFTY50 (Base = 100)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price")
    ax.grid(True)
    ax.legend(loc="upper left")

    st.pyplot(fig)

with tab2:
    for i in plot_stocks:
        fig,ax = plt.subplots(figsize=(12, 6))
        ax.plot(rolling_vol.index, rolling_vol[i], label=f"{i} Rolling Volatility")
        ax.set_title(f"{i} Rolling Volatility")
        ax.set_xlabel("Date")
        ax.set_ylabel("Volatility")
        ax.grid(True)
        ax.legend(loc="upper left")
        st.pyplot(fig)

with tab3:
    for i in plot_stocks:
        fig,ax = plt.subplots(figsize=(12, 6))
        ax.plot(drawdown.index, drawdown[i], label=f"{i} Drawdown")
        ax.set_title(f"{i} Drawdown")
        ax.set_xlabel("Date")
        ax.set_ylabel("Drawdown")
        ax.grid(True)
        ax.legend(loc="upper left")
        st.pyplot(fig)

with tab4:
    for i in plot_stocks:

        fig,ax = plt.subplots(figsize=(12, 6))
        ax.plot(sharpe.index, sharpe[i], label=f"{i} Sharpe Ratio")
        ax.set_title(f"{i} Sharpe Ratio")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sharpe Ratio")
        ax.grid(True)
        ax.legend(loc="upper left")
        st.pyplot(fig)

with tab5:
    fig, ax = plt.subplots(figsize=(10, 8))
    corr_matrix = log_returns.corr()
    mask=np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdYlGn", ax=ax, mask=mask,vmin=-1, vmax=1,square=True,
            linewidths=0.5, cbar_kws={"shrink": 0.8})
    ax.set_title("Correlation Heatmap of Log Returns",fontweight='bold')
    st.pyplot(fig)