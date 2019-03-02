# -*- coding: utf-8 -*-
import numpy as np
import tools
from datetime import datetime ,timedelta
import matplotlib.dates as mdates
from twstocka import Stock
from urllib.request import urlopen
from lxml import etree
import talib


class stock:

    def __init__(self, filename, adj_fix=False):
        def datefunc(x): 
            # 日期格式，將'%Y-%m-%d' 轉成 '%Y/%m/%d'
            # since str and bytes is different in python 3. so it need encode and decode function here.
            tmpx = x.encode('ascii').decode().replace('-','/')
            #ret = mdates.date2num(datetime.strptime(x.encode('ascii').replace('-','/'), '%Y/%m/%d'))
            ret = mdates.date2num(datetime.strptime(tmpx, '%Y/%m/%d'))
            return ret
            
        self.filename = filename
        # add encoding parameter, let this function know the file format is ISO-8859-1, then it will working fine
        # under system with UTF-8 environment.
        self.raw = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=1,
            converters={0: datefunc},encoding='ISO-8859-1')
            
        if(self.raw[0][0] > self.raw[1][0]):
            self.raw = self.raw[::-1]  # 反向

        self.date = []
        self.opened = []
        self.high = []
        self.low = []
        self.close = []
        self.adj = [] # 只有yahoo finance 使用

        for index, data in enumerate(self.raw):
            tmp_date = data[0]
            tmp_open = data[1]
            tmp_high = data[2]
            tmp_low = data[3]
            tmp_close = data[4]
            tmp_adj = data[5]

            if np.isnan(tmp_close):
                continue

            self.date.append(tmp_date)
            self.opened.append(tmp_open)
            self.high.append(tmp_high)
            self.low.append(tmp_low)
            self.close.append(tmp_close)
            self.adj.append(tmp_adj)
        
        if adj_fix:
            close = np.array(self.close)
            adj = np.array(self.adj)
            diff = adj - close
            
            self.opened   = self.opened +diff
            self.high     = self.high   +diff
            self.low      = self.low    +diff
            self.close    = self.close  +diff
        

    def reduce_data_len(self, n = 1250): 
        # ex:最後五年的資料
        l = len(self.date)
        if l > n:
            if len(self.date) >= l:
                self.date = self.date[l-n:l-1]
            if len(self.opened) >= l:
                self.opened = self.opened[l-n:l-1]
            if len(self.high) >= l:
                self.high = self.high[l-n:l-1]
            if len(self.low) >= l:
                self.low = self.low[l-n:l-1]
            if len(self.close) >= l:
                self.close = self.close[l-n:l-1]
        print(l, len(self.close))
    
    def complete_data_yahoo(self,sid):
        url = "https://tw.stock.yahoo.com/q/q?s={0}".format(sid)
        #html = get_html(url)
        html =  urlopen(url).read()
        page = etree.HTML(html)
        hrefs = page.xpath(u"//td[contains(@align, 'center')]")
        t = hrefs[1].text
        o = hrefs[8].text
        h = hrefs[9].text
        l = hrefs[10].text
        c = hrefs[2].xpath(u"//b")[0].text 
        
        print(t,o,h,l,c)
        if t != '13:30' or o == '－':
            print("未收盤")
            return (datetime(2000,1,1),o,h,l,c)
        
        # for debug 找出相對應的位置
        #index = 0
        #for h in hrefs:
        #    print("\r\n {0}".format(index))
        #    print(etree.tostring(h, encoding='utf8') )
        #    index = index +1
        
        date_element = page.xpath(u"//td[contains(@width, '160')]")    
        date_element = page.xpath(u"//td[contains(@width, '160')]/font")
        date_str = date_element[0].text
        print(date_str)
        #date_str.index('資料日期:')
        date_str = date_str[12:]
        date_split = date_str.split("/")
        y = int(date_split[0])+1911
        m = int(date_split[1])
        d = int(date_split[2])
        
        dd = datetime(y,m,d)
        #return (datetime(2000,1,1),o,h,l,c)
        return(dd,o,h,l,c)
        
    def complate_data(self, sid):
        ret = False
        last_date = self.date[-1]
        stock = Stock(sid, initial_fetch=False)
        
        
        fetch_from_date = mdates.num2date(last_date) + timedelta(-10)
        stock.fetch_from(fetch_from_date.year, fetch_from_date.month)
        
        col_num = len(self.raw[0]) # csv 檔的 column 數
        append_str = ""
        for index in range(0,col_num -5):
            append_str = append_str + ",0"
        
        for index in range(-len(stock.date),0):
            d = stock.date[index]
            o = stock.open[index]
            h = stock.high[index]
            l = stock.low[index]
            c = stock.close[index]
            if(mdates.date2num(d) > last_date):
                str = "{0},{1},{2},{3},{4}".format(d.strftime('%Y/%m/%d'),o,h,l,c )
                print("資料回補：" + str)
                f = open(self.filename, 'a+')
                f.write(str+append_str+"\n")
                f.close()
                ret = True

        #return ret  # no yahoo
        #yahoo 資料確認
#        d,o,h,l,c = self.complete_data_yahoo(sid)
#        #print(d,o,h,l,c)
#        try:
#            if(mdates.date2num(d) > mdates.date2num(stock.date[-1]) and mdates.date2num(d) > last_date ):
#                str = "{0},{1},{2},{3},{4}".format(d.strftime('%Y/%m/%d'),o,h,l,c )
#                print("資料回補 yahoo：" + str)
#                f = open(self.filename, 'a+')
#                f.write(str+append_str+"\n")
#                f.close()
#                ret = True
#        except:
#            print("Error 資料回補 yahoo：" + str)
#            pass
        # 有更新資料時，回傳True
        return ret
    
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
        
        ma = ret[:] / n
        d = self.date
        return d[n:], ma[n:]

    def feature_MA_slope(self, n=10): # 均線斜率
        _, ret = self.feature_MA(n)
        ret[1:] = ret[1:] - ret[:-1]
        return ret[:]

    def feature_BIAS(self, n=5):  # 乖離率
        ret = np.cumsum(self.close, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        ret = ret / n  # average
        ret = ((self.close - ret) / ret)
        return ret[:]
        
    def feature_BIAS_down(self, n=5):  # 只計算負的乖離率
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

    def feature_talib_FASTK(self, n=9): # RSV
        h = np.array(self.high)
        l = np.array(self.low)
        c = np.array(self.close)
        K, D = talib.STOCHF(h,l,c,fastk_period=n, fastd_period=n, fastd_matype=0)
        return K  # RSV

    def feature_K(self, n=9):
        K = []
     #   RSV = self.feature_RSV(n)
        RSV = self.feature_talib_FASTK(n)
        for i in range(0, len(self.high)):
            pre_K = 50
            if(i > 0):
                pre_K = K[i - 1]
            if np.isnan(RSV[i]):
                RSV[i] = 50
            current_K = pre_K * (2 / 3) + RSV[i] * (1 / 3)
            K.append(current_K)
#            print(mdates.num2date(self.date[i]), current_K)
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

    def feature_K_MA(self, n=100): # k 值的移動平均線
        K = self.feature_K()
        ret = np.cumsum(K, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        ma = ret[:] / n
        return self.date[n:], ma[n:]   
        
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
            Day.append(self.date[index])
            pulldown.append((self.close[index] - h)*100/h)
        return Day, pulldown

    def feature_pullUp(self, n=120):
        #低檔拉回幅度
        Day = []
        pulldown = []
        l = len(self.close)
        for index in range(n+1,l):
            start = index - n
            end = index
            h = np.min(self.high[start:end])
            if np.isnan(h):
                h = np.min(self.close[start:end])
            Day.append(self.date[index])
            pulldown.append((self.close[index] - h)*100/h)
        return Day, pulldown
    
    def feature_diff(self, n=1): #漲跌幅度 百分比計算
        close_n = np.roll(self.close, n)
        ret = (np.array(self.close) - close_n) / close_n
        return ret		
        
class stock_5day(stock):

    def __init__(self, filename, adj_fix = False):

        super().__init__(filename, adj_fix)
        
        a_day_date = self.date
        a_day_opened = self.opened
        a_day_high = self.high
        a_day_low = self.low
        a_day_close = self.close
        a_day_adj = self.adj
        
        self.date = []
        self.opened = []
        self.high = []
        self.low = []
        self.close = []
        
        #資料長度調整為5的倍數, 這樣才會有最新一日的資料。
        trim_len = 5 - len(a_day_date) % 5
        for index in range(trim_len + 5 , len(a_day_close), 5):
            start = index -5
            end = index
            tmp_o =  np.array(a_day_opened[start:end])
            tmp_c =  np.array(a_day_close[start:end])
            tmp_h =  np.array(a_day_high[start:end])
            tmp_l =  np.array(a_day_low[start:end])
            tmp_date = a_day_date[end]
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
    
    #s = stock("測試資料/基金/富蘭克林坦伯頓全球投資系列-全球債券總報酬基金美元A.csv")
    fname = "測試資料/台股/VTd.csv"
    s = stock(fname, adj_fix = False)
    s5 = stock_5day(fname, adj_fix = False)
    
    ma_d, ma = s.feature_MA(30)
    k = s.feature_K()
#    k_date, k_up, k_down = tools.list_best_range(s.date,k,max = 0.8, min=0.2, n = 100)
    k_date, k_up, k_down = tools.list_best_range_std(s.date,k,std_range=1.2, n = 100)
    kma_d, kma = s.feature_K_MA(n=100)
    
    
    k5 = s5.feature_K()
#    k5_date, k5_up, k5_down = tools.list_best_range(s5.date,k5,max = 0.8, min=0.2, n = 100)
    k5_date, k5_up, k5_down = tools.list_best_range_std(s5.date,k5,std_range=1.2, n = 100)
    k5ma_d, k5ma = s5.feature_K_MA(n=100)
    
    print(len(s5.date))
    print(len(k5ma_d))
    print(len(k5ma))
    print(len(k5))
    #print(len(s.date))
    #print(len(s.close))

#    plt.plot( data[:] , "-", label="1")
#    plt.plot_date( s.date, s.close , "-", label="3")
#    plt.plot_date( date3, data3 , "-", label="3")
#    plt.plot_date( date5, data5 , "-", label="5")
#    plt.grid()
#    plt.legend()
#    plt.show()

# ############ 兩種 Y 軸#######    
#    t = np.arange(0.01, 10.0, 0.01)
#    data1 = np.exp(t)
#    data2 = np.sin(2 * np.pi * t)
#    
#    fig, ax1 = plt.subplots()
#    
#    color = 'tab:red'
#    ax1.set_xlabel('date')
#    ax1.set_ylabel('price', color=color)
#    ax1.plot_date(s.date, s.close, "-", color=color)
#    ax1.tick_params(axis='y', labelcolor=color)
#    
#    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
#    
#    color = 'tab:blue'
#    ax2.set_ylabel('K', color=color)  # we already handled the x-label with ax1
#    ax2.plot_date(s.date, k,"-", color=color)
#    ax2.tick_params(axis='y', labelcolor=color)
#    
#    fig.tight_layout()  # otherwise the right y-label is slightly clipped
#    plt.show()

# ############ 上下 兩圖 #######    
    plt.close('all')
    fig = plt.figure()
#    fig = plt.figure(figsize=(20,20))
    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((4, 1), (2, 0))
    ax3 = plt.subplot2grid((4, 1), (3, 0))
    

    ax1.set_title(fname)
    ax1.plot_date(s.date, s.close, "-")
    ax1.plot_date(ma_d, ma, "-")
    date_str = mdates.num2date(s.date[-1]).strftime("%m/%d")
    ax1.text(s.date[-1], s.close[-1] , "{0}={1}".format(date_str,s.close[-1]))
    ax1.grid()
    
    ax2.plot_date(s.date, k,"-")
    ax2.plot_date(kma_d, kma ,"-")
    ax2.plot_date(k_date, k_up,"-")
    ax2.plot_date(k_date, k_down,"-")
    ax2.grid()
    
    
    
    ax3.plot_date(s5.date, k5,"-")
    ax3.plot_date(k5ma_d, k5ma ,"-")
    ax3.plot_date(k5_date, k5_up,"-")
    ax3.plot_date(k5_date, k5_down,"-")
    ax3.text(k5_date[-1], k5_up[-1], round(k5_up[-1],2))
    ax3.text(k5_date[-1], k5[-1] , "K=" +str(round(k5[-1],2)))
    ax3.text(k5_date[-1], k5_down[-1], round(k5_down[-1],2))
    date_str = mdates.num2date(k5_date[-1]).strftime("%m/%d")
    ax3.text(k5_date[-1], 0 , date_str)
    ax3.grid()
    
    print( )
#    plt.tight_layout()
    
    plt.show()
    #plt.savefig('test.png',dpi=199) # 不顯示存圖
  

# ############ 畫 K 線########    
#    s = stock_daytrade("測試資料/台灣加權指數/TXF1-分鐘-成交價_test.csv")
#    b = s.raw.tolist()
#    fig, ax = plt.subplots()
#    #plt.plot_date(s.date, s.close, "o")
#    candlestick_ohlc(ax, b, colorup='r', colordown='g', width=0.0003)
#    plt.show()
#    a = s.feature_MA_slope(5)
#    b = s.feature_MA(5)

