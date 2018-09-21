# -*- coding: utf-8 -*-
import numpy as np
import sys
import tools
import time
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import config_stock_tw

Configs = config_stock_tw.Configs

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
                caculate_model(sid, nday)
                time.sleep(10)
    
    
    