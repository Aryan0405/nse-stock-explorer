# NSE Stock Explorer

**Business question:** Among 10 major NSE-listed stocks spanning different sectors, which offer the best risk-adjusted returns over a 5-year horizon (2019–2024), and which carry tail risk that a long-term investor should know about before allocating capital?

🔗 **[Live demo](https://nse-stock-explorer.streamlit.app/)**

## What it does

An interactive Streamlit dashboard that pulls 5 years of daily OHLCV data (Jan 2019 – Dec 2024, 1,480 trading days) for 10 NSE blue-chip stocks across different sectors, benchmarked against the NIFTY50 (`^NSEI`). Users select any combination of stocks and a custom date range from the sidebar, and the app generates six views:

1. **Log Returns Distribution** - histogram with normal-distribution overlay, plus kurtosis and skewness
2. **Normalized Price (Growth)** - base-100 growth vs. NIFTY50
3. **Rolling Volatility** - 21-day annualized volatility
4. **Drawdown** - peak-to-trough decline over time
5. **Sharpe Ratio** - rolling 63-day risk-adjusted return (assumes a 7% annualized risk-free rate)
6. **Correlation** - correlation matrix of daily log returns across the selected stocks

## Data & Cleaning

- Source: Yahoo Finance via `yfinance`, daily adjusted close prices
- Tickers with more than 5% missing data were dropped; remaining gaps were forward-filled
- `^NSEI` had 1 residual null after forward-fill, removed via a final `dropna()`
- Final dataset: 1,480 trading days × 11 tickers (10 stocks + NIFTY50 benchmark)

## Stock Selection

Selected 1–2 stocks per sector for sector diversification:

| Ticker | Sector |
|---|---|
| RELIANCE | Energy / Conglomerate |
| HDFCBANK | Banking |
| INFY | IT |
| TCS | IT |
| MARUTI | Auto |
| SUNPHARMA | Pharma |
| BAJFINANCE | NBFC |
| ASIANPAINT | Consumer |
| ONGC | PSU Energy |
| ADANIENT | Conglomerate |

## Metrics Explained

- **Log returns** - day-over-day percentage change in price, expressed in log form so returns are additive across time.
- **Rolling volatility (21-day)** - annualized standard deviation of returns over the trailing 21 trading days. Higher = larger day-to-day price swings.
- **Drawdown** - percentage decline from a stock's most recent peak. A -40% drawdown means the stock has lost 40% of its value from its prior high.
- **Sharpe ratio (rolling 63-day)** - excess return over the risk-free rate (assumed 7% annualized), divided by volatility, annualized. Higher = better return per unit of risk taken; a sustained negative Sharpe ratio means the stock underperformed a risk-free asset on a risk-adjusted basis over that window.
- **Correlation** - how closely two stocks' daily returns move together. Lower correlation between holdings improves diversification.
- **Kurtosis / Skewness** - kurtosis measures how often extreme returns (large gains *and* large losses) occur relative to a normal distribution. Skewness measures whether those extremes lean negative (crash-prone) or positive (rally-prone).

## Key Findings

* **ADANIENT.NS carried by far the most tail risk in the basket.** Over 2019–2024, its daily log returns exhibited a kurtosis of **20.29** and a skewness of **-1.14**, the most extreme values among all 10 stocks (the next-highest kurtosis was BAJFINANCE at **14.06**). High kurtosis indicates that extreme price movements occurred far more frequently than a normal distribution would predict, while the strongly negative skew suggests those extremes were disproportionately downside events. This behavior was reflected in the stock's severe drawdowns during the period.

* **Despite being the strongest absolute performer, ADANIENT demanded an unusually high risk tolerance.** The stock generated roughly **15× cumulative growth** over the analysis period, substantially outperforming both the broader market and every other stock in the basket. However, it also experienced a maximum drawdown of approximately **-77%** during the 2023 Hindenburg-related selloff, exceeding even its COVID-era drawdown (~-55%). Notably, the stock remained significantly below its prior peak by the end of 2024, illustrating how exceptional long-term returns can coexist with extreme interim losses.

* **SUNPHARMA emerged as the strongest risk-adjusted investment candidate.** While ADANIENT delivered the highest absolute return, SUNPHARMA combined strong cumulative performance with lower volatility, shallower drawdowns, and more stable risk-adjusted returns throughout the period. For a long-term investor focused on consistency rather than maximizing upside, SUNPHARMA offered a more attractive return-to-risk profile.

* **Diversification benefits varied substantially across sectors.** HDFCBANK exhibited one of the strongest relationships with broader market movements, making it a useful proxy for overall market exposure. In contrast, SUNPHARMA displayed weaker correlations with much of the basket, providing diversification benefits that could reduce portfolio risk when combined with more market-sensitive holdings.


## Run Locally

```bash
git clone https://github.com/Aryan0405/nse-stock-explorer.git
cd nse-stock-explorer
pip install -r requirements.txt
streamlit run app/app.py
```

## Limitations

- Risk-free rate is a fixed 7% annualized assumption, not a time-varying 10-year G-Sec yield
- Returns exclude transaction costs, taxes, and dividends
- Analysis is limited to this 10-ticker basket, not the broader NSE universe - findings shouldn't be generalized beyond these names
