import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from SMA_backtest_class import SMAbacktest

tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD']
start = '2022-01-01'
end = '2025-05-01'
sma1 = 12
sma2 = 24
strat_returns = pd.DataFrame()
for ticker in tickers:
    smab = SMAbacktest(ticker=ticker, start=start, end=end, sma1=sma1, sma2=sma2)
    smab.strategy()
    strat_returns[f'ret_{ticker}'] = smab.results['sum_strategy']

fig, ax = plt.subplots(1, 1)
for column in strat_returns.columns:
    ax.plot(strat_returns.index, strat_returns[column], label=column, alpha=0.8)
ax.legend()
ax.grid()
plt.show()