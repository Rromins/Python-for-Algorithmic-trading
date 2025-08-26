"""
Long positions only backtest strategy
"""

from backtest_base import BacktestBase
import matplotlib.pyplot as plt
plt.style.use('seaborn')

class LongOnlyBacktest(BacktestBase):
    """
    Long positions only backtest strategy
    """
    def __init__(self,
                 ticker: str,
                 start: str,
                 end: str,
                 amount: float,
                 ftc=0.0,
                 ptc=0.0,
                 verbose=True):
        super().__init__(ticker, start, end, amount, ftc, ptc, verbose)

    def RunMeanReversionStrategy(self, sma, threshold):
        '''
        Backtest a mean reversion strategy. The signals are computed from a time series 
        calculated as follow: close price - SMA. 

        Inputs
        ------
            SMA: length of the SMA
            threshold: the threshold used to compute the signals of the trading strategy
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
        self.data['norm_diff'] = (self.data['difference'] - self.data['difference'].mean()) / self.data['difference'].std()

        for bar in range(sma, len(self.data)):
            if self.position == 0:
                if (self.data['norm_diff'].iloc[bar] < -threshold):
                    self._place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if (self.data['norm_diff'].iloc[bar] >= 0.0):
                    self._place_sell_order(bar, units=self.units)
                    self.position = 0
        self._close_out(bar)

if __name__ == '__main__':
    start = '2020-01-01'
    end = '2025-05-01'
    longOnly_MeanReversion_strat = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000)
    longOnly_MeanReversion_strat.RunMeanReversionStrategy(sma=24, threshold=2)

    print("\n")
    print("Same but with 4USD fixed transaction costs and 1% proportional transaction costs")
    longOnly_MeanReversion_strat_wCosts = LongOnlyBacktest(ticker='BTC-USD', start=start, end=end, amount=1000, ftc=4, ptc=0.01)
    longOnly_MeanReversion_strat_wCosts.RunMeanReversionStrategy(sma=24, threshold=2)