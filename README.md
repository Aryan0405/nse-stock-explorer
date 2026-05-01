# NSE Stock Explorer 
Fetches 5 year OHLCV data using yfinance, computes and shows returns, rolling volatility, normalized price, drawdown, sharpe ratio, correlation. 
🔗 [Live Demo](https://nse-stock-explorer.streamlit.app/) 

## Metrics
* Log returns tells us about the returns.
* Rolling volatility tells us about how much standard deviation the stock has how much it varies in 21 days.
* Drawdown measures the decline from a historical peak at any point in time.
* Sharpe ratio tells us that is the profit worth the risk we are taking(higher Sharpe ratio- worth it & vice versa).
* Correlation talks about how strongly the stocks move together. Stocks shouldn't be highly correlated, decreases diversification and increases risk.

## Stock Selection 
Selected 1-2 stocks per sector for diversification.
Sectors are:
* RELIANCE: Energy/Conglomerate
* HDFCBANK: Banking
* INFY: IT
* TCS: IT
* MARUTI: Auto
* SUNPHARMA: Pharma
* BAJFINANCE: NBFC
* ASIANPAINT: Consumer
* ONGC: PSU Energy
* ADANIENT: Conglomerate 
## Key Finding
* Adani is a high risk stock according to me as it has shown extreme growth compared to NSEI and also it has shown extreme drawdowns too(70-80%). 
## Run Locally 
```bash git clone https://github.com/Aryan0405/nse-stock-explorer>  
cd nse-stock-explorer  
pip install -r requirements.txt  
streamlit run app/app.py
```