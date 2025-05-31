import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')
from backtestbase_class import BacktestBase

class LongOnlyBacktest(BacktestBase):
    def __init__(self, 
                 ticker: str,
                 start: str,
                 end: str,
                 amount: float,
                 ftc=0.0,
                 ptc=0.0,
                 verbose=True):
        super().__init__(ticker, start, end, amount, ftc, ptc, verbose)

    def run_meanReversion_strategy(self, SMA, threshold):
        '''
        Backtest a mean reversion strategy. The signals are computed from a time series calculated as follow: close price - SMA. 

        Inputs ---
            SMA: length of the SMA
            threshold: the threshold used to compute the signals of the trading strategy
        '''
        msg  = f"\n\nRunning mean reversion strategy | "
        msg += f"Length SMA={SMA} & thr={threshold}"
        msg += f"\nfixed costs {self.ftc} | "
        msg += f"proportional costs {self.ptc}"
        print(msg)
        print("-"*55)
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount
        
        self.data['SMA'] = self.data['close'].rolling(SMA).mean()
        self.data['difference'] = self.data['close'] - self.data['SMA']
        self.data['norm_diff'] = (self.data['difference'] - self.data['difference'].mean()) / self.data['difference'].std()
        
        for bar in range(SMA, len(self.data)):
            if self.position == 0:
                if (self.data['norm_diff'].iloc[bar] < -threshold):
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if (self.data['norm_diff'].iloc[bar] >= 0.0):
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0
        self.close_out(bar)

if __name__ == '__main__':
    start = '2020-01-01'
    end = '2025-05-01'
    longOnly_MeanReversion_strat = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000)
    longOnly_MeanReversion_strat.run_meanReversion_strategy(SMA=24, threshold=2)

    print("\n")
    print("Same but with 4USD fixed transaction costs and 1% proportional transaction costs")
    longOnly_MeanReversion_strat_wCosts = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000, ftc=4, ptc=0.01)
    longOnly_MeanReversion_strat_wCosts.run_meanReversion_strategy(SMA=24, threshold=2)