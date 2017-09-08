# -*- coding: utf-8 -*-
# J.Granville Rules 葛蘭碧八大法則 測試
# http://allanlin998.blogspot.tw/2014/04/etf-5-mean-reversion.html
# python D:\Dropbox\0_回家作業\finance\GranvilleRules.py

import sys
import matplotlib.pyplot as plt
import numpy as np
from stock import stock


class GranvilleRules:
    def __init__(self, filename, nday=40, BIAS_std1=0.15, BIAS_std2=1):
        self.nday = nday
        self.BIAS_std1 = BIAS_std1
        self.BIAS_std2 = BIAS_std2
        self.s = stock(filename)

        self.list_ma = self.s.feature_MA(nday)
        self.list_ma_slope = np.array(self.s.feature_MA_slope(nday))  # 均線斜率
        self.list_BIAS = self.s.feature_BIAS(nday)

        self.BIAS_mean = self.list_BIAS[nday:].mean() / 100
        self.BIAS_std = self.list_BIAS[nday:].std() / 100

        self.list_line1 = (self.BIAS_mean + self.BIAS_std1 *
                           self.BIAS_std) * self.list_ma + self.list_ma
        self.list_line2 = (self.BIAS_mean - self.BIAS_std1 *
                           self.BIAS_std) * self.list_ma + self.list_ma
        self.list_line3 = (self.BIAS_mean + self.BIAS_std2 *
                           self.BIAS_std) * self.list_ma + self.list_ma
        self.list_line4 = (self.BIAS_mean - self.BIAS_std2 *
                           self.BIAS_std) * self.list_ma + self.list_ma

        # 均線向下時，放寬
        self.ma_slope_down = self.list_ma_slope[nday:].mean(
        ) - self.BIAS_std1 * self.list_ma_slope[nday:].std()
        # 均線向上時，放寬
        self.ma_slope_up = self.list_ma_slope[nday:].mean(
        ) + self.BIAS_std1 * self.list_ma_slope[nday:].std()

    def cross_over(self, line1, line2, index):
        if (index < 1):
            return False
        today = line1[index]
        yesterday = line1[index - 1]
        value = line2[index]
        if (today > value and yesterday <= value):
            return True
        else:
            return False

    def cross_under(self, line1, line2, index):
        if (index < 1):
            return False
        today = line1[index]
        yesterday = line1[index - 1]
        value = line2[index]
        if (today < value and yesterday >= value):
            return True
        else:
            return False

    def get_profit_up(self):  # 只做多單
        marketposition = 0
        self.list_close = self.s.close
        self.list_date = self.s.date
        self.list_profit = []
        self.list_profit_date = []

        self.list_trade = []
        self.list_trade_date = []
        self.list_trade_out = []
        self.list_trade_out_date = []
        for index, data in enumerate(self.list_close):
            if(index <= self.nday):
                continue
            if(marketposition == 0):
                if(self.list_ma[index] > self.list_ma[index - 1]):  # 均線向上
                    if(self.cross_over(self.list_close, self.list_line1, index)):
                        marketposition = 1
                if(self.list_ma[index] > self.list_ma[index - 1]):  # 均線向下，乖離過大，
                    if(self.cross_over(self.list_close, self.list_line4, index)):
                        marketposition = 0  # (逆勢，不使用)
                if(marketposition == 1):  # 確定入場
                    cost = data
                    self.list_trade.append(data)
                    self.list_trade_date.append(self.list_date[index])

            if(marketposition != 0):  # 停損 or 停利
                if(self.list_ma_slope[index] < self.ma_slope_down):  # 均線向下
                    marketposition = 0
                if(self.cross_under(self.list_close, self.list_line3, index)):  # 乖離率過高
                    marketposition = 0
                if(self.cross_under(self.list_close, self.list_line2, index)):  # 向下突破
                    marketposition = 0
                if(marketposition == 0):  # 確定出場
                    profit = data - cost
                    self.list_profit.append(profit)
                    self.list_profit_date.append(self.list_date[index])
                    self.list_trade_out.append(data)
                    self.list_trade_out_date.append(self.list_date[index])
        return (np.array(self.list_profit).sum())

    def get_profit_down(self):  # 只做空單
        marketposition = 0
        self.list_close = self.s.close
        self.list_date = self.s.date
        self.list_profit = []
        self.list_profit_date = []

        self.list_trade = []
        self.list_trade_date = []
        self.list_trade_out = []
        self.list_trade_out_date = []
        for index, data in enumerate(self.list_close):
            if(index <= self.nday):
                continue
            if(marketposition == 0):
                if(self.list_ma[index] < self.list_ma[index - 1]):  # 均線向上
                    if(self.cross_under(self.list_close, self.list_line2, index)):
                        marketposition = 1
                if(self.list_ma[index] > self.list_ma[index - 1]):  # 均線向下，乖離過大，
                    if(self.cross_over(self.list_close, self.list_line4, index)):
                        marketposition = 0  # (逆勢，不使用)
                if(marketposition == 1):  # 確定入場
                    cost = data
                    self.list_trade.append(data)
                    self.list_trade_date.append(self.list_date[index])

            if(marketposition != 0):  # 停損 or 停利
                if(self.list_ma_slope[index] > self.ma_slope_up):  # 均線向下
                    marketposition = 0
                if(self.cross_over(self.list_close, self.list_line4, index)):  # 乖離率過高
                    marketposition = 0
                if(self.cross_over(self.list_close, self.list_line1, index)):  # 向下突破
                    marketposition = 0
                if(marketposition == 0):  # 確定出場
                    profit = data - cost
                    self.list_profit.append(profit)
                    self.list_profit_date.append(self.list_date[index])
                    self.list_trade_out.append(data)
                    self.list_trade_out_date.append(self.list_date[index])
        return (np.array(self.list_profit).sum())
        pass

    def plot(self):
        plt.plot_date(self.list_date, self.list_ma, "-", lw=1)
        plt.plot_date(self.list_date, self.list_line1, "--")
        plt.plot_date(self.list_date, self.list_line2, "--")
        plt.plot_date(self.list_date, self.list_line3, "--")
        plt.plot_date(self.list_date, self.list_line4, "--")
        plt.plot_date(self.list_date, self.list_close, "-")
        plt.plot_date(self.list_trade_date, self.list_trade, "gv")
        plt.plot_date(self.list_trade_out_date, self.list_trade_out, "r^")  
        plt.show()
        pass

    def plot_profit(self):
        plt.plot_date(self.list_profit_date, np.cumsum(self.list_profit), "-")
        plt.show()
        pass


if __name__ == '__main__':
    g = GranvilleRules("price_data.csv", nday=50, BIAS_std1=0.15, BIAS_std2=1)
    profit = g.get_profit_down()
    g.plot()
    sys.exit
    
    test_range = np.array((np.arange(0.6,1.5,0.1)))
    test_result = np.arange(0.5,1.5,0.1)
    #for nday in range (20,90):
    for nday in range (30,60):
        tmp = []
        tmp.append(nday)
        for std in test_range:
            g = GranvilleRules("price_data.csv", nday=nday, BIAS_std1=0.15, BIAS_std2=std)
            profit = g.get_profit_up()
            print(nday, std, profit)
            tmp.append(profit)
    
        test_result = np.vstack([test_result, tmp])
