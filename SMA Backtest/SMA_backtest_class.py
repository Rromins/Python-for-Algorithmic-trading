import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class SMAbacktest(object):
    '''
    Class for vectorized backtesting of SMA trading strategy.

    Inputs ---
        ticker: ticker of the stock used
        start: start date for stock data, 
            format = 'yyyy-mm-dd'
        end: end date for stock data
            format = 'yyyy-mm-dd'
        sma1: length of the shorter sma
        sma2: length of the longest sma

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
                 sma1: int, 
                 sma2: int):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.sma1 = sma1
        self.sma2 = sma2
        self.get_data()
        self.results = None

    def get_data(self):
        '''
        Get the data with yahoo finance api, and calculate the needed features. 
        '''
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volumne']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['SMA1'] = df['close'].rolling(self.sma1).mean()
        df['SMA2'] = df['close'].rolling(self.sma2).mean()
        self.data = df

    def plot_asset(self):
        df = self.data.copy()
        fig, ax = plt.subplots(1, 1)
        ax.plot(df['close'], c='gray', label='Asset price')
        ax.plot(df['SMA1'], label='SMA1')
        ax.plot(df['SMA2'], c='blue', label='SMA2')
        ax.legend()
        ax.set_title(self.ticker)
        plt.plot()

    def strategy(self):
        '''
        Run the trading strategy.
        '''
        df = self.data.copy()
        df['position'] = np.where(df['SMA1'] > df['SMA2'], 1, -1)
        df['strategy_logret'] = df['position'].shift(1)*df['log_returns']
        df['sum_returns'] = df['log_returns'].cumsum().apply(np.exp)
        df['sum_strategy'] = df['strategy_logret'].cumsum().apply(np.exp)
        
        # returns from buy-and-hold and returns from the strategy
        returns, strategy_returns = df[['log_returns', 'strategy_logret']].sum().apply(np.exp)
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
    sma_strat = SMAbacktest('BTC-USD', start=start, end=end, sma1=12, sma2=24)
    sma_strat.plot_asset()
    sma_strat.strategy()
    sma_strat.plot_results()