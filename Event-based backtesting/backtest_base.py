"""
Base class for event-based backtesting
"""

import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class BacktestBase():
    """
    Base class for event-based backtesting of trading strategies.

    Provides fundamental methods to download market data, 
    simulate trades (buy/sell), track balances, and evaluate performance.

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
    def __init__(self,
                 ticker: str,
                 start: str,
                 end: str,
                 amount: float,
                 ftc=0.0,
                 ptc=0.0,
                 verbose=True):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.units = 0
        self.position = 0
        self.trades = 0
        self.verbose = verbose
        self._get_data()

    def _get_data(self):
        '''
        Retrieve historical price data from Yahoo Finance.

        The method renames standard OHLCV columns and computes log returns.
        '''
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volume']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        self.data = df

    def plot_data(self):
        '''
        Plot the asset's close price over time.
        '''
        plt.plot(self.data['close'], color='gray', label='close price')
        plt.legend()
        plt.title(f"{self.ticker} close price")
        plt.plot()

    def _get_date_price(self, candle):
        '''
        Get the date and closing price for a given candle index.

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.

        Returns
        -------
        tuple
            (date as str, close price as float)
        '''
        date = str(self.data.index[candle])
        price = self.data['close'].iloc[candle]
        return date, price

    def _print_balance(self, candle):
        '''
        Print the current cash balance at a given candle.

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.
        '''
        date, price = self._get_date_price(candle)
        print(f"{date}, current balance: {self.amount:.2f}, at current price: {price}")

    def _print_net_wealth(self, candle):
        '''
        Print the current net wealth (cash + asset holdings).

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.
        '''
        date, price = self._get_date_price(candle)
        net_wealth = self.units*price + self.amount
        print(f"{date}, current net wealth: {net_wealth:.2f}")

    def _place_buy_order(self, candle, units=None, amount=None):
        '''
        Execute a buy order for a given number of units or monetary amount.

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.
        units : float, optional
            Number of units to buy. If None, 'amount' must be provided.
        amount : float, optional
            Monetary amount to invest. Used to compute units if `units` is None.
        '''
        date, price = self._get_date_price(candle)
        if units is None:
            units = float(amount / price)
        self.amount -= (units*price) * (1+self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f"{date}, buying {units} units at {price:.2f}")
            self._print_balance(candle)
            self._print_net_wealth(candle)

    def _place_sell_order(self, candle, units=None, amount=None):
        '''
        Execute a sell order for a given number of units or monetary amount.

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.
        units : float, optional
            Number of units to sell. If None, 'amount' must be provided.
        amount : float, optional
            Monetary amount to liquidate. Used to compute units if `units` is None.
        '''
        date, price = self._get_date_price(candle)
        if units is None:
            units = float(amount / price)
        self.amount += (units*price) * (1-self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(f"{date}, selling {units} units at {price:.2f}")
            self._print_balance(candle)
            self._print_net_wealth(candle)

    def _close_out(self, candle):
        '''
        Close all open positions at a given candle.

        Parameters
        ----------
        candle : int
            Index of the bar/candle in the price DataFrame.
        '''
        date, price = self._get_date_price(candle)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(f"{date}, inventory {self.units} units at {price:.2f}")
            print("-"*55)
            print(f"Final balance  [$] {self.amount:.2f}")
            perf = (self.amount - self.initial_amount) / self.initial_amount*100
            print(f"Net performance  [%] {perf:.2f}")
            print(f"Trades Executed  [#] {self.trades:.2f}")
            print("-"*55)
