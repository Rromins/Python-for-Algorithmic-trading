"""
Backtesting framework for long-only trading strategies.
"""

from backtest_base import BacktestBase
import matplotlib.pyplot as plt
plt.style.use('seaborn')

class LongOnlyBacktest(BacktestBase):
    """
    Backtesting framework for long-only trading strategies.

    This class inherits from `BacktestBase`. 

    Parameters
    ----------
    ticker : str
        The asset ticker symbol (e.g., 'AAPL').
    start : str
        Start date for historical data (format: 'YYYY-MM-DD').
    end : str
        End date for historical data (format: 'YYYY-MM-DD').
    amount : float
        Initial cash amount for the backtest.
    ftc : float, optional, default=0.0
        Fixed transaction cost per trade.
    ptc : float, optional, default=0.0
        Proportional transaction cost (percentage of trade volume).
    verbose : bool, optional, default=True
        If True, print trade and performance details.

    Attributes
    ----------
    initial_amount : float
        The starting cash balance.
    amount : float
        Current cash balance.
    units : float
        Number of units currently held (long position).
    position : int
        Position indicator (not yet used in base class).
    trades : int
        Number of executed trades.
    data : pandas.DataFrame
        Historical price data with log returns.
    """
    def run_mean_reversion_strategy(self, sma, threshold):
        '''
        Run a mean reversion backtest with long-only positions.

        The trading signal is based on the deviation of the close price
        from its Simple Moving Average (SMA). The normalized difference
        is used to identify entry and exit points:
        
        - **Buy signal**: when the normalized difference < `-threshold`
        - **Sell signal**: when the normalized difference ≥ 0

        Parameters
        ----------
        sma : int
            Window length of the Simple Moving Average (SMA) used to
            compute the mean reversion signal.
        threshold : float
            Threshold value for the normalized difference to trigger
            trading signals. Higher values make the strategy more
            conservative.
        '''
        msg  = "\n\nRunning mean reversion strategy | "
        msg += f"Length SMA={sma} & thr={threshold}"
        msg += f"\nfixed costs {self.ftc} | "
        msg += f"proportional costs {self.ptc}"
        print(msg)
        print("-"*55)
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount

        self.data['SMA'] = self.data['close'].rolling(sma).mean()
        self.data['difference'] = self.data['close'] - self.data['SMA']
        self.data['norm_diff'] = ((self.data['difference'] - self.data['difference'].mean())
                                  / self.data['difference'].std())

        for candle in range(sma, len(self.data)):
            if self.position == 0:
                if self.data['norm_diff'].iloc[candle] < -threshold:
                    self._place_buy_order(candle, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if self.data['norm_diff'].iloc[candle] >= 0.0:
                    self._place_sell_order(candle, units=self.units)
                    self.position = 0
        self._close_out(candle)

if __name__ == '__main__':
    start = '2020-01-01'
    end = '2025-05-01'
    longOnly_MeanReversion_strat = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000)
    longOnly_MeanReversion_strat.run_mean_reversion_strategy(sma=24, threshold=2)

    print("\n")
    print("Same but with 4USD fixed transaction costs and 1% proportional transaction costs")
    longOnly_MeanReversion_strat_wCosts = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000, ftc=4, ptc=0.01)
    longOnly_MeanReversion_strat_wCosts.run_mean_reversion_strategy(sma=24, threshold=2)