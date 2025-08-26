"""
Vectorized backtesting of a Mean Reversion trading strategy.
"""

import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class MeanReversionBacktest():
    """
    Vectorized backtesting of a Mean Reversion trading strategy.

    This class downloads historical price data for a given asset,
    computes a mean-reversion signal based on the deviation of the price 
    from its Simple Moving Average (SMA), and evaluates the strategy’s 
    performance against a buy-and-hold benchmark.

    Parameters
    ----------
    ticker : str
        Ticker symbol of the stock or asset to backtest.
    start : str
        Start date for historical data (format: 'YYYY-MM-DD').
    end : str
        End date for historical data (format: 'YYYY-MM-DD').
    length_sma : int
        Window length of the SMA used to compute the deviation signal.
    threshold : float
        Threshold value for normalized deviations to trigger 
        long/short trading signals.

    Attributes
    ----------
    data : pandas.DataFrame
        Price data and calculated indicators.
    results : pandas.DataFrame or None
        Results of the backtest after running `run_strategy`.
    """
    def __init__(self,
                 ticker: str,
                 start: str,
                 end: str,
                 length_sma: int,
                 threshold: int
                 ):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.length_sma = length_sma
        self.threshold = threshold
        self._get_data()
        self.results = None

    def _get_data(self):
        """
        Download price data and compute log returns.

        Data is fetched from Yahoo Finance and enhanced with:
        - Log returns
        """
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volume']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        self.data = df

    def plot_asset(self):
        """
        Plot asset price over time.

        Displays the historical closing price of the asset.
        """
        df = self.data.copy()
        plt.plot(df['close'], c='gray', label='Asset price')
        plt.legend()
        plt.title(self.ticker)
        plt.plot()

    def run_strategy(self):
        """
        Run the mean reversion trading strategy.

        A trading signal is generated based on the normalized deviation
        of the price from its SMA:
        
        - Long position: when normalized difference < `-threshold`
        - Short position: when normalized difference > `threshold`
        - Exit position: when the normalized difference crosses zero

        Returns
        -------
        tuple
            returns : float
                Total buy-and-hold return.
            strategy_returns : float
                Total mean reversion strategy return.
            max_drawdown : float
                Maximum drawdown of the strategy.
            max_drawdown_period : datetime.timedelta
                Longest continuous drawdown period.
        """
        df = self.data.copy()
        df['sma'] = df['close'].rolling(self.length_sma).mean()
        df['difference'] = df['close'] - df['sma']
        df['norm_diff'] = (df['difference'] - df['difference'].mean()) / df['difference'].std()
        df['position'] = np.where(df['norm_diff'] > self.threshold, -1, np.nan)
        df['position'] = np.where(df['norm_diff'] < -self.threshold, 1, df['position'])
        df['position'] = np.where(df['norm_diff'] * df['norm_diff'].shift(1) < 0, 0, df['position'])
        df['position'] = df['position'].ffill().fillna(0)
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
        """
        Plot backtest results.

        Displays:
        - Cumulative buy-and-hold returns
        - Cumulative mean reversion strategy returns
        - Maximum cumulative strategy returns (for drawdown visualization)
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
    mr_strat = MeanReversionBacktest('BTC-USD', start=start_backtest, end=end_backtest, length_sma=24, threshold=2)
    mr_strat.plot_asset()
    mr_strat.run_strategy()
    mr_strat.plot_results()
