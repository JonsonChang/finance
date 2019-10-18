# -*- coding: utf-8 -*-
import numpy as np
import sys
import tools
import time
from stock import stock
from stock import stock_5day
from twstock import Stock
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import config_stock_tw

Configs = config_stock_tw.Configs

def check_history_data(sid):
    my_file = Path("測試資料/台股/{0}d.csv".format(sid))
    if my_file.exists() ==  False:
        print("{0} history data is not exist, create it now.".format(sid))
        append_str = ",0,0"
        stock = Stock(sid, initial_fetch=False)
        stock.fetch(2013, 1)
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
            
if __name__ == '__main__':

    if len(sys.argv) > 1:
        sid = sys.argv[1]
        nday = get_nday(sid)
        caculate_model(sid, nday)
    else:
        for config in Configs:
            if(config['Update'] == "TW"):
                print ("\r\n *-*-*-*-*-*-* ",config['Update'], config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
                sid = config['sid']
                nday = config['best_ma'] #設定主軸
                check_history_data(sid)
                caculate_model(sid, nday)
                time.sleep(10)
    
    
    if hasattr(sys, '_MEIPASS'):
        input("按任意鍵結束")