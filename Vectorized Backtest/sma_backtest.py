"""
Vectorized backtesting of a Simple Moving Average (SMA) trading strategy.
"""

import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class SMAbacktest():
    """
    Vectorized backtesting of a Simple Moving Average (SMA) trading strategy.

    This class downloads historical price data for a given asset,
    computes technical indicators (SMA1, SMA2), and evaluates
    a crossover-based SMA trading strategy.

    Parameters
    ----------
    ticker : str
        Ticker symbol of the stock or asset to backtest.
    start : str
        Start date for historical data (format: 'YYYY-MM-DD').
    end : str
        End date for historical data (format: 'YYYY-MM-DD').
    sma1 : int
        Window length for the short-term Simple Moving Average.
    sma2 : int
        Window length for the long-term Simple Moving Average.

    Attributes
    ----------
    data : pandas.DataFrame
        Price data and calculated indicators.
    results : pandas.DataFrame or None
        Results of the backtest after running `strategy`.
    """
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
        self._get_data()
        self.results = None

    def _get_data(self):
        """
        Download price data and compute SMA indicators.

        Data is fetched from Yahoo Finance and enhanced with:
        - Log returns
        - Short-term SMA (`SMA1`)
        - Long-term SMA (`SMA2`)
        """
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volumne']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['SMA1'] = df['close'].rolling(self.sma1).mean()
        df['SMA2'] = df['close'].rolling(self.sma2).mean()
        self.data = df

    def plot_asset(self):
        """
        Plot asset price with SMA indicators.

        Plots the asset’s closing price alongside the short-term and
        long-term moving averages.
        """
        df = self.data.copy()
        plt.plot(df['close'], c='gray', label='Asset price')
        plt.plot(df['SMA1'], label='SMA1')
        plt.plot(df['SMA2'], c='blue', label='SMA2')
        plt.legend()
        plt.title(self.ticker)
        plt.plot()

    def run_strategy(self):
        """
        Run the SMA crossover trading strategy.

        A long position is taken when `SMA1 > SMA2`, and a short
        position otherwise. The strategy is evaluated against a
        buy-and-hold benchmark.

        Returns
        -------
        tuple
            returns : float
                Total buy-and-hold return.
            strategy_returns : float
                Total strategy return.
            max_drawdown : float
                Maximum drawdown of the strategy.
            max_drawdown_period : datetime.timedelta
                Longest continuous drawdown period.
        """
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
        """
        Plot backtest results.

        Displays:
        - Cumulative buy-and-hold returns
        - Cumulative strategy returns
        - Maximum strategy cumulative returns (for drawdown visualization)
        """
        results = self.results.copy()
        if self.results is None:
            print("No results to plot yet. Run a strategy.")
        plt.plot(results['sum_returns'], c='gray', label='Returns')
        plt.plot(results['sum_strategy'], c='black', label='Returns strategy')
        plt.plot(results['summax_strategy'], c='red', label='Max returns strategy')
        plt.legend()
        plt.title('Results')
        plt.show()

if __name__ == '__main__':
    start_backtest = '2020-01-01'
    end_backtest = '2025-05-01'
    sma_strat = SMAbacktest('BTC-USD', start=start_backtest, end=end_backtest, sma1=12, sma2=24)
    sma_strat.plot_asset()
    sma_strat.run_strategy()
    sma_strat.plot_results()
