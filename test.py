# -*- coding: utf-8 -*-
# 常態分佈測試

import sys
import tools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from stock import stock
from stock import stock_daytrade

def test_profit():
    s = stock_daytrade("測試資料/台灣加權指數/TXF1-分鐘-成交價.csv")
    nday = 45
    good_mean = -100
    for nday in range(20, 21):
        data = np.array(s.close)
        data = (np.roll(data, -nday) - data) / data  # 報酬率
        data = data[nday:len(data) - nday - 1]

        num_bins = 50
        n, bins, patches = plt.hist(
            data, num_bins, normed=1, facecolor='blue', alpha=0.5)
        x, y = tools.normfun_ex(data)
        plt.plot(x, y, color='g', linewidth=1)
        plt.show()

        if(data.mean() * 100 > good_mean):
            good_mean = data.mean() * 100
            print(nday, data.mean() * 100, data.std() * 100)

        result = []
        for i in range(0, len(data), nday):
            result.append(data[i])
        n, bins, patches = plt.hist(
            result, num_bins, normed=1, facecolor='red', alpha=0.5)
        result = np.array(result)
        if(result.mean() * 100 > good_mean):
            good_mean = result.mean() * 100
            print(nday, result.mean() * 100, result.std() * 100)


def test_up_down():
    # 分別計算 上漲 和 下跌 的常態分佈 (分開來後，就沒有常態分佈了)
    up_mean = -100
    down_mean = -100
    for nday in range(30, 30):
        data = np.array(s.close)
        data = (np.roll(data, -nday) - data) / data
        data = data[nday:len(data) - nday - 1]

        up = []
        down = []
        for up_or_down in data:
            if(up_or_down > 0):
                up.append(up_or_down)
            elif(up_or_down < 0):
                down.append(up_or_down)

        up = np.array(up)
        down = np.array(down)
        num_bins = 50

        n, bins, patches = plt.hist(
            up, num_bins, normed=1, facecolor='red', alpha=0.5)
        n, bins, patches = plt.hist(
            down, num_bins, normed=1, facecolor='green', alpha=0.5)
        print(nday, up.mean() * 100, down.mean() * 100)


def test_ma_slope(nday=10):
    s = stock_daytrade("測試資料/台灣加權指數/TXF1-分鐘-成交價.csv")
    data = np.array(s.feature_MA_slope(nday))
    data = data[nday:len(data) - nday - 1]

    n, bins, patches = plt.hist(
        data, 50, normed=1, facecolor='red', alpha=0.5)
    x, y = tools.normfun_ex(data)
    print(nday, data.mean(), data.std())
    plt.plot(x, y, color='g', linewidth=1)
    plt.show()


def test_oneday():
    # 計算單一天的漲跌 (有常態分佈)
    # 長紅，長黑，是否為交易訊號？
    s = stock_daytrade("測試資料/台灣加權指數/TXF1-分鐘-成交價.csv")
    c = np.array(s.close)
    o = np.array(s.opened)
    data = c - o
    
    n, bins, patches = plt.hist(
        data, 500, normed=1, facecolor='red', alpha=0.5)
    x, y = tools.normfun_ex(data)
    print(data.mean(), data.std())
    plt.plot(x, y, color='g', linewidth=1)
    plt.show()

    # 找出訊號
    #up_signal_list = []
    #up_signal_date_list = []
    #down_signal_list = []
    #down_signal_date_list = []
    #
    #for index, data in enumerate(x):
    #    if(data > up_signal):
    #        up_signal_date_list.append(s.date[index])
    #        up_signal_list.append(c[index])
    #    if(data < down_signal):
    #        down_signal_date_list.append(s.date[index])
    #        down_signal_list.append(c[index])
    #
    #plt.plot(s.date, s.close)
    #plt.plot(up_signal_date_list, up_signal_list, "ro")
    #plt.plot(down_signal_date_list, down_signal_list, "go")
    #plt.show()


def test_BIAS():
    #計算乖離率, 有常態分佈
    nday = 50
    f_name = "測試資料/台股/HYGd.csv"
#    s = stock_daytrade(f_name)
    s = stock(f_name)
    c = np.array(s.close)
    o = np.array(s.opened)
    x = s.feature_BIAS(nday)
    x = x[nday:]
#    x = tools.time_filter(x, s.date,9*60,11*60)
    a, b = tools.normfun_ex(x)
    plt.plot(a, b, color='g', linewidth=1)
    plt.hist(x, 50, normed=1, facecolor='blue', alpha=0.5)
    plt.show()

    def fa(x):
        if x >0:
            return True
        else:
            return False
    def fb(x):
        if x >0:
            return False
        else:
            return True
                    
    x1 = np.array(list(filter(fa,x)))
    x2 = np.array(list(filter(fb,x)))
    print(x1)
    
    a, b = tools.normfun_ex(x1)
    plt.plot(a, b, color='g', linewidth=1)
    plt.hist(x1, 50, normed=1, facecolor='blue', alpha=0.5)
    plt.show()
    a, b = tools.normfun_ex(x2)
    plt.plot(a, b, color='g', linewidth=1)
    plt.hist(x2, 50, normed=1, facecolor='blue', alpha=0.5)
    plt.show()    
    
    # 如何定義漲多，跌深
    #sigma = 1  # 50% = 0.65，60% = 0.85，70% = 1.04，80%=1.3，90%=1.6
    #up_signal = x.mean() + sigma * x.std()
    #down_signal = x.mean() - sigma * x.std()
    #print(x.mean(), up_signal, down_signal)
    #sigma = 1.6  # 50% = 0.65，60% = 0.85，70% = 1.04，80%=1.3，90%=1.6
    #up_signal = x.mean() + sigma * x.std()
    #down_signal = x.mean() - sigma * x.std()
    #print(x.mean(), up_signal, down_signal)


def test_K():
    # K, D無常態分佈
    nday = 10
    s = stock("price_data.csv")
    x = s.feature_K()
    x = np.array(x[nday:])

    a, b = tools.normfun_ex(x)
    plt.plot(a, b, color='g', linewidth=1) 
    plt.hist(x, 60, normed=1, facecolor='blue', alpha=0.5)
    plt.show()

def test():
    nday = 20
    s = stock("測試資料/台股/0056d.csv")
    x = s.feature_diff()[nday:]*100

    a, b = tools.normfun_ex(x)
    plt.plot(a, b, color='g', linewidth=1)
    plt.hist(x, 60, normed=1, facecolor='blue', alpha=0.5)
    plt.show()

def fn_twstock():
    from twstocka import Stock    
    stock = Stock('2330')
    a= stock.fetch_from(2013, 11)
    b = stock.price



if __name__ == '__main__':
    #test_oneday()
    # test_profit()
    test_BIAS()
    #test()
    #test_ma_slope(60)
    # test_K()
