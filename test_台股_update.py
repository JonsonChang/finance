# -*- coding: utf-8 -*-
import numpy as np
import sys
import os
import tools
import time
from stock import stock
from stock import stock_5day
from twstock import Stock
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import commentjson  #使用pyinstall 會有file not found error
import json

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() # <== that's all it takes :-)


def check_history_data(sid):
    my_file = Path("測試資料/台股/{0}d.csv".format(sid))
    if my_file.exists() ==  False:
        print("{0} history data is not exist, create it now.".format(sid))
        append_str = ",0,0"
        stock = Stock(sid, initial_fetch=False)
        stock.fetch(2015, 1)
        for index in range(-len(stock.date),0):
            d = stock.date[index]
            o = stock.open[index]
            h = stock.high[index]
            l = stock.low[index]
            c = stock.close[index]
            
            str = "{0},{1},{2},{3},{4}".format(d.strftime('%Y/%m/%d'),o,h,l,c )
            print("資料回補：" + str)
            f = open(my_file, 'a+')
            f.write(str+append_str+"\n")
            f.close()
                

def caculate_model(sid, nday):
    s = stock("測試資料/台股/{0}d.csv".format(sid))
    if s.complate_data(sid) : 
         # 如果有新的資料，再重新laod 一次
        s = stock("測試資料/台股/{0}d.csv".format(sid))
    tmp12 = (mdates.num2date(s.date[-1]).strftime("%Y/%m/%d"))
    print(tmp12)
            
def get_nday(sid):
    for config in Configs:
        if(sid == config['sid']):
            print ("\r\n *-*-*-*-*-*-* ",config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
            return config['best_ma']

def caculate_model_yahoo(sid, nday):
    print('\r\n更新「美股」歷史資料 開始')
    
    n_year = 15

    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # n 年的資料
    start_date = (datetime.datetime.now()- datetime.timedelta(days=n_year*365)).strftime('%Y-%m-%d')
    out_file = "測試資料/台股/{0}d.csv".format(sid)

    # 日K 資料
    data = pdr.get_data_yahoo(sid, start=start_date, end=end_date)

    print(len(data.index.values))
    data.to_csv(out_file, sep=',', encoding='utf-8')

    # download Panel
    #= pdr.get_data_yahoo(["SPY", "IWM"], start="2017-01-01", end="2017-04-30")
    #print(data3)
    time.sleep(3)
    print('更新股價歷史資料 結束')

if __name__ == '__main__':
#讀取設定檔
    f = open('config_stock.tw.json', "r",  encoding='UTF-8')
    #Configs = commentjson.loads(f.read())
    Configs = json.loads(f.read())
    f.close()


    if len(sys.argv) > 1:  #傳入的第一個參數為第幾個設定檔
        index = int(sys.argv[1])
        config = Configs[index]

        print ("\r\n *-*-*-*-*-*-* ",config['Update'], config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
        sid = config['sid']
        nday = config['best_ma'] #設定主軸
        if(config['Update'] == "TW"):
            check_history_data(sid)
            caculate_model(sid, nday)
        elif(config['Update'] == "yahoo"):
            caculate_model_yahoo(sid, nday)
    else:
        for config in Configs:
            print ("\r\n *-*-*-*-*-*-* ",config['Update'], config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
            sid = config['sid']
            nday = config['best_ma'] #設定主軸
            
            if(config['Update'] == "TW"):
                check_history_data(sid)
                caculate_model(sid, nday)
                time.sleep(10)
    
            elif(config['Update'] == "yahoo"):
                caculate_model_yahoo(sid, nday)
    if hasattr(sys, '_MEIPASS'):
        input("按任意鍵結束")