import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class MomentumBacktest(object):
    '''
    Class for vectorized backtesting of Momentum trading strategy.

    Inputs ---
        ticker: ticker of the stock used
        start: start date for stock data, 
            format = 'yyyy-mm-dd'
        end: end date for stock data
            format = 'yyyy-mm-dd'
        lookback: number of returns we are taking into acount to compute the strategy signals

    functions ---
        get_data: get the data from yahoo finance and prepare the dataset with all the needed features
        
        plot_asset: plot the data of the asset and the two SMA
        
        strategy: run the backtest of the trading strategy, 
            return the returns, the strategy returns, the max drawdown and the longest drawdown period
        
        plot_resuts: plot the cumulative returns of the buy-and-hold, the cumulative returns of the strategy, 
            and the max cumulative returns of the strategy
    '''
    def __init__(self,
                 ticker: str,
                 start: str,
                 end: str,
                 lookback: int):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.lookback = lookback
        self.get_data()

    def get_data(self):
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volume']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        self.data = df

    def plot_asset(self):
        df = self.data.copy()
        fig, ax = plt.subplots(1, 1)
        ax.plot(df['close'], c='gray', label='Asset price')
        ax.legend()
        ax.set_title(self.ticker)
        plt.plot()

    def strategy(self):
        df = self.data.copy()
        df['position'] = np.sign(df['log_returns'].rolling(self.lookback).mean())
        df['strategy'] = df['position'].shift(1)*df['log_returns']
        df['sum_returns'] = df['log_returns'].cumsum().apply(np.exp)
        df['sum_strategy'] = df['strategy'].cumsum().apply(np.exp)

        # returns from buy-and-hold and returns from the strategy
        returns, strategy_returns = df[['log_returns', 'strategy']].sum().apply(np.exp)
        print(f"Returns: {returns}")
        print(f"Strategy returns: {strategy_returns}")

        # max drawdown and max period of drawndown of the strategy
        df['summax_strategy'] = df['sum_strategy'].cummax()
        drawdown = df['summax_strategy'] - df['sum_strategy']
        temp = drawdown[drawdown==0]
        period = (temp.index[1:].to_pydatetime() - temp.index[:-1].to_pydatetime())
        print(f"Max drawdown: {drawdown.max()}")
        print(f"Longuest period of drawdown: {period.max()}")
        
        self.results = df
        return returns, strategy_returns, drawdown.max(), period.max()
    
    def plot_results(self):
        '''
        Plot the strategy results.
        '''
        results = self.results.copy()
        if self.results is None:
            print("No results to plot yet. Run a strategy.")
        fig, ax = plt.subplots(1, 1)
        ax.plot(results['sum_returns'], c='gray', label='Returns')
        ax.plot(results['sum_strategy'], c='black', label='Returns strategy')
        ax.plot(results['summax_strategy'], c='red', label='Max returns strategy')
        ax.legend()
        ax.set_title('Results')
        plt.show()


if __name__ == '__main__':
    start = '2020-01-01'
    end = '2025-05-01'
    mom_strat = MomentumBacktest('BTC-USD', start=start, end=end, lookback=7)
    mom_strat.plot_asset()
    mom_strat.strategy()
    mom_strat.plot_results()