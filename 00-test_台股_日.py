# -*- coding: utf-8 -*-
import numpy as np
import sys
import tools
from stock import stock
from stock import stock_5day
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import config_stock_tw

Configs = config_stock_tw.Configs

def caculate_model(sid, nday):
    print("")
    
    s = stock("測試資料/台股/{0}d.csv".format(sid))
#    if s.complate_data(sid) : 
        # 如果有新的資料，再重新laod 一次
#        s = stock("測試資料/台股/{0}d.csv".format(sid))

    #s.reduce_data_len(250*10) # 用五年內的資料
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
    
    #中長 紅黑K統計
    diff = s.feature_diff()[1:]*100
    diff_up_list = list(filter(lambda x: x > 0, diff))
    diff_down_list = list(filter(lambda x: x < 0, diff))
    diff_current = diff[-1]
    diff_up_std1 = tools.list_percentage(diff_up_list,0.55)
    diff_up_std2 = tools.list_percentage(diff_up_list,0.75)
    diff_down_std1 = tools.list_percentage(diff_down_list,1-0.55)
    diff_down_std2 = tools.list_percentage(diff_down_list,1-0.75)
    print("中紅標準：", round(diff_up_std1,2), "\t目前：", round(diff_current,2))
    print("中黑標準：", round(diff_down_std1,2), "\t目前：", round(diff_current,2))
    print("長紅標準：", round(diff_up_std2,2), "\t目前：", round(diff_current,2))
    print("長黑標準：", round(diff_down_std2,2), "\t目前：", round(diff_current,2))    
    
    #5日 K
    s5 = stock_5day("測試資料/台股/{0}d.csv".format(sid))
    list_K = s5.feature_K()
    currnt_K = list_K[-1]

    print("5日K 高低檔數值：", round(tools.list_percentage(list_K,0.2),2), round(tools.list_percentage(list_K,0.8),2), "目前 K：", round(currnt_K, 2))
    print(tmp12,",",s.close[-1],",",s.close[-2],",",s.close[-3],",",s.close[-4])

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
    if diff_current > diff_up_std2:
        print("** 長紅")
    elif diff_current > diff_up_std1:
        print("** 中紅")
    if diff_current < diff_down_std2:
        print("** 長黑")
    elif diff_current < diff_down_std1:
        print("** 中黑")
    print("")
    print(tmp12,tmp1,tmp2,tmp3,tmp4,tmp5,tmp6,tmp7,tmp8,tmp9,tmp10, tmp11)
            
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
            print ("\r\n *-*-*-*-*-*-* ",config['sid'], config['S_name'], "均線：", config['best_ma'], "*-*-*-*-*-*-*")
            sid = config['sid']
            nday = config['best_ma'] #設定主軸
            caculate_model(sid, nday)
    
    
    