# -*- coding: utf-8 -*-
# J.Granville Rules 葛蘭碧八大法則 測試
# http://allanlin998.blogspot.tw/2014/04/etf-5-mean-reversion.html
# python D:\Dropbox\0_回家作業\finance\GranvilleRules.py

import sys
import matplotlib.pyplot as plt
import numpy as np
from stock import stock
from stock import stock_5day
import tools


class GranvilleRules:
    def __init__(self, filename, nday=40, BIAS_std1=0.15, BIAS_std2=1):
        # for traning data, 自動找出最佳的 乖離率
        self.nday = nday
        self.BIAS_std1 = BIAS_std1
        self.BIAS_std2 = BIAS_std2
        self.s = stock(filename)
#        self.s = stock_5day(filename)

        self.list_ma = self.s.feature_MA(nday)
        self.list_ma_slope = np.array(self.s.feature_MA_slope(nday))  # 均線斜率
        self.list_BIAS = self.s.feature_BIAS(nday)

        self.BIAS_mean = self.list_BIAS[nday:].mean()
        self.BIAS_std = self.list_BIAS[nday:].std()

        
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
                        
        x1 = np.array(list(filter(fa,self.list_BIAS)))
        x2 = np.array(list(filter(fb,self.list_BIAS)))
        self.list_line1 = (tools.list_percentage(x1,BIAS_std1)+1)* self.list_ma 
        self.list_line3 = (tools.list_percentage(x1,BIAS_std2)+1)* self.list_ma 
        
        self.list_line2 = (tools.list_percentage(x2,(1-BIAS_std1))+1)* self.list_ma
        self.list_line4 = (tools.list_percentage(x2,(1-BIAS_std2))+1)* self.list_ma 
        
        print(tools.list_percentage(self.list_BIAS,0.1), tools.list_percentage(self.list_BIAS,0.5), tools.list_percentage(self.list_BIAS,0.6), tools.list_percentage(self.list_BIAS,0.85))

        # 均線向下時，放寬
        self.ma_slope_down = self.list_ma_slope[nday:].mean() - 0.15 * self.list_ma_slope[nday:].std()
        if self.ma_slope_down > 0:
            self.ma_slope_down = 0
        # 均線向上時，放寬
        self.ma_slope_up = self.list_ma_slope[nday:].mean() + 0.15 * self.list_ma_slope[nday:].std()

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
                    # todo: 增加扣抵值的預估，基金的操作需要。 當沖可能不需要
                    if(self.cross_over(self.list_close, self.list_line1, index)):
                        marketposition = 1
                        print("in: 方向往上", )
                elif(self.list_ma[index] > self.list_ma[index - 1]):  # 均線向下，乖離過大，
                    if(self.cross_over(self.list_close, self.list_line4, index)):
                        pass
                        # marketposition = 0  # (逆勢，不使用)
                if(marketposition == 1):  # 確定入場
                    cost = data
                    self.list_trade.append(data)
                    self.list_trade_date.append(self.list_date[index])

            if(marketposition != 0):  # 停損 or 停利
                #連續三天，均線向下
                if(self.list_ma_slope[index] < self.ma_slope_down and self.list_ma_slope[index-1] < self.ma_slope_down and self.list_ma_slope[index-2] < self.ma_slope_down):  
                    marketposition = 0
                    print(
                        "out: 連三天均線向下 ",
                        self.list_ma_slope[index],
                        "<",
                        self.ma_slope_down)
                elif(self.cross_under(self.list_close, self.list_line3, index)):  # 乖離率過高
                    marketposition = 0
                    print(
                        "out: 乖離率過高 ",
                        self.list_close[index],
                        "<",
                        self.list_line3[index])
                elif(self.list_close[index] < self.list_line2[index]):  # 向下突破
                    marketposition = 0
                    print(
                        "out: 向下突破 ",
                        self.list_close[index],
                        "<",
                        self.list_line2[index])
                elif(self.list_date[-2] == self.list_date[index]):
                    marketposition = 0
                    print("out: 最後一天，強制離場 ")
                else:
                    pass
#                    print("留單", self.list_date[-2] , self.list_date[index])
                if(marketposition == 0):  # 確定出場
                    profit = data - cost
                    self.list_profit.append(profit)
                    self.list_profit_date.append(self.list_date[index])
                    self.list_trade_out.append(data)
                    self.list_trade_out_date.append(self.list_date[index])
        return (np.array(self.list_profit).sum())

    def print_param(self):
        # 輸出traning 完的參數，供test 用
        Bias1 = self.BIAS_mean + self.BIAS_std1 * self.BIAS_std
        Bias2 = self.BIAS_mean - self.BIAS_std1 * self.BIAS_std
        Bias3 = self.BIAS_mean + self.BIAS_std2 * self.BIAS_std
        Bias4 = self.BIAS_mean - self.BIAS_std2 * self.BIAS_std
        print("**** 參數輸出 ****")
        print("Bias1=", Bias1)
        print("Bias2=", Bias2)
        print("Bias3=", Bias3)
        print("Bias4=", Bias4)
        print("nday=", self.nday)
        print("ma_slope_down=", self.ma_slope_down)
        print("ma_slope_up=", self.ma_slope_up)
        return (self.nday, Bias1, Bias2, Bias3, Bias4,
                self.ma_slope_down, self.ma_slope_up)

    def plot(self):
        plt.plot_date(self.list_date[self.nday:],
                      self.list_ma[self.nday:], "-", lw=1)
        plt.plot_date(self.list_date[self.nday:],
                      self.list_line1[self.nday:], "--")
        plt.plot_date(self.list_date[self.nday:],
                      self.list_line2[self.nday:], "--")
        plt.plot_date(self.list_date[self.nday:],
                      self.list_line3[self.nday:], "--")
        plt.plot_date(self.list_date[self.nday:],
                      self.list_line4[self.nday:], "--")
        plt.plot_date(self.list_date, self.list_close, "-")
        plt.plot_date(self.list_trade_out_date, self.list_trade_out, "go")
        plt.plot_date(self.list_trade_date, self.list_trade, "ro")
        plt.show()

    def plot_profit(self):
        profit = np.sum(self.list_profit)
        print("*** 次數=", len(self.list_profit), " 獲利=", profit)
        plt.plot_date(self.list_profit_date, np.cumsum(self.list_profit), "-")
        plt.show()


class GranvilleRules_test(GranvilleRules):
    def __init__(self, filename, nday, Bias1, Bias2,
                 Bias3, Bias4, ma_slope_down, ma_slope_up):
        # for test data, 手動帶入所有參數
        self.nday = nday
        self.s = stock(filename)

        self.list_ma = self.s.feature_MA(nday)
        self.list_ma_slope = np.array(self.s.feature_MA_slope(nday))  # 均線斜率

        self.list_line1 = (Bias1) * self.list_ma + self.list_ma
        self.list_line2 = (Bias2) * self.list_ma + self.list_ma
        self.list_line3 = (Bias3) * self.list_ma + self.list_ma
        self.list_line4 = (Bias4) * self.list_ma + self.list_ma

        self.ma_slope_down = ma_slope_down
        self.ma_slope_up = ma_slope_up

def get_good_days(test_result):
    l = len(test_result)
    l2 = len(test_result[0])
    max_val = -999
    
    best_idx1 = -1
    best_idx2 = -1
    for idx in range(3,l-3):
        for idx2 in range(2,l2-2):
            val = (test_result[idx-1][idx2-1] + test_result[idx-1][idx2] + test_result[idx-1][idx2+1]+ 
            test_result[idx][idx2-1] + test_result[idx][idx2] + test_result[idx][idx2+1] + 
            test_result[idx+1][idx2-1] + test_result[idx+1][idx2] + test_result[idx+1][idx2+1])/9
            if val > max_val :
                max_val = val
                best_idx1 = idx
                best_idx2 = idx2
#                print(idx,idx2)

    best_ma =test_result[best_idx1][0]
    best_std = test_result[0][best_idx2]
    print("\n ## Best day: {}, best STD: {}, val: {}".format(best_ma,best_std , max_val))
    return best_ma,best_std

if __name__ == '__main__':
    # 1. 用大範圍找出最佳參數
    #f_name = "測試資料/基金/{0}.csv".format(sys.argv[1])
    f_name = "測試資料/台股/000001.SSd.csv"
    f_name = "測試資料/台股/HYGd.csv"
    #f_name = "測試資料/msci_china.csv"
    #f_name = "測試資料/基金/貝萊德環球政府債券基金A2美元.csv"
    #f_name = "測試資料/基金/HYG_5Y.csv"
    
    test_range = np.array((np.arange(0.3, 0.48, 0.01)))
    test_result = np.arange(0.3 - 0.01, 0.48, 0.01)
    for nday in range(15, 90, 1):
        tmp = []
        tmp.append(nday)
        for std in test_range:
            print("new start n=", nday, " std=", std)
            g = GranvilleRules(
                f_name,
                nday=nday,
                BIAS_std1=0.03,
                BIAS_std2=std)
            profit = g.get_profit_up()
            print(nday, std, profit)
            tmp.append(profit)

        test_result = np.vstack([test_result, tmp])
        
# 計算最佳天數。
    best_ma,best_std = get_good_days(test_result)
    #best_ma =13
        
    print(f_name)
# 2. 使用traning 數據, 將參數印出。
    g = GranvilleRules(
        f_name,
        nday=int(best_ma),
        BIAS_std1=0.03,
        BIAS_std2=best_std)
    profit = g.get_profit_up()
    g.plot()
    g.plot_profit()
    nday, Bias1, Bias2, Bias3, Bias4, ma_slope_down, ma_slope_up = g.print_param()

# 3. 將資料帶入 測試數據
#    gtest = GranvilleRules_test(
#        f_name,
#        nday,
#        Bias1,
#        Bias2,
#        Bias3,
#        Bias4,
#        ma_slope_down,
#        ma_slope_up)
#    profit = gtest.get_profit_up()
#    print(profit)
#    gtest.plot()
#    gtest.plot_profit()
#