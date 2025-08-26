"""
Backtesting framework for long/short trading strategies.
"""

from backtest_base import BacktestBase
import matplotlib.pyplot as plt
plt.style.use('seaborn')

class LongShortBacktest(BacktestBase):
    """
    Backtesting framework for long/short trading strategies.

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
    def _go_long(self, candle, units=None, amount=None):
        """
        Enter a long position at a given candle.

        If there is already an open short position, it is liquidated first.
        A long position can then be opened either by specifying a number of units
        or by allocating a monetary amount.

        Parameters
        ----------
        candle : int
            Index of the candle (row in the DataFrame) at which the order is executed.
        units : int, optional
            Number of units to buy. Mutually exclusive with `amount`.
        amount : float or str, optional
            Monetary amount to invest. If set to `"all"`, the entire
            available capital (`self.amount`) is invested.
        """
        # first check if there already a short position, and if yes liquidate it.
        if self.position == -1:
            self._place_buy_order(candle, units=-self.units)
        if units:
            self._place_buy_order(candle, units=units)
        elif amount:
            if amount == 'all':
                amount = self.amount
            self._place_buy_order(candle, amount=amount)

    def _go_short(self, candle, units=None, amount=None):
        """
        Enter a short position at a given candle.

        If there is already an open long position, it is liquidated first.
        A short position can then be opened either by specifying a number of units
        or by allocating a monetary amount.

        Parameters
        ----------
        candle : int
            Index of the candle (row in the DataFrame) at which the order is executed.
        units : int, optional
            Number of units to sell short. Mutually exclusive with `amount`.
        amount : float or str, optional
            Monetary amount to short. If set to `"all"`, the entire
            available capital (`self.amount`) is used.
        """
        # first check if there already a long position, and if yes liquidate it.
        if self.position == 1:
            self._place_sell_order(candle, units=self.units)
        if units:
            self._place_sell_order(candle, units=units)
        elif amount:
            if amount == 'all':
                amount = self.amount
            self._place_sell_order(candle, amount=amount)

    def run_mean_reversion_strategy(self, sma, threshold):
        """
        Run a mean reversion backtest with long and short positions.

        The trading signal is based on the deviation of the close price
        from its Simple Moving Average (SMA). The normalized difference
        is used to identify entry and exit points:
        
        - **Go long**: when normalized difference < `-threshold`
        - **Go short**: when normalized difference > `threshold`
        - **Exit long**: when normalized difference ≥ 0
        - **Exit short**: when normalized difference ≤ 0

        Parameters
        ----------
        sma : int
            Window length of the Simple Moving Average (SMA) used to
            compute the mean reversion signal.
        threshold : float
            Threshold value for the normalized difference to trigger
            trading signals. Higher values make the strategy more
            conservative.
        """
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
                    self._go_long(candle, amount=self.amount)
                    self.position = 1
                elif self.data['norm_diff'].iloc[candle] > threshold:
                    self._go_short(candle, amount=self.amount)
                    self.position = -1

            elif self.position == 1:
                if self.data['norm_diff'].iloc[candle] >= 0:
                    self._place_sell_order(candle, units=self.units)
                    self.position = 0

            elif self.position == -1:
                if self.data['norm_diff'].iloc[candle] <= 0:
                    self._place_buy_order(candle, units=-self.units)
                    self.position = 0
        self._close_out(candle)

if __name__ == '__main__':
    start = '2020-01-01'
    end = '2025-05-01'
    longShort_MeanReversion_strat = LongShortBacktest(ticker='BTC-USD', start=start, end=end, amount=1000)
    longShort_MeanReversion_strat.run_mean_reversion_strategy(sma=24, threshold=2)

    print("\n")
    print("Same but with 4USD fixed transaction costs and 1% proportional transaction costs")
    longShort_MeanReversion_strat = LongShortBacktest(ticker='BTC-USD', start=start, end=end, amount=1000, ftc=4, ptc=0.01)
    longShort_MeanReversion_strat.run_mean_reversion_strategy(sma=24, threshold=2)
