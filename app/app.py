import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import timedelta

import charts

st.set_page_config(page_title="Stock Price Analysis", layout="wide")
st.title("Stock Price Analysis")

BENCHMARK = "^NSEI"

# Sidebar
stocks = st.sidebar.multiselect(
    "Select the stock(s) to analyze:",
    ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS",
     "MARUTI.NS", "SUNPHARMA.NS", "BAJFINANCE.NS",
     "ASIANPAINT.NS", "ONGC.NS", "ADANIENT.NS", "^NSEI"],
    default=["RELIANCE.NS", "HDFCBANK.NS"],
)

date_range = st.sidebar.date_input(
    "Select the date range for analysis:",
    [pd.to_datetime("2019-01-01"), pd.to_datetime("2024-12-31")],
    min_value=pd.to_datetime("2019-01-01"),
    max_value=pd.to_datetime("2024-12-31"),
)

if not stocks:
    st.warning("Please select at least one stock from the sidebar.")
    st.stop()

# date_input returns a 1-tuple while the user is still picking the end date
if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
    st.info("Select both a start and an end date.")
    st.stop()
start_date, end_date = date_range


@st.cache_data(ttl=3600, show_spinner="Downloading prices...")
def load_data(tickers, start, end):
    # yfinance treats `end` as exclusive, so add a day to include it
    return yf.download(list(tickers), start=start, end=end + timedelta(days=1),
                       auto_adjust=True, progress=False)


def computation(close):
    log_returns = np.log(close / close.shift(1)).dropna(how="all")
    rolling_volatility = log_returns.rolling(window=21).std() * np.sqrt(252)

    # Log returns add up, they do not compound as (1 + r)
    cumulative = np.exp(log_returns.cumsum())
    drawdown = (cumulative - cumulative.cummax()) / cumulative.cummax()

    rf = 0.07 / 252
    sharpe = ((log_returns.rolling(63).mean() - rf) / log_returns.rolling(63).std()) * np.sqrt(252)
    return log_returns, rolling_volatility, drawdown, sharpe, log_returns.corr()


tickers = sorted(set(stocks + [BENCHMARK]))
data = load_data(tuple(tickers), start_date, end_date)

if data is None or data.empty:
    st.error("No price data came back from Yahoo Finance. Try again in a minute.")
    st.stop()

close = data["Close"].ffill()
if isinstance(close, pd.Series):
    close = close.to_frame(name=tickers[0])

valid_cols = close.columns[close.notna().any()]
dropped = [t for t in tickers if t not in valid_cols]
if dropped:
    st.warning(f"No data fetched for: {', '.join(dropped)}. Excluded from analysis.")
close = close[valid_cols]

log_returns, rolling_vol, drawdown, sharpe, corr = computation(close)
plot_stocks = [s for s in stocks if s != BENCHMARK and s in close.columns]

if not plot_stocks:
    st.info("Select at least one stock other than the benchmark (^NSEI).")
    st.stop()

tabs = st.tabs(["Log Returns Dist", "Normalized Price", "Rolling Volatility",
                "Drawdown", "Sharpe Ratio", "Correlation"])


def show(fig):
    st.plotly_chart(fig, width="stretch", theme=None)


with tabs[0]:
    st.subheader("Returns Distribution & Normality")
    for s in plot_stocks:
        show(charts.returns_distribution(log_returns[s], s))

with tabs[1]:
    st.subheader("Price Growth (Base 100)")
    show(charts.normalized_price(close, plot_stocks, BENCHMARK))

with tabs[2]:
    st.subheader("21-Day Rolling Volatility (Annualized)")
    for s in plot_stocks:
        show(charts.rolling_volatility(rolling_vol[s], s))

with tabs[3]:
    st.subheader("Historical Drawdowns")
    for s in plot_stocks:
        show(charts.drawdown_chart(drawdown[s], s))

with tabs[4]:
    st.subheader("Rolling 63-Day Sharpe Ratio")
    for s in plot_stocks:
        show(charts.sharpe_chart(sharpe[s], s))

with tabs[5]:
    st.subheader("Asset Correlation Matrix")
    if corr.shape[0] < 2:
        st.info("Select at least two assets to see correlations.")
    else:
        show(charts.correlation_heatmap(corr))
