# -*- coding: utf-8 -*-
import numpy as np
import sys
import tools
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_nday(sid):
    # 取得各股的均線
    if sid == '0050':
        return 69
    if sid == '1232':
        return 33
    if sid == '4904':
        return 75
    if sid == '9917':
        return 26
    if sid == '1229':
        return 39
    if sid == '1730':
        return 31
    if sid == '2412':
        return 62
    if sid == '4506':
        return 69
    if sid == '5903':
        return 37
    if sid == '2912':
        return 33
    if sid == '00636':
        return 50
    if sid == '1216':
        return 68
    if sid == '2207':
        return 76
    if sid == '4205':
        return 40
    if sid == '6469':
        return 44
    if sid == '6803':
        return 25
    
    print("Error: 無設定主軸")
    return 40

            
if __name__ == '__main__':
    print("*-*-*-*-*-*-*")
    sid = sys.argv[1]
#    nday = int(sys.argv[2]) #設定主軸
    nday = get_nday(sid) #設定主軸
    period = 12

    
    s = stock("測試資料/台股/{0}d.csv".format(sid))
    if s.complate_data(sid) : 
        # 如果有新的資料，再重新laod 一次
        s = stock("測試資料/台股/{0}d.csv".format(sid))
        
    pulldown_date, pulldown = s.feature_pulldown(20*6) # 半年
    print("半年高檔拉回標準：", round(tools.list_percentage(pulldown,0.4),3), "目前：", round(pulldown[-1],3)) 
    
    tmp1= round(tools.list_percentage(pulldown,0.4),3)
    tmp2= round(pulldown[-1],3)
    
    BIAS = s.feature_BIAS(nday)
    BIAS_low = list(filter(lambda x: x < 0, BIAS[nday:]))
    print("主軸拉回標準：", round(tools.list_percentage(BIAS_low,0.4)*100,3), "目前：", round(BIAS[-1]*100,3)) 
    
    tmp3 = round(tools.list_percentage(BIAS_low,0.4)*100,3)
    tmp4 = round(BIAS[-1]*100,3)
        
    #1日 K
    list_K = s.feature_K()
    currnt_K = list_K[-1]

    print("1日K 高低檔數值：", round(tools.list_percentage(list_K,0.2),2), round(tools.list_percentage(list_K,0.8),2), "目前 K：", round(currnt_K, 2))    
    tmp5 =  round(tools.list_percentage(list_K,0.2),2)
    tmp6 = round(tools.list_percentage(list_K,0.8),2)
    tmp7 = round(currnt_K, 2)
    
    MA_slope = s.feature_MA(nday)
    print("目前均線：", MA_slope[-1], " 均線漲跌：", round(MA_slope[-1] - MA_slope[-2],4))
    tmp11 = round(MA_slope[-1] - MA_slope[-2],4)
    tmp12 = (mdates.num2date(s.date[-1]).strftime("%Y/%m/%d"))
    
    
    #5日 K
    s = stock_5day("測試資料/台股/{0}d.csv".format(sys.argv[1]))
    list_K = s.feature_K()
    currnt_K = list_K[-1]

    print("5日K 高低檔數值：", round(tools.list_percentage(list_K,0.2),2), round(tools.list_percentage(list_K,0.8),2), "目前 K：", round(currnt_K, 2))

    tmp8 = round(tools.list_percentage(list_K,0.2),2)
    tmp9 =  round(tools.list_percentage(list_K,0.8),2)
    tmp10 = round(currnt_K, 2)
    
    print("")
    if tmp2<tmp1:
        print("** 高檔拉回")
    if tmp4<tmp3:
        print("** 主軸拉回")
    if tmp7<tmp5:
        print("** 1日k 低檔")
    if tmp10<tmp8:
        print("** 5日k 低檔")        
    print("")
    print(tmp12,tmp1,tmp2,tmp3,tmp4,tmp5,tmp6,tmp7,tmp8,tmp9,tmp10, tmp11)
    
    
    