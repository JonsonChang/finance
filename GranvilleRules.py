# -*- coding: utf-8 -*-
# J.Granville Rules 葛蘭碧八大法則 測試
# http://allanlin998.blogspot.tw/2014/04/etf-5-mean-reversion.html

import sys
import matplotlib.pyplot as plt
import numpy as np
from stock import stock

# 參數設定
nday = 20
BIAS_std1 = 0.08  # 停損用
BIAS_std1 = 0.15  # 進場用
BIAS_std2 = 1


s = stock("price_data.csv")
list_ma = s.feature_MA(nday)
list_BIAS = s.feature_BIAS(nday)

BIAS_mean = list_BIAS[nday:].mean() / 100
BIAS_std = list_BIAS[nday:].std() / 100

list_line1 = (BIAS_mean + BIAS_std1 * BIAS_std) * list_ma + list_ma
list_line2 = (BIAS_mean - BIAS_std1 * BIAS_std) * list_ma + list_ma
list_line3 = (BIAS_mean + BIAS_std2 * BIAS_std) * list_ma + list_ma
list_line4 = (BIAS_mean - BIAS_std2 * BIAS_std) * list_ma + list_ma


plt.plot(list_ma[nday:])
plt.plot(s.close[nday:])
plt.plot(list_line1[nday:], "--")
plt.plot(list_line2[nday:], "--")
plt.plot(list_line3[nday:], "--")
plt.plot(list_line4[nday:], "--")
plt.show()

###############################################
# 回測


def cross_over(line1, line2, index):
    if (index < 1):
        return False
    today = line1[index]
    yesterday = line1[index - 1]
    value = line2[index]
    if (today > value and yesterday <= value):
        return True
    else:
        return False


def cross_under(line1, line2, index):
    if (index < 1):
        return False
    today = line1[index]
    yesterday = line1[index - 1]
    value = line2[index]
    if (today < value and yesterday >= value):
        return True
    else:
        return False


money = 0
marketposition = 0

list_ma5 = s.feature_MA(5)
list_ma20 = s.feature_MA(30)
list_close = s.close
list_date = s.date
list_profit = []
list_profit_date = []


list_trade = []
list_trade_date = []

plt.subplot(211)
for index, data in enumerate(list_close):
    if(index <= nday):
        continue
    if(marketposition == 0):
        if(cross_over(list_ma5, list_ma20, index)):
            marketposition = 1
            cost = data
            list_trade = [data]
            list_trade_date = [list_date[index]]

    if(marketposition != 0):
        if(cross_under(list_ma5, list_ma20, index)):
            marketposition = 0
            profit = data - cost
            list_profit.append(profit)
            list_profit_date.append(list_date[index])
            list_trade.append(data)
            list_trade_date.append(list_date[index])

            plt.plot_date(list_trade_date, list_trade, "r")


plt.plot_date(list_date, list_close, "-", lw=1)
plt.plot_date(list_date, list_ma20, "--")
plt.plot_date(list_date, list_ma5, "--")
plt.subplot(212)
plt.plot_date(list_profit_date, np.cumsum(list_profit), "-")
plt.show()
