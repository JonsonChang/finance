# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
#from matplotlib.finance import candlestick_ohlc


class stock:

    def __init__(self, filename):
        def datefunc(x): return mdates.date2num(
            datetime.strptime(x.decode('ascii'), '%Y/%m/%d'))
        self.raw = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=1,
            converters={0: datefunc})
            
        if(self.raw[0][0] > self.raw[1][0]):
            self.raw = self.raw[::-1]  # 反向

        self.date = []
        self.opened = []
        self.high = []
        self.low = []
        self.close = []

        for index, data in enumerate(self.raw):
            tmp_date = data[0]
            tmp_open = data[1]
            tmp_high = data[2]
            tmp_low = data[3]
            tmp_close = data[4]

            if np.isnan(tmp_close):
                continue

            self.date.append(tmp_date)
            self.opened.append(tmp_open)
            self.high.append(tmp_high)
            self.low.append(tmp_low)
            self.close.append(tmp_close)


    def feature_High(self, n=5):
        high_n = []
        for i in range(0, len(self.high)):
            start = i - n + 1
            end = i + 1
            if(start < 0):
                start = 0
            high_n.append(max(self.high[start:end]))
        return (high_n)

    def feature_Low(self, n=5):
        low_n = []
        for i in range(0, len(self.low)):
            start = i - n + 1
            end = i + 1
            if(start < 0):
                start = 0
            low_n.append(min(self.low[start:end]))
        return (low_n)

    def feature_MA(self, n=5):  # 移動平均線
        ret = np.cumsum(self.close, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        # return ret[n - 1:] / n
        return ret[:] / n

    def feature_MA_slope(self, n=10): # 均線協率
        ret = self.feature_MA(n)
        ret[1:] = ret[1:] - ret[:-1]
        return ret[:]

    def feature_BIAS(self, n=5):  # 乖離率
        ret = np.cumsum(self.close, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        ret = ret / n  # average
        ret = ((self.close - ret) / ret)
        return ret[:]

    def feature_Annualized(self, y=5, period = 20):  
        # 年化報酬率, 
        # y: 幾年
        # period： 幾條k 為一年。
        # 日k, period = 260, 月K period =12，週k period = 52
        n = y*period 
        close = np.array(self.close)
        high = np.array(self.high) #買在當時的最高點
        if(np.isnan(high[0])):
            high = np.array(self.close) #基金資料 沒有High 的值，使用close 代替
        ret = ((close / np.roll(high, n))**(1/y)) -1
        return self.date[n:], ret[n:]*100

    def feature_RSV(self, n=9):
        high_n = []
        low_n = []
        result = []
        for i in range(0, len(self.high)):
            start = i - n + 1
            end = i + 1
            if(start < 0):
                start = 0

            high_n.append(max(self.high[start:end]))
            low_n.append(min(self.low[start:end]))

        h = np.array(high_n)
        l = np.array(low_n)
        c = np.array(self.close)
        result = ((c - l) / (h - l)) * 100
        return (result)

    def feature_K(self, n=9):
        K = []
        RSV = self.feature_RSV(n)
        for i in range(0, len(self.high)):
            pre_K = 50
            if(i > 0):
                pre_K = K[i - 1]
            current_K = pre_K * (2 / 3) + RSV[i] * (1 / 3)
            K.append(current_K)
        return K

    def feature_D(self, n=9):
        D = []
        K = self.feature_K(n)
        for i in range(0, len(self.high)):
            pre_D = 50
            if(i > 0):
                pre_D = D[i - 1]
            current_D = pre_D * (2 / 3) + K[i] * (1 / 3)
            D.append(current_D)
        return D

    def feature_pulldown(self, n=120):
        #高檔拉回幅度
        Day = []
        pulldown = []
        l = len(self.close)
        for index in range(n+1,l):
            start = index - n
            end = index
            h = np.max(self.high[start:end])
            if np.isnan(h):
                h = np.max(self.close[start:end])
            Day.append(self.date[index -1])
            pulldown.append((self.close[index -1] - h)*100/h)

        return Day, pulldown

class stock_5day(stock):

    def __init__(self, filename):
        def datefunc(x): return mdates.date2num(
            datetime.strptime(x.decode('ascii'), '%Y/%m/%d'))
        self.raw = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=1,
            converters={0: datefunc})
            
        if(self.raw[0][0] > self.raw[1][0]):
            self.raw = self.raw[::-1]  # 反向

        self.date = []
        self.opened = []
        self.high = []
        self.low = []
        self.close = []
        
        a_day_date = []
        a_day_opened = []
        a_day_high = []
        a_day_low = []
        a_day_close = []        

        for index, data in enumerate(self.raw):
            tmp_date = data[0]
            tmp_open = data[1]
            tmp_high = data[2]
            tmp_low = data[3]
            tmp_close = data[4]

            if np.isnan(tmp_close):
                continue

            a_day_date.append(tmp_date)
            a_day_opened.append(tmp_open)
            a_day_high.append(tmp_high)
            a_day_low.append(tmp_low)
            a_day_close.append(tmp_close)

        for index in range(5 , len(a_day_close), 5):
            start = index -5
            end = index
            tmp_o =  np.array(a_day_opened[start:end])
            tmp_c =  np.array(a_day_close[start:end])
            tmp_h =  np.array(a_day_high[start:end])
            tmp_l =  np.array(a_day_low[start:end])
            tmp_date = a_day_date[index - 1]
            tmp_open = tmp_o[0]
            tmp_high = tmp_h.max()
            tmp_low = tmp_l.min()
            tmp_close = tmp_c[4]
            
            if np.isnan(tmp_open):
                tmp_open = tmp_c[0]
                tmp_high = tmp_c.max()
                tmp_low = tmp_c.min()
            
            self.date.append(tmp_date)
            self.opened.append(tmp_open)
            self.high.append(tmp_high)
            self.low.append(tmp_low)
            self.close.append(tmp_close)            
            
            

        
class stock_daytrade(stock):
    def __init__(self, filename):
        def datefunc(x): return mdates.date2num(
            datetime.strptime(x.decode('ascii'), '%Y/%m/%d %H:%M:%S'))
        self.raw = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=1,
            converters={0: datefunc})

        #if(self.raw[0][0] > self.raw[0][1]):
            #self.raw = self.raw[::-1]  # 反向
        
        self.date = []
        self.opened = []
        self.high = []
        self.low = []
        self.close = []
        
        for index, data in enumerate(self.raw):
            tmp_date = data[0]
            tmp_open = data[1]
            tmp_high = data[2]
            tmp_low = data[3]
            tmp_close = data[4]
        
            if np.isnan(tmp_close):
                continue
        
            self.date.append(tmp_date)
            self.opened.append(tmp_open)
            self.high.append(tmp_high)
            self.low.append(tmp_low)
            self.close.append(tmp_close)
            #f_UpDown.append(tmp_close - tmp_open)
            
    def feature_MA(self, n=5):  # 當沖移動平均線
        ma = np.cumsum(self.close, dtype=float)
        ma[n:] = ma[n:] - ma[:-n]
        ma = ma[:] / n
        
        #修正每日的前 n 個
        d = np.floor(self.date)
        day_start_index = 0
        for index, close in enumerate(self.close):
            #確認是否為新的一天
            if(index > 0 and d[index] != d[index-1] ):
                day_start_index = index
            diff = index - day_start_index
            if(diff >= n):
                continue
            ma[index] = np.average(self.close[day_start_index:index+1])
        return ma
        
    def feature_MA_slope(self, n=10):
        ret = self.feature_MA(n)
        ret[1:] = ret[1:] - ret[:-1]
        #修正每日的前 n 個
        d = np.floor(self.date)
        day_start_index = 0
        for index, close in enumerate(self.close):
            if(index > 0 and d[index] != d[index-1] ):
                day_start_index = index
                ret[index] = 0
        
        return ret[:]        
    def feature_BIAS(self, n=5):  # 當沖乖離率
        ret = self.feature_MA(n)
        ret = ((self.close - ret) / ret)
        return ret[:]
        
def time_filter(list_data, list_datetime, starttime=8*60, endtime=14*60):
    #跟據時間過濾資料
    result = []
    for index, data in enumerate(list_data):
        d = mdates.num2date(list_datetime[index])
        current = d.hour*60+d.minute
        if( current > starttime and current < endtime) :
            result.append(data)
    return result    
        
            
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    s = stock("測試資料/基金/富蘭克林坦伯頓全球投資系列-全球債券總報酬基金美元A.csv")
    date, data = s.feature_Annualized(1)
    date3, data3 = s.feature_Annualized(3)
    date5, data5 = s.feature_Annualized(5)
    date10, data10 = s.feature_Annualized(10)
    
    print("1年化: 平均 {0}，標準差 {1}，最小值 {2}".format(np.average(data),np.std(data),np.min(data)))
    print("3年化: 平均 {0}，標準差 {1}，最小值 {2}".format(np.average(data3),np.std(data3),np.min(data3)))
    if len(data3) >0 :
        print("5年化: 平均 {0}，標準差 {1}，最小值 {2}".format(np.average(data5),np.std(data5),np.min(data5)))
    if len(data10) >0 :
        print("10年化: 平均 {0}，標準差 {1}，最小值 {2}".format(np.average(data10),np.std(data10),np.min(data10)))

    plt.plot_date( date, data , "-", label="1")
    plt.plot_date( date3, data3 , "-", label="3")
    plt.plot_date( date5, data5 , "-", label="5")
    plt.grid()
    plt.legend()
    plt.show()
    

# ############ 畫 K 線########    
#    s = stock_daytrade("測試資料/台灣加權指數/TXF1-分鐘-成交價_test.csv")
#    b = s.raw.tolist()
#    fig, ax = plt.subplots()
#    #plt.plot_date(s.date, s.close, "o")
#    candlestick_ohlc(ax, b, colorup='r', colordown='g', width=0.0003)
#    plt.show()
#    a = s.feature_MA_slope(5)
#    b = s.feature_MA(5)

