import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
plt.style.use('seaborn')

from backtest_base import BacktestBase

class MACDBacktest(BacktestBase):
    def __init__(self, 
                 ticker, 
                 start, 
                 end, 
                 amount, 
                 ftc=0, 
                 ptc=0, 
                 verbose=True):
        super().__init__(ticker, start, end, amount, ftc, ptc, verbose)

    def macd(method, fast_length, slow_length):
        '''
        Compute the MACD indicator
        '''
        

    def run_macd_strategy():
        '''
        MACD Strategy
        '''