import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

class BacktestBase(object):
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
        self.get_data()

    def get_data(self):
        '''
        Retreive data from yahoo finance, rename the columns and create the columns 
        with the log returns
        '''
        df = yf.download(tickers=self.ticker, start=self.start, end=self.end)
        df.columns = ['close', 'high', 'low', 'open', 'volume']
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        self.data = df

    def plot_data(self):
        '''
        Plot the stock close price
        '''
        fig, ax = plt.subplots(1, 1)
        ax.plot(self.data['close'], color='gray', label='close price')
        ax.legend()
        ax.set_title(f"{self.ticker} close price")
        plt.plot()

    def get_date_price(self, bar):
        '''
        Return date and price for a given bar
        '''
        date = str(self.data.index[bar])
        price = self.data['close'].iloc[bar]
        return date, price
    
    def print_balance(self, bar):
        '''
        Print current cash balance info
        '''
        date, price = self.get_date_price(bar)
        print(f"{date}, current balance: {self.amount:.2f}")

    def print_net_wealth(self, bar):
        '''
        Print current net wealth info
        '''
        date, price = self.get_date_price(bar)
        net_wealth = self.units*price + self.amount
        print(f"{date}, current net wealth: {net_wealth:.2f}")

    def place_buy_order(self, bar, units=None, amount=None):
        '''
        Place a buy order
        '''
        date, price = self.get_date_price(bar)
        if units is None:
            units = float(amount / price)
        self.amount -= (units*price) * (1+self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f"{date}, buying {units} units at {price:.2f}")
            self.print_balance(bar)
            self.print_net_wealth(bar)
        
    def place_sell_order(self, bar, units=None, amount=None):
        '''
        Place a sell order
        '''
        date, price = self.get_date_price(bar)
        if units is None:
            units = float(amount / price)
        self.amount += (units*price) * (1-self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(f"{date}, selling {units} units at {price:.2f}")
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def close_out(self, bar):
        '''
        Closing out a long or short position
        '''
        date, price = self.get_date_price(bar)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(f"{date}, inventory {self.units} units at {price:.2f}")
            print("-"*55)
            print(f"Final balance  [$] {self.amount:.2f}")
            perf = ((self.amount - self.initial_amount) / self.initial_amount*100)
            print(f"Net performance  [%] {perf:.2f}")
            print(f"Trades Executed  [#] {self.trades:.2f}")
            print("-"*55)